#!/usr/bin/env python3
"""
fetch_news.py

用途：
- 抓取 finance-news-alert 第一版使用的新闻源原始数据。
- 当前覆盖国际 RSS（CNBC / FT / Yahoo Finance）和国内财联社电报。

输入：
- 内置新闻源 URL 配置。

输出：
- 写入 `data/raw/news_raw.json`。

在流程中的位置：
- 第 1 步，负责把上游新闻先抓下来。
- 下游由 `normalize_news.py` 继续处理。
"""
import json
import pathlib
import re
import urllib.request
from html import unescape
from xml.etree import ElementTree as ET

BASE = pathlib.Path(__file__).resolve().parent.parent
RAW_DIR = BASE / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

RSS_SOURCES = {
    "cnbc": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "ft": "https://www.ft.com/rss/home/international",
    "yahoo_finance": "https://finance.yahoo.com/news/rssindex",
}
CLS_URL = "https://m.cls.cn/telegraph"


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def parse_rss(xml_text: str, source: str):
    items = []
    root = ET.fromstring(xml_text)
    channel = root.find("channel")
    if channel is None:
        return items
    for item in channel.findall("item")[:20]:
        items.append({
            "source": source,
            "source_type": "rss",
            "title": (item.findtext("title") or "").strip(),
            "summary": (item.findtext("description") or "").strip(),
            "url": (item.findtext("link") or "").strip(),
            "published_at": (item.findtext("pubDate") or "").strip(),
        })
    return items


def parse_cls(html: str):
    text = unescape(re.sub(r"<[^>]+>", " ", html))
    text = re.sub(r"\s+", " ", text)
    matches = re.findall(r"(\d{2}:\d{2})([^阅]{8,300}?)阅\s*\d+", text)
    items = []
    for t, body in matches[:20]:
        body = body.strip()
        if len(body) < 8:
            continue
        items.append({
            "source": "cls_telegraph",
            "source_type": "web",
            "title": body[:80],
            "summary": body,
            "url": CLS_URL,
            "published_at": t,
        })
    return items


def main():
    result = {"rss": {}, "china": {}}
    for name, url in RSS_SOURCES.items():
        try:
            xml_text = fetch_text(url)
            result["rss"][name] = parse_rss(xml_text, name)
        except Exception as e:
            result["rss"][name] = {"error": str(e)}

    try:
        html = fetch_text(CLS_URL)
        result["china"]["cls_telegraph"] = parse_cls(html)
    except Exception as e:
        result["china"]["cls_telegraph"] = {"error": str(e)}

    out = RAW_DIR / "news_raw.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
