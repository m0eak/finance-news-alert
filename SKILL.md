---
name: finance-news-alert
description: 使用轻量 RSS / 网页新闻源抓取国际与国内财经新闻，完成标准化、聚类与候选事件整理，再由当前聊天模型完成归因分析、简报与单条预警输出。适合金融新闻预警 PoC、市场简报生成、利好利空归因与后续定时分发方案设计。
---

# finance-news-alert

这是一个轻量金融新闻预警 Skill 的“当前模型版”原型。

## 核心思路
- 脚本层只负责：
  - 新闻抓取
  - 标准化
  - 轻量聚类
  - 候选事件整理
- **不在脚本里调用任何外部模型 API**
- 最终的金融影响分析、digest、alert，交给**当前聊天模型**完成

## 当前脚本
- `scripts/fetch_news.py`
  - 抓取国际 RSS 和国内财联社电报
- `scripts/normalize_news.py`
  - 转成统一 JSON 结构
  - 做第一轮输入清洗 / 噪音治理
- `scripts/cluster_news.py`
  - 做轻量聚类
  - 计算优先级分数与排序
- `scripts/prepare_analysis_input.py`
  - 从聚类结果中挑出最值得分析的候选事件
  - 输出给当前模型读取的 `analysis_input.json`
- `scripts/run_poc.py`
  - 串联整条前半段链路

## 当前输出目录
- `data/raw/`
  - 原始抓取结果
- `data/normalized/`
  - 标准化结果
- `data/clustered/`
  - 聚类结果
- `data/analysis/`
  - 供当前模型读取的候选分析输入
- `data/output/`
  - 可选的人类最终输出目录（如后续需要落盘）

## 当前适合做什么
- 跑一轮金融新闻 PoC，查看当前候选事件集合
- 让当前模型基于 `analysis_input.json` 生成：
  - 市场简报
  - 单条高优先级提醒
  - 利好 / 利空 / 逻辑归因
- 继续迭代分类 / alert 阈值 / 规则边界
- 为后续 `cron` + `message` 分发做准备

## 使用方式
先运行：

```bash
python3 scripts/run_poc.py
```

或：

```bash
bash scripts/manual_run.sh
```

然后由当前模型读取：
- `data/analysis/analysis_input.json`

并完成：
- 结构化金融影响分析
- digest 生成
- 单条 alert 判断

## 当前不做
- 不做交易建议
- 不做自动下单
- 不做脚本内置模型 API 调用
- 不做重型依赖集成（Docker / OpenBB / 数据库）
- 不直接承诺“全自动稳定推送”——当前更适合作为可试用原型继续打磨
