# finance-news-alert

A lightweight finance news alert PoC for OpenClaw-style workflows.

It pulls international and Chinese finance news, normalizes events, applies lightweight clustering and scoring, runs LLM-based impact analysis, and renders two outputs:

- `digest.txt`: ranked multi-item finance news brief
- `alert.txt`: a single high-priority alert candidate

## What it does

Pipeline:

1. `fetch_news.py`
   - Pulls RSS / web sources
2. `normalize_news.py`
   - Cleans and standardizes items into a unified JSON schema
3. `cluster_news.py`
   - Deduplicates lightly, clusters by normalized title, scores and ranks events
4. `analyze_news.py`
   - Calls a real model for structured impact analysis
5. `render_digest.py`
   - Renders final human-readable outputs

Current news sources:

- CNBC RSS
- Financial Times RSS
- Yahoo Finance RSS
- 财联社电报

## Output structure

The model analysis currently includes:

- `summary`
- `bullish`
- `bearish`
- `logic`
- `impact_level`
- `confidence`
- `should_alert`
- `signal_type`
- `driver_bucket`

The alert logic is intentionally conservative:

- prioritizes **driver** events over pure market outcome recaps
- generally filters out `mixed` items for single-alert output
- focuses more on macro / geopolitics / commodity / liquidity-sensitive events

## Quick start

Requirements:

- Python 3.10+
- A DeepSeek API key

Set environment variables:

```bash
export DEEPSEEK_API_KEY="your_key_here"
# optional
export DEEPSEEK_MODEL="deepseek-v4-flash"
export DEEPSEEK_API_URL="https://api.deepseek.com/chat/completions"
```

Run the full pipeline:

```bash
python3 scripts/run_poc.py
```

Or use the manual helper:

```bash
bash scripts/manual_run.sh
```

Generated files:

- `data/raw/news_raw.json`
- `data/normalized/news_normalized.json`
- `data/clustered/news_clustered.json`
- `data/analysis/analysis.json`
- `data/output/digest.txt`
- `data/output/alert.txt`

## Repo layout

```text
finance-news-alert/
├── SKILL.md
├── README.md
├── data/
│   ├── README.md
│   ├── raw/
│   ├── normalized/
│   ├── clustered/
│   ├── analysis/
│   └── output/
└── scripts/
    ├── fetch_news.py
    ├── normalize_news.py
    ├── cluster_news.py
    ├── analyze_news.py
    ├── render_digest.py
    ├── run_poc.py
    └── manual_run.sh
```

## Can this run in LobeHub / LobeChat?

Yes — but not as a drop-in native plugin yet.

Current status:

- this repo is a **standalone script-based PoC**
- it works well as a local/server-side pipeline
- it is **not yet packaged** as an MCP server, hosted API, or native LobeChat extension

Practical ways to use it today:

1. Run it as an independent pipeline on a VPS / local machine
2. Wrap it behind an MCP server or HTTP API for LobeChat
3. Add scheduling + message delivery as a later integration layer

## Limitations

- lightweight clustering only; similar stories may still remain split
- no cron / scheduler included by default
- no automatic message delivery in this repo
- no trading advice, no order execution
- designed as a PoC / prototyping workflow, not a production-grade financial terminal

## Roadmap ideas

- better semantic clustering / deduplication
- cooldown / repeat suppression
- more China-friendly source expansion
- markdown / chat-friendly rendering
- MCP server wrapper for LobeChat / LobeHub integration
- optional Discord / Telegram / webhook delivery layer

## Notes

This project is for information structuring and alert prototyping only.
It does **not** provide investment advice.

## Credits

Built as a finance-news-alert prototype inside an OpenClaw workspace.
