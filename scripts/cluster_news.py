#!/usr/bin/env python3
"""
cluster_news.py

用途：
- 对标准化后的新闻做轻量去重、聚类与优先级排序。
- 把重复或相近事件合并成事件簇，减少模型分析阶段的噪音。

输入：
- `data/normalized/news_normalized.json`

输出：
- 写入 `data/clustered/news_clustered.json`。

在流程中的位置：
- 第 3 步，负责生成给模型分析前的候选事件簇列表。
- 下游由 `analyze_news.py` 调模型继续分析。
"""
import json
import pathlib
from collections import defaultdict
from datetime import datetime, timezone

BASE = pathlib.Path(__file__).resolve().parent.parent
IN_FILE = BASE / "data" / "normalized" / "news_normalized.json"
OUT_DIR = BASE / "data" / "clustered"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_dt(value: str):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def age_hours(value: str):
    dt = parse_dt(value)
    if not dt:
        return None
    now = datetime.now(timezone.utc) if dt.tzinfo else datetime.now()
    delta = now - dt
    return max(delta.total_seconds() / 3600, 0)


def score_item(item: dict) -> float:
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()

    base = {
        "macro": 1.0,
        "geopolitics": 0.98,
        "commodity": 0.92,
        "industry": 0.76,
        "market": 0.55,
    }.get(item.get("category_hint", "market"), 0.5)

    source_bonus = {
        "ft": 0.16,
        "cnbc": 0.12,
        "yahoo_finance": 0.06,
        "cls_telegraph": 0.16,
    }.get(item.get("source", ""), 0.0)

    region_bonus = 0.03 if item.get("region") == "china" else 0.0

    keyword_bonus = 0.0
    high_priority_keywords = [
        "cpi", "ppi", "inflation", "央行", "加息", "降息", "利率",
        "oil", "brent", "wti", "原油", "黄金", "白银",
        "war", "iran", "israel", "制裁", "关税", "冲突",
        "withdrawals", "redemption", "赎回", "流动性"
    ]
    if any(k in text for k in high_priority_keywords):
        keyword_bonus += 0.12

    low_signal_keywords = [
        "raises $", "融资", "league", "padel", "delivery", "same-day",
        "partnership", "checkout", "campaign", "election"
    ]
    if any(k in text for k in low_signal_keywords):
        keyword_bonus -= 0.12

    age_bonus = 0.0
    hours = age_hours(item.get("published_at", ""))
    if hours is not None:
        if hours <= 2:
            age_bonus += 0.10
        elif hours <= 6:
            age_bonus += 0.05
        elif hours >= 18:
            age_bonus -= 0.08

    return round(base + source_bonus + region_bonus + keyword_bonus + age_bonus, 3)


def choose_main_title(items):
    items = sorted(items, key=lambda x: (score_item(x), len(x.get("title", ""))), reverse=True)
    return items[0].get("title", "") if items else ""


def choose_main_summary(items):
    items = sorted(items, key=lambda x: (score_item(x), len(x.get("summary", ""))), reverse=True)
    return items[0].get("summary", "") if items else ""


def cluster(items):
    groups = defaultdict(list)
    for item in items:
        key = item.get("normalized_title") or item.get("title")
        groups[key].append(item)

    clusters = []
    for idx, (_, group_items) in enumerate(groups.items(), start=1):
        group_items.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        dts = [parse_dt(x.get("published_at", "")) for x in group_items]
        dts = [d for d in dts if d is not None]

        priority = round(max(score_item(x) for x in group_items), 3) if group_items else 0.0
        cluster = {
            "cluster_id": f"cluster-{idx:03d}",
            "title": choose_main_title(group_items),
            "summary": choose_main_summary(group_items),
            "main_source": group_items[0].get("source", "") if group_items else "",
            "sources": sorted(list({x.get("source", "") for x in group_items})),
            "urls": sorted(list({x.get("url", "") for x in group_items if x.get("url", "")})),
            "first_seen_at": min(dts).isoformat() if dts else "",
            "last_seen_at": max(dts).isoformat() if dts else "",
            "region": group_items[0].get("region", "") if group_items else "",
            "category_hint": group_items[0].get("category_hint", "market") if group_items else "market",
            "priority_score": priority,
            "items_count": len(group_items),
            "items": group_items,
        }
        clusters.append(cluster)

    clusters.sort(key=lambda x: (x["priority_score"], x["last_seen_at"]), reverse=True)
    return clusters


def main():
    items = json.loads(IN_FILE.read_text(encoding="utf-8"))
    clusters = cluster(items)
    out = OUT_DIR / "news_clustered.json"
    out.write_text(json.dumps(clusters, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
