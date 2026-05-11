# data/analysis/

这个目录存放模型分析后的结构化结果。

## 目录用途

这里是模型对新闻事件做完金融影响判断后的输出，用于后续渲染成简报或提醒。

## 这里的文件通常是什么

例如：

- 模型分析结果 JSON
- 每个事件簇对应的结构化归因结果

## 常见字段

例如：

- `summary`
- `bullish`
- `bearish`
- `logic`
- `impact_level`
- `confidence`
- `should_alert`
- `signal_type`
- `driver_bucket`

## 使用建议

如果渲染文本看起来不合理，先看这里：

- 是模型本身判断歪了
- 还是渲染层把正确结果写坏了

## 注意

这一层应尽量保留结构化 JSON，避免只保留最终纯文本，不然不利于后续调试和回归。
