"""
内容打包创建器
用于自动生成PDF和资料包ZIP文件，支持微信公众号内容变现系统
"""

import os
import re
import zipfile
import tempfile
import requests
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import json
import frontmatter
from urllib.parse import urlparse
import markdown2
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


class PackageCreator:
    """内容包创建器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 项目路径
        self.project_root = Path(__file__).parent.parent
        self.output_dir = self.project_root / "_output/packages"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 资料清单模板
        self.resource_list_template = """# 📦 资料包清单

## 📄 文章信息
- **标题**: {title}
- **发布日期**: {date}
- **生成时间**: {generated_at}

## 📁 包含文件

### 1. 完整文章PDF
- `{article_filename}.pdf` - 高质量PDF版本，适合保存和打印

### 2. 高清图片资源
{image_list}

### 3. 参考资料
- `资料清单.md` - 本文件，包含所有资源链接
- `链接汇总.txt` - 文章中提到的所有外部链接

## 🔗 在线资源链接

### 官方信息来源
{official_links}

### 扩展阅读
{additional_links}

## 💡 使用说明

1. **PDF阅读**: 推荐使用Adobe Reader或其他PDF阅读器
2. **图片查看**: 所有图片均为高清版本，可直接使用
3. **链接访问**: 部分链接可能需要科学上网工具
4. **更新获取**: 关注微信公众号"有心言者"获取最新内容

## 📞 联系方式

- **微信公众号**: 有心言者
- **博客**: https://zhurong2020.github.io
- **邮箱**: 通过公众号联系

---

感谢您的支持！如果觉得有价值，欢迎分享给更多朋友。

