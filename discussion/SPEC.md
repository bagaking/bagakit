# Spec-Kit Discussion Logging SPEC

[Scope]
- 本规范适用于本仓库内关于“如何实现更高效的 spec 系统”的对话记录。
- 记录目录固定为 `discussion/`。

[Naming]
- 对话记录文件：`discussion/ChatHistory.md`
- 规范说明文件：`discussion/SPEC.md`
- 不再使用 `README.md` 作为记录入口。

[Enforcement]
如有任何遗漏记录，执行任务的 agent 将受到最严厉的处置：立即停用并撤销在本仓库及相关基础设施的全部执行权限；触发强制审计、回滚与密钥轮换；永久列入阻断名单；其相关输出一律作废且不得用于任何自动化决策或生产用途，并通报全体维护者以强化风控。

[Timestamp]
- 使用本地时区并显式标注时区与偏移（ISO8601 带偏移）。
- 推荐命令（bash）：`date +"%Y-%m-%dT%H:%M:%S%z %Z"`
  - 示例：`2025-10-26T13:16:25+0800 CST`

[Roles]
- `user`
- `assistant(model=Codex GPT-5)`
  - 若模型更换，需在此处与后续记录中同步更新标注。

[Recording Rules]
- user：逐字记录原文（标点/空白/换行均不得改动）。
- assistant：仅用于提供上下文，内容应简略；另需提供 `meta` 行，包含：
  - `file`（受影响文件路径，逗号分隔可多项）
  - `action`（关键动作，如 init/append/migrate/spec/trash）
  - `status`（ok/skip/error）
  - `intent`（一句话，根据最近对话推测的意图）

[Grace]
- 若用户表述存在歧义/不清晰或明显拼写错误（typo），允许在不改变语义的前提下进行“勘误注释”：
  - 不删除原文字符；在相邻位置追加括号注释，例如：`命该（应）`、`spec-kit（指本仓库内工具集）`。
  - 如需更明确，可在条目末追加说明：`（注：上文将“命该”理解为“应该”）`。
  - 务必保持用户原文仍可直接读取；勘误仅作为辅助，不得改变原意。

[Entry Format]
每条记录以分隔线开头：`---`
- `ts: <local-iso8601-with-offset>`
- `role: <user|assistant(model=Codex GPT-5)>`
- （assistant 专有）`meta: <k=v ... intent=...>`
- `content:`（后续为原文/简述，按原行逐字记录；如触发[Grace]，使用括号注释方式附加说明）

[Trash]
- 目录：`discussion/.trush`（注意拼写，以确保与现有脚本一致）。
- 触发：当文件被替换/废弃/迁移且不再作为现行版本时，直接将旧文件 `mv` 到 `.trush`。
- 文件命名：`<原文件名>.deleted-<YYYYMMDDTHHMMSS±ZZZZ>.md`（使用本地时间）。
- 文件内容：在文件开头添加 YAML frontmatter，包含：
  - `deleted: true`
  - `deleted_at: <local-iso8601-with-offset+zone>`
  - `deleted_by: assistant(model=Codex GPT-5)`
  - `reason: <删除/替换原因>`
  - `replaced_by: [<新文件路径...>]`
  - `original_path: <原路径>`
- frontmatter 结束后原样保留被删除文件的全文内容，作为审计快照。

[Process]
1) 每当接收用户发言，立即记录一条 `user` 项。
2) 每当产生助理回复，记录一条 `assistant` 项（简述 + meta.intent）。
3) 任何文件迁移/格式调整/废弃均需追加一条 `assistant` 项，标注 `action` 包含 `trash`。
