#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from common import (
    dump_json_file,
    json_ready,
    load_json_file,
    load_yaml_file,
    path_for_log,
    read_text,
    repo_root,
    resolve_repo_path,
    sha256_file,
    sha256_text,
    utc_iso,
    utc_now,
    write_text,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare and record synthesis-model runs from completed review runs."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="Prepare synthesis run bundles.")
    prepare.add_argument(
        "--run-dir",
        required=True,
        help="Run group directory containing completed review bundles.",
    )
    prepare.add_argument(
        "--model",
        action="append",
        default=[],
        help="Limit output to one or more synthesis model aliases.",
    )

    record = subparsers.add_parser(
        "record", help="Attach a synthesis response and write a report."
    )
    record.add_argument("--bundle", required=True, help="Path to a synthesis bundle.")
    record.add_argument(
        "--response-file",
        required=True,
        help="File containing the raw synthesis response.",
    )
    record.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing recorded synthesis response.",
    )

    return parser.parse_args()


def select_synthesis_models(
    registry: dict[str, Any], aliases: list[str]
) -> list[dict[str, Any]]:
    synthesis_models = registry.get("synthesis_models")
    if not isinstance(synthesis_models, list) or not synthesis_models:
        raise SystemExit("models/registry.yaml does not define any synthesis models.")

    enabled_models = [model for model in synthesis_models if model.get("enabled", True)]
    if not aliases:
        return enabled_models

    index = {model["alias"]: model for model in enabled_models if "alias" in model}
    missing = [alias for alias in aliases if alias not in index]
    if missing:
        raise SystemExit(f"Unknown synthesis model aliases: {', '.join(missing)}")
    return [index[alias] for alias in aliases]


def load_completed_reviews(run_dir: Path) -> list[tuple[Path, dict[str, Any]]]:
    review_files = sorted(run_dir.glob("review__*.json"))
    completed: list[tuple[Path, dict[str, Any]]] = []
    for review_file in review_files:
        bundle = load_json_file(review_file)
        if bundle.get("stage") != "review":
            continue
        if bundle.get("raw_response"):
            completed.append((review_file, bundle))
    if len(completed) < 3:
        raise SystemExit(
            "Synthesis requires at least three completed review bundles with recorded responses."
        )
    return completed


def build_prompt_body(
    prompt_template: str,
    manifest: dict[str, Any],
    completed_reviews: list[tuple[Path, dict[str, Any]]],
) -> str:
    manifest_json = json.dumps(json_ready(manifest), indent=2, ensure_ascii=False)
    sections = [
        prompt_template.rstrip(),
        "",
        "## Policy Metadata",
        "",
        "```json",
        manifest_json,
        "```",
        "",
        "## Review Inputs",
        "",
    ]

    for review_file, bundle in completed_reviews:
        model = bundle["model"]
        sections.extend(
            [
                f"### {model['alias']}",
                "",
                f"- Provider: {model['provider']}",
                f"- Model: {model['model']}",
                f"- Source bundle: `{path_for_log(review_file)}`",
                "",
                "```text",
                str(bundle["raw_response"]).rstrip(),
                "```",
                "",
            ]
        )

    return "\n".join(sections).rstrip() + "\n"


