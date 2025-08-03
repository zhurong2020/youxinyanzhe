# YouTube音频上传解决方案

## 🚨 问题总结
你遇到的YouTube上传401错误是因为YouTube上传API需要OAuth2用户授权，不能使用简单的API Key。

## 🎯 现在有两个解决方案

### 方案一：简化版 - 立即可用 🚀

**只生成视频文件，然后手动上传到YouTube**

#### 使用方法：
```bash
source venv/bin/activate
python youtube_video_gen.py
```

#### 功能特点：
- ✅ **无需OAuth认证** - 避免复杂的授权流程
- ✅ **立即可用** - 直接运行，无需额外配置
- ✅ **自动生成缩略图** - 智能匹配或创建默认缩略图
- ✅ **批量处理** - 一次性为所有音频生成视频
- ✅ **完整信息文件** - 为每个视频生成上传指导

#### 输出结果：
- 📁 视频文件保存在 `youtube_videos/` 目录
- 🎬 每个音频对应一个 `.mp4` 视频文件
- 📝 每个视频对应一个 `.txt` 信息文件（包含建议的标题、描述、标签）

#### 工作流程：
1. 运行工具生成所有视频文件
2. 打开YouTube Studio
3. 批量上传生成的视频文件
4. 使用信息文件中的建议设置标题、描述等

### 方案二：完整版 - OAuth2认证 🔐

**完全自动化上传，需要一次性设置OAuth2**

#### 准备步骤：
1. **安装额外依赖**：
   ```bash
   source venv/bin/activate
   pip install google-auth-oauthlib google-auth-httplib2
   ```

2. **获取OAuth凭据**：
   - 访问 [Google Cloud Console](https://console.cloud.google.com/)
   - 创建项目 > 启用YouTube Data API v3
   - 创建 OAuth client ID (Desktop application)
   - 下载JSON文件重命名为 `youtube_oauth_credentials.json`
   - 放入 `config/` 目录

3. **运行完整版工具**：
   ```bash
   python youtube_upload.py
   ```

#### 首次运行：
- 会自动打开浏览器完成Google授权
- 授权后会保存token供后续使用
- 支持完全自动化上传

## 🎯 立即开始 - 推荐简化版

由于你想立即开始使用，建议先用**方案一（简化版）**：

### 第1步：运行简化版工具
```bash
source venv/bin/activate
python youtube_video_gen.py
```

### 第2步：选择操作
- 选择 `1` - 扫描并显示音频文件
- 选择 `3` - 批量生成所有视频文件

### 第3步：等待生成完成
工具会为你的6个音频文件生成对应的视频：

1. `youtube-20250730-president-trump-tours-the-federal-reserve.mp4`
2. `joe-rogan-elon-musk202501.mp4`
3. `tesla-ai-empire.mp4` 
4. `tesla-optimus-humanoid-robot.mp4`
5. `tesla-robotaxi-expansion.mp4`
6. `tesla-unboxed-manufacturing-podcast.mp4`

### 第4步：手动上传到YouTube
1. 打开 [YouTube Studio](https://studio.youtube.com/)
2. 点击"创建" > "上传视频"
3. 批量选择 `youtube_videos/` 目录中的所有 `.mp4` 文件
4. 使用对应的 `.txt` 文件中的建议信息设置标题、描述、标签

## 💡 两个方案对比

| 特性 | 简化版 | 完整版 |
|-----|-------|-------|
| 设置复杂度 | ✅ 零配置 | ⚠️ 需要OAuth设置 |
| 立即可用 | ✅ 是 | ❌ 需要授权 |
| 自动上传 | ❌ 需手动 | ✅ 全自动 |
| 视频生成 | ✅ 支持 | ✅ 支持 |
| 批量处理 | ✅ 支持 | ✅ 支持 |

## 🚀 开始使用

现在你可以立即运行：

```bash
source venv/bin/activate
python youtube_video_gen.py
```

选择选项 `3` 进行批量生成，几分钟后就能获得所有视频文件！