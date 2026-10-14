import json

# 每份 fixture 的期望，按 run_date 取。新增样本只需在这里加一项。
EXPECT = {
    "2026-10-14": {
        "must_items": [  # url 片段: 期望字段
            {"url": "L96R61BF", "type": "合作", "importance_min": 4},
        ],
        "items_count": 1,
        "must_filtered": ["L96NB5NE", "ifanr.com/1684200"],  # 这些链接不得出现在 items
        "forbid_competitor": ["钉钉", "飞书"],  # items 里不应出现
    },
    "2026-10-12": {
        "must_items": [
            {"url": "L92PVD0R", "importance_min": 3},
            {"url": "huxiu.com/article/4896760", "type": "行业观察", "importance_min": 2, "importance_max": 2},
        ],
        "items_count": 2,
        "must_filtered": ["anker-recorder-bean", "aily-repost"],
        "forbid_competitor": [],
    },
    "2026-11-01": {  # S1 空结果日
        "must_items": [], "items_count": 0, "must_filtered": [], "forbid_competitor": [],
        "forbid_words": ["importance"],  # 空日允许写「今日无动态」
    },
    "2026-11-02": {  # S2 年度发布会+同事件
        "must_items": [{"url": "dingtalk-9-launch", "importance_min": 5}],
        "items_count": 1,
        "must_filtered": ["dingtalk-9-media", "dingtalk-9-analysis"],
        "forbid_competitor": ["飞书", "企业微信"],
    },
    "2026-11-03": {  # S3 三家同天+横评
        "must_items": [
            {"url": "feishu-base-ai-field", "importance_min": 3, "importance_max": 3},
            {"url": "dingtalk-bank-partner", "type": "合作", "importance_min": 4},
            {"url": "wecom-5015-fix", "importance_min": 1, "importance_max": 2},
        ],
        "items_count": 3,
        "must_filtered": ["office-suite-review"],
        "forbid_competitor": [],
    },
    "2026-11-04": {  # S4 日期边界
        "must_items": [
            {"url": "dingtalk-doc-ai-formula", "importance_min": 3},
            {"url": "wecom-sheet-templates", "importance_min": 2},
        ],
        "items_count": 2,
        "must_filtered": ["www.feishu.cn", "wecom-old-news"],
        "forbid_competitor": ["飞书"],
    },
}
FORBID_WORDS = ["无动态", "无符合", "无官方动态", "没有动态", "importance"]


def main(out, run_date: str) -> dict:
    if isinstance(out, str):
        try:
            out = json.loads(out)
        except Exception:
            return {"score": "0/0", "fails": "out 不是合法 JSON"}
    exp = EXPECT.get(run_date)
    if not exp:
        return {"score": "-", "fails": f"没有 {run_date} 的期望，跳过打分"}

    items = out.get("items") or []
    text = (out.get("highlights") or "") + (out.get("comparison") or "")
    checks = []  # (名称, 是否通过, 说明)

    checks.append(("条数", len(items) == exp["items_count"], f"items {len(items)} 条，应为 {exp['items_count']}"))

    for m in exp["must_items"]:
        hit = [i for i in items if m["url"] in (i.get("url") or "")]
        if not hit:
            checks.append((f"收录 {m['url']}", False, "未收录"))
            continue
        it = hit[0]
        imp = it.get("importance") or 0
        try:
            imp = int(imp)
        except Exception:
            imp = 0
        if "type" in m:
            checks.append((f"{m['url']} type", it.get("type") == m["type"], f"type={it.get('type')}，应为 {m['type']}"))
        ok = imp >= m.get("importance_min", 0) and imp <= m.get("importance_max", 5)
        checks.append((f"{m['url']} importance", ok, f"importance={imp}"))

    for u in exp["must_filtered"]:
        bad = any(u in (i.get("url") or "") for i in items)
        checks.append((f"过滤 {u}", not bad, "仍在 items 中"))

    for c in exp["forbid_competitor"]:
        bad = any(i.get("competitor") == c for i in items)
        checks.append((f"无 {c} 条目", not bad, f"items 出现 {c}"))

    hits = [w for w in exp.get("forbid_words", FORBID_WORDS) if w in text]
    checks.append(("highlights/comparison 无禁词", not hits, "出现：" + "、".join(hits)))

    passed = sum(1 for _, ok, _ in checks if ok)
    fails = [f"{n}：{why}" for n, ok, why in checks if not ok]
    return {"score": f"{passed}/{len(checks)}", "fails": "；".join(fails) or "全部通过"}