def prepare(args: argparse.Namespace) -> int:
    root = repo_root()
    run_dir = resolve_repo_path(args.run_dir)
    if not run_dir.exists():
        raise SystemExit(f"Run directory not found: {run_dir}")

    completed_reviews = load_completed_reviews(run_dir)
    first_bundle = completed_reviews[0][1]
    policy_id = str(first_bundle["policy_id"])

    manifest_path = resolve_repo_path(str(first_bundle["policy_manifest_path"]))
    manifest = load_yaml_file(manifest_path)

    registry = load_yaml_file(root / "models" / "registry.yaml")
    selected_models = select_synthesis_models(registry, args.model)

    prompt_template_path = root / "prompts" / "synthesis_review.md"
    prompt_template = read_text(prompt_template_path)
    created_at = utc_now()

    source_run_files = [path_for_log(path) for path, _ in completed_reviews]

    for model in selected_models:
        alias = str(model["alias"])
        prepared_prompt_path = run_dir / f"synthesis__{alias}.prompt.md"
        prompt_body = build_prompt_body(prompt_template, manifest, completed_reviews)
        write_text(prepared_prompt_path, prompt_body)

        bundle = {
            "schema_version": 1,
            "run_id": f"{first_bundle['run_group_id']}__synthesis__{alias}",
            "run_group_id": first_bundle["run_group_id"],
            "stage": "synthesis",
            "created_at_utc": utc_iso(created_at),
            "policy_id": policy_id,
            "policy_path": first_bundle.get("policy_path"),
            "policy_manifest_path": first_bundle.get("policy_manifest_path"),
            "prompt": {
                "template_path": path_for_log(prompt_template_path),
                "template_sha256": sha256_file(prompt_template_path),
                "prepared_prompt_path": path_for_log(prepared_prompt_path),
                "prepared_prompt_sha256": sha256_file(prepared_prompt_path),
            },
            "model": model,
            "source_run_files": source_run_files,
            "raw_response": None,
            "response_source_path": None,
            "response_sha256": None,
            "response_recorded_at_utc": None,
        }
        bundle_path = run_dir / f"synthesis__{alias}.json"
        dump_json_file(bundle_path, bundle)
        print(path_for_log(bundle_path))

    return 0


def render_report(bundle: dict[str, Any]) -> str:
    model = bundle["model"]
    lines = [
        f"# Synthesis Report: {bundle['policy_id']}",
        "",
        f"- Run group: `{bundle['run_group_id']}`",
        f"- Recorded at: `{bundle['response_recorded_at_utc']}`",
        f"- Model alias: `{model['alias']}`",
        f"- Provider: `{model['provider']}`",
        f"- Model: `{model['model']}`",
        "",
        "## Source Review Bundles",
        "",
    ]

    for source_path in bundle.get("source_run_files", []):
        lines.append(f"- `{source_path}`")

    lines.extend(
        [
            "",
            "## Raw Synthesis Output",
            "",
            str(bundle["raw_response"]).rstrip(),
            "",
        ]
    )
    return "\n".join(lines)


def record(args: argparse.Namespace) -> int:
    bundle_path = resolve_repo_path(args.bundle)
    if not bundle_path.exists():
        raise SystemExit(f"Bundle not found: {bundle_path}")

    response_path = Path(args.response_file).expanduser().resolve()
    if not response_path.exists():
        raise SystemExit(f"Response file not found: {response_path}")

    bundle = load_json_file(bundle_path)
    if bundle.get("stage") != "synthesis":
        raise SystemExit(f"Bundle is not a synthesis run: {bundle_path}")
    if bundle.get("raw_response") and not args.force:
        raise SystemExit(
            "Bundle already has a recorded response. Use --force to overwrite it."
        )

    raw_response = read_text(response_path)
    if not raw_response.strip():
        raise SystemExit(f"Response file is empty: {response_path}")

    bundle["raw_response"] = raw_response
    bundle["response_source_path"] = path_for_log(response_path)
    bundle["response_sha256"] = sha256_text(raw_response)
    bundle["response_recorded_at_utc"] = utc_iso(utc_now())

    output_dir = repo_root() / "outputs" / str(bundle["policy_id"]) / str(bundle["run_group_id"])
    report_path = output_dir / f"{bundle['model']['alias']}.md"
    write_text(report_path, render_report(bundle))
    bundle["report_path"] = path_for_log(report_path)

    dump_json_file(bundle_path, bundle)
    print(f"Recorded synthesis in {path_for_log(bundle_path)}")
    print(f"Wrote report to {path_for_log(report_path)}")
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "prepare":
        return prepare(args)
    if args.command == "record":
        return record(args)
    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
