# OneDrive图片管理工作流程

本文档详细说明博客图片从创作到发布的完整自动化工作流程。

## ⚠️ 重要更新 (2025-08-14)

### 企业账户适配优化
- ✅ **企业账户兼容性** - 优化为企业Microsoft 365账户的view+anonymous分享模式
- ✅ **避免embed模式** - 企业账户不支持embed+anonymous，使用view+anonymous替代
- ✅ **配置自动检测** - 系统自动检测账户类型并选择最佳分享方式

### 新增功能 (2025-08-11)
- ✅ **修复图片渲染问题** - OneDrive链接现在生成可直接嵌入Jekyll的图片URL
- ✅ **增加回退机制** - 处理失败时自动恢复到原始状态  
- ✅ **集成GitHub备份** - 完整的文章和图片资源备份到GitHub Release
- ✅ **链接验证功能** - 自动测试图片链接可访问性

### 新增工具
- `enhanced_onedrive_processor.py` - 增强处理器(包含回退+备份)
- `restore_local_image_links.py` - OneDrive链接恢复为本地链接
- `cleanup_onedrive_images.py` - 安全清理OneDrive文件和记录

## 工作流程概览

### 完整流程图
```
内容创作 → 图片准备 → 本地引用 → OneDrive处理 → 文章发布
    ↓         ↓         ↓          ↓          ↓
 草稿文件   assets图片   MD引用    云端托管    _posts发布
```

## 详细工作流程

### 1. 内容创作阶段
**目标**: 创建带有本地图片引用的草稿文章

**操作步骤**:
```bash
# 创建草稿文件
_drafts/YYYY-MM-DD-文章标题.md
```

**文件结构示例**:
```markdown
---
title: "文章标题"
date: "YYYY-MM-DD"
categories: ["cognitive-upgrade"]
---

文章内容...

![图片描述](assets/images/posts/2025/08/screenshot.png)
```

### 2. 图片准备阶段
**目标**: 收集和整理文章相关图片

**目录结构**:
```
assets/images/posts/
└── YYYY/
    └── MM/
        ├── image1.png
        ├── image2.jpg
        └── screenshot.png
```

**支持格式**: `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, `.svg`

### 3. 本地引用阶段
**目标**: 在草稿中正确引用本地图片

**引用格式支持**:
- `assets/images/posts/2025/08/image.png` (相对于项目根目录)
- `./images/screenshot.png` (相对于文章目录)
- `{{ site.baseurl }}/assets/images/posts/2025/08/image.png` (Jekyll变量)

### 4. OneDrive处理阶段 ⭐
**目标**: 自动化图片上传、链接替换、本地清理

#### 4.1 启动处理
```bash
# 方式1: 通过run.py菜单
python run.py
# 选择: 14. OneDrive图床管理 → 1. 处理单个草稿文件

