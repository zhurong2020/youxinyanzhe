#!/usr/bin/env python3
"""
YouTube播客生成器
将英文YouTube视频转换为中文播客和导读文章，用于英语学习
"""

import os
import re
import json
import requests
from datetime import datetime
from typing import Dict, Any, Optional
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
    from elevenlabs import Voice, VoiceSettings, generate, set_api_key
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

# Markdown和音频处理
try:
    from markdown_it import MarkdownIt
    from bs4 import BeautifulSoup
    # AudioSegment 在需要时动态导入
    MARKDOWN_AUDIO_TOOLS_AVAILABLE = True
except ImportError:
    MARKDOWN_AUDIO_TOOLS_AVAILABLE = False


class YouTubePodcastGenerator:
    """YouTube播客生成器类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化生成器
        
        Args:
            config: 配置字典，包含API密钥等
        """
        self.config = config
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
        """设置日志 - 避免重复配置"""
        self.logger = logging.getLogger(__name__)
        
        # 检查是否已经配置过处理器，避免重复日志
        if not self.logger.handlers:
            # 只有在没有处理器时才添加
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def setup_apis(self):
        """设置API连接"""
        # 设置Gemini API
        if 'GEMINI_API_KEY' in self.config:
            genai.configure(api_key=self.config['GEMINI_API_KEY'])
            # 使用与主系统一致的模型配置（从配置文件读取）
            model_name = "gemini-2.5-flash"  # 默认模型
            self.gemini_model = genai.GenerativeModel(model_name)
            self.logger.info(f"✅ Gemini配置完成 - 模型: {model_name}")
        else:
            raise ValueError("需要GEMINI_API_KEY配置")
        
        # 设置YouTube API
        if 'YOUTUBE_API_KEY' in self.config:
            self.youtube = build('youtube', 'v3', developerKey=self.config['YOUTUBE_API_KEY'])
            self.logger.info("✅ YouTube API 配置完成")
        else:
            self.logger.warning("未配置YOUTUBE_API_KEY，将使用基础视频信息提取")
            self.youtube = None
        
        # 设置ElevenLabs API
        if 'ELEVENLABS_API_KEY' in self.config and ELEVENLABS_AVAILABLE:
            try:
                from elevenlabs import set_api_key
                set_api_key(self.config['ELEVENLABS_API_KEY'])
                self.elevenlabs_available = True
                self.logger.info("✅ ElevenLabs API 配置完成")
            except Exception as e:
                self.logger.warning(f"ElevenLabs API 配置失败: {e}")
                self.elevenlabs_available = False
        else:
            self.elevenlabs_available = False
            if not ELEVENLABS_AVAILABLE:
                self.logger.info("💡 ElevenLabs库未安装，可运行 pip install elevenlabs 获得高质量语音")
        
        # 设置Podcastfy客户端
        try:
            self.podcastfy_client = Client("thatupiso/Podcastfy.ai_demo")
            self.logger.info("✅ Podcastfy 客户端连接成功")
            self.use_fallback = False
            
        except Exception as e:
            self.logger.warning(f"Podcastfy 客户端连接失败: {e}")
            self.logger.info("将使用备用播客生成器")
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
                self.logger.error(f"YouTube API调用失败: {e}")
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
            items: 可能是字符串或数组
            
        Returns:
            格式化后的字符串
        """
        try:
            if isinstance(items, list):
                # 如果是数组，用逗号和空格连接
                return ', '.join(items)
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
        生成播客脚本（备用方法）
        """
        self.logger.info("开始生成播客脚本")
        
        # 解析视频时长，智能调整播客长度
        duration_str = video_info.get('duration', '未知')
        try:
            # 尝试从时长字符串中提取分钟数
            import re
            duration_match = re.search(r'(\d+)分钟|(\d+):\d+', duration_str)
            if duration_match:
                video_minutes = int(duration_match.group(1) or duration_match.group(2))
                # 播客长度不超过原视频的80%，但至少5分钟
                podcast_minutes = max(5, min(10, int(video_minutes * 0.8)))
                word_count = podcast_minutes * 250  # 每分钟约250字
            else:
                podcast_minutes = 6
                word_count = 1500
        except:
            # 默认值
            podcast_minutes = 6
            word_count = 1500
        
        prompt = f"""
        请为以下YouTube视频生成一个简洁高效的中文播客脚本，包含两个主播的对话：

        视频标题: {video_info['title']}
        视频描述: {video_info['description'][:1000] if video_info['description'] else '暂无描述'}
        频道: {video_info['channel_title']}
        时长: {video_info['duration']}
        
        要求：
        1. 生成约{podcast_minutes}分钟的播客脚本（约{word_count}字）
        2. 两个角色：
           - 主播助手：负责引导话题、总结要点
           - 学习导师：负责核心分析、提供学习建议
        3. 对话风格：{conversation_style}，保持专业且简洁
        4. 目标语言：{target_language}
        5. 内容结构：
           - 简要开场和背景（30秒）
           - 核心内容精华解析（{podcast_minutes-2}分钟）
           - 学习要点总结（1分钟）
           - 简短结语（30秒）
        6. 重点突出，避免冗长重复，确保每句话都有价值
        
        请以以下格式输出：
        [主播助手]: 对话内容
        [学习导师]: 对话内容
        
        确保对话紧凑高效，信息密度高。
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            script = response.text
            self.logger.info("播客脚本生成成功")
            return script
        except Exception as e:
            self.logger.error(f"播客脚本生成失败: {e}")
            return f"""
