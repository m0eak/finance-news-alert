#!/usr/bin/env python3
"""
normalize_news.py

用途：
- 把抓取层得到的原始新闻统一成内部标准结构。
- 完成基础清洗、噪音过滤、标题标准化、时间标准化和简单分类提示。

输入：
- `data/raw/news_raw.json`

输出：
- 写入 `data/normalized/news_normalized.json`。

在流程中的位置：
- 第 2 步，负责把不同来源的数据整理成一致格式。
- 下游由 `cluster_news.py` 做去重、聚类和排序。
"""
import hashlib
import json
import pathlib
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

BASE = pathlib.Path(__file__).resolve().parent.parent
RAW_FILE = BASE / "data" / "raw" / "news_raw.json"
OUT_DIR = BASE / "data" / "normalized"
OUT_DIR.mkdir(parents=True, exist_ok=True)

NOISE_PATTERNS = [
    r"VIP资讯",
    r"解锁直达",
    r"风口研报",
    r"电报解读",
    r"点击查看",
    r"点击加载更多",
]


def is_noise_text(text: str) -> bool:
    text = text or ""
    for pat in NOISE_PATTERNS:
        if re.search(pat, text, flags=re.IGNORECASE):
            return True
    return False


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", (text or "")).strip()
    text = re.sub(r"VIP资讯.*?财联社", "财联社", text)
    text = re.sub(r"解锁直达>\s*", "", text)
    return text.strip()


def normalize_title(title: str) -> str:
    title = clean_text(title).lower()
    title = re.sub(r"^(财联社\d+月\d+日电[，,:：]?|财联社[，,:：]?)", "", title)
    title = re.sub(r"^(快讯|电报|更新)[：: ]*", "", title)
    title = re.sub(r"\s+", " ", title)
    return title.strip()


def normalize_time(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return ""

    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc).isoformat()
    except Exception:
        pass

    if re.fullmatch(r"\d{2}:\d{2}", value):
        today = datetime.now().astimezone().date().isoformat()
        return f"{today}T{value}:00"

    return value


def make_id(source: str, title: str, url: str) -> str:
    raw = f"{source}|{title}|{url}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:16]


def infer_region(source: str) -> str:
    if source in {"cls_telegraph"}:
        return "china"
    return "international"


def infer_category(text: str) -> str:
    t = text.lower()

    macro_keywords = [
        "rate", "rates", "inflation", "cpi", "ppi", "fed", "ecb", "boj",
        "央行", "降息", "加息", "通胀", "货币政策", "财政", "社融", "汇率"
    ]
    commodity_keywords = [
        "oil", "crude", "brent", "wti", "gold", "silver", "copper",
        "原油", "黄金", "白银", "铜", "天然气"
    ]
    geopolitics_keywords = [
        "war", "tariff", "tariffs", "sanction", "sanctions", "iran", "israel",
        "地缘", "冲突", "制裁", "关税", "中东", "军事"
    ]
    industry_keywords = [
        "semiconductor", "chip", "battery", "defense", "pharma",
        "半导体", "芯片", "电池", "军工", "医药", "卫星", "航天", "物流", "配送"
    ]

    if any(k in t for k in macro_keywords):
        return "macro"
    if any(k in t for k in commodity_keywords):
        return "commodity"
    if any(k in t for k in geopolitics_keywords):
        return "geopolitics"
    if any(k in t for k in industry_keywords):
        return "industry"
    return "market"


def trim_summary(summary: str) -> str:
    summary = clean_text(summary)
    return summary[:280]


def main():
    raw = json.loads(RAW_FILE.read_text(encoding="utf-8"))
    items = []

    for bucket in raw.values():
        for source, entries in bucket.items():
            if isinstance(entries, dict):
                continue
            for entry in entries:
                title = clean_text(entry.get("title", "").strip())
                summary = trim_summary(entry.get("summary", "").strip())
                url = entry.get("url", "").strip()

                if is_noise_text(title) or is_noise_text(summary):
                    continue
                if len(title) < 8 and len(summary) < 12:
                    continue

                norm_title = normalize_title(title)
                item = {
                    "id": make_id(source, norm_title, url),
                    "title": title,
                    "summary": summary,
                    "source": source,
                    "url": url,
                    "published_at": normalize_time(entry.get("published_at", "")),
                    "region": infer_region(source),
                    "category_hint": infer_category(f"{title} {summary}"),
                    "normalized_title": norm_title,
                }
                items.append(item)

    out = OUT_DIR / "news_normalized.json"
    out.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
