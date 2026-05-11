# data/normalized/

这个目录存放标准化后的新闻对象。

## 目录用途

把不同来源的数据统一成内部一致的数据结构，供聚类和分析层继续使用。

## 这里的文件通常是什么

例如：

- 统一字段后的新闻列表 JSON
- 已做基础清洗和标题标准化的中间结果

## 典型字段

常见字段包括：

- `id`
- `title`
- `summary`
- `source`
- `url`
- `published_at`
- `region`
- `category_hint`
- `normalized_title`
- `priority_score`

## 作用

这一层的目标不是做复杂判断，而是把输入先变干净、统一、可处理。
