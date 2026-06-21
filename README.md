# ads-creat

`ads-creat` is a Codex skill for turning upstream Amazon Ads strategy conclusions into stable, machine-executable execution tasks.

This repository is designed primarily for AI agents, not for marketing copy.

## What This Skill Is For

Use `ads-creat` when another skill has already produced conclusions such as:

- create a new SP manual campaign
- add negative targets
- lower bids
- raise budget
- switch SP bid strategy
- adjust top-of-search placement
- pause low-efficiency entities

`ads-creat` takes those conclusions and compiles them into:

- structured JSON task bundles
- MySQL-oriented SQL task inserts
- validation results for missing fields, unsupported actions, and conflicts

It is an execution compiler, not a diagnosis skill.

## What This Skill Is Not For

Do not use this repository as the primary place for:

- raw ad diagnosis
- search-term analysis
- keyword mining
- product selection
- competitor intelligence
- direct Amazon Ads API execution

Those jobs should happen upstream. This skill starts after strategy has already been decided.

## Core Contract

The skill keeps a fixed outer task envelope and allows dynamic action payloads.

Each task is compiled around:

- `task_id`
- `source_skill`
- `action_type`
- `ad_type`
- `target_entity`
- `payload`
- `validation`
- `status`

Supported action names are intentionally fixed in v1:

- `create_campaign`
- `create_ad_group`
- `create_ad`
- `create_target`
- `add_negative_target`
- `update_bid`
- `update_budget`
- `update_bid_strategy`
- `update_placement_modifier`
- `pause_entity`
- `enable_entity`

If upstream strategy cannot be safely mapped into those actions, the skill should return a structured non-ready status instead of guessing.

## Repository Layout

```text
ads-creat/
  SKILL.md
  agents/openai.yaml
  references/
    action-mapping-rules.md
    mysql-task-table.md
    task-payload-contract.md
    upstream-strategy-patterns.md
  scripts/
    render_delivery_bundle.py
    validate_task_payload.py
docs/superpowers/
  plans/
  specs/
README.md
LICENSE
```

## Files AI Agents Should Read First

Start in this order:

1. `ads-creat/SKILL.md`
2. `ads-creat/references/action-mapping-rules.md`
3. `ads-creat/references/task-payload-contract.md`
4. `ads-creat/references/mysql-task-table.md`
5. `ads-creat/scripts/validate_task_payload.py`

Read `upstream-strategy-patterns.md` when the upstream strategy format is ambiguous.

## Validation

Before declaring a bundle executable, run:

```bash
python3 ads-creat/scripts/validate_task_payload.py <bundle.json>
```

This validator checks:

- required task fields
- supported ad types
- supported action types
- action-specific payload requirements
- same-entity conflicts
- risk warnings that should downgrade `ready` to `needs_review`

## Delivery

To render delivery artifacts into the system Downloads path, run:

```bash
python3 ads-creat/scripts/render_delivery_bundle.py --skill-dir /absolute/path/to/ads-creat
```

This emits:

- a JSON bundle
- a SQL file
- a summary markdown file
- a copied skill folder
- a zipped skill package

## Installation Hint

If you want to install this skill into Codex from GitHub, install the skill folder itself, not the whole repository as a generic doc repo.

The important payload lives in:

```text
ads-creat/
```

## License

MIT
