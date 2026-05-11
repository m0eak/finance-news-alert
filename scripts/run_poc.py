#!/usr/bin/env python3
"""
run_poc.py

用途：
- 串联 finance-news-alert 的“当前模型版”前半段流程。
- 按顺序执行抓取、标准化、聚类、准备分析输入。

输入：
- 不直接读取业务数据文件，而是依次调用各阶段脚本。

输出：
- 产出整条链路的中间文件，最终给当前聊天模型读取 `analysis_input.json` 后完成分析。

注意：
- 本脚本不再调用外部模型 API。
- 金融影响分析、digest、alert 的最终生成应由当前模型接手。
"""
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent


def run(script: str):
    path = BASE / script
    print(f"==> running {path.name}")
    subprocess.run([sys.executable, str(path)], check=True)


if __name__ == "__main__":
    run("fetch_news.py")
    run("normalize_news.py")
    run("cluster_news.py")
    run("prepare_analysis_input.py")
    print("PoC pre-analysis done")
