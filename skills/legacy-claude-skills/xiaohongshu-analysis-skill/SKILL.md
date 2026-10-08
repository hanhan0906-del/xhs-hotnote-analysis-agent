---
name: xiaohongshu-account-analysis
description: 分析小红书对标账号数据，生成标准化的12模块账号分析报告（md格式）。当用户提到要分析对标账号、提供采集数据目录/Excel文件、或提到要生成账号分析报告时，必须使用此Skill。输入是本地Excel文件（【社媒助手】采集导出），CC自动读取笔记数据、下载封面图及笔记内全部图片并用视觉能力分析，输出是标准12模块md分析报告。
---

# 小红书对标账号分析 Skill

## 概述

读取本地 Excel 采集文件（【社媒助手】插件导出），自动下载每条笔记的封面图和笔记内全部图片，用视觉能力分析图片内容，生成标准12模块账号分析报告，输出md文件供用户检查后存入 Obsidian。

支持两种触发方式：
1. **自动模式**：用户只提到"分析对标账号"或给出采集目录，不指定具体文件 → 扫描目录，找出尚未分析过的Excel文件，逐个分析
2. **指定模式**：用户给出具体Excel文件路径 → 只分析这一个文件

---

## 数据源目录

```
C:\Users\Lenovo\Desktop\小红书对标博主笔记采集\
```

所有【社媒助手】采集导出的 Excel 文件都存放在这里，文件名格式类似：
`【社媒助手】博主「XXX」的笔记数据-YYYYMMDD-HHMM.xlsx`

---

## 已分析清单（自动模式判重用）

清单文件：`references/analyzed_manifest.json`（本skill目录下，不存在则视为空清单，首次运行需创建）

结构：
```json
{
  "files": [
    {
      "filename": "【社媒助手】博主「程程老师厚德载物」的笔记数据-20260706-1931.xlsx",
      "mtime": "2026-07-06T19:31:00",
      "account_name": "程程老师厚德载物",
      "report_path": "对标分析_程程老师厚德载物.md",
      "archive_type": "优秀案例",
      "analyzed_at": "2026-07-12"
    }
  ]
}
```

**自动模式执行逻辑：**
1. 扫描数据源目录下所有 `*.xlsx` 文件
2. 对比清单：文件名不在清单中，或文件的修改时间比清单记录的更新 → 判定为"待分析"
3. 待分析文件逐个跑完整流程，每跑完一个就更新清单（不要等全部跑完再统一写清单，防止中途中断丢进度）
4. 清单里已有且 mtime 未变的文件，跳过，不重复分析

**指定模式执行逻辑：**
用户给出具体文件路径 → 直接分析该文件，跳过判重检查，分析完成后仍更新清单（若已存在则覆盖对应条目）。

---

## Excel 字段说明

【社媒助手】导出的字段（表头在第1行）：

| 字段 | 说明 |
|---|---|
| 笔记ID | 唯一标识 |
| 笔记链接 | 笔记原始URL |
| 笔记类型 | 图文/视频 |
| 笔记标题 | 标题 |
| 笔记内容 | 正文，注意话题标签也拼在这个字段里，格式 `#话题名[话题]#` |
| 点赞量 | 核心互动指标之一 |
| 收藏量 | 核心互动指标之一（资料电商类账号通常收藏比点赞更重要） |
| 评论量 | |
| 分享量 | 可能为空 |
| 发布时间 | datetime |
| 更新时间 | datetime |
| 博主链接 | |
| 博主昵称 | 账号名，用于报告标题和文件命名 |
| 图片数量 | 笔记总图数 |
| 笔记封面链接 | 第一张图/封面图的CDN直链 |
| 笔记图片链接 | 该笔记全部图片链接，**换行符分隔**，第一条通常与封面链接相同 |
| 粉丝数 | 采集时刻的博主粉丝数快照 |

