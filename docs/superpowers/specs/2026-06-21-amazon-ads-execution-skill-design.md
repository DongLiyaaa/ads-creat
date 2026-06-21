# Amazon Ads Execution Skill Design

Date: 2026-06-21
Status: Draft written, pending user review
Skill name: `executing-amazon-ads-strategies`
Workspace: `/Users/dongli/Documents/Skill`

## Objective

Create a reusable Codex skill that consumes upstream Amazon advertising strategy conclusions and converts them into machine-executable task payloads for Sponsored Products (SP), Sponsored Brands (SB), and Sponsored Display (SD) campaign creation and optimization.

The skill is execution-oriented, not diagnosis-oriented. It does not analyze raw ad performance as its primary job. Its responsibility is to take already-produced strategy conclusions and compile them into stable downstream actions that can be reviewed, stored, and executed by later systems or skills.

## User-Approved Decisions

| Topic | Decision | Reason |
|---|---|---|
| Primary mode | Execution orchestration | The user wants stable, reusable ad creation and optimization outputs rather than advisory text. |
| Position in workflow | Downstream of other skills | This skill is intended to receive conclusions produced elsewhere. |
| Output mode | Machine-executable payloads | The user selected machine execution over human-only operation sheets. |
| Input flexibility | Adaptive input recognition | The skill should infer structure from detected upstream strategy data rather than require one rigid source format. |
| Payload contract | Fixed outer envelope with dynamic inner payload | This preserves machine stability while allowing varied upstream strategy shapes. |
| Delivery location | System Downloads path | Final deliverables must be written to `/Users/dongli/Downloads`. |
| Database default | MySQL | Per workspace instruction, database examples and task tables use MySQL. |

## Problem Statement

Without a dedicated execution skill, upstream strategy skills can generate useful recommendations but still leave a brittle gap between "what to do" and "what to execute." That gap causes inconsistent naming, missing fields, ad-type-specific rule drift, and poor auditability.

The skill should close that gap by standardizing how strategy conclusions become executable tasks.

## In Scope

| In scope item | Description |
|---|---|
| Upstream strategy intake | Consume structured or semi-structured strategy conclusions from other skills. |
| Ad type recognition | Detect whether work applies to SP, SB, SD, or a combination. |
| Intent recognition | Distinguish creation tasks from optimization tasks. |
| Action compilation | Map conclusions into a fixed action dictionary. |
| Payload generation | Produce JSON bundles with a stable outer contract and dynamic action payloads. |
| MySQL task output | Produce SQL or table-ready records for downstream ingestion and auditing. |
| Validation | Reject unmappable, conflicting, or incomplete tasks with structured status output. |
| Delivery | Write final artifacts into `/Users/dongli/Downloads`. |

## Out of Scope

| Out of scope item | Why excluded |
|---|---|
| Raw ad diagnosis | Upstream skills should diagnose and conclude strategy first. |
| Direct Amazon Ads API execution | This skill compiles execution payloads but does not need to call the live API in its first version. |
| Creative generation | SB and SD creative authoring is broader than this execution compiler. |
| Reporting dashboards | This skill is for task compilation, not analytics presentation. |

## Primary Workflow

| Step | Behavior |
|---|---|
| 1 | Read upstream strategy conclusions. |
| 2 | Detect whether the requested work is campaign creation, campaign optimization, or both. |
| 3 | Detect target ad type: SP, SB, SD, or mixed. |
| 4 | Normalize the upstream conclusion into a standard action model. |
| 5 | Validate action compatibility, required fields, and conflicts. |
| 6 | Generate a machine-executable JSON task bundle. |
| 7 | Generate MySQL-compatible task records or SQL output. |
| 8 | Write final artifacts to `/Users/dongli/Downloads`. |

## Skill Triggering Rules

### Should Trigger

| Trigger case | Example |
|---|---|
| Explicit invocation | `$executing-amazon-ads-strategies` |
| Upstream-to-downstream handoff | "Convert these Amazon ad strategy conclusions into executable tasks." |
| Execution compilation request | "Generate SP/SB/SD ad task payloads from this strategy." |
| Automation handoff | "Turn these ad optimization conclusions into machine-readable tasks." |

### Should Not Trigger

| Non-trigger case | Reason |
|---|---|
| Pure diagnosis | No execution compilation requested. |
| Pure keyword mining | Upstream research only. |
| Pure product selection | Different domain. |
| API troubleshooting | Infrastructure rather than execution planning. |
| Analytics-only reporting | No action bundle needed. |

## Proposed Skill Directory

