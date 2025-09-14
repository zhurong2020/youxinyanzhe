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
        "draft_add": 1000,  # 新的草稿箱API
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
        
        cache_dir = project_root / ".tmp/cache/wechat/images"
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
        """Transforms markdown content into WeChat-ready plain text."""
        self.logger.info("Starting full content transformation for WeChat...")
        print("\n📱 正在准备微信内容...")

        # 1. AI-powered content summarization and rewriting
        self.logger.info("Step 1: Rewriting and summarizing content with AI...")
        print("  1️⃣ 正在使用AI优化内容（适配移动端阅读）...")
        summarize_prompt = f"""Please rewrite and summarize the following article to be about 600-800 words, making it highly engaging for WeChat mobile reading. Focus on the core ideas and maintain the original tone.

IMPORTANT FORMATTING RULES:
1. Return ONLY plain text content - no HTML tags, no markdown syntax, no special formatting
2. Use appropriate emojis (2-3 per major section) to enhance readability
3. Structure paragraphs for mobile reading: 2-4 sentences per paragraph
4. Avoid single-line paragraphs - combine related ideas into cohesive paragraphs
5. Use natural transitions between paragraphs - no "---" or special separators
6. Keep the content concise and punchy for WeChat's fast-paced reading style
7. Use conversational tone with direct address to readers

---

{markdown_content}"""
        try:
            response = self.model.generate_content(summarize_prompt)
            rewritten_content = response.text
            self.logger.info("Content successfully rewritten by AI.")
            print("     ✅ AI内容优化完成")
        except Exception as e:
            self.logger.error(f"AI content summarization failed: {e}. Using original content.")
            print("     ⚠️ AI优化失败，使用原始内容")
            # Fallback: convert markdown to plain text
            import html2text
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            rewritten_content = h.handle(markdown2.markdown(markdown_content))

        # 2. AI-powered mobile optimization
        self.logger.info("Step 2: Optimizing content for mobile reading...")
        print("  2️⃣ 正在进行移动端阅读体验优化...")
        format_prompt = f"""You are an expert in WeChat mobile reading optimization. Your task is to polish the following content for the best WeChat reading experience. Follow these strict rules:

FORMATTING REQUIREMENTS:
1. Keep content as PLAIN TEXT only - absolutely no HTML tags, no markdown syntax, no special symbols
2. Use 3-5 relevant emojis throughout the entire article to enhance engagement
3. Create natural paragraph flow: each paragraph should be 2-4 sentences, avoid single-sentence paragraphs
4. Use smooth transitions between paragraphs - no artificial separators like "---" or bullets
5. Maintain conversational and engaging tone with direct reader engagement
6. Ensure total length is concise for mobile reading (aim for easy 2-3 minute read)
7. Use line breaks sparingly - only between distinct topic shifts
8. Make sure content flows naturally from one idea to the next

CONTENT GOALS:
- Keep readers engaged throughout
- Make complex ideas simple and relatable
- Use examples and analogies where appropriate
- End with a compelling conclusion or call-to-action

Here is the content to optimize:
---
{rewritten_content}"""
        try:
            response = self.model.generate_content(format_prompt)
            final_content = response.text
            self.logger.info("Content successfully optimized by AI.")
            print("     ✅ 移动端优化完成")
        except Exception as e:
            self.logger.error(f"AI optimization failed: {e}. Using rewritten content.")
            print("     ⚠️ 移动端优化失败，使用基础优化内容")
            final_content = rewritten_content

        # 3. Append "Read More" notice
        self.logger.info("Step 3: Appending 'Read More' notice.")
        print("  3️⃣ 正在添加阅读原文提示...")
        read_more_notice = "\n\n💡 因篇幅限制，更多详细内容和实用资源，请点击文末的\"阅读原文\"在我的博客上查看完整版本。"
        final_content = final_content + read_more_notice
        print("     ✅ 内容准备完成")

        return final_content

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

    def _upload_content_image_from_url(self, image_url: str) -> Optional[str]:
        """从OneDrive URL下载图片并上传到微信服务器"""
        try:
            self.logger.info(f"Downloading content image from: {image_url}")
            response = requests.get(image_url, timeout=20)
            response.raise_for_status()
            image_data = response.content
            
            # 检查缓存
            cached_url = self._get_cached_image_url(image_url, image_data)
            if cached_url:
                self.logger.info(f"Using cached image URL: {cached_url}")
                return cached_url
            
            if not self.api_tracker.check_limit("uploadimg", self.API_LIMITS["uploadimg"]): 
                return None
            
            access_token = self._get_access_token()
            if not access_token: return None
            
            url = f"{self.api_base_url}/media/uploadimg?access_token={access_token}"
            files = {'media': ('image.jpg', image_data, 'image/jpeg')}
            
            self.logger.info(f"Uploading content image to WeChat...")
            upload_response = requests.post(url, files=files, timeout=30)
            upload_response.raise_for_status()
            upload_data = upload_response.json()
            
            if "url" in upload_data:
                self.api_tracker.increment("uploadimg")
                wechat_url = upload_data["url"]
                self.logger.info(f"Successfully uploaded content image. WeChat URL: {wechat_url}")
                # 缓存映射关系
                self._cache_image_mapping(image_url, wechat_url, image_data)
                return wechat_url
            else:
                error_msg = upload_data.get("errmsg", "Unknown upload error")
                self.logger.error(f"Failed to upload content image to WeChat: {error_msg}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download or upload content image from {image_url}: {e}")
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

    def _upload_thumb_media_from_url(self, image_url: str) -> Optional[str]:
        """从OneDrive URL下载图片并上传为thumb media"""
        try:
            self.logger.info(f"Downloading cover image from: {image_url}")
            response = requests.get(image_url, timeout=20)
            response.raise_for_status()
            image_data = response.content
            
            if not self.api_tracker.check_limit("add_material", self.API_LIMITS["add_material"]): 
                return None
            
            access_token = self._get_access_token()
            if not access_token: return None
            
            url = f"{self.api_base_url}/material/add_material?access_token={access_token}&type=thumb"
            files = {'media': ('cover_image.jpg', image_data, 'image/jpeg')}
            
            self.logger.info(f"Uploading cover image to WeChat as thumb media...")
            upload_response = requests.post(url, files=files, timeout=30)
            upload_response.raise_for_status()
            upload_data = upload_response.json()
            
            if "media_id" in upload_data:
                self.api_tracker.increment("add_material")
                self.logger.info(f"Successfully uploaded cover image. Media ID: {upload_data['media_id']}")
                return upload_data["media_id"]
            else:
                error_msg = upload_data.get("errmsg", "Unknown upload error")
                self.logger.error(f"Failed to upload cover image to WeChat: {error_msg}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to download or upload cover image from {image_url}: {e}")
            return None

    def _process_html_images(self, html: str, project_root: Path) -> str:
        self.logger.info("Step 4: Processing and uploading images from HTML content...")
        print("  4️⃣ 正在处理文章中的图片...")

        # 统计图片数量
        import re
        img_pattern = re.compile(r'<img src="([^"]+)"')
        img_matches = img_pattern.findall(html)
        if img_matches:
            print(f"     发现 {len(img_matches)} 张图片需要处理")
        processed_count = [0]  # 使用列表以便在闭包中修改

        def replace_src(match):
            original_src = match.group(1)
            processed_count[0] += 1

            # 处理OneDrive链接
            if original_src.startswith("https://1drv.ms/"):
                print(f"     [{processed_count[0]}/{len(img_matches)}] 正在上传图片到微信服务器...")
                wechat_url = self._upload_content_image_from_url(original_src)
                if wechat_url:
                    print(f"     [{processed_count[0]}/{len(img_matches)}] ✅ 图片上传成功")
                    return f'<img src="{wechat_url}"'
                else:
                    print(f"     [{processed_count[0]}/{len(img_matches)}] ❌ 图片上传失败")
                return ""
            
            # 处理其他HTTP链接（跳过）
            if original_src.startswith(('http', '//', 'data:')): 
                return match.group(0)
            
            # 处理本地文件路径
            image_path = (project_root / original_src).resolve()
            print(f"     [{processed_count[0]}/{len(img_matches)}] 正在上传本地图片...")
            wechat_url = self._upload_content_image(image_path)
            if wechat_url:
                print(f"     [{processed_count[0]}/{len(img_matches)}] ✅ 图片上传成功")
                return f'<img src="{wechat_url}"'
            else:
                print(f"     [{processed_count[0]}/{len(img_matches)}] ❌ 图片上传失败")
            return ""

        result = img_pattern.sub(replace_src, html)
        if img_matches:
            print(f"     ✅ 图片处理完成")
        return result

    def publish_to_draft(self, project_root: Path, front_matter: Dict[str, Any], markdown_content: str) -> Optional[str]:
        self.logger.info(f"Starting API publish process for: {front_matter.get('title', 'Untitled')}")
        print(f"\n🚀 开始发布到微信公众号: {front_matter.get('title', 'Untitled')}")
        
        # 尝试多种方式获取封面图片
        cover_image_path_str = None
        cover_image_url = None
        
        # 方式1: 从image.path获取本地文件路径
        if front_matter.get("image", {}).get("path"):
            cover_image_path_str = front_matter.get("image", {}).get("path")
        # 方式2: 从header.overlay_image获取URL
        elif front_matter.get("header", {}).get("overlay_image"):
            cover_image_url = front_matter.get("header", {}).get("overlay_image")
        # 方式3: 从header.teaser获取URL
        elif front_matter.get("header", {}).get("teaser"):
            cover_image_url = front_matter.get("header", {}).get("teaser")
        else:
            self.logger.error("No cover image found in front matter")
            return None
        
        # 处理本地文件路径
        if cover_image_path_str:
            print("\n📷 正在上传封面图片...")
            cover_image_path = (project_root / cover_image_path_str).resolve()
            thumb_url = self._upload_content_image(cover_image_path)
        # 处理OneDrive URL
        elif cover_image_url and cover_image_url.startswith("https://1drv.ms/"):
            print("\n📷 正在从OneDrive下载并上传封面图片...")
            thumb_url = self._upload_content_image_from_url(cover_image_url)
        else:
            self.logger.error(f"Unsupported cover image format: {cover_image_url}")
            print(f"\n❌ 不支持的封面图片格式: {cover_image_url}")
            return None
            
        if not thumb_url:
            self.logger.error("Failed to upload cover image")
            print("❌ 封面图片上传失败")
            return None
        else:
            print("✅ 封面图片上传成功")

        final_html = self._transform_for_wechat(markdown_content)
        final_html = self._process_html_images(final_html, project_root)

        article = {
            "title": front_matter.get("title", "Untitled"),
            "author": front_matter.get("author", ""),
            "digest": front_matter.get("excerpt", "")[:120],
            "content": final_html,
            "content_source_url": "",
            "thumb_url": thumb_url,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }
        
        if not self.api_tracker.check_limit("draft_add", self.API_LIMITS["draft_add"]):
            print("\n❌ 已达到微信API每日调用限制")
            return None

        print("\n📤 正在创建微信草稿...")
        access_token = self._get_access_token()
        if not access_token:
            print("❌ 获取访问令牌失败")
            return None

        url = f"{self.api_base_url}/draft/add?access_token={access_token}"
        payload = {"articles": [article]}

        try:
            print("   正在提交到微信服务器...")
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            response = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()

            if "media_id" in data:
                self.api_tracker.increment("draft_add")
                self.logger.info(f"✅ Successfully created draft! Media ID: {data['media_id']}")
                print(f"\n🎉 成功创建微信草稿！")
                print(f"   Media ID: {data['media_id']}")
                print(f"\n📱 请登录微信公众号后台查看和发布草稿")
                print(f"   https://mp.weixin.qq.com/")
                return data["media_id"]
            else:
                # 处理微信API返回的错误
                error_code = data.get("errcode", "unknown")
                error_msg = data.get("errmsg", "Unknown error")
                self.logger.error(f"WeChat API error: {error_code} - {error_msg}")
                self.logger.error(f"Full response: {data}")
                print(f"\n❌ 微信API返回错误:")
                print(f"   错误代码: {error_code}")
                print(f"   错误信息: {error_msg}")
                return None
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request to create draft failed: {e}")
            print(f"\n❌ 创建草稿请求失败: {e}")
        return None

    def _load_reward_footer_template(self, project_root: Path) -> str:
        """加载奖励页脚模板"""
        template_path = project_root / "config/templates/wechat_reward_footer.html"
        if template_path.exists():
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                self.logger.warning(f"加载页脚模板失败: {e}")
        
        # 如果模板文件不存在，返回默认页脚
        return """
💡 获取完整深度版本

本文为精华浓缩版，完整版包含：
• 详细技术分析与数据解读  
• 独家调研资料与趋势预测
• 高清图表与参考资料合集

📧 获取方式：
1. 打赏本文任意金额
2. 截图发送到本公众号 + 您的邮箱地址
3. 24小时内发送完整资料包到您邮箱

示例回复格式："已打赏截图 + example@email.com"

---
🌐 完整文章请点击"阅读原文"
访问我们的博客获得最佳阅读体验
"""

    def generate_guide_file(self, project_root: Path, front_matter: Dict[str, Any], markdown_content: str) -> bool:
        self.logger.info(f"Generating manual guide file for: {front_matter.get('title', 'Untitled')}")
        print(f"\n📝 生成微信发布指南: {front_matter.get('title', 'Untitled')}")
        guide_dir = project_root / ".tmp/output/wechat/guides"
        guide_dir.mkdir(parents=True, exist_ok=True)
        safe_title = re.sub(r'[^\w\s-]', '', front_matter.get('title', 'draft')).strip()
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        guide_file = guide_dir / f"{safe_title}_{timestamp}_guide.md"

        final_content = self._transform_for_wechat(markdown_content)
        
        # 添加奖励页脚到内容末尾
        reward_footer = self._load_reward_footer_template(project_root)
        final_content_with_footer = final_content + "\n\n" + reward_footer

        # 获取封面图片信息
        cover_image = "N/A"
        if front_matter.get("image", {}).get("path"):
            cover_image = front_matter.get("image", {}).get("path")
        elif front_matter.get("header", {}).get("overlay_image"):
            cover_image = front_matter.get("header", {}).get("overlay_image")
        elif front_matter.get("header", {}).get("teaser"):
            cover_image = front_matter.get("header", {}).get("teaser")
        
        guide_text = f"""# 微信公众号发布指导

## 📋 文章信息
- **标题**: {front_matter.get('title', 'N/A')}
- **作者**: {front_matter.get('author', 'N/A')}
- **封面图片**: {cover_image}

## 📱 使用方法
1. 复制下方的"文章内容"
2. 打开微信公众号后台
3. 点击"写新图文"
4. 将内容粘贴到编辑器中
5. 手动上传封面图片
6. 根据需要调整格式和样式
7. 预览并发布

## 📝 文章内容
请复制以下内容到微信公众号编辑器：

{final_content_with_footer}

## 💡 格式提示
- 上述内容包含了完整的文章和奖励页脚
- 建议在微信编辑器中手动调整字体大小和颜色
- 可以使用微信编辑器的样式功能美化排版
- 记得上传封面图片以获得更好的视觉效果
- 奖励页脚已自动添加，支持读者获取完整资料包

## 🎁 内容变现说明
- 文章末尾已添加获取完整资料包的说明
- 用户打赏后发送截图和邮箱即可获得完整资料
- 确保在后台及时处理用户的打赏请求
"""
        
        try:
            # 保存指导文件
            print("\n📄 正在生成发布指南文件...")
            with open(guide_file, 'w', encoding='utf-8') as f:
                f.write(guide_text)
            self.logger.info(f"✅ Successfully generated guide file with reward footer: {guide_file}")
            self.logger.info(f"📂 微信指导文件位置: {guide_file}")
            print(f"\n✅ 微信发布指南生成成功！")
            print(f"📂 文件位置: {guide_file}")
            print(f"\n💡 使用提示:")
            print(f"   1. 打开生成的指南文件")
            print(f"   2. 复制其中的内容到微信公众号编辑器")
            print(f"   3. 手动上传封面图片并调整格式")
            print(f"   4. 预览并发布")
            return True
        except IOError as e:
            self.logger.error(f"Failed to write guide file: {e}")
            print(f"\n❌ 生成指南文件失败: {e}")
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
