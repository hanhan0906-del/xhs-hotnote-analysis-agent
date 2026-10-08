from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import time
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd


HEADERS = {
    "Referer": "https://www.xiaohongshu.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}


def text(value) -> str:
    if pd.isna(value):
        return ""
    s = str(value).strip()
    return "" if s.lower() == "nan" else s


def number(value) -> int:
    if pd.isna(value) or value == "":
        return 0
    if isinstance(value, str):
        value = value.replace(",", "").strip()
    try:
        return int(float(value))
    except Exception:
        return 0


def fmt_num(value: int) -> str:
    return f"{value:,}"


def safe_filename(name: str, max_len: int = 48) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "", name)
    name = re.sub(r"\s+", " ", name).strip()
    return (name[:max_len].rstrip(" .") or "无标题")


def classify_title(title: str, content: str) -> tuple[str, str, str]:
    t = f"{title} {content[:80]}"
    rules = [
        ("一些……小tips系列", r"一些.*(tips?|小tips?|小tip)", "轻量口语化 + 可保存小动作"),
        ("给刚毕业/应届/实习生系列", r"刚毕业|应届|实习生|初入职场|职场新人|新人刚入职", "点名新人身份 + 生存/成长承诺"),
        ("打工后/上班后认知觉醒系列", r"打工后|上班后|工作后|才发现|长脑子|开智|明白了", "前后认知差 + 隐藏规则补课"),
        ("如果你觉得……可以看看这系列", r"如果你|建议.*看看|反复观看|真的建议", "先接情绪 + 低压力解决入口"),
        ("职场相处/生存法则系列", r"相处之道|生存之道|生存法则|人生法则|职场法则|游戏规则", "复杂关系规则化"),
        ("原来……社会化系列", r"原来|社会化|低社会化|防套话", "补课感 + 社会化诊断"),
        ("名人/权威观点引语系列", r"大冰|大佬|老师|说[:：]|讲透|看完.*懂", "权威背书 + 一句话洞察"),
        ("让领导觉得你靠谱系列", r"领导|老板|上级|汇报|靠谱|leader|向上管理", "评价焦虑 + 可执行微习惯"),
        ("新人大忌/学生思维系列", r"大忌|学生思维|巨婴|孩子气|最忌讳|一人说一个", "负面提醒 + 避坑动机"),
        ("不要太有责任心/别太在乎系列", r"(不要|别|没必要|不必).*(责任心|在乎|内耗|太乖|善良|不争不抢)", "反努力叙事 + 边界感"),
        ("保命/生存指南系列", r"保命|生存指南|避雷指南|避坑|救命|自救|防身", "高风险提醒 + 防坑清单"),
        ("早知道/早发现/后悔系列", r"早知道|早发现|没早点|越早|后悔|第一次.*刷到", "时间差 + 错失感"),
        ("第一课/报到前时间节点系列", r"第一课|报到|实习前|入职前|第十集|第\d+集", "时间节点 + 课程感"),
        ("多年经验背书系列", r"\d+年|四年|五年|六年|10年|十年|工作.*年|独居.*年", "经验年限背书"),
        ("漂亮话/弱者表达/提问意识系列", r"漂亮话|弱者表达|提问意识|沟通|表达|话术|请教", "沟通焦虑 + 可复制表达"),
        ("心眼子/防套话/防背刺系列", r"心眼|防套话|背刺|甩锅|接盘侠|老油条|欺负", "隐性风险 + 自我保护"),
        ("低社会化/女宝/心眼少人群系列", r"低社会化|女宝|心眼少|年轻女生|i人|老实人", "细分人群 + 代入感"),
        ("数字清单系列", r"\d+个|\d+条|\d+句|100个|27条|17个|清单|合集", "数字密度 + 收藏动机"),
        ("不被轻视/不被欺负系列", r"不被|被欺负|被轻视|被看轻|被拿捏|拿捏", "不安全感 + 边界训练"),
        ("训练别人/反击恶意系列", r"训练任何人|反击|恶意|硬气|怼回去|怼人", "掌控感 + 冲突处理"),
        ("新人如何避免/别内耗系列", r"如何避免|别内耗|治愈自己|焦虑|迷茫|破防", "问题解决 + 反内耗"),
    ]
    if not title:
        return "无标题/封面正文驱动型", "标题缺失，点击任务主要由封面、正文或话题承担", "不适合直接复用标题，但适合保留为封面/正文边界样本"
    for name, pattern, hook in rules:
        if re.search(pattern, t, re.I):
            return name, hook, "可作为逐条爆款标题样本；若同结构多次出现，也可支撑公式库"
    return "单篇现象/混合表达型", "单篇有用，但标题结构不一定稳定", "逐条保留，后续积累到多篇再升级为公式"