**字段映射到分析概念：**
- `count`（互动量）= 优先用**点赞量**做主指标，但报告开头必须注明"点赞量"字样（不同账号可能收藏更关键，若收藏量明显比点赞更能区分高低表现，可在模块一注明改用收藏量并说明理由）
- `title` = 笔记标题
- `tags` = 从"笔记内容"中用正则 `#([^#]+?)\[话题\]#` 提取
- `note_desc` = "笔记内容"去除话题标签后的剩余文本（如果剩余为空，说明该笔记正文即为标签堆砌，据实记录）
- `create_time` = 发布时间
- `cover_url` = 笔记封面链接
- `all_image_urls` = 笔记图片链接按 `\n` 切分成列表

**nan/空值处理：** 原因不明，只记录数量和占比，不推断原因。

---

## 执行流程

### Step 1：扫描目录 + 判重（自动模式）或直接定位文件（指定模式）

```python
import os, json, glob
from datetime import datetime

DATA_DIR = r"C:\Users\Lenovo\Desktop\小红书对标博主笔记采集"
MANIFEST_PATH = r"C:\Users\Lenovo\Desktop\小红书相关的skill\.claude\skills\xiaohongshu-analysis-skill\references\analyzed_manifest.json"

def load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"files": []}

def save_manifest(manifest):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

def find_pending_files():
    """自动模式：找出尚未分析或已更新的xlsx文件"""
    manifest = load_manifest()
    known = {f["filename"]: f["mtime"] for f in manifest["files"]}
    pending = []
    for path in glob.glob(os.path.join(DATA_DIR, "*.xlsx")):
        fname = os.path.basename(path)
        mtime = datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
        if fname not in known or known[fname] != mtime:
            pending.append(path)
    return pending

def update_manifest_entry(filepath, account_name, report_path, archive_type):
    manifest = load_manifest()
    fname = os.path.basename(filepath)
    mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
    manifest["files"] = [f for f in manifest["files"] if f["filename"] != fname]
    manifest["files"].append({
        "filename": fname,
        "mtime": mtime,
        "account_name": account_name,
        "report_path": report_path,
        "archive_type": archive_type,
        "analyzed_at": datetime.now().strftime("%Y-%m-%d")
    })
    save_manifest(manifest)
```

### Step 2：读取 Excel → DataFrame

```python
import pandas as pd
import re

def load_data(xlsx_path):
    df = pd.read_excel(xlsx_path, sheet_name=0)

    df["dt"] = pd.to_datetime(df["发布时间"], errors="coerce")
    df["hour"] = df["dt"].dt.hour
    df["weekday"] = df["dt"].dt.dayofweek
    df["month"] = df["dt"].dt.to_period("M")

    def extract_tags(text):
        if pd.isna(text):
            return []
        return re.findall(r"#([^#]+?)\[话题\]#", str(text))

    def strip_tags(text):
        if pd.isna(text):
            return ""
        return re.sub(r"#[^#]+?\[话题\]#", "", str(text)).strip()

    df["tags"] = df["笔记内容"].apply(extract_tags)
    df["note_desc"] = df["笔记内容"].apply(strip_tags)
    df["title_len"] = df["笔记标题"].astype(str).str.len()

    df["image_urls"] = df["笔记图片链接"].apply(
        lambda x: [u.strip() for u in str(x).split("\n") if u.strip()] if pd.notna(x) else []
    )

    # 主互动指标默认点赞量，异常情况在报告模块一注明后可切换
    df_valid = df.dropna(subset=["点赞量"]).copy()

    account_name = df["博主昵称"].iloc[0] if "博主昵称" in df.columns else "未知账号"
    return df, df_valid, account_name
```

### Step 3：核心统计

