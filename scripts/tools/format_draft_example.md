# 手工草稿快速排版工具使用指南

## 功能说明

`format_draft.py` 是一个智能草稿排版工具，可以将手工编写的简单文本快速转换为符合项目规范的Jekyll格式文章。

## 主要功能

1. **智能分类检测**: 基于内容关键词自动检测文章分类
2. **标签自动生成**: 根据内容和分类智能生成相关标签  
3. **摘要提取**: 自动生成50-60字符的精准摘要
4. **格式规范化**: 添加完整的front matter和页脚
5. **内容优化**: 自动添加`<!-- more -->`标签和格式调整

## 使用方法

### 基本用法
```bash
python scripts/tools/format_draft.py input.txt
```

### 高级用法
```bash
# 指定输出文件
python scripts/tools/format_draft.py input.txt -o _drafts/2025-01-15-my-article.md

# 指定标题和分类
python scripts/tools/format_draft.py input.txt -t "我的文章标题" -c tech-empowerment

# 指定标签
python scripts/tools/format_draft.py input.txt --tags "人工智能" "效率工具" "技术趋势"

# 详细输出
python scripts/tools/format_draft.py input.txt -v
```

## 输入文件格式

### 推荐格式
```
# 文章标题

这里是文章的开头段落，会被用作摘要提取的基础。

## 第一个小节

详细内容...

## 第二个小节

更多内容...

### 子标题

具体说明...

- 列表项1
- 列表项2
- 列表项3

## 总结

总结内容...
```

### 注意事项
- 如果第一行是`# 标题`格式，会自动提取作为文章标题
- 如果没有标题行，将使用文件名作为标题
- 已有front matter的文件会跳过处理
- 支持markdown格式，会自动优化格式

## 分类说明

工具支持四种分类，会根据内容关键词自动检测：

1. **cognitive-upgrade** (认知升级): 思维模型、学习方法、个人成长
2. **tech-empowerment** (技术赋能): 工具推荐、技术教程、效率提升  
3. **global-perspective** (全球视野): 国际趋势、文化观察、跨文化思维
4. **investment-finance** (投资理财): 投资策略、理财方法、财务规划

## 输出文件结构

格式化后的文件包含：

```yaml
---
title: "文章标题"
date: 2025-01-15
categories: [tech-empowerment]
tags: ["人工智能", "效率工具", "技术趋势"]
excerpt: "这是自动生成的50-60字符摘要..."
header:
  teaser: "/assets/images/default-teaser.jpg"
layout: single
author_profile: true
breadcrumbs: true
comments: true
related: true
share: true
toc: true
toc_icon: "list"
toc_label: "本页内容"
toc_sticky: true
---

文章开头段落...

<!-- more -->

## 详细内容

具体内容...

---

> 根据分类自动添加的页脚提示
```

## 使用流程建议

1. **编写原始文档**: 用任意文本编辑器编写原始内容
2. **运行格式化工具**: 使用本工具进行自动排版
3. **检查和调整**: 检查生成的文件，必要时手工调整
4. **发布到平台**: 使用`run.py`的"处理现有草稿"功能发布

## 常见问题

**Q: 如何修改默认头图？**  
A: 编辑生成的文件，修改`header.teaser`字段为您的图片路径

**Q: 分类检测不准确怎么办？**  
A: 使用`-c`参数手动指定分类

**Q: 如何添加更多标签？**  
A: 使用`--tags`参数指定，或在生成后手工编辑文件

**Q: 可以批量处理多个文件吗？**  
A: 当前版本不支持，建议使用shell脚本循环调用

## 示例

假设有文件`my_draft.txt`:
```
# ChatGPT在日常工作中的10个实用技巧

最近ChatGPT的普及让很多人开始关注AI工具在工作中的应用。

## 文案写作助手

ChatGPT可以帮助...

## 代码调试助手

在编程时...
```

运行命令：
```bash
python scripts/tools/format_draft.py my_draft.txt
```

会生成完整的Jekyll格式文章，包含：
- 分类：tech-empowerment  
- 标签：["人工智能", "AI工具", "效率工具", "技术工具"]
- 摘要："最近ChatGPT的普及让很多人开始关注AI工具在工作中的应用。"
- 完整的front matter和页脚