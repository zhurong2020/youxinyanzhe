# YouTube Data API 密钥获取指南

## 📋 为什么需要YouTube API密钥？

YouTube API密钥是**可选的**，用于获取视频的详细信息：
- ✅ **有API密钥**: 获取精确的视频标题、描述、时长、观看次数等
- ⚠️ **无API密钥**: 使用基础信息提取，功能稍有限制但仍可正常工作

## 🔧 获取步骤

### 1. 创建Google Cloud项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 点击顶部的"选择项目" → "新建项目"
3. 输入项目名称，例如：`youtube-podcast-generator`
4. 点击"创建"

### 2. 启用YouTube Data API v3

1. 在Google Cloud Console中，确保选择了刚创建的项目
2. 搜索"YouTube Data API v3"
3. 点击进入API页面
4. 点击"启用"按钮

### 3. 创建API凭据

1. 在左侧菜单中，点击"凭据"
2. 点击"+ 创建凭据" → "API密钥"
3. 复制生成的API密钥
4. （可选）点击"限制密钥"设置使用限制

### 4. 配置API密钥限制（推荐）

为了安全，建议限制API密钥的使用：

**应用限制**：
- 选择"无"（用于服务器应用）

**API限制**：
- 选择"限制密钥"
- 勾选"YouTube Data API v3"
- 点击"保存"

## 📝 添加到项目配置

将获取的API密钥添加到`.env`文件：

```bash
# YouTube Data API密钥（可选）
YOUTUBE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## 📊 API配额限制

YouTube Data API有以下免费配额：
- **每日配额**: 10,000 units
- **单次视频查询**: 1 unit
- **足够使用**: 每日可查询10,000个视频信息

## 🔍 验证配置

在YouTube播客生成器中选择：
```
run.py → 6. YouTube播客生成器 → 2. 查看配置状态
```

应该显示：
```
YOUTUBE_API_KEY: ✅ 已配置
```

## ⚠️ 注意事项

1. **保密性**: 不要将API密钥提交到公开的Git仓库
2. **配额管理**: 注意API调用次数，避免超出免费配额
3. **可选性**: 即使没有API密钥，播客生成器仍可正常工作
4. **安全性**: 定期轮换API密钥以提高安全性

## 🚨 故障排除

**问题1**: "API key not valid" 错误
- 检查API密钥是否正确复制
- 确认YouTube Data API v3已启用
- 检查API密钥限制设置

**问题2**: "Quota exceeded" 错误
- 当日API调用已达上限
- 等待第二天重置或考虑付费升级

**问题3**: "Access denied" 错误
- 检查API密钥的应用限制设置
- 确保服务器IP地址被允许访问