# finance-news-alert

A lightweight finance news alert PoC for OpenClaw-style workflows.

This version is designed around a **current-model analysis** architecture:

- scripts do the deterministic parts
- the current chat model does the final reasoning
- no model API key is required inside the skill itself

## Architecture

Pipeline:

1. `fetch_news.py`
   - pulls RSS / web sources
2. `normalize_news.py`
   - cleans and standardizes raw news into a unified schema
3. `cluster_news.py`
   - lightly clusters and ranks event candidates
4. `prepare_analysis_input.py`
   - trims the candidate set into a compact JSON payload for the current model
5. the **current chat model** reads `analysis_input.json`
   - produces digest / alert / impact reasoning

## Why this version

The earlier version called an external model API from inside the script.
This refactor removes that requirement.

Benefits:

- no extra model API key in the repo
- no duplicated model configuration inside the skill
- better alignment with the active model in the current session
- easier to integrate into agent-driven workflows

## Current news sources

- CNBC RSS
- Financial Times RSS
- Yahoo Finance RSS
- 财联社电报

## Quick start

Requirements:

- Python 3.10+

Run the pre-analysis pipeline:

```bash
python3 scripts/run_poc.py
```

Or use the helper script:

```bash
bash scripts/manual_run.sh
```

Generated files:

- `data/raw/news_raw.json`
- `data/normalized/news_normalized.json`
- `data/clustered/news_clustered.json`
- `data/analysis/analysis_input.json`

## How to use with the current model

After running the scripts, let the current agent/model read:

- `data/analysis/analysis_input.json`

Then ask it to produce:

- a ranked finance digest
- one high-priority alert candidate
- bullish / bearish directions
- impact logic and confidence

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
    ├── prepare_analysis_input.py
    ├── run_poc.py
    └── manual_run.sh
```

## Can this run in LobeHub / LobeChat?

Yes, this structure is **closer** to that direction than the previous one.

Current status:

- still a standalone script-based PoC
- no native LobeChat extension packaging yet
- better suited for integration because the final reasoning is delegated to the current model

Natural next steps:

1. wrap this as an MCP server
2. expose the pre-analysis pipeline as a tool/API
3. let LobeChat call it and use its active model for final reasoning

## Limitations

- lightweight clustering only
- no scheduler included
- no automatic message delivery in this repo
- no trading advice, no order execution
- designed as a PoC, not a production-grade financial terminal

## Roadmap ideas

- better semantic clustering / deduplication
- cooldown / repeat suppression
- more China-friendly source expansion
- markdown / chat-friendly rendering
- MCP server wrapper for LobeChat / LobeHub integration
- optional Discord / Telegram / webhook delivery layer