```python
def core_stats(df, df_valid, metric="点赞量"):
    return {
        "total": len(df),
        "valid": len(df_valid),
        "nan_count": int(df[metric].isna().sum()),
        "nan_pct": round(df[metric].isna().mean() * 100, 1),
        "max": df_valid[metric].max(),
        "median": df_valid[metric].median(),
        "mean": round(df_valid[metric].mean(), 1),
        "date_min": df["dt"].min().strftime("%Y-%m-%d") if df["dt"].notna().any() else None,
        "date_max": df["dt"].max().strftime("%Y-%m-%d") if df["dt"].notna().any() else None,
        "monthly": df["month"].value_counts().sort_index().to_dict(),
        "fans": df["粉丝数"].iloc[0] if "粉丝数" in df.columns else None,
    }
```

### Step 4：选题分析 / 标题公式 / 标签分析 / 正文结构 / 发布时间 / 互动数据

与原有逻辑一致，不再赘述，规则：
- 样本≤3条：标注"样本不足，仅供参考"
- 单条爆款占总互动量50%以上：说明失真，去掉爆款重新计算
- 标签从 `tags` 列（已是list）直接 `Counter` 统计
- 采集工具只能稳定采集较新一段时间数据，更早数据可能残缺，**不随意下"断更"结论**，只描述数据现象

### Step 5：图片下载

小红书 CDN 图片直链（`xhscdn.com` 域名）需要带请求头才能稳定下载，直接 `WebFetch` 拿不到图像内容，必须用命令行下载到本地再用 `Read` 工具查看。

```python
import requests, os, hashlib

HEADERS = {
    "Referer": "https://www.xiaohongshu.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def download_image(url, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    fname = hashlib.md5(url.encode()).hexdigest()[:16] + ".jpg"
    path = os.path.join(save_dir, fname)
    if os.path.exists(path):
        return path
    resp = requests.get(url, headers=HEADERS, timeout=15)
    if resp.status_code == 200 and resp.content:
        with open(path, "wb") as f:
            f.write(resp.content)
        return path
    return None
```

按笔记逐条下载：封面图 + `image_urls` 里的全部图片，存到 scratchpad 下按账号分文件夹，例如：
```
{scratchpad}/xhs_covers/{账号名}/{笔记ID}_cover.jpg
{scratchpad}/xhs_images/{账号名}/{笔记ID}_01.jpg, _02.jpg, ...
```

### Step 6：封面图分析（全量）

**先做全量缩略图概览，再对高互动笔记看原图细节** —— 避免67条笔记×N张图逐张单独查看导致效率过低。

```python
from PIL import Image
import math

def make_contact_sheet(image_paths, labels, out_path, cols=5, thumb_size=280):
    """把多张图拼成网格缩略图，每张图下方标注label（如点赞数）"""
    rows = math.ceil(len(image_paths) / cols)
    sheet = Image.new("RGB", (cols * thumb_size, rows * (thumb_size + 30)), "white")
    from PIL import ImageDraw
    draw = ImageDraw.Draw(sheet)
    for i, (p, label) in enumerate(zip(image_paths, labels)):
        try:
            img = Image.open(p).convert("RGB")
            img.thumbnail((thumb_size, thumb_size))
            x = (i % cols) * thumb_size
            y = (i // cols) * (thumb_size + 30)
            sheet.paste(img, (x, y))
            draw.text((x + 5, y + thumb_size + 5), str(label), fill="black")
        except Exception:
            continue
    sheet.save(out_path)
    return out_path
```

**执行顺序：**
1. 全部笔记的封面图下载完成后，按互动量降序排列，每 20-25 张拼一版缩略图（`labels` 用"点赞数"），用 `Read` 工具依次查看每一版缩略图，建立整体封面类型分布的印象（纯文字大字报 / 资料截图密集型 / 实物拍照 / 插画 / 结构化清单 / 备忘录截图风格等）
2. 对互动量 Top 15-20 的笔记，单独下载原图并用 `Read` 逐张查看，提炼具体的封面公式（文案内容、配色、布局细节）
3. 对互动量最低的一批（尾部10-15条），同样单独查看，作为"低效封面"的对照样本

