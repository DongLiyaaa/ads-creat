---
name: ads-creat
description: Use when an upstream Amazon advertising skill has already produced strategy conclusions and the current task is to convert those conclusions into machine-executable Sponsored Products, Sponsored Brands, or Sponsored Display ad tasks.
---

# Ads-Creat

## Overview

Use this skill to compile upstream Amazon Ads strategy conclusions into stable execution payloads for SP, SB, and SD. It is an execution compiler, not a diagnosis skill: it translates conclusions into action bundles, validates them, and prepares JSON, MySQL-oriented SQL, and Downloads deliverables.

## When to Use

Use this skill when:

- Another skill has already produced ad strategy conclusions.
- The current task is to turn those conclusions into executable tasks.
- The output must be machine-readable.
- The work concerns Sponsored Products, Sponsored Brands, or Sponsored Display.
- The final deliverables should be written to `/Users/dongli/Downloads`.

Do not use this skill when:

- The task is raw ad diagnosis or KPI analysis.
- The task is keyword research, product research, or competitor review without execution compilation.
- The task is direct Amazon Ads API debugging.
- The task only needs a human-readable strategy memo.

## Workflow

1. Confirm the upstream strategy conclusion already exists.
2. Detect whether the request is about creation, optimization, or a mixed bundle.
3. Detect whether the work targets `SP`, `SB`, `SD`, or more than one ad type.
4. Read [references/upstream-strategy-patterns.md](references/upstream-strategy-patterns.md) if the upstream conclusion format is ambiguous.
5. Read [references/action-mapping-rules.md](references/action-mapping-rules.md) to map conclusions into the fixed action dictionary.
6. Read [references/task-payload-contract.md](references/task-payload-contract.md) before finalizing the JSON bundle.
7. If MySQL output is required, read [references/mysql-task-table.md](references/mysql-task-table.md) and emit row-ready records or SQL inserts.
8. Run `scripts/validate_task_payload.py <bundle.json>` before treating the bundle as complete.
9. If delivery artifacts are required, run `scripts/render_delivery_bundle.py --skill-dir <skill-dir> --bundle-json <bundle.json>`.

## Fixed Action Dictionary

Only use these action names in the compiled output:

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

Do not invent new action names for the first version. If a strategy cannot be mapped into this dictionary, return `unmapped_strategy`.

## Output Rules

The output contract uses a fixed outer envelope with a dynamic inner payload. Every task should include:

- `task_id`
- `source_skill`
- `action_type`
- `ad_type`
- `target_entity`
- `payload`
- `validation`
- `status`

Valid statuses are:

- `ready`
- `needs_review`
- `invalid_input`
- `unmapped_strategy`
- `unsupported_action`
- `conflict_detected`

## Safety Rules

- Do not guess missing business fields.
- Do not silently coerce unsupported actions.
- Do not merge contradictory actions on the same target entity.
- Prefer structured invalid or review statuses over speculative payload generation.
- Treat MySQL as the default database when showing task-table examples.

## Reference Routing

Use only the reference file needed for the current step:

- Upstream pattern recognition: [references/upstream-strategy-patterns.md](references/upstream-strategy-patterns.md)
- Strategy-to-action compilation: [references/action-mapping-rules.md](references/action-mapping-rules.md)
- JSON contract and validation rules: [references/task-payload-contract.md](references/task-payload-contract.md)
- MySQL task table and SQL shape: [references/mysql-task-table.md](references/mysql-task-table.md)

## Helper Scripts

- Validate a bundle: `python3 scripts/validate_task_payload.py <bundle.json>`
- Package Downloads deliverables: `python3 scripts/render_delivery_bundle.py --skill-dir . --bundle-json <bundle.json>`
- Create a sample delivery bundle: `python3 scripts/render_delivery_bundle.py --skill-dir .`

## Example Requests

- "Use `$ads-creat` to convert this SP strategy conclusion into executable tasks."
- "These SB and SD optimization conclusions are ready. Compile the machine payload and SQL."
- "Turn these ad strategy outputs into a validated task bundle and write deliverables to Downloads."