# 方式2: 直接命令行
python scripts/tools/onedrive_blog_images.py --draft _drafts/文章名.md
```

#### 4.2 自动化处理流程
1. **OAuth认证验证**
   - 检查OneDrive访问令牌有效性
   - 如需要，自动刷新令牌
   - WSL环境优化: 使用PowerShell启动浏览器

2. **图片扫描和解析**
   - 扫描草稿文件中的图片引用
   - 解析各种格式的本地路径
   - 验证图片文件实际存在

3. **文件哈希计算**
   - 计算每个图片的MD5哈希值
   - 检查重复文件，避免重复上传
   - 如发现重复，直接返回已存在的OneDrive链接

4. **OneDrive上传**
   - 创建目标文件夹: `/BlogImages/{year}/{month}/`
   - 上传文件，命名格式: `{date}_{article_title}_{index:02d}.{ext}`
   - 获取OneDrive分享链接和嵌入链接

5. **索引记录更新**
   - 保存图片记录到`_data/onedrive_image_index.json`
   - 记录完整元数据: 路径、链接、文件信息、文章关联等

6. **文章链接替换**
   - 将本地图片路径替换为OneDrive嵌入链接
   - 更新草稿文件内容

7. **本地文件清理** (可配置)
   - 删除assets目录中已成功上传的图片文件
   - 自动清理空目录

#### 4.3 处理示例
**处理前**:
```markdown
![截图](assets/images/posts/2025/08/screenshot.png)
```

**处理后**:
```markdown
![截图](https://7fp1fj-my.sharepoint.com/:i:/g/personal/zhurong_7fp1fj_onmicrosoft_com/EQbmqgcFdMxOjQeFxdHciEMB...)
```

**OneDrive结构**:
```
/BlogImages/
└── 2025/
    └── 08/
        └── 20250811_文章标题_01.png
```

**索引记录**:
```json
{
  "文章名_01_abc12345": {
    "local_path": "assets/images/posts/2025/08/screenshot.png",
    "onedrive_path": "/BlogImages/2025/08/20250811_文章标题_01.png",
    "onedrive_url": "https://...",
    "embed_url": "https://...",
    "article_file": "_drafts/2025-08-11-文章标题.md",
    "article_title": "文章标题",
    "file_hash": "abc123...",
    "upload_date": "2025-08-11T10:30:00"
  }
}
```

### 5. 文章发布阶段
**目标**: 将处理完成的文章移动到发布目录

**操作**:
```bash
# 手动移动文件
mv _drafts/YYYY-MM-DD-标题.md _posts/

# Jekyll自动构建发布
# 所有OneDrive链接在生产环境正常显示
```

## 增强工具使用指南

### 1. 增强处理器 (推荐)
```bash
# 带回退和GitHub备份的完整处理
python3 scripts/tools/enhanced_onedrive_processor.py "_drafts/文章.md" --with-github-backup

# 从快照回退
python3 scripts/tools/enhanced_onedrive_processor.py --rollback "snapshot_id"
```

**特性**:
- ✅ 自动创建处理前快照
- ✅ 失败时自动回退
- ✅ 图片链接验证
- ✅ GitHub Release备份
- ✅ 自动生成恢复脚本

### 2. 链接恢复工具
```bash
# 将OneDrive链接恢复为本地Jekyll链接
python3 scripts/tools/restore_local_image_links.py "_drafts/文章.md"

# 演练模式
python3 scripts/tools/restore_local_image_links.py "_drafts/文章.md" --dry-run
```

### 3. 安全清理工具
```bash
# 交互式清理OneDrive文件和记录
python3 scripts/tools/cleanup_onedrive_images.py --article "_drafts/文章.md"

# 清理所有记录
python3 scripts/tools/cleanup_onedrive_images.py
```

## 图片索引管理系统

### 索引查询功能
```bash
# 查看统计信息
python scripts/tools/onedrive_image_index.py --stats

# 生成详细报告
python scripts/tools/onedrive_image_index.py --report

# 查看文章相关图片
python scripts/tools/onedrive_image_index.py --article _drafts/文章名.md

# 查看日期范围内图片
python scripts/tools/onedrive_image_index.py --date-range 2025-08-01 2025-08-31

# 清理无效记录
python scripts/tools/onedrive_image_index.py --cleanup
```

### run.py集成菜单
```
14. OneDrive图床管理
    1. 处理单个草稿文件
    2. 批量处理草稿目录  
    3. 设置OneDrive认证
    4. 测试OneDrive连接
    5. 查看配置信息
    6. 图片索引管理 ← 新增功能
        1. 查看图片统计
        2. 生成详细报告
        3. 按文章查询图片
        4. 清理无效记录
        5. 显示帮助信息
```

## OneDrive账户类型说明

### 企业账户 vs 个人账户

**企业Microsoft 365账户** (当前使用):
- ✅ 支持 `view+anonymous` 分享模式
- ❌ **不支持** `embed+anonymous` 分享模式 
- ✅ 企业级管理和安全控制
- ✅ 更大存储空间
- 🔗 分享链接格式: `https://xxx.sharepoint.com/:i:/g/personal/...`

**个人OneDrive账户**:
- ✅ 支持 `view+anonymous` 分享模式
- ✅ 支持 `embed+anonymous` 分享模式
- 🔗 分享链接格式: `https://onedrive.live.com/...`

### 配置建议

**企业账户配置** (推荐):
```json
{
  "links": {
    "type": "view",
    "scope": "anonymous",
    "width": 800
  }
}
```

**个人账户配置**:
```json
{
  "links": {
    "type": "embed",
    "scope": "anonymous", 
    "width": 800
  }
}
```

## 配置管理

### 核心配置文件: `config/onedrive_config.json`
```json
{
  "auth": {
    "tenant_id": "YOUR_TENANT_ID",
    "client_id": "YOUR_CLIENT_ID", 
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uri": "http://localhost:8080/callback",
    "scopes": ["Files.ReadWrite", "offline_access"]
  },
  "onedrive": {
    "base_folder": "/BlogImages",
    "folder_structure": "{year}/{month:02d}",
    "filename_format": "{date}_{article_title}_{index:02d}.{ext}"
  },
  "processing": {
    "max_file_size_mb": 32,
    "delete_local_after_upload": true,
    "backup_before_delete": false
  },
  "links": {
    "type": "view",
    "scope": "anonymous",
    "width": 800,
    "height": null,
    "quality": "auto"
  }
}
```

### 环境变量配置: `.env`
```bash
# OneDrive认证信息 (敏感数据)
ONEDRIVE_TENANT_ID=actual_tenant_id
ONEDRIVE_CLIENT_ID=actual_client_id
ONEDRIVE_CLIENT_SECRET=actual_client_secret
ONEDRIVE_REDIRECT_URI=http://localhost:8080/callback
```

## 故障排除

### 常见问题和解决方案

#### 1. OAuth认证失败
**症状**: 浏览器显示"missing scope parameter"
**解决**: 
- 检查Azure应用权限配置
- 确认环境变量正确设置
- WSL环境使用PowerShell启动浏览器

#### 2. 路径解析失败
**症状**: 日志显示"Could not resolve local path"
**解决**:
- 检查图片文件是否实际存在
- 确认路径格式正确
- 支持的格式: 相对路径、Jekyll变量、绝对路径

#### 3. 上传失败
**症状**: 上传过程中报错
**解决**:
- 检查文件大小限制 (默认32MB)
- 验证OneDrive存储空间
- 确认网络连接稳定

#### 4. 索引记录不一致
**症状**: 索引显示的图片与实际不符
**解决**:
```bash
# 清理无效记录
python scripts/tools/onedrive_image_index.py --cleanup
```

#### 5. 图片链接403错误
**症状**: OneDrive图片链接返回"403 Forbidden"错误
**原因**: 企业账户不支持embed+anonymous模式
**解决**:
1. 检查配置文件中的links.type设置
2. 企业账户使用`"type": "view"`
3. 个人账户可使用`"type": "embed"`
```json
{
  "links": {
    "type": "view",       // 企业账户必须使用view
    "scope": "anonymous"  // 匿名访问
  }
}
```

## 最佳实践

### 1. 文件命名规范
- 图片文件使用英文名称，避免特殊字符
- 采用描述性命名: `wechat-interface.png`, `data-analysis-chart.jpg`

### 2. 文件大小控制
- 单个图片文件不超过32MB
- 建议压缩大图片以提高上传速度

### 3. 批量处理建议
- 对于多篇文章，可以使用批量处理功能
- 建议在网络稳定时进行批量操作

### 4. 备份策略
- 重要图片建议保留本地备份
- 可配置`backup_before_delete: true`保留原文件

---

**文档版本**: v1.0  
**创建日期**: 2025-08-11  
**维护**: 与OneDrive系统功能变更同步更新