import os
import requests
import time
import json
import logging
import re
import markdown2
import hashlib
from typing import Optional, Dict, Any, TYPE_CHECKING
from pathlib import Path
from dotenv import load_dotenv

if TYPE_CHECKING:
    from google.generativeai.generative_models import GenerativeModel

class WeChatApiUsageTracker:
    """Tracks WeChat API usage to prevent exceeding daily limits."""
    def __init__(self, cache_dir: Path):
        self.usage_file = cache_dir / "wechat_api_usage.json"
        self.usage_data = self._load_usage()
        self._reset_if_new_day()

    def _load_usage(self) -> Dict[str, Any]:
        if not self.usage_file.exists():
            return {"date": time.strftime("%Y-%m-%d"), "calls": {}}
        try:
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"date": time.strftime("%Y-%m-%d"), "calls": {}}

    def _save_usage(self):
        try:
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=2)
        except IOError as e:
            logging.error(f"Failed to save API usage data: {e}")

    def _reset_if_new_day(self):
        today = time.strftime("%Y-%m-%d")
        if self.usage_data.get("date") != today:
            self.usage_data = {"date": today, "calls": {}}
            self._save_usage()
            logging.info("New day detected, resetting WeChat API usage stats.")

    def check_limit(self, api_name: str, limit: int) -> bool:
        """Check if the API call would exceed the limit."""
        count = self.usage_data["calls"].get(api_name, 0)
        if count >= limit:
            logging.error(f"API call to '{api_name}' aborted. Daily limit of {limit} reached.")
            return False
        if count >= limit * 0.95:
            logging.warning(f"API '{api_name}' usage ({count}/{limit}) is approaching daily limit.")
        return True

    def increment(self, api_name: str):
        """Increment the call count for a specific API."""
        self.usage_data["calls"][api_name] = self.usage_data["calls"].get(api_name, 0) + 1
        self._save_usage()

