# Upstream Strategy Patterns

Use this file when the upstream strategy is present but not already normalized.

## What To Look For

| Signal | Examples | Interpretation |
|---|---|---|
| Creation intent | `新建SP自动+手动`, `create manual campaign`, `launch SB structure` | Compile `create_*` actions. |
| Negative targeting | `加否词`, `negative exact`, `block irrelevant search terms` | Compile `add_negative_target`. |
| Bid change | `提高竞价`, `lower bids 15%`, `keyword bid too aggressive` | Compile `update_bid`. |
| Budget change | `预算加到80`, `cut budget`, `increase daily budget` | Compile `update_budget`. |
| SP bidding mode | `up and down`, `down only`, `fixed bids`, `动态竞价` | Compile `update_bid_strategy` for SP only. |
| SP placement | `top of search +30%`, `商品页降低`, `placement modifier` | Compile `update_placement_modifier` for SP only. |
| Pause / enable | `暂停低效`, `resume winner`, `re-enable` | Compile `pause_entity` or `enable_entity`. |

## Recommended Intake Fields

Prefer these fields when available from the upstream skill:

| Field | Why it matters |
|---|---|
| `source_skill` | Traceability across chained skills. |
| `ad_type` | Action legality differs across SP, SB, and SD. |
| `intent` | Distinguishes creation from optimization. |
| `entity_scope` | Campaign, ad group, ad, target, or placement. |
| `targeting_type` | Keyword, product, or audience logic. |
| `budget` or `budget_change` | Needed for `update_budget` or `create_campaign`. |
| `bid` or `bid_change` | Needed for `update_bid`. |
| `bidding_strategy` | Needed for `update_bid_strategy`. |
| `placement_modifier` | Needed for `update_placement_modifier`. |

## Recognition Notes

- Chinese and English cues may coexist. Detect meaning, not language.
- One upstream conclusion can compile into multiple tasks.
- If the conclusion mixes ad types, compile one task per resolved target entity.
- If the same sentence contains both strategic rationale and execution details, keep only execution-relevant data in the payload.

## Escalate To Structured Status

Return a structured non-ready status instead of guessing when:

- Ad type is missing and cannot be inferred.
- The target entity is ambiguous.
- The requested action is unsupported for the detected ad type.
- Two conclusions conflict on the same target entity.