| Path | Role |
|---|---|
| `/Users/dongli/Documents/Skill/executing-amazon-ads-strategies/SKILL.md` | Main skill instructions and routing rules. |
| `/Users/dongli/Documents/Skill/executing-amazon-ads-strategies/agents/openai.yaml` | UI metadata and default prompt. |
| `/Users/dongli/Documents/Skill/executing-amazon-ads-strategies/references/upstream-strategy-patterns.md` | Common upstream input patterns and recognition notes. |
| `/Users/dongli/Documents/Skill/executing-amazon-ads-strategies/references/action-mapping-rules.md` | Mapping from conclusions to action dictionary. |
| `/Users/dongli/Documents/Skill/executing-amazon-ads-strategies/references/task-payload-contract.md` | Fixed outer envelope and dynamic payload rules. |
| `/Users/dongli/Documents/Skill/executing-amazon-ads-strategies/references/mysql-task-table.md` | MySQL task table design and field semantics. |
| `/Users/dongli/Documents/Skill/executing-amazon-ads-strategies/scripts/validate_task_payload.py` | Validate payload structure and action-specific fields. |
| `/Users/dongli/Documents/Skill/executing-amazon-ads-strategies/scripts/render_delivery_bundle.py` | Write final output artifacts to Downloads. |

## Architecture

| Layer | Responsibility | Notes |
|---|---|---|
| Intake layer | Accept upstream conclusions and detect intent | Must tolerate varied upstream phrasing. |
| Normalization layer | Translate upstream strategy into standard internal actions | This is the reuse core. |
| Validation layer | Enforce action compatibility and missing-field rules | Must prefer structured rejection over guessing. |
| Packaging layer | Emit JSON and MySQL-compatible outputs | Stable downstream handoff format. |
| Delivery layer | Copy artifacts to Downloads | User-facing completion contract. |

## Payload Contract

The payload contract should not be fully free-form. For downstream machine execution, the outer envelope is fixed while `payload` remains action-specific.

### Required Outer Fields

| Field | Type | Meaning |
|---|---|---|
| `task_id` | string | Unique execution task id. |
| `source_skill` | string | Upstream skill or workflow source. |
| `action_type` | string | One action from the allowed action dictionary. |
| `ad_type` | string | `SP`, `SB`, `SD`, or `MIXED` if the bundle holds several task rows. |
| `target_entity` | object | The entity to create or mutate, such as campaign, ad group, ad, keyword, product target, or placement scope. |
| `payload` | object | Dynamic action-specific body. |
| `validation` | object | Validation summary, warnings, and missing field notes. |
| `status` | string | Execution-readiness state. |

### Status Values

| Status | Meaning |
|---|---|
| `ready` | Action is valid for downstream execution. |
| `needs_review` | Action is structurally valid but risky. |
| `invalid_input` | Required upstream data is missing. |
| `unmapped_strategy` | Upstream conclusion could not be mapped to a supported action. |
| `unsupported_action` | Action is not valid for the detected ad type. |
| `conflict_detected` | The task conflicts with another task or its own target state. |

## Allowed Action Dictionary

The first version should keep action names fixed, even when payload fields vary.

| Action type | Applies to | Purpose |
|---|---|---|
| `create_campaign` | SP, SB, SD | Create a campaign. |
| `create_ad_group` | SP, SB, SD | Create an ad group or equivalent grouping unit. |
| `create_ad` | SB, SD | Create an ad or creative-level entity. |
| `create_target` | SP, SD | Create keyword, product, or audience targeting. |
| `add_negative_target` | SP, SB, SD | Add negative keyword or negative target constraints. |
| `update_bid` | SP, SD | Change keyword or target bid. |
| `update_budget` | SP, SB, SD | Change campaign budget. |
| `update_bid_strategy` | SP | Change dynamic bidding strategy. |
| `update_placement_modifier` | SP | Change placement modifier such as top-of-search adjustment. |
| `pause_entity` | SP, SB, SD | Pause a campaign, ad group, ad, or target. |
| `enable_entity` | SP, SB, SD | Re-enable a paused entity. |

## Validation Rules

| Validation layer | Rule |
|---|---|
| Structure validation | Outer fields must exist and be typed correctly. |
| Action validation | `action_type` must be from the allowed dictionary. |
| Ad-type validation | The action must be legal for the detected ad type. |
| Required-field validation | Required action-specific payload fields must exist. |
| Conflict validation | The same entity should not receive contradictory actions in one bundle. |
| Risk validation | Large budget increases, aggressive bid changes, or broad pauses should be flagged. |

## Error-Handling Rules

| Condition | Output behavior |
|---|---|
| Missing required fields | Emit `invalid_input` with missing-field details. |
| Strategy not recognized | Emit `unmapped_strategy` and preserve source fragment. |
| Action not supported for ad type | Emit `unsupported_action`. |
| Conflicting instructions | Emit `conflict_detected` with involved entities. |
| High-risk but valid change | Emit `needs_review` and retain executable payload. |

## MySQL Task Output

The user requires MySQL by default. The skill should therefore produce either SQL insert statements or clearly structured rows that can be inserted into a downstream MySQL task table.

### Recommended First-Version Table Shape

