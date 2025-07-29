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
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlparse, parse_qs
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
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_apis(self):
        """设置API连接"""
        # 设置Gemini API
        if 'GEMINI_API_KEY' in self.config:
            genai.configure(api_key=self.config['GEMINI_API_KEY'])
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            self.logger.info("Gemini API 配置完成")
        else:
            raise ValueError("需要GEMINI_API_KEY配置")
        
        # 设置YouTube API
        if 'YOUTUBE_API_KEY' in self.config:
            self.youtube = build('youtube', 'v3', developerKey=self.config['YOUTUBE_API_KEY'])
            self.logger.info("YouTube API 配置完成")
        else:
            self.logger.warning("未配置YOUTUBE_API_KEY，将使用基础视频信息提取")
            self.youtube = None
        
        # 设置Podcastfy客户端
        try:
            self.podcastfy_client = Client("thatupiso/Podcastfy.ai_demo")
            self.logger.info("Podcastfy 客户端连接成功")
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
    
    def generate_podcast_script(self, video_info: Dict[str, Any], youtube_url: str, 
                              target_language: str = "zh-CN",
                              conversation_style: str = "casual,informative") -> str:
        """
        生成播客脚本（备用方法）
        """
        self.logger.info("开始生成播客脚本")
        
        prompt = f"""
        请为以下YouTube视频生成一个中文播客脚本，包含两个主播的对话：

        视频标题: {video_info['title']}
        视频描述: {video_info['description'][:500]}...
        频道: {video_info['channel_title']}
        时长: {video_info['duration']}
        
        要求：
        1. 生成一个约5-8分钟的播客对话脚本
        2. 两个角色：主播助手（负责介绍和总结）和学习导师（负责提问和解释）
        3. 对话风格：{conversation_style}
        4. 目标语言：{target_language}
        5. 内容要适合英语学习者收听
        6. 包含以下结构：
           - 开场白（30秒）
           - 内容总结（3-4分钟）
           - 学习要点（2-3分钟）
           - 结语（30秒）
        
        请以以下格式输出：
        [主播助手]: 对话内容
        [学习导师]: 对话内容
        
        确保对话自然流畅，信息丰富且具有教育价值。
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

    def generate_local_audio(self, script: str, output_path: str) -> bool:
        """
        使用本地TTS生成音频
        """
        try:
            import pyttsx3
            
            # 初始化TTS引擎
            engine = pyttsx3.init()
            
            # 设置语音属性
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'chinese' in voice.name.lower() or 'mandarin' in voice.name.lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.8)
            
            # 处理脚本，移除角色标签
            clean_text = re.sub(r'\[.*?\]:\s*', '', script)
            
            # 生成音频
            engine.save_to_file(clean_text, output_path)
            engine.runAndWait()
            
            self.logger.info(f"本地音频生成成功: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"本地音频生成失败: {e}")
            return False

    def generate_podcast(self, youtube_url: str, custom_style: str = "casual,informative", 
                        tts_model: str = "edge", target_language: str = "zh-CN") -> str:
        """
        生成播客音频
        
        Args:
            youtube_url: YouTube视频链接
            custom_style: 播客风格
            tts_model: TTS模型选择 ("edge", "openai", "elevenlabs", "geminimulti")
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
            # 确保URL格式正确，去除可能的换行符和空格
            clean_url = youtube_url.strip()
            self.logger.info(f"处理的URL: {clean_url}")
            
            # 使用正确的API端点和参数
            result = self.podcastfy_client.predict(
                text_input="",
                urls_input=clean_url,
                pdf_files=[],
                image_files=[],
                gemini_key=self.config['GEMINI_API_KEY'],
                openai_key="",  # 使用Edge TTS，不需要OpenAI密钥
                elevenlabs_key="",  # 不使用ElevenLabs
                word_count=1500,
                conversation_style=custom_style,
                roles_person1="主播助手",  # 新增角色1
                roles_person2="学习导师",  # 新增角色2
                dialogue_structure="引言,内容总结,学习要点,结语",  # 新增对话结构
                podcast_name="全球视野英语学习",
                podcast_tagline="用中文播客理解英文内容",
                tts_model=tts_model,  # 使用指定的TTS模型
                creativity_level=0.7,
                user_instructions=f"请生成一个关于YouTube视频的中文播客，目标语言是{target_language}，内容要适合英语学习者收听。".replace('\n', ' '),  # 新增用户指令
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
    
    def generate_content_guide(self, video_info: Dict[str, Any], youtube_url: str) -> Dict[str, Any]:
        """
        生成中文导读内容
        
        Args:
            video_info: 视频信息
            youtube_url: 视频链接
            
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
    
    def download_thumbnail(self, thumbnail_url: str, video_id: str) -> str:
        """
        下载视频缩略图
        
        Args:
            thumbnail_url: 缩略图URL
            video_id: 视频ID
            
        Returns:
            本地缩略图路径
        """
        try:
            # 创建按日期组织的目录
            today = datetime.now()
            date_dir = os.path.join(self.image_dir, str(today.year), f"{today.month:02d}")
            os.makedirs(date_dir, exist_ok=True)
            
            # 生成文件名
            thumbnail_filename = f"youtube-{today.strftime('%Y%m%d')}-{video_id}-thumbnail.jpg"
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
                            youtube_url: str, audio_path: str, thumbnail_path: str) -> str:
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
        
        # 生成文件名
        video_id = self.extract_video_id(youtube_url)
        article_filename = f"{today.strftime('%Y-%m-%d')}-youtube-learning-{video_id}.md"
        article_path = os.path.join(self.draft_dir, article_filename)
        
        # 生成相对路径（用于Jekyll）
        audio_relative = audio_path.replace("assets/", "{{ site.baseurl }}/assets/")
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
<audio controls>
  <source src="{audio_relative}" type="audio/mpeg">
  您的浏览器不支持音频播放。
</audio>

*建议配合原视频食用，通过中文播客快速理解英文内容精华*

## 📋 内容大纲
"""
        
        # 添加大纲内容
        for point in content_guide['outline']:
            article_content += f"- {point}\n"
        
        article_content += f"""
## 🌍 英语学习指南

### 🔤 关键词汇
{', '.join(content_guide['learning_tips']['vocabulary'])}

### 💬 常用表达
{', '.join(content_guide['learning_tips']['expressions'])}

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
            temp_audio_path = self.generate_podcast(youtube_url, conversation_style, tts_model, target_language)
            
            # 检查是否使用备用模式
            if temp_audio_path == "fallback_mode":
                self.logger.info("使用备用播客生成模式")
                # 生成播客脚本
                script = self.generate_podcast_script(video_info, youtube_url, target_language, conversation_style)
                
                # 尝试生成本地音频
                today = datetime.now()
                audio_filename = f"youtube-{today.strftime('%Y%m%d')}-{video_id}.wav"
                audio_path = os.path.join(self.audio_dir, audio_filename)
                
                if self.generate_local_audio(script, audio_path):
                    self.logger.info(f"本地音频生成成功: {audio_path}")
                else:
                    self.logger.warning("本地音频生成失败，将只提供文本脚本")
                    # 保存脚本到文件
                    script_filename = f"youtube-{today.strftime('%Y%m%d')}-{video_id}-script.txt"
                    script_path = os.path.join(self.audio_dir, script_filename)
                    with open(script_path, 'w', encoding='utf-8') as f:
                        f.write(script)
                    audio_path = script_path
            else:
                # 使用Podcastfy生成的音频
                audio_path = self.save_audio_file(temp_audio_path, video_id)
            
            # 4. 生成导读内容
            content_guide = self.generate_content_guide(video_info, youtube_url)
            if custom_title:
                content_guide['title'] = custom_title
            
            # 5. 下载缩略图
            thumbnail_path = self.download_thumbnail(video_info['thumbnail_url'], video_id)
            
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