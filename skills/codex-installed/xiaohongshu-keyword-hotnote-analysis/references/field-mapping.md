# Field Mapping

Use this reference for keyword hot-note Excel exports from Shemei/Shebei assistant.

## Expected Columns

Common columns:

- `笔记链接`
- `笔记标题`
- `笔记内容`
- `点赞量`
- `收藏量`
- `评论量`
- `分享量`
- `发布时间`
- `更新时间`
- `博主链接`
- `博主昵称`
- `图片数量`
- `笔记封面链接`
- `笔记图片链接`
- `笔记话题`
- `发布日期`
- `粉丝数`

Some account exports may also include `笔记ID` or `笔记类型`. Do not require them for keyword analysis.

## Derived Fields

- `互动合计` = likes + collects + comments + shares.
- `收藏赞比` = collects / likes. Use only when likes > 0.
- `赞粉比` = likes / followers. Use only when followers > 0; if followers is 0, record as data quality issue.
- `正文长度` = character count of `笔记内容` after converting missing values to empty string.
- `标题字数` = character count of `笔记标题`.
- `图片URL列表` = split `笔记图片链接` by newline, trim blank rows.

## Metric Guidance

Default primary metric is `点赞量`, but keyword analysis should always inspect:

- `收藏量`: stronger signal for manuals, templates, checklists, and reusable guidance.
- `分享量`: signal for emotion resonance or "send to coworker/friend" usefulness.
- `评论量`: signal for controversy, identity resonance, disagreement, or follow-up demand.

Never merge these metrics into one conclusion without explaining what each metric means.
