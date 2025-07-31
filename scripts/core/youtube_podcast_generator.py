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
    import moviepy.editor
    MOVIEPY_AVAILABLE = True
except ImportError:
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
        # 设置Gemini API
        if 'GEMINI_API_KEY' in self.config:
            genai.configure(api_key=self.config['GEMINI_API_KEY'])  # type: ignore
            # 使用与主系统一致的模型配置（从配置文件读取）
            model_name = "gemini-2.5-flash"  # 默认模型
            self.gemini_model = genai.GenerativeModel(model_name)  # type: ignore
            self._log(f"✅ Gemini配置完成 - 模型: {model_name}", "info")
        else:
            raise ValueError("需要GEMINI_API_KEY配置")
        
        # 设置YouTube API
        if 'YOUTUBE_API_KEY' in self.config:
            self.youtube = build('youtube', 'v3', developerKey=self.config['YOUTUBE_API_KEY'])
            self._log("✅ YouTube API 配置完成")
        else:
            self._log("未配置YOUTUBE_API_KEY，将使用基础视频信息提取")
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
        
        Args:
            youtube_url: YouTube视频链接
            
        Returns:
            视频ID
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)'
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
                # 使用YouTube API获取详细信息
                request = self.youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=video_id
                )
                response = request.execute()
                
                if not response['items']:
                    raise ValueError(f"找不到视频ID: {video_id}")
                
                video = response['items'][0]
                snippet = video['snippet']
                content_details = video['contentDetails']
                
                # 解析视频时长
                duration = self.parse_duration(content_details['duration'])
                
                return {
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
                              _target_language: str = "zh-CN",
                              _conversation_style: str = "casual,informative") -> str:
        """
        生成NotebookLM风格的纯对话播客脚本
        """
        self._log("开始生成NotebookLM风格播客脚本")
        
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
        
        # 简化的英语学习播客prompt
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
            # 简化的备用脚本
            return f"""
[A]: 今天这个视频《{video_info['title']}》很有意思，你觉得对英语学习者来说主要价值在哪里？

[B]: 我觉得最大的价值是可以学习到真实的英语表达。这类视频用词都比较地道，语速也适中。

[A]: 那具体应该怎么学呢？直接看可能有点困难。

[B]: 建议先听咱们的中文导读理解大意，然后再看英文原版，这样学习效果会更好。

[A]: 这确实是个不错的学习方法，既能了解内容又能提高英语水平。
"""

    def generate_local_audio(self, script: str, output_path: str, tts_engine: str = "gtts", dual_speaker: bool = True) -> bool:
        """
        使用本地TTS生成音频，支持多种TTS引擎
        
        Args:
            script: 播客脚本
            output_path: 输出音频文件路径
            tts_engine: TTS引擎选择 ("gtts", "elevenlabs", "espeak", "pyttsx3")
            dual_speaker: 是否启用双人对话模式（仅ElevenLabs支持）
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
            if self._generate_elevenlabs_audio(clean_text, output_path, dual_speaker=use_dual_speaker):
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
    
    def _generate_elevenlabs_audio(self, text: str, output_path: str, dual_speaker: bool = False) -> bool:
        """使用ElevenLabs生成高质量AI语音（优化中文自然度）"""
        if not self.elevenlabs_available or not self.elevenlabs_client:
            self._log("ElevenLabs API未配置或库未安装")
            return False
            
        try:
            if dual_speaker:
                return self._generate_dual_speaker_audio(text, output_path)
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
            if hasattr(self.elevenlabs_client, 'text_to_speech'):
                audio_generator = self.elevenlabs_client.text_to_speech.convert(
                    voice_id=voice_id,
                    text=text,
                    model_id="eleven_multilingual_v2",
                    voice_settings=voice_settings
                )
            else:
                # 使用兼容的API方法
                from elevenlabs import generate, Voice
                audio_generator = generate(
                    text=text,
                    voice=Voice(voice_id=voice_id),
                    model="eleven_multilingual_v2"
                )
        except (AttributeError, ImportError):
            # 如果API方法不可用，抛出错误
            raise RuntimeError("ElevenLabs API方法不兼容，请检查库版本")
        
        # 保存音频文件
        with open(output_path, 'wb') as f:
            for chunk in audio_generator:
                f.write(chunk)
        
        self._log(f"✅ ElevenLabs单人音频生成成功: {output_path}")
        return True
    
    def _generate_dual_speaker_audio(self, text: str, output_path: str) -> bool:
        """生成双人对话音频"""
        self._log("🎭 使用ElevenLabs生成双人对话音频")
        
        try:
            # 加载声音配置
            voice_config = self._load_voice_config()
            
            # 解析对话内容，分离不同说话者
            dialogue_segments = self._parse_dialogue(text)
            
            if len(dialogue_segments) < 2:
                self._log("⚠️ 文本不包含对话格式，切换到单人模式")
                return self._generate_single_speaker_audio(text, output_path)
            
            # 生成每个对话片段的音频
            audio_segments = []
            for i, (speaker, segment_text) in enumerate(dialogue_segments):
                self._log(f"   🎤 生成对话片段 {i+1}/{len(dialogue_segments)}: {segment_text[:30]}...")
                
                # 根据说话者选择声音配置
                voice_settings = self._get_speaker_settings(speaker, voice_config)
                voice_id = self._get_speaker_voice_id(speaker, voice_config)
                
                try:
                    # 使用正确的ElevenLabs API调用方式
                    if hasattr(self.elevenlabs_client, 'text_to_speech'):
                        audio_generator = self.elevenlabs_client.text_to_speech.convert(
                            voice_id=voice_id,
                            text=segment_text,
                            model_id="eleven_multilingual_v2",
                            voice_settings=voice_settings
                        )
                    else:
                        # 使用兼容的API方法
                        from elevenlabs import generate, Voice
                        audio_generator = generate(
                            text=segment_text,
                            voice=Voice(voice_id=voice_id),
                            model="eleven_multilingual_v2"
                        )
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
        config_path = "config/elevenlabs_voices.yml"
        
        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config.get('elevenlabs_voices', {})
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
        
        dialogue_segments = []
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
    
    def _get_speaker_settings(self, speaker: str, voice_config: Dict[str, Any]):
        """获取说话者的语音设置"""
        try:
            from elevenlabs import VoiceSettings
        except ImportError:
            # 如果ElevenLabs不可用，返回None
            return None
        
        combination = voice_config.get('voice_combinations', {}).get('chinese_podcast', {})
        speaker_key = 'speaker_a' if speaker == 'A' else 'speaker_b'
        settings = combination.get(speaker_key, {}).get('settings', {})
        
        return VoiceSettings(
            stability=settings.get('stability', 0.4),
            similarity_boost=settings.get('similarity_boost', 0.8),
            style=settings.get('style', 0.6),
            use_speaker_boost=True
        )
    
    def _get_speaker_voice_id(self, speaker: str, voice_config: Dict[str, Any]) -> str:
        """获取说话者的声音ID"""
        combination = voice_config.get('voice_combinations', {}).get('chinese_podcast', {})
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
                    # 创建gTTS对象
                    tts = gTTS(text=text, lang='zh-CN', slow=False)
                    
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
                        target_language: str = "zh-CN") -> str:
        """
        生成播客音频
        
        Args:
            youtube_url: YouTube视频链接
            custom_style: 播客风格
            target_language: 目标语言 ("zh-CN", "en-US", "ja-JP", "ko-KR")
            
        Returns:
            生成的音频文件路径
        """
        self._log(f"开始生成播客: {youtube_url}")
        
        # 如果Podcastfy不可用，使用备用方法
        if self.use_fallback or not self.podcastfy_client:
            self._log("使用备用播客生成方法")
            return "fallback_mode"  # 标识使用备用模式
        
        try:
            # 强化URL和字符串清理 - 移除所有不可打印字符
            def clean_string(s: str) -> str:
                """彻底清理字符串中的不可打印字符"""
                if not s:
                    return ""
                # 转换为字符串并严格清理所有控制字符
                s_str = str(s).strip()
                # 移除所有控制字符包括换行符、制表符等
                cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', s_str)
                # 特殊处理URL - 移除换行但保留基本字符
                if 'youtube.com' in s_str or 'youtu.be' in s_str:
                    # 对于URL，更严格地清理
                    cleaned = re.sub(r'[\r\n\t\v\f]', '', cleaned)
                    # 只保留ASCII字符用于URL
                    cleaned = re.sub(r'[^\x20-\x7e]', '', cleaned)
                else:
                    # 对于其他字符串，保留中文字符
                    cleaned = re.sub(r'[^\x20-\x7e\u4e00-\u9fff]', '', cleaned)
                # 规范化空白字符
                cleaned = re.sub(r'\s+', ' ', cleaned.strip())
                # 限制长度并确保结果有效
                return cleaned[:500] if cleaned else ""
            
            # 清理所有输入参数
            clean_url = clean_string(youtube_url)
            clean_style = clean_string(custom_style)
            clean_language = clean_string(target_language)
            clean_instructions = clean_string(f"请生成一个关于YouTube视频的中文播客，目标语言是{clean_language}，内容要适合英语学习者收听")
            
            self._log(f"🔍 清理后的URL: {clean_url}")
            self._log(f"🔍 URL长度: {len(clean_url)}, URL字符检查: {repr(clean_url)}")
            self._log(f"🎭 清理后的风格: {clean_style}")
            
            # 额外验证所有参数不包含非打印字符
            all_params = {
                'clean_url': clean_url,
                'clean_style': clean_style,
                'clean_language': clean_language,
                'clean_instructions': clean_instructions,
                'gemini_key': clean_string(self.config['GEMINI_API_KEY'])[:10] + "...",
                'elevenlabs_key': clean_string(self.config.get('ELEVENLABS_API_KEY', ''))[:10] + "..."
            }
            
            # 检查每个参数是否包含非打印字符
            for param_name, param_value in all_params.items():
                if param_value and any(ord(c) < 32 or ord(c) > 126 for c in str(param_value) if c not in '一二三四五六七八九十'):
                    self._log(f"⚠️ 参数{param_name}可能包含问题字符，长度: {len(param_value)}", "warning")
                    # 显示前50个字符用于调试
                    self._log(f"   内容预览: {repr(str(param_value)[:50])}", "debug")
            
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
            notebooklm_instructions = f"""
            生成NotebookLM风格的纯对话播客，要求：
            1. 绝对禁止开场白、介绍、总结、结束语
            2. 只能是两个人的自然对话，一问一答
            3. 像真实朋友聊天，深入讨论视频内容
            4. 不要任何"欢迎来到播客"等话语
            5. 直接开始讨论，自然结束
            6. 保持口语化、真实、有深度的对话风格
            目标语言：{target_language}
            """
            
            result = self.podcastfy_client.predict(
                text_input="",
                urls_input=clean_url,
                pdf_files=[],
                image_files=[],
                gemini_key=clean_string(self.config['GEMINI_API_KEY']),
                openai_key="",  # 使用Edge TTS，不需要OpenAI密钥
                elevenlabs_key=clean_string(self.config.get('ELEVENLABS_API_KEY', "")),
                word_count=1200,  # 更精炼的对话长度
                conversation_style=clean_string("natural,deep,conversational"),
                roles_person1=clean_string("A"),  # 简化角色名
                roles_person2=clean_string("B"),
                dialogue_structure=clean_string("对话"),  # 禁用结构化的章节
                podcast_name=clean_string(""),  # 禁用播客名称
                podcast_tagline=clean_string(""),  # 禁用标语
                tts_model="elevenlabs",  # 优先使用ElevenLabs获得最佳音质
                creativity_level=0.8,  # 增加创造力，使对话更自然
                user_instructions=clean_string(notebooklm_instructions),
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
            
            # 使用ffmpeg将音频和图片合成视频
            ffmpeg_cmd = [
                'ffmpeg', '-y',  # -y 覆盖输出文件
                '-loop', '1',  # 循环图片
                '-i', thumbnail_path,  # 输入图片
                '-i', audio_path,  # 输入音频
                '-c:v', 'libx264',  # 视频编码
                '-c:a', 'aac',  # 音频编码
                '-b:a', '192k',  # 音频比特率
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
    
    def _create_audio_video_fallback(self, audio_path: str, thumbnail_path: str, output_path: str) -> bool:
        """使用moviepy作为备用方案生成音频视频"""
        try:
            # 动态导入moviepy以避免必须依赖
            if not MOVIEPY_AVAILABLE:
                raise ImportError("MoviePy not available")
            from moviepy.editor import AudioFileClip, ImageClip
            
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
    
    def upload_to_youtube(self, video_path: str, _video_info: Dict[str, Any], 
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
                    'privacyStatus': 'public',  # 或者使用 'unlisted' 进行测试
                    'selfDeclaredMadeForKids': False
                }
            }
            
            self._log("开始上传到YouTube...")
            
            # 执行上传
            from googleapiclient.http import MediaFileUpload
            
            media = MediaFileUpload(
                video_path,
                chunksize=-1,  # 一次性上传
                resumable=True,
                mimetype='video/*'
            )
            
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = request.execute()
            
            if 'id' in response:
                video_id = response['id']
                youtube_link = f"https://www.youtube.com/watch?v={video_id}"
                self._log(f"✅ YouTube上传成功: {youtube_link}")
                return video_id
            else:
                self._log("YouTube上传失败：未返回视频ID")
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
{f"<iframe width='560' height='315' src='https://www.youtube.com/embed/{youtube_video_id}' frameborder='0' allowfullscreen></iframe>" if youtube_video_id else ""}

{f"🎙️ **[在YouTube上收听完整播客](https://www.youtube.com/watch?v={youtube_video_id})**" if youtube_video_id else ""}

<!-- 本地音频备用 -->
<audio controls>
  <source src="{audio_relative}" type="audio/mpeg">
  您的浏览器不支持音频播放。
</audio>

*建议配合原视频观看，通过中文播客快速理解英文内容精华*''' if audio_relative else f'''
{f"<iframe width='560' height='315' src='https://www.youtube.com/embed/{youtube_video_id}' frameborder='0' allowfullscreen></iframe>" if youtube_video_id else ""}

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
            self._log(f"开始处理YouTube视频: {youtube_url}")
            
            # 1. 提取视频ID
            video_id = self.extract_video_id(youtube_url)
            self._log(f"视频ID: {video_id}")
            
            # 2. 获取视频信息
            video_info = self.get_video_info(video_id)
            self._log(f"视频标题: {video_info['title']}")
            
            # 3. 生成播客
            self._log("正在生成中文播客（预计1-3分钟）...")
            temp_audio_path = self.generate_podcast(youtube_url, conversation_style, target_language)
            
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
                    if self.generate_local_audio(script, audio_path, tts_engine):
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