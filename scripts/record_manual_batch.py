#!/usr/bin/env python3
"""Record manual review/synthesis responses for a prepared batch."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from common import load_json_file, read_text, repo_root, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True, help="Manual batch directory")
    parser.add_argument("--force", action="store_true", help="Overwrite recorded bundle responses")
    return parser.parse_args()


def save_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_command(root: Path, args: list[str]) -> None:
    subprocess.run(args, cwd=root, check=True)


def nonempty(path: Path) -> bool:
    return path.exists() and bool(read_text(path).strip())


def bundle_has_response(path: Path) -> bool:
    return bool(load_json_file(path).get("raw_response"))


def record_review_responses(root: Path, run_dir: Path, force: bool) -> int:
    recorded = 0
    for response_path in sorted(run_dir.glob("review__*.manual_response.txt")):
        if not nonempty(response_path):
            continue
        bundle_path = response_path.with_name(response_path.name.replace(".manual_response.txt", ".json"))
        if bundle_has_response(bundle_path) and not force:
            continue
        run_command(
            root,
            [
                sys.executable,
                "scripts/run_review.py",
                "record",
                "--bundle",
                str(bundle_path.relative_to(root)),
                "--response-file",
                str(response_path),
                *(["--force"] if force else []),
            ],
        )
        recorded += 1
    return recorded


def completed_review_count(run_dir: Path) -> int:
    count = 0
    for bundle_path in sorted(run_dir.glob("review__*.json")):
        if bundle_has_response(bundle_path):
            count += 1
    return count


def ensure_synthesis_prepared(root: Path, run_dir: Path) -> Path | None:
    existing = sorted(run_dir.glob("synthesis__*.json"))
    if not existing:
        run_command(
            root,
            [
                sys.executable,
                "scripts/synthesize_review.py",
                "prepare",
                "--run-dir",
                str(run_dir.relative_to(root)),
            ],
        )
        existing = sorted(run_dir.glob("synthesis__*.json"))
    if not existing:
        return None

    bundle_path = existing[0]
    response_path = bundle_path.with_name(bundle_path.name.replace(".json", ".manual_response.txt"))
    if not response_path.exists():
        write_text(response_path, "")
    return bundle_path


def record_synthesis_response(root: Path, bundle_path: Path, force: bool) -> bool:
    response_path = bundle_path.with_name(bundle_path.name.replace(".json", ".manual_response.txt"))
    if not nonempty(response_path):
        return False
    if bundle_has_response(bundle_path) and not force:
        return False
    run_command(
        root,
        [
            sys.executable,
            "scripts/synthesize_review.py",
            "record",
            "--bundle",
            str(bundle_path.relative_to(root)),
            "--response-file",
            str(response_path),
            *(["--force"] if force else []),
        ],
    )
    return True


def append_synthesis_instructions(root: Path, batch_dir: Path, synthesis_bundle: Path) -> None:
    readme_path = batch_dir / "README.md"
    content = read_text(readme_path)
    if "## Synthesis Response" in content:
        return
    response_path = synthesis_bundle.with_name(synthesis_bundle.name.replace(".json", ".manual_response.txt"))
    prompt_path = synthesis_bundle.with_name(synthesis_bundle.name.replace(".json", ".prompt.md"))
    addition = (
        "\n## Synthesis Response\n\n"
        "Paste the synthesis prompt into the synthesis model and save the raw answer in the response file below.\n\n"
        f"- Prompt: `{prompt_path.relative_to(root)}`\n"
        f"- Save response: `{response_path.relative_to(root)}`\n"
        f"- Bundle: `{synthesis_bundle.relative_to(root)}`\n\n"
        "Then run the same recorder command again.\n"
    )
    write_text(readme_path, content.rstrip() + "\n" + addition)


def main() -> int:
    args = parse_args()
    root = repo_root()
    batch_dir = Path(args.batch)
    if not batch_dir.is_absolute():
        batch_dir = root / batch_dir
    manifest_path = batch_dir / "batch_manifest.json"
    if not manifest_path.exists():
        raise SystemExit(f"Batch manifest not found: {manifest_path}")

    manifest = load_json_file(manifest_path)
    run_dir = root / str(manifest["run_dir"])
    if not run_dir.exists():
        raise SystemExit(f"Run directory not found: {run_dir}")

    recorded_reviews = record_review_responses(root, run_dir, args.force)
    review_count = completed_review_count(run_dir)
    manifest["completed_review_responses"] = review_count

    if review_count < 3:
        manifest["status"] = "awaiting_review_responses"
        save_manifest(manifest_path, manifest)
        print(f"Recorded {recorded_reviews} review response(s); {review_count}/3 complete.")
        return 0

    synthesis_bundle = ensure_synthesis_prepared(root, run_dir)
    if synthesis_bundle is None:
        raise SystemExit("Unable to prepare synthesis bundle.")

    append_synthesis_instructions(root, batch_dir, synthesis_bundle)
    if record_synthesis_response(root, synthesis_bundle, args.force):
        manifest["status"] = "completed"
        manifest["synthesis_bundle"] = str(synthesis_bundle.relative_to(root))
        bundle = load_json_file(synthesis_bundle)
        if bundle.get("report_path"):
            manifest["report_path"] = bundle["report_path"]
        save_manifest(manifest_path, manifest)
        print("Recorded synthesis response and wrote final report.")
    else:
        manifest["status"] = "awaiting_synthesis_response"
        manifest["synthesis_bundle"] = str(synthesis_bundle.relative_to(root))
        save_manifest(manifest_path, manifest)
        response_path = synthesis_bundle.with_name(synthesis_bundle.name.replace(".json", ".manual_response.txt"))
        print(f"Review responses complete. Fill synthesis response: {response_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
