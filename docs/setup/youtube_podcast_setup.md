# YouTube播客生成器完整设置指南

## 📋 功能概述

YouTube播客生成器能够将英文YouTube视频转换为中文播客和导读文章，专为英语学习设计，自动分类到全球视野系列。

## 🚀 快速设置

### 1. 安装依赖

```bash
# 推荐：安装完整项目依赖
pip install -r requirements.txt
```

### 2. API密钥配置

在`.env`文件中配置以下密钥：

```bash
# 必需 - Gemini API密钥（用于内容生成）
GEMINI_API_KEY=your_gemini_api_key_here

# 可选 - YouTube Data API密钥（用于获取详细视频信息）
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### 3. 本地TTS支持（推荐）

安装eSpeak TTS引擎用于音频生成：

```bash
# Ubuntu/Debian系统
sudo apt-get update
sudo apt-get install -y espeak espeak-data

# 验证安装
espeak "Hello World" -v zh -s 150
```

## 🔑 API密钥详细配置

### Gemini API密钥（必需）

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 登录Google账号
3. 点击"Create API Key"
4. 复制生成的API密钥到`.env`文件

### YouTube Data API密钥（可选）

#### 为什么需要YouTube API密钥？

- ✅ **有API密钥**: 获取精确的视频标题、描述、时长、观看次数等
- ⚠️ **无API密钥**: 使用基础信息提取，功能稍有限制但仍可正常工作

#### 获取步骤

**1. 创建Google Cloud项目**
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 点击"选择项目" → "新建项目"
3. 输入项目名称：`youtube-podcast-generator`
4. 点击"创建"

**2. 启用YouTube Data API v3**
1. 在Google Cloud Console中选择刚创建的项目
2. 搜索"YouTube Data API v3"
3. 点击进入API页面并点击"启用"

**3. 创建API凭据**
1. 左侧菜单点击"凭据"
2. 点击"+ 创建凭据" → "API密钥"
3. 复制生成的API密钥

**4. 配置API密钥限制（推荐）**
- **应用限制**: 选择"无"（用于服务器应用）
- **API限制**: 选择"限制密钥"，勾选"YouTube Data API v3"

**5. 添加到项目配置**
```bash
# 添加到.env文件
YOUTUBE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

#### API配额限制
- **每日配额**: 10,000 units（免费）
- **单次视频查询**: 1 unit
- **足够使用**: 每日可查询10,000个视频信息

## 📝 使用方法

### 基本使用流程

1. 运行主程序：`python run.py`
2. 选择 `6. YouTube播客生成器`
3. 选择 `1. 生成YouTube播客学习文章`
4. 输入YouTube视频链接
5. 等待1-3分钟自动处理

### 验证配置

在菜单中选择：
```
run.py → 6. YouTube播客生成器 → 2. 查看配置状态
```

正确配置应显示：
```
GEMINI_API_KEY: ✅ 已配置
YOUTUBE_API_KEY: ✅ 已配置（或"⚠️ 未配置（可选）"）
```

## 📁 生成文件结构

生成的文件保存位置：

```
📁 项目根目录
├── assets/audio/                    # 播客音频文件
│   └── youtube-YYYYMMDD-视频ID.mp3
├── assets/images/posts/YYYY/MM/     # 视频缩略图
│   └── youtube-YYYYMMDD-视频ID-thumbnail.jpg
└── _drafts/                         # 生成的Jekyll文章
    └── YYYY-MM-DD-youtube-learning-视频ID.md
```

## 📋 生成文章格式

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
  <source src="{{ site.baseurl }}/assets/audio/podcast.mp3" type="audio/mpeg">
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

## 🚨 故障排除

### 常见问题及解决方案

**1. 依赖安装错误**
```bash
ImportError: No module named 'gradio_client'
```
**解决**: `pip install -r requirements.txt`

**2. API密钥配置错误**
```
❌ 需要GEMINI_API_KEY配置
```
**解决**: 在`.env`文件中正确设置`GEMINI_API_KEY`

**3. YouTube链接格式错误**
```
❌ 请输入有效的YouTube链接
```
**解决**: 确保链接格式正确，支持：
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`

**4. 网络连接问题**
```
❌ Podcastfy 客户端连接失败，将使用备用播客生成方法
```
**解决**: 检查网络连接，系统会自动使用本地TTS生成音频

**5. YouTube API相关错误**

**"API key not valid" 错误**
- 检查API密钥是否正确复制  
- 确认YouTube Data API v3已启用
- 检查API密钥限制设置

**"Quota exceeded" 错误**
- 当日API调用已达上限
- 等待第二天重置或考虑付费升级

**"Access denied" 错误**
- 检查API密钥的应用限制设置
- 确保服务器IP地址被允许访问

## 🔧 技术架构

### 核心组件
1. **YouTubePodcastGenerator**: 主要处理类
2. **Podcastfy API**: 托管播客生成服务
3. **本地TTS备用**: eSpeak/gTTS/ElevenLabs
4. **Gemini API**: 内容分析和中文导读生成
5. **YouTube Data API**: 视频信息获取（可选）

### 处理流程
```
YouTube链接 → 视频信息提取 → 播客生成 → 导读生成 → Jekyll文章创建
```

## 📊 使用限制和建议

### 系统限制
- **视频时长**: 建议60分钟以内
- **语言**: 最佳效果为英文视频
- **网络**: 需要稳定的国际网络连接
- **API配额**: Gemini API有每日调用限制

### 最佳实践
1. **视频选择**: 选择高质量的英文教育或商业内容
2. **标题优化**: 使用自定义标题功能提高吸引力
3. **后期编辑**: 生成后可手动编辑文章内容
4. **分批处理**: 避免同时处理大量视频
5. **备份重要**: 定期备份生成的音频和文章文件

## 🔄 维护和更新

### 定期维护
```bash
# 更新依赖包
pip install --upgrade -r requirements.txt

# 检查配置状态
python run.py # 选择菜单6 → 2
```

### 配置文件位置
- 主配置：`config/youtube_podcast_config.yml`
- 环境变量：`.env`
- 日志文件：`.build/logs/pipeline.log`

## 💡 技术支持

遇到问题时的排查步骤：
1. 检查配置状态（菜单6 → 2）
2. 查看系统日志（菜单8 → 3）
3. 参考本文档故障排除部分
4. 检查网络连接和API配额

---

*最后更新：2025-07-30*