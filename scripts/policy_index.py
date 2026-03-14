from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from common import load_yaml_file, read_text, repo_root, write_text


README_START = "<!-- COVERED_POLICIES_START -->"
README_END = "<!-- COVERED_POLICIES_END -->"


@dataclass
class CoveredPolicy:
    policy_id: str
    title: str
    evaluation_mode: str
    as_of_date: str
    policy_file: str
    report_file: str
    bundle_file: str
    prompt_file: str


def refresh_policy_indexes() -> None:
    covered = discover_covered_policies()
    update_readme(covered)


def discover_covered_policies() -> list[CoveredPolicy]:
    root = repo_root()
    covered: list[CoveredPolicy] = []

    for manifest_path in sorted(root.glob("policies/*/*/policy_manifest.yaml")):
        manifest = load_yaml_file(manifest_path)
        policy_id = str(manifest.get("policy_id", "")).strip()
        title = str(manifest.get("title", policy_id)).strip() or policy_id
        evaluation_mode = str(manifest.get("evaluation_mode", "")).strip()
        as_of_date = str(manifest.get("as_of_date", "")).strip()
        policy_dir = manifest_path.parent
        report_path = latest_report_for_policy(policy_id)
        if report_path is None:
            continue

        run_group_dir = report_path.parent
        alias = report_path.stem
        bundle_path = root / "runs" / policy_id / run_group_dir.name / f"synthesis__{alias}.json"
        prompt_path = root / "runs" / policy_id / run_group_dir.name / f"synthesis__{alias}.prompt.md"

        covered.append(
            CoveredPolicy(
                policy_id=policy_id,
                title=title,
                evaluation_mode=evaluation_mode,
                as_of_date=as_of_date,
                policy_file=relative_posix(policy_dir / str(manifest.get("policy_text_file", "policy.md"))),
                report_file=relative_posix(report_path),
                bundle_file=relative_posix(bundle_path),
                prompt_file=relative_posix(prompt_path),
            )
        )

    covered.sort(key=lambda item: (item.as_of_date, item.title.lower()), reverse=True)
    return covered


def latest_report_for_policy(policy_id: str) -> Path | None:
    root = repo_root()
    report_paths = sorted(
        root.glob(f"outputs/{policy_id}/*/*.md"),
        key=lambda path: (path.parent.name, path.name),
    )
    if not report_paths:
        return None
    return report_paths[-1]


def update_readme(covered: list[CoveredPolicy]) -> None:
    readme_path = repo_root() / "README.md"
    content = read_text(readme_path)
    if README_START not in content or README_END not in content:
        raise SystemExit("README.md is missing covered-policy markers.")

    before, remainder = content.split(README_START, 1)
    _, after = remainder.split(README_END, 1)
    replacement = f"{README_START}\n{render_table(covered)}\n{README_END}"
    write_text(readme_path, before + replacement + after)


def render_table(covered: list[CoveredPolicy]) -> str:
    if not covered:
        return "_No processed policies listed yet._"

    lines = [
        "| Policy | Mode | As-of | Policy | Synthesis | Processing |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in covered:
        lines.append(
            "| "
            f"{escape_pipe(item.title)} | "
            f"{escape_pipe(item.evaluation_mode)} | "
            f"{escape_pipe(item.as_of_date)} | "
            f"[policy]({item.policy_file}) | "
            f"[report]({item.report_file}) | "
            f"[bundle]({item.bundle_file}) · [prompt]({item.prompt_file}) |"
        )
    return "\n".join(lines)


def relative_posix(path: Path) -> str:
    return path.relative_to(repo_root()).as_posix()


def escape_pipe(value: str) -> str:
    return value.replace("|", "\\|")


if __name__ == "__main__":
    refresh_policy_indexes()
