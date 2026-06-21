# MySQL Task Table

Use this file when the compiled bundle also needs SQL or row-ready MySQL output.

## Recommended Table

```sql
CREATE TABLE amazon_ads_execution_tasks (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  bundle_id VARCHAR(64) NOT NULL,
  task_id VARCHAR(64) NOT NULL,
  source_skill VARCHAR(128) NOT NULL,
  ad_type ENUM('SP', 'SB', 'SD', 'MIXED') NOT NULL,
  action_type VARCHAR(64) NOT NULL,
  target_entity_type VARCHAR(64) NOT NULL,
  target_entity_key VARCHAR(255) NOT NULL,
  payload_json JSON NOT NULL,
  status VARCHAR(32) NOT NULL,
  risk_level VARCHAR(16) NOT NULL DEFAULT 'low',
  created_at DATETIME NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_task_id (task_id),
  KEY idx_bundle_id (bundle_id),
  KEY idx_action_type (action_type),
  KEY idx_target_entity_key (target_entity_key),
  KEY idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Field Semantics

| Column | Meaning |
|---|---|
| `bundle_id` | Shared id for one compiled execution batch. |
| `task_id` | Unique id for one executable task row. |
| `source_skill` | Upstream skill or workflow source. |
| `ad_type` | SP, SB, SD, or MIXED. |
| `action_type` | Fixed action dictionary value. |
| `target_entity_type` | Campaign, ad group, ad, keyword, product target, audience target, or placement scope. |
| `target_entity_key` | Stable key for downstream mutation targeting. |
| `payload_json` | Dynamic JSON body for the action. |
| `status` | Validation state from the compiler. |
| `risk_level` | Low, medium, or high based on the compiled change. |
| `created_at` | Compilation timestamp. |

## SQL Output Rules

- Emit one `INSERT` row per compiled task.
- Store the dynamic body in `payload_json`.
- Keep `risk_level` deterministic from the compiler's validation output.
- If a task is not `ready`, still emit the row when the downstream system needs full auditability.
