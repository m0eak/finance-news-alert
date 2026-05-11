#!/usr/bin/env python3
"""
render_digest.py

用途：
- 把聚类结果和模型分析结果渲染成最终给人阅读的文本。
- 当前负责生成汇总简报和单条高优先级预警。

输入：
- `data/clustered/news_clustered.json`
- `data/analysis/analysis.json`

输出：
- 写入 `data/output/` 下的最终文本文件，例如 `digest.txt`、`alert.txt`。

在流程中的位置：
- 第 5 步，负责最终输出。
- 这一层主要做呈现、筛选和文本组织。
"""
import json
import pathlib
from datetime import datetime

BASE = pathlib.Path(__file__).resolve().parent.parent
CLUSTER_FILE = BASE / "data" / "clustered" / "news_clustered.json"
ANALYSIS_FILE = BASE / "data" / "analysis" / "analysis.json"
OUT_DIR = BASE / "data" / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_analysis_map():
    if not ANALYSIS_FILE.exists():
        return {}
    analyses = json.loads(ANALYSIS_FILE.read_text(encoding="utf-8"))
    return {a.get("cluster_id", ""): a for a in analyses}


def fmt_list(values):
    if not values:
        return "无明显方向"
    return "、".join(values)


def classify_signal_type(cluster, analysis):
    text = f"{cluster.get('title', '')} {cluster.get('summary', '')} {analysis.get('logic', '')}".lower()
    driver_terms = [
        "央行", "加息", "降息", "利率", "cpi", "ppi", "inflation",
        "iran", "israel", "war", "制裁", "关税", "中东", "谈判", "增兵",
        "withdrawal", "withdrawals", "redemption", "赎回", "流动性", "封锁",
        "oil", "wti", "brent", "原油",
        "missile", "rocket", "drone", "strike", "attack", "airstrike", "military",
        "袭击", "空袭", "导弹", "无人机", "轰炸", "军事"
    ]
    outcome_terms = [
        "stocks jump", "stocks fall", "股走强", "股走弱", "上涨", "下跌", "涨", "跌",
        "open higher", "open lower", "市场上涨", "市场下跌", "升至", "跌至"
    ]

    has_driver = any(t in text for t in driver_terms)
    has_outcome = any(t in text for t in outcome_terms)

    if has_driver and not has_outcome:
        return "driver"
    if has_outcome and not has_driver:
        return "outcome"
    if has_driver and has_outcome:
        return "mixed"
    return "neutral"


def classify_driver_bucket(cluster, analysis):
    raw_text = f"{cluster.get('title', '')} {cluster.get('summary', '')}".lower()
    full_text = f"{cluster.get('title', '')} {cluster.get('summary', '')} {analysis.get('logic', '')}".lower()

    macro_terms = [
        "央行", "加息", "降息", "利率", "cpi", "ppi", "inflation", "通胀", "汇率",
        "fed", "federal reserve", "powell", "warsh", "fomc", "rate cut", "rate hike",
        "central bank", "governor", "chair", "monetary policy", "逆回购", "公开市场"
    ]
    geopolitics_terms = ["iran", "israel", "war", "中东", "谈判", "增兵", "制裁", "关税", "冲突", "军事"]
    liquidity_terms = ["withdrawal", "withdrawals", "redemption", "赎回", "流动性", "credit fund", "private credit"]
    chokepoint_core_terms = ["hormuz", "霍尔木兹"]
    chokepoint_route_terms = ["strait", "海峡"]
    chokepoint_transport_terms = ["shipping", "航运", "通航", "blockade", "封锁"]
    legal_regulation_terms = [
        "meta", "google", "alphabet", "lawsuit", "liable", "liability", "jury", "court",
        "mental health", "antitrust", "regulation", "regulatory", "监管", "诉讼", "判决", "赔偿"
    ]

    has_core_chokepoint = any(t in raw_text for t in chokepoint_core_terms)
    has_route_chokepoint = any(t in raw_text for t in chokepoint_route_terms)
    has_transport_chokepoint = any(t in raw_text for t in chokepoint_transport_terms)

    if any(t in full_text for t in legal_regulation_terms):
        return "other_driver", 0
    if any(t in full_text for t in macro_terms):
        return "macro_policy", 2
    if has_core_chokepoint or (has_route_chokepoint and has_transport_chokepoint):
        return "energy_chokepoint", 5
    if any(t in full_text for t in geopolitics_terms):
        return "geopolitics_core", 4
    if any(t in full_text for t in liquidity_terms):
        return "liquidity_risk", 3
    return "other_driver", 0


