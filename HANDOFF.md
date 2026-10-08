# 小红书爆款拆解Agent 交接

最后更新时间：2026-07-28 21:20:00 +08:00

## 当前状态

本 Agent 项目已集中放入：

`C:\Users\Lenovo\Desktop\Codex Agent合集\小红书爆款拆解Agent`

本目录是 Agent 项目总入口。Codex 实际调用的 skill 仍保留在 `.codex\skills` 原位置，不能直接搬走，否则 Codex 可能无法自动发现。

## 已迁入/归档的内容

- Codex skill 副本：
  - `skills\codex-installed\xiaohongshu-keyword-hotnote-analysis`
  - `skills\codex-installed\xiaohongshu-keyword-report-archive`
- 旧 Claude skill 参考副本：
  - `skills\legacy-claude-skills\xiaohongshu-analysis-skill`
  - `skills\legacy-claude-skills\xiaohongshu-report-archive-skill`
- 项目入口：
  - `README.md`
  - `config\agent-paths.json`
  - `docs\workflow.md`
  - `scripts\检查Agent状态.cmd`

## 仍在原位的真实调用文件

- `C:\Users\Lenovo\.codex\skills\xiaohongshu-keyword-hotnote-analysis`
- `C:\Users\Lenovo\.codex\skills\xiaohongshu-keyword-report-archive`

更新 skill 时优先更新上述真实调用位置，再同步副本到本 Agent 项目。

## 当前已验证业务成果

关键词：`职场新人成长手册`

- 关键词报告已生成。
- 90 篇逐篇拆解附录已生成。
- 标题库已补齐 90 条逐条标题 + 1 个索引。
- 封面库已补齐 90 条逐条封面 + 1 个索引。
- 封面图已补齐 90 张逐条封面图。
- 选题库已有 7 个规律条目，包含弱爆/非爆反面样本。

详见 Obsidian 项目交接：

`C:\Users\Lenovo\Desktop\小红书\obsidian1\HANDOFF.md`

## 后续前三步

1. 新对话接手时先读取本文件、`README.md` 和 `config\agent-paths.json`。
2. 再读取 `.codex\skills` 下两个真实 skill 的 `SKILL.md`，不要只看本项目副本。
3. 如果继续处理新关键词，先生成分析报告和逐篇附录，再用逐条归档脚本补标题库/封面库。

## 禁止事项

- 不要从 `.codex\skills` 移走已安装 skill。
- 不要把分析报告总结层当成爆款标题库/封面库。
- 不要删除弱爆/非爆样本。
- 不要修改源 Excel。
