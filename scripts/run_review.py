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
    require_keys,
    resolve_repo_path,
    sha256_file,
    sha256_text,
    utc_iso,
    utc_now,
    utc_stamp,
    write_text,
)


REQUIRED_MANIFEST_KEYS = [
    "policy_id",
    "title",
    "status",
    "evaluation_mode",
    "jurisdiction",
    "as_of_date",
    "summary",
    "policy_text_file",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare and record review-model runs for a policy."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="Prepare review run bundles.")
    prepare.add_argument(
        "--policy-dir",
        required=True,
        help="Policy directory path, relative to repo root or absolute.",
    )
    prepare.add_argument(
        "--model",
        action="append",
        default=[],
        help="Limit output to one or more review model aliases.",
    )

    record = subparsers.add_parser("record", help="Attach a raw model response to a bundle.")
    record.add_argument(
        "--bundle",
        required=True,
        help="Path to a review bundle JSON file.",
    )
    record.add_argument(
        "--response-file",
        required=True,
        help="File containing the raw model response.",
    )
    record.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing recorded response.",
    )

    return parser.parse_args()


def load_policy(policy_dir: Path) -> tuple[dict[str, Any], Path, Path, str]:
    manifest_path = policy_dir / "policy_manifest.yaml"
    if not manifest_path.exists():
        raise SystemExit(f"Missing manifest: {manifest_path}")

    manifest = load_yaml_file(manifest_path)
    require_keys(manifest, REQUIRED_MANIFEST_KEYS, str(manifest_path))

    policy_text_path = policy_dir / str(manifest["policy_text_file"])
    if not policy_text_path.exists():
        raise SystemExit(f"Missing policy text file: {policy_text_path}")

    policy_text = read_text(policy_text_path)
    if not policy_text.strip():
        raise SystemExit(f"Policy text file is empty: {policy_text_path}")

    return manifest, manifest_path, policy_text_path, policy_text


def select_review_models(registry: dict[str, Any], aliases: list[str]) -> list[dict[str, Any]]:
    review_models = registry.get("review_models")
    if not isinstance(review_models, list) or not review_models:
        raise SystemExit("models/registry.yaml does not define any review models.")

    enabled_models = [model for model in review_models if model.get("enabled", True)]
    if not aliases:
        return enabled_models

    index = {model["alias"]: model for model in enabled_models if "alias" in model}
    missing = [alias for alias in aliases if alias not in index]
    if missing:
        raise SystemExit(f"Unknown review model aliases: {', '.join(missing)}")
    return [index[alias] for alias in aliases]


def build_prompt_body(prompt_template: str, manifest: dict[str, Any], policy_text: str) -> str:
    manifest_json = json.dumps(json_ready(manifest), indent=2, ensure_ascii=False)
    return (
        f"{prompt_template.rstrip()}\n\n"
        "## Policy Metadata\n\n"
        "```json\n"
        f"{manifest_json}\n"
        "```\n\n"
        "## Policy Text\n\n"
        "```markdown\n"
        f"{policy_text.rstrip()}\n"
        "```\n"
    )


def prepare(args: argparse.Namespace) -> int:
    root = repo_root()
    policy_dir = resolve_repo_path(args.policy_dir)
    if not policy_dir.exists():
        raise SystemExit(f"Policy directory not found: {policy_dir}")

    manifest, manifest_path, policy_text_path, policy_text = load_policy(policy_dir)
    registry = load_yaml_file(root / "models" / "registry.yaml")
    selected_models = select_review_models(registry, args.model)

    prompt_template_path = root / "prompts" / "policy_review.md"
    prompt_template = read_text(prompt_template_path)

    created_at = utc_now()
    run_group_id = f"{manifest['policy_id']}__{utc_stamp(created_at)}"
    run_dir = root / "runs" / str(manifest["policy_id"]) / run_group_id
    run_dir.mkdir(parents=True, exist_ok=False)

    for model in selected_models:
        alias = str(model["alias"])
        prepared_prompt_path = run_dir / f"review__{alias}.prompt.md"
        prompt_body = build_prompt_body(prompt_template, manifest, policy_text)
        write_text(prepared_prompt_path, prompt_body)

        bundle = {
            "schema_version": 1,
            "run_id": f"{run_group_id}__review__{alias}",
            "run_group_id": run_group_id,
            "stage": "review",
            "created_at_utc": utc_iso(created_at),
            "policy_id": manifest["policy_id"],
            "policy_path": path_for_log(policy_dir),
            "policy_manifest_path": path_for_log(manifest_path),
            "policy_manifest_sha256": sha256_file(manifest_path),
            "policy_text_path": path_for_log(policy_text_path),
            "policy_text_sha256": sha256_file(policy_text_path),
            "prompt": {
                "template_path": path_for_log(prompt_template_path),
                "template_sha256": sha256_file(prompt_template_path),
                "prepared_prompt_path": path_for_log(prepared_prompt_path),
                "prepared_prompt_sha256": sha256_file(prepared_prompt_path),
            },
            "model": model,
            "raw_response": None,
            "response_source_path": None,
            "response_sha256": None,
            "response_recorded_at_utc": None,
        }
        bundle_path = run_dir / f"review__{alias}.json"
        dump_json_file(bundle_path, bundle)
        print(path_for_log(bundle_path))

    return 0


def record(args: argparse.Namespace) -> int:
    bundle_path = resolve_repo_path(args.bundle)
    if not bundle_path.exists():
        raise SystemExit(f"Bundle not found: {bundle_path}")

    response_path = Path(args.response_file).expanduser().resolve()
    if not response_path.exists():
        raise SystemExit(f"Response file not found: {response_path}")

    bundle = load_json_file(bundle_path)
    if bundle.get("stage") != "review":
        raise SystemExit(f"Bundle is not a review run: {bundle_path}")
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

    dump_json_file(bundle_path, bundle)
    print(f"Recorded response in {path_for_log(bundle_path)}")
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
