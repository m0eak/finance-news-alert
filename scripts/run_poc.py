#!/usr/bin/env python3
"""
run_poc.py

用途：
- 串联 finance-news-alert 的整条 PoC 流程。
- 按顺序执行抓取、标准化、聚类、分析、渲染。

输入：
- 不直接读取业务数据文件，而是依次调用各阶段脚本。

输出：
- 间接产出整条链路的所有中间文件和最终输出。

在流程中的位置：
- 总入口脚本。
- 适合手动跑一整轮流程，也适合作为后续 cron 的调用入口候选。

用法：
- 在 skill 根目录或任意位置运行都可以：
  - `python3 scripts/run_poc.py`
- 如果当前目录已经在 `scripts/` 下，也可以：
  - `python3 run_poc.py`

运行后会依次执行：
1. `fetch_news.py`
2. `normalize_news.py`
3. `cluster_news.py`
4. `analyze_news.py`
5. `render_digest.py`

常见排查方式：
- 看原始抓取：`data/raw/`
- 看标准化结果：`data/normalized/`
- 看聚类结果：`data/clustered/`
- 看模型分析：`data/analysis/`
- 看最终输出：`data/output/`

注意：
- `analyze_news.py` 依赖模型 API 环境变量；如果缺少密钥，流程会在分析阶段失败。
- 建议先确认前几步输出正常，再检查模型调用问题。
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
    run("analyze_news.py")
    run("render_digest.py")
    print("PoC done")
