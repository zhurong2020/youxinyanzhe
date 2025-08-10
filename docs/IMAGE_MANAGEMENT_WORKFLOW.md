# 智能图片管理工作流

## 概述

基于文件大小和用途的智能图片管理系统，自动选择最优存储策略，平衡GitHub空间使用和访问体验。

## 存储策略

### 分类规则

| 大小范围 | 存储位置 | 处理方式 | 适用场景 |
|---------|---------|----------|----------|
| < 50KB | 本地assets | 直接存储 | 图标、小截图 |
| 50KB-200KB | 本地assets | 压缩优化 | 普通截图 |
| 200KB-1MB | 外部CDN | 原图上传 | 高质量图片 |
| > 1MB | 外部CDN | 原图+缩略图 | 大图、动图 |

### 存储路径规范

```
本地存储：
assets/images/posts/YYYY/MM/filename.ext

CDN存储：
https://cdn-provider.com/xxxxx

配置文件：
config/image_config.json
```

## 使用方法

### 1. 环境准备

```bash
# 安装依赖
pip install Pillow requests

# 可选：Cloudinary支持
pip install cloudinary

# 配置CDN API密钥（以ImgBB为例）
# 编辑 config/image_config.json，填入api_key
```

### 2. 基本使用

```bash
# 分析图片（不处理）
python scripts/tools/image_manager.py --analyze-only --image-dir /path/to/images --article-date 2025/08

# 处理图片
python scripts/tools/image_manager.py --image-dir /path/to/images --article-date 2025/08
```

### 3. 写作工作流集成

#### 步骤1: 准备图片
```bash
# 创建文章图片目录
mkdir temp_images_20250808

# 将截图/素材放入目录
# 支持: .png, .jpg, .jpeg, .gif, .webp
```

#### 步骤2: 分析与处理
```bash
# 先分析，了解处理策略
python scripts/tools/image_manager.py --analyze-only --image-dir temp_images_20250808 --article-date 2025/08

# 确认无误后处理
python scripts/tools/image_manager.py --image-dir temp_images_20250808 --article-date 2025/08
```

#### 步骤3: 获取Markdown链接
处理完成后，工具会输出可直接使用的Markdown链接：

```markdown
![图片描述]({{ site.baseurl }}/assets/images/posts/2025/08/small_image.webp)
![大图片](https://i.ibb.co/xxxxx/large_image.png)
```

## 配置选项

### image_config.json详解

```json
{
  "local_path": "assets/images/posts/",       // 本地存储基础路径
  "cdn_config": {
    "provider": "imgbb",                      // CDN提供商: imgbb/cloudinary
    "api_key": "your_api_key_here",          // API密钥
    "base_url": ""                           // 自定义CDN域名
  },
  "compression": {
    "jpeg_quality": 85,                      // JPEG压缩质量 (1-100)
    "webp_quality": 80,                      // WebP压缩质量 (1-100) 
    "png_optimize": true                     // PNG优化开关
  },
  "max_width": 1200,                         // 最大宽度限制
  "thumbnail_width": 400                     // 缩略图宽度
}
```

## 高级功能

### 1. 批量迁移现有图片

```bash
# 分析现有assets目录
find assets/images -name "*.png" -o -name "*.jpg" | while read file; do
  size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file")
  if [ $size -gt 204800 ]; then  # >200KB
    echo "Large file: $file ($((size/1024))KB) - 建议迁移到CDN"
  fi
done
```

### 2. 自动化集成到run.py

在`run.py`中添加图片处理步骤：

```python
def process_article_images(article_path: str):
    """处理文章图片"""
    import subprocess
    
    # 检查是否有待处理图片目录
    temp_dir = f"temp_images_{datetime.now().strftime('%Y%m%d')}"
    if os.path.exists(temp_dir):
        article_date = datetime.now().strftime('%Y/%m')
        
        # 调用图片管理工具
        result = subprocess.run([
            'python', 'scripts/tools/image_manager.py',
            '--image-dir', temp_dir,
            '--article-date', article_date
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 图片处理完成")
            print(result.stdout)
        else:
            print("❌ 图片处理失败")
            print(result.stderr)
```

### 3. Jekyll插件集成

创建Jekyll插件自动优化图片：

```ruby
# _plugins/image_optimizer.rb
Jekyll::Hooks.register :posts, :pre_render do |post|
  # 检查图片链接，必要时提示优化
  content = post.content
  large_images = content.scan(/!\[.*?\]\((.*?)\)/).flatten
  
  large_images.each do |img_url|
    if img_url.include?('assets/images') && !img_url.include?('compressed')
      # 检查文件大小，给出建议
    end
  end
end
```

## 最佳实践

### 1. 文章写作时

1. **截图阶段**：直接保存为PNG，不要手动压缩
2. **收集阶段**：将所有图片放入临时目录
3. **处理阶段**：运行图片管理工具一次性处理
4. **写作阶段**：复制粘贴生成的Markdown链接

### 2. 存储策略选择

- **图表/流程图**：通常<100KB，适合本地存储
- **截图**：100KB-500KB，压缩后本地存储
- **摄影作品**：>500KB，CDN存储
- **GIF动图**：通常>1MB，必须CDN存储

### 3. 性能考虑

- **本地图片**：首次访问慢，但CDN加速后很快
- **CDN图片**：全球访问快，但依赖第三方服务
- **混合策略**：核心内容本地，辅助内容CDN

## 监控与维护

### 1. 空间使用监控

```bash
# 检查assets目录大小
du -sh assets/images/

# 统计各类型文件数量
find assets/images -name "*.webp" | wc -l
find assets/images -name "*.png" | wc -l
```

### 2. CDN使用情况

- ImgBB：访问dashboard查看使用量
- Cloudinary：查看monthly usage报告
- 建议设置用量告警

### 3. 定期清理

```bash
# 查找可能的冗余文件
find assets/images -name "*_compressed*" -size +200k

# 查找超大本地图片（可能需要迁移）
find assets/images -size +500k -type f
```

## 故障排除

### 常见问题

1. **上传CDN失败**
   - 检查API密钥配置
   - 确认网络连接
   - 查看CDN服务状态

2. **图片压缩失败**
   - 检查PIL库安装
   - 确认图片格式支持
   - 查看磁盘空间

3. **Jekyll构建失败**
   - 检查图片路径格式
   - 确认baseurl配置
   - 验证Markdown语法

### 日志记录

工具会自动记录处理日志，位于：
- `logs/image_processing.log`
- 包含处理时间、文件大小、存储策略等信息

## 扩展功能

### 计划中的功能
- [ ] 自动图片格式转换（PNG→WebP）
- [ ] 图片水印添加
- [ ] 智能裁剪和缩放
- [ ] 图片内容识别（OCR）
- [ ] 多CDN负载均衡
- [ ] 图片访问统计分析

这套工作流能帮你实现：
- ✅ 自动选择最优存储策略
- ✅ 减少GitHub仓库空间占用
- ✅ 保持图片访问速度
- ✅ 简化日常写作流程