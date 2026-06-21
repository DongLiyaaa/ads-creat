# ads-creat

[English](./README.md)

`ads-creat` 是一个 Codex skill，用于把上游 Amazon Ads 策略结论转换成稳定、可机器执行的任务。

这个仓库主要面向 AI agent，而不是市场宣传文案。

## 这个 Skill 用来做什么

当另一个 skill 已经产出类似以下结论时，使用 `ads-creat`：

- 新建一个 SP 手动广告活动
- 添加否定投放
- 下调竞价
- 提高预算
- 切换 SP 竞价策略
- 调整搜索首页广告位系数
- 暂停低效率实体

`ads-creat` 会把这些结论编译成：

- 结构化 JSON 任务包
- 面向 MySQL 的 SQL 任务插入语句
- 对缺失字段、不支持动作、冲突动作的校验结果

它是一个执行编译器，不是诊断 skill。

## 这个 Skill 不负责什么

不要把这个仓库作为以下工作的主要入口：

- 原始广告诊断
- 搜索词分析
- 关键词挖掘
- 选品
- 竞品情报分析
- 直接执行 Amazon Ads API

这些工作应该在上游完成。这个 skill 的起点，是“策略已经决定”之后。

## 核心契约

这个 skill 保持固定的外层任务结构，内部 `payload` 允许按动作动态变化。

每个任务都围绕以下字段编译：

- `task_id`
- `source_skill`
- `action_type`
- `ad_type`
- `target_entity`
- `payload`
- `validation`
- `status`

v1 支持的动作名固定为：

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

如果上游策略无法安全映射到这些动作中，skill 应返回结构化的非就绪状态，而不是猜测。

## 仓库结构

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
README.md
README.zh-CN.md
LICENSE
```

## AI Agent 推荐阅读顺序

建议按这个顺序阅读：

1. `ads-creat/SKILL.md`
2. `ads-creat/references/action-mapping-rules.md`
3. `ads-creat/references/task-payload-contract.md`
4. `ads-creat/references/mysql-task-table.md`
5. `ads-creat/scripts/validate_task_payload.py`

如果上游策略格式不清晰，再去读 `upstream-strategy-patterns.md`。

## 校验

在声明任务包可执行之前，先运行：

```bash
python3 ads-creat/scripts/validate_task_payload.py <bundle.json>
```

这个校验器会检查：

- 必填任务字段
- 支持的广告类型
- 支持的动作类型
- 动作级 `payload` 要求
- 同一实体上的冲突动作
- 是否存在应把 `ready` 降级为 `needs_review` 的风险警告

## 交付

如果需要把交付物写入系统 `Downloads` 路径，运行：

```bash
python3 ads-creat/scripts/render_delivery_bundle.py --skill-dir /absolute/path/to/ads-creat
```

这个脚本会输出：

- 一个 JSON 任务包
- 一个 SQL 文件
- 一个 Markdown 摘要文件
- 一个复制出的 skill 文件夹
- 一个打包好的 ZIP skill 包

## 安装提示

如果你要从 GitHub 把这个 skill 安装到 Codex，请安装 skill 目录本身，而不是把整个仓库当成普通文档仓库安装。

真正的 skill 载荷在：

```text
ads-creat/
```

## 协议

MIT