[主播助手]: 大家好，欢迎收听全球视野英语学习播客。今天我们要讨论的是YouTube视频《{video_info['title']}》。

[学习导师]: 这个视频来自{video_info['channel_title']}频道，时长{video_info['duration']}。让我们一起来了解其中的精彩内容。

[主播助手]: 建议大家先听我们的中文导读，然后再观看原版视频，这样能更好地理解内容。

[学习导师]: 好的，今天的播客就到这里。记得点击原视频链接深入学习！
"""

    def generate_local_audio(self, script: str, output_path: str, tts_engine: str = "gtts") -> bool:
        """
        使用本地TTS生成音频，支持多种TTS引擎
        
        Args:
            script: 播客脚本
            output_path: 输出音频文件路径
            tts_engine: TTS引擎选择 ("gtts", "elevenlabs", "espeak", "pyttsx3")
        """
        # 移除角色标签
        script = re.sub(r'\[.*?\]:\s*', '', script)

        # 使用markdown-it-py和BeautifulSoup进行可靠的文本清理
        if MARKDOWN_AUDIO_TOOLS_AVAILABLE:
            try:
                from markdown_it import MarkdownIt
                from bs4 import BeautifulSoup
                md = MarkdownIt()
                html = md.render(script)
                soup = BeautifulSoup(html, 'html.parser')
                clean_text = soup.get_text()
            except ImportError:
                # Fallback to basic regex cleaning
                self.logger.warning("Markdown/Audio tools import failed. Using basic text cleaning.")
                clean_text = re.sub(r'<[^>]+>', '', script)
        else:
            # Fallback to basic regex cleaning if libraries are not available
            self.logger.warning("Markdown/Audio tools not found. Using basic text cleaning.")
            clean_text = re.sub(r'<[^>]+>', '', script) # Basic HTML tag removal

        # 移除多余的空白
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        self.logger.info(f"🎧 开始音频生成 - 引擎: {tts_engine}, 文本长度: {len(clean_text)}字符")
        
        # 对于超长文本，gTTS库会自动分块处理，无需人为截断
        if len(clean_text) > 5000:
            self.logger.info("💡 检测到超长文本，gTTS将自动分块处理以保证完整性")
        
        # 1. 优先尝试ElevenLabs（最高音质）
        if tts_engine == "elevenlabs":
            if self._generate_elevenlabs_audio(clean_text, output_path):
                return True
            self.logger.warning("ElevenLabs失败，尝试其他引擎")
        
        # 2. 尝试Google TTS（高音质）
        if tts_engine == "gtts":
            if self._generate_gtts_audio(clean_text, output_path):
                return True
            self.logger.warning("Google TTS失败，尝试其他引擎")
        
        # 3. 尝试eSpeak（快速但音质一般）
        if tts_engine == "espeak" or tts_engine == "gtts":
            if self._generate_espeak_audio(clean_text, output_path):
                return True
            self.logger.warning("eSpeak TTS失败，尝试pyttsx3")
            
        # 4. 最后尝试pyttsx3（系统TTS）
        if self._generate_pyttsx3_audio(clean_text, output_path):
            return True
            
        self.logger.error("所有TTS引擎都失败了")
        return False
    
    def _generate_elevenlabs_audio(self, text: str, output_path: str) -> bool:
        """使用ElevenLabs生成高质量AI语音"""
        if not self.elevenlabs_available:
            self.logger.warning("ElevenLabs API未配置或库未安装")
            return False
            
        try:
            from elevenlabs import Voice, VoiceSettings, generate
            
            self.logger.info("🎙️ 使用ElevenLabs生成高质量AI语音")
            
            # 使用ElevenLabs的中文语音模型
            # 注意：这里使用的是一个通用的英文声音，ElevenLabs对中文支持可能有限
            audio = generate(
                text=text,
                voice=Voice(
                    voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel (女声，适合叙述)
                    settings=VoiceSettings(
                        stability=0.75,    # 语音稳定性
                        similarity_boost=0.75,  # 相似度增强
                        style=0.1,         # 风格强度
                        use_speaker_boost=True  # 使用说话者增强
                    )
                ),
                model="eleven_multilingual_v2"  # 多语言模型，支持中文
            )
            
            # 保存音频文件
            with open(output_path, 'wb') as f:
                f.write(audio)
            
            self.logger.info(f"✅ ElevenLabs音频生成成功: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ ElevenLabs音频生成失败: {e}")
            return False

    def _generate_gtts_audio(self, text: str, output_path: str) -> bool:
        """使用Google Text-to-Speech生成高质量音频并加速"""
        try:
            from gtts import gTTS
            
            self.logger.info("尝试使用Google TTS生成音频")
            
            # 创建gTTS对象
            tts = gTTS(text=text, lang='zh-CN', slow=False)
            
            # 保存到临时文件
            temp_path = output_path.replace('.wav', '_temp.mp3')
            tts.save(temp_path)
            
            # 加速音频
            if MARKDOWN_AUDIO_TOOLS_AVAILABLE:
                try:
                    from pydub import AudioSegment
                    self.logger.info("加速音频至1.5倍速")
                    sound = AudioSegment.from_mp3(temp_path)
                    fast_sound = sound.speedup(playback_speed=1.5)
                    
                    # 导出加速后的音频
                    fast_sound.export(temp_path, format="mp3")
                except ImportError:
                    self.logger.warning("pydub未安装，跳过音频加速")

            # 如果需要WAV格式，转换音频格式
            if output_path.endswith('.wav'):
                self._convert_audio_format(temp_path, output_path)
                os.remove(temp_path)  # 删除临时文件
            else:
                # 直接重命名为最终文件
                os.rename(temp_path, output_path)
            
            if os.path.exists(output_path):
                self.logger.info(f"Google TTS音频生成成功: {output_path}")
                return True
            else:
                self.logger.error("Google TTS未能创建音频文件")
                return False
                
        except ImportError:
            self.logger.warning("gtts库未安装，跳过Google TTS。安装命令: pip install gtts pygame")
            return False
        except Exception as e:
            self.logger.warning(f"Google TTS生成失败: {e}")
            return False
    
    def _generate_espeak_audio(self, text: str, output_path: str) -> bool:
        """
        使用eSpeak生成音频
        """
        try:
            import subprocess
            
            self.logger.info("尝试使用eSpeak TTS生成音频")
            
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
                    
                    self.logger.info(f"执行eSpeak命令: {' '.join(cmd[:6])}...")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0 and os.path.exists(output_file):
                        self.logger.info(f"eSpeak音频生成成功: {output_file}")
                        # 如果生成的不是目标格式，重命名
                        if output_file != output_path:
                            os.rename(output_file, output_path)
                        return True
                    else:
                        self.logger.warning(f"eSpeak生成失败，返回码: {result.returncode}")
                        if result.stderr:
                            self.logger.warning(f"eSpeak错误: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    self.logger.warning("eSpeak执行超时")
                except Exception as e:
                    self.logger.warning(f"eSpeak格式{audio_format}失败: {e}")
                    continue
                    
            return False
            
        except Exception as e:
            self.logger.warning(f"eSpeak生成失败: {e}")
            return False
    
    def _generate_pyttsx3_audio(self, text: str, output_path: str) -> bool:
        """
        使用pyttsx3生成音频
        """
        try:
            import pyttsx3
            
            self.logger.info("尝试使用pyttsx3 TTS生成音频")
            
            # 初始化TTS引擎
            engine = pyttsx3.init()
            
            # 设置语音属性
            voices = engine.getProperty('voices')
            chinese_voice_found = False
            
            if voices and hasattr(voices, '__len__') and hasattr(voices, '__iter__'):
                self.logger.info(f"可用语音数量: {len(voices)}")
                for i, voice in enumerate(voices):
                    if hasattr(voice, 'name') and hasattr(voice, 'id'):
                        self.logger.debug(f"语音{i}: {voice.name} - {voice.id}")
                        # 更宽松的中文语音匹配
                        if any(keyword in voice.name.lower() for keyword in ['chinese', 'mandarin', 'zh', 'china']):
                            engine.setProperty('voice', voice.id)
                            chinese_voice_found = True
                            self.logger.info(f"选择中文语音: {voice.name}")
                            break
            
            if not chinese_voice_found:
                self.logger.warning("未找到中文语音，使用默认语音")
            
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.8)
            
            # 生成音频
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
            if os.path.exists(output_path):
                self.logger.info(f"pyttsx3音频生成成功: {output_path}")
                return True
            else:
                self.logger.error("pyttsx3未能创建音频文件")
                return False
                
        except ImportError:
            self.logger.warning("pyttsx3库未安装，跳过。安装命令: pip install pyttsx3")
            return False
        except Exception as e:
            self.logger.warning(f"pyttsx3生成失败: {e}")
            return False
    
    def _convert_audio_format(self, input_path: str, output_path: str) -> bool:
        """转换音频格式（MP3转WAV等）"""
        try:
            from pydub import AudioSegment
            
            # 读取输入音频
            audio = AudioSegment.from_file(input_path)
            
            # 导出为目标格式
            audio.export(output_path, format="wav")
            
            self.logger.info(f"音频格式转换成功: {input_path} -> {output_path}")
            return True
            
        except ImportError:
            self.logger.warning("pydub库未安装，无法转换音频格式。安装命令: pip install pydub")
            # 如果无法转换，直接复制文件
            import shutil
            shutil.copy2(input_path, output_path)
            return True
        except Exception as e:
            self.logger.warning(f"音频格式转换失败: {e}")
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
        self.logger.info(f"开始生成播客: {youtube_url}")
        
        # 如果Podcastfy不可用，使用备用方法
        if self.use_fallback or not self.podcastfy_client:
            self.logger.info("使用备用播客生成方法")
            return "fallback_mode"  # 标识使用备用模式
        
        try:
            # 清理URL
            clean_url = youtube_url.strip()
            
            # 强化URL和字符串清理 - 移除所有不可打印字符
            def clean_string(s: str) -> str:
                """清理字符串中的不可打印字符"""
                if not s:
                    return ""
                # 移除换行符、回车符、制表符等不可打印字符
                cleaned = re.sub(r'[\n\r\t\x00-\x1f\x7f-\x9f]', '', str(s).strip())
                return cleaned
            
            clean_style = clean_string(custom_style)
            clean_language = clean_string(target_language)
            clean_instructions = clean_string(f"请生成一个关于YouTube视频的中文播客，目标语言是{clean_language}，内容要适合英语学习者收听")
            
            self.logger.info(f"🔍 清理后的URL: {clean_url}")
            self.logger.info(f"🎭 清理后的风格: {clean_style}")
            
            # 使用正确的API端点和参数
            result = self.podcastfy_client.predict(
                text_input="",
                urls_input=clean_url,
                pdf_files=[],
                image_files=[],
                gemini_key=clean_string(self.config['GEMINI_API_KEY']),
                openai_key="",  # 使用Edge TTS，不需要OpenAI密钥
                elevenlabs_key=clean_string(self.config.get('ELEVENLABS_API_KEY', "")),
                word_count=1500,
                conversation_style=clean_style,
                roles_person1=clean_string("主播助手"),
                roles_person2=clean_string("学习导师"),
                dialogue_structure=clean_string("引言,内容总结,学习要点,结语"),
                podcast_name=clean_string("全球视野英语学习"),
                podcast_tagline=clean_string("用中文播客理解英文内容"),
                tts_model="edge",  # Podcastfy只支持edge, openai, elevenlabs
                creativity_level=0.7,
                user_instructions=clean_instructions,
                api_name="/process_inputs"  # 使用正确的API端点
            )
            
            # result应该包含生成的音频文件路径
            if result and len(result) > 0:
                audio_path = result[0]  # 通常第一个元素是音频文件路径
                self.logger.info(f"播客生成成功: {audio_path}")
                return audio_path
            else:
                raise Exception("播客生成失败，未返回音频文件")
                
        except Exception as e:
            self.logger.error(f"Podcastfy播客生成失败: {e}")
            self.logger.info("切换到备用播客生成方法")
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
        self.logger.info("开始生成中文导读")
        
        prompt = f"""
        请为以下英文YouTube视频生成一篇中文导读文章，用于英语学习：

        视频标题: {video_info['title']}
        视频描述: {video_info['description'][:500]}...
        频道: {video_info['channel_title']}
        时长: {video_info['duration']}
        
        请生成以下内容：
        1. 25-35字符的中文标题（前缀：【英语学习】）
        2. 50-60字的文章摘要
        3. 4-5个要点的内容大纲
        4. 英语学习建议（关键词汇、表达方式、文化背景）
        5. 3-5个相关标签
        
        要求：
        - 强调全球视野和学习价值
        - 内容要吸引中文读者
        - 突出英语学习的实用性
        - 保持客观和专业的语调
        
        请以JSON格式返回，包含以下字段：
        - title: 文章标题
        - excerpt: 文章摘要  
        - outline: 内容大纲（数组）
        - learning_tips: 学习建议对象，包含vocabulary、expressions、cultural_context
        - tags: 标签数组
        - difficulty_level: 难度级别（初级/中级/高级）
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            content_text = response.text
            
            # 提取JSON内容
            json_match = re.search(r'\{.*\}', content_text, re.DOTALL)
            if json_match:
                content_data = json.loads(json_match.group())
                self.logger.info("导读内容生成成功")
                return content_data
            else:
                raise ValueError("无法解析Gemini返回的JSON内容")
                
        except Exception as e:
            self.logger.error(f"导读生成失败: {e}")
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
            
            self.logger.info(f"缩略图下载成功: {thumbnail_path}")
            return thumbnail_path
            
        except Exception as e:
            self.logger.error(f"缩略图下载失败: {e}")
            return ""
    
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
            
            self.logger.info(f"音频文件保存成功: {final_audio_path}")
            return final_audio_path
            
        except Exception as e:
            self.logger.error(f"音频文件保存失败: {e}")
            return temp_audio_path
    
    def create_jekyll_article(self, video_info: Dict[str, Any], content_guide: Dict[str, Any], 
                            youtube_url: str, audio_path: Optional[str] = None, thumbnail_path: str = "") -> str:
        """
        创建Jekyll格式的文章
        
        Args:
            video_info: 视频信息
            content_guide: 导读内容
            youtube_url: YouTube链接
            audio_path: 音频文件路径
            thumbnail_path: 缩略图路径
            
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
{f'''<audio controls>
  <source src="{audio_relative}" type="audio/mpeg">
  您的浏览器不支持音频播放。
</audio>

*建议配合原视频食用，通过中文播客快速理解英文内容精华*''' if audio_relative else '''
> ⚠️ **音频生成失败**：本次未能生成音频文件，但播客文本脚本已保存在 `assets/audio/` 目录中。
> 
> 建议：
> 1. 查看文本脚本了解播客内容结构
> 2. 直接观看英文原视频进行学习
> 3. 可考虑安装 eSpeak TTS 引擎以支持本地音频生成
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
            
            self.logger.info(f"Jekyll文章创建成功: {article_path}")
            return article_path
            
        except Exception as e:
            self.logger.error(f"文章创建失败: {e}")
            raise
    
    def generate_from_youtube(self, youtube_url: str, custom_title: str = "", 
                            tts_model: str = "edge", target_language: str = "zh-CN",
                            conversation_style: str = "casual,informative") -> Dict[str, str]:
        """
        从YouTube链接生成完整的播客学习资料
        
        Args:
            youtube_url: YouTube视频链接
            custom_title: 自定义标题（可选）
            tts_model: TTS模型 ("edge", "openai", "elevenlabs", "geminimulti")
            target_language: 目标语言 ("zh-CN", "en-US", "ja-JP", "ko-KR")
            conversation_style: 对话风格
            
        Returns:
            生成结果字典
        """
        try:
            self.logger.info(f"开始处理YouTube视频: {youtube_url}")
            
            # 1. 提取视频ID
            video_id = self.extract_video_id(youtube_url)
            self.logger.info(f"视频ID: {video_id}")
            
            # 2. 获取视频信息
            video_info = self.get_video_info(video_id)
            self.logger.info(f"视频标题: {video_info['title']}")
            
            # 3. 生成播客
            self.logger.info("正在生成中文播客（预计1-3分钟）...")
            temp_audio_path = self.generate_podcast(youtube_url, conversation_style, target_language)
            
            # 检查是否使用备用模式
            if temp_audio_path == "fallback_mode":
                self.logger.info("使用备用播客生成模式")
                self.logger.info(f"配置参数 - 目标语言: {target_language}, 对话风格: {conversation_style}")
                # 生成播客脚本
                script = self.generate_podcast_script(video_info, target_language, conversation_style)
                self.logger.info(f"播客脚本生成完成，长度: {len(script)}字符")
                
                # 尝试生成本地音频
                today = datetime.now()
                safe_title = self._generate_safe_filename(video_info['title'])
                audio_filename = f"youtube-{today.strftime('%Y%m%d')}-{safe_title}.wav"
                audio_path = os.path.join(self.audio_dir, audio_filename)
                
                # 总是保存播客脚本供用户查看和调试
                script_filename = f"youtube-{today.strftime('%Y%m%d')}-{safe_title}-script.txt"
                script_path = os.path.join(self.audio_dir, script_filename)
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(script)
                self.logger.info(f"📝 播客脚本已保存: {script_path}")
                
                try:
                    # 根据用户选择的TTS模型决定使用的引擎
                    if tts_model == "elevenlabs" and self.elevenlabs_available:
                        tts_engine = "elevenlabs"  # 使用ElevenLabs获得最高音质
                    elif tts_model == "edge":
                        tts_engine = "gtts"  # 使用Google TTS替代Edge TTS
                    elif tts_model == "espeak":
                        tts_engine = "espeak"
                    else:
                        # 智能默认选择：ElevenLabs > Google TTS > eSpeak
                        if self.elevenlabs_available:
                            tts_engine = "elevenlabs"
                        else:
                            tts_engine = "gtts"  # 默认使用Google TTS获得最佳音质
                    
                    self.logger.info(f"使用TTS引擎: {tts_engine}")
                    if self.generate_local_audio(script, audio_path, tts_engine):
                        self.logger.info(f"本地音频生成成功: {audio_path}")
                    else:
                        raise Exception("所有TTS引擎都不可用")
                except Exception as e:
                    self.logger.warning(f"本地音频生成失败: {e}")
                    self.logger.warning("将只提供文本脚本，请考虑安装eSpeak或其他TTS引擎")
                    # 设置音频路径为None，表示没有音频文件
                    audio_path = None
            else:
                # 使用Podcastfy生成的音频
                audio_path = self.save_audio_file(temp_audio_path, video_id)
            
            # 4. 生成导读内容
            content_guide = self.generate_content_guide(video_info)
            if custom_title:
                content_guide['title'] = custom_title
                self.logger.info(f"使用自定义标题: {custom_title}")
            
            # 5. 下载缩略图
            thumbnail_path = self.download_thumbnail(video_info['thumbnail_url'], video_info)
            if not thumbnail_path:
                self.logger.warning("缩略图下载失败")
            
            # 6. 创建Jekyll文章
            article_path = self.create_jekyll_article(
                video_info, content_guide, youtube_url, audio_path, thumbnail_path
            )
            
            result = {
                'status': 'success',
                'article_path': article_path,
                'audio_path': audio_path,
                'thumbnail_path': thumbnail_path,
                'video_title': video_info['title'],
                'article_title': content_guide['title']
            }
            
            self.logger.info("YouTube播客生成完成！")
            return result
            
        except Exception as e:
            self.logger.error(f"生成过程失败: {e}")
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