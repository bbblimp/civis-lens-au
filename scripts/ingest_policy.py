#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import repo_root, slugify, write_text


def yaml_scalar(value: str | None) -> str:
    if value is None:
        return "null"
    return json.dumps(value, ensure_ascii=False)


def build_manifest(
    title: str,
    policy_id: str,
    evaluation_mode: str,
    jurisdiction: str,
    as_of_date: str,
    status: str,
) -> str:
    return (
        f"policy_id: {policy_id}\n"
        f"title: {yaml_scalar(title)}\n"
        f"status: {status}\n"
        f"evaluation_mode: {evaluation_mode}\n"
        f"jurisdiction: {jurisdiction}\n"
        f"as_of_date: {as_of_date}\n"
        "original_decision_date: null\n"
        "policy_owner: null\n"
        "summary: >\n"
        "  Replace this with a neutral summary of the policy under review.\n"
        "policy_text_file: policy.md\n"
        "attachments: []\n"
        "sources: []\n"
        "tags: []\n"
        "notes:\n"
        "  - Record the exact policy text and source links before submitting to models.\n"
        "  - Keep hindsight separate from contemporaneous analysis for historical reviews.\n"
    )


def build_policy_file(title: str) -> str:
    return (
        f"# {title}\n\n"
        "## Policy text\n\n"
        "Paste the policy text, bill extract, cabinet proposal, or consultation draft here.\n\n"
        "## Context\n\n"
        "Add only neutral context needed to understand the policy. Keep opinions and later analysis out of this file.\n"
    )


def build_notes_file() -> str:
    return (
        "# Working Notes\n\n"
        "- Add source collection notes here.\n"
        "- Keep judgments for model outputs and synthesis reports, not in the source policy text.\n"
    )


def build_sources_readme() -> str:
    return (
        "# Sources\n\n"
        "Store downloaded source documents or extracts here when local copies are needed.\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a new policy workspace in the Civis Lens AU repository."
    )
    parser.add_argument("--title", required=True, help="Human-readable policy title.")
    parser.add_argument(
        "--policy-id",
        help="Optional slug. If omitted, a slug is derived from the title.",
    )
    parser.add_argument(
        "--evaluation-mode",
        required=True,
        choices=["historical", "current", "proposed"],
        help="Policy review mode.",
    )
    parser.add_argument(
        "--jurisdiction",
        required=True,
        choices=["federal", "state", "local"],
        help="Jurisdiction level.",
    )
    parser.add_argument(
        "--as-of-date",
        required=True,
        help="Anchor date in YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--status",
        default="draft",
        choices=["draft", "historical", "active", "proposed", "archived"],
        help="Manifest status value.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    policy_id = args.policy_id or slugify(args.title)
    policy_dir = root / "policies" / args.evaluation_mode / policy_id

    if policy_dir.exists():
        raise SystemExit(f"Policy directory already exists: {policy_dir}")

    (policy_dir / "sources").mkdir(parents=True, exist_ok=False)
    (policy_dir / "attachments").mkdir(parents=True, exist_ok=False)

    write_text(
        policy_dir / "policy_manifest.yaml",
        build_manifest(
            title=args.title,
            policy_id=policy_id,
            evaluation_mode=args.evaluation_mode,
            jurisdiction=args.jurisdiction,
            as_of_date=args.as_of_date,
            status=args.status,
        ),
    )
    write_text(policy_dir / "policy.md", build_policy_file(args.title))
    write_text(policy_dir / "notes.md", build_notes_file())
    write_text(policy_dir / "sources" / "README.md", build_sources_readme())
    write_text(policy_dir / "attachments" / ".gitkeep", "")

    print(f"Created policy workspace: {policy_dir.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

