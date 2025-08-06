#!/usr/bin/env python3
"""
YouTube播客生成器
将英文YouTube视频转换为中文播客和导读文章，用于英语学习
"""

import os
import re
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 第三方库导入
try:
    from gradio_client import Client
    import google.generativeai as genai
    from googleapiclient.discovery import build
except ImportError as e:
    print(f"请安装必要的依赖: pip install gradio-client google-generativeai google-api-python-client")
    raise e

# 可选TTS库导入
try:
    from elevenlabs import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from elevenlabs import ElevenLabs
    else:
        ElevenLabs = None

# Markdown和音频处理
try:
    from markdown_it import MarkdownIt
    from bs4 import BeautifulSoup
    # AudioSegment 在需要时动态导入
    MARKDOWN_AUDIO_TOOLS_AVAILABLE = True
except ImportError:
    MARKDOWN_AUDIO_TOOLS_AVAILABLE = False

# MoviePy动态导入
try:
    import moviepy.editor  # type: ignore
    MOVIEPY_AVAILABLE = True
except ImportError:
    moviepy = None  # type: ignore
    MOVIEPY_AVAILABLE = False


class YouTubePodcastGenerator:
    """YouTube播客生成器类"""
    
    def __init__(self, config: Dict[str, Any], pipeline=None):
        """
        初始化生成器
        
        Args:
            config: 配置字典，包含API密钥等
            pipeline: ContentPipeline实例，用于统一日志管理
        """
        self.config = config
        self.pipeline = pipeline
        self.setup_logging()
        self.setup_apis()
        
        # 文件路径配置
        self.audio_dir = "assets/audio"
        self.image_dir = "assets/images/posts"
        self.draft_dir = "_drafts"
        
        # 确保目录存在
        for directory in [self.audio_dir, self.image_dir, self.draft_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def setup_logging(self):
        """设置日志 - 使用系统统一日志配置"""
        if self.pipeline:
            # 使用pipeline的日志系统
            self.logger = self.pipeline
        else:
            # 备用日志配置
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
    
    def _log(self, message: str, level: str = "info", force: bool = False):
        """统一的日志处理方法"""
        if self.pipeline:
            # 使用pipeline的log方法
            self.pipeline.log(message, level, force)
        else:
            # 使用标准logging
            logger_method = getattr(self.logger, level, self.logger.info)
            logger_method(message)
    
    def setup_apis(self):
        """设置API连接"""
        # 设置Gemini API - 从环境变量或配置获取
        import os
        gemini_key = self.config.get('GEMINI_API_KEY') or os.getenv('GEMINI_API_KEY')
        
        if gemini_key:
            genai.configure(api_key=gemini_key)  # type: ignore
            # 使用与主系统一致的模型配置（从配置文件读取）
            model_name = "gemini-2.5-flash"  # 默认模型
            self.gemini_model = genai.GenerativeModel(model_name)  # type: ignore
            self._log(f"✅ Gemini配置完成 - 模型: {model_name}", "info")
        else:
            # 对于某些功能（如查看文件列表），不强制要求Gemini API
            self._log("⚠️ 未配置GEMINI_API_KEY，AI功能将不可用", "warning")
            self.gemini_model = None
        
        # 设置YouTube API - 支持OAuth和API Key两种认证方式
        youtube_configured = False
        
        # 尝试OAuth认证（用于上传）
        try:
            from googleapiclient.errors import HttpError
            import json
            
            oauth_token_path = "config/youtube_oauth_token.json"
            if os.path.exists(oauth_token_path):
                with open(oauth_token_path, 'r') as f:
                    token_data = json.load(f)
                    
                # 检查token是否有效（检查模板数据和占位符数据）
                template_patterns = [
                    'your-oauth-access-token-here', 'your_access_token_here'
                ]
                
                if (token_data.get('token', '').startswith('placeholder_token_') or
                    token_data.get('token') in template_patterns):
                    self._log("📋 检测到占位符或模板数据，使用API Key模式")
                    raise ValueError("OAuth token is placeholder or template data")
                    
                if 'access_token' in token_data or 'token' in token_data:
                    from google.auth.transport.requests import Request
                    from google.oauth2.credentials import Credentials
                    
                    creds = Credentials.from_authorized_user_info(token_data)
                    self._log(f"OAuth令牌状态: valid={creds.valid}, has_refresh={bool(creds.refresh_token)}")
                    
                    if creds.valid or creds.refresh_token:
                        if not creds.valid and creds.refresh_token:
                            self._log("🔄 刷新过期的OAuth令牌...")
                            creds.refresh(Request())
                            # 保存刷新后的token
                            with open(oauth_token_path, 'w') as f:
                                json.dump(json.loads(creds.to_json()), f, indent=2)
                            self._log("✅ OAuth令牌刷新成功")
                        
                        self.youtube = build('youtube', 'v3', credentials=creds)
                        self._log("✅ YouTube OAuth 配置完成 (支持上传)")
                        youtube_configured = True
                    else:
                        self._log("❌ OAuth令牌无效且无法刷新")
        except Exception as e:
            error_msg = str(e)
            if 'invalid_client' in error_msg:
                self._log(f"YouTube OAuth配置失败: OAuth客户端配置有误 - {e}")
                self._log("💡 建议: 请检查 config/youtube_oauth_token.json 或重新设置OAuth认证")
            else:
                self._log(f"YouTube OAuth配置失败: {e}")
            
        # 如果OAuth失败，尝试API Key（仅用于读取）
        if not youtube_configured:
            api_key = self.config.get('YOUTUBE_API_KEY') or os.getenv('YOUTUBE_API_KEY')
            self._log(f"🔍 尝试使用YouTube API Key: {'有效' if api_key and api_key.strip() else '无效或为空'}")
            
            if api_key and api_key.strip():
                try:
                    # 测试API Key是否有效
                    test_youtube = build('youtube', 'v3', developerKey=api_key)
                    # 进行一个简单的测试调用来验证API Key
                    test_request = test_youtube.videos().list(part="snippet", id="dQw4w9WgXcQ", maxResults=1)
                    test_response = test_request.execute()
                    self._log(f"🧪 API Key测试成功，响应项数: {len(test_response.get('items', []))}")
                    
                    self.youtube = test_youtube
                    self._log("✅ YouTube API Key 配置完成 (仅支持读取)")
                    youtube_configured = True
                except Exception as e:
                    self._log(f"YouTube API Key配置失败: {e}")
                    self._log("💡 可能的原因: API Key无效、配额不足或网络问题")
            else:
                self._log("❌ 未找到有效的 YOUTUBE_API_KEY")
            
        if not youtube_configured:
            self._log("⚠️ 未配置YouTube认证，将使用基础视频信息提取")
            self._log("💡 提示: 这可能导致视频信息获取不完整，建议配置YouTube API Key")
            self.youtube = None
        
        # 设置ElevenLabs API  
        if 'ELEVENLABS_API_KEY' in self.config and ELEVENLABS_AVAILABLE:
            try:
                # 检查API密钥是否为空
                api_key = self.config['ELEVENLABS_API_KEY']
                if not api_key or api_key.strip() == '':
                    raise ValueError("ELEVENLABS_API_KEY为空")
                    
                # 创建ElevenLabs客户端实例
                if ElevenLabs is not None:
                    self.elevenlabs_client = ElevenLabs(api_key=api_key.strip())
                else:
                    raise ImportError("ElevenLabs library not available")
                self.elevenlabs_available = True
                self._log("✅ ElevenLabs API 配置完成")
                
                # 检查配额状态
                self.check_elevenlabs_quota()
            except Exception as e:
                self._log(f"ElevenLabs API 配置失败: {e}", "warning")
                self.elevenlabs_available = False
                self.elevenlabs_client = None
        else:
            self.elevenlabs_available = False
            self.elevenlabs_client = None
            if not ELEVENLABS_AVAILABLE:
                self._log("💡 ElevenLabs库未安装，可运行 pip install elevenlabs 获得高质量语音")
            elif 'ELEVENLABS_API_KEY' not in self.config:
                self._log("💡 未配置ELEVENLABS_API_KEY，跳过ElevenLabs配置")
            else:
                self._log("⚠️ ElevenLabs配置不满足条件")
        
        # 设置Podcastfy客户端
        try:
            self.podcastfy_client = Client("thatupiso/Podcastfy.ai_demo")
            self._log("✅ Podcastfy 客户端连接成功")
            self.use_fallback = False
            
        except Exception as e:
            self._log(f"Podcastfy 客户端连接失败: {e}")
            self._log("将使用备用播客生成器")
            self.podcastfy_client = None
            self.use_fallback = True
    
    def extract_video_id(self, youtube_url: str) -> str:
        """
        从YouTube URL提取视频ID
        支持多种YouTube链接格式：
        - 标准视频: youtube.com/watch?v=VIDEO_ID
        - 短链接: youtu.be/VIDEO_ID 
        - 嵌入格式: youtube.com/embed/VIDEO_ID
        - YouTube Shorts: youtube.com/shorts/VIDEO_ID
        
        Args:
            youtube_url: YouTube视频链接
            
        Returns:
            视频ID
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
            r'youtube\.com\/shorts\/([^&\n?#]+)'  # 支持YouTube Shorts格式
        ]
        
        for pattern in patterns:
            match = re.search(pattern, youtube_url)
            if match:
                return match.group(1)
        
        raise ValueError(f"无法从URL提取视频ID: {youtube_url}")
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        获取YouTube视频信息
        
        Args:
            video_id: 视频ID
            
        Returns:
            视频信息字典
        """
        if self.youtube:
            try:
                # 首先尝试基础权限API调用
                request = self.youtube.videos().list(
                    part="snippet",
                    id=video_id
                )
                response = request.execute()
                
                if not response['items']:
                    raise ValueError(f"找不到视频ID: {video_id}")
                
                video = response['items'][0]
                snippet = video['snippet']
                
                # 尝试获取更多详细信息
                content_details = None
                duration = "未知时长"
                try:
                    # 尝试获取contentDetails（可能需要更高权限）
                    detailed_request = self.youtube.videos().list(
                        part="contentDetails,statistics",
                        id=video_id
                    )
                    detailed_response = detailed_request.execute()
                    if detailed_response['items']:
                        content_details = detailed_response['items'][0].get('contentDetails')
                        if content_details:
                            duration = self.parse_duration(content_details['duration'])
                except Exception as detail_error:
                    self._log(f"⚠️ 无法获取详细信息(权限限制): {detail_error}", "warning")
                    # 继续使用基础信息
                
                return {
                    'video_id': video_id,  # 确保video_id被正确传递
                    'title': snippet['title'],
                    'description': snippet['description'],
                    'channel_title': snippet['channelTitle'],
                    'published_at': snippet['publishedAt'],
                    'duration': duration,
                    'view_count': video.get('statistics', {}).get('viewCount', '0'),
                    'thumbnail_url': snippet['thumbnails']['maxres']['url'] if 'maxres' in snippet['thumbnails'] else snippet['thumbnails']['high']['url']
                }
            except Exception as e:
                self._log(f"YouTube API调用失败: {e}")
                # 降级到基础信息提取
                return self.get_basic_video_info(video_id)
        else:
            return self.get_basic_video_info(video_id)
    
    def get_basic_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        获取基础视频信息（无需API）
        
        Args:
            video_id: 视频ID
            
        Returns:
            基础视频信息
        """
        return {
            'video_id': video_id,  # 确保video_id被正确传递
            'title': f"YouTube视频 {video_id}",
            'description': "",
            'channel_title': "Unknown",
            'published_at': datetime.now().isoformat(),
            'duration': "未知时长",
            'view_count': "0",
            'thumbnail_url': f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        }
    
    def parse_duration(self, duration_str: str) -> str:
        """
        解析YouTube API返回的时长格式 (PT15M33S -> 15分33秒)
        
        Args:
            duration_str: ISO 8601时长格式
            
        Returns:
            中文时长描述
        """
        import re
        
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return "未知时长"
        
        hours, minutes, seconds = match.groups()
        hours = int(hours) if hours else 0
        minutes = int(minutes) if minutes else 0
        seconds = int(seconds) if seconds else 0
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分钟")
        if seconds > 0:
            parts.append(f"{seconds}秒")
        
        return "".join(parts) if parts else "0秒"
    
    def get_duration_seconds(self, duration_str: str) -> int:
        """
        解析YouTube API返回的时长格式，返回总秒数
        
        Args:
            duration_str: ISO 8601时长格式 (PT15M33S)
            
        Returns:
            总秒数
        """
        import re
        
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return 0  # 未知时长默认为0
        
        hours, minutes, seconds = match.groups()
        hours = int(hours) if hours else 0
        minutes = int(minutes) if minutes else 0
        seconds = int(seconds) if seconds else 0
        
        return hours * 3600 + minutes * 60 + seconds
    
    def calculate_adaptive_word_count(self, video_duration_seconds: int) -> int:
        """
        根据视频长度自适应计算播客字数
        
        Args:
            video_duration_seconds: 视频总秒数
            
        Returns:
            适合的播客字数
        """
        if video_duration_seconds <= 0:
            return 800  # 默认字数
        
        # 自适应规则：
        # - 1分钟以下: 400-600字（3-5轮对话）
        # - 1-3分钟: 600-800字（5-7轮对话）  
        # - 3-5分钟: 800-1000字（7-9轮对话）
        # - 5-10分钟: 1000-1200字（9-12轮对话）
        # - 10分钟以上: 1200-1500字（12-15轮对话）
        
        if video_duration_seconds <= 60:
            return 500  # 1分钟以下，短对话
        elif video_duration_seconds <= 180:  # 3分钟
            return 700
        elif video_duration_seconds <= 300:  # 5分钟
            return 900  
        elif video_duration_seconds <= 600:  # 10分钟
            return 1100
        else:
            return 1300  # 长视频
    
    def get_video_duration_seconds(self, video_info: Dict[str, Any]) -> int:
        """
        从视频信息中提取时长秒数
        
        Args:
            video_info: 视频信息字典
            
        Returns:
            视频时长（秒）
        """
        duration_str = video_info.get('duration', '')
        
        # 如果duration是ISO格式(PT1M30S)，直接解析
        if duration_str.startswith('PT'):
            return self.get_duration_seconds(duration_str)
        
        # 如果是中文格式(1分30秒)，解析
        if '分钟' in duration_str or '分' in duration_str or '秒' in duration_str:
            import re
            total_seconds = 0
            
            # 匹配小时
            hour_match = re.search(r'(\d+)小时', duration_str)
            if hour_match:
                total_seconds += int(hour_match.group(1)) * 3600
            
            # 匹配分钟
            minute_match = re.search(r'(\d+)分钟?', duration_str)
            if minute_match:
                total_seconds += int(minute_match.group(1)) * 60
            
            # 匹配秒
            second_match = re.search(r'(\d+)秒', duration_str)
            if second_match:
                total_seconds += int(second_match.group(1))
            
            return total_seconds
        
        return 0  # 无法解析，返回0
    
    def _generate_safe_filename(self, title: str, max_length: int = 50) -> str:
        """
        从标题生成安全的文件名
        
        Args:
            title: 原始标题
            max_length: 最大长度
            
        Returns:
            安全的文件名
        """
        # 移除特殊字符，只保留字母、数字、中文和连字符
        safe_title = re.sub(r'[^\w\u4e00-\u9fa5\s-]', '', title)
        
        # 将空格替换为连字符
        safe_title = re.sub(r'\s+', '-', safe_title.strip())
        
        # 移除多余的连字符
        safe_title = re.sub(r'-+', '-', safe_title)
        
        # 限制长度
        if len(safe_title) > max_length:
            safe_title = safe_title[:max_length].rstrip('-')
        
        # 如果结果为空，使用默认名称
        if not safe_title:
            safe_title = "youtube-video"
            
        return safe_title.lower()
    
    def _format_learning_items(self, items) -> str:
        """
        格式化学习项目（关键词汇、常用表达等）
        
        Args:
            items: 可能是字符串、数组或字典
            
        Returns:
            格式化后的字符串
        """
        try:
            if isinstance(items, dict):
                # 如果是字典，检查是否包含提示信息
                if 'tip' in items and 'words' in items:
                    # 新格式：{'tip': '...', 'words': [...]}
                    formatted_items = []
                    for word in items['words']:
                        formatted_items.append(f"**{word}**")
                    return f"{items['tip']}\n\n" + " | ".join(formatted_items)
                elif 'tip' in items and 'expressions' in items:
                    # 表达格式：{'tip': '...', 'expressions': [...]}
                    formatted_items = []
                    for expr in items['expressions']:
                        formatted_items.append(f"**{expr}**")
                    return f"{items['tip']}\n\n" + " | ".join(formatted_items)
                elif 'tip' in items and 'context' in items:
                    # 文化背景格式：{'tip': '...', 'context': [...]}
                    context_items = "\n".join([f"- {item}" for item in items['context']])
                    return f"{items['tip']}\n\n{context_items}"
                else:
                    # 其他字典格式，转换为键值对显示
                    return "\n".join([f"**{k}**: {v}" for k, v in items.items()])
            elif isinstance(items, list):
                # 如果是数组，格式化为带标记的列表
                return " | ".join([f"**{item}**" for item in items])
            elif isinstance(items, str):
                # 如果是字符串，直接返回
                return items
            else:
                # 其他情况，转换为字符串
                return str(items)
        except Exception:
            return "暂无相关内容"
    
    def generate_podcast_script(self, video_info: Dict[str, Any], 
                              target_language: str = "zh-CN",
                              conversation_style: str = "casual,informative") -> str:
        """
        生成NotebookLM风格的纯对话播客脚本
        """
        self._log("开始生成NotebookLM风格播客脚本")
        
        # 检查是否有足够的视频信息生成有意义的播客
        title = video_info.get('title', '')
        description = video_info.get('description', '')
        
        if (not description or len(description.strip()) < 50) and ('YouTube视频' in title or not title):
            self._log("⚠️ 视频信息不足，无法生成高质量播客", "warning")
            self._log("💡 建议：检查YouTube API权限或使用包含详细描述的视频", "warning")
            
            # 返回一个通用的错误提示脚本
            video_id = video_info.get('video_id', 'unknown')
            return f"""[A]: 抱歉，我们无法获取到这个YouTube视频的详细信息。视频ID是 {video_id}。

[B]: 是的，这可能是因为API权限限制或者视频不可访问。要生成高质量的播客内容，我们需要视频的标题、描述和其他详细信息。

[A]: 建议您检查一下YouTube API的配置，或者尝试使用其他包含完整信息的视频链接。

[B]: 没错，完整的视频信息可以帮助我们生成更准确、更有价值的播客内容。"""
        
        # 解析视频时长，智能调整播客长度
        duration_str = video_info.get('duration', '未知')
        try:
            import re
            duration_match = re.search(r'(\d+)分钟|(\d+):\d+', duration_str)
            if duration_match:
                video_minutes = int(duration_match.group(1) or duration_match.group(2))
                podcast_minutes = max(4, min(8, int(video_minutes * 0.7)))  # 更紧凑的时长
                word_count = podcast_minutes * 200  # 每分钟200字，更自然的语速
            else:
                podcast_minutes = 5
                word_count = 1000
        except:
            podcast_minutes = 5
            word_count = 1000
        
        # 根据目标语言生成不同的prompt
        if target_language.startswith("en"):
            prompt = f"""
Generate a {podcast_minutes}-minute English podcast dialogue about the YouTube video "{video_info['title']}".

Focus: Explain language points, cultural background, learning value
Audience: English language learners
Length: {word_count} words

Format:
[A]: Questions (focus on English learning points)
[B]: Answers (simple and clear, with examples)

Requirements:
- Start dialogue directly, no intro/outro
- Focus on English expressions and cultural background
- Conversational, natural dialogue style
- Provide practical learning suggestions

Output dialogue content directly:
        """
        elif target_language.startswith("ja"):
            prompt = f"""
YouTube動画「{video_info['title']}」について{podcast_minutes}分間の日本語学習ポッドキャスト対話を生成してください。

重点：言語のポイント、文化的背景、学習価値を説明
対象：日本語学習者
長さ：{word_count}文字

形式：
[A]: 質問（学習のポイントに焦点）
[B]: 回答（シンプルで分かりやすく、例を挙げて）

要求：
- 対話を直接開始、導入・終了なし
- 表現と文化的背景に重点
- 会話的で自然な対話スタイル
- 実用的な学習アドバイスを提供

対話内容を直接出力：
        """
        elif target_language.startswith("ko"):
            prompt = f"""
YouTube 동영상 "{video_info['title']}"에 대한 {podcast_minutes}분간의 한국어 학습 팟캐스트 대화를 생성하세요.

초점: 언어 포인트, 문화적 배경, 학습 가치 설명
대상: 한국어 학습자
길이: {word_count}자

형식:
[A]: 질문 (학습 포인트에 초점)
[B]: 답변 (간단하고 명확하며 예시 포함)

요구사항:
- 대화를 직접 시작, 도입/결말 없음
- 표현과 문화적 배경에 중점
- 대화적이고 자연스러운 대화 스타일
- 실용적인 학습 조언 제공

대화 내용을 직접 출력:
        """
        else:
            prompt = f"""
为YouTube视频《{video_info['title']}》生成{podcast_minutes}分钟中文学习播客对话。

重点：解释英语难点、文化背景、学习价值
对象：中国英语学习者
长度：{word_count}字

格式：
[A]: 提问（关注英语学习难点）
[B]: 解答（简单易懂，举例说明）

要求：
- 直接开始对话，无开场结束
- 重点讲解英语表达和文化背景
- 口语化、自然对话风格
- 提供实用学习建议

直接输出对话内容：
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            script = response.text
            self._log("播客脚本生成成功")
            return script
        except Exception as e:
            self._log(f"播客脚本生成失败: {e}")
            # 根据目标语言生成备用脚本
            if target_language.startswith("en"):
                return f"""
[A]: Today's video "{video_info['title']}" is quite interesting. What do you think is the main value for English learners?

[B]: I think the biggest value is learning authentic English expressions. These videos use natural vocabulary and have appropriate speaking pace.

[A]: So how should we approach learning from it? Watching directly might be challenging.

[B]: I suggest first understanding the main ideas through our guide, then watching the original English version. This approach works better for learning.

[A]: That's indeed a good learning method, helping us understand content while improving English skills.
"""
            elif target_language.startswith("ja"):
                return f"""
[A]: 今日の動画「{video_info['title']}」はとても興味深いですね。日本語学習者にとっての主な価値は何だと思いますか？

[B]: 最大の価値は本物の日本語表現を学習できることだと思います。このような動画は自然な語彙を使用し、適切な話速を持っています。

[A]: では、どのように学習に取り組むべきでしょうか？直接見るのは難しいかもしれません。

[B]: まず私たちのガイドを通じて大意を理解し、その後で日本語のオリジナル版を見ることをお勧めします。この方法の方が学習効果が高いです。

[A]: それは確かに良い学習方法ですね。内容を理解しながら日本語スキルも向上させることができます。
"""
            elif target_language.startswith("ko"):
                return f"""
[A]: 오늘 영상 "{video_info['title']}"이 정말 흥미롭네요. 한국어 학습자들에게 주요 가치는 무엇이라고 생각하세요?

[B]: 가장 큰 가치는 진정한 한국어 표현을 배울 수 있다는 것이라고 생각합니다. 이런 영상들은 자연스러운 어휘를 사용하고 적절한 말하기 속도를 가지고 있어요.

[A]: 그럼 어떻게 학습에 접근해야 할까요? 직접 보는 것은 어려울 수 있어요.

[B]: 먼저 우리 가이드를 통해 주요 내용을 이해한 후, 한국어 원본을 보는 것을 추천합니다. 이 방법이 학습 효과가 더 좋아요.

[A]: 정말 좋은 학습 방법이네요. 내용을 이해하면서 한국어 실력도 향상시킬 수 있어요.
"""
            else:
                return f"""
[A]: 今天这个视频《{video_info['title']}》很有意思，你觉得对英语学习者来说主要价值在哪里？

[B]: 我觉得最大的价值是可以学习到真实的英语表达。这类视频用词都比较地道，语速也适中。

[A]: 那具体应该怎么学呢？直接看可能有点困难。

[B]: 建议先听咱们的中文导读理解大意，然后再看英文原版，这样学习效果会更好。

[A]: 这确实是个不错的学习方法，既能了解内容又能提高英语水平。
"""

    def generate_local_audio(self, script: str, output_path: str, tts_engine: str = "gtts", dual_speaker: bool = True, target_language: str = "zh-CN") -> bool:
        """
        使用本地TTS生成音频，支持多种TTS引擎
        
        Args:
            script: 播客脚本
            output_path: 输出音频文件路径
            tts_engine: TTS引擎选择 ("gtts", "elevenlabs", "espeak", "pyttsx3")
            dual_speaker: 是否启用双人对话模式（仅ElevenLabs支持）
            target_language: 目标语言 ("zh-CN", "en-US", "ja-JP", "ko-KR")
        """
        # 检测是否包含对话格式
        has_dialogue_format = bool(re.search(r'[\[【].*?[\]】][:：]\s*', script) or 
                                 re.search(r'^[AB甲乙主持人嘉宾][:：]\s*', script, re.MULTILINE))
        
        # 决定是否使用双人模式
        use_dual_speaker = dual_speaker and has_dialogue_format and tts_engine == "elevenlabs"
        
        if use_dual_speaker:
            self._log("🎭 检测到对话格式，启用双人对话模式")
            # 保留对话标记用于双人模式解析
            clean_text = script
        else:
            self._log("🎙️ 使用单人播音模式")
            # 移除角色标签
            script = re.sub(r'\[.*?\]:\s*', '', script)
            clean_text = script

        # 对于非双人模式，进行文本清理
        if not use_dual_speaker:
            # 使用markdown-it-py和BeautifulSoup进行可靠的文本清理
            if MARKDOWN_AUDIO_TOOLS_AVAILABLE:
                try:
                    from markdown_it import MarkdownIt
                    from bs4 import BeautifulSoup
                    md = MarkdownIt()
                    html = md.render(clean_text)
                    soup = BeautifulSoup(html, 'html.parser')
                    clean_text = soup.get_text()
                except ImportError:
                    # Fallback to basic regex cleaning
                    self._log("Markdown/Audio tools import failed. Using basic text cleaning.")
                    clean_text = re.sub(r'<[^>]+>', '', clean_text)
            else:
                # Fallback to basic regex cleaning if libraries are not available
                self._log("Markdown/Audio tools not found. Using basic text cleaning.")
                clean_text = re.sub(r'<[^>]+>', '', clean_text) # Basic HTML tag removal

            # 移除多余的空白
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        self._log(f"🎧 开始音频生成 - 引擎: {tts_engine}, 模式: {'双人对话' if use_dual_speaker else '单人播音'}, 文本长度: {len(clean_text)}字符")
        
        # 对于超长文本，gTTS库会自动分块处理，无需人为截断
        if len(clean_text) > 5000:
            self._log("💡 检测到超长文本，gTTS将自动分块处理以保证完整性")
        
        # 1. 优先尝试ElevenLabs（最高音质）
        if tts_engine == "elevenlabs":
            if self._generate_elevenlabs_audio(clean_text, output_path, dual_speaker=use_dual_speaker, target_language=target_language):
                return True
            self._log("ElevenLabs失败，尝试其他引擎")
        
        # 2. 尝试Google TTS（高音质）
        if tts_engine == "gtts":
            if self._generate_gtts_audio(clean_text, output_path):
                return True
            self._log("Google TTS失败，尝试其他引擎")
        
        # 3. 尝试eSpeak（快速但音质一般）
        if tts_engine == "espeak" or tts_engine == "gtts":
            if self._generate_espeak_audio(clean_text, output_path):
                return True
            self._log("eSpeak TTS失败，尝试pyttsx3")
            
        # 4. 最后尝试pyttsx3（系统TTS）
        if self._generate_pyttsx3_audio(clean_text, output_path):
            return True
            
        self._log("所有TTS引擎都失败了", "error")
        return False
    
    def _generate_elevenlabs_audio(self, text: str, output_path: str, dual_speaker: bool = False, target_language: str = "zh-CN") -> bool:
        """使用ElevenLabs生成高质量AI语音（优化中文自然度）"""
        if not self.elevenlabs_available or not self.elevenlabs_client:
            self._log("ElevenLabs API未配置或库未安装")
            return False
            
        try:
            if dual_speaker:
                return self._generate_dual_speaker_audio(text, output_path, target_language)
            else:
                return self._generate_single_speaker_audio(text, output_path)
                
        except Exception as e:
            self._log(f"❌ ElevenLabs音频生成失败: {e}", "error")
            return False
    
    def _generate_single_speaker_audio(self, text: str, output_path: str) -> bool:
        """生成单人音频"""
        self._log("🎙️ 使用ElevenLabs生成单人音频（优化版）")
        
        # 为中文播客优化参数，减少机器人感
        if ELEVENLABS_AVAILABLE:
            from elevenlabs import VoiceSettings
            voice_settings = VoiceSettings(
                stability=0.35,  # 更低稳定性，增加自然变化，减少机器人感
                similarity_boost=0.85,  # 保持声音特征
                style=0.6,  # 增强表现力，让语调更自然
                use_speaker_boost=True
            )
        else:
            self._log("ElevenLabs库不可用")
            return False
        
        # 使用可靠的中文语音ID（已验证的公开语音）
        available_voice_ids = [
            "21m00Tcm4TlvDq8ikWAM",  # Rachel - 英文女声（多语言支持）
            "AZnzlk1XvdvUeBnXmlld",  # Domi - 多语言女声
            "EXAVITQu4vr4xnSDxMaL",  # Bella - 多语言女声
            "MF3mGyEYCl7XYWbV9V6O",  # Elli - 多语言女声
            "TxGEqnHWrfWFTfGW9XjX",  # Josh - 多语言男声
        ]
        
        # 优先使用第一个可用的语音ID
        voice_id = available_voice_ids[0]
        
        try:
            # 使用正确的ElevenLabs API调用方式
            if self.elevenlabs_client and hasattr(self.elevenlabs_client, 'text_to_speech'):
                audio_generator = self.elevenlabs_client.text_to_speech.convert(
                    voice_id=voice_id,
                    text=text,
                    model_id="eleven_multilingual_v2",
                    voice_settings=voice_settings
                )
            else:
                # 使用兼容的API方法
                try:
                    from elevenlabs import generate, Voice  # type: ignore
                    audio_generator = generate(
                        text=text,
                        voice=Voice(voice_id=voice_id),
                        model="eleven_multilingual_v2"
                    )
                except ImportError:
                    raise RuntimeError("ElevenLabs generate功能不可用，请检查库版本")
        except (AttributeError, ImportError):
            # 如果API方法不可用，抛出错误
            raise RuntimeError("ElevenLabs API方法不兼容，请检查库版本")
        
        # 保存音频文件
        with open(output_path, 'wb') as f:
            for chunk in audio_generator:
                f.write(chunk)
        
        self._log(f"✅ ElevenLabs单人音频生成成功: {output_path}")
        return True
    
    def _generate_dual_speaker_audio(self, text: str, output_path: str, language: str = "zh-CN") -> bool:
        """生成双人对话音频"""
        self._log("🎭 使用ElevenLabs生成双人对话音频")
        
        try:
            # 加载声音配置
            voice_config = self._load_voice_config()
            
            # 根据语言选择最佳组合
            selected_combination = self._select_best_voice_combination(voice_config, language)
            self._log(f"📻 使用语音组合: {selected_combination}")
            
            # 解析对话内容，分离不同说话者
            dialogue_segments = self._parse_dialogue(text)
            
            if len(dialogue_segments) < 2:
                self._log("⚠️ 文本不包含对话格式，切换到单人模式")
                return self._generate_single_speaker_audio(text, output_path)
            
            # 获取Pro账户优化的模型设置
            api_settings = voice_config.get('api_settings', {})
            model_id = api_settings.get('model_id', 'eleven_multilingual_v2')
            self._log(f"🤖 使用模型: {model_id}")
            
            # 生成每个对话片段的音频
            audio_segments = []
            total_segments = len(dialogue_segments)
            self._log(f"🎤 开始生成 {total_segments} 个对话片段...")
            
            for i, (speaker, segment_text) in enumerate(dialogue_segments):
                # 只显示关键进度点，减少日志冗余
                if i == 0 or i == total_segments - 1 or (i + 1) % 5 == 0:
                    progress = f"{i+1}/{total_segments}"
                    self._log(f"   🎤 生成对话片段 {progress}: {segment_text[:30]}...")
                elif i % 10 == 0:  # 每10个显示一次简化进度
                    self._log(f"   📊 进度: {i+1}/{total_segments} ({(i+1)*100//total_segments}%)")
                
                # 根据说话者选择声音配置
                voice_settings = self._get_speaker_settings(speaker, voice_config, language)
                voice_id = self._get_speaker_voice_id(speaker, voice_config, language)
                
                try:
                    # 使用正确的ElevenLabs API调用方式
                    if self.elevenlabs_client and hasattr(self.elevenlabs_client, 'text_to_speech'):
                        audio_generator = self.elevenlabs_client.text_to_speech.convert(
                            voice_id=voice_id,
                            text=segment_text,
                            model_id="eleven_multilingual_v2",
                            voice_settings=voice_settings
                        )
                    else:
                        # 使用兼容的API方法
                        try:
                            from elevenlabs import generate, Voice  # type: ignore
                            audio_generator = generate(
                                text=segment_text,
                                voice=Voice(voice_id=voice_id),
                                model="eleven_multilingual_v2"
                            )
                        except ImportError:
                            raise RuntimeError("ElevenLabs generate功能不可用，请检查库版本")
                except (AttributeError, ImportError):
                    # 如果API方法不可用，抛出错误
                    raise RuntimeError("ElevenLabs API方法不兼容，请检查库版本")
                
                # 收集音频数据
                audio_data = b''.join(chunk for chunk in audio_generator)
                audio_segments.append(audio_data)
                
                # 避免API限流
                import time
                time.sleep(0.5)
            
            # 合并音频片段
            if MARKDOWN_AUDIO_TOOLS_AVAILABLE:
                combined_audio = self._merge_dialogue_segments(audio_segments)
                if combined_audio:
                    combined_audio.export(output_path, format="wav")
                    self._log(f"✅ 双人对话音频生成成功: {output_path}")
                    return True
                else:
                    self._log("⚠️ 音频合并失败，切换到单人模式")
                    return self._generate_single_speaker_audio(text, output_path)
            else:
                self._log("⚠️ pydub未安装，无法合并音频，切换到单人模式")
                return self._generate_single_speaker_audio(text, output_path)
                
        except Exception as e:
            self._log(f"❌ 双人对话音频生成失败: {e}")
            self._log("🔄 切换到单人模式")
            return self._generate_single_speaker_audio(text, output_path)
    
    def _load_voice_config(self) -> Dict[str, Any]:
        """加载声音配置"""
        # 优先使用Pro账户配置
        pro_config_path = "config/elevenlabs_voices_pro.yml"
        standard_config_path = "config/elevenlabs_voices.yml"
        
        try:
            import yaml
            
            # 首先尝试加载Pro配置
            if Path(pro_config_path).exists():
                with open(pro_config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    self._log("✅ 使用ElevenLabs Pro账户优化配置")
                    return config.get('elevenlabs_voices', {})
            
            # 回退到标准配置
            elif Path(standard_config_path).exists():
                with open(standard_config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    self._log("✅ 使用标准ElevenLabs配置")
                    return config.get('elevenlabs_voices', {})
            
            else:
                self._log("⚠️ 未找到配置文件，使用默认配置")
                return self._get_default_voice_config()
                
        except ImportError:
            self._log("⚠️ PyYAML未安装，使用默认配置")
            return self._get_default_voice_config()
        except Exception as e:
            self._log(f"⚠️ 无法加载声音配置文件: {e}，使用默认配置")
            return self._get_default_voice_config()
    
    def _get_default_voice_config(self) -> Dict[str, Any]:
        """获取默认声音配置"""
        return {
            "voice_combinations": {
                "chinese_podcast": {
                    "speaker_a": {
                        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Rachel
                        "name": "Rachel",
                        "role": "主持人",
                        "settings": {
                            "stability": 0.4,
                            "similarity_boost": 0.8,
                            "style": 0.6
                        }
                    },
                    "speaker_b": {
                        "voice_id": "TxGEqnHWrfWFTfGW9XjX",  # Josh
                        "name": "Josh",
                        "role": "嘉宾",
                        "settings": {
                            "stability": 0.35,
                            "similarity_boost": 0.85,
                            "style": 0.5
                        }
                    }
                }
            }
        }
    
    def _parse_dialogue(self, text: str) -> List[Tuple[str, str]]:
        """解析对话文本，分离不同说话者"""
        import re
        
        # 常见的对话分隔符模式
        patterns = [
            r'^\[(.*?)\][：:]\s*(.+)$',      # [角色]: 内容
            r'^【(.*?)】[：:]\s*(.+)$',      # 【角色】: 内容
            r'^(A|甲|主持人)[：:]\s*(.+)$',  # A: 内容
            r'^(B|乙|嘉宾)[：:]\s*(.+)$',   # B: 内容
            r'^([^：:]+)[：:]\s*(.+)$',     # 通用格式: 说话者: 内容
        ]
        
        dialogue_segments: List[Tuple[str, str]] = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            matched = False
            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    speaker_raw = match.group(1).strip()
                    content = match.group(2).strip()
                    
                    # 标准化说话者标识
                    if speaker_raw in ['A', '甲', '主持人', '主播助手', '主持', '播音员']:
                        speaker = 'A'
                    elif speaker_raw in ['B', '乙', '嘉宾', '学习导师', '专家', '分析师']:
                        speaker = 'B'
                    else:
                        speaker = 'A' if len(dialogue_segments) % 2 == 0 else 'B'
                    
                    dialogue_segments.append((speaker, content))
                    matched = True
                    break
            
            if not matched:
                # 如果没有匹配到格式，交替分配给不同说话者
                speaker = 'A' if len(dialogue_segments) % 2 == 0 else 'B'
                dialogue_segments.append((speaker, line))
        
        return dialogue_segments
    
    def _get_speaker_settings(self, speaker: str, voice_config: Dict[str, Any], language: str = "chinese"):
        """获取说话者的语音设置"""
        try:
            from elevenlabs import VoiceSettings
        except ImportError:
            # 如果ElevenLabs不可用，返回None
            return None
        
        # 根据语言选择最佳语音组合
        combination_key = self._select_best_voice_combination(voice_config, language)
        combination = voice_config.get('voice_combinations', {}).get(combination_key, {})
        
        speaker_key = 'speaker_a' if speaker == 'A' else 'speaker_b'
        settings = combination.get(speaker_key, {}).get('settings', {})
        
        # 使用Pro账户优化设置
        default_settings = voice_config.get('api_settings', {}).get('default_settings', {})
        
        return VoiceSettings(
            stability=settings.get('stability', default_settings.get('stability', 0.35)),
            similarity_boost=settings.get('similarity_boost', default_settings.get('similarity_boost', 0.9)),
            style=settings.get('style', default_settings.get('style', 0.7)),
            use_speaker_boost=settings.get('use_speaker_boost', default_settings.get('use_speaker_boost', True))
        )
    
    def _select_best_voice_combination(self, voice_config: Dict[str, Any], language: str) -> str:
        """根据语言选择最佳语音组合"""
        combinations = voice_config.get('voice_combinations', {})
        recommendations = voice_config.get('usage_recommendations', {})
        
        # 标准化语言代码识别
        is_chinese = (language.startswith('zh') or 
                     language.lower() in ['chinese', 'zh-cn', 'zh-tw'])
        is_english = (language.startswith('en') or 
                     language.lower() in ['english', 'en-us', 'en-gb'])
        
        # 根据语言内容选择推荐组合
        if is_chinese:
            if 'chinese_content' in recommendations:
                primary = recommendations['chinese_content'].get('primary', 'chinese_podcast_pro')
                if primary in combinations:
                    return primary
            # 回退选项
            if 'chinese_podcast_pro' in combinations:
                return 'chinese_podcast_pro'
            else:
                return 'chinese_podcast'
                
        elif is_english:
            if 'english_content' in recommendations:
                primary = recommendations['english_content'].get('primary', 'english_podcast_pro')
                if primary in combinations:
                    return primary
            # 回退选项
            if 'english_podcast_pro' in combinations:
                return 'english_podcast_pro'
            else:
                return 'chinese_podcast'  # Rachel和Josh也适合英文
        
        # 默认选择（包括日语、韩语等其他语言）
        return 'chinese_podcast'
    
    def _get_speaker_voice_id(self, speaker: str, voice_config: Dict[str, Any], language: str = "chinese") -> str:
        """获取说话者的声音ID"""
        # 根据语言选择最佳语音组合
        combination_key = self._select_best_voice_combination(voice_config, language)
        combination = voice_config.get('voice_combinations', {}).get(combination_key, {})
        speaker_key = 'speaker_a' if speaker == 'A' else 'speaker_b'
        
        return combination.get(speaker_key, {}).get('voice_id', 
            "21m00Tcm4TlvDq8ikWAM" if speaker == 'A' else "TxGEqnHWrfWFTfGW9XjX")
    
    def _merge_dialogue_segments(self, audio_segments: List[bytes]):
        """合并对话音频片段"""
        try:
            from pydub import AudioSegment
            import io
        except ImportError:
            self._log("pydub未安装，无法合并音频片段")
            return None
        
        combined_audio = AudioSegment.empty()
        
        for i, audio_data in enumerate(audio_segments):
            # 将bytes数据转换为AudioSegment
            audio_io = io.BytesIO(audio_data)
            segment = AudioSegment.from_file(audio_io, format="mp3")
            
            # 添加适当的停顿
            if i > 0:
                pause = AudioSegment.silent(duration=600)  # 0.6秒停顿
                combined_audio += pause
            
            combined_audio += segment
        
        return combined_audio

    def _generate_gtts_audio(self, text: str, output_path: str) -> bool:
        """使用Google Text-to-Speech生成高质量音频并加速"""
        try:
            from gtts import gTTS
            
            self._log("尝试使用Google TTS生成音频")
            
            # 添加重试机制
            max_retries = 3
            temp_path = None
            for attempt in range(max_retries):
                try:
                    # 根据target_language设置语言
                    lang_code = 'zh-CN'  # 默认中文
                    if hasattr(self, 'current_target_language'):
                        if self.current_target_language.startswith('en'):
                            lang_code = 'en'
                        elif self.current_target_language.startswith('ja'):
                            lang_code = 'ja'
                        elif self.current_target_language.startswith('ko'):
                            lang_code = 'ko'
                    
                    # 创建gTTS对象
                    tts = gTTS(text=text, lang=lang_code, slow=False)
                    
                    # 保存到临时文件
                    temp_path = output_path.replace('.wav', '_temp.mp3')
                    tts.save(temp_path)
                    break  # 成功则退出重试循环
                    
                except Exception as e:
                    if attempt < max_retries - 1:
                        self._log(f"Google TTS第{attempt + 1}次尝试失败: {e}，{3-attempt}秒后重试...")
                        import time
                        time.sleep(3)
                        continue
                    else:
                        raise e
            
            if temp_path is None:
                raise Exception("无法生成临时音频文件")
            
            # 加速音频
            if MARKDOWN_AUDIO_TOOLS_AVAILABLE:
                try:
                    from pydub import AudioSegment
                    self._log("加速音频至1.5倍速")
                    sound = AudioSegment.from_mp3(temp_path)
                    fast_sound = sound.speedup(playback_speed=1.5)
                    
                    # 导出加速后的音频
                    fast_sound.export(temp_path, format="mp3")
                except ImportError:
                    self._log("pydub未安装，跳过音频加速")

            # 如果需要WAV格式，转换音频格式
            if output_path.endswith('.wav'):
                self._convert_audio_format(temp_path, output_path)
                os.remove(temp_path)  # 删除临时文件
            else:
                # 直接重命名为最终文件
                os.rename(temp_path, output_path)
            
            if os.path.exists(output_path):
                self._log(f"Google TTS音频生成成功: {output_path}")
                return True
            else:
                self._log("Google TTS未能创建音频文件", "error")
                return False
                
        except ImportError:
            self._log("gtts库未安装，跳过Google TTS。安装命令: pip install gtts pygame")
            return False
        except Exception as e:
            self._log(f"Google TTS生成失败: {e}")
            return False
    
    def _generate_espeak_audio(self, text: str, output_path: str) -> bool:
        """
        使用eSpeak生成音频
        """
        try:
            import subprocess
            
            self._log("尝试使用eSpeak TTS生成音频")
            
            # 尝试不同的音频格式
            for audio_format in ['wav', 'mp3']:
                try:
                    output_file = output_path.replace('.wav', f'.{audio_format}')
                    cmd = [
                        'espeak', 
                        '-v', 'zh',  # 使用中文语音
                        '-s', '150',  # 语速
                        '-a', '80',   # 音量
                        '-w', output_file,  # 输出到文件
                        text
                    ]
                    
                    self._log(f"执行eSpeak命令: {' '.join(cmd[:6])}...")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0 and os.path.exists(output_file):
                        self._log(f"eSpeak音频生成成功: {output_file}")
                        # 如果生成的不是目标格式，重命名
                        if output_file != output_path:
                            os.rename(output_file, output_path)
                        return True
                    else:
                        self._log(f"eSpeak生成失败，返回码: {result.returncode}")
                        if result.stderr:
                            self._log(f"eSpeak错误: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    self._log("eSpeak执行超时")
                except Exception as e:
                    self._log(f"eSpeak格式{audio_format}失败: {e}")
                    continue
                    
            return False
            
        except Exception as e:
            self._log(f"eSpeak生成失败: {e}")
            return False
    
    def _generate_pyttsx3_audio(self, text: str, output_path: str) -> bool:
        """
        使用pyttsx3生成音频
        """
        try:
            import pyttsx3
            
            self._log("尝试使用pyttsx3 TTS生成音频")
            
            # 初始化TTS引擎
            engine = pyttsx3.init()
            
            # 设置语音属性
            voices = engine.getProperty('voices')
            chinese_voice_found = False
            
            if voices is not None:
                try:
                    voices_list = list(voices) if hasattr(voices, '__iter__') else []  # type: ignore
                    self._log(f"可用语音数量: {len(voices_list)}")
                except (TypeError, AttributeError):
                    self._log("无法获取语音列表")
                    voices_list = []
                    
                for i, voice in enumerate(voices_list):
                    if hasattr(voice, 'name') and hasattr(voice, 'id'):
                        self._log(f"语音{i}: {voice.name} - {voice.id}", "debug")
                        # 更宽松的中文语音匹配
                        if any(keyword in voice.name.lower() for keyword in ['chinese', 'mandarin', 'zh', 'china']):
                            engine.setProperty('voice', voice.id)
                            chinese_voice_found = True
                            self._log(f"选择中文语音: {voice.name}")
                            break
            
            if not chinese_voice_found:
                self._log("未找到中文语音，使用默认语音")
            
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.8)
            
            # 生成音频
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
            if os.path.exists(output_path):
                self._log(f"pyttsx3音频生成成功: {output_path}")
                return True
            else:
                self._log("pyttsx3未能创建音频文件")
                return False
                
        except ImportError:
            self._log("pyttsx3库未安装，跳过。安装命令: pip install pyttsx3")
            return False
        except Exception as e:
            self._log(f"pyttsx3生成失败: {e}")
            return False
    
    def _convert_audio_format(self, input_path: str, output_path: str) -> bool:
        """转换音频格式（MP3转WAV等）"""
        try:
            from pydub import AudioSegment
            
            # 读取输入音频
            audio = AudioSegment.from_file(input_path)
            
            # 导出为目标格式
            audio.export(output_path, format="wav")
            
            self._log(f"音频格式转换成功: {input_path} -> {output_path}")
            return True
            
        except ImportError:
            self._log("pydub库未安装，无法转换音频格式。安装命令: pip install pydub")
            # 如果无法转换，直接复制文件
            import shutil
            shutil.copy2(input_path, output_path)
            return True
        except Exception as e:
            self._log(f"音频格式转换失败: {e}")
            return False

    def generate_podcast(self, youtube_url: str, custom_style: str = "casual,informative", 
                        target_language: str = "zh-CN", word_count: int = 1200) -> str:
        """
        生成播客音频
        
        Args:
            youtube_url: YouTube视频链接
            custom_style: 播客风格
            target_language: 目标语言 ("zh-CN", "en-US", "ja-JP", "ko-KR")
            word_count: 播客字数，会影响对话长度
            
        Returns:
            生成的音频文件路径
        """
        self._log(f"开始生成播客: {youtube_url}")
        
        # 如果Podcastfy不可用，使用备用方法
        if self.use_fallback or not self.podcastfy_client:
            self._log("使用备用播客生成方法")
            return "fallback_mode"  # 标识使用备用模式
        
        try:
            # 使用全局清理函数清理所有输入参数
            clean_url = self._clean_string_aggressive(youtube_url)
            clean_style = self._clean_string_aggressive(custom_style)
            clean_language = self._clean_string_aggressive(target_language)
            # 根据目标语言生成不同的指令
            if target_language.startswith("en"):
                clean_instructions = self._clean_string_aggressive(f"Generate an English podcast about this YouTube video for language learners, target language: {clean_language}")
            elif target_language.startswith("ja"):
                clean_instructions = self._clean_string_aggressive(f"日本語でYouTube動画についてのポッドキャストを生成してください、対象言語: {clean_language}")
            elif target_language.startswith("ko"):
                clean_instructions = self._clean_string_aggressive(f"이 YouTube 동영상에 대한 한국어 팟캐스트를 생성하세요, 대상 언어: {clean_language}")
            else:
                clean_instructions = self._clean_string_aggressive(f"请生成一个关于YouTube视频的中文播客，目标语言是{clean_language}，内容要适合英语学习者收听")
            
            self._log(f"🔍 清理后的URL: {clean_url}")
            self._log(f"🔍 URL长度: {len(clean_url)}, URL字符检查: {repr(clean_url)}")
            self._log(f"🎭 清理后的风格: {clean_style}")
            
            # 额外验证所有参数不包含非打印字符
            all_params = {
                'clean_url': clean_url,
                'clean_style': clean_style,
                'clean_language': clean_language,
                'clean_instructions': clean_instructions,
                'gemini_key': self._clean_string_aggressive(self.config['GEMINI_API_KEY'])[:10] + "...",
                'elevenlabs_key': self._clean_string_aggressive(self.config.get('ELEVENLABS_API_KEY', ''))[:10] + "..."
            }
            
            # 检查每个参数是否包含真正的控制字符（排除中文字符）
            for param_name, param_value in all_params.items():
                if param_value:
                    # 只检查真正的控制字符和特殊字符，排除正常的中文字符
                    problematic_chars = [c for c in str(param_value) if ord(c) < 32 and c not in '\n\r\t']
                    if problematic_chars:
                        self._log(f"⚠️ 参数{param_name}包含控制字符: {[ord(c) for c in problematic_chars[:5]]}", "warning")
            
            # 额外的URL验证
            if '\\n' in repr(clean_url) or '\\r' in repr(clean_url):
                self._log("⚠️ 检测到URL中仍有换行符，进行二次清理", "warning")
                clean_url = clean_url.replace('\n', '').replace('\r', '').replace('\t', '').strip()
                self._log(f"🔍 二次清理后的URL: {repr(clean_url)}")
            
            # 验证所有参数
            all_params = {
                'urls_input': clean_url,
                'conversation_style': clean_style,
                'user_instructions': clean_instructions
            }
            
            for param_name, param_value in all_params.items():
                if any(ord(c) < 32 or ord(c) == 127 for c in str(param_value)):
                    self._log(f"⚠️ 参数{param_name}包含控制字符: {repr(param_value)}", "warning")
            
            # 修改Podcastfy参数，实现NotebookLM风格的纯对话
            notebooklm_instructions = f"生成NotebookLM风格的纯对话播客，要求：1. 绝对禁止开场白、介绍、总结、结束语；2. 只能是两个人的自然对话，一问一答；3. 像真实朋友聊天，深入讨论视频内容；4. 不要任何欢迎来到播客等话语；5. 直接开始讨论，自然结束；6. 保持口语化、真实、有深度的对话风格；目标语言：{target_language}"
            
            # 清理notebooklm_instructions并验证所有即将传递的参数
            clean_instructions = self._clean_string_aggressive(notebooklm_instructions)
            
            # 完整的参数验证
            final_params = {
                'urls_input': clean_url,
                'gemini_key': self._clean_string_aggressive(self.config['GEMINI_API_KEY']),
                'user_instructions': clean_instructions,
                'conversation_style': self._clean_string_aggressive("natural,deep,conversational"),
                'roles_person1': self._clean_string_aggressive("A"),
                'roles_person2': self._clean_string_aggressive("B"),
                'dialogue_structure': self._clean_string_aggressive("对话"),
                'podcast_name': self._clean_string_aggressive(""),
                'podcast_tagline': self._clean_string_aggressive("")
            }
            
            for param_name, param_value in final_params.items():
                if any(ord(c) < 32 or ord(c) == 127 for c in str(param_value)):
                    self._log(f"⚠️ 最终参数{param_name}包含控制字符: {repr(param_value)}", "warning")
                    # 对于URL参数，记录详细信息
                    if param_name == 'urls_input':
                        for i, char in enumerate(str(param_value)):
                            if ord(char) < 32 or ord(char) == 127:
                                self._log(f"   位置{i}: {repr(char)} (ASCII {ord(char)})", "warning")
            
            result = self.podcastfy_client.predict(
                text_input="",
                urls_input=final_params['urls_input'],
                pdf_files=[],
                image_files=[],
                gemini_key=final_params['gemini_key'],
                openai_key="",  # 使用Edge TTS，不需要OpenAI密钥
                elevenlabs_key=self._clean_string_aggressive(self.config.get('ELEVENLABS_API_KEY', "")),
                word_count=word_count,  # 根据视频长度自适应调整
                conversation_style=final_params['conversation_style'],
                roles_person1=final_params['roles_person1'],
                roles_person2=final_params['roles_person2'],
                dialogue_structure=final_params['dialogue_structure'],
                podcast_name=final_params['podcast_name'],
                podcast_tagline=final_params['podcast_tagline'],
                tts_model="elevenlabs",  # 优先使用ElevenLabs获得最佳音质
                creativity_level=0.8,  # 增加创造力，使对话更自然
                user_instructions=final_params['user_instructions'],
                api_name="/process_inputs"
            )
            
            # result应该包含生成的音频文件路径
            if result and len(result) > 0:
                audio_path = result[0]  # 通常第一个元素是音频文件路径
                self._log(f"播客生成成功: {audio_path}")
                return audio_path
            else:
                raise Exception("播客生成失败，未返回音频文件")
                
        except Exception as e:
            self._log(f"Podcastfy播客生成失败: {e}")
            self._log("切换到备用播客生成方法")
            self.use_fallback = True
            return "fallback_mode"
    
    def generate_content_guide(self, video_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成中文导读内容
        
        Args:
            video_info: 视频信息
            
        Returns:
            导读内容字典
        """
        self._log("开始生成中文导读")
        
        # 简化的导读生成prompt
        prompt = f"""
为YouTube视频生成英语学习导读：

视频：{video_info['title']} | {video_info['channel_title']} | {video_info['duration']}

请生成JSON格式：
{{
  "title": "【英语学习】{video_info['title'][:20]}的简短标题",
  "excerpt": "学习价值描述(50字内)",
  "outline": ["3-4个要点"],
  "learning_tips": {{
    "vocabulary": ["5个关键英语词汇"],
    "expressions": ["3个实用表达"],
    "cultural_context": "1-2句文化背景"
  }},
  "tags": ["英语学习", "相关话题"],
  "difficulty_level": "初级/中级/高级"
}}

重点：实用性、易理解、有学习价值
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            content_text = response.text
            
            # 提取JSON内容
            json_match = re.search(r'\{.*\}', content_text, re.DOTALL)
            if json_match:
                content_data = json.loads(json_match.group())
                self._log("导读内容生成成功")
                return content_data
            else:
                raise ValueError("无法解析Gemini返回的JSON内容")
                
        except Exception as e:
            self._log(f"导读生成失败: {e}")
            # 返回默认内容
            return {
                "title": f"【英语学习】{video_info['title'][:20]}",
                "excerpt": "通过中文播客导读，轻松理解英文YouTube内容",
                "outline": [
                    "🎯 视频核心观点总结",
                    "🌍 全球视野角度分析", 
                    "💡 关键概念解读",
                    "🤔 值得思考的问题"
                ],
                "learning_tips": {
                    "vocabulary": ["关键词汇1", "关键词汇2", "关键词汇3"],
                    "expressions": ["常用表达1", "常用表达2"],
                    "cultural_context": "相关文化背景知识"
                },
                "tags": ["英语学习", "YouTube", "全球视野"],
                "difficulty_level": "中级"
            }
    
    def download_thumbnail(self, thumbnail_url: str, video_info: Dict[str, Any]) -> str:
        """
        下载视频缩略图
        
        Args:
            thumbnail_url: 缩略图URL
            video_info: 视频信息字典
            
        Returns:
            本地缩略图路径
        """
        try:
            # 创建按日期组织的目录
            today = datetime.now()
            date_dir = os.path.join(self.image_dir, str(today.year), f"{today.month:02d}")
            os.makedirs(date_dir, exist_ok=True)
            
            # 生成文件名
            # 使用有意义的文件名而非视频ID
            safe_title = self._generate_safe_filename(video_info['title'])
            thumbnail_filename = f"youtube-{today.strftime('%Y%m%d')}-{safe_title}-thumbnail.jpg"
            thumbnail_path = os.path.join(date_dir, thumbnail_filename)
            
            # 下载图片
            response = requests.get(thumbnail_url, stream=True)
            response.raise_for_status()
            
            with open(thumbnail_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self._log(f"缩略图下载成功: {thumbnail_path}")
            return thumbnail_path
            
        except Exception as e:
            self._log(f"缩略图下载失败: {e}")
            return ""
    
    def create_audio_video(self, audio_path: str, thumbnail_path: str, output_path: str) -> bool:
        """
        将音频和缩略图合成为视频文件，用于YouTube上传
        
        Args:
            audio_path: 音频文件路径
            thumbnail_path: 缩略图路径
            output_path: 输出视频路径
            
        Returns:
            是否成功生成视频
        """
        try:
            
            # 检查文件是否存在
            if not os.path.exists(audio_path):
                self._log(f"音频文件不存在: {audio_path}")
                return False
                
            if not os.path.exists(thumbnail_path):
                self._log(f"缩略图不存在: {thumbnail_path}")
                return False
            
            self._log("开始生成音频视频文件")
            
            # 第一步：音频预处理和压缩优化
            optimized_audio_path = self._optimize_audio_for_video(audio_path)
            if not optimized_audio_path:
                self._log("音频优化失败，使用原始音频")
                optimized_audio_path = audio_path
            
            # 使用ffmpeg将音频和图片合成视频
            ffmpeg_cmd = [
                'ffmpeg', '-y',  # -y 覆盖输出文件
                '-loop', '1',  # 循环图片
                '-i', thumbnail_path,  # 输入图片
                '-i', optimized_audio_path,  # 输入优化后的音频
                '-c:v', 'libx264',  # 视频编码
                '-c:a', 'aac',  # 音频编码 (会重新编码优化过的音频)
                '-b:a', '96k',  # 降低音频比特率以进一步压缩
                '-pix_fmt', 'yuv420p',  # 像素格式
                '-shortest',  # 以最短的输入为准
                output_path
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self._log(f"✅ 音频视频生成成功: {output_path}")
                return True
            else:
                self._log(f"ffmpeg错误: {result.stderr}")
                # 尝试备用方案 - 使用moviepy
                return self._create_audio_video_fallback(audio_path, thumbnail_path, output_path)
                
        except subprocess.TimeoutExpired:
            self._log("ffmpeg执行超时，尝试备用方案")
            return self._create_audio_video_fallback(audio_path, thumbnail_path, output_path)
        except FileNotFoundError:
            self._log("ffmpeg未安装，使用备用方案")
            return self._create_audio_video_fallback(audio_path, thumbnail_path, output_path)
        except Exception as e:
            self._log(f"音频视频生成失败: {e}")
            return False
    
    def _create_audio_video_without_optimization(self, audio_path: str, thumbnail_path: str, output_path: str) -> bool:
        """
        将已优化的音频和缩略图合成为视频文件，不进行重复优化
        
        Args:
            audio_path: 已优化的音频文件路径
            thumbnail_path: 缩略图路径
            output_path: 输出视频路径
            
        Returns:
            是否成功生成视频
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(audio_path):
                self._log(f"音频文件不存在: {audio_path}")
                return False
                
            if not os.path.exists(thumbnail_path):
                self._log(f"缩略图不存在: {thumbnail_path}")
                return False
            
            self._log("开始生成音频视频文件（使用已优化音频）")
            
            # 直接使用已优化的音频，不再重复优化
            # 使用ffmpeg将音频和图片合成视频
            ffmpeg_cmd = [
                'ffmpeg', '-y',  # -y 覆盖输出文件
                '-loop', '1',  # 循环图片
                '-i', thumbnail_path,  # 输入图片
                '-i', audio_path,  # 输入已优化的音频
                '-c:v', 'libx264',  # 视频编码
                '-c:a', 'copy',  # 音频直接复制，不重新编码
                '-pix_fmt', 'yuv420p',  # 像素格式
                '-shortest',  # 以最短的输入为准
                output_path
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self._log(f"✅ 音频视频生成成功: {output_path}")
                return True
            else:
                self._log(f"ffmpeg错误: {result.stderr}")
                # 尝试备用方案 - 使用moviepy
                return self._create_audio_video_fallback(audio_path, thumbnail_path, output_path)
                
        except subprocess.TimeoutExpired:
            self._log("ffmpeg执行超时，尝试备用方案")
            return self._create_audio_video_fallback(audio_path, thumbnail_path, output_path)
        except FileNotFoundError:
            self._log("ffmpeg未安装，使用备用方案")
            return self._create_audio_video_fallback(audio_path, thumbnail_path, output_path)
        except Exception as e:
            self._log(f"音频视频生成失败: {e}")
            return False
    
    def _optimize_audio_for_video(self, audio_path: str) -> Optional[str]:
        """
        优化音频文件以减小视频大小
        使用高质量音频压缩参数，包含音频处理链
        
        Args:
            audio_path: 原始音频文件路径
            
        Returns:
            优化后的音频文件路径，失败返回None
        """
        try:
            # 生成优化后的音频文件路径
            path_obj = Path(audio_path)
            optimized_filename = f"{path_obj.stem}_optimized.mp3"
            optimized_path = path_obj.parent / optimized_filename
            
            self._log(f"🔄 开始优化音频文件: {audio_path}")
            
            # 使用专业的音频压缩命令
            # 音频处理链说明：
            # - highpass=100: 高通滤波器，去除100Hz以下的低频噪音
            # - lowpass=7000: 低通滤波器，去除7kHz以上的高频，适合语音
            # - compand: 动态压缩，平衡音量
            # - volume=1.8: 增加音量
            # - loudnorm: 标准化响度，符合播放标准
            audio_filter = (
                "highpass=f=100,"
                "lowpass=f=7000,"
                "compand=attacks=0.05:decays=0.2:points=-80/-80|-62/-62|-26/-26|-15/-15|-10/-8|0/-7,"
                "volume=1.8,"
                "loudnorm=I=-18:LRA=7:TP=-2"
            )
            
            ffmpeg_cmd = [
                'ffmpeg', '-y',  # 覆盖输出文件
                '-i', audio_path,  # 输入文件
                '-af', audio_filter,  # 音频滤镜链
                '-codec:a', 'libmp3lame',  # MP3编码器
                '-b:a', '96k',  # 96kbps比特率，适合语音
                '-ar', '44100',  # 采样率
                '-ac', '2',  # 双声道
                str(optimized_path)
            ]
            
            self._log("执行音频优化命令...")
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and optimized_path.exists():
                # 检查文件大小压缩效果
                original_size = Path(audio_path).stat().st_size
                optimized_size = optimized_path.stat().st_size
                compression_ratio = (1 - optimized_size / original_size) * 100
                
                self._log(f"✅ 音频优化成功:")
                self._log(f"   原始大小: {original_size / 1024 / 1024:.1f}MB")
                self._log(f"   优化大小: {optimized_size / 1024 / 1024:.1f}MB")
                self._log(f"   压缩率: {compression_ratio:.1f}%")
                
                return str(optimized_path)
            else:
                self._log(f"音频优化失败: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            self._log("音频优化超时")
            return None
        except FileNotFoundError:
            self._log("ffmpeg未找到，跳过音频优化")
            return None
        except Exception as e:
            self._log(f"音频优化异常: {e}")
            return None
    
    def _create_audio_video_fallback(self, audio_path: str, thumbnail_path: str, output_path: str) -> bool:
        """使用moviepy作为备用方案生成音频视频"""
        try:
            # 动态导入moviepy以避免必须依赖
            if not MOVIEPY_AVAILABLE:
                raise ImportError("MoviePy not available")
            from moviepy.editor import AudioFileClip, ImageClip  # type: ignore
            
            self._log("使用moviepy生成音频视频")
            
            # 加载音频和图片
            audio_clip = AudioFileClip(audio_path)
            image_clip = ImageClip(thumbnail_path).set_duration(audio_clip.duration)
            
            # 设置视频分辨率
            image_clip = image_clip.resize(height=720)  # 720p
            
            # 合成视频
            video_clip = image_clip.set_audio(audio_clip)
            
            # 导出视频
            video_clip.write_videofile(
                output_path,
                fps=1,  # 静态图片，低帧率即可
                codec='libx264',
                audio_codec='aac'
            )
            
            # 清理资源
            audio_clip.close()
            image_clip.close()
            video_clip.close()
            
            self._log(f"✅ moviepy音频视频生成成功: {output_path}")
            return True
            
        except ImportError:
            self._log("moviepy未安装，无法生成音频视频。请安装: pip install moviepy")
            return False
        except Exception as e:
            self._log(f"moviepy生成失败: {e}")
            return False
    
    def list_audio_files(self) -> List[str]:
        """
        列出assets/audio目录中的所有音频文件
        
        Returns:
            音频文件路径列表
        """
        audio_dir = Path(self.audio_dir)
        if not audio_dir.exists():
            self._log(f"音频目录不存在: {audio_dir}")
            return []
        
        # 支持的音频格式
        audio_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac']
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(audio_dir.glob(f"*{ext}"))
        
        # 按修改时间排序（最新的在前）
        audio_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        return [str(f) for f in audio_files]
    
    def select_audio_file(self) -> Optional[str]:
        """
        让用户选择要上传的音频文件
        
        Returns:
            选择的音频文件路径，如果取消则返回None
        """
        audio_files = self.list_audio_files()
        
        if not audio_files:
            print("❌ 未找到任何音频文件")
            return None
        
        print("\n🎵 可上传的音频文件:")
        for i, file_path in enumerate(audio_files, 1):
            file_obj = Path(file_path)
            file_size = file_obj.stat().st_size / (1024 * 1024)  # MB
            mod_time = datetime.fromtimestamp(file_obj.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            print(f"  {i}. {file_obj.name} ({file_size:.1f}MB, {mod_time})")
        
        print("  0. 取消")
        
        try:
            choice = input(f"\n请选择音频文件 (1-{len(audio_files)}): ").strip()
            
            if choice == '0':
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(audio_files):
                selected_file = audio_files[idx]
                print(f"✅ 已选择: {Path(selected_file).name}")
                return selected_file
            else:
                print("❌ 无效选择")
                return None
                
        except (ValueError, KeyboardInterrupt):
            print("❌ 操作取消")
            return None
    
    def select_cover_image(self, audio_file_path: str) -> Optional[str]:
        """
        为音频文件选择或生成封面图片
        
        Args:
            audio_file_path: 音频文件路径
            
        Returns:
            封面图片路径，如果取消则返回None
        """
        print("\n🖼️ 封面图片选项:")
        print("  1. 使用默认播客封面")
        print("  2. 从现有图片中选择")
        print("  3. 生成纯色背景封面")
        print("  0. 取消")
        
        try:
            choice = input("\n请选择封面类型 (1-3): ").strip()
            
            if choice == '0':
                return None
            elif choice == '1':
                return self._create_default_cover(audio_file_path)
            elif choice == '2':
                return self._select_existing_image()
            elif choice == '3':
                return self._create_simple_cover(audio_file_path)
            else:
                print("❌ 无效选择，使用默认封面")
                return self._create_default_cover(audio_file_path)
                
        except (ValueError, KeyboardInterrupt):
            print("❌ 操作取消")
            return None
    
    def _create_default_cover(self, audio_file_path: str) -> str:
        """
        创建默认播客封面
        
        Args:
            audio_file_path: 音频文件路径
            
        Returns:
            封面图片路径
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            self._log("PIL未安装，使用纯色封面。请安装: pip install pillow")
            return self._create_solid_color_cover(audio_file_path)
        
        audio_name = Path(audio_file_path).stem
        cover_path = f"assets/images/posts/{datetime.now().strftime('%Y/%m')}/{audio_name}-cover.jpg"
        
        # 确保目录存在
        Path(cover_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 创建720x720的正方形封面
        img = Image.new('RGB', (720, 720), color='#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        # 添加渐变背景效果
        for y in range(720):
            alpha = y / 720
            color = (
                int(26 + alpha * 20),    # R: 26 -> 46
                int(32 + alpha * 30),    # G: 32 -> 62  
                int(46 + alpha * 40)     # B: 46 -> 86
            )
            draw.line([(0, y), (720, y)], fill=color)
        
        # 添加文字
        try:
            # 尝试使用系统字体
            font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
            font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            try:
                font_large = ImageFont.truetype("arial.ttf", 48)
                font_small = ImageFont.truetype("arial.ttf", 24)
            except:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()
        
        # 绘制标题
        title = "Audio Podcast"
        subtitle = audio_name.replace('-', ' ').title()
        
        # 居中绘制文字
        title_bbox = draw.textbbox((0, 0), title, font=font_large)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((720 - title_width) // 2, 280), title, fill='white', font=font_large)
        
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=font_small)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        draw.text(((720 - subtitle_width) // 2, 350), subtitle, fill='#cccccc', font=font_small)
        
        # 保存图片
        img.save(cover_path, 'JPEG', quality=85)
        self._log(f"✅ 默认封面创建成功: {cover_path}")
        
        return cover_path
    
    def _create_solid_color_cover(self, audio_file_path: str) -> str:
        """
        创建纯色封面（PIL不可用时的备用方案）
        
        Args:
            audio_file_path: 音频文件路径
            
        Returns:
            封面图片路径
        """
        # 使用ffmpeg创建纯色封面
        audio_name = Path(audio_file_path).stem
        cover_path = f"assets/images/posts/{datetime.now().strftime('%Y/%m')}/{audio_name}-cover.jpg"
        
        Path(cover_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            ffmpeg_cmd = [
                'ffmpeg', '-y',
                '-f', 'lavfi',
                '-i', 'color=c=#1a1a2e:size=720x720:d=1',
                '-vframes', '1',
                cover_path
            ]
            
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self._log(f"✅ 纯色封面创建成功: {cover_path}")
                return cover_path
            else:
                raise Exception(f"ffmpeg失败: {result.stderr}")
                
        except Exception as e:
            self._log(f"封面创建失败: {e}")
            # 返回一个占位符路径
            return "assets/images/header-test.jpg"
    
    def _select_existing_image(self) -> Optional[str]:
        """
        从现有图片中选择封面
        
        Returns:
            选择的图片路径，如果取消则返回None
        """
        # 查找assets/images目录中的图片文件
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        image_files = []
        
        images_dir = Path("assets/images")
        if images_dir.exists():
            for ext in image_extensions:
                image_files.extend(images_dir.rglob(f"*{ext}"))
        
        if not image_files:
            print("❌ 未找到任何图片文件")
            return None
        
        # 筛选最近2个月的图片（2025年7月和8月）
        from datetime import datetime
        current_year = datetime.now().year
        recent_months = [7, 8]  # 7月和8月
        
        filtered_images = []
        for img_path in image_files:
            # 检查路径中是否包含2025年的7月或8月
            path_str = str(img_path)
            if (f"/{current_year}/07/" in path_str or f"/{current_year}/08/" in path_str or
                f"posts/{current_year}/07/" in path_str or f"posts/{current_year}/08/" in path_str):
                filtered_images.append(img_path)
        
        if not filtered_images:
            print("❌ 未找到最近2个月的图片文件")
            return None
        
        # 按修改时间排序，限制显示数量
        filtered_images.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        image_files = filtered_images[:30]  # 显示最新的30张图片
        
        print("\n🖼️ 可选择的图片文件:")
        for i, img_path in enumerate(image_files, 1):
            relative_path = str(img_path).replace("assets/images/", "")
            print(f"  {i}. {relative_path}")
        
        print("  0. 取消")
        
        try:
            choice = input(f"\n请选择图片 (1-{len(image_files)}): ").strip()
            
            if choice == '0':
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(image_files):
                selected_image = str(image_files[idx])
                print(f"✅ 已选择: {selected_image}")
                return selected_image
            else:
                print("❌ 无效选择")
                return None
                
        except (ValueError, KeyboardInterrupt):
            print("❌ 操作取消")
            return None
    
    def _create_simple_cover(self, audio_file_path: str) -> str:
        """
        创建简单的纯色背景封面
        
        Args:
            audio_file_path: 音频文件路径
            
        Returns:
            封面图片路径
        """
        return self._create_solid_color_cover(audio_file_path)
    
    def upload_audio_to_youtube(self) -> Dict[str, Any]:
        """
        完整的音频上传YouTube流程
        
        Returns:
            上传结果字典，包含状态信息和YouTube链接等信息
        """
        self._log("开始音频上传YouTube流程")
        
        # 1. 选择音频文件
        audio_file = self.select_audio_file()
        if not audio_file:
            self._log("未选择音频文件，取消上传")
            return {'success': False, 'cancelled': True, 'message': '用户取消操作'}
        
        # 2. 选择封面图片
        cover_image = self.select_cover_image(audio_file)
        if not cover_image:
            self._log("未选择封面图片，取消上传")
            return {'success': False, 'cancelled': True, 'message': '用户取消操作'}
        
        # 3. 收集上传信息
        upload_info = self._collect_upload_info(audio_file)
        if not upload_info:
            self._log("未收集到上传信息，取消上传")
            return {'success': False, 'cancelled': True, 'message': '用户取消操作'}
        
        try:
            # 4. 优化音频
            self._log("优化音频文件...")
            print("\n🎵 正在优化音频文件...")
            optimized_audio = self._optimize_audio_for_video(audio_file)
            if not optimized_audio:
                self._log("音频优化失败，使用原始音频")
                optimized_audio = audio_file
            
            # 5. 生成视频文件
            self._log("生成视频文件...")
            print("\n🎬 正在生成视频文件...")
            audio_name = Path(audio_file).stem
            video_path = f".tmp/videos/{audio_name}.mp4"
            Path(video_path).parent.mkdir(parents=True, exist_ok=True)
            
            success = self._create_audio_video_without_optimization(optimized_audio, cover_image, video_path)
            if not success:
                self._log("视频生成失败")
                return {'success': False, 'cancelled': False, 'message': '视频生成失败'}
            
            # 6. 上传到YouTube
            self._log("上传到YouTube...")
            
            # 构造video_info和content_guide以兼容现有上传方法
            video_info = {
                'title': upload_info['title'],
                'description': upload_info['description'],
                'id': audio_name
            }
            
            content_guide = {
                'title': upload_info['title'],
                'excerpt': upload_info['description'],
                'outline': [
                    "音频内容播客",
                    "高质量音频体验", 
                    "便于学习和收听"
                ],
                'tags': ["音频播客", "学习资源", "高质量音频"],
                'learning_tips': {
                    'vocabulary': ["audio", "podcast", "content"],
                    'expressions': ["high quality", "easy listening"],
                    'cultural_context': "音频播客在全球范围内越来越受欢迎，成为获取信息和娱乐的重要方式。"
                }
            }
            
            youtube_video_id = self.upload_to_youtube(
                video_path, video_info, content_guide, ""
            )
            
            if youtube_video_id:
                youtube_url = f"https://www.youtube.com/watch?v={youtube_video_id}"
                self._log(f"✅ 上传成功! YouTube链接: {youtube_url}")
                
                # 7. 清理临时文件
                try:
                    Path(video_path).unlink()
                    if optimized_audio != audio_file:
                        Path(optimized_audio).unlink()
                except:
                    pass
                
                return {
                    'success': True,
                    'youtube_url': youtube_url,
                    'youtube_video_id': youtube_video_id,
                    'title': upload_info['title'],
                    'description': upload_info['description'],
                    'audio_file': audio_file,
                    'cover_image': cover_image
                }
            else:
                self._log("YouTube上传失败")
                return {'success': False, 'cancelled': False, 'message': 'YouTube上传失败'}
                
        except Exception as e:
            self._log(f"上传过程中出现错误: {e}")
            return {'success': False, 'cancelled': False, 'message': f'上传过程中出现错误: {e}'}
    
    def _collect_upload_info(self, audio_file: str) -> Optional[Dict[str, str]]:
        """
        收集YouTube上传所需的信息
        
        Args:
            audio_file: 音频文件路径
            
        Returns:
            包含标题和描述的字典，取消时返回None
        """
        audio_name = Path(audio_file).stem
        
        print(f"\n📝 为音频文件 '{audio_name}' 设置YouTube上传信息:")
        
        # 检查并提示终端编码设置
        import sys
        if sys.stdout.encoding.lower() not in ['utf-8', 'utf8']:
            print(f"⚠️  提示：当前终端编码为 {sys.stdout.encoding}，建议设置为UTF-8以获得更好的中文支持")
            print("   可尝试运行: export LANG=zh_CN.UTF-8 或 export LC_ALL=zh_CN.UTF-8")
        
        try:
            # 默认标题（基于文件名）
            default_title = audio_name.replace('-', ' ').replace('_', ' ').title()
            title = input(f"视频标题 (默认: {default_title}): ").strip()
            if not title:
                title = default_title
            
            # 描述
            print("\n视频描述 (多行输入，输入空行结束):")
            print("💡 提示：如果遇到中文删除问题，可以在外部编辑器中准备文本后粘贴")
            description_lines = []
            while True:
                try:
                    line = input()
                    if not line:
                        break
                    description_lines.append(line)
                except (UnicodeDecodeError, KeyboardInterrupt):
                    print("\n输入中断，使用默认描述")
                    break
            
            description = '\n'.join(description_lines) if description_lines else f"音频播客: {title}"
            
            # 确认信息
            print(f"\n📋 上传信息确认:")
            print(f"标题: {title}")
            print(f"描述: {description}")
            
            confirm = input("\n确认上传? (y/N): ").strip().lower()
            if confirm in ['y', 'yes']:
                return {
                    'title': title,
                    'description': description
                }
            else:
                print("取消上传")
                return None
                
        except (KeyboardInterrupt, EOFError):
            print("\n操作取消")
            return None
    
    def integrate_youtube_link_to_post(self, upload_result: Dict[str, Any]) -> bool:
        """
        将YouTube链接集成到相关博文中
        
        Args:
            upload_result: 上传结果字典
            
        Returns:
            是否成功集成到博文
        """
        if not upload_result or not upload_result.get('success'):
            return False
        
        # 查找可能相关的博文
        related_posts = self._find_related_posts(upload_result['audio_file'])
        
        if not related_posts:
            print("❌ 未找到相关博文")
            return False
        
        print(f"\n📝 找到 {len(related_posts)} 篇草稿博文:")
        for i, post_path in enumerate(related_posts, 1):
            post_name = Path(post_path).stem
            # 移除日期前缀以便显示
            display_name = post_name[11:] if len(post_name) > 10 and post_name[10] == '-' else post_name
            print(f"  {i}. {display_name}")
        
        print("  0. 取消集成")
        
        try:
            choice = input(f"\n请选择要集成YouTube链接的博文 (1-{len(related_posts)}): ").strip()
            
            if choice == '0':
                return False
            
            idx = int(choice) - 1
            if 0 <= idx < len(related_posts):
                selected_post = related_posts[idx]
                return self._add_youtube_link_to_post(selected_post, upload_result)
            else:
                print("❌ 无效选择")
                return False
                
        except (ValueError, KeyboardInterrupt):
            print("❌ 操作取消")
            return False
    
    def _find_related_posts(self, audio_file: str) -> List[str]:
        """
        查找与音频文件相关的博文，使用多种匹配策略
        
        Args:
            audio_file: 音频文件路径
            
        Returns:
            相关博文路径列表
        """
        audio_name = Path(audio_file).stem.lower()
        
        # 只查找_drafts目录中的文件（草稿）
        search_dirs = ['_drafts']
        all_posts = []
        exact_matches = []
        partial_matches = []
        
        for search_dir in search_dirs:
            posts_dir = Path(search_dir)
            if posts_dir.exists():
                for post_file in posts_dir.glob('*.md'):
                    post_name = post_file.stem.lower()
                    all_posts.append((str(post_file), post_name))
                    
                    # 精确匹配策略
                    if self._is_exact_match(audio_name, post_name):
                        exact_matches.append(str(post_file))
                    # 部分匹配策略  
                    elif self._is_partial_match(audio_name, post_name):
                        partial_matches.append(str(post_file))
        
        # 如果没有找到任何匹配，返回所有草稿博文供用户选择
        if not exact_matches and not partial_matches:
            print(f"🔍 音频文件名: {Path(audio_file).stem}")
            print("💡 未找到直接匹配的博文，将显示所有草稿博文")
            # 按修改时间排序，返回最近的20篇
            all_posts.sort(key=lambda x: Path(x[0]).stat().st_mtime, reverse=True)
            return [post[0] for post in all_posts[:20]]
        
        # 优先返回精确匹配，然后是部分匹配
        result = exact_matches + partial_matches
        
        # 按修改时间排序
        result.sort(key=lambda x: Path(x).stat().st_mtime, reverse=True)
        
        return result[:15]  # 限制显示最多15篇
    
    def _is_exact_match(self, audio_name: str, post_name: str) -> bool:
        """
        精确匹配策略：检查音频文件名的关键部分是否在博文名中
        """
        # 清理音频文件名
        audio_clean = audio_name.replace('youtube-', '').replace('-script', '').replace('-optimized', '')
        audio_clean = audio_clean.replace('_', '-')
        
        # 移除日期前缀（如果存在）
        if len(post_name) > 10 and post_name[10] == '-':
            post_clean = post_name[11:]
        else:
            post_clean = post_name
        
        # 检查音频文件名是否包含在博文名中，或者反之
        return audio_clean in post_clean or post_clean in audio_clean
    
    def _is_partial_match(self, audio_name: str, post_name: str) -> bool:
        """
        部分匹配策略：检查关键词重叠度
        """
        # 清理和分词
        audio_clean = audio_name.replace('youtube-', '').replace('-script', '').replace('-optimized', '')
        audio_words = set(audio_clean.split('-'))
        
        # 移除日期前缀
        if len(post_name) > 10 and post_name[10] == '-':
            post_clean = post_name[11:]
        else:
            post_clean = post_name
        
        post_words = set(post_clean.split('-'))
        
        # 移除常见的停用词
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'}
        audio_words = audio_words - stop_words
        post_words = post_words - stop_words
        
        # 过滤掉过短的词
        audio_words = {word for word in audio_words if len(word) > 2}
        post_words = {word for word in post_words if len(word) > 2}
        
        if not audio_words or not post_words:
            return False
        
        # 计算重叠度
        common_words = audio_words.intersection(post_words)
        overlap_ratio = len(common_words) / min(len(audio_words), len(post_words))
        
        # 如果重叠度超过50%，认为相关
        return overlap_ratio >= 0.5
    
    def _is_related_post(self, audio_name: str, post_name: str) -> bool:
        """
        判断音频文件和博文是否相关
        
        Args:
            audio_name: 音频文件名（小写）
            post_name: 博文文件名（小写）
            
        Returns:
            是否相关
        """
        # 移除常见前缀和后缀
        audio_clean = audio_name.replace('youtube-', '').replace('-script', '').replace('-optimized', '')
        post_clean = post_name
        
        # 如果移除日期前缀
        if len(post_clean) > 10 and post_clean[10] == '-':
            post_clean = post_clean[11:]
        
        # 分割为单词
        audio_words = set(audio_clean.split('-'))
        post_words = set(post_clean.split('-'))
        
        # 计算交集
        common_words = audio_words.intersection(post_words)
        
        # 如果有3个或以上公共单词，或公共单词占比超过50%，认为相关
        if len(common_words) >= 3:
            return True
        
        if len(audio_words) > 0:
            overlap_ratio = len(common_words) / len(audio_words)
            if overlap_ratio >= 0.5:
                return True
        
        return False
    
    def _add_youtube_link_to_post(self, post_path: str, upload_result: Dict[str, Any]) -> bool:
        """
        将YouTube链接添加到博文中
        
        Args:
            post_path: 博文文件路径
            upload_result: 上传结果字典
            
        Returns:
            是否成功添加
        """
        try:
            import frontmatter
            
            with open(post_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            
            content = post.content
            youtube_url = upload_result['youtube_url']
            title = upload_result['title']
            
            # 检查是否已经包含此YouTube链接，避免重复添加
            if youtube_url in content:
                self._log(f"⚠️ YouTube链接已存在于博文中: {Path(post_path).name}")
                print(f"⚠️ YouTube链接已存在于博文中，跳过添加")
                return True
            
            # 构造YouTube播客区块（响应式iframe）
            youtube_section = f"""
## 🎧 播客收听 (YouTube版)

<div class="video-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000;">
  <iframe src='https://www.youtube.com/embed/{upload_result['youtube_video_id']}?rel=0&showinfo=0&color=white&iv_load_policy=3' 
          style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
          frameborder='0' 
          allowfullscreen>
  </iframe>
</div>

**标题**: [{title}]({youtube_url})  
**平台**: YouTube | **类型**: 音频播客 | **隐私**: 仅限会员链接访问

> 💡 **提示**: 此视频设为"非公开"状态，只有通过本站链接才能访问，保护会员专享内容。
"""
            
            # 总是追加到文末
            post.content = content + '\n' + youtube_section
            
            # 保存修改后的文件
            # 使用frontmatter.dumps()生成字符串，然后写入文件
            content_str = frontmatter.dumps(post, default_flow_style=False, allow_unicode=True)
            with open(post_path, 'w', encoding='utf-8') as f:
                f.write(content_str)
            
            self._log(f"✅ YouTube链接已添加到博文: {Path(post_path).name}")
            print(f"✅ YouTube链接已集成到博文: {Path(post_path).name}")
            
            return True
            
        except Exception as e:
            self._log(f"添加YouTube链接到博文失败: {e}")
            print(f"❌ 集成失败: {e}")
            return False
    
    def _find_insert_position(self, content: str) -> int:
        """
        在博文内容中找到合适的插入位置
        
        Args:
            content: 博文内容
            
        Returns:
            插入位置的行号，-1表示添加到末尾
        """
        lines = content.split('\n')
        
        # 查找已有的播客部分
        for i, line in enumerate(lines):
            if '🎧' in line or '播客' in line or 'podcast' in line.lower():
                # 在现有播客部分之后插入
                return i + 1
        
        # 查找"更多"标记之后
        for i, line in enumerate(lines):
            if '<!-- more -->' in line:
                return i + 2
        
        # 默认添加到第一个二级标题之前
        for i, line in enumerate(lines):
            if line.startswith('## ') and i > 0:
                return i
        
        return -1

    def check_elevenlabs_quota(self):
        """
        检查ElevenLabs API配额状态
        """
        if not self.elevenlabs_available or not self.elevenlabs_client:
            return
            
        try:
            # ElevenLabs API 获取用户信息和配额
            user_info = self.elevenlabs_client.user.get()
            
            if hasattr(user_info, 'subscription'):
                subscription = user_info.subscription
                
                # 获取配额信息
                character_count = getattr(subscription, 'character_count', 0)
                character_limit = getattr(subscription, 'character_limit', 0)
                remaining_characters = character_limit - character_count
                
                # 计算使用百分比
                usage_percentage = (character_count / character_limit * 100) if character_limit > 0 else 0
                
                self._log(f"📊 ElevenLabs配额状态:")
                self._log(f"   已使用: {character_count:,} characters")
                self._log(f"   总配额: {character_limit:,} characters")
                self._log(f"   剩余额度: {remaining_characters:,} characters")
                self._log(f"   使用率: {usage_percentage:.1f}%")
                
                # 配额预警
                if usage_percentage > 90:
                    self._log("⚠️ ElevenLabs配额即将用完！", "warning")
                elif usage_percentage > 75:
                    self._log("⚠️ ElevenLabs配额使用率较高", "warning")
                    
                # 估算剩余可生成的音频时长（粗略估算：每分钟约100字符）
                estimated_minutes = remaining_characters // 100
                if estimated_minutes < 10:
                    self._log(f"⚠️ 预计剩余可生成音频约{estimated_minutes}分钟", "warning")
                else:
                    self._log(f"💡 预计剩余可生成音频约{estimated_minutes}分钟")
                    
        except Exception as e:
            self._log(f"获取ElevenLabs配额信息失败: {e}", "warning")
            
    def upload_to_youtube(self, video_path: str, video_info: Dict[str, Any], 
                         content_guide: Dict[str, Any], youtube_url: str) -> Optional[str]:
        """
        上传视频到YouTube
        
        Args:
            video_path: 视频文件路径
            video_info: 原始视频信息
            content_guide: 导读内容
            youtube_url: 原始YouTube链接
            
        Returns:
            上传成功后的YouTube视频ID，失败返回None
        """
        if not self.youtube:
            self._log("YouTube API未配置，无法上传")
            return None
            
        # 检查是否使用OAuth认证（只有OAuth可以上传）
        # 优先检查是否使用API Key模式（这种情况下无法上传）
        try:
            if hasattr(self.youtube, '_developerKey') and self.youtube._developerKey:
                # 使用API Key构建的客户端，无法上传
                oauth_configured = False
                self._log("❌ 检测到API Key模式，上传需要OAuth认证")
                self._log("YouTube上传需要OAuth认证，当前仅配置了API Key，无法上传")
                self._log("💡 请运行: python scripts/tools/youtube_oauth_setup.py 配置OAuth认证")
                return None
            elif hasattr(self.youtube, '_http') and hasattr(self.youtube._http, 'credentials'):
                # 新版本OAuth API客户端 - 但需要验证credentials是否有效
                creds = self.youtube._http.credentials
                if creds and hasattr(creds, 'valid') and creds.valid:
                    oauth_configured = True
                    self._log("✅ 检测到有效的OAuth认证（新版API客户端）")
                else:
                    oauth_configured = False
                    self._log("❌ OAuth认证无效或过期")
                    self._log("💡 请运行: python scripts/tools/youtube_oauth_setup.py 重新认证")
                    return None
            elif hasattr(self.youtube, '_http') and hasattr(self.youtube._http, '_credentials'):
                # 旧版本OAuth API客户端 - 但需要验证credentials是否有效  
                creds = self.youtube._http._credentials
                if creds and hasattr(creds, 'valid') and creds.valid:
                    oauth_configured = True
                    self._log("✅ 检测到有效的OAuth认证（旧版API客户端）")
                else:
                    oauth_configured = False
                    self._log("❌ OAuth认证无效或过期")
                    self._log("💡 请运行: python scripts/tools/youtube_oauth_setup.py 重新认证")
                    return None
            else:
                # 无法确定认证类型
                oauth_configured = False
                self._log("❌ 无法检测到有效的OAuth认证")
                self._log("💡 请运行: python scripts/tools/youtube_oauth_setup.py 配置OAuth认证")
                return None
        except Exception as auth_check_error:
            self._log(f"OAuth认证检查出错，尝试继续上传: {auth_check_error}")
            # 如果检查失败，尝试继续上传，让上传API自己报错
            
        try:
    
            # 准备视频元数据
            title = f"{content_guide['title']} | 中文播客导读"
            description = f"""
🎧 中文播客导读：{content_guide['excerpt']}

📚 学习要点：
{chr(10).join([f"• {point}" for point in content_guide['outline']])}

🔤 关键词汇：
{' | '.join(content_guide['learning_tips']['vocabulary'])}

💬 常用表达：
{' | '.join(content_guide['learning_tips']['expressions'])}

🏛️ 文化背景：
{content_guide['learning_tips']['cultural_context']}

🌍 原视频链接：{youtube_url}

---
这是基于YouTube英文视频生成的中文学习播客，帮助中文用户理解英语内容，拓展全球视野。

#英语学习 #播客 #全球视野 #中文导读
            """.strip()
            
            # 准备上传参数
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube标题限制
                    'description': description[:5000],  # YouTube描述限制
                    'tags': content_guide['tags'] + ['英语学习播客', '中文导读', '全球视野'],
                    'categoryId': '27',  # Education类别
                    'defaultLanguage': 'zh-CN',
                    'defaultAudioLanguage': 'zh-CN'
                },
                'status': {
                    'privacyStatus': 'unlisted',  # 设为unlisted保护会员内容，只有知道链接的人才能访问
                    'selfDeclaredMadeForKids': False
                }
            }
            
            self._log("开始上传到YouTube...")
            
            # 执行上传
            from googleapiclient.http import MediaFileUpload
            
            media = MediaFileUpload(
                video_path,
                chunksize=10*1024*1024,  # 10MB chunks instead of all at once
                resumable=True,
                mimetype='video/mp4'
            )
            
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            self._log(f"开始分块上传视频，文件大小: {media.size()} bytes")
            
            # 可恢复上传的循环
            response = None
            retry_count = 0
            max_retries = 3
            last_progress = 0
            
            print("\n📤 开始上传到YouTube...")
            print("上传进度:")
            
            while response is None and retry_count < max_retries:
                try:
                    if retry_count > 0:
                        self._log(f"尝试上传 (第{retry_count + 1}次/共{max_retries}次)...")
                    status, response = request.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        if progress > last_progress:
                            # 显示简单的进度条
                            bar_length = 30
                            filled_length = int(bar_length * progress // 100)
                            bar = '█' * filled_length + '░' * (bar_length - filled_length)
                            print(f"\r[{bar}] {progress}% ", end='', flush=True)
                            last_progress = progress
                        self._log(f"上传进度: {progress}%")
                    
                except Exception as upload_error:
                    retry_count += 1
                    if retry_count >= max_retries:
                        raise upload_error
                    else:
                        self._log(f"上传失败，准备重试: {upload_error}")
                        import time
                        time.sleep(2 ** retry_count)  # 指数退避
            
            if response and isinstance(response, dict) and 'id' in response:
                # 确保进度条显示100%
                bar_length = 30
                filled_bar = '█' * bar_length
                print(f"\r[{filled_bar}] 100% ")  # 强制显示100%
                print(f"✅ 上传完成！")  # 完成进度条显示
                video_id = response['id']
                youtube_link = f"https://www.youtube.com/watch?v={video_id}"
                self._log(f"✅ YouTube上传成功: {youtube_link}")
                return video_id
            else:
                self._log(f"YouTube上传失败：未返回视频ID，response: {response}")
                return None
                
        except Exception as e:
            self._log(f"YouTube上传失败: {e}")
            return None

    def save_audio_file(self, temp_audio_path: str, video_id: str) -> str:
        """
        保存音频文件到指定位置
        
        Args:
            temp_audio_path: 临时音频文件路径
            video_id: 视频ID
            
        Returns:
            最终音频文件路径
        """
        try:
            today = datetime.now()
            audio_filename = f"youtube-{today.strftime('%Y%m%d')}-{video_id}.mp3"
            final_audio_path = os.path.join(self.audio_dir, audio_filename)
            
            # 复制文件到最终位置
            import shutil
            shutil.copy2(temp_audio_path, final_audio_path)
            
            self._log(f"音频文件保存成功: {final_audio_path}")
            return final_audio_path
            
        except Exception as e:
            self._log(f"音频文件保存失败: {e}")
            return temp_audio_path
    
    def create_jekyll_article(self, video_info: Dict[str, Any], content_guide: Dict[str, Any], 
                            youtube_url: str, audio_path: Optional[str] = None, thumbnail_path: str = "",
                            youtube_video_id: Optional[str] = None) -> str:
        """
        创建Jekyll格式的文章
        
        Args:
            video_info: 视频信息
            content_guide: 导读内容
            youtube_url: YouTube链接
            audio_path: 音频文件路径
            thumbnail_path: 缩略图路径
            youtube_video_id: YouTube播客视频ID（可选）
            
        Returns:
            文章文件路径
        """
        today = datetime.now()
        
        # 从视频标题生成安全的文件名
        safe_title = self._generate_safe_filename(video_info['title'])
        article_filename = f"{today.strftime('%Y-%m-%d')}-youtube-{safe_title}.md"
        article_path = os.path.join(self.draft_dir, article_filename)
        
        # 生成相对路径（用于Jekyll）
        audio_relative = audio_path.replace("assets/", "{{ site.baseurl }}/assets/") if audio_path else None
        thumbnail_relative = thumbnail_path.replace("assets/", "{{ site.baseurl }}/assets/") if thumbnail_path else ""
        
        # 构建文章内容
        article_content = f"""---
title: "{content_guide['title']}"
date: {today.strftime('%Y-%m-%d')}
categories: [global-perspective]
tags: {json.dumps(content_guide['tags'], ensure_ascii=False)}
excerpt: "{content_guide['excerpt']}"
header:
  teaser: "{thumbnail_relative}"
---

## 📺 原始视频
**YouTube链接**: [{video_info['title']}]({youtube_url})  
**时长**: {video_info['duration']} | **难度**: {content_guide['difficulty_level']} | **频道**: {video_info['channel_title']}

<!-- more -->

## 🎧 中文播客导读
{f'''<!-- YouTube播客优先显示 -->
{f"""<div class="video-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000;">
  <iframe src='https://www.youtube.com/embed/{youtube_video_id}?rel=0&showinfo=0&color=white&iv_load_policy=3' 
          style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
          frameborder='0' 
          allowfullscreen>
  </iframe>
</div>""" if youtube_video_id else ""}

{f"🎙️ **[在YouTube上收听完整播客](https://www.youtube.com/watch?v={youtube_video_id})**" if youtube_video_id else ""}

<!-- 本地音频备用 -->
<audio controls>
  <source src="{audio_relative}" type="audio/mpeg">
  您的浏览器不支持音频播放。
</audio>

*建议配合原视频观看，通过中文播客快速理解英文内容精华*''' if audio_relative else f'''
{f"""<div class="video-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000;">
  <iframe src='https://www.youtube.com/embed/{youtube_video_id}?rel=0&showinfo=0&color=white&iv_load_policy=3' 
          style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;" 
          frameborder='0' 
          allowfullscreen>
  </iframe>
</div>""" if youtube_video_id else ""}

{f"🎙️ **[在YouTube上收听完整播客](https://www.youtube.com/watch?v={youtube_video_id})**" if youtube_video_id else ""}

{"" if youtube_video_id else """> ⚠️ **音频生成失败**：本次未能生成音频文件，但播客文本脚本已保存在 `assets/audio/` 目录中。
> 
> 建议：
> 1. 查看文本脚本了解播客内容结构
> 2. 直接观看英文原视频进行学习
> 3. 可考虑安装 eSpeak TTS 引擎以支持本地音频生成"""}
'''}

## 📋 内容大纲
"""
        
        # 添加大纲内容
        for point in content_guide['outline']:
            article_content += f"- {point}\n"
        
        article_content += f"""
## 🌍 英语学习指南

### 🔤 关键词汇
{self._format_learning_items(content_guide['learning_tips']['vocabulary'])}

### 💬 常用表达
{self._format_learning_items(content_guide['learning_tips']['expressions'])}

### 🏛️ 文化背景
{content_guide['learning_tips']['cultural_context']}

## 🎯 学习建议
1. **第一遍**: 先听中文播客了解大意和框架
2. **第二遍**: 观看英文原视频，验证理解
3. **第三遍**: 重点关注语言表达和文化细节
4. **进阶**: 尝试用英文总结视频要点

---

**💡 提示**: 这种"中文导读+英文原版"的学习方式能帮助你：
- 降低英语学习门槛
- 快速掌握内容框架  
- 提升听力理解能力
- 培养全球化视野

🌍 **英文原始资料**: [点击观看YouTube原视频]({youtube_url})
"""

        # 写入文件
        try:
            with open(article_path, 'w', encoding='utf-8') as f:
                f.write(article_content)
            
            self._log(f"Jekyll文章创建成功: {article_path}")
            return article_path
            
        except Exception as e:
            self._log(f"文章创建失败: {e}")
            raise
    
    def _clean_string_aggressive(self, s: str) -> str:
        """彻底清理字符串中的不可打印字符 - 全局版本"""
        if not s:
            return ""
        
        # 转换为字符串并严格清理
        s_str = str(s).strip()
        
        # 特殊处理URL - 更严格地清理
        if 'youtube.com' in s_str or 'youtu.be' in s_str:
            # 对于URL，只保留基本ASCII字符和必要的URL符号
            # 先移除所有控制字符和非打印字符
            import re
            cleaned = re.sub(r'[\x00-\x1f\x7f-\xff]', '', s_str)
            # 再次清理空白字符
            cleaned = re.sub(r'\s+', '', cleaned)  # 移除所有空白字符
            # 确保只有有效的URL字符：字母数字和 -._/:?&=
            cleaned = re.sub(r'[^\w\-./:?&=]', '', cleaned)
            
            # 验证URL基本结构 - 更宽松的检查
            valid_patterns = [
                'youtube.com/watch?v=', 'youtu.be/', 'youtube.com/shorts/',
                'youtube.com/embed/', 'youtube.com/v/'
            ]
            is_valid_url = any(pattern in cleaned for pattern in valid_patterns)
            
            if not is_valid_url:
                self._log(f"⚠️ URL清理后格式异常，尝试恢复: {repr(cleaned)}", "warning")
                # 尝试从原始字符串重新提取
                import urllib.parse
                try:
                    parsed = urllib.parse.urlparse(s_str.replace('\n', '').replace('\r', ''))
                    if parsed.netloc and parsed.path:
                        cleaned = urllib.parse.urlunparse(parsed)
                except Exception:
                    pass
            else:
                # URL格式正常，不需要警告
                self._log(f"✅ URL清理成功: {cleaned[:50]}{'...' if len(cleaned) > 50 else ''}")
        else:
            # 对于其他字符串，移除控制字符但保留中文字符
            import re
            cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', s_str)
            # 移除换行符和制表符
            cleaned = re.sub(r'[\r\n\t\v\f]', ' ', cleaned)
            # 保留中文字符和基本字符
            cleaned = re.sub(r'[^\x20-\x7e\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', '', cleaned)
            # 压缩多个空格
            cleaned = re.sub(r'\s+', ' ', cleaned)
        
        result = cleaned.strip()
        
        # 限制长度并确保结果有效
        return result[:500] if result else ""

    def generate_from_youtube(self, youtube_url: str, custom_title: str = "", 
                            tts_model: str = "elevenlabs", target_language: str = "zh-CN",
                            conversation_style: str = "casual,informative", 
                            upload_to_youtube: bool = False) -> Dict[str, str]:
        """
        从YouTube链接生成完整的播客学习资料
        
        Args:
            youtube_url: YouTube视频链接
            custom_title: 自定义标题（可选）
            tts_model: TTS模型 ("edge", "openai", "elevenlabs", "geminimulti")
            target_language: 目标语言 ("zh-CN", "en-US", "ja-JP", "ko-KR")
            conversation_style: 对话风格
            upload_to_youtube: 是否上传播客到YouTube
            
        Returns:
            生成结果字典
        """
        try:
            # 🚨 在开始时立即清理所有输入参数，防止任何控制字符传播
            youtube_url = self._clean_string_aggressive(youtube_url)
            custom_title = self._clean_string_aggressive(custom_title)
            target_language = self._clean_string_aggressive(target_language)
            conversation_style = self._clean_string_aggressive(conversation_style)
            
            self._log(f"🧹 输入参数清理完成: URL={repr(youtube_url)}, Style={repr(conversation_style)}")
            
            # 保存当前目标语言供TTS使用
            self.current_target_language = target_language
            self._log(f"开始处理YouTube视频: {youtube_url}")
            
            # 1. 提取视频ID
            video_id = self.extract_video_id(youtube_url)
            self._log(f"视频ID: {video_id}")
            
            # 2. 获取视频信息
            video_info = self.get_video_info(video_id)
            self._log(f"视频标题: {video_info['title']}")
            
            # 3. 根据视频时长计算自适应字数
            video_duration_seconds = self.get_video_duration_seconds(video_info)
            adaptive_word_count = self.calculate_adaptive_word_count(video_duration_seconds)
            
            self._log(f"📊 视频时长: {video_info['duration']} ({video_duration_seconds}秒)")
            self._log(f"📝 自适应字数: {adaptive_word_count}字 (估算{adaptive_word_count//100}轮对话)")
            
            # 检查视频信息质量，如果API获取失败则提供更多信息
            if video_info['title'] == f"YouTube视频 {video_id}" or not video_info.get('description'):
                self._log("⚠️ 视频信息不足，无法生成高质量播客", "warning", True)
                self._log("💡 建议：检查YouTube API权限或使用包含详细描述的视频", "warning", True)
                
                # 尝试获取更多信息用于播客生成
                try:
                    # 如果有完整的视频URL，尝试直接使用
                    if 'youtube.com/watch?v=' in youtube_url or 'youtu.be/' in youtube_url:
                        # 将原始URL也传递给播客生成，让Podcastfy尝试直接处理
                        self._log("🔄 将使用原始URL进行播客生成", "info")
                        # 更新video_info以便后续处理
                        video_info['original_url'] = youtube_url
                except Exception as e:
                    self._log(f"获取额外视频信息失败: {e}", "warning")
            
            # 3. 生成播客
            language_name = {
                "zh-CN": "中文",
                "en-US": "英文", 
                "ja-JP": "日文",
                "ko-KR": "韩文"
            }.get(target_language, target_language)
            self._log(f"正在生成{language_name}播客（预计1-3分钟）...")
            temp_audio_path = self.generate_podcast(youtube_url, conversation_style, target_language, adaptive_word_count)
            
            # 检查是否使用备用模式
            if temp_audio_path == "fallback_mode":
                self._log("使用备用播客生成模式", "info", True)
                self._log("🔄 步骤1/4: 初始化本地播客生成器...", "info", True)
                self._log(f"配置参数 - 目标语言: {target_language}, 对话风格: {conversation_style}")
                
                # 生成播客脚本
                self._log("🔄 步骤2/4: 正在生成播客脚本（可能需要30-60秒）...", "info", True)
                script = self.generate_podcast_script(video_info, target_language, conversation_style)
                self._log(f"播客脚本生成完成，长度: {len(script)}字符")
                
                # 尝试生成本地音频
                self._log("🔄 步骤3/4: 准备音频生成...", "info", True)
                today = datetime.now()
                safe_title = self._generate_safe_filename(video_info['title'])
                audio_filename = f"youtube-{today.strftime('%Y%m%d')}-{safe_title}.wav"
                audio_path = os.path.join(self.audio_dir, audio_filename)
                
                # 总是保存播客脚本供用户查看和调试
                script_filename = f"youtube-{today.strftime('%Y%m%d')}-{safe_title}-script.txt"
                script_path = os.path.join(self.audio_dir, script_filename)
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(script)
                self._log(f"📝 播客脚本已保存: {script_path}")
                
                try:
                    # 智能TTS引擎选择，优先ElevenLabs获得最佳音质
                    self._log(f"🎯 TTS选择检查: tts_model={tts_model}, elevenlabs_available={self.elevenlabs_available}")
                    
                    if tts_model == "elevenlabs" and self.elevenlabs_available:
                        tts_engine = "elevenlabs"
                        self._log("🎯 选择ElevenLabs - 最高质量AI语音")
                    elif tts_model == "gtts":
                        tts_engine = "gtts"
                        self._log("🎯 选择Google TTS - 高质量语音")
                    elif tts_model == "espeak":
                        tts_engine = "espeak"
                        self._log("🎯 选择eSpeak - 快速生成")
                    else:
                        # 智能默认：始终优先ElevenLabs
                        if self.elevenlabs_available:
                            tts_engine = "elevenlabs"
                            self._log("🎯 智能选择ElevenLabs（最高质量）")
                        else:
                            tts_engine = "gtts"
                            self._log("🎯 智能选择Google TTS（高质量）")
                    
                    self._log(f"🔄 步骤4/4: 开始音频生成（使用{tts_engine}引擎，可能需要1-2分钟）...", "info", True)
                    if self.generate_local_audio(script, audio_path, tts_engine, dual_speaker=True, target_language=target_language):
                        self._log(f"✅ 本地音频生成成功: {audio_path}", "info", True)
                    else:
                        raise Exception("所有TTS引擎都不可用")
                except Exception as e:
                    self._log(f"本地音频生成失败: {e}")
                    self._log("将只提供文本脚本，请考虑安装eSpeak或其他TTS引擎")
                    # 设置音频路径为None，表示没有音频文件
                    audio_path = None
            else:
                # 使用Podcastfy生成的音频
                audio_path = self.save_audio_file(temp_audio_path, video_id)
            
            # 4. 生成导读内容
            content_guide = self.generate_content_guide(video_info)
            if custom_title:
                content_guide['title'] = custom_title
                self._log(f"使用自定义标题: {custom_title}")
            
            # 5. 下载缩略图
            thumbnail_path = self.download_thumbnail(video_info['thumbnail_url'], video_info)
            if not thumbnail_path:
                self._log("缩略图下载失败")
            
            # 6. YouTube上传（可选）
            youtube_video_id = None
            if upload_to_youtube and audio_path and thumbnail_path:
                self._log("🔄 开始YouTube上传流程...")
                
                # 生成视频文件
                today = datetime.now()
                safe_title = self._generate_safe_filename(video_info['title'])
                video_filename = f"youtube-{today.strftime('%Y%m%d')}-{safe_title}-podcast.mp4"
                temp_video_path = os.path.join(".tmp", "output", "videos", video_filename)
                
                # 确保输出目录存在
                os.makedirs(os.path.dirname(temp_video_path), exist_ok=True)
                
                # 创建音频视频
                if self.create_audio_video(audio_path, thumbnail_path, temp_video_path):
                    # 上传到YouTube
                    youtube_video_id = self.upload_to_youtube(
                        temp_video_path, video_info, content_guide, youtube_url
                    )
                    
                    if youtube_video_id:
                        self._log(f"✅ YouTube播客上传成功: https://www.youtube.com/watch?v={youtube_video_id}")
                        # 清理临时视频文件
                        try:
                            os.remove(temp_video_path)
                        except:
                            pass
                    else:
                        self._log("⚠️ YouTube上传失败，播客仍保存在本地")
                else:
                    self._log("⚠️ 音频视频生成失败，跳过YouTube上传")
            
            # 7. 创建Jekyll文章（更新以包含YouTube链接）
            article_path = self.create_jekyll_article(
                video_info, content_guide, youtube_url, audio_path, thumbnail_path, youtube_video_id
            )
            
            result = {
                'status': 'success',
                'article_path': article_path,
                'audio_path': audio_path,
                'thumbnail_path': thumbnail_path,
                'video_title': video_info['title'],
                'article_title': content_guide['title'],
                'youtube_video_id': youtube_video_id,
                'youtube_podcast_url': f"https://www.youtube.com/watch?v={youtube_video_id}" if youtube_video_id else None
            }
            
            self._log("YouTube播客生成完成！")
            return result
            
        except Exception as e:
            self._log(f"生成过程失败: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }


def main():
    """测试函数"""
    # 示例配置
    config = {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'YOUTUBE_API_KEY': os.getenv('YOUTUBE_API_KEY')  # 可选
    }
    
    if not config['GEMINI_API_KEY']:
        print("请设置GEMINI_API_KEY环境变量")
        return
    
    generator = YouTubePodcastGenerator(config)
    
    # 测试YouTube链接
    test_url = input("请输入YouTube视频链接: ")
    
    if test_url:
        result = generator.generate_from_youtube(test_url)
        print("\n生成结果:")
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()