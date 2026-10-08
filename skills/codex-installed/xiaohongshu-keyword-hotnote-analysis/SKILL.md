---
name: xiaohongshu-keyword-hotnote-analysis
description: Analyze Xiaohongshu keyword-search hot-note Excel exports from Shemei/Shebei assistant and generate an Obsidian Markdown report. Use when the user provides a keyword such as "职场新人成长手册", a keyword hot-note collection folder or Excel file, or asks to analyze all popular notes under one keyword rather than all notes from one blogger account.
---

# Xiaohongshu Keyword Hotnote Analysis

## Purpose

Generate a keyword-level hot-note analysis report from a Xiaohongshu search/export Excel file. This skill is for cross-account keyword research, not single-account diagnostics.

Default paths for this user's workflow:

- Input folder: `C:\Users\Lenovo\Desktop\爆款笔记采集`
- Report output root: `C:\Users\Lenovo\Desktop\小红书\obsidian1\关键词库分析报告`
- Related title archive root: `C:\Users\Lenovo\Desktop\小红书\obsidian1\标题库`

Use `xiaohongshu-keyword-report-archive` after the report is accepted or when the user asks to archive report findings.

## Read First When Needed

- Read `references/field-mapping.md` before parsing a new Excel export.
- Read `references/report-template.md` before writing the final report.

## Workflow

1. Locate the source Excel.
   - If a folder is provided, use the only non-temporary `.xlsx` file.
   - Ignore Excel lock files beginning with `~$`.
   - If multiple candidate exports exist and the user did not specify one, list them and ask which keyword/export to use.

2. Parse and normalize the data.
   - Preserve the original workbook; never write back into the source Excel.
   - Normalize numeric fields: `点赞量`, `收藏量`, `评论量`, `分享量`, `粉丝数`, `图片数量`.
   - Normalize text fields: `笔记标题`, `笔记内容`, `笔记话题`, `博主昵称`, `笔记链接`, `笔记封面链接`, `笔记图片链接`.
   - Use `笔记话题` when present. Otherwise extract tags from `笔记内容` with `#([^#]+?)\[话题\]#`.
   - Treat `nan` and empty titles/content as data quality facts; do not infer a cause.

3. Establish keyword context.
   - Infer the keyword from the filename if obvious; otherwise ask or record `待确认`.
   - Distinguish this report from an account report: the unit of analysis is a search keyword and the competitive content surface under that keyword.

4. Compute basic metrics.
   - Total notes, unique accounts, date range, median/mean/max likes, max collects, max shares.
   - Like/collect/share distributions.
   - Low-follower outliers: high likes from accounts with low follower counts.
   - Collection-heavy notes: high `收藏量 / 点赞量`, especially for reusable templates, lists, scripts, manuals, and guides.
   - Image-count distribution and high/low performance by image count.

5. Cluster search intent.
   - Cluster by concrete demand, not just surface words. Typical workplace-newcomer clusters include:
     - 人情世故 / 社会化
     - 新人成长 / 学生转职场
     - 心态边界 / 反内耗
     - 沟通汇报 / 话术
     - 方法清单 / 习惯细节
     - 防坑 / 心眼子 / 防背刺
   - For every cluster, calculate count, median likes, max likes, representative top notes, and warning notes.
   - Identify content gaps: high-demand intent with weak current supply, low-quality current supply, or clear productizable need.

6. Analyze titles.
   - Extract formulas from high-performing notes and contrast with low-performing or generic titles.
   - Treat keyword match separately from click appeal. A title can match the keyword but still be weak.
   - Record formulas with examples, applicable intent, and risk.
   - Do not overfit one viral note as a stable formula unless similar notes support it.
   - Do not treat the formula section as the only useful output. For keyword hot-note exports where the user states all rows are hot notes, or when the export has 150 rows or fewer, create a full per-note teardown appendix covering every row. The main report can summarize stable formulas, but the appendix must preserve single-note value.
   - The per-note appendix should include, for each note: title, account, likes/collects/comments/shares/followers/image count, title structure, search intent/content cluster, reusable hook, archive suggestion, and risk/limit. Notes that are not strong title-formula candidates should still be kept as cover, body-structure, search-intent, or boundary samples.

7. Analyze covers and image sets when useful.
   - Download representative images only when writing the full report, using the same safe method as the existing Xiaohongshu account-analysis skill: request headers with `Referer: https://www.xiaohongshu.com/`.
   - Prioritize: top 15-20 by likes, top collection-heavy notes, low-follower outliers, and bottom nonzero notes.
   - Build cover grids and note-set grids for the report assets folder.
   - Do not copy images into Obsidian template libraries during analysis; archiving is a separate step.

8. Write the report.
   - Use `references/report-template.md`.
   - Save to `C:\Users\Lenovo\Desktop\小红书\obsidian1\关键词库分析报告`.
   - Filename format: `关键词分析_[关键词]_[YYYY-MM-DD].md`.
   - If image assets are created, place them next to the report in `[报告文件名]_assets`.

9. Keep conclusions bounded.
   - This is a search-result snapshot, not a platform-wide truth.
   - Do not call old content "currently trending" unless recency and search-rank evidence support it.
   - Separate proven patterns, promising hypotheses, and single-note phenomena.

## Output Contract

The final report must include:

- Keyword, source Excel filename, analysis date, row count, unique account count, and selected interaction metric.
- Search-intent clusters with data support.
- Top notes by likes, collection-heavy notes, and low-follower breakout notes.
- Reusable title formulas with examples.
- A linked full per-note teardown appendix when the dataset is small enough to review completely or when the user explicitly says all notes are valuable hot notes.
- Cover/image-set observations if images were inspected.
- Opportunities for original content/product packaging.
- A "可归档条目候选" section listing title formulas and optional topic/cover findings for the archive skill.

Do not write to `标题库`, `选题库`, or `封面模版库` from this skill unless the user explicitly asks to combine analysis and archive in one run.
