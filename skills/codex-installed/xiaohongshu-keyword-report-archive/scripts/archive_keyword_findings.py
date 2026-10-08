from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd


DEFAULT_KEYWORD = "职场新人成长手册"


def clean_text(value) -> str:
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


def safe_filename(name: str, max_len: int = 76) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "", name).strip()
    name = re.sub(r"\s+", " ", name)
    return name[:max_len].rstrip(" .") or "未命名条目"


@dataclass
class FormulaRule:
    name: str
    template: str
    intent: str
    predicate: object
    hook: str
    condition: str
    risk: str


FORMULAS = [
    FormulaRule("一些……小tips系列", "一些[具体场景/人群]的小tips", "人情世故 / 社会化", lambda t: "一些" in t and re.search(r"tips?|小tips?|小tip", t, re.I), "轻量口语感降低进入门槛，把复杂职场社交拆成可保存的小动作。", "适合真实经验、具体场景、行为细节；不适合空泛鸡汤。", "容易变成泛泛清单，必须给具体场景。"),
    FormulaRule("给刚毕业/应届/实习生系列", "给[刚毕业/应届/实习生/职场新人]的[生存/成长/避坑]tips", "新人转职场", lambda t: bool(re.search(r"刚毕业|应届|实习生|初入职场|职场新人|新人刚入职", t)), "直接点名新人身份，降低搜索用户判断成本。", "适合新人手册入口、阶段型内容、入职前后场景。", "人群越宽越容易普通，要叠加具体痛点或时间节点。"),
    FormulaRule("打工后/上班后认知觉醒系列", "[打工后/上班后/工作后]才发现/开始明白[隐藏规则]", "新人转职场 / 社会化", lambda t: bool(re.search(r"打工后|上班后|工作后|才发现|长脑子|开智|明白了", t)), "用前后对比制造顿悟感，满足新人补隐藏规则的需求。", "适合反常识经验、社会化规则、从学生到职场的认知转换。", "容易写成鸡汤，必须落到具体行为。"),
    FormulaRule("如果你觉得……可以看看这系列", "如果你觉得[情绪困境]，可以看看这篇/这些话", "心态边界 / 反内耗", lambda t: bool(re.search(r"如果你|建议.*看看|反复观看|真的建议", t)), "先接住情绪，再给低压力动作。", "适合上班烦躁、讨厌上班、焦虑、迷茫、破防等情绪场景。", "不能只安慰，要给判断或行动。"),
    FormulaRule("职场相处/生存法则系列", "[职场/办公室/成年人]相处之道/生存法则", "人情世故 / 社会化", lambda t: bool(re.search(r"相处之道|生存之道|生存法则|人生法则|职场法则|游戏规则", t)), "把复杂关系压缩成规则感，用户会为少走弯路收藏。", "适合关系规则、分寸感、协作边界。", "规则感强但容易端着，需要案例支撑。"),
    FormulaRule("原来……社会化系列", "原来[高社会化的人/大家]都在这样做", "人情世故 / 社会化", lambda t: "原来" in t or bool(re.search(r"社会化|低社会化|防套话", t)), "用“原来”制造补课感，击中新人对社会化不足的自我诊断。", "适合低社会化训练、人情世故、观察别人怎么做。", "避免把用户标签化得太重。"),
    FormulaRule("名人/权威观点引语系列", "[名人/大佬/老师]说：[一句职场洞察]", "心态边界 / 社会化", lambda t: bool(re.search(r"大冰|大佬|老师|说[:：]|讲透|看完.*懂", t)), "借权威降低说教感，用一句话承载洞察。", "适合金句解释、价值观松绑、职场边界感。", "不能只搬运名人，要转化成场景判断。"),
    FormulaRule("让领导觉得你靠谱系列", "让[领导/leader/老板]觉得你靠谱的[微习惯/汇报方式]", "沟通话术 / 向上管理", lambda t: bool(re.search(r"领导|老板|上级|汇报|靠谱|leader|向上管理", t, re.I)), "把模糊评价变成可执行行为，新人收藏意愿强。", "适合汇报、反馈、协作、向上管理。", "避免讨好式表达，重点写协作效率。"),
    FormulaRule("新人大忌/学生思维系列", "职场新人最忌讳[学生思维/巨婴思维/某种行为]", "防坑 / 自我保护", lambda t: bool(re.search(r"大忌|学生思维|巨婴|孩子气|最忌讳|一人说一个", t)), "用负面提醒制造风险感，帮助新人快速识别坑。", "适合避坑清单、身份转换、不能做的事。", "语气不能只恐吓，要给替代做法。"),
    FormulaRule("不要太有责任心/别太在乎系列", "不要太[有责任心/在乎/乖/善良]，否则[后果]", "心态边界 / 反内耗", lambda t: bool(re.search(r"不要|别|没必要|不必", t)) and bool(re.search(r"责任心|在乎|内耗|太乖|善良|不争不抢", t)), "反努力叙事帮用户松绑，适合边界感内容。", "适合责任心过强、讨好、情绪劳动、反内耗。", "要区分边界感和摆烂。"),
    FormulaRule("保命/生存指南系列", "[工作/职场/办公室]保命指南/生存指南/避雷指南", "防坑 / 自我保护", lambda t: bool(re.search(r"保命|生存指南|避雷指南|避坑|救命|自救|防身", t)), "高风险词汇放大紧迫感，适合防坑和场景清单。", "适合新人防坑、体制内/办公室规则、接盘侠预防。", "标题刺激，正文必须给真方法。"),
    FormulaRule("早知道/早发现/后悔系列", "早知道/早发现[某经验]就好了", "新人转职场 / 反内耗", lambda t: bool(re.search(r"早知道|早发现|没早点|越早|后悔|第一次.*刷到", t)), "用时间差制造错失感，让用户觉得现在收藏还来得及。", "适合入职前、实习前、刚毕业阶段复盘。", "不能泛泛说早知道，要有明确经验差。"),
    FormulaRule("第一课/报到前时间节点系列", "[入职/实习/报到]前必须知道的第一课/第N集", "新人转职场", lambda t: bool(re.search(r"第一课|报到|实习前|入职前|第十集|第\\d+集", t)), "用时间节点或课程感包装成必修课。", "适合做系列化新人手册目录。", "系列感要有连续主题。"),
    FormulaRule("多年经验背书系列", "[工作N年/多年后]总结出的[职场建议/细节/规则]", "新人转职场 / 社会化", lambda t: bool(re.search(r"\\d+年|四年|五年|六年|10年|十年|工作.*年|独居.*年", t)), "用经验年限建立信任。", "适合踩坑复盘、成熟职场人对新人的建议。", "年限只是背书，核心仍是具体经验。"),
    FormulaRule("漂亮话/弱者表达/提问意识系列", "[漂亮话/提问意识/弱者表达]让你在职场更好沟通", "沟通话术 / 向上管理", lambda t: bool(re.search(r"漂亮话|弱者表达|提问意识|沟通|表达|话术|请教", t)), "把不会说话的焦虑转成可复制表达。", "适合话术卡、请教、反馈、冲突前置沟通。", "避免机械话术，最好配使用场景。"),
    FormulaRule("心眼子/防套话/防背刺系列", "[心眼子/防套话/防背刺/防甩锅]收藏版", "防坑 / 自我保护", lambda t: bool(re.search(r"心眼|防套话|背刺|甩锅|接盘侠|老油条|欺负", t)), "满足新人对隐性攻击和责任转嫁的防御需求。", "适合责任边界、会议纪要、任务确认、同事甩锅。", "容易走向阴谋论，要用具体工作流判断。"),
    FormulaRule("低社会化/女宝/心眼少人群系列", "给[低社会化/心眼少/年轻女生/i人]的职场补课", "人情世故 / 社会化", lambda t: bool(re.search(r"低社会化|女宝|心眼少|年轻女生|i人|老实人", t)), "用细分身份增强代入感。", "适合精准人群痛点库。", "标签要谨慎，避免冒犯和自我矮化。"),
    FormulaRule("数字清单系列", "[N条/N个/N句]职场细节/人情世故/避坑清单", "清单资料 / 收藏型", lambda t: bool(re.search(r"\\d+个|\\d+条|\\d+句|100个|27条|17个|清单|合集", t)), "数字让价值密度可见，适合资料包和清单。", "适合资料产品化、收藏型内容。", "数字不能虚高，每条都要有用。"),
    FormulaRule("不被轻视/不被欺负系列", "如何不被[轻视/欺负/拿捏]", "防坑 / 自我保护", lambda t: bool(re.search(r"不被|被欺负|被轻视|被看轻|被拿捏", t)), "把职场不安全感具体化。", "适合边界训练、自我保护、办公室关系。", "要给可执行动作，避免只有情绪宣泄。"),
    FormulaRule("训练别人/反击恶意系列", "训练任何人/反击恶意的[沟通方式]", "沟通话术 / 自我保护", lambda t: bool(re.search(r"训练任何人|反击|恶意|硬气|怼回去|怼人", t)), "满足掌控感和反击感，评论互动潜力强。", "适合冲突处理、拒绝、边界表达。", "语气强，风险是过度对抗。"),
    FormulaRule("新人如何避免/别内耗系列", "新人如何避免[接盘/内耗/焦虑]", "心态边界 / 反内耗", lambda t: bool(re.search(r"如何避免|别内耗|治愈自己|焦虑|迷茫|破防", t)), "把情绪困境转成解决路径。", "适合心态模块、问题解决型内容。", "不能停在情绪共鸣，要给下一步动作。"),
]


