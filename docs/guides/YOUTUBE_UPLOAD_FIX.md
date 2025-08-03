# YouTube上传认证问题解决方案

## 🚨 问题分析

你遇到的错误：
```
HttpError 401: API keys are not supported by this API. Expected OAuth2 access token
```

**原因**：YouTube的上传API需要OAuth2用户授权，不能使用简单的API Key。

## 🛠️ 解决方案

### 方案一：快速设置OAuth2认证（推荐）

#### 1. 安装额外依赖
```bash
source venv/bin/activate
pip install google-auth-oauthlib google-auth-httplib2
```

#### 2. 创建Google Cloud OAuth凭据
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 选择你的项目或创建新项目
3. 启用 YouTube Data API v3
4. 转到 "APIs & Services" > "Credentials" 
5. 点击 "Create Credentials" > "OAuth client ID"
6. 选择 "Desktop application"
7. 下载JSON文件

#### 3. 配置凭据文件
```bash
# 运行OAuth设置工具
python scripts/tools/youtube_oauth_setup.py

# 或者手动创建目录和文件
mkdir -p config
# 将下载的JSON文件重命名并移动到：
# config/youtube_oauth_credentials.json
```

#### 4. 运行工具进行首次认证
```bash
python youtube_upload.py
```
首次运行时会自动打开浏览器完成授权。

### 方案二：临时解决方案 - 本地视频生成

如果暂时不想设置OAuth2，可以只生成视频文件：

#### 修改工具为"仅生成视频"模式
```bash
# 运行工具
python youtube_upload.py

# 选择选项 2，会生成视频但不上传
# 视频文件保存在 .tmp/youtube_uploads/ 目录
```

然后你可以手动上传这些视频到YouTube。

### 方案三：使用YouTube Studio上传

我可以为你创建一个脚本，自动生成所有视频文件，然后你手动批量上传：

```bash
# 运行批量视频生成（不上传）
python scripts/tools/youtube_batch_video_generator.py
```

## 🚀 推荐流程（最简单）

### 步骤1：安装依赖
```bash
source venv/bin/activate
pip install google-auth-oauthlib google-auth-httplib2
```

### 步骤2：快速OAuth设置
我已经更新了工具，运行以下命令获取设置指导：
```bash
python scripts/tools/youtube_oauth_setup.py
```

### 步骤3：获取OAuth凭据
1. 打开 https://console.cloud.google.com/
2. 选择项目 > APIs & Services > Credentials
3. Create Credentials > OAuth client ID > Desktop application
4. 下载JSON文件，重命名为 `youtube_oauth_credentials.json`
5. 放入 `config/` 目录

### 步骤4：测试上传
```bash
python youtube_upload.py
```
首次运行会打开浏览器完成授权。

## 🔧 如果遇到问题

### 问题1：浏览器授权失败
**解决**：检查防火墙设置，确保能访问 Google 服务

### 问题2：OAuth凭据错误
**解决**：重新下载凭据文件，确保文件名和路径正确

### 问题3：权限不足
**解决**：确保Google Cloud项目中启用了YouTube Data API v3

## 📝 当前状态检查

运行以下命令检查当前配置：
```bash
python youtube_upload.py
# 选择选项 4 - 检查配置状态
```

## 🎯 简化版本（立即可用）

如果你想立即测试，我可以创建一个简化版本，只生成视频文件：