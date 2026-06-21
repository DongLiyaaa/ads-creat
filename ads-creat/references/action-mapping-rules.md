# Action Mapping Rules

Use this file when translating strategy conclusions into the fixed action dictionary.

## Mapping Table

| Strategy conclusion pattern | Compile to | Required payload fields | Notes |
|---|---|---|---|
| Launch or create a new campaign | `create_campaign` | `campaign_name`, `daily_budget` | `target_entity.entity_type` should be `campaign`. |
| Create a new ad group or equivalent group | `create_ad_group` | `ad_group_name` | Use the platform group term only inside payload if needed. |
| Create a new SB or SD ad | `create_ad` | `ad_name` | SB and SD only in V1. |
| Add keyword, product, or audience targeting | `create_target` | `target_type`, `target_value` | `target_type` should be explicit. |
| Add negative keyword or negative target | `add_negative_target` | `negative_type`, `target_value` | Use exact or phrase details when available. |
| Raise or lower bid | `update_bid` | one of `bid`, `bid_delta`, `bid_percent_delta` | Prefer absolute `bid` if upstream provides it. |
| Raise or lower budget | `update_budget` | one of `daily_budget`, `budget_delta`, `budget_percent_delta` | Keep values at campaign scope. |
| Change SP dynamic bidding mode | `update_bid_strategy` | `bidding_strategy` | SP only. |
| Change SP placement modifier | `update_placement_modifier` | `placement`, `modifier_percent` | SP only. |
| Pause an object | `pause_entity` | none | Target entity must be resolvable. |
| Re-enable an object | `enable_entity` | none | Target entity must be resolvable. |

## Entity Resolution

| Upstream wording | Suggested `target_entity.entity_type` |
|---|---|
| Campaign | `campaign` |
| Ad group / ad set | `ad_group` |
| Ad / creative | `ad` |
| Keyword | `keyword` |
| Product target / ASIN target | `product_target` |
| Audience | `audience_target` |
| Placement | `placement_scope` |

## Conflict Rules

Treat these as `conflict_detected` unless the user explicitly asks for a conflict-preserving bundle:

| Conflict | Reason |
|---|---|
| `pause_entity` and `enable_entity` on the same `entity_key` | Opposite state changes. |
| `pause_entity` and any mutation action on the same `entity_key` in the same bundle | Execution order becomes ambiguous. |
| Two `update_bid_strategy` tasks on the same SP campaign | Last-write ambiguity. |
| Two `update_placement_modifier` tasks on the same SP placement without explicit sequencing | Last-write ambiguity. |

## Compilation Guidance

- Keep action names fixed even if upstream wording varies.
- Put execution details into `payload`, not into `action_type`.
- Preserve the upstream source fragment inside `validation.source_fragment` when the mapping is uncertain.
- If a conclusion implies multiple actions, split it into multiple tasks instead of building one overloaded task.