def classify_event_strength(cluster, analysis):
    text = f"{cluster.get('title', '')} {cluster.get('summary', '')} {analysis.get('logic', '')}".lower()
    category = str(cluster.get("category_hint", "market")).lower()
    signal_type = analysis.get("signal_type") or classify_signal_type(cluster, analysis)
    driver_bucket, _ = classify_driver_bucket(cluster, analysis)

    strong_terms = [
        "iran", "israel", "war", "missile", "attack", "strike", "drone", "bomb",
        "hormuz", "strait of hormuz", "霍尔木兹", "封锁", "制裁", "关税",
        "央行", "加息", "降息", "利率", "cpi", "ppi", "inflation", "通胀",
        "withdrawal", "withdrawals", "redemption", "赎回", "流动性", "credit", "private credit"
    ]
    medium_terms = [
        "oil", "wti", "brent", "原油", "shipping", "航运", "通航", "海峡",
        "谈判", "冲突", "military", "军事", "能源", "gold", "黄金", "silver", "白银"
    ]
    outcome_price_terms = [
        "rise", "rises", "rose", "up", "jump", "jumps", "fall", "falls",
        "上涨", "下跌", "触及", "升至", "跌至", "走强", "走弱"
    ]
    legal_terms = [
        "lawsuit", "court", "judge", "liable", "liability", "jury", "mental health",
        "recuse", "shareholder", "bias", "antitrust", "regulation", "regulatory",
        "诉讼", "判决", "赔偿", "监管"
    ]

    if signal_type == "outcome" and any(t in text for t in outcome_price_terms):
        if any(t in text for t in strong_terms):
            return "medium", 2
        return "weak", 1
    if any(t in text for t in legal_terms):
        return "medium", 2
    if any(t in text for t in strong_terms):
        return "strong", 3
    if driver_bucket in {"macro_policy", "geopolitics_core", "liquidity_risk"} and signal_type != "outcome":
        return "strong", 3
    if any(t in text for t in medium_terms):
        return "medium", 2
    if signal_type == "driver" or driver_bucket == "energy_chokepoint" or category in {"macro", "geopolitics", "commodity"}:
        return "medium", 2
    return "weak", 1


def classify_analysis_quality(analysis):
    logic = str(analysis.get("logic", "") or "").strip().lower()
    impact = str(analysis.get("impact_level", "unknown") or "unknown").lower()
    confidence = str(analysis.get("confidence", "unknown") or "unknown").lower()

    empty_logic_markers = {"", "暂无", "unknown", "none", "n/a", "无"}
    logic_empty = logic in empty_logic_markers
    impact_unknown = impact in {"unknown", "", "none", "n/a"}
    confidence_unknown = confidence in {"unknown", "", "none", "n/a"}

    empty_hits = sum([logic_empty, impact_unknown, confidence_unknown])

    if empty_hits >= 2:
        return "empty", 0
    if empty_hits == 1:
        return "partial", 1
    return "good", 2


def normalize_alert_decision(cluster, analysis):
    impact = str(analysis.get("impact_level", "low")).lower()
    confidence = str(analysis.get("confidence", "low")).lower()
    category = str(cluster.get("category_hint", "market")).lower()
    score = float(cluster.get("priority_score", 0) or 0)
    text = f"{cluster.get('title', '')} {cluster.get('summary', '')} {analysis.get('logic', '')}".lower()

    high_signal_terms = [
        "cpi", "ppi", "inflation", "央行", "加息", "降息", "利率", "汇率",
        "iran", "israel", "war", "冲突", "制裁", "关税", "中东",
        "oil", "wti", "brent", "原油", "黄金", "白银",
        "withdrawal", "withdrawals", "redemption", "赎回", "流动性", "封锁"
    ]
    low_signal_terms = [
        "融资", "raises $", "partnership", "delivery", "same-day", "padel", "checkout"
    ]

    has_high_signal = any(t in text for t in high_signal_terms)
    has_low_signal = any(t in text for t in low_signal_terms)
    signal_type = classify_signal_type(cluster, analysis)
    driver_bucket, driver_rank = classify_driver_bucket(cluster, analysis)

    should_alert = (
        category in {"macro", "geopolitics", "commodity"}
        and impact in {"high", "medium"}
        and confidence in {"high", "medium"}
        and score >= 1.28
        and has_high_signal
        and not has_low_signal
        and signal_type == "driver"
        and bool(analysis.get("should_alert", False))
    )

    if not should_alert and signal_type == "driver" and impact == "high" and confidence in {"high", "medium"} and score >= 1.27:
        should_alert = True

    analysis["signal_type"] = signal_type
    analysis["driver_bucket"] = driver_bucket
    analysis["driver_rank"] = driver_rank
    analysis["should_alert_final"] = should_alert
    return analysis


