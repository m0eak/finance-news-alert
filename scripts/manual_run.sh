#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASE_DIR"

python3 "$BASE_DIR/scripts/run_poc.py"

echo
echo "输出文件："
echo "- $BASE_DIR/data/raw/news_raw.json"
echo "- $BASE_DIR/data/normalized/news_normalized.json"
echo "- $BASE_DIR/data/clustered/news_clustered.json"
echo "- $BASE_DIR/data/analysis/analysis_input.json"
echo
echo "=== analysis_input.json（前 120 行） ==="
sed -n '1,120p' "$BASE_DIR/data/analysis/analysis_input.json"
