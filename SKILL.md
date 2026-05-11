---
name: finance-news-alert
description: 使用轻量 RSS / 网页新闻源抓取国际与国内财经新闻，完成标准化、聚类、模型归因、简报与单条预警输出。适合金融新闻预警 PoC、市场简报生成、利好利空归因与后续 cron 定时分发方案设计。
---

# finance-news-alert

这是一个轻量金融新闻预警 Skill 的可试用原型。

## 当前阶段
- 已不再只是“抓取 + 标准化”骨架
- 当前已具备：
  - 新闻抓取
  - 标准化
  - 基础聚类
  - 真实模型分析
  - 简报输出
  - 单条预警输出
  - 第一轮噪音治理
  - 排序 / 打分
  - alert 阈值与 driver 优先逻辑

## 当前脚本
- `scripts/fetch_news.py`
  - 抓取国际 RSS 和国内财联社电报
- `scripts/normalize_news.py`
  - 转成统一 JSON 结构
  - 做第一轮输入清洗 / 噪音治理
- `scripts/cluster_news.py`
  - 做轻量聚类
  - 计算优先级分数与排序
- `scripts/analyze_news.py`
  - 调用真实模型做结构化金融影响分析
- `scripts/render_digest.py`
  - 生成 `digest.txt` 与 `alert.txt`
  - 负责 alert 最终筛选逻辑
- `scripts/run_poc.py`
  - 串联整条 PoC 链路

## 当前输出目录
- `data/raw/`
  - 原始抓取结果
- `data/normalized/`
  - 标准化结果
- `data/clustered/`
  - 聚类结果
- `data/analysis/`
  - 模型分析结果
- `data/output/`
  - 最终简报与单条预警文本

## 当前能力
### 已实现
- 国际源：
  - CNBC RSS
  - FT RSS
  - Yahoo Finance RSS
- 国内源：
  - 财联社电报
- 输出结构包含：
  - 摘要
  - 利好方向
  - 利空方向
  - 逻辑
  - 影响级别
  - 置信度
  - 是否建议提醒
- 已实现 `signal_type`：
  - `driver`
  - `outcome`
  - `mixed`
  - `neutral`
- 已实现 `driver bucket`：
  - `macro_policy`
  - `geopolitics_core`
  - `liquidity_risk`
  - `energy_chokepoint`
  - `other_driver`
- 当前单条提醒逻辑：
  - 优先只认 `driver`
  - `mixed` 基本不放行

## 当前适合做什么
- 跑一轮金融新闻 PoC，查看当前新闻结构化输出
- 观察简报排序是否合理
- 观察单条提醒是否更偏向源头驱动事件
- 继续迭代分类 / alert 阈值 / 规则边界
- 为后续 `cron` + `message` 分发做准备

## 当前不做
- 不做交易建议
- 不做自动下单
- 不做复杂数据库 / Web 前端
- 不做重型依赖集成（Docker / Lobster / OpenBB）
- 不直接承诺“全自动稳定推送”——当前更适合作为可试用原型继续打磨
