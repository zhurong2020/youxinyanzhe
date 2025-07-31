# YouTube音频上传工具使用指南

## 🎯 工具概述

这是一个独立的YouTube音频上传测试工具，可以将`assets/audio/`目录下的mp3文件上传到YouTube。

### ✨ 主要功能
- 🔍 自动扫描音频文件
- 🖼️ 智能匹配或生成缩略图
- 🎬 生成视频文件（音频+静态图片）
- 📤 上传到YouTube（不公开链接）
- 🧹 批量处理和清理功能

## 🚀 快速开始

### 1. 运行工具
```bash
# 激活虚拟环境
source venv/bin/activate

# 运行工具（方式一：直接运行）
python youtube_upload.py

# 运行工具（方式二：模块方式）
python scripts/tools/youtube_upload_tester.py
```

### 2. 菜单选项说明
```
🔧 操作选项:
1. 扫描并显示音频文件      # 查看所有可用的音频文件
2. 选择音频文件并上传到YouTube  # 上传单个文件
3. 批量上传所有音频文件    # 一次性上传所有文件
4. 检查配置状态          # 检查环境配置
5. 清理临时文件          # 清理生成的临时视频
0. 退出                # 退出程序
```

## 📁 当前音频文件

根据扫描结果，你的`assets/audio/`目录包含以下音频文件：

1. **youtube-20250730-president-trump-tours-the-federal-reserve.mp3** (3.6MB)
   - 类型：YouTube播客
   - 日期：2025-07-30

2. **joe-rogan-elon-musk202501.mp3** (6.1MB)
   - Joe Rogan与Elon Musk访谈录音

3. **tesla-ai-empire.mp3** (4.5MB)
   - Tesla AI帝国相关播客

4. **tesla-optimus-humanoid-robot.mp3** (8.2MB)
   - Tesla Optimus人形机器人播客

5. **tesla-robotaxi-expansion.mp3** (4.2MB)
   - Tesla Robotaxi扩张播客

6. **tesla-unboxed-manufacturing-podcast.mp3** (4.2MB)
   - Tesla Unboxed制造播客

## 🛠️ 使用步骤

### 单个文件上传
1. 选择菜单选项 `2`
2. 从列表中选择要上传的音频文件
3. 工具会自动：
   - 查找匹配的缩略图（或生成默认缩略图）
   - 生成视频文件（音频+图片）
   - 上传到YouTube
   - 返回YouTube链接

### 批量上传
1. 选择菜单选项 `3`
2. 确认批量上传
3. 工具会依次处理所有音频文件

## 🔧 配置要求

### 必需配置
- ✅ **YOUTUBE_API_KEY**: 已配置并可用
- ✅ **音频目录**: `assets/audio/` 存在且包含6个文件
- ✅ **图片目录**: `assets/images/` 存在

### 可选优化
- **ffmpeg**: 用于高质量视频生成（推荐）
- **moviepy**: 备用视频生成方案
- **PIL/Pillow**: 用于生成默认缩略图

## 📤 上传设置

- **隐私状态**: 不公开（unlisted）- 通过链接可访问
- **分类**: 教育类（Education）
- **语言**: 中文（zh-CN）
- **标签**: 播客、音频、学习、中文

## 🖼️ 缩略图策略

工具会按以下顺序查找缩略图：
1. 匹配的图片文件（如：`tesla-ai-empire-thumbnail.jpg`）
2. 同名图片文件（如：`tesla-ai-empire.jpg`）
3. 默认缩略图文件
4. 自动生成默认缩略图（1280x720，黑底白字）

## 📊 预期结果

每个成功上传的文件将获得：
- YouTube视频ID
- 完整的YouTube链接
- 不公开访问权限（通过链接可访问）

## 🧹 维护功能

### 清理临时文件
- 选择菜单选项 `5`
- 清理 `.tmp/youtube_uploads/` 目录中的临时视频文件

### 检查配置状态
- 选择菜单选项 `4`
- 查看所有配置和依赖状态

## ⚠️ 注意事项

1. **API配额**: YouTube API有每日上传限制，避免短时间内大量上传
2. **视频质量**: 生成的视频为静态图片+音频，适合音频内容
3. **隐私设置**: 默认为不公开，如需公开需手动在YouTube后台修改
4. **临时文件**: 成功上传后会自动清理临时视频文件
5. **错误处理**: 如遇到错误，检查网络连接和API配额

## 🚀 开始使用

现在你可以运行以下命令开始使用：

```bash
source venv/bin/activate
python youtube_upload.py
```

选择选项 `1` 查看所有可用文件，然后选择 `2` 上传单个文件进行测试！