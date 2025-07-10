import os
import requests
import time
import json
import logging
import re
import markdown2
from typing import Optional
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

        # TODO: Image uploading and URL replacement

        html = self.process_images(html)

        html = self.enhance_html_with_ai(html)

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
        """从URL下载图片并上传到微信服务器"""
        try:
            self.logger.info(f"Downloading image from: {image_url}")
            response = requests.get(image_url, timeout=20)
            response.raise_for_status()
            image_data = response.content
            content_type = response.headers.get('content-type', 'image/jpeg')

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