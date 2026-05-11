#!/usr/bin/env python3
"""
analyze_news.py

用途：
- 调用真实模型对事件簇做结构化金融影响分析。
- 输出摘要、利好/利空方向、逻辑、影响级别、置信度和是否提醒。

输入：
- `data/clustered/news_clustered.json`

输出：
- 写入 `data/analysis/analysis.json`。

在流程中的位置：
- 第 4 步，负责把候选事件簇转成结构化分析结果。
- 下游由 `render_digest.py` 渲染成人可读文本。
"""
import json
import os
import pathlib
import re
import urllib.request

BASE = pathlib.Path(__file__).resolve().parent.parent
IN_FILE = BASE / "data" / "clustered" / "news_clustered.json"
OUT_DIR = BASE / "data" / "analysis"
OUT_DIR.mkdir(parents=True, exist_ok=True)
DEFAULT_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash")
API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")

PROMPT_TEMPLATE = """你是一个金融新闻影响分析助手。
你的任务不是给出买卖建议，而是根据输入新闻，判断它可能对哪些市场、板块、资产或主题产生利好或利空影响，并解释原因。

必须遵守：
1. 只做方向性影响分析，不提供交易建议。
2. 如果新闻信息不足，降低置信度，不要硬编。
3. 优先分析：宏观、行业/板块、资产类别。
4. 只有当事件具有较强宏观、地缘、流动性、能源或系统性影响时，才把 should_alert 设为 true。
5. 普通公司新闻、一般涨跌播报、信息不足的条目，默认 should_alert = false。
6. 输出必须是 JSON。

输出字段：
- summary
- bullish
- bearish
- logic
- impact_level（high/medium/low）
- confidence（high/medium/low）
- should_alert（true/false）
"""


def extract_json_object(text: str) -> dict:
    text = (text or "").strip()
    if not text:
        raise ValueError("empty model output")

    try:
        return json.loads(text)
    except Exception:
        pass

    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if fenced:
        try:
            return json.loads(fenced.group(1))
        except Exception:
            pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end + 1]
        return json.loads(candidate)

    raise ValueError("no valid json object found in model output")


def call_deepseek(cluster: dict) -> dict:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY not found")

    user_prompt = (
        "请分析下面这条事件簇，并只输出 JSON。\n\n"
        f"事件簇：{json.dumps(cluster, ensure_ascii=False)}"
    )

    payload = {
        "model": DEFAULT_MODEL,
        "messages": [
            {"role": "system", "content": PROMPT_TEMPLATE},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.15,
        "response_format": {"type": "json_object"},
    }

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    content = data["choices"][0]["message"]["content"]
    result = extract_json_object(content)
    result["analysis_status"] = "real"
    result["analysis_model"] = DEFAULT_MODEL
    result["cluster_id"] = cluster.get("cluster_id", "")
    return result


def placeholder(cluster: dict, error: str) -> dict:
    return {
        "cluster_id": cluster.get("cluster_id", ""),
        "summary": cluster.get("summary", "")[:160],
        "bullish": [],
        "bearish": [],
        "logic": f"REAL_MODEL_FAILED: {error}",
        "impact_level": "low",
        "confidence": "low",
        "should_alert": False,
        "analysis_status": "fallback",
        "analysis_model": DEFAULT_MODEL,
    }


def main():
    clusters = json.loads(IN_FILE.read_text(encoding="utf-8"))
    analyses = []
    for cluster in clusters[:8]:
        try:
            analyses.append(call_deepseek(cluster))
        except Exception as e:
            analyses.append(placeholder(cluster, str(e)))

    analysis_file = OUT_DIR / "analysis.json"
    prompt_file = OUT_DIR / "prompt_template.txt"

    analysis_file.write_text(json.dumps(analyses, ensure_ascii=False, indent=2), encoding="utf-8")
    prompt_file.write_text(PROMPT_TEMPLATE, encoding="utf-8")

    print(f"model={DEFAULT_MODEL}")
    print(analysis_file)
    print(prompt_file)


if __name__ == "__main__":
    main()