TOPIC_ENTRIES = [
    ("职场新人-社会化补课需求", "人情世故 / 社会化", "用户不是单纯搜索职场技巧，而是在补学校没有教过的人情世故、分寸感、潜规则。", "可以做成低社会化训练、办公室分寸感清单、入职后观察别人怎么做系列。", "不要把社会化写成厚黑学；要落到具体协作动作。"),
    ("职场新人-学生思维到职场思维切换", "新人转职场", "高频标题都在处理身份切换：刚毕业、应届、实习、入职前、打工后才发现。", "适合做成新人第1个月/第3个月/第1年成长手册。", "只讲道理会显空，要配具体错误行为和替代做法。"),
    ("职场新人-反内耗与边界感", "心态边界 / 反内耗", "不要太有责任心、别太在乎、上班烦躁说明新人正在寻找心理减负和边界感。", "适合做情绪场景卡：被批评、被甩锅、过度负责、讨好领导、下班后内耗。", "要避免鼓励摆烂，重点是边界和协作责任划分。"),
    ("职场新人-向上管理与靠谱感", "沟通话术 / 向上管理", "让领导觉得靠谱、提问意识、漂亮话等内容收藏价值高，因为它能直接改善职场评价。", "适合做汇报模板、提问模板、反馈模板、请教话术卡。", "不能只有讨好语气，要体现信息同步和风险前置。"),
    ("职场新人-防背刺防甩锅自我保护", "防坑 / 自我保护", "心眼子、防套话、接盘侠、生存指南等内容满足新人对隐性风险的防御需求。", "适合做会议留痕、任务确认、拒绝接锅、同事套话识别专题。", "不要过度阴谋论，要强调可验证证据和工作流程。"),
    ("职场新人-清单资料收藏型内容", "清单资料 / 收藏型", "高收藏赞比样本往往把经验压成清单、细节、手册、收藏版。", "适合做资料包、N条细节、每日一条职场规则、可打印清单。", "清单密度不能虚高，最好每条都可单独执行。"),
    ("职场新人-综合采集弱爆反面样本", "反面教材 / 边界样本", "综合采集会混入少量弱爆样本，这些样本能帮助判断什么样的关键词匹配不够强、标题不够新、封面承诺不够明确。", "每次关键词归档都保留一个反面样本条目，用来积累低效标题、弱封面、泛痛点的避坑经验。", "不要删除弱样本，也不要把弱样本当稳定公式。"),
]


