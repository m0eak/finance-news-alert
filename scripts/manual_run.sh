#!/usr/bin/env bash
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASE_DIR"

python3 "$BASE_DIR/scripts/run_poc.py"

echo
echo "输出文件："
echo "- $BASE_DIR/data/output/digest.txt"
echo "- $BASE_DIR/data/output/alert.txt"
echo
echo "=== digest.txt（前 80 行） ==="
sed -n '1,80p' "$BASE_DIR/data/output/digest.txt"
echo
echo "=== alert.txt（前 80 行） ==="
sed -n '1,80p' "$BASE_DIR/data/output/alert.txt"
