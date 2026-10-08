# 小红书爆款拆解Agent

> 把小红书关键词采集表自动拆解成：关键词分析报告、逐篇拆解附录、爆款标题库、爆款封面库和选题库，供内容创作复用。

| 项目状态 | 技术栈 |
| --- | --- |
| ✅ 可用（已在真实关键词样本上验证） | Codex Skills、Python |

> 本项目为个人 AI 辅助开发（vibe coding）作品。仓库只包含源码与文档，运行数据、账号配置、密钥均已排除；文中出现的本机路径仅供参考，使用时请按自己的环境修改。

---

这是「爆款笔记拆解」Agent 的项目入口目录。它负责把小红书采集表拆成：

- 关键词分析报告
- 90 篇以内全量逐篇拆解附录
- 爆款标题库逐条记录
- 爆款封面库逐条记录
- 选题库规律沉淀
- 弱爆/非爆样本反面教材

## 当前实际调用位置

Codex 自动发现 skill 仍然依赖 `.codex\skills`，不要把这些目录从原位置移走：

- `C:\Users\Lenovo\.codex\skills\xiaohongshu-keyword-hotnote-analysis`
- `C:\Users\Lenovo\.codex\skills\xiaohongshu-keyword-report-archive`

本项目下的 `skills\codex-installed\` 是归档副本，用于集中管理、查看和交接；如要更新可调用 skill，应同步更新 `.codex\skills` 下的原始安装目录。

## 项目结构

- `config\agent-paths.json`：关键路径索引
- `skills\codex-installed\`：当前 Codex skills 副本
- `skills\legacy-claude-skills\`：旧 Claude skill 参考副本
- `docs\`：说明和流程文档
- `scripts\`：项目级辅助脚本
- `HANDOFF.md`：交接状态

## 当前关键词样例

关键词：`职场新人成长手册`

已验证产物：

- 报告：`C:\Users\Lenovo\Desktop\小红书\obsidian1\关键词库分析报告\关键词分析_职场新人成长手册_2026-07-27.md`
- 逐篇附录：`C:\Users\Lenovo\Desktop\小红书\obsidian1\关键词库分析报告\关键词分析_职场新人成长手册_2026-07-27_逐篇拆解附录.md`
- 标题库：`C:\Users\Lenovo\Desktop\小红书\obsidian1\标题库\职场新人成长手册`
- 封面库：`C:\Users\Lenovo\Desktop\小红书\obsidian1\封面模版库\职场新人成长手册`
- 选题库：`C:\Users\Lenovo\Desktop\小红书\obsidian1\选题库\职场新人成长手册`

## 关键口径

分析报告可以总结共性；爆款标题库和爆款封面库必须逐条记录。公式总结和封面类型总结不能替代逐条样本。

弱爆/非爆样本不删除，标为反面教材/边界样本。
