# YouTube播客生成器设置指南

## 📋 概述

YouTube播客生成器是一个专为英语学习设计的工具，能够将英文YouTube视频转换为中文播客和导读文章，自动分类到全球视野系列。

## 🚀 快速开始

### 1. 安装依赖

```bash
# 方法1: 安装完整项目依赖 (推荐)
pip install -r requirements.txt

# 方法2: 仅安装YouTube额外依赖
pip install -r requirements_youtube_only.txt

# 方法3: 手动安装特定包
pip install gradio-client google-api-python-client
```

### 4. 本地TTS支持（推荐）

为了支持本地音频生成，建议安装eSpeak TTS引擎：

#### Ubuntu/Debian系统
```bash
sudo apt-get update
sudo apt-get install -y espeak espeak-data
```

#### 验证安装
```bash
espeak "Hello World" -v zh -s 150
```

如果听到语音输出，说明安装成功。如果无法安装eSpeak，系统会生成播客文本脚本并提供替代学习方案。

### 2. 配置API密钥

确保在`.env`文件中配置以下密钥：

```bash
# 必需 - Gemini API密钥（用于内容生成）
GEMINI_API_KEY=your_gemini_api_key_here

# 可选 - YouTube Data API密钥（用于获取详细视频信息）
YOUTUBE_API_KEY=your_youtube_api_key_here
```

**获取API密钥方法：**
- **Gemini API**: 访问 [Google AI Studio](https://makersuite.google.com/app/apikey) 获取免费API密钥
- **YouTube Data API**: 访问 [Google Cloud Console](https://console.cloud.google.com/) 创建项目并启用YouTube Data API v3

### 3. 使用方法

1. 运行主程序：`python run.py`
2. 选择 `6. YouTube播客生成器`
3. 选择 `1. 生成YouTube播客学习文章`
4. 输入YouTube视频链接
5. 等待1-3分钟自动处理

## 📁 文件结构

生成的文件将保存到以下位置：

```
📁 项目根目录
├── assets/audio/                    # 播客音频文件
│   └── youtube-YYYYMMDD-视频ID.mp3
├── assets/images/posts/YYYY/MM/     # 视频缩略图
│   └── youtube-YYYYMMDD-视频ID-thumbnail.jpg
└── _drafts/                         # 生成的Jekyll文章
    └── YYYY-MM-DD-youtube-learning-视频ID.md
```

## 📝 生成的文章结构

```markdown
---
title: "【英语学习】文章标题"
date: 2025-07-29
categories: [global-perspective]
tags: ["英语学习", "YouTube", "全球视野"]
excerpt: "文章摘要（50-60字）"
header:
  teaser: "{{ site.baseurl }}/assets/images/posts/2025/07/thumbnail.jpg"
---

## 📺 原始视频
**YouTube链接**: [视频标题](https://youtube.com/watch?v=...)
**时长**: X分钟 | **难度**: 中级 | **频道**: 频道名称

<!-- more -->

## 🎧 中文播客导读
<audio controls>
  <source src="{{ site.baseurl }}/assets/audio/youtube-20250729-topic.mp3" type="audio/mpeg">
</audio>

## 📋 内容大纲
- 🎯 核心观点1
- 🌍 全球视野角度
- 💡 关键洞察
- 🤔 思考要点

## 🌍 英语学习指南
### 🔤 关键词汇
### 💬 常用表达  
### 🏛️ 文化背景

## 🎯 学习建议
[学习方法和使用建议]
```

## 🔧 技术架构

### 核心组件

1. **YouTubePodcastGenerator**: 主要处理类
2. **Podcastfy API**: 托管播客生成服务
3. **Gemini API**: 内容分析和中文导读生成
4. **YouTube Data API**: 视频信息获取（可选）

### 处理流程

```
YouTube链接 → 视频信息提取 → Podcastfy播客生成 → Gemini导读生成 → Jekyll文章创建
```

## ⚙️ 配置文件

主要配置文件：`config/youtube_podcast_config.yml`

```yaml
# API配置
api_keys:
  gemini_api_key: "${GEMINI_API_KEY}"
  youtube_api_key: "${YOUTUBE_API_KEY}"

# Podcastfy配置
podcastfy:
  endpoint: "thatupiso/Podcastfy.ai_demo"
  tts_model: "edge"  # 免费TTS
  conversation_style: "casual,informative"

# 内容配置
content:
  category: "global-perspective"
  title_prefix: "【英语学习】"
```

## 🚨 故障排除

### 常见问题

**1. 导入错误**
```bash
ImportError: No module named 'gradio_client'
```
**解决方案**: 安装依赖 `pip install -r requirements_youtube.txt`

**2. API密钥错误**
```
❌ 未配置GEMINI_API_KEY
```
**解决方案**: 在`.env`文件中设置`GEMINI_API_KEY`

**3. YouTube链接无效**
```
❌ 请输入有效的YouTube链接
```
**解决方案**: 确保链接格式正确，支持：
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`

**4. 网络连接问题**
```
❌ Podcastfy 客户端连接失败
```
**解决方案**: 检查网络连接，确保能访问HuggingFace Spaces

### 调试模式

在`run.py`中选择`6. YouTube播客生成器` → `2. 查看配置状态`检查系统状态。

## 📊 使用限制

- **视频时长**: 建议60分钟以内
- **语言**: 最佳效果为英文视频
- **网络**: 需要稳定的国际网络连接
- **API配额**: Gemini API有每日调用限制

## 🔄 更新和维护

定期检查依赖包更新：
```bash
pip install --upgrade -r requirements_youtube.txt
```

## 💡 最佳实践

1. **视频选择**: 选择高质量的英文教育或商业内容
2. **标题优化**: 使用自定义标题功能提高吸引力
3. **后期编辑**: 生成后可手动编辑文章内容
4. **分批处理**: 避免同时处理大量视频
5. **备份重要**: 定期备份生成的音频和文章文件

## 📞 技术支持

如遇问题，请：
1. 检查配置状态
2. 查看系统日志（`run.py` → `8. 调试和维护工具` → `3. 查看系统日志`）
3. 参考错误处理指南