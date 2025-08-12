# OneDrive图床智能管理系统

## 概述

OneDrive图床系统提供完整的图片管理解决方案，支持从图片上传到恢复的全生命周期管理。

## 核心特性

### 🔄 智能路径处理
- **Windows路径支持**: 自动转换Windows绝对路径（`c:\Users\...`）为WSL路径（`/mnt/c/Users/...`）
- **Front Matter处理**: 支持Jekyll头部字段中的图片路径（如`header.teaser`）
- **相对路径智能解析**: 支持相对于文章目录的图片引用

### 🛡️ 智能备份策略
- **外部文件检测**: 自动识别项目外部的图片文件
- **项目内备份**: 外部图片自动备份到`temp/image_processing/`
- **备份索引**: 完整记录原始路径、备份路径、远程路径的映射关系
- **手动删除确认**: 用户决定是否删除原始文件

### 🔗 永久链接生成
- **优先级策略**: 永久embed链接 → 永久分享链接 → 临时下载链接
- **避免过期**: 优先使用不包含临时认证令牌的链接类型
- **跨平台兼容**: 生成的链接在各种设备和浏览器中都能正常显示

## 工具集

### 1. recover_onedrive_images.py - 图片恢复工具

#### 功能
- 从OneDrive索引恢复图片到本地
- 保持原始文件名和目录结构
- 支持选择性或批量恢复

#### 使用方法
```bash
# 列出可恢复的图片
python scripts/tools/recover_onedrive_images.py --list

# 恢复指定文章的图片
python scripts/tools/recover_onedrive_images.py --article "文章标题"

# 恢复所有图片
python scripts/tools/recover_onedrive_images.py --all

# 指定索引文件路径
python scripts/tools/recover_onedrive_images.py --index "custom_index.json" --list
```

#### 恢复目标目录
- **项目外图片**: 恢复到`temp/recovered_images/desktop/`
- **项目内图片**: 恢复到原始相对路径

### 2. manage_uploaded_images.py - 已上传图片管理

#### 功能
- 管理已上传图片的本地备份
- 存储空间统计和清理
- 批量删除操作

#### 使用方法
```bash
# 列出已上传的文件
python scripts/tools/manage_uploaded_images.py --list

# 清理所有已上传的文件
python scripts/tools/manage_uploaded_images.py --clean

# 删除指定文件
python scripts/tools/manage_uploaded_images.py --delete file1.png file2.jpg

# 显示存储信息
python scripts/tools/manage_uploaded_images.py --info

# 跳过确认提示
python scripts/tools/manage_uploaded_images.py --clean --yes
```

### 3. cleanup_onedrive_cloud.py - 云端清理工具

#### 功能
- 按日期范围删除OneDrive中的图片文件
- 支持预览和安全删除机制
- 自动更新本地索引记录

#### 使用方法
```bash
# 列出所有云端文件
python scripts/tools/cleanup_onedrive_cloud.py --list

# 预览指定日期范围的文件
python scripts/tools/cleanup_onedrive_cloud.py --preview 7d
python scripts/tools/cleanup_onedrive_cloud.py --preview 2025-08-12

# 删除指定日期范围的文件
python scripts/tools/cleanup_onedrive_cloud.py --delete 24h
python scripts/tools/cleanup_onedrive_cloud.py --delete 2025-08-12:2025-08-15

# 跳过删除确认（危险操作）
python scripts/tools/cleanup_onedrive_cloud.py --delete 1d --yes
```

#### 支持的日期格式
- **相对时间**: `7d` (7天), `24h` (24小时), `30d` (30天)
- **绝对日期**: `2025-08-12` (指定日期当天)
- **日期范围**: `2025-08-12:2025-08-15` (日期范围)

#### 安全特性
- 删除前显示详细文件列表预览
- 二次确认机制防止误删
- 自动更新本地索引保持一致性
- 支持仅预览模式查看待删除文件

### 4. onedrive_blog_images.py - 核心处理器

#### 新增功能
- `_handle_local_file_after_upload()`: 智能处理上传后的本地文件
- `_delete_local_file()`: 安全删除本地文件和空目录
- Front Matter图片检测和处理
- Windows路径自动转换

## 配置说明

### onedrive_config.json 关键配置

```json
{
  "processing": {
    "backup_originals": true,              // 开启原始文件备份
    "delete_local_after_upload": false,    // 关闭自动删除
    "backup_before_delete": true,          // 删除前创建备份
    "manual_delete_confirmation": true,    // 手动删除确认
    "temp_storage_dir": "temp/image_processing"  // 临时存储目录
  }
}
```

## 目录结构

```
temp/
├── image_processing/           # 外部图片备份目录
│   ├── backup_index.json     # 备份索引文件
│   └── *.png, *.jpg          # 备份的图片文件
├── recovered_images/          # 恢复的图片目录
│   ├── desktop/              # 来自桌面的图片
│   └── *.png, *.jpg          # 恢复的图片文件
└── onedrive_snapshots/        # Enhanced processor快照目录
```

## 工作流程

### 标准处理流程
1. **图片检测**: 扫描Markdown内容和Front Matter
2. **路径解析**: Windows路径自动转换为WSL路径
3. **外部文件备份**: 项目外图片备份到临时目录
4. **OneDrive上传**: 生成永久链接
5. **文章更新**: 替换图片链接
6. **用户选择**: 手动确认是否删除原文件

### 恢复流程
1. **索引查询**: 从`_data/onedrive_image_index.json`读取记录
2. **链接转换**: 将分享链接转换为直接下载链接
3. **文件下载**: 从OneDrive下载图片
4. **路径恢复**: 恢复到原始目录结构

## 安全特性

### 隐私保护
- 所有用户图片目录被`.gitignore`排除
- 敏感配置文件不进入版本控制
- 完整的备份恢复机制

### 数据安全
- 多重备份：本地备份 + OneDrive + 索引记录
- 操作确认：重要操作需要用户确认
- 回退机制：支持从各种备份中恢复

## 故障排除

### 常见问题

#### 1. Windows路径无法识别
**症状**: 日志显示"Could not resolve local path"
**解决**: 确保路径格式为`c:\Users\...`，系统会自动转换

#### 2. 图片下载失败
**症状**: 恢复时提示下载失败
**解决**: 检查网络连接和OneDrive权限

#### 3. 备份文件丢失
**症状**: 本地备份文件不存在
**解决**: 使用恢复工具从OneDrive重新下载

### 日志文件
- 主要日志: `logs/onedrive_blog_images.log`
- 查看详细错误信息和处理过程

## 版本历史

### v2.2.0 (2025-08-12)
- ✅ 新增OneDrive云端清理工具
- ✅ 支持按日期范围删除云端文件
- ✅ 集成到主菜单系统
- ✅ 完善安全删除机制

### v2.1.0 (2025-08-12)
- ✅ 新增Windows路径支持
- ✅ 新增Front Matter图片处理
- ✅ 新增智能备份机制
- ✅ 新增图片恢复工具
- ✅ 新增已上传图片管理工具
- ✅ 优化链接持久性

### v2.0.0 (2025-08-11)
- ✅ 基础OneDrive图床功能
- ✅ Enhanced processor快照功能
- ✅ 混合图片管理系统

## 开发指南

### 扩展新功能
1. 在`onedrive_blog_images.py`中添加新的处理逻辑
2. 更新配置文件结构
3. 添加对应的测试用例
4. 更新文档

### 贡献指南
- 遵循现有的代码风格
- 添加充分的错误处理
- 更新相关文档
- 确保隐私和安全性