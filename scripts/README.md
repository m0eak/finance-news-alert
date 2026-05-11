# scripts/

这个目录放 `finance-news-alert` 的实际执行脚本。

## 目录用途

这里的文件负责跑完“当前模型版”的前半段流程：

- 抓取新闻
- 标准化
- 聚类 / 排序
- 整理候选分析输入
- 总控执行

## 当前文件说明

- `fetch_news.py`
  - 抓取国际 RSS 和国内财联社电报
  - 输出原始新闻数据到 `data/raw/`

- `normalize_news.py`
  - 把不同来源的新闻转成统一 JSON 结构
  - 做基础清洗、字段统一、标题标准化等
  - 输出到 `data/normalized/`

- `cluster_news.py`
  - 对标准化新闻做轻量聚类
  - 执行去重、合并、排序、打分
  - 输出到 `data/clustered/`

- `prepare_analysis_input.py`
  - 从聚类结果中挑出更值得进一步分析的候选事件簇
  - 生成 `data/analysis/analysis_input.json`
  - 给当前聊天模型读取并完成最终金融影响分析

- `run_poc.py`
  - 总入口脚本
  - 串联整条前半段流程
  - 一般优先从这里运行

- `manual_run.sh`
  - 手动触发入口
  - 适合快速跑一轮并预览 `analysis_input.json`

## 使用建议

- 日常手动调试：优先跑 `run_poc.py` 或 `manual_run.sh`
- 排查具体阶段问题：单独跑对应脚本
- 当前模型分析时，优先读取：
  - `data/analysis/analysis_input.json`

## 维护约定

- 一个脚本尽量只负责一层职责
- 不要把抓取、分析、渲染全部混在一个脚本里
- 如果后续增加新源，优先在抓取层扩展，而不是直接改最终输出层
