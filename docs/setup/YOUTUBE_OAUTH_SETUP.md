# YouTube OAuth2 设置完整指南

## 🎯 目标
设置YouTube OAuth2认证，实现完全自动化的音频文件上传到YouTube。

## 📋 前提条件
✅ 依赖已安装：`google-auth-oauthlib`, `google-auth-httplib2`  
✅ 模板配置文件已创建：`config/youtube_oauth_credentials.json`

## 🚀 详细设置步骤

### 第1步：创建Google Cloud项目

1. **访问Google Cloud Console**
   - 打开 https://console.cloud.google.com/
   - 登录你的Google账号

2. **创建或选择项目**
   - 点击顶部的项目选择器
   - 选择现有项目或点击"新建项目"
   - 项目名称建议：`youxinyanzhe-youtube-uploader`

### 第2步：启用YouTube Data API v3

1. **进入API库**
   - 在左侧菜单中，点击"APIs & Services" > "Library"
   
2. **搜索并启用API**
   - 搜索"YouTube Data API v3"
   - 点击进入，然后点击"启用"

### 第3步：创建OAuth2凭据

1. **进入凭据页面**
   - 点击"APIs & Services" > "Credentials"

2. **创建OAuth client ID**
   - 点击"+ CREATE CREDENTIALS" > "OAuth client ID"
   
3. **配置OAuth同意屏幕**（如果是首次创建）
   - 选择"External"（外部用户类型）
   - 填写应用名称：`YouXinYanZhe YouTube Uploader`
   - 填写用户支持邮箱：你的邮箱
   - 开发者联系信息：你的邮箱
   - 点击"保存并继续"
   - 在"范围"页面，点击"添加或删除范围"
   - 搜索并添加：`../auth/youtube.upload`
   - 保存并继续
   - 在"测试用户"页面，添加你的Gmail邮箱作为测试用户

4. **创建客户端ID**
   - 应用类型选择：**"Desktop application"**
   - 名称：`YouXinYanZhe Desktop Client`
   - 点击"创建"

5. **下载凭据文件**
   - 创建成功后，会弹出下载对话框
   - 点击"下载JSON"保存文件

### 第4步：配置凭据文件

1. **替换模板文件**
   - 将下载的JSON文件重命名为：`youtube_oauth_credentials.json`
   - 替换项目中的模板文件：`config/youtube_oauth_credentials.json`

2. **验证文件格式**
   文件应该类似这样：
   ```json
   {
     "installed": {
       "client_id": "123456789-abcdefg.apps.googleusercontent.com",
       "project_id": "youxinyanzhe-youtube-uploader",
       "auth_uri": "https://accounts.google.com/o/oauth2/auth",
       "token_uri": "https://oauth2.googleapis.com/token",
       "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
       "client_secret": "GOCSPX-abcdefghijklmnop",
       "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
     }
   }
   ```

### 第5步：首次认证测试

1. **运行YouTube上传工具**
   ```bash
   source venv/bin/activate
   python youtube_upload.py
   ```

2. **自动认证流程**
   - 首次运行会自动打开浏览器
   - 登录你的Google账号
   - 选择项目并授权应用访问YouTube
   - 完成后浏览器会显示成功信息

3. **验证认证成功**
   - 控制台应显示：`✅ YouTube OAuth2认证成功`
   - 会生成：`config/youtube_oauth_token.json`（自动保存的认证token）

## 🧪 测试上传

### 测试单个文件上传
1. 运行工具：`python youtube_upload.py`
2. 选择选项 `2` - 选择音频文件并上传到YouTube
3. 选择任意一个音频文件进行测试
4. 等待视频生成和上传完成
5. 获得YouTube链接

### 测试批量上传
1. 选择选项 `3` - 批量上传所有音频文件
2. 确认批量操作
3. 等待所有6个文件处理完成

## ✅ 成功标志

认证成功后，你应该看到：
- `✅ YouTube OAuth2认证成功`
- `✅ 视频生成成功`
- `✅ YouTube上传成功`
- `视频ID: abc123xyz`
- `链接: https://www.youtube.com/watch?v=abc123xyz`

## 🔐 安全注意事项

1. **保护凭据文件**
   - `config/youtube_oauth_credentials.json` 包含敏感信息
   - `config/youtube_oauth_token.json` 包含访问token
   - 这些文件已在 `.gitignore` 中，不会提交到Git

2. **定期检查权限**
   - 在 https://myaccount.google.com/permissions 查看已授权的应用
   - 如有需要可以撤销权限

## ❓ 常见问题

### Q: 浏览器授权失败
**A**: 检查网络连接，确保能访问Google服务

### Q: 显示"OAuth凭据文件不存在"
**A**: 确认文件路径：`config/youtube_oauth_credentials.json`

### Q: 上传失败 403 权限错误
**A**: 检查OAuth同意屏幕是否正确配置，确保添加了测试用户

### Q: Token过期
**A**: 工具会自动刷新token，如果失败会重新启动OAuth流程

## 🎯 下一步

设置完成后，你就可以：
1. 使用 `python youtube_upload.py` 进行自动化上传
2. 批量处理所有音频文件
3. 享受完全自动化的YouTube发布流程

---

**💡 提示**: 首次设置可能需要5-10分钟，但设置完成后就能长期自动化使用！