#!/usr/bin/env python3
"""Validate Amazon Ads execution task bundles."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

ALLOWED_AD_TYPES = {"SP", "SB", "SD", "MIXED"}
ALLOWED_STATUSES = {
    "ready",
    "needs_review",
    "invalid_input",
    "unmapped_strategy",
    "unsupported_action",
    "conflict_detected",
}
ACTION_SPECS = {
    "create_campaign": {
        "ad_types": {"SP", "SB", "SD", "MIXED"},
        "required": ["campaign_name", "daily_budget"],
    },
    "create_ad_group": {
        "ad_types": {"SP", "SB", "SD", "MIXED"},
        "required": ["ad_group_name"],
    },
    "create_ad": {
        "ad_types": {"SB", "SD", "MIXED"},
        "required": ["ad_name"],
    },
    "create_target": {
        "ad_types": {"SP", "SD", "MIXED"},
        "required": ["target_type", "target_value"],
    },
    "add_negative_target": {
        "ad_types": {"SP", "SB", "SD", "MIXED"},
        "required": ["negative_type", "target_value"],
    },
    "update_bid": {
        "ad_types": {"SP", "SD", "MIXED"},
        "required_any": ["bid", "bid_delta", "bid_percent_delta"],
    },
    "update_budget": {
        "ad_types": {"SP", "SB", "SD", "MIXED"},
        "required_any": ["daily_budget", "budget_delta", "budget_percent_delta"],
    },
    "update_bid_strategy": {
        "ad_types": {"SP", "MIXED"},
        "required": ["bidding_strategy"],
    },
    "update_placement_modifier": {
        "ad_types": {"SP", "MIXED"},
        "required": ["placement", "modifier_percent"],
    },
    "pause_entity": {
        "ad_types": {"SP", "SB", "SD", "MIXED"},
    },
    "enable_entity": {
        "ad_types": {"SP", "SB", "SD", "MIXED"},
    },
}
REQUIRED_TASK_FIELDS = [
    "task_id",
    "source_skill",
    "action_type",
    "ad_type",
    "target_entity",
    "payload",
    "validation",
    "status",
]


def _ensure_validation_shape(task: Dict[str, Any]) -> Dict[str, Any]:
    validation = task.get("validation")
    if not isinstance(validation, dict):
        validation = {}
        task["validation"] = validation
    validation.setdefault("warnings", [])
    validation.setdefault("missing_fields", [])
    validation.setdefault("errors", [])
    return validation


def _append_unique(items: List[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _required_payload_errors(action_type: str, payload: Dict[str, Any]) -> List[str]:
    spec = ACTION_SPECS.get(action_type, {})
    errors: List[str] = []
    for field_name in spec.get("required", []):
        if field_name not in payload:
            errors.append(f"missing payload field: {field_name}")
    required_any = spec.get("required_any", [])
    if required_any and not any(field_name in payload for field_name in required_any):
        joined = ", ".join(required_any)
        errors.append(f"missing one of payload fields: {joined}")
    return errors


def _risk_review(task: Dict[str, Any], validation: Dict[str, Any]) -> None:
    payload = task.get("payload", {})
    action_type = task.get("action_type")
    if not isinstance(payload, dict):
        return
    if action_type == "update_budget" and abs(payload.get("budget_percent_delta", 0)) > 50:
        _append_unique(validation["warnings"], "large budget_percent_delta")
    if action_type == "update_bid" and abs(payload.get("bid_percent_delta", 0)) > 40:
        _append_unique(validation["warnings"], "large bid_percent_delta")
    if action_type == "update_placement_modifier" and abs(payload.get("modifier_percent", 0)) > 100:
        _append_unique(validation["warnings"], "large placement modifier")
    if validation["warnings"] and task.get("status") == "ready":
        task["status"] = "needs_review"


def validate_bundle(bundle: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if not isinstance(bundle, dict):
        raise ValueError("Bundle must be a JSON object.")
    tasks = bundle.get("tasks")
    if not isinstance(tasks, list):
        raise ValueError("Bundle must include a tasks array.")

    entity_actions: Dict[str, List[int]] = defaultdict(list)

    for index, task in enumerate(tasks):
        if not isinstance(task, dict):
            tasks[index] = {
                "task_id": f"task_{index + 1:03d}",
                "source_skill": "unknown",
                "action_type": "unmapped_strategy",
                "ad_type": "MIXED",
                "target_entity": {"entity_type": "unknown", "entity_key": f"unknown:{index}"},
                "payload": {},
                "validation": {"warnings": [], "missing_fields": [], "errors": ["task must be an object"]},
                "status": "invalid_input",
            }
            task = tasks[index]

        validation = _ensure_validation_shape(task)
        for field_name in REQUIRED_TASK_FIELDS:
            if field_name not in task:
                _append_unique(validation["missing_fields"], field_name)
        if validation["missing_fields"]:
            task["status"] = "invalid_input"

        action_type = task.get("action_type")
        ad_type = task.get("ad_type")
        payload = task.get("payload")
        target_entity = task.get("target_entity")

        if not isinstance(payload, dict):
            _append_unique(validation["errors"], "payload must be an object")
            task["status"] = "invalid_input"
            payload = {}
            task["payload"] = payload

        if not isinstance(target_entity, dict):
            _append_unique(validation["errors"], "target_entity must be an object")
            task["status"] = "invalid_input"
            target_entity = {}
            task["target_entity"] = target_entity

        if "entity_type" not in target_entity:
            _append_unique(validation["missing_fields"], "target_entity.entity_type")
            task["status"] = "invalid_input"
        if "entity_key" not in target_entity:
            _append_unique(validation["missing_fields"], "target_entity.entity_key")
            task["status"] = "invalid_input"

        if action_type not in ACTION_SPECS:
            _append_unique(validation["errors"], f"unsupported action_type: {action_type}")
            task["status"] = "unmapped_strategy"
        else:
            allowed_ad_types = ACTION_SPECS[action_type]["ad_types"]
            if ad_type not in ALLOWED_AD_TYPES:
                _append_unique(validation["errors"], f"invalid ad_type: {ad_type}")
                task["status"] = "invalid_input"
            elif ad_type not in allowed_ad_types:
                _append_unique(validation["errors"], f"{action_type} is not allowed for {ad_type}")
                task["status"] = "unsupported_action"
            for error in _required_payload_errors(action_type, payload):
                _append_unique(validation["errors"], error)
                if error.startswith("missing payload field"):
                    missing_name = error.split(": ", 1)[1]
                    _append_unique(validation["missing_fields"], missing_name)
                task["status"] = "invalid_input"

        if task.get("status") not in ALLOWED_STATUSES:
            task["status"] = "invalid_input"
            _append_unique(validation["errors"], "invalid status value")

        entity_key = target_entity.get("entity_key")
        if entity_key:
            entity_actions[entity_key].append(index)

        _risk_review(task, validation)

    for entity_key, indexes in entity_actions.items():
        actions = [tasks[index]["action_type"] for index in indexes]
        if "pause_entity" in actions and "enable_entity" in actions:
            for index in indexes:
                tasks[index]["status"] = "conflict_detected"
                _append_unique(tasks[index]["validation"]["errors"], f"conflicting enable/pause on {entity_key}")
        if "pause_entity" in actions and len(set(actions)) > 1:
            for index in indexes:
                tasks[index]["status"] = "conflict_detected"
                _append_unique(tasks[index]["validation"]["errors"], f"conflicting mutation while paused on {entity_key}")
        if actions.count("update_bid_strategy") > 1:
            for index in indexes:
                if tasks[index]["action_type"] == "update_bid_strategy":
                    tasks[index]["status"] = "conflict_detected"
                    _append_unique(tasks[index]["validation"]["errors"], f"duplicate bid strategy updates on {entity_key}")
        if actions.count("update_placement_modifier") > 1:
            for index in indexes:
                if tasks[index]["action_type"] == "update_placement_modifier":
                    tasks[index]["status"] = "conflict_detected"
                    _append_unique(tasks[index]["validation"]["errors"], f"duplicate placement modifier updates on {entity_key}")

    status_counter = Counter(task.get("status", "invalid_input") for task in tasks)
    action_counter = Counter(task.get("action_type", "unknown") for task in tasks)
    summary = {
        "bundle_id": bundle.get("bundle_id"),
        "task_count": len(tasks),
        "status_counts": dict(status_counter),
        "action_counts": dict(action_counter),
    }
    return bundle, summary


def load_bundle(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an Amazon Ads task bundle JSON file.")
    parser.add_argument("bundle_json", help="Path to the bundle JSON file")
    parser.add_argument("--output", help="Optional path to write the normalized bundle")
    parser.add_argument("--summary-only", action="store_true", help="Only print the summary JSON")
    args = parser.parse_args()

    bundle_path = Path(args.bundle_json).resolve()
    bundle = load_bundle(bundle_path)
    normalized, summary = validate_bundle(bundle)

    if args.output:
        Path(args.output).write_text(json.dumps(normalized, indent=2, ensure_ascii=False) + "\n")

    if args.summary_only:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({"summary": summary, "bundle": normalized}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
