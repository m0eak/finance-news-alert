#!/usr/bin/env python3
"""
prepare_analysis_input.py

用途：
- 从聚类结果里挑出最值得让当前模型分析的候选事件簇。
- 不调用任何外部模型 API，只做裁剪、排序、整理输入。

输入：
- `data/clustered/news_clustered.json`

输出：
- `data/analysis/analysis_input.json`

说明：
- 这个脚本是“当前模型版”架构的中间层。
- 上游脚本负责抓取 / 标准化 / 聚类。
- 当前聊天模型读取本脚本产物后，负责真正的金融影响分析与最终文案生成。
"""
import json
import pathlib

BASE = pathlib.Path(__file__).resolve().parent.parent
IN_FILE = BASE / "data" / "clustered" / "news_clustered.json"
OUT_DIR = BASE / "data" / "analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT_DIR / "analysis_input.json"

TOP_N = 12


def simplify_cluster(cluster: dict) -> dict:
    items = cluster.get("items", [])[:3]
    return {
        "cluster_id": cluster.get("cluster_id", ""),
        "title": cluster.get("title", ""),
        "summary": cluster.get("summary", ""),
        "main_source": cluster.get("main_source", ""),
        "sources": cluster.get("sources", []),
        "urls": cluster.get("urls", [])[:3],
        "first_seen_at": cluster.get("first_seen_at", ""),
        "last_seen_at": cluster.get("last_seen_at", ""),
        "region": cluster.get("region", ""),
        "category_hint": cluster.get("category_hint", "market"),
        "priority_score": cluster.get("priority_score", 0),
        "items_count": cluster.get("items_count", 0),
        "sample_items": [
            {
                "title": item.get("title", ""),
                "summary": item.get("summary", ""),
                "source": item.get("source", ""),
                "published_at": item.get("published_at", ""),
                "url": item.get("url", ""),
            }
            for item in items
        ],
    }


def main():
    clusters = json.loads(IN_FILE.read_text(encoding="utf-8"))
    top_clusters = clusters[:TOP_N]
    payload = {
        "meta": {
            "mode": "current-model-analysis",
            "top_n": TOP_N,
            "cluster_count": len(clusters),
            "selected_count": len(top_clusters),
        },
        "clusters": [simplify_cluster(c) for c in top_clusters],
    }
    OUT_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUT_FILE)


if __name__ == "__main__":
    main()
