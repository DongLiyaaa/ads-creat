#!/usr/bin/env python3
"""Package Amazon Ads skill artifacts into Downloads."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

from validate_task_payload import validate_bundle


def sample_bundle() -> Dict[str, Any]:
    return {
        "bundle_id": f"bundle_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "tasks": [
            {
                "task_id": "task_001",
                "source_skill": "sample-upstream-strategy-skill",
                "action_type": "create_campaign",
                "ad_type": "SP",
                "target_entity": {
                    "entity_type": "campaign",
                    "entity_key": "campaign:sample-sp-auto"
                },
                "payload": {
                    "campaign_name": "Sample SP Auto",
                    "daily_budget": 50
                },
                "validation": {
                    "warnings": [],
                    "missing_fields": [],
                    "errors": []
                },
                "status": "ready"
            },
            {
                "task_id": "task_002",
                "source_skill": "sample-upstream-strategy-skill",
                "action_type": "add_negative_target",
                "ad_type": "SP",
                "target_entity": {
                    "entity_type": "ad_group",
                    "entity_key": "ad_group:sample-sp-manual"
                },
                "payload": {
                    "negative_type": "negative_phrase",
                    "target_value": "free"
                },
                "validation": {
                    "warnings": [],
                    "missing_fields": [],
                    "errors": []
                },
                "status": "ready"
            },
            {
                "task_id": "task_003",
                "source_skill": "sample-upstream-strategy-skill",
                "action_type": "update_placement_modifier",
                "ad_type": "SP",
                "target_entity": {
                    "entity_type": "campaign",
                    "entity_key": "campaign:sample-sp-manual"
                },
                "payload": {
                    "placement": "TOP_OF_SEARCH",
                    "modifier_percent": 30
                },
                "validation": {
                    "warnings": [],
                    "missing_fields": [],
                    "errors": []
                },
                "status": "ready"
            }
        ]
    }


def load_bundle(path: Path | None) -> Dict[str, Any]:
    if path is None:
        return sample_bundle()
    return json.loads(path.read_text())


def risk_level(task: Dict[str, Any]) -> str:
    warnings = task.get("validation", {}).get("warnings", [])
    if task.get("status") in {"conflict_detected", "invalid_input", "unsupported_action"}:
        return "high"
    if warnings:
        return "medium"
    return "low"


def sql_literal(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"


def build_sql(bundle: Dict[str, Any]) -> str:
    rows = []
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for task in bundle["tasks"]:
        entity = task["target_entity"]
        payload_json = json.dumps(task["payload"], ensure_ascii=False, separators=(",", ":"))
        row = "(" + ", ".join(
            [
                sql_literal(bundle["bundle_id"]),
                sql_literal(task["task_id"]),
                sql_literal(task["source_skill"]),
                sql_literal(task["ad_type"]),
                sql_literal(task["action_type"]),
                sql_literal(entity["entity_type"]),
                sql_literal(entity["entity_key"]),
                sql_literal(payload_json),
                sql_literal(task["status"]),
                sql_literal(risk_level(task)),
                sql_literal(generated_at),
            ]
        ) + ")"
        rows.append(row)

    header = (
        "INSERT INTO amazon_ads_execution_tasks "
        "(bundle_id, task_id, source_skill, ad_type, action_type, target_entity_type, "
        "target_entity_key, payload_json, status, risk_level, created_at)\nVALUES\n"
    )
    return header + ",\n".join(rows) + ";\n"


def write_summary(bundle: Dict[str, Any], downloads_dir: Path, artifact_paths: Dict[str, Path]) -> str:
    status_counts = Counter(task["status"] for task in bundle["tasks"])
    action_counts = Counter(task["action_type"] for task in bundle["tasks"])
    lines = [
        "# Amazon Ads Task Bundle Summary",
        "",
        f"- bundle_id: `{bundle['bundle_id']}`",
        f"- generated_at: `{bundle.get('generated_at', '')}`",
        f"- downloads_dir: `{downloads_dir}`",
        "",
        "## Status Counts",
        "",
    ]
    for status, count in sorted(status_counts.items()):
        lines.append(f"- `{status}`: {count}")
    lines.extend(["", "## Action Counts", ""])
    for action, count in sorted(action_counts.items()):
        lines.append(f"- `{action}`: {count}")
    lines.extend(["", "## Artifacts", ""])
    for label, path in artifact_paths.items():
        lines.append(f"- `{label}`: `{path}`")
    lines.append("")
    return "\n".join(lines)


def package_skill(skill_dir: Path, downloads_dir: Path) -> Tuple[Path, Path]:
    target_skill_dir = downloads_dir / skill_dir.name
    if target_skill_dir.exists():
        shutil.rmtree(target_skill_dir)
    shutil.copytree(
        skill_dir,
        target_skill_dir,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )

    archive_path = downloads_dir / f"{skill_dir.name}.zip"
    if archive_path.exists():
        archive_path.unlink()
    with tempfile.TemporaryDirectory() as temp_dir:
        staging_root = Path(temp_dir) / skill_dir.name
        shutil.copytree(
            skill_dir,
            staging_root,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zip_handle:
            for path in sorted(staging_root.rglob("*")):
                if path.is_dir():
                    continue
                zip_handle.write(path, arcname=path.relative_to(Path(temp_dir)))
    return target_skill_dir, archive_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Downloads artifacts for the skill and a bundle JSON.")
    parser.add_argument("--skill-dir", required=True, help="Path to the skill directory")
    parser.add_argument("--bundle-json", help="Optional path to an input bundle JSON. Defaults to a sample bundle.")
    parser.add_argument("--downloads-dir", default="/Users/dongli/Downloads", help="Downloads output directory")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    downloads_dir = Path(args.downloads_dir).resolve()
    downloads_dir.mkdir(parents=True, exist_ok=True)

    raw_bundle = load_bundle(Path(args.bundle_json).resolve()) if args.bundle_json else load_bundle(None)
    normalized_bundle, _ = validate_bundle(raw_bundle)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    bundle_json_path = downloads_dir / f"amazon-ads-task-bundle-{timestamp}.json"
    sql_path = downloads_dir / f"amazon-ads-task-bundle-{timestamp}.sql"
    summary_path = downloads_dir / f"amazon-ads-task-summary-{timestamp}.md"

    bundle_json_path.write_text(json.dumps(normalized_bundle, indent=2, ensure_ascii=False) + "\n")
    sql_path.write_text(build_sql(normalized_bundle))

    copied_skill_dir, archive_path = package_skill(skill_dir, downloads_dir)
    artifact_paths = {
        "bundle_json": bundle_json_path,
        "sql": sql_path,
        "summary": summary_path,
        "skill_copy": copied_skill_dir,
        "skill_zip": archive_path,
    }
    summary_path.write_text(write_summary(normalized_bundle, downloads_dir, artifact_paths))

    print(json.dumps({key: str(value) for key, value in artifact_paths.items()}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
