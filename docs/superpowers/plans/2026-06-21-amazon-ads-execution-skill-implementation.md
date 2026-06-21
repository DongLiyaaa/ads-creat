# Amazon Ads Execution Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `ads-creat` skill so it can convert upstream Amazon ad strategy conclusions into machine-executable SP, SB, and SD task payloads, validate them, and package deliverables into Downloads.

**Architecture:** The skill will be a compact instruction layer in `SKILL.md`, detailed rule files in `references/`, and two helper scripts in `scripts/`. The validator enforces a fixed outer payload envelope plus action-specific checks. The delivery script emits JSON, SQL, summary, and packaged skill artifacts into `/Users/dongli/Downloads`.

**Tech Stack:** Markdown, Python 3, JSON, MySQL-oriented SQL text output

---

### Task 1: Scaffold the skill layout

**Files:**
- Create: `/Users/dongli/Documents/Skill/ads-creat/SKILL.md`
- Create: `/Users/dongli/Documents/Skill/ads-creat/agents/openai.yaml`
- Create: `/Users/dongli/Documents/Skill/ads-creat/references/`
- Create: `/Users/dongli/Documents/Skill/ads-creat/scripts/`

- [ ] Step 1: Initialize the skill skeleton with `skill-creator`.
- [ ] Step 2: Inspect generated files and remove placeholder structure by overwriting with production content.
- [ ] Step 3: Generate `agents/openai.yaml` from the finalized skill metadata.

### Task 2: Author the skill instructions

**Files:**
- Modify: `/Users/dongli/Documents/Skill/ads-creat/SKILL.md`

- [ ] Step 1: Write concise frontmatter with a trigger-focused description.
- [ ] Step 2: Define when to use and when not to use the skill.
- [ ] Step 3: Document the execution workflow, action dictionary, validation behavior, and delivery contract.

### Task 3: Author the reference files

**Files:**
- Create: `/Users/dongli/Documents/Skill/ads-creat/references/upstream-strategy-patterns.md`
- Create: `/Users/dongli/Documents/Skill/ads-creat/references/action-mapping-rules.md`
- Create: `/Users/dongli/Documents/Skill/ads-creat/references/task-payload-contract.md`
- Create: `/Users/dongli/Documents/Skill/ads-creat/references/mysql-task-table.md`

- [ ] Step 1: Document upstream strategy shapes and recognition hints.
- [ ] Step 2: Define the allowed actions and how strategy phrases map into them.
- [ ] Step 3: Define the payload contract and MySQL task table fields.

### Task 4: Implement the helper scripts

**Files:**
- Create: `/Users/dongli/Documents/Skill/ads-creat/scripts/validate_task_payload.py`
- Create: `/Users/dongli/Documents/Skill/ads-creat/scripts/render_delivery_bundle.py`

- [ ] Step 1: Write the payload validator with fixed outer-field checks, action legality checks, and conflict detection.
- [ ] Step 2: Write the delivery bundler to create JSON, SQL, summary, zip, and a Downloads copy of the skill.
- [ ] Step 3: Make both scripts executable.

### Task 5: Validate and package

**Files:**
- Use: `/Users/dongli/Documents/Skill/ads-creat/scripts/validate_task_payload.py`
- Use: `/Users/dongli/Documents/Skill/ads-creat/scripts/render_delivery_bundle.py`

- [ ] Step 1: Run the validator on representative sample inputs and inspect the statuses.
- [ ] Step 2: Run the delivery bundler to emit Downloads artifacts.
- [ ] Step 3: Verify the expected files exist in `/Users/dongli/Downloads`.
