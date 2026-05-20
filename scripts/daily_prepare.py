#!/usr/bin/env python3
"""Prepare one queued civic agenda item for manual model review."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from common import load_yaml_file, repo_root, slugify, utc_now, write_text
from ingest_policy import build_manifest, build_notes_file, build_policy_file, build_sources_readme


QUEUE_PATH = Path("agendas/queue.yaml")


def yaml() -> Any:
    try:
        import yaml as yaml_module
    except ImportError as exc:
        raise SystemExit(
            "PyYAML is required. Install dependencies with `pip install -r requirements.txt`."
        ) from exc
    return yaml_module


def dump_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml().safe_dump(payload, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", default=str(QUEUE_PATH), help="Agenda queue YAML path")
    parser.add_argument("--agenda-id", help="Specific queued agenda_id to prepare")
    parser.add_argument("--policy-id", help="Override generated policy id")
    parser.add_argument(
        "--force-placeholder",
        action="store_true",
        help="Allow preparing the shipped example placeholder item.",
    )
    return parser.parse_args()


def load_queue(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Agenda queue not found: {path}")
    payload = load_yaml_file(path)
    items = payload.get("items")
    if not isinstance(items, list):
        raise SystemExit(f"Expected `items` list in {path}")
    return payload


def select_item(items: list[dict[str, Any]], agenda_id: str | None) -> dict[str, Any]:
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("status") != "queued":
            continue
        if agenda_id and item.get("agenda_id") != agenda_id:
            continue
        return item
    suffix = f" for agenda_id {agenda_id!r}" if agenda_id else ""
    raise SystemExit(f"No queued agenda item found{suffix}.")


def ensure_not_placeholder(item: dict[str, Any], force: bool) -> None:
    text = " ".join(str(item.get(key, "")) for key in ("agenda_id", "title", "summary")).lower()
    if "example" in text and not force:
        raise SystemExit(
            "The next queued item appears to be the shipped example. Replace it in "
            "agendas/queue.yaml or rerun with --force-placeholder."
        )


def write_policy_workspace(root: Path, item: dict[str, Any], policy_id: str) -> Path:
    title = str(item["title"]).strip()
    evaluation_mode = str(item.get("evaluation_mode", "current")).strip()
    jurisdiction = str(item.get("jurisdiction", "federal")).strip()
    as_of_date = str(item.get("as_of_date", "")).strip()
    if not as_of_date:
        raise SystemExit("Queued agenda item must include as_of_date.")

    status_by_mode = {
        "historical": "historical",
        "current": "active",
        "proposed": "proposed",
    }
    status = str(item.get("policy_status") or status_by_mode.get(evaluation_mode, "draft"))
    policy_dir = root / "policies" / evaluation_mode / policy_id
    if policy_dir.exists():
        raise SystemExit(f"Policy directory already exists: {policy_dir}")

    (policy_dir / "sources").mkdir(parents=True, exist_ok=False)
    (policy_dir / "attachments").mkdir(parents=True, exist_ok=False)

    manifest = build_manifest(
        title=title,
        policy_id=policy_id,
        evaluation_mode=evaluation_mode,
        jurisdiction=jurisdiction,
        as_of_date=as_of_date,
        status=status,
    )
    manifest_data = yaml().safe_load(manifest)
    manifest_data["summary"] = str(item.get("summary") or manifest_data["summary"])
    manifest_data["sources"] = [
        {"url": url, "note": "Queued agenda source"}
        for url in item.get("source_urls", [])
    ]
    manifest_data["tags"] = item.get("tags", [])
    if item.get("owner"):
        manifest_data["policy_owner"] = item["owner"]
    dump_yaml(policy_dir / "policy_manifest.yaml", manifest_data)

    policy_body = build_policy_file(title)
    source_lines = [f"- {url}" for url in item.get("source_urls", [])]
    context = str(item.get("summary") or "").strip()
    if source_lines or context:
        policy_body = (
            f"# {title}\n\n"
            "## Policy text\n\n"
            "Collect the exact policy text, bill extract, instrument, consultation paper, "
            "or official agenda material here before final review.\n\n"
            "## Context\n\n"
            f"{context or 'Neutral context to be completed during source collection.'}\n\n"
            "## Source links\n\n"
            + ("\n".join(source_lines) if source_lines else "- Add official source links here.")
            + "\n"
        )
    write_text(policy_dir / "policy.md", policy_body)
    write_text(policy_dir / "notes.md", build_notes(item))
    write_text(policy_dir / "sources" / "README.md", build_sources_readme())
    write_text(policy_dir / "attachments" / ".gitkeep", "")
    return policy_dir


def build_notes(item: dict[str, Any]) -> str:
    lines = [build_notes_file().rstrip(), "", "## Agenda Queue Notes", ""]
    for note in item.get("notes", []):
        lines.append(f"- {note}")
    if len(lines) == 4:
        lines.append("- Add source collection and manual processing notes here.")
    return "\n".join(lines).rstrip() + "\n"


def run_prepare(root: Path, policy_dir: Path) -> Path:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_review.py",
            "prepare",
            "--policy-dir",
            str(policy_dir.relative_to(root)),
        ],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    )
    bundle_paths = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not bundle_paths:
        raise SystemExit("run_review.py did not report any bundles.")
    first_bundle = root / bundle_paths[0]
    return first_bundle.parent


def create_manual_placeholders(run_dir: Path) -> list[Path]:
    placeholders: list[Path] = []
    for prompt_path in sorted(run_dir.glob("review__*.prompt.md")):
        response_path = prompt_path.with_name(prompt_path.name.replace(".prompt.md", ".manual_response.txt"))
        write_text(response_path, "")
        placeholders.append(response_path)
    return placeholders


def write_batch(root: Path, item: dict[str, Any], policy_id: str, policy_dir: Path, run_dir: Path) -> Path:
    today = utc_now().date().isoformat()
    batch_dir = root / "manual_batches" / f"{today}__{policy_id}"
    if batch_dir.exists():
        raise SystemExit(f"Manual batch already exists: {batch_dir}")
    batch_dir.mkdir(parents=True)

    placeholders = create_manual_placeholders(run_dir)
    manifest = {
        "schema_version": 1,
        "agenda_id": item.get("agenda_id"),
        "policy_id": policy_id,
        "policy_dir": str(policy_dir.relative_to(root)),
        "run_dir": str(run_dir.relative_to(root)),
        "status": "awaiting_review_responses",
        "created_at_utc": utc_now().isoformat().replace("+00:00", "Z"),
    }
    (batch_dir / "batch_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        f"# Manual Batch: {item['title']}",
        "",
        f"- Policy id: `{policy_id}`",
        f"- Policy workspace: `{policy_dir.relative_to(root)}`",
        f"- Run directory: `{run_dir.relative_to(root)}`",
        "",
        "## Review Responses",
        "",
        "Paste each prompt into the matching web model and save the raw answer in the response file listed beside it.",
        "",
    ]
    for response_path in placeholders:
        prompt_path = response_path.with_name(response_path.name.replace(".manual_response.txt", ".prompt.md"))
        bundle_path = response_path.with_name(response_path.name.replace(".manual_response.txt", ".json"))
        lines.extend(
            [
                f"### {bundle_path.stem}",
                "",
                f"- Prompt: `{prompt_path.relative_to(root)}`",
                f"- Save response: `{response_path.relative_to(root)}`",
                f"- Bundle: `{bundle_path.relative_to(root)}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Record Progress",
            "",
            "After saving one or more responses, run:",
            "",
            "```bash",
            f"python3 scripts/record_manual_batch.py --batch {batch_dir.relative_to(root)}",
            "```",
            "",
            "When all review responses are recorded, that command prepares the synthesis prompt and creates the synthesis manual response file.",
        ]
    )
    write_text(batch_dir / "README.md", "\n".join(lines).rstrip() + "\n")
    return batch_dir


def main() -> int:
    args = parse_args()
    root = repo_root()
    queue_path = root / args.queue
    queue = load_queue(queue_path)
    item = select_item(queue["items"], args.agenda_id)
    ensure_not_placeholder(item, args.force_placeholder)

    policy_id = args.policy_id or str(item.get("policy_id") or slugify(str(item["title"])))
    policy_dir = write_policy_workspace(root, item, policy_id)
    run_dir = run_prepare(root, policy_dir)
    batch_dir = write_batch(root, item, policy_id, policy_dir, run_dir)

    item["status"] = "prepared"
    item["policy_id"] = policy_id
    item["policy_dir"] = str(policy_dir.relative_to(root))
    item["run_dir"] = str(run_dir.relative_to(root))
    item["manual_batch_dir"] = str(batch_dir.relative_to(root))
    item["prepared_at_utc"] = utc_now().isoformat().replace("+00:00", "Z")
    dump_yaml(queue_path, queue)

    print(f"prepared: {policy_id}")
    print(f"policy: {policy_dir.relative_to(root)}")
    print(f"run: {run_dir.relative_to(root)}")
    print(f"manual batch: {batch_dir.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