def classify_cover(title: str, likes: int, image_count: int) -> tuple[str, str, str]:
    if likes < 1000:
        return "弱爆/边界封面样本", "保留低互动样本，观察承诺、层级或痛点为什么没有打透", "反面教材，不直接模仿"
    if re.search(r"烦躁|讨厌|朋友|大冰|情绪|上班", title):
        return "情绪梗图或真实截图封面", "用情绪图像/截图承接痛点，标题负责点题", "适合情绪共鸣和反内耗"
    if re.search(r"保命|大忌|不要|别|生存指南|避雷", title):
        return "极简大字警示封面", "一眼给出强判断或风险提醒", "适合防坑、边界、警示类"
    if re.search(r"\d+|清单|收藏|细节|习惯|话术|提问", title) or image_count >= 6:
        return "资料清单/截图型封面", "直接展示内容密度，增强收藏动机", "适合清单、手册、资料包"
    if re.search(r"刚毕业|应届|实习|新人|职场菜鸟", title):
        return "新人身份标签封面", "先框定人群，再给生存/成长承诺", "适合新人手册入口"
    return "单篇爆款封面样本", "保留该爆款封面原貌，后续和更多样本对比", "逐条保留，不强行归入大类型"


def sample_status(likes: int) -> str:
    return "反面教材/边界样本" if likes < 1000 else "爆款样本"


def download_cover(url: str, dst: Path) -> tuple[bool, str]:
    if not url:
        return False, "missing url"
    if dst.exists() and dst.stat().st_size > 0:
        return True, "exists"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        if not data:
            return False, "empty response"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        time.sleep(0.08)
        return True, "downloaded"
    except Exception as exc:
        return False, str(exc)[:120]


def find_existing_asset(assets_dir: Path, title: str, likes: int) -> Path | None:
    if not assets_dir.exists():
        return None
    title_key = safe_filename(title, 16)
    candidates = list(assets_dir.glob(f"*{likes}赞*"))
    if title_key:
        candidates += list(assets_dir.glob(f"*{title_key}*"))
    for path in candidates:
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            return path
    return None


def make_title_md(item: dict, report_stem: str, appendix_stem: str, archive_date: str) -> str:
    return f"""# {item['title']}

**类型：** 逐条爆款标题
**样本状态：** {item['status']}
**关键词：** 职场新人成长手册
**来源报告：** [[{report_stem}]]
**逐篇附录：** [[{appendix_stem}]]
**原表序号：** {item['source_index']}

**标题原文：**
```text
{item['title']}
```

**标题结构：** {item['title_formula']}
**标题钩子：** {item['title_hook']}
**归档判断：** {item['title_archive_note']}

**代表数据：**
- 账号：{item['author'] or '未提供'}
- 点赞：{fmt_num(item['likes'])}
- 收藏：{fmt_num(item['collects'])}
- 评论：{fmt_num(item['comments'])}
- 分享：{fmt_num(item['shares'])}
- 粉丝：{fmt_num(item['followers'])}
- 图片数：{item['image_count']}

**为什么要逐条保留：**
这条标题是关键词采集样本的一部分。即使它不一定能升级成稳定公式，也保留原始标题、数据和钩子，方便以后横向比较同类爆款和弱爆样本。

**原始链接：** {item['link'] or '未提供'}

---
*首次归档：{archive_date}；来源关键词：职场新人成长手册*
"""


