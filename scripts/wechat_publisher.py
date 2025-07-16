import os
import requests
import time
import json
import logging
import re
import markdown2
import hashlib
from typing import Optional, Dict
from pathlib import Path
from dotenv import load_dotenv

class WeChatPublisher:
    def __init__(self):
        """初始化微信发布器"""
        load_dotenv()
        self.app_id = os.getenv("WECHAT_APPID")
        self.app_secret = os.getenv("WECHAT_APPSECRET")
        if not self.app_id or not self.app_secret:
            raise ValueError("WECHAT_APPID and WECHAT_APPSECRET must be set in .env file")
        self.access_token = None
        self.token_expires_at = 0
        self.logger = logging.getLogger("WeChatPublisher")
        
        # 图片缓存系统
        self.cache_dir = Path("_output/wechat_image_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "image_cache.json"
        self.image_cache = self._load_image_cache()

    def get_access_token(self, force_refresh: bool = False) -> str:
        """获取或刷新 access_token"""
        if self.access_token and time.time() < self.token_expires_at and not force_refresh:
            self.logger.info("Using cached access_token.")
            return self.access_token

        self.logger.info("Requesting new access_token...")
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if "access_token" in data:
                self.access_token = data["access_token"]
                self.token_expires_at = time.time() + data.get("expires_in", 7200) - 300
                self.logger.info("Successfully obtained new access_token.")
                return self.access_token
            else:
                error_msg = data.get("errmsg", "Unknown error")
                self.logger.error(f"Failed to get access_token: {error_msg}")
                raise Exception(f"WeChat API Error: {error_msg}")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request to get access_token failed: {e}")
            raise

    def transform_content(self, markdown_text: str) -> str:
        """将Markdown内容转换为微信公众号文章格式

        Args:
            markdown_text: 文章的Markdown原文.

        Returns:
            转换和处理后的HTML字符串.
        """
        self.logger.info("Transforming content for WeChat...")

        # 1. Markdown to HTML
        # 使用markdown2并启用一些推荐的扩展
        html = markdown2.markdown(markdown_text, extras=["tables", "fenced-code-blocks", "footnotes", "cuddled-lists"])

        # 2. 移除所有<a>标签，但保留标签内的文本
        # 使用正则表达式将 <a ...>...</a> 替换为其内部的文本
        html = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', html)
        self.logger.info("Removed all hyperlinks from content.")

        # 3. 添加“阅读原文”引导
        read_more_text = "<p>--</p><p>请点击文末的阅读原文查看完整文档</p>"
        html += read_more_text
        self.logger.info("Appended 'Read More' notice.")

        # 先进行AI优化，再处理图片，避免上传不需要的图片
        html = self.enhance_html_with_ai(html)
        
        # 在AI优化后再处理图片，只上传最终需要的图片
        html = self.process_images(html)

        return html

    def process_images(self, html_content: str) -> str:
        """处理HTML内容中的图片，将其上传到微信并替换链接"""
        self.logger.info("Processing images in HTML content...")
        img_urls = re.findall(r'<img src="(https?://1drv\.ms/[^\s"]+)"', html_content)
        if not img_urls:
            self.logger.info("No OneDrive images found to process.")
            return html_content

        # 去重，避免重复上传
        unique_urls = sorted(list(set(img_urls)))
        self.logger.info(f"Found {len(unique_urls)} unique image(s) to upload.")

        url_map = {}
        for url in unique_urls:
            wechat_url = self._upload_image_from_url(url)
            if wechat_url:
                url_map[url] = wechat_url
        
        self.logger.info("Replacing image URLs in HTML...")
        for onedrive_url, wechat_url in url_map.items():
            html_content = html_content.replace(onedrive_url, wechat_url)
        
        self.logger.info("Image processing complete.")
        return html_content

    def _upload_image_from_url(self, image_url: str) -> Optional[str]:
        """从URL下载图片并上传到微信服务器，支持缓存机制"""
        try:
            self.logger.info(f"Downloading image from: {image_url}")
            response = requests.get(image_url, timeout=20)
            response.raise_for_status()
            image_data = response.content
            content_type = response.headers.get('content-type', 'image/jpeg')

            # 检查缓存
            cached_url = self._get_cached_image_url(image_url, image_data)
            if cached_url:
                return cached_url

            # 获取access_token
            access_token = self.get_access_token()
            if not access_token:
                return None

            # 上传到微信
            upload_url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={access_token}"
            files = {'media': ('image.jpg', image_data, content_type)}
            
            self.logger.info(f"Uploading image to WeChat...")
            upload_response = requests.post(upload_url, files=files, timeout=30)
            upload_response.raise_for_status()
            upload_data = upload_response.json()

            if "url" in upload_data:
                wechat_url = upload_data["url"]
                self.logger.info(f"Successfully uploaded image. WeChat URL: {wechat_url}")
                # 缓存映射关系
                self._cache_image_mapping(image_url, wechat_url, image_data)
                return wechat_url
            else:
                error_msg = upload_data.get("errmsg", "Unknown upload error")
                self.logger.error(f"Failed to upload image to WeChat: {error_msg}")
                return None

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download or upload image from {image_url}: {e}")
            return None

    def enhance_html_with_ai(self, html_content: str) -> str:
        """使用Gemini API对HTML内容进行排版和风格优化"""
        self.logger.info("Enhancing HTML with AI for better layout...")
        try:
            # 获取Gemini模型，这里假设ContentPipeline已经初始化了模型
            # 在实际应用中，可能需要通过参数传入或更优雅地获取
            from scripts.content_pipeline import ContentPipeline
            gemini_model = ContentPipeline().model

            # 构建一个专门为微信排版优化的Prompt
            prompt = f"""
            You are an expert in WeChat article formatting. Your task is to refine the following HTML to make it more readable and engaging on mobile devices. You must follow these rules strictly:
            1.  Do NOT change, add, or remove any text content. Your task is to format, not rewrite.
            2.  Do NOT change any `<img>` tags or their `src` attributes.
            3.  Add relevant Emojis: Insert a single, appropriate emoji at the beginning of each heading (`<h1>`, `<h2>`, `<h3>`). For example, `<h2>...` becomes `<h2>✨ ...</h2>`.
            4.  Inject mobile-friendly inline CSS: Add `style` attributes to HTML tags. For example:
                -   For `<p>`: `style="margin: 1.2em 0; line-height: 1.8; font-size: 16px;"`
                -   For `<h2>`: `style="font-size: 1.5em; margin-top: 2em; margin-bottom: 1em; border-bottom: 2px solid #f2f2f2; padding-bottom: 0.3em;"`
                -   For `<h3>`: `style="font-size: 1.2em; margin-top: 1.8em; margin-bottom: 1em;"`
                -   For `<ul>` or `<ol>`: `style="padding-left: 20px;"`
                -   For `<li>`: `style="margin-bottom: 0.8em;"`
            5.  Ensure all text content is wrapped in appropriate tags like `<p>` or `<li>`. Do not leave raw text outside of tags.
            6.  Return ONLY the modified, clean HTML body content. Do not include `<html>`, `<head>`, `<body>` tags or any explanations.
            7.  Do NOT generate empty tags like `<h2>{{}}</h2>` or `<p>{{}}</p>`. If you encounter malformed content, skip it.
            8.  Do NOT include markdown code block markers like ```html or ``` in your output.

            Here is the HTML content to process:
            ---
            {html_content}
            """

            # 调用Gemini API
            response = gemini_model.generate_content(prompt)
            enhanced_html = response.text.strip()
            
            self.logger.info("Successfully enhanced HTML with AI.")
            return enhanced_html

        except Exception as e:
            self.logger.error(f"Failed to enhance HTML with AI: {e}")
            # 如果AI增强失败，返回原始的HTML，确保流程不中断
            return html_content
    
    def _load_image_cache(self) -> Dict[str, dict]:
        """加载图片缓存映射"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load image cache: {e}")
        return {}
    
    def _save_image_cache(self):
        """保存图片缓存映射"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.image_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save image cache: {e}")
    
    def _get_image_hash(self, image_data: bytes) -> str:
        """计算图片数据的MD5哈希值"""
        return hashlib.md5(image_data).hexdigest()
    
    def _get_cached_image_url(self, onedrive_url: str, image_data: bytes) -> Optional[str]:
        """检查图片是否已缓存，返回微信URL"""
        image_hash = self._get_image_hash(image_data)
        
        # 检查是否有相同内容的图片已上传
        for cached_url, cached_info in self.image_cache.items():
            if isinstance(cached_info, dict) and cached_info.get('hash') == image_hash:
                self.logger.info(f"Found cached image for {onedrive_url}: {cached_info['wechat_url']}")
                return cached_info['wechat_url']
        
        return None
    
    def _cache_image_mapping(self, onedrive_url: str, wechat_url: str, image_data: bytes):
        """缓存图片映射关系"""
        image_hash = self._get_image_hash(image_data)
        self.image_cache[onedrive_url] = {
            'wechat_url': wechat_url,
            'hash': image_hash,
            'upload_time': time.time()
        }
        self._save_image_cache()

    def save_as_draft(self, title: str, content: str, author: str = "系统发布") -> bool:
        """保存文章为草稿到微信公众号后台
        
        由于微信API限制，此方法现在只生成本地预览文件
        用户需要手动在微信公众平台后台创建文章
        
        Args:
            title: 文章标题
            content: 文章内容（HTML格式）
            author: 作者名称
            
        Returns:
            bool: 始终返回True（生成预览文件成功）
        """
        try:
            self.logger.info(f"Preparing WeChat content for: {title}")
            
            # 清理HTML内容，移除可能导致问题的元素
            cleaned_content = self._clean_html_for_wechat(content)
            
            # 生成发布指导信息
            guide_info = self._generate_publish_guide(title, cleaned_content, author)
            
            # 保存指导信息到文件
            self._save_publish_guide(title, guide_info)
            
            self.logger.info(f"✅ WeChat content prepared successfully for: {title}")
            self.logger.info("📋 请查看 _output/wechat_guides/ 目录中的发布指导文件")
            self.logger.info("🔗 在微信公众平台后台手动创建文章：https://mp.weixin.qq.com/")
            
            return True
                
        except Exception as e:
            self.logger.error(f"Error preparing WeChat content for '{title}': {e}")
            return False

    def _clean_html_for_wechat(self, html_content: str) -> str:
        """清理HTML内容，移除可能导致微信API错误的元素"""
        import re
        
        # 移除可能的媒体ID引用
        html_content = re.sub(r'media_id\s*=\s*["\'][^"\']*["\']', '', html_content)
        
        # 移除完整的HTML文档结构（如果存在）
        # 提取<body>标签内的内容，如果没有<body>标签则保持原样
        body_match = re.search(r'<body[^>]*>(.*?)</body>', html_content, re.DOTALL | re.IGNORECASE)
        if body_match:
            html_content = body_match.group(1)
        
        # 移除可能存在的<div class="content">包装
        content_match = re.search(r'<div class="content"[^>]*>(.*?)</div>', html_content, re.DOTALL | re.IGNORECASE)
        if content_match:
            html_content = content_match.group(1)
        
        # 移除不支持的HTML标签
        unsupported_tags = ['script', 'style', 'meta', 'link', 'iframe', 'embed', 'object', 'html', 'head', 'title']
        for tag in unsupported_tags:
            html_content = re.sub(f'<{tag}[^>]*>.*?</{tag}>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
            html_content = re.sub(f'<{tag}[^>]*/?>', '', html_content, flags=re.IGNORECASE)
        
        # 移除<hr>分隔线（微信可能不支持）
        html_content = re.sub(r'<hr[^>]*/?>', '', html_content, flags=re.IGNORECASE)
        
        # 确保图片URL格式正确
        html_content = re.sub(r'<img\s+([^>]*?)src\s*=\s*["\']([^"\']*)["\']([^>]*?)>', 
                            lambda m: f'<img {m.group(1)}src="{m.group(2)}" {m.group(3)}>' if m.group(2).startswith('http') else '',
                            html_content)
        
        # 移除空的img标签
        html_content = re.sub(r'<img[^>]*src\s*=\s*["\']["\'][^>]*>', '', html_content)
        
        # 清理多余的空白字符
        html_content = re.sub(r'\n\s*\n', '\n', html_content)
        
        return html_content.strip()

    def _extract_digest(self, html_content: str) -> str:
        """从HTML内容中提取摘要"""
        import re
        
        # 移除HTML标签，提取纯文本
        text = re.sub(r'<[^>]+>', '', html_content)
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 取前60个字符作为摘要
        digest = text[:60]
        if len(text) > 60:
            digest += "..."
        
        return digest

    def _generate_publish_guide(self, title: str, content: str, author: str) -> dict:
        """生成发布指导信息"""
        return {
            "title": title,
            "author": author,
            "digest": self._extract_digest(content),
            "content": content,
            "instructions": [
                "1. 登录微信公众平台：https://mp.weixin.qq.com/",
                "2. 点击左侧菜单 → 素材管理 → 新建图文素材",
                "3. 填写标题、作者、摘要等信息",
                "4. 将下方的HTML内容复制到正文编辑器中",
                "5. 上传封面图片（可选）",
                "6. 保存并发布或保存为草稿"
            ],
            "html_content": content,
            "tips": [
                "💡 HTML内容已经过优化，可以直接粘贴到微信编辑器",
                "📱 图片URL已经是微信服务器地址，无需重新上传",
                "🔗 所有外部链接已被移除，符合微信公众号规范",
                "✨ 内容已针对手机阅读进行了格式优化"
            ]
        }

    def _save_publish_guide(self, title: str, guide_info: dict):
        """保存发布指导文件"""
        try:
            from pathlib import Path
            import re
            from datetime import datetime
            
            # 创建指导文件目录
            guide_dir = Path("_output/wechat_guides")
            guide_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成安全的文件名
            safe_title = re.sub(r'[^\w\s-]', '', title).strip()
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 保存指导文件
            guide_file = guide_dir / f"{safe_title}_{timestamp}_guide.md"
            
            with open(guide_file, 'w', encoding='utf-8') as f:
                f.write(f"""# 微信公众号发布指导

## 📝 文章信息
- **标题**: {guide_info['title']}
- **作者**: {guide_info['author']}
- **摘要**: {guide_info['digest']}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📋 发布步骤
""")
                for instruction in guide_info['instructions']:
                    f.write(f"{instruction}\n")
                
                f.write(f"""
## 💡 使用提示
""")
                for tip in guide_info['tips']:
                    f.write(f"{tip}\n")
                
                f.write(f"""
## 📄 HTML内容
请复制以下HTML内容到微信公众号编辑器中：

```html
{guide_info['html_content']}
```

## 🔗 相关链接
- 微信公众平台：https://mp.weixin.qq.com/
- 素材管理：https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&type=10

## 📝 使用说明
1. 复制上方HTML内容到剪贴板
2. 在微信公众号编辑器中切换到HTML模式
3. 粘贴HTML内容
4. 切换回可视化编辑模式进行最终调整
""")
            
            # 同时保存纯HTML文件方便复制
            html_file = guide_dir / f"{safe_title}_{timestamp}_content.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(guide_info['html_content'])
            
            self.logger.info(f"📋 发布指导文件已保存: {guide_file}")
            self.logger.info(f"📄 HTML内容文件已保存: {html_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save publish guide: {e}")

    def publish_article(self, title: str, markdown_content: str, author: str = "系统发布") -> bool:
        """发布文章到微信公众号（保存为草稿）
        
        Args:
            title: 文章标题
            markdown_content: Markdown格式的文章内容
            author: 作者名称
            
        Returns:
            bool: 发布成功返回True，失败返回False
        """
        try:
            self.logger.info(f"Publishing article to WeChat: {title}")
            
            # 转换Markdown内容为适合微信的HTML
            html_content = self.transform_content(markdown_content)
            
            # 保存发布指导（替代草稿API）
            success = self.save_as_draft(title, html_content, author)
            
            if success:
                self.logger.info(f"Article '{title}' successfully prepared for WeChat publishing")
            else:
                self.logger.error(f"Failed to prepare article '{title}' for WeChat publishing")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error publishing article '{title}': {e}")
            return False
    
    def _save_local_preview(self, title: str, html_content: str, original_markdown: str):
        """保存微信版本的本地预览文件"""
        try:
            from pathlib import Path
            import re
            from datetime import datetime
            
            # 创建预览目录
            preview_dir = Path("_output/wechat_previews")
            preview_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成安全的文件名
            safe_title = re.sub(r'[^\w\s-]', '', title).strip()
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # 保存HTML预览文件
            html_file = preview_dir / f"{safe_title}_{timestamp}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 微信版本预览</title>
    <style>
        body {{ max-width: 800px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif; }}
        .header {{ background: #f0f0f0; padding: 15px; margin-bottom: 20px; border-radius: 5px; }}
        .content {{ line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📱 微信公众号版本预览</h1>
        <p><strong>标题:</strong> {title}</p>
        <p><strong>生成时间:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p><strong>状态:</strong> 已保存到微信草稿箱，可在公众号后台查看和发布</p>
    </div>
    <div class="content">
        {html_content}
    </div>
</body>
</html>""")
            
            # 保存处理后的Markdown文件
            md_file = preview_dir / f"{safe_title}_{timestamp}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(f"""---
title: {title}
platform: 微信公众号
generated_at: {datetime.now().isoformat()}
status: 已保存到草稿箱
---

# {title}

{original_markdown}

---

**处理说明:**
- 已移除所有超链接
- 已添加"阅读原文"引导
- 图片已上传到微信服务器
- 已通过AI进行排版优化
""")
            
            self.logger.info(f"Local preview saved: {html_file}")
            self.logger.info(f"Local markdown saved: {md_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save local preview: {e}")
            # 不影响主流程，继续执行

if __name__ == '__main__':
    # 用于直接测试此类
    try:
        publisher = WeChatPublisher()
        token = publisher.get_access_token()
        print(f"Successfully got access token: {token[:10]}...")

        # 测试内容转换
        test_md = """# 测试标题

这是一个段落，包含一个[链接](http://example.com)，我们会移除它。

- 列表1
- 列表2
"""
        transformed_html = publisher.transform_content(test_md)
        print("\n--- Transformed HTML ---")
        print(transformed_html)
        with open("wechat_preview.html", "w", encoding="utf-8") as f:
            f.write(transformed_html)
        print("\nPreview saved to wechat_preview.html")

    except (ValueError, Exception) as e:
        print(f"An error occurred: {e}")