重点观察：
- 封面类型
- 底色风格（深色/浅色/纯色/渐变）
- 文字布局（行数/字号/高亮关键词颜色）
- 特殊元素（emoji/图标/人物/产品图）
- 各封面类型与互动量的关系，得出哪种封面效果最好

### Step 7：图集结构分析（全量，本skill新增维度）

小红书笔记除封面外，还有多张内页图（9宫格上限），这些图的构成本身是一种可分析的结构（比如"资料截图占比""正文引导图占比""封面+内容图+CTA图三段式"等），尤其对资料电商类账号，图集的"内容量感"直接影响收藏率。

**执行顺序：**
1. 对每条笔记，把该笔记的全部图片（封面+内页图）拼成一张"单笔记图集缩略图"（用 `make_contact_sheet`，`cols` 按图片数量取3-4，不需要label或用序号），保存为 `{笔记ID}_gallery.jpg`
2. 按互动量分组（高/中/低），每组抽样查看若干条笔记的图集缩略图，归纳图集结构规律，例如：
   - 图1封面（钩子）+ 图2-8资料截图（内容量证明）+ 图9引导图（购买/关注CTA）
   - 全部纯文字卡片，无实物图/资料图穿插
   - 图片数量本身与互动量的相关性（是否图片越多互动越好，还是存在最优区间）
3. 对结构特别突出（互动量很高或很低）的笔记，单独查看该笔记图集内每张原图，做详细结构拆解

---

## 12模块报告结构

详细写作模板见 `references/report-template.md`

**核心写作规则（严格遵守）：**

1. **单账号分析不提其他账号** — 不做横向比较，报告正文中不出现任何其他已分析账号的名字或"此前XX账号"这类表述，即使规律相似也只描述本账号数据，不归因/联系到其他账号
2. **数据撑不住就跳过** — 写"数据不足，本模块跳过"并说明原因
3. **不随意下断更结论** — 只描述数据现象
4. **不写"可以直接移植/借鉴"** — 模块十二只陈述规律
5. **nan原因不推断** — 只记录数量和占比
6. **互动指标要注明用的是点赞量还是收藏量**，不能混用
7. **账号基本画像模块不列中位数点赞/平均点赞** — 这两个指标极易被头部内容拉偏，参考价值低，不放入模块一（模块三选题分析里各分类/系列的平均点赞仍保留，那是用于组间对比，不是同一问题）
8. **封面公式和图集结构分析必须附实际图片，不能只写文字描述** — 用 Markdown 图片语法把代表性截图嵌入报告正文（存到报告同目录的 `[报告文件名]_assets/` 文件夹），至少包含：全账号最高互动和最低互动笔记的封面对比图、每种封面类型的代表图、高互动和低互动笔记的图集缩略图对比

---

## 输出

Obsidian 知识库根目录：
```
C:\Users\Lenovo\Desktop\小红书\obsidian1\对标账号分析\
```
下设三个固定子文件夹：`优秀案例` / `错误案例` / `特殊案例`

**归档类型判断标准（分析完数据后自行判断，不用询问用户）：**
- **优秀案例** ✅：整体数据健康，有可复用的选题/标题/封面/正文打法，值得模仿
- **错误案例** ❌：打法有明显缺陷（如品类过散、正文空洞、蹭热点无沉淀），整体不建议模仿，但可能有零散可借鉴点
- **特殊案例** ⚠️：数据结构极端（如单条爆款占比过高、断更后重启、样本量过小等），常规分析方法在此账号上不完全适用，结论需谨慎参考

**文件名格式：**
- `对标分析_[账号名].md`（优秀案例）
- `错误案例_[账号名].md`（错误案例）
- `特殊案例_[账号名].md`（特殊案例）

生成后直接写入对应子文件夹（`优秀案例`/`错误案例`/`特殊案例`），不需要用户手动搬运。

分析完成后，务必执行 Step 1 中的 `update_manifest_entry`，把本次结果（含 `archive_type` 和最终 `report_path`）写入清单，避免下次自动模式重复分析。