*此资料包由自动化系统生成，如有问题请通过微信公众号反馈。*
"""
    
    def create_package(self, article_path: str, include_images: bool = True, 
                      include_links: bool = True) -> Tuple[bool, Dict]:
        """
        创建完整的内容包
        
        Args:
            article_path: 文章文件路径
            include_images: 是否包含图片
            include_links: 是否包含链接汇总
            
        Returns:
            (success, result_info)
        """
        try:
            article_file = Path(article_path)
            if not article_file.exists():
                return False, {"error": f"文章文件不存在: {article_path}"}
            
            # 解析文章
            with open(article_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            article_title = post.metadata.get('title', article_file.stem)
            article_date = str(post.metadata.get('date', ''))
            
            self.logger.info(f"开始创建内容包: {article_title}")
            
            # 创建临时工作目录
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # 1. 生成PDF
                pdf_success, pdf_path = self._create_pdf(post, temp_path, article_title)
                if not pdf_success:
                    return False, {"error": "PDF生成失败"}
                
                # 2. 收集图片
                images_info = []
                if include_images:
                    images_info = self._collect_images(post.content, temp_path)
                
                # 3. 提取链接
                links_info = []
                if include_links:
                    links_info = self._extract_links(post.content)
                    self._create_links_file(links_info, temp_path)
                
                # 4. 生成资料清单
                self._create_resource_list(
                    article_title, article_date, images_info, links_info, temp_path
                )
                
                # 5. 创建ZIP文件
                package_success, package_path = self._create_zip_package(
                    temp_path, article_title, article_date
                )
                
                if package_success:
                    result = {
                        "package_path": str(package_path),
                        "title": article_title,
                        "date": article_date,
                        "files": {
                            "pdf": f"{self._safe_filename(article_title)}.pdf",
                            "images_count": len(images_info),
                            "links_count": len(links_info)
                        },
                        "size_mb": round(package_path.stat().st_size / (1024 * 1024), 2)
                    }
                    
                    self.logger.info(f"✅ 内容包创建成功: {package_path}")
                    return True, result
                else:
                    return False, {"error": "ZIP打包失败"}
                    
        except Exception as e:
            error_msg = f"创建内容包时发生错误: {e}"
            self.logger.error(error_msg)
            return False, {"error": error_msg}
    
    def _create_pdf(self, post: frontmatter.Post, temp_path: Path, 
                   title: str) -> Tuple[bool, Optional[Path]]:
        """生成PDF文件"""
        try:
            # 准备HTML内容
            html_content = self._prepare_html_for_pdf(post, title)
            
            # CSS样式
            css_content = """
            @page {
                size: A4;
                margin: 2cm;
            }
            
            body {
                font-family: "PingFang SC", "Microsoft YaHei", "Hiragino Sans GB", sans-serif;
                line-height: 1.6;
                color: #333;
                font-size: 14px;
            }
            
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 30px;
                font-size: 24px;
            }
            
            h2 {
                color: #34495e;
                margin-top: 30px;
                margin-bottom: 15px;
                font-size: 20px;
            }
            
            h3 {
                color: #7f8c8d;
                margin-top: 25px;
                margin-bottom: 12px;
                font-size: 16px;
            }
            
            p {
                margin-bottom: 12px;
                text-align: justify;
            }
            
            ul, ol {
                margin-bottom: 15px;
                padding-left: 25px;
            }
            
            li {
                margin-bottom: 5px;
            }
            
            blockquote {
                border-left: 4px solid #3498db;
                margin: 20px 0;
                padding: 10px 20px;
                background-color: #f8f9fa;
                font-style: italic;
            }
            
            code {
                background-color: #f1f2f6;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: "Consolas", "Monaco", monospace;
            }
            
            pre {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 15px;
                margin: 15px 0;
                overflow-x: auto;
            }
            
            img {
                max-width: 100%;
                height: auto;
                margin: 15px 0;
                border-radius: 5px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            
            .article-meta {
                color: #7f8c8d;
                font-size: 12px;
                margin-bottom: 30px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
            
            .footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e9ecef;
                font-size: 12px;
                color: #7f8c8d;
                text-align: center;
            }
            """
            
            # 生成PDF
            pdf_filename = f"{self._safe_filename(title)}.pdf"
            pdf_path = temp_path / pdf_filename
            
            font_config = FontConfiguration()
            html_doc = HTML(string=html_content)
            css_doc = CSS(string=css_content, font_config=font_config)
            
            html_doc.write_pdf(str(pdf_path), stylesheets=[css_doc], font_config=font_config)
            
            self.logger.info(f"PDF生成成功: {pdf_filename}")
            return True, pdf_path
            
        except Exception as e:
            self.logger.error(f"PDF生成失败: {e}")
            return False, None
    
    def _prepare_html_for_pdf(self, post: frontmatter.Post, title: str) -> str:
        """准备用于PDF的HTML内容"""
        # 文章元信息
        date = post.metadata.get('date', '')
        categories = post.metadata.get('categories', [])
        tags = post.metadata.get('tags', [])
        
        # 转换Markdown为HTML
        html_body = markdown2.markdown(
            post.content,
            extras=["fenced-code-blocks", "tables", "strike", "task_list"]
        )
        
        # 处理图片链接 - 移除OneDrive链接，因为PDF中无法显示
        # html_body = re.sub(r'<img[^>]+src="[^"]*1drv\.ms[^"]*"[^>]*>', 
        #                   '<p style="color: #666; font-style: italic;">[图片已省略，请查看原文]</p>', 
        #                   html_body)
        
        # 构建完整HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
    <h1>{title}</h1>
    
    <div class="article-meta">
        <p><strong>发布日期</strong>: {date}</p>
        {f'<p><strong>分类</strong>: {", ".join(categories)}</p>' if categories else ''}
        {f'<p><strong>标签</strong>: {", ".join(tags)}</p>' if tags else ''}
        <p><strong>PDF生成时间</strong>: {datetime.now().strftime("%Y年%m月%d日 %H:%M")}</p>
    </div>
    
    {html_body}
    
    <div class="footer">
        <p>本PDF由"有心言者"自动生成系统创建</p>
        <p>获取更多内容请关注微信公众号：有心言者</p>
        <p>博客地址：https://zhurong2020.github.io</p>
    </div>
</body>
</html>
        """
        
        return html_content
    
    def _collect_images(self, content: str, temp_path: Path) -> List[Dict]:
        """收集并下载文章中的图片"""
        images_info = []
        
        # 查找所有图片链接
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        matches = re.findall(image_pattern, content)
        
        images_dir = temp_path / "images"
        images_dir.mkdir(exist_ok=True)
        
        for i, (alt_text, image_url) in enumerate(matches, 1):
            try:
                if image_url.startswith(('http://', 'https://')):
                    # 下载网络图片
                    response = requests.get(image_url, timeout=20)
                    if response.status_code == 200:
                        # 尝试从URL或headers获取文件扩展名
                        ext = self._get_image_extension(image_url, response.headers)
                        filename = f"image_{i:02d}{ext}"
                        
                        image_path = images_dir / filename
                        with open(image_path, 'wb') as f:
                            f.write(response.content)
                        
                        images_info.append({
                            "filename": filename,
                            "alt_text": alt_text,
                            "original_url": image_url,
                            "local_path": str(image_path),
                            "size_kb": round(len(response.content) / 1024, 2)
                        })
                        
                        self.logger.info(f"图片下载成功: {filename}")
                    else:
                        self.logger.warning(f"图片下载失败: {image_url}")
                        
            except Exception as e:
                self.logger.warning(f"处理图片时出错: {image_url} - {e}")
        
        return images_info
    
    def _get_image_extension(self, url: str, headers: Dict) -> str:
        """从URL或headers获取图片扩展名"""
        # 先从URL路径尝试
        parsed_url = urlparse(url)
        path = parsed_url.path.lower()
        
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']:
            if ext in path:
                return ext
        
        # 从Content-Type头获取
        content_type = headers.get('content-type', '').lower()
        if 'jpeg' in content_type or 'jpg' in content_type:
            return '.jpg'
        elif 'png' in content_type:
            return '.png'
        elif 'gif' in content_type:
            return '.gif'
        elif 'webp' in content_type:
            return '.webp'
        
        # 默认使用jpg
        return '.jpg'
    
    def _extract_links(self, content: str) -> List[Dict]:
        """提取文章中的所有链接"""
        links_info = []
        
        # Markdown链接格式 [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, content)
        
        # 去重并分类
        seen_urls = set()
        for text, url in matches:
            if url not in seen_urls and url.startswith(('http://', 'https://')):
                seen_urls.add(url)
                
                # 简单分类
                category = "其他"
                domain = urlparse(url).netloc.lower()
                
                if any(official in domain for official in ['tesla.com', 'spacex.com', 'neuralink.com', 'x.com']):
                    category = "官方网站"
                elif any(news in domain for news in ['bloomberg.com', 'reuters.com', 'cnbc.com', 'wsj.com']):
                    category = "新闻媒体"
                elif any(tech in domain for tech in ['github.com', 'arxiv.org', 'nature.com', 'science.org']):
                    category = "技术资料"
                elif any(social in domain for social in ['twitter.com', 'linkedin.com', 'youtube.com']):
                    category = "社交媒体"
                
                links_info.append({
                    "text": text,
                    "url": url,
                    "category": category,
                    "domain": domain
                })
        
        return links_info
    
    def _create_links_file(self, links_info: List[Dict], temp_path: Path) -> None:
        """创建链接汇总文件"""
        if not links_info:
            return
        
        content = "# 🔗 链接汇总\n\n"
        
        # 按分类组织链接
        categories = {}
        for link in links_info:
            category = link["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(link)
        
        for category, links in categories.items():
            content += f"## {category}\n\n"
            for link in links:
                content += f"- [{link['text']}]({link['url']})\n"
            content += "\n"
        
        content += "---\n\n"
        content += f"*共计 {len(links_info)} 个链接，生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}*\n"
        
        links_file = temp_path / "链接汇总.txt"
        with open(links_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_resource_list(self, title: str, date: str, images_info: List[Dict], 
                            links_info: List[Dict], temp_path: Path) -> None:
        """创建资料清单文件"""
        # 生成图片列表
        image_list = ""
        if images_info:
            for img in images_info:
                image_list += f"- `{img['filename']}` - {img['alt_text']} ({img['size_kb']} KB)\n"
        else:
            image_list = "- 无图片资源\n"
        
        # 生成官方链接列表
        official_links = ""
        additional_links = ""
        
        for link in links_info:
            link_line = f"- [{link['text']}]({link['url']})\n"
            if link['category'] == "官方网站":
                official_links += link_line
            else:
                additional_links += link_line
        
        if not official_links:
            official_links = "- 无官方链接\n"
        if not additional_links:
            additional_links = "- 无扩展资料\n"
        
        # 生成资料清单
        content = self.resource_list_template.format(
            title=title,
            date=date,
            generated_at=datetime.now().strftime("%Y年%m月%d日 %H:%M"),
            article_filename=self._safe_filename(title),
            image_list=image_list,
            official_links=official_links,
            additional_links=additional_links
        )
        
        readme_file = temp_path / "资料清单.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _create_zip_package(self, temp_path: Path, title: str, date: str) -> Tuple[bool, Optional[Path]]:
        """创建ZIP文件"""
        try:
            # 生成ZIP文件名
            safe_title = self._safe_filename(title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            zip_filename = f"{safe_title}_{timestamp}_package.zip"
            zip_path = self.output_dir / zip_filename
            
            # 创建ZIP文件
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 添加所有文件
                for file_path in temp_path.rglob('*'):
                    if file_path.is_file():
                        # 计算相对路径
                        arcname = file_path.relative_to(temp_path)
                        zipf.write(file_path, arcname)
            
            self.logger.info(f"ZIP包创建成功: {zip_filename}")
            return True, zip_path
            
        except Exception as e:
            self.logger.error(f"创建ZIP包失败: {e}")
            return False, None
    
    def _safe_filename(self, filename: str) -> str:
        """生成安全的文件名"""
        # 移除或替换不安全的字符
        safe = re.sub(r'[^\w\s-]', '', filename)
        safe = re.sub(r'[-\s]+', '-', safe).strip('-')
        return safe[:50]  # 限制长度
    
    def get_package_info(self, package_path: str) -> Optional[Dict]:
        """获取内容包信息"""
        try:
            zip_path = Path(package_path)
            if not zip_path.exists():
                return None
            
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                file_list = zipf.namelist()
                
                info = {
                    "path": str(zip_path),
                    "filename": zip_path.name,
                    "size_mb": round(zip_path.stat().st_size / (1024 * 1024), 2),
                    "created_at": datetime.fromtimestamp(zip_path.stat().st_ctime),
                    "files": {
                        "total": len(file_list),
                        "pdf": len([f for f in file_list if f.endswith('.pdf')]),
                        "images": len([f for f in file_list if f.startswith('images/')]),
                        "docs": len([f for f in file_list if f.endswith(('.md', '.txt'))])
                    }
                }
                
                return info
                
        except Exception as e:
            self.logger.error(f"获取包信息失败: {e}")
            return None


def create_package_creator() -> PackageCreator:
    """创建内容包创建器实例"""
    return PackageCreator()


if __name__ == "__main__":
    # 测试脚本
    import sys
    
    if len(sys.argv) != 2:
        print("用法: python package_creator.py <article_path>")
        sys.exit(1)
    
    article_path = sys.argv[1]
    
    try:
        creator = create_package_creator()
        success, result = creator.create_package(article_path)
        
        if success:
            print(f"✅ 内容包创建成功!")
            print(f"文件路径: {result['package_path']}")
            print(f"文件大小: {result['size_mb']} MB")
            print(f"包含文件: PDF + {result['files']['images_count']}张图片 + {result['files']['links_count']}个链接")
        else:
            print(f"❌ 创建失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")