| Column | Purpose |
|---|---|
| `task_id` | Unique id for one executable task row. |
| `bundle_id` | Id shared across tasks produced from one upstream strategy batch. |
| `source_skill` | Upstream source identifier. |
| `ad_type` | SP, SB, SD, or MIXED. |
| `action_type` | Allowed action dictionary value. |
| `target_entity_type` | campaign, ad_group, ad, keyword, product_target, audience_target, placement, or similar. |
| `target_entity_key` | External or internal key used to identify the target entity. |
| `payload_json` | JSON body with action-specific fields. |
| `status` | Validation status. |
| `risk_level` | low, medium, high. |
| `created_at` | Timestamp generated during compilation. |

## Delivery Contract

All final artifacts must be written to `/Users/dongli/Downloads`.

### Required Deliverables

| Artifact | Path pattern | Purpose |
|---|---|---|
| Skill source directory copy | `/Users/dongli/Downloads/executing-amazon-ads-strategies/` | User review and later installation. |
| Skill archive | `/Users/dongli/Downloads/executing-amazon-ads-strategies.zip` | Easy transfer and backup. |
| JSON task bundle | `/Users/dongli/Downloads/amazon-ads-task-bundle-<YYYYMMDD-HHMMSS>.json` | Primary machine-executable output. |
| SQL task file | `/Users/dongli/Downloads/amazon-ads-task-bundle-<YYYYMMDD-HHMMSS>.sql` | MySQL ingestion output. |
| Summary file | `/Users/dongli/Downloads/amazon-ads-task-summary-<YYYYMMDD-HHMMSS>.md` | Fast human verification. |

## Naming Rules

| Artifact | Naming rule |
|---|---|
| Skill folder | `executing-amazon-ads-strategies` |
| Skill zip | `executing-amazon-ads-strategies.zip` |
| JSON bundle | `amazon-ads-task-bundle-<timestamp>.json` |
| SQL bundle | `amazon-ads-task-bundle-<timestamp>.sql` |
| Summary | `amazon-ads-task-summary-<timestamp>.md` |

Timestamps should be preferred over stuffing brand, ASIN, or ad type into filenames because upstream inputs may not always provide complete identity fields.

## Minimal Example Output Shape

```json
{
  "bundle_id": "bundle_20260621_083500",
  "generated_at": "2026-06-21T08:35:00+08:00",
  "tasks": [
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
        "missing_fields": []
      },
      "status": "ready"
    }
  ]
}
```

## Verification Strategy

This skill should be validated like documentation TDD.

### Baseline Failure Expectations

Before the skill exists, a general agent is likely to:

| Expected failure | Why it matters |
|---|---|
| Return advisory prose instead of executable tasks | Fails the core goal. |
| Invent inconsistent action names | Breaks downstream systems. |
| Omit validation status | Removes machine safety. |
| Ignore Downloads delivery | Breaks user handoff expectations. |

### First-Version Acceptance Cases

| Test case | Upstream strategy input | Expected output |
|---|---|---|
| Case 1 | Create SP automatic and manual campaigns with defined budget and core keywords | `create_campaign`, `create_ad_group`, and `create_target` tasks |
| Case 2 | Add negative search terms, increase top-of-search placement, switch SP bidding mode | `add_negative_target`, `update_placement_modifier`, and `update_bid_strategy` tasks |
| Case 3 | Pause low-performing SB or SD entities and reduce budget, with one conflicting object reference | `pause_entity`, `update_budget`, and at least one `conflict_detected` task status |

## First-Version Scope

The first version should cover SP, SB, and SD but keep the action set intentionally bounded.

| Version | Coverage |
|---|---|
| V1 | SP, SB, SD support with the fixed action dictionary defined above |
| Not in V1 | Direct API execution, complex creative generation, multi-table analytics joins, and unrestricted custom action names |

## Non-Functional Requirements

| Requirement | Expectation |
|---|---|
| Reusability | The skill should work across multiple upstream strategy skills. |
| Stability | The outer payload envelope must remain consistent. |
| Auditability | Outputs must support MySQL storage and later replay. |
| Safety | Unknown or conflicting instructions must return structured statuses rather than guessed actions. |
| Maintainability | Variant-specific rules should live in references files, not all inside `SKILL.md`. |

## Risks And Mitigations

| Risk | Mitigation |
|---|---|
| Upstream conclusion formats vary heavily | Create a dedicated `upstream-strategy-patterns.md` reference file. |
| SB and SD support may diverge from SP rules | Keep action legality validation ad-type-specific. |
| Flexible payloads may drift | Enforce outer envelope and validate dynamic payload fields with a script. |
| Downstream consumers may want stricter schemas later | Treat V1 as a bounded action compiler with room for stricter contracts in V2. |

## Implementation Notes For The Next Phase

| Next task | Goal |
|---|---|
| Create implementation plan | Break the skill into file creation, metadata generation, references drafting, validator script, and delivery bundling steps. |
| Build skill files | Create `SKILL.md`, `agents/openai.yaml`, references, and scripts. |
| Validate outputs | Run payload validator against representative examples. |
| Package deliverables | Copy final artifacts into `/Users/dongli/Downloads`. |
