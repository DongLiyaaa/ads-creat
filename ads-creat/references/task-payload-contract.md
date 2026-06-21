# Task Payload Contract

Use this file when generating or validating the machine-executable bundle.

## Top-Level Bundle Shape

```json
{
  "bundle_id": "bundle_20260621_090000",
  "generated_at": "2026-06-21T09:00:00+08:00",
  "tasks": []
}
```

## Required Task Fields

| Field | Type | Rule |
|---|---|---|
| `task_id` | string | Required and unique within the bundle. |
| `source_skill` | string | Required. |
| `action_type` | string | Must be in the fixed action dictionary. |
| `ad_type` | string | Must be `SP`, `SB`, `SD`, or `MIXED`. |
| `target_entity` | object | Must contain `entity_type` and `entity_key`. |
| `payload` | object | Action-specific body. |
| `validation` | object | Holds warnings, missing fields, optional errors, and optional source fragment. |
| `status` | string | Must be an allowed status value. |

## Allowed Status Values

| Status | Meaning |
|---|---|
| `ready` | The task can be executed downstream. |
| `needs_review` | Structurally valid but risky. |
| `invalid_input` | Missing required data. |
| `unmapped_strategy` | Not enough certainty to map to a supported action. |
| `unsupported_action` | Action is invalid for the detected ad type. |
| `conflict_detected` | Another task or state change conflicts with this task. |

## Required `validation` Shape

```json
{
  "warnings": [],
  "missing_fields": [],
  "errors": []
}
```

`source_fragment` is optional and useful when preserving ambiguous upstream text.

## Action-Specific Minimum Fields

| Action type | Minimum payload requirement |
|---|---|
| `create_campaign` | `campaign_name`, `daily_budget` |
| `create_ad_group` | `ad_group_name` |
| `create_ad` | `ad_name` |
| `create_target` | `target_type`, `target_value` |
| `add_negative_target` | `negative_type`, `target_value` |
| `update_bid` | one of `bid`, `bid_delta`, `bid_percent_delta` |
| `update_budget` | one of `daily_budget`, `budget_delta`, `budget_percent_delta` |
| `update_bid_strategy` | `bidding_strategy` |
| `update_placement_modifier` | `placement`, `modifier_percent` |
| `pause_entity` | no required payload fields |
| `enable_entity` | no required payload fields |

## Example Task

```json
{
  "task_id": "task_001",
  "source_skill": "upstream-amazon-ads-strategy-skill",
  "action_type": "update_placement_modifier",
  "ad_type": "SP",
  "target_entity": {
    "entity_type": "campaign",
    "entity_key": "campaign:brand-core-manual"
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
```
