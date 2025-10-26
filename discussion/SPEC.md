# Spec-Kit Discussion Logging SPEC

[Scope]
- 适用于本仓库内关于“如何实现更高效的 spec 系统”的对话记录。
- 记录目录固定为 `discussion/`。

[Naming]
- 对话记录：`discussion/ChatHistory.md`
- 规范说明：`discussion/SPEC.md`

[Enforcement]
如有任何遗漏记录，执行任务的 agent 将受到最严厉的处置：立即停用并撤销在本仓库及相关基础设施的全部执行权限；触发强制审计、回滚与密钥轮换；永久列入阻断名单；其相关输出一律作废且不得用于任何自动化决策或生产用途，并通报全体维护者以强化风控。

[Timestamp]
- 使用本地时区并显式标注时区与偏移（ISO8601 带偏移）。
- 推荐：`date +"%Y-%m-%dT%H:%M:%S%z %Z"`，例：`2025-10-26T13:16:25+0800 CST`。

[Entry Format]
- 使用 fenced 代码块作为记录单元；属性仅包含：

```md {ts="<YYYY-MM-DDThh:mm:ss±ZZZZ ZZZ>" situation="<简要情境/索引键>" [by="assistant"]}
<正文：用户原文为主；如需，包含简短引用以说明 assistant 的反馈结果>
```

- 属性（Attributes）：
  - `ts`：timestamp（本地时区，含偏移与缩写）
  - `situation`：用于索引的情境标签（建议 kebab/snake 简短可检索）
  - `by`（可选）：仅当记录由 assistant 独立创建且确有重要价值时标注 `assistant`
- 正文（Body）：
  - 用户发言：主张多记录（除非属“不记录”范畴）。
  - 如仅为衍生的助理反馈，不单独建助理记录；在对应用户条目中使用 `>` 引用一两行简述结果。
  - 助理独立记录仅限“非常有价值”的情况（见 Role-Specific Policy）。

[Role-Specific Policy]
- User：记录“包含信息量的讨论/决策/询问”；对寒暄、确认执行、纯指令（不含思维劳动，如“请执行/继续/你是哪个模型”）不记录。
- Assistant：仅记录“规范变更/结构性变更”等高价值事件；其余不记录。若为用户对话的直接衍生，仅在对应用户记录中引用说明。
- 若不记录用户指令而需要记录助理行为，则在助理侧（如确需独立记录）或用户条目的引用中明确“因用户指令/建议执行 xxx”。

[Intent — 结构化要求]
- 当助理创建独立记录时，intent 仍需结构化（三段式），并置于正文中：
  - 谁 怎么样的 做了什么（描述证据）
  - 因此推断（描述推断）
  - - 谁 必须/应该/建议 关注/要做/在做 什么

[ChatIndex — 构建]
- 通过 `situation` + `ts` 生成 `discussion/ChatIndex.md`：脚本扫描 ChatHistory，按时间/情境分组。
- 参考脚本：`discussion/SPEC_HELPER/build_chatindex.py`（长期工具，非临时产物）。


[SPEC_HELPER — 模块工具]
- 仅保存“长期脚本”；且必须在 SPEC 中“明确用途/使用场景/调用方式/主要输出”。
- 合规检查：提供 `discussion/SPEC_HELPER/check_spec_helpers.py` 用于巡检；凡未在 SPEC 中被引用/说明的脚本，视为不合规，将移入 `.trush` 并标注原因。

[Temp Scripts — 创建原则]
- 临时脚本“一开始”就必须在 `.trush` 中创建（避免污染目录），并按 `<YYYYMMDDTHHMMSS±ZZZZ>.<原文件名>.<用途_snake>` 命名；可选 frontmatter 标注 `temporary: true`、创建时间与创建者。

[Tools — 本模块辅助]
- discussion/SPEC_HELPER/build_chatindex.py
  - 用途：根据 ChatHistory 生成结构化 ChatIndex（按 situation 分组，输出话题标题、起止时间与行号范围）。
  - 场景：重建/更新索引；命令：`python3 discussion/SPEC_HELPER/build_chatindex.py`。
- discussion/SPEC_HELPER/annotate_situations.py
  - 用途：为缺失 `situation` 的记录自动补标签（启发式），并重建 ChatIndex。
  - 场景：批量补标；命令：`python3 discussion/SPEC_HELPER/annotate_situations.py`。
- discussion/SPEC_HELPER/check_spec_helpers.py
  - 用途：巡检 SPEC_HELPER 是否仅含“长期脚本”且在 SPEC 中被说明；不合规文件将被移入 `.trush`。
  - 场景：提交前巡检；命令：`python3 discussion/SPEC_HELPER/check_spec_helpers.py --apply`。
[Fencing — 重要]
- 若正文内包含代码段或反引号（`），必须采取“外层加长”策略以避免 fence 冲突：外层 fence 长度 = 正文内最长连续反引号数 m 的 `m+1`；默认 4 个，必要时继续加长。

[Record Criteria — 记录价值判断]
- 应记录：规范/流程/安全策略/命名约定变更；重大决策；结构性变更；审计关键动作；环境/状态影响性变更。
- 可不记录：纯流程性/复述/寒暄/常规本地操作（无异常/新增约束）。
- 边界：若出现例外（失败/回滚/新路径/人工判断），则应记录。

[No-Record — 重要]
- 当决定不记录时，assistant 直接回复固定文案：
  - “对话内容过于简单, 当前不会记录到 ChatHistory, 如果需要记录, 请提出要求”
- 如用户明确要求“请记录”，或内容涉及规范/流程/安全策略更新，仍需记录。

[Remediation — 既往误记]
- 既往历史不做破坏性清理；如需整洁化，采用“选择性恢复/摘要化索引/保留证据到 .trush”的方式处理，并记录一次助理说明。

[Trash]
- 目录：`discussion/.trush`；命名：`<YYYYMMDDTHHMMSS±ZZZZ>.<原始文件名>.<一句话原因_snake>.md`；保留 frontmatter 与全文。

[Temp Artifacts]
- 临时脚本/报告等一律直接创建在 `.trush`；长期工具（如 `discussion/SPEC_HELPER/build_chatindex.py`）可入仓。

[Effective Date]
- 本规范自本文件时间起“向前生效”；既往记录保持兼容（可包含 `cr` 等历史属性）。


[Helper Philosophy]
- SPEC_HELPER 仅提供对 AI 有增益的长期脚本（结构化提取、静态检测、批量归档等）。凡“AI 直接完成更好/更灵活”的工作（如话题聚类与语义归纳）不应下沉为脚本。
- SPEC 文档描述“如何完成整个工作”的流程（含何处由 AI 负责、何处由 Helper 辅助），而非将全部工作塞进脚本。