def top_clusters(clusters, analysis_map, limit=8):
    enriched = []
    for item in clusters:
        analysis = normalize_alert_decision(item, dict(analysis_map.get(item.get("cluster_id", ""), {})))
        event_strength, event_rank = classify_event_strength(item, analysis)
        analysis_quality, quality_rank = classify_analysis_quality(analysis)
        alert_rank = 1 if analysis.get("should_alert_final") else 0
        base_score = float(item.get("priority_score", 0) or 0)

        if event_strength == "strong" and analysis_quality == "empty":
            adjusted_score = base_score - 0.03
        elif event_strength == "medium" and analysis_quality == "empty":
            adjusted_score = base_score - 0.12
        elif event_strength == "weak" and analysis_quality == "empty":
            adjusted_score = base_score - 0.35
        elif event_strength == "weak" and analysis_quality == "partial":
            adjusted_score = base_score - 0.12
        else:
            adjusted_score = base_score

        analysis["event_strength"] = event_strength
        analysis["analysis_quality"] = analysis_quality
        analysis["adjusted_priority_score"] = round(adjusted_score, 4)

        enriched.append((
            alert_rank,
            event_rank,
            adjusted_score,
            analysis.get("driver_rank", 0),
            quality_rank,
            item,
            analysis,
        ))

    enriched.sort(key=lambda x: (x[0], x[1], x[2], x[3], x[4]), reverse=True)
    return [(item, analysis) for _, _, _, _, _, item, analysis in enriched[:limit]]


def render_digest(clusters, analysis_map):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "金融新闻简报（PoC）",
        f"生成时间：{now}",
        "",
    ]

    for idx, (item, analysis) in enumerate(top_clusters(clusters, analysis_map), start=1):
        lines.extend([
            f"{idx}. {item.get('title', '')}",
            f"- 来源：{item.get('main_source', '')}",
            f"- 分类：{item.get('category_hint', '')}",
            f"- 信号类型：{analysis.get('signal_type', 'neutral')}",
            f"- driver 桶：{analysis.get('driver_bucket', 'n/a')}",
            f"- 事件强度：{analysis.get('event_strength', 'weak')}",
            f"- 分析质量：{analysis.get('analysis_quality', 'empty')}",
            f"- 优先级分数：{item.get('priority_score', 0)}",
            f"- 调整后分数：{analysis.get('adjusted_priority_score', item.get('priority_score', 0))}",
            f"- 摘要：{analysis.get('summary') or item.get('summary', '')}",
            f"- 可能利好：{fmt_list(analysis.get('bullish', []))}",
            f"- 可能利空：{fmt_list(analysis.get('bearish', []))}",
            f"- 逻辑：{analysis.get('logic', '暂无')}",
            f"- 影响级别：{analysis.get('impact_level', 'unknown')}",
            f"- 置信度：{analysis.get('confidence', 'unknown')}",
            f"- 是否建议提醒：{analysis.get('should_alert_final', False)}",
            "",
        ])
    return "\n".join(lines).strip() + "\n"


def render_alert(clusters, analysis_map):
    ranked = top_clusters(clusters, analysis_map, limit=len(clusters))
    top = None
    for cluster, analysis in ranked:
        if analysis.get("should_alert_final"):
            top = (cluster, analysis)
            break
    if top is None:
        return "暂无高优先级单条提醒（已通过保守阈值 + 驱动优先过滤）。\n"

    cluster, analysis = top
    lines = [
        "金融新闻单条预警（PoC）",
        f"标题：{cluster.get('title', '')}",
        f"来源：{cluster.get('main_source', '')}",
        f"分类：{cluster.get('category_hint', '')}",
        f"信号类型：{analysis.get('signal_type', 'neutral')}",
        f"driver 桶：{analysis.get('driver_bucket', 'n/a')}",
        f"事件强度：{analysis.get('event_strength', 'weak')}",
        f"分析质量：{analysis.get('analysis_quality', 'empty')}",
        f"优先级分数：{cluster.get('priority_score', 0)}",
        f"调整后分数：{analysis.get('adjusted_priority_score', cluster.get('priority_score', 0))}",
        f"摘要：{analysis.get('summary') or cluster.get('summary', '')}",
        f"可能利好：{fmt_list(analysis.get('bullish', []))}",
        f"可能利空：{fmt_list(analysis.get('bearish', []))}",
        f"逻辑：{analysis.get('logic', '暂无')}",
        f"影响级别：{analysis.get('impact_level', 'unknown')}",
        f"置信度：{analysis.get('confidence', 'unknown')}",
        f"是否建议提醒：{analysis.get('should_alert_final', False)}",
    ]
    return "\n".join(lines).strip() + "\n"


def main():
    clusters = json.loads(CLUSTER_FILE.read_text(encoding="utf-8"))
    analysis_map = load_analysis_map()
    digest = render_digest(clusters, analysis_map)
    alert = render_alert(clusters, analysis_map)

    digest_file = OUT_DIR / "digest.txt"
    alert_file = OUT_DIR / "alert.txt"
    digest_file.write_text(digest, encoding="utf-8")
    alert_file.write_text(alert, encoding="utf-8")

    print(digest_file)
    print(alert_file)


if __name__ == "__main__":
    main()
