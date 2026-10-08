# Keyword Archive Decision Rules

Use these rules when archiving Xiaohongshu keyword hot-note findings into Obsidian libraries.

## Core Principle

Keep every collected note useful, but do not put every note into every library.

- Analysis reports may summarize and cluster. Hot-note libraries must also preserve per-note records.
- Title library stores reusable title structures and per-note hot-title records.
- Topic library stores reusable demand, pain-point, scenario, and productizable angles.
- Cover library stores reusable visual structures and per-note hot-cover records with the original cover image when available.
- Weak or non-hot notes are not deleted. Keep them as negative or boundary samples and explain why they underperformed.

When the user asks to build or fix the hot title/cover library, create one Markdown record per collected note unless the user explicitly asks for summary-only output. Summary formulas and cover types are useful, but they do not replace per-note library entries.

## Title Library

Create a title-library entry when at least one condition is true:

- The structure appears in multiple notes under the keyword.
- One note is a strong low-follower breakout and the title structure is clearly generalizable.
- The title creates a repeatable click mechanism: named audience, time gap, risk warning, emotional relief, authority quote, number/list density, or concrete workplace scenario.

Do not create a stable title formula when:

- The title is empty.
- The title is generic and only works because the cover or body carries the hook.
- The title is a one-off meme, proper noun, or context-dependent phrase.

Use evidence levels:

- 强证据: 4 or more supporting notes, or several high-performing notes across accounts.
- 中证据: 2-3 supporting notes, or 1 strong note plus related boundary samples.
- 弱证据/观察: 1 note only; keep as observation unless the user asks to archive observations.

## Topic Library

Create topic-library entries for keyword-level demand clusters, not individual raw titles.

Good topic entries usually answer one of these:

- What exact problem is the search user trying to solve?
- What anxiety, identity shift, or workplace scenario keeps recurring?
- What can become a series, checklist, template, course module, or content pillar?
- What underperforming samples reveal about weak packaging?

Topic entries should include representative evidence from multiple notes and a clear production direction.

## Cover Library

Create cover-library entries for reusable visual structures, not for every downloaded image.

Archive only representative images, usually 1-3 per cover type. Copy them into the cover folder's `图片` subfolder and embed with Obsidian width syntax:

```markdown
![说明|300](图片/example.jpg)
```

Do not mix domain folders. Workplace keyword cover patterns should go under a workplace/keyword folder, not under `小学资料`.

## Negative and Boundary Samples

If 综合采集 includes weak or non-hot notes, keep them as a learning asset.

Archive weak samples when they reveal a useful failure pattern:

- Title has the right keyword but lacks a fresh hook.
- User pain is real but scenario is too vague.
- Cover carries text but has weak contrast, weak hierarchy, or unclear promise.
- The note relies on a generic phrase without proof, list density, or emotional specificity.

Do not call weak samples useless. Mark them as `反面教材/边界样本`.