COVER_ENTRIES = [
    ("类型1-情绪梗图或真实截图做职场痛点封面", "用人物表情、影视截图、聊天/评论截图承接情绪，标题负责点题，图片负责代入。", "适合反内耗、职场边界、职场情绪痛点。", "图片不能太暗或信息过碎，文字钩子要清晰。", ["04_top_32000赞_如果你觉得上班很烦躁_讨厌上班可以看看这.jpg", "07_top_20000赞_大冰_永远别想在职场上交朋友.jpg"]),
    ("类型2-极简大字标题卡", "封面只保留高冲击标题或一句核心判断，减少装饰，让搜索页第一眼读懂。", "适合保命指南、大忌、不要太有责任心等强判断内容。", "必须有强句子支撑，否则会显空。", ["14_lowfan_9605赞_工作保命指南_每天看一遍心态稳一半.jpg", "13_lowfan_11000赞_大家特别是刚进入职场的_不要太有责任心.jpg"]),
    ("类型3-资料截图或清单页直接当封面", "把清单、手册、截图、笔记页直接放到封面，先证明内容密度，再让用户收藏。", "适合 N 条职场细节、收藏版、手册、提问话术、微习惯。", "字太小会降低点击；封面要有一眼能读懂的主标题。", ["18_collect_4076赞_工作10年总结出的100个职场小细节.jpg", "21_collect_3173赞_办公室里一定要有的心眼子_收藏版_.jpg"]),
    ("类型4-新人身份标签加痛点承诺", "封面突出刚毕业、职场新人、实习生、年轻女生等身份，再给出一个生存/避坑承诺。", "适合新人手册入口、职场身份切换、入职前准备。", "身份标签要精准，避免泛泛写新人必看。", ["03_top_35000赞_给刚毕业学弟学妹的职场生存tips.jpg", "12_top_13000赞_职场新人大忌_学生_巨婴思维.jpg"]),
    ("类型5-弱爆边界样本封面", "保留低互动样本，用来观察同样是职场关键词，哪些封面没有把承诺、痛点或层级讲清楚。", "适合作为反面教材，不作为优先模仿模板。", "只用于避坑分析，不能直接当优质封面模板复用。", ["24_bottom_2赞_新人如何避免成为全单位工作的接盘侠.jpg", "26_bottom_10赞_职场新人责任心太强会让自己更痛苦吗.jpg"]),
]


