# 工作流

## 1. 关键词分析

使用 live skill：

`C:\Users\Lenovo\.codex\skills\xiaohongshu-keyword-hotnote-analysis`

输入是社媒助手/设备助手导出的关键词热门笔记 Excel。输出：

- 关键词分析报告
- 全量逐篇拆解附录
- 封面 assets

## 2. 归档

使用 live skill：

`C:\Users\Lenovo\.codex\skills\xiaohongshu-keyword-report-archive`

归档分两层：

- 总结层：标题公式、选题规律、封面类型。
- 逐条层：每篇笔记一条标题记录、每篇笔记一条封面记录。

当用户说“爆款标题库”或“爆款封面库”时，必须做逐条层。

## 3. 弱爆/非爆样本

综合采集可能混入弱爆或非爆笔记。这些样本不删除。

处理方式：

- 在逐条标题/封面记录里标注 `反面教材/边界样本`。
- 在选题库里总结为什么没有爆。
- 不把弱样本升级成稳定公式，除非用户明确要反面标题库。

## 4. 更新 skill 的规则

如果本项目继续产生新判断，应先更新 `.codex\skills` 下 live skill，再同步副本到本 Agent 项目。
