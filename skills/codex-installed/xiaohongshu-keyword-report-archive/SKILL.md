---
name: xiaohongshu-keyword-report-archive
description: Archive findings from Xiaohongshu keyword hot-note analysis reports into the user's Obsidian title/topic/cover libraries. Use after a keyword report is generated or when the user asks to store keyword hot-title formulas, search-intent findings, or cover patterns from a keyword such as "职场新人成长手册"; default first-stage behavior archives title formulas only unless the user explicitly approves broader library writes.
---

# Xiaohongshu Keyword Report Archive

## Purpose

Convert a keyword hot-note analysis report into reusable Obsidian library entries. This skill archives cross-account keyword findings, not single-account account-analysis findings.

Default paths for this user's workflow:

- Keyword reports: `C:\Users\Lenovo\Desktop\小红书\obsidian1\关键词库分析报告`
- Title library root: `C:\Users\Lenovo\Desktop\小红书\obsidian1\标题库`
- Existing primary-school title folder: `C:\Users\Lenovo\Desktop\小红书\obsidian1\标题库\小学资料`
- Current workplace keyword title folder: `C:\Users\Lenovo\Desktop\小红书\obsidian1\标题库\职场新人成长手册`
- Topic library root: `C:\Users\Lenovo\Desktop\小红书\obsidian1\选题库`
- Cover library root: `C:\Users\Lenovo\Desktop\小红书\obsidian1\封面模版库`

## Safety Boundary

Default first-stage archive behavior:

1. Archive title formulas from the keyword report into `标题库\[关键词]\`.
2. Update this skill's `references/keyword_archive_manifest.json`.
3. Do not write topic-library or cover-library entries unless the user explicitly asks for that broader archive step.

Never overwrite an existing library entry silently. If a same-name file exists, merge intentionally or create a distinct filename with a concise suffix.

## Read First When Needed

- Read `references/title-entry-template.md` before creating title entries.
- Read `references/archive-rules.md` before deciding whether to merge, skip, or create a new entry.
- Read `references/keyword-archive-decision-rules.md` when archiving title, topic, cover, or negative/boundary findings from a keyword hot-note report.
- Prefer `scripts/archive_keyword_findings.py` for repeatable keyword archives when the source Excel, report, and per-note appendix are available.
- Prefer `scripts/archive_keyword_per_note_records.py` when the user asks for hot-title or hot-cover libraries to record every note one by one. Formula/type summaries do not replace per-note title and cover records.

## Workflow

1. Locate the source report.
   - If a specific report path is given, use it.
   - If only a keyword is given, search `关键词库分析报告` for the newest `关键词分析_[关键词]_*.md`.
   - If multiple plausible reports exist, list candidates and ask which one to archive.

2. Confirm the keyword archive folder.
   - For `职场新人成长手册`, write title entries to:
     `C:\Users\Lenovo\Desktop\小红书\obsidian1\标题库\职场新人成长手册`
   - For other keywords, create `标题库\[关键词]` under the title library root.
   - Keep `标题库\小学资料` for the existing primary-school title formulas. Do not move those files unless the user explicitly asks.

3. Extract archive candidates.
   - Prefer the report section `可归档条目候选`.
   - If that section is missing, extract from `标题公式` and use conservative judgment.
   - Only create entries for patterns supported by multiple notes or by a very strong low-follower breakout note with clear limitations.
   - Do not archive raw titles as standalone formulas unless the formula/generalizable structure is stated.

4. Check existing entries.
   - Read filenames in the target keyword folder.
   - For every candidate, compare formula structure, not exact wording only.
   - If a candidate matches an existing entry, merge new evidence into that file.
   - If similar but not identical, create a new file and add `参见[[...]]`.

5. Write title entries.
   - Use `references/title-entry-template.md`.
   - Include: formula name, type, keyword, search intent, source report, evidence notes, applicable conditions, risks, representative original titles, and first archive date.
   - Keep full original title examples short and bounded; do not paste full note bodies.

6. Update manifest.
   - Create or update `references/keyword_archive_manifest.json`.
   - Record report path, keyword, archived date, and entries written.

7. Report results.
   - List every created/merged/skipped entry.
   - State which libraries were modified.
   - State whether topic/cover archive remains pending.

## Topic and Cover Archive Rules

Use broader archive only after the user explicitly asks or grants judgment authority over title/topic/cover classification.

For topic entries:

- Write keyword-level demand patterns, not account-level tactics.
- Include evidence from multiple accounts when available.
- Keep limitations visible: snapshot nature, possible search-rank bias, and sample-size limits.

For cover entries:

- Create a keyword or domain folder only when needed, such as `封面模版库\职场资料`.
- Copy only representative images, not every downloaded image.
- Do not mix workplace cover templates into `封面模版库\小学资料`.

For weak or non-hot rows in a comprehensive keyword collection:

- Do not delete them.
- Keep them as `反面教材/边界样本` when they reveal why a note did not become a strong hot note.
- Archive the lesson in the topic library, not the title library, unless the title structure itself is useful as a negative example.

## Output Contract

After a successful title-only archive, the target folder must contain one Markdown file per reusable title formula. The keyword report itself remains in `关键词库分析报告`; it is not moved into the title library.
## Broader Archive Contract

After a successful broader archive, the title/topic/cover folders should each contain one Markdown file per reusable pattern, and the cover folder should contain only representative copied images under `图片`.
## Per-Note Hot Library Contract

When the user asks for a hot-title library or hot-cover library rather than only an analysis report, create one per-note Markdown record for every collected note in the title and cover folders, plus an index. Mark weak or non-hot samples as boundary/negative samples, but do not delete them. Formula summaries and cover-type summaries are useful, but they do not replace per-note records.