def make_cover_md(item: dict, report_stem: str, appendix_stem: str, image_rel: str, image_status: str, archive_date: str) -> str:
    image_block = f"![{item['title']}|300]({image_rel})" if image_rel else f"- 封面图暂未成功下载：{image_status}"
    return f"""# {item['title']}

**类型：** 逐条爆款封面
**样本状态：** {item['status']}
**关键词：** 职场新人成长手册
**来源报告：** [[{report_stem}]]
**逐篇附录：** [[{appendix_stem}]]
**原表序号：** {item['source_index']}

**封面图：**
{image_block}

**封面归类：** {item['cover_type']}
**封面钩子：** {item['cover_hook']}
**使用判断：** {item['cover_note']}

**对应标题：**
```text
{item['title']}
```

**代表数据：**
- 账号：{item['author'] or '未提供'}
- 点赞：{fmt_num(item['likes'])}
- 收藏：{fmt_num(item['collects'])}
- 评论：{fmt_num(item['comments'])}
- 分享：{fmt_num(item['shares'])}
- 粉丝：{fmt_num(item['followers'])}
- 图片数：{item['image_count']}

**为什么要逐条保留：**
封面库不是只存总结类型，也要保留爆款封面的原始样本。后续做封面时，可以按单篇样本回看标题、封面、数据之间的原始搭配。

**原始链接：** {item['link'] or '未提供'}

---
*首次归档：{archive_date}；来源关键词：职场新人成长手册*
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", default=os.environ.get("XLSX_PATH"))
    parser.add_argument("--report", default=os.environ.get("REPORT_PATH"))
    parser.add_argument("--appendix", default=os.environ.get("APPENDIX_PATH"))
    parser.add_argument("--vault", default=os.environ.get("VAULT_PATH", r"C:\Users\Lenovo\Desktop\小红书\obsidian1"))
    parser.add_argument("--archive-date", default=os.environ.get("ARCHIVE_DATE", date.today().isoformat()))
    args = parser.parse_args()

    xlsx_path = Path(args.xlsx)
    report_path = Path(args.report)
    appendix_path = Path(args.appendix)
    vault = Path(args.vault)
    archive_date = args.archive_date

    df = pd.read_excel(xlsx_path)
    for col in ["点赞量", "收藏量", "评论量", "分享量", "粉丝数", "图片数量"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    rows = []
    for idx, row in df.iterrows():
        title = text(row["笔记标题"]) or "无标题/封面正文驱动型"
        content = text(row["笔记内容"])
        likes = number(row["点赞量"])
        title_formula, title_hook, title_note = classify_title("" if title.startswith("无标题/") else title, content)
        cover_type, cover_hook, cover_note = classify_cover(title, likes, number(row["图片数量"]))
        rows.append({
            "source_index": idx + 1,
            "title": title,
            "content": content,
            "likes": likes,
            "collects": number(row["收藏量"]),
            "comments": number(row["评论量"]),
            "shares": number(row["分享量"]),
            "followers": number(row["粉丝数"]),
            "image_count": number(row["图片数量"]),
            "author": text(row["博主昵称"]),
            "link": text(row["笔记链接"]),
            "cover_url": text(row["笔记封面链接"]),
            "status": sample_status(likes),
            "title_formula": title_formula,
            "title_hook": title_hook,
            "title_archive_note": title_note,
            "cover_type": cover_type,
            "cover_hook": cover_hook,
            "cover_note": cover_note,
        })
    rows.sort(key=lambda r: (r["likes"], r["collects"], r["comments"]), reverse=True)

    title_dir = vault / "标题库" / "职场新人成长手册"
    cover_dir = vault / "封面模版库" / "职场新人成长手册"
    cover_images = cover_dir / "图片"
    assets_dir = report_path.with_name(report_path.stem + "_assets")

    title_entries = []
    cover_entries = []
    download_stats = {"downloaded": 0, "exists": 0, "copied": 0, "failed": 0}
    for pos, item in enumerate(rows, 1):
        prefix = f"{pos:02d}"
        title_slug = safe_filename(item["title"], 34)
        title_path = title_dir / f"爆款标题{prefix}-{title_slug}.md"
        title_path.write_text(make_title_md(item, report_path.stem, appendix_path.stem, archive_date), encoding="utf-8")
        title_entries.append(str(title_path))

        image_name = f"爆款封面{prefix}-{title_slug}.jpg"
        image_path = cover_images / image_name
        existing = find_existing_asset(assets_dir, item["title"], item["likes"])
        if existing and not image_path.exists():
            cover_images.mkdir(parents=True, exist_ok=True)
            shutil.copy2(existing, image_path)
            ok, image_status = True, "copied"
            download_stats["copied"] += 1
        else:
            ok, image_status = download_cover(item["cover_url"], image_path)
            download_stats[image_status if image_status in download_stats else "failed"] += 1
        image_rel = f"图片/{image_name}" if ok else ""

        cover_path = cover_dir / f"爆款封面{prefix}-{title_slug}.md"
        cover_path.write_text(make_cover_md(item, report_path.stem, appendix_path.stem, image_rel, image_status, archive_date), encoding="utf-8")
        cover_entries.append(str(cover_path))

    title_index = title_dir / "爆款标题逐条索引.md"
    title_index.write_text(
        "# 职场新人成长手册：爆款标题逐条索引\n\n"
        f"> 来源报告：[[{report_path.stem}]]\n"
        f"> 逐篇附录：[[{appendix_path.stem}]]\n"
        f"> 归档日期：{archive_date}\n"
        f"> 条目数：{len(title_entries)}\n\n"
        + "\n".join(f"- [[{Path(p).stem}]]" for p in title_entries)
        + "\n",
        encoding="utf-8",
    )

    cover_index = cover_dir / "爆款封面逐条索引.md"
    cover_index.write_text(
        "# 职场新人成长手册：爆款封面逐条索引\n\n"
        f"> 来源报告：[[{report_path.stem}]]\n"
        f"> 逐篇附录：[[{appendix_path.stem}]]\n"
        f"> 归档日期：{archive_date}\n"
        f"> 条目数：{len(cover_entries)}\n\n"
        + "\n".join(f"- [[{Path(p).stem}]]" for p in cover_entries)
        + "\n",
        encoding="utf-8",
    )

    skill_root = Path(__file__).resolve().parents[1]
    manifest_path = skill_root / "references" / "keyword_archive_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {"archives": []}
    manifest.setdefault("per_note_archives", [])
    manifest["per_note_archives"] = [m for m in manifest["per_note_archives"] if m.get("report_path") != str(report_path)]
    manifest["per_note_archives"].append({
        "keyword": "职场新人成长手册",
        "report_path": str(report_path),
        "appendix_path": str(appendix_path),
        "source_excel": str(xlsx_path),
        "archived_at": archive_date,
        "row_count": len(rows),
        "title_entries": len(title_entries),
        "cover_entries": len(cover_entries),
        "title_index": str(title_index),
        "cover_index": str(cover_index),
        "download_stats": download_stats,
    })
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "rows": len(rows),
        "title_entries": len(title_entries),
        "cover_entries": len(cover_entries),
        "title_index": str(title_index),
        "cover_index": str(cover_index),
        "download_stats": download_stats,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