def classify(title: str, content: str):
    combined = f"{title} {content[:80]}"
    if not title:
        return None
    for rule in FORMULAS:
        if rule.predicate(combined):
            return rule
    return None


def evidence_level(count: int, max_likes: int, low_fan_breakouts: int) -> str:
    if count >= 4 or (count >= 2 and max_likes >= 10000) or low_fan_breakouts >= 2:
        return "强证据"
    if count >= 2 or max_likes >= 10000:
        return "中证据"
    return "弱证据/观察"


def write_if_changed(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return "unchanged"
    status = "updated" if path.exists() else "created"
    path.write_text(content, encoding="utf-8")
    return status


def representative(rows: list[dict], limit: int = 5) -> list[dict]:
    return sorted(rows, key=lambda r: (r["likes"], r["collects"], r["comments"]), reverse=True)[:limit]


def make_title_entry(keyword, report_stem, appendix_stem, rule, rows, archive_date):
    reps = representative(rows, 5)
    low_fan_breakouts = sum(1 for r in rows if r["followers"] and r["likes"] / max(r["followers"], 1) >= 5)
    level = evidence_level(len(rows), max((r["likes"] for r in rows), default=0), low_fan_breakouts)
    lines = [
        f"# {rule.name}", "", "**类型：** 关键词标题公式", f"**关键词：** {keyword}", f"**搜索意图：** {rule.intent}",
        f"**来源报告：** [[{report_stem}]]", f"**逐篇附录：** [[{appendix_stem}]]", f"**证据等级：** {level}", "",
        "**公式/内容：**", "```text", rule.template, "```", "", f"**为什么值得入标题库：** {rule.hook}", "",
        f"**适用条件/限定：** {rule.condition}", "", f"**风险：** {rule.risk}", "", "**代表数据：**",
    ]
    for r in reps:
        lines.append(f"- {r['author'] or '未提供账号'}《{r['title']}》：点赞 {fmt_num(r['likes'])}，收藏 {fmt_num(r['collects'])}，评论 {fmt_num(r['comments'])}，分享 {fmt_num(r['shares'])}，粉丝 {fmt_num(r['followers'])}，图片 {r['image_count']} 张")
    lines.extend(["", "**代表原始标题：**"])
    for r in reps:
        lines.append(f"- {r['title']}")
    lines.extend(["", "**同源笔记完整信息（组合搭配时参考）：**"])
    for r in reps[:3]:
        lines.append(f"- 标题原文：{r['title']}")
        lines.append(f"  - 内容簇：{rule.intent}")
        lines.append(f"  - 封面/图集形态：图片 {r['image_count']} 张；具体封面见报告 assets 或封面库代表类型")
        lines.append(f"  - 正文风格：{r['content_preview']}")
        lines.append(f"  - 点赞/收藏/分享：{fmt_num(r['likes'])}/{fmt_num(r['collects'])}/{fmt_num(r['shares'])}")
    lines.extend(["", "---", f"*首次归档：{archive_date}；来源关键词：{keyword}*"])
    return "\n".join(lines) + "\n"


def make_topic_entry(keyword, report_stem, appendix_stem, topic, rows, archive_date):
    name, cluster, logic, production, risk = topic
    reps = representative(rows, 6)
    lines = [
        f"# {name}", "", "**类型：** 选题判断", f"**关键词：** {keyword}", f"**来源报告：** [[{report_stem}]]",
        f"**逐篇附录：** [[{appendix_stem}]]", "**证据状态：** 关键词搜索结果快照，多账号交叉观察", "",
        "**规律/判断：**", logic, "", "**适合做成什么：**", production, "", "**适用条件/限定：**", risk, "", "**代表数据：**",
    ]
    for r in reps:
        lines.append(f"- {r['author'] or '未提供账号'}《{r['title']}》：点赞 {fmt_num(r['likes'])}，收藏 {fmt_num(r['collects'])}，粉丝 {fmt_num(r['followers'])}")
    lines.extend(["", "**可延展选题：**"])
    if "反面" in cluster:
        lines.extend(["- 为什么同样带“职场新人”关键词，有些笔记互动低？", "- 弱标题常见问题：只有问题，没有新鲜承诺；只有关键词，没有强情绪或强场景。", "- 弱封面常见问题：信息层级不清、承诺不明确、痛点不够一眼读懂。"])
    else:
        lines.extend([f"- {name}：入门篇", f"- {name}：错误行为清单", f"- {name}：可复制话术/动作清单"])
    lines.extend(["", "---", f"*首次归档：{archive_date}；来源关键词：{keyword}*"])
    return "\n".join(lines) + "\n"


def make_cover_entry(keyword, report_stem, appendix_stem, cover, copied, archive_date):
    name, pattern, when, risk, _ = cover
    lines = [
        f"# {name}", "", "**类型：** 封面类型", f"**关键词：** {keyword}", f"**来源报告：** [[{report_stem}]]",
        f"**逐篇附录：** [[{appendix_stem}]]", "", "**封面结构：**", pattern, "", "**适用内容：**", when, "", "**风险/限制：**", risk, "", "**代表图：**",
    ]
    if copied:
        for img in copied:
            lines.append(f"![{Path(img).stem}|300](图片/{img})")
    else:
        lines.append("- 未找到可复制的代表图，需回看报告 assets。")
    lines.extend(["", "**归档判断：** 只保存代表图，不搬运全部采集图；该条目用于后续做封面结构参考。", "", "---", f"*首次归档：{archive_date}；来源关键词：{keyword}*"])
    return "\n".join(lines) + "\n"


def load_rows(xlsx_path: Path):
    df = pd.read_excel(xlsx_path)
    for col in ["点赞量", "收藏量", "评论量", "分享量", "粉丝数", "图片数量"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    rows = []
    grouped = defaultdict(list)
    formula_counts = Counter()
    for idx, row in df.iterrows():
        title = clean_text(row["笔记标题"])
        content = clean_text(row["笔记内容"])
        rule = classify(title, content)
        item = {
            "index": idx + 1, "title": title or "无标题/封面正文驱动型", "content": content,
            "content_preview": re.sub(r"\s+", " ", content[:90]) + ("…" if len(content) > 90 else ""),
            "author": clean_text(row["博主昵称"]), "likes": number(row["点赞量"]), "collects": number(row["收藏量"]),
            "comments": number(row["评论量"]), "shares": number(row["分享量"]), "followers": number(row["粉丝数"]),
            "image_count": number(row["图片数量"]), "intent": rule.intent if rule else "反面教材 / 边界样本",
        }
        rows.append(item)
        if rule:
            grouped[rule.name].append(item)
            formula_counts[rule.name] += 1
    return rows, grouped, formula_counts


def update_manifest(manifest_path: Path, payload: dict):
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    data = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {"archives": []}
    data["archives"] = [a for a in data.get("archives", []) if a.get("report_path") != payload["report_path"]]
    data["archives"].append(payload)
    manifest_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--xlsx", default=os.environ.get("XLSX_PATH"))
    parser.add_argument("--report", default=os.environ.get("REPORT_PATH"))
    parser.add_argument("--appendix", default=os.environ.get("APPENDIX_PATH"))
    parser.add_argument("--vault", default=os.environ.get("VAULT_PATH", r"C:\Users\Lenovo\Desktop\小红书\obsidian1"))
    parser.add_argument("--keyword", default=os.environ.get("KEYWORD", DEFAULT_KEYWORD))
    parser.add_argument("--archive-date", default=os.environ.get("ARCHIVE_DATE", date.today().isoformat()))
    args = parser.parse_args()

    xlsx_path, report_path, appendix_path, vault = Path(args.xlsx), Path(args.report), Path(args.appendix), Path(args.vault)
    keyword, archive_date = args.keyword, args.archive_date
    rows, grouped, formula_counts = load_rows(xlsx_path)
    title_dir, topic_dir, cover_dir = vault / "标题库" / keyword, vault / "选题库" / keyword, vault / "封面模版库" / keyword
    assets_dir, cover_img_dir = report_path.with_name(report_path.stem + "_assets"), cover_dir / "图片"
    changed = {"titles": [], "topics": [], "covers": [], "copied_images": []}

    for rule in FORMULAS:
        rows_for_rule = grouped.get(rule.name, [])
        if not rows_for_rule:
            continue
        low_fan_breakouts = sum(1 for r in rows_for_rule if r["followers"] and r["likes"] / max(r["followers"], 1) >= 5)
        level = evidence_level(len(rows_for_rule), max(r["likes"] for r in rows_for_rule), low_fan_breakouts)
        if level == "弱证据/观察":
            continue
        path = title_dir / (safe_filename(rule.name) + ".md")
        status = write_if_changed(path, make_title_entry(keyword, report_path.stem, appendix_path.stem, rule, rows_for_rule, archive_date))
        changed["titles"].append({"file": str(path), "status": status, "evidence": level, "count": len(rows_for_rule)})

    by_intent = defaultdict(list)
    for row in rows:
        by_intent[row["intent"]].append(row)
    weak_rows = sorted(rows, key=lambda r: (r["likes"], r["collects"]))[:12]
    for topic in TOPIC_ENTRIES:
        topic_rows = weak_rows if "反面" in topic[1] else by_intent.get(topic[1], representative(rows, 8))
        path = topic_dir / (safe_filename(topic[0]) + ".md")
        status = write_if_changed(path, make_topic_entry(keyword, report_path.stem, appendix_path.stem, topic, topic_rows, archive_date))
        changed["topics"].append({"file": str(path), "status": status, "count": len(topic_rows)})

    for cover in COVER_ENTRIES:
        copied_names = []
        for image_name in cover[4]:
            src = assets_dir / image_name
            if src.exists():
                cover_img_dir.mkdir(parents=True, exist_ok=True)
                dst = cover_img_dir / image_name
                if not dst.exists() or src.stat().st_size != dst.stat().st_size:
                    shutil.copy2(src, dst)
                copied_names.append(image_name)
                changed["copied_images"].append(str(dst))
        path = cover_dir / (safe_filename(cover[0]) + ".md")
        status = write_if_changed(path, make_cover_entry(keyword, report_path.stem, appendix_path.stem, cover, copied_names, archive_date))
        changed["covers"].append({"file": str(path), "status": status, "images": len(copied_names)})

    skill_root = Path(__file__).resolve().parents[1]
    manifest_path = skill_root / "references" / "keyword_archive_manifest.json"
    update_manifest(manifest_path, {
        "keyword": keyword, "report_path": str(report_path), "appendix_path": str(appendix_path), "source_excel": str(xlsx_path),
        "archived_at": archive_date, "row_count": len(rows), "title_entries": changed["titles"], "topic_entries": changed["topics"],
        "cover_entries": changed["covers"], "copied_images": changed["copied_images"], "formula_counts": dict(formula_counts),
    })

    print(json.dumps({"keyword": keyword, "rows": len(rows), "title_entries": len(changed["titles"]), "topic_entries": len(changed["topics"]), "cover_entries": len(changed["covers"]), "copied_images": len(changed["copied_images"]), "title_dir": str(title_dir), "topic_dir": str(topic_dir), "cover_dir": str(cover_dir), "manifest": str(manifest_path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