class WechatPublisher:
    """
    Handles all interactions with the WeChat Official Account API.
    """
    API_LIMITS = {
        "token": 2000,
        "add_material": 1000,
        "uploadimg": 1000,
        "add_news": 1000,
    }

    def __init__(self, gemini_model):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model = gemini_model

        load_dotenv()
        self.app_id = os.getenv("WECHAT_APPID")
        self.app_secret = os.getenv("WECHAT_APPSECRET")
        if not self.app_id or not self.app_secret:
            raise ValueError("WECHAT_APPID and WECHAT_APPSECRET must be set in .env file.")

        project_root = Path(__file__).parent.parent
        self.api_base_url = "https://api.weixin.qq.com/cgi-bin"
        self.access_token: Optional[str] = None
        self.token_expires_at: int = 0
        
        cache_dir = project_root / "_output/wechat_image_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = cache_dir / "image_cache.json"
        self.image_cache = self._load_image_cache()
        self.api_tracker = WeChatApiUsageTracker(cache_dir)

    def _get_access_token(self) -> Optional[str]:
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        if not self.api_tracker.check_limit("token", self.API_LIMITS["token"]):
            return None

        self.logger.info("Requesting new access_token from WeChat API...")
        url = f"{self.api_base_url}/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            if "access_token" in data:
                self.api_tracker.increment("token")
                self.access_token = data["access_token"]
                self.token_expires_at = time.time() + data.get("expires_in", 7200) - 300
                return self.access_token
            else:
                self.logger.error(f"Failed to get access_token: {data.get('errmsg', 'Unknown error')}")
                return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request for access_token failed: {e}")
            return None

    def _transform_for_wechat(self, markdown_content: str) -> str:
        """Transforms markdown content into WeChat-ready HTML."""
        self.logger.info("Starting full content transformation for WeChat...")

        # 1. AI-powered content summarization and rewriting
        self.logger.info("Step 1: Rewriting and summarizing content with AI...")
        summarize_prompt = f"""Please rewrite and summarize the following article to be about 800-1000 words, making it more engaging for a WeChat audience. Focus on the core ideas, use shorter paragraphs, and maintain the original tone. Do not add any titles or headers.

---

{markdown_content}"""
        try:
            response = self.model.generate_content(summarize_prompt)
            rewritten_md = response.text
            self.logger.info("Content successfully rewritten by AI.")
        except Exception as e:
            self.logger.error(f"AI content summarization failed: {e}. Using original content.")
            rewritten_md = markdown_content

        # 2. Convert to HTML
        html = markdown2.markdown(rewritten_md, extras=["tables", "fenced-code-blocks", "footnotes"])

        # 3. AI-powered layout and formatting
        self.logger.info("Step 2: Formatting HTML for WeChat with AI...")
        format_prompt = f"""You are an expert in WeChat article formatting. Your task is to refine the following HTML to make it more readable and engaging on mobile devices. You must follow these rules strictly:
1.  Do NOT change, add, or remove any text content. Your task is to format, not rewrite.
2.  Do NOT change any `<img>` tags or their `src` attributes.
3.  Add relevant Emojis: Insert a single, appropriate emoji at the beginning of each heading (`<h1>`, `<h2>`, `<h3>`). For example, `<h2>...` becomes `<h2>✨ ...</h2>`.
4.  Inject mobile-friendly inline CSS: Add `style` attributes to HTML tags. For example:
    -   For `<p>`: `style="margin: 1.2em 0; line-height: 1.8; font-size: 16px;"`
    -   For `<h2>`: `style="font-size: 1.5em; margin-top: 2em; margin-bottom: 1em; border-bottom: 2px solid #f2f2f2; padding-bottom: 0.3em;"`
    -   For `<h3>`: `style="font-size: 1.2em; margin-top: 1.8em; margin-bottom: 1em;"`
    -   For `<ul>` or `<ol>`: `style="padding-left: 20px;"`
    -   For `<li>`: `style="margin-bottom: 0.8em;"`
5.  Remove all hyperlink `<a>` tags but keep the link text. For example, `<a href=... >text</a>` becomes `text`.
6.  Return ONLY the modified, clean HTML body content. Do not include `<html>`, `<head>`, `<body>` tags or any explanations.

Here is the HTML content to process:
---
{html}"""
        try:
            response = self.model.generate_content(format_prompt)
            formatted_html = response.text
            self.logger.info("HTML successfully formatted by AI.")
        except Exception as e:
            self.logger.error(f"AI formatting failed: {e}. Proceeding with basic HTML and removing links manually.")
            # Fallback to manual link removal if AI fails
            formatted_html = re.sub(r'<a[^>]*>(.*?)</a>', r'\1', html)

        # 4. Append "Read More" notice
        self.logger.info("Step 3: Appending 'Read More' notice.")
        read_more_notice = "<p style='text-align: center; color: #888; margin-top: 40px;'>- - -</p>" + "<p style='text-align: center; color: #888;'>因篇幅限制，更多技术细节和完整代码，<br>请点击文末的\"阅读原文\"在我的博客上查看。</p>"
        final_html = formatted_html + read_more_notice

        return final_html

    def _upload_content_image(self, image_path: Path) -> Optional[str]:
        if not image_path.exists(): return None
        with open(image_path, 'rb') as f: image_data = f.read()
        cached_url = self._get_cached_image_url(str(image_path), image_data)
        if cached_url: return cached_url
        if not self.api_tracker.check_limit("uploadimg", self.API_LIMITS["uploadimg"]): return None
        access_token = self._get_access_token()
        if not access_token: return None
        url = f"{self.api_base_url}/media/uploadimg?access_token={access_token}"
        files = {'media': (image_path.name, image_data)}
        try:
            response = requests.post(url, files=files, timeout=30)
            response.raise_for_status()
            data = response.json()
            if "url" in data:
                self.api_tracker.increment("uploadimg")
                wechat_url = data["url"]
                self._cache_image_mapping(str(image_path), wechat_url, image_data)
                return wechat_url
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request to upload content image failed: {e}")
        return None

    def _upload_thumb_media(self, image_path: Path) -> Optional[str]:
        if not image_path.exists(): return None
        if not self.api_tracker.check_limit("add_material", self.API_LIMITS["add_material"]): return None
        access_token = self._get_access_token()
        if not access_token: return None
        url = f"{self.api_base_url}/material/add_material?access_token={access_token}&type=thumb"
        files = {'media': (image_path.name, open(image_path, 'rb'))}
        try:
            response = requests.post(url, files=files, timeout=30)
            response.raise_for_status()
            data = response.json()
            if "media_id" in data:
                self.api_tracker.increment("add_material")
                return data["media_id"]
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request to upload thumbnail failed: {e}")
        return None

    def _process_html_images(self, html: str, project_root: Path) -> str:
        self.logger.info("Step 4: Processing and uploading images from HTML content...")
        img_pattern = re.compile(r'<img src="([^"]+)"')
        def replace_src(match):
            original_src = match.group(1)
            if original_src.startswith(('http', '//', 'data:')): return match.group(0)
            image_path = (project_root / original_src).resolve()
            wechat_url = self._upload_content_image(image_path)
            if wechat_url: return f'<img src="{wechat_url}"'
            return ""
        return img_pattern.sub(replace_src, html)

    def publish_to_draft(self, project_root: Path, front_matter: Dict[str, Any], markdown_content: str) -> Optional[str]:
        self.logger.info(f"Starting API publish process for: {front_matter.get('title', 'Untitled')}")
        cover_image_path_str = front_matter.get("image", {}).get("path")
        if not cover_image_path_str: return None
        cover_image_path = (project_root / cover_image_path_str).resolve()
        thumb_media_id = self._upload_thumb_media(cover_image_path)
        if not thumb_media_id: return None

        final_html = self._transform_for_wechat(markdown_content)
        final_html = self._process_html_images(final_html, project_root)

        article = {
            "title": front_matter.get("title", "Untitled"),
            "author": front_matter.get("author", ""),
            "digest": front_matter.get("excerpt", "")[:120],
            "content": final_html,
            "content_source_url": "",
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }
        
        if not self.api_tracker.check_limit("add_news", self.API_LIMITS["add_news"]): return None
        access_token = self._get_access_token()
        if not access_token: return None
        url = f"{self.api_base_url}/material/add_news?access_token={access_token}"
        payload = {"articles": [article]}
        try:
            response = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), timeout=30)
            response.raise_for_status()
            data = response.json()
            if "media_id" in data:
                self.api_tracker.increment("add_news")
                self.logger.info(f"✅ Successfully created draft! Media ID: {data['media_id']}")
                return data["media_id"]
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request to create draft failed: {e}")
        return None

    def generate_guide_file(self, project_root: Path, front_matter: Dict[str, Any], markdown_content: str) -> bool:
        self.logger.info(f"Generating manual guide file for: {front_matter.get('title', 'Untitled')}")
        guide_dir = project_root / "_output/wechat_guides"
        guide_dir.mkdir(parents=True, exist_ok=True)
        safe_title = re.sub(r'[^\w\s-]', '', front_matter.get('title', 'draft')).strip()
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        guide_file = guide_dir / f"{safe_title}_{timestamp}_guide.md"

        final_html = self._transform_for_wechat(markdown_content)
        final_html = self._process_html_images(final_html, project_root)

        guide_text = f"""# WeChat Publication Guide
- **Title**: {front_matter.get('title', 'N/A')}
- **Author**: {front_matter.get('author', 'N/A')}
- **Cover Image**: `{front_matter.get("image", {}).get("path", "N/A")}`
- **HTML Content**: See below
```html
{final_html}
```"""
        try:
            with open(guide_file, 'w', encoding='utf-8') as f: f.write(guide_text)
            self.logger.info(f"✅ Successfully generated guide file: {guide_file}")
            return True
        except IOError as e:
            self.logger.error(f"Failed to write guide file: {e}")
            return False

    def _load_image_cache(self) -> Dict[str, dict]:
        if not self.cache_file.exists(): return {}
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f: return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.logger.warning(f"Could not load image cache file: {e}")
            return {}

    def _save_image_cache(self):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.image_cache, f, ensure_ascii=False, indent=2)
        except IOError as e: self.logger.error(f"Failed to save image cache: {e}")

    def _get_image_hash(self, image_data: bytes) -> str:
        return hashlib.md5(image_data).hexdigest()

    def _get_cached_image_url(self, image_key: str, image_data: bytes) -> Optional[str]:
        image_hash = self._get_image_hash(image_data)
        cached_entry = self.image_cache.get(image_key)
        if cached_entry and cached_entry.get('hash') == image_hash:
            return cached_entry['wechat_url']
        for key, value in self.image_cache.items():
            if value.get('hash') == image_hash: return value['wechat_url']
        return None

    def _cache_image_mapping(self, image_key: str, wechat_url: str, image_data: bytes):
        self.image_cache[image_key] = {
            'wechat_url': wechat_url,
            'hash': self._get_image_hash(image_data),
            'upload_time': time.time()
        }
        self._save_image_cache()
