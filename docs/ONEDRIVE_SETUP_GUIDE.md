# OneDrive博客图床设置指南

## 📋 前期准备

### 1. Azure应用注册

1. **访问Azure Portal**
   - 打开 [https://portal.azure.com/](https://portal.azure.com/)
   - 使用开发者账号 `zhurong@7fp1fj.onmicrosoft.com` 登录

2. **注册新应用**
   ```
   路径: Azure Active Directory → 应用注册 → 新注册
   
   配置:
   - 名称: BlogImageManager
   - 支持的帐户类型: 仅此组织目录中的帐户
   - 重定向 URI: Web - http://localhost:8080/callback
   ```

3. **配置API权限**
   ```
   路径: 应用 → API权限 → 添加权限
   
   添加权限:
   - Microsoft Graph → 委托的权限 → Files.ReadWrite
   - Microsoft Graph → 委托的权限 → Sites.ReadWrite.All
   ```

4. **创建客户端密码**
   ```
   路径: 应用 → 证书和密码 → 新建客户端密码
   
   设置:
   - 说明: BlogImageManager Secret
   - 过期时间: 24个月
   
   ⚠️ 重要: 立即复制密码值，稍后无法查看！
   ```

5. **获取应用信息**
   ```
   需要记录的信息:
   - 应用程序(客户端) ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   - 客户端密码: 刚才创建的密码值
   - 目录(租户) ID: 7fp1fj.onmicrosoft.com
   ```

### 2. 配置系统

1. **更新配置文件**
   ```bash
   编辑 config/onedrive_config.json
   
   填入获得的信息:
   {
     "auth": {
       "tenant_id": "7fp1fj.onmicrosoft.com",
       "client_id": "你的客户端ID",
       "client_secret": "你的客户端密码",
       "redirect_uri": "http://localhost:8080/callback",
       ...
     }
   }
   ```

2. **安装Python依赖**
   ```bash
   pip install requests
   ```

## 🚀 初始化设置

### 方法1: 通过run.py（推荐）
```bash
python run.py
# 选择: 14. OneDrive图床管理
# 选择: 1. 初始化OneDrive认证
```

### 方法2: 直接运行脚本
```bash
python scripts/tools/onedrive_blog_images.py --setup
```

### 方法3: 快速脚本
```bash
bash scripts/quick_onedrive_images.sh --setup
```

## 🔐 认证流程

1. **启动认证**
   - 系统会自动打开浏览器
   - 访问Microsoft登录页面

2. **登录授权**
   - 使用开发者账号登录: `zhurong@7fp1fj.onmicrosoft.com`
   - 同意应用权限请求

3. **完成认证**
   - 浏览器显示 "Authorization Successful!"
   - 系统自动获取并保存访问令牌
   - 认证信息存储在 `config/onedrive_tokens.json`

4. **验证连接**
   - 系统会测试OneDrive连接
   - 显示存储空间使用情况

## 📝 使用方法

### 博客写作工作流

1. **写作阶段**
   ```markdown
   在Markdown中正常插入本地图片:
   ![图片描述]({{ site.baseurl }}/assets/images/posts/2025/08/image1.png)
   ![另一张图](./local/path/image2.jpg)
   ```

2. **图片处理**
   ```bash
   # 方法1: 通过run.py
   python run.py → 14. OneDrive图床管理 → 2. 处理单个草稿的图片
   
   # 方法2: 直接处理
   python scripts/tools/onedrive_blog_images.py --draft _drafts/my-article.md
   
   # 方法3: 快速脚本
   bash scripts/quick_onedrive_images.sh -d _drafts/my-article.md
   ```

3. **批量处理**
   ```bash
   # 处理所有草稿
   python scripts/tools/onedrive_blog_images.py --batch _drafts
   
   # 或通过run.py → 14 → 3
   ```

### 处理结果

系统会自动:
1. 检测Markdown中的本地图片链接
2. 上传图片到OneDrive的 `/BlogImages/YYYY/MM/` 结构
3. 获取图片的嵌入式分享链接
4. 替换原文中的本地链接

**替换示例**:
```markdown
# 处理前
![截图]({{ site.baseurl }}/assets/images/posts/2025/08/screenshot.png)

# 处理后  
![截图](https://onedrive.live.com/embed?resid=xxx&authkey=xxx&width=800)
```

## 📁 OneDrive目录结构

```
/BlogImages/
├── 2025/
│   ├── 08/
│   │   ├── 20250808_信息核实方法论_01.png
│   │   ├── 20250808_信息核实方法论_02.webp
│   │   └── 20250808_AI医疗_01.jpg
│   └── 09/
└── metadata/
    └── upload_log.json
```

## 🔧 高级功能

### 1. 连接状态检查
```bash
# 通过run.py → 14 → 4
# 显示:
# - OneDrive连接状态
# - 存储空间使用情况
# - 可用空间统计
```

### 2. 处理统计查看
```bash
# 通过run.py → 14 → 5
# 显示:
# - 成功上传的图片数量
# - 失败处理的图片数量
# - 最近的处理日志
```

### 3. 自定义配置
```json
// config/onedrive_config.json
{
  "onedrive": {
    "base_folder": "/BlogImages",           // 基础文件夹
    "folder_structure": "{year}/{month:02d}", // 目录结构
    "filename_format": "{date}_{article_title}_{index:02d}.{ext}" // 文件名格式
  },
  "processing": {
    "max_file_size_mb": 32,                // 最大文件大小
    "compress_large_images": true,         // 是否压缩大图片
    "compression_quality": 85              // 压缩质量
  },
  "links": {
    "type": "embed",                       // 链接类型
    "width": 800,                         // 嵌入宽度
    "height": null                        // 嵌入高度 (自动)
  }
}
```

## ❗ 故障排除

### 常见问题

1. **认证失败**
   ```
   错误: Token exchange failed
   解决: 检查Azure应用配置，确认重定向URI正确
   ```

2. **上传失败**
   ```
   错误: Upload failed: 401 Unauthorized
   解决: 令牌可能过期，重新运行认证
   ```

3. **文件找不到**
   ```
   错误: Could not resolve local path
   解决: 检查图片文件是否存在，路径是否正确
   ```

4. **文件过大**
   ```
   错误: File too large
   解决: 压缩图片或调整max_file_size_mb配置
   ```

### 日志检查
```bash
# 查看详细日志
cat logs/onedrive_blog_images.log

# 实时监控日志
tail -f logs/onedrive_blog_images.log
```

### 令牌管理
```bash
# 令牌文件位置
config/onedrive_tokens.json

# 手动清除令牌 (重新认证)
rm config/onedrive_tokens.json
```

## 💡 最佳实践

### 1. 图片管理
- 使用有意义的图片文件名
- 保持合理的图片大小 (建议<5MB)
- 批量处理前先测试单个文件

### 2. 存储优化
- 定期检查OneDrive使用情况
- 清理不再需要的旧图片
- 利用5TB空间优势

### 3. 工作流优化
- 先完成文章写作，最后处理图片
- 使用批量处理提高效率
- 保留本地备份直到确认上传成功

### 4. 开发活动合规
- 图片上传操作算作Graph API开发活动
- 有助于Microsoft 365 E5 Developer订阅续订
- 保持合理的使用频率

## 🔄 续订贡献

这个图床系统对Microsoft 365开发者订阅续订的贡献:
- ✅ 真实的Graph API开发和使用
- ✅ 持续的OneDrive文件操作
- ✅ 合规的开发目的使用
- ✅ 丰富的API调用记录

每次使用都在为续订加分！🎉