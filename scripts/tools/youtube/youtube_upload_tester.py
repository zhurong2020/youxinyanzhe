#!/usr/bin/env python3
"""
独立的YouTube音频上传测试工具
用于将assets/audio目录下的mp3文件上传到YouTube

功能：
1. 扫描并列出所有可用的音频文件
2. 选择音频文件和对应的缩略图
3. 生成视频文件（音频+静态图片）
4. 上传到YouTube
"""

import os
import sys
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv()

class YouTubeUploadTester:
    """YouTube音频上传测试工具"""
    
    def __init__(self):
        """初始化工具"""
        self.audio_dir = Path("assets/audio")
        self.image_dir = Path("assets/images")
        self.temp_dir = Path(".tmp/youtube_uploads")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 检查配置
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.oauth_credentials_file = Path("config/youtube_oauth_credentials.json")
        self.oauth_token_file = Path("config/youtube_oauth_token.json")
        self.setup_apis()
    
    def setup_apis(self):
        """设置API连接"""
        # 首先尝试OAuth2认证
        if self.setup_oauth2():
            self.youtube_available = True
            print("✅ YouTube OAuth2认证成功")
            return
        
        # 如果OAuth2失败，尝试API Key（仅用于读取操作）
        if self.youtube_api_key:
            try:
                from googleapiclient.discovery import build
                self.youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
                self.youtube_available = True
                print("⚠️ YouTube API配置成功（仅支持读取，上传需要OAuth2）")
            except ImportError:
                print("❌ 缺少依赖：pip install google-api-python-client google-auth-oauthlib")
                self.youtube_available = False
            except Exception as e:
                print(f"❌ YouTube API配置失败: {e}")
                self.youtube_available = False
        else:
            print("❌ 未配置YOUTUBE_API_KEY，且OAuth2不可用")
            self.youtube_available = False
    
    def setup_oauth2(self) -> bool:
        """设置OAuth2认证"""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            
            # YouTube上传需要的权限范围
            SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
            
            creds = None
            
            # 检查是否已有有效的token
            if self.oauth_token_file.exists():
                creds = Credentials.from_authorized_user_file(str(self.oauth_token_file), SCOPES)
            
            # 如果没有有效凭证，进行OAuth流程
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                        print("🔄 OAuth2 token已刷新")
                    except Exception as e:
                        print(f"⚠️ Token刷新失败: {e}")
                        creds = None
                
                if not creds:
                    if not self.oauth_credentials_file.exists():
                        print(f"❌ OAuth凭据文件不存在: {self.oauth_credentials_file}")
                        print("💡 运行 python scripts/tools/youtube_oauth_setup.py 获取设置帮助")
                        return False
                    
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            str(self.oauth_credentials_file), SCOPES)
                        creds = flow.run_local_server(port=8080, timeout_seconds=120)
                        print("✅ OAuth2认证完成")
                    except Exception as e:
                        print(f"❌ OAuth2认证失败: {e}")
                        return False
                
                # 保存凭证供下次使用
                self.oauth_token_file.parent.mkdir(exist_ok=True)
                with open(self.oauth_token_file, 'w') as token:
                    token.write(creds.to_json())
                print(f"💾 OAuth2 token已保存: {self.oauth_token_file}")
            
            # 创建YouTube服务对象
            self.youtube = build('youtube', 'v3', credentials=creds)
            self.oauth_available = True
            return True
            
        except ImportError:
            print("❌ 缺少依赖：pip install google-auth-oauthlib google-auth-httplib2")
            return False
        except Exception as e:
            print(f"❌ OAuth2设置失败: {e}")
            return False
    
    def scan_audio_files(self) -> List[Dict[str, Any]]:
        """扫描音频文件"""
        if not self.audio_dir.exists():
            print(f"❌ 音频目录不存在: {self.audio_dir}")
            return []
        
        audio_files = []
        supported_formats = ['.mp3', '.wav', '.m4a', '.aac']
        
        for file_path in self.audio_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                # 获取文件信息
                file_info = {
                    'path': file_path,
                    'name': file_path.name,
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                    'format': file_path.suffix.lower()
                }
                
                # 尝试从文件名推断相关信息
                file_info.update(self.parse_filename(file_path.name))
                audio_files.append(file_info)
        
        # 按修改时间排序（最新的在前）
        audio_files.sort(key=lambda x: x['modified'], reverse=True)
        return audio_files
    
    def parse_filename(self, filename: str) -> Dict[str, str]:
        """从文件名解析信息"""
        info = {
            'title': filename,
            'date': '',
            'type': 'unknown'
        }
        
        # 尝试解析YouTube播客文件名格式：youtube-YYYYMMDD-title.mp3
        youtube_pattern = r'youtube-(\d{8})-(.*?)\..*'
        match = re.match(youtube_pattern, filename)
        if match:
            date_str, title_part = match.groups()
            try:
                date_obj = datetime.strptime(date_str, '%Y%m%d')
                info['date'] = date_obj.strftime('%Y-%m-%d')
                info['title'] = title_part.replace('-', ' ').title()
                info['type'] = 'youtube_podcast'
            except ValueError:
                pass
        
        return info
    
    def find_thumbnail_for_audio(self, audio_file: Dict[str, Any]) -> Optional[Path]:
        """为音频文件查找对应的缩略图"""
        audio_path = audio_file['path']
        audio_name = audio_path.stem
        
        # 查找可能的缩略图文件
        thumbnail_patterns = [
            f"{audio_name}-thumbnail.*",
            f"{audio_name}.*",
            f"*{audio_name}*thumbnail*",
        ]
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        
        for pattern in thumbnail_patterns:
            for image_file in self.image_dir.rglob(pattern):
                if image_file.suffix.lower() in image_extensions:
                    return image_file
        
        # 如果没找到，查找默认缩略图
        default_thumbnails = [
            "default-thumbnail.jpg",
            "podcast-thumbnail.jpg",
            "youtube-thumbnail.jpg"
        ]
        
        for default_name in default_thumbnails:
            default_path = self.image_dir / default_name
            if default_path.exists():
                return default_path
        
        return None
    
    def create_default_thumbnail(self, title: str) -> Optional[Path]:
        """创建默认缩略图"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建1280x720的图片（YouTube推荐分辨率）
            img = Image.new('RGB', (1280, 720), color='#1a1a1a')
            draw = ImageDraw.Draw(img)
            
            # 尝试使用系统字体
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            # 绘制标题
            text_lines = self.wrap_text(title, 30)  # 每行最多30个字符
            y_offset = 300
            
            for line in text_lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (1280 - text_width) // 2
                draw.text((x, y_offset), line, fill='white', font=font)
                y_offset += 60
            
            # 保存图片
            thumbnail_path = self.temp_dir / f"default_thumbnail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            img.save(thumbnail_path, 'JPEG', quality=95)
            return thumbnail_path
            
        except ImportError:
            print("⚠️ PIL库未安装，无法生成默认缩略图")
            return None
        except Exception as e:
            print(f"❌ 生成默认缩略图失败: {e}")
            return None
    
    def wrap_text(self, text: str, width: int) -> List[str]:
        """文本换行"""
        words = text.split()
        lines = []
        current_line: List[str] = []
        
        for word in words:
            if len(' '.join(current_line + [word])) <= width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def create_video_from_audio(self, audio_path: Path, thumbnail_path: Path, output_path: Path) -> bool:
        """将音频和缩略图合成为视频"""
        try:
            print(f"🔄 正在生成视频文件...")
            print(f"   音频: {audio_path}")
            print(f"   缩略图: {thumbnail_path}")
            print(f"   输出: {output_path}")
            
            # 使用ffmpeg合成视频
            cmd = [
                'ffmpeg', '-y',  # -y 覆盖输出文件
                '-loop', '1',  # 循环图片
                '-i', str(thumbnail_path),  # 输入图片
                '-i', str(audio_path),  # 输入音频
                '-c:v', 'libx264',  # 视频编码
                '-c:a', 'aac',  # 音频编码
                '-b:a', '192k',  # 音频比特率
                '-pix_fmt', 'yuv420p',  # 像素格式
                '-shortest',  # 以最短的输入为准
                '-loglevel', 'error',  # 只显示错误
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print(f"✅ 视频生成成功: {output_path}")
                return True
            else:
                print(f"❌ ffmpeg错误: {result.stderr}")
                return self.create_video_fallback(audio_path, thumbnail_path, output_path)
                
        except FileNotFoundError:
            print("❌ ffmpeg未安装，尝试使用备用方案")
            return self.create_video_fallback(audio_path, thumbnail_path, output_path)
        except subprocess.TimeoutExpired:
            print("❌ 视频生成超时")
            return False
        except Exception as e:
            print(f"❌ 视频生成失败: {e}")
            return False
    
    def create_video_fallback(self, audio_path: Path, thumbnail_path: Path, output_path: Path) -> bool:
        """使用moviepy作为备用方案"""
        try:
            # 条件导入 MoviePy - 仅在需要时加载，避免 Pylance 导入警告
            from moviepy.editor import AudioFileClip, ImageClip  # type: ignore[import]
            
            print("🔄 使用moviepy生成视频...")
            
            # 加载音频和图片
            audio_clip = AudioFileClip(str(audio_path))
            image_clip = ImageClip(str(thumbnail_path)).set_duration(audio_clip.duration)
            
            # 设置视频分辨率
            image_clip = image_clip.resize(height=720)  # 720p
            
            # 合成视频
            video_clip = image_clip.set_audio(audio_clip)
            
            # 导出视频
            video_clip.write_videofile(
                str(output_path),
                fps=1,  # 静态图片，低帧率即可
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            # 清理资源
            audio_clip.close()
            image_clip.close()
            video_clip.close()
            
            print(f"✅ moviepy视频生成成功: {output_path}")
            return True
            
        except ImportError:
            print("❌ moviepy未安装，无法生成视频。请安装: pip install moviepy")
            return False
        except Exception as e:
            print(f"❌ moviepy生成失败: {e}")
            return False
    
    def upload_to_youtube(self, video_path: Path, title: str, description: str = "") -> Optional[str]:
        """上传视频到YouTube"""
        if not self.youtube_available:
            print("❌ YouTube API不可用")
            return None
        
        if not hasattr(self, 'oauth_available') or not self.oauth_available:
            print("❌ YouTube上传需要OAuth2认证，当前仅有API Key无法上传")
            print("💡 请运行 python scripts/tools/youtube_oauth_setup.py 设置OAuth2认证")
            return None
        
        try:
            from googleapiclient.http import MediaFileUpload
            
            # 准备视频元数据
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube标题限制
                    'description': description[:5000],  # YouTube描述限制
                    'tags': ['播客', '音频', '学习', '中文'],
                    'categoryId': '27',  # Education类别
                    'defaultLanguage': 'zh-CN',
                    'defaultAudioLanguage': 'zh-CN'
                },
                'status': {
                    'privacyStatus': 'unlisted',  # 不公开（通过链接可访问）
                    'selfDeclaredMadeForKids': False
                }
            }
            
            print(f"🔄 开始上传到YouTube...")
            print(f"   标题: {title}")
            print(f"   隐私: 不公开（通过链接可访问）")
            
            # 执行上传
            media = MediaFileUpload(
                str(video_path),
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
                youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                print(f"✅ YouTube上传成功!")
                print(f"   视频ID: {video_id}")
                print(f"   链接: {youtube_url}")
                return video_id
            else:
                print("❌ YouTube上传失败：未返回视频ID")
                return None
                
        except Exception as e:
            print(f"❌ YouTube上传失败: {e}")
            return None
    
    def display_audio_list(self, audio_files: List[Dict[str, Any]]):
        """显示音频文件列表"""
        if not audio_files:
            print("📋 未找到音频文件")
            return
        
        print(f"\n📁 找到 {len(audio_files)} 个音频文件:")
        print("=" * 80)
        
        for i, file_info in enumerate(audio_files, 1):
            size_mb = file_info['size'] / (1024 * 1024)
            modified = file_info['modified'].strftime('%Y-%m-%d %H:%M')
            
            print(f"{i:2d}. {file_info['name']}")
            print(f"    📊 大小: {size_mb:.1f}MB | 📅 修改: {modified} | 🎵 格式: {file_info['format']}")
            
            if file_info['type'] == 'youtube_podcast':
                print(f"    📝 标题: {file_info['title']}")
                if file_info['date']:
                    print(f"    📅 日期: {file_info['date']}")
            
            print()
    
    def main_menu(self):
        """主菜单"""
        print("=" * 60)
        print("🎬 YouTube音频上传测试工具")
        print("=" * 60)
        print("📋 功能:")
        print("   • 扫描 assets/audio/ 目录下的音频文件")
        print("   • 自动匹配或生成缩略图")
        print("   • 生成视频文件（音频+静态图片）")
        print("   • 上传到YouTube（不公开链接）")
        
        if not self.youtube_available:
            print("\n⚠️  注意: YouTube API未配置，只能生成视频文件")
        
        print("\n" + "=" * 60)
        
        while True:
            print("\n🔧 操作选项:")
            print("1. 扫描并显示音频文件")
            print("2. 选择音频文件并上传到YouTube")
            print("3. 批量上传所有音频文件")
            print("4. 检查配置状态")
            print("5. 清理临时文件")
            print("0. 退出")
            
            choice = input("\n请选择操作 (0-5): ").strip()
            
            if choice == "0":
                print("👋 再见!")
                break
            elif choice == "1":
                self.handle_scan_audio()
            elif choice == "2":
                self.handle_single_upload()
            elif choice == "3":
                self.handle_batch_upload()
            elif choice == "4":
                self.handle_check_config()
            elif choice == "5":
                self.handle_cleanup()
            else:
                print("❌ 无效选择，请重新输入")
    
    def handle_scan_audio(self):
        """处理扫描音频文件"""
        print("\n🔍 扫描音频文件...")
        audio_files = self.scan_audio_files()
        self.display_audio_list(audio_files)
    
    def handle_single_upload(self):
        """处理单个文件上传"""
        audio_files = self.scan_audio_files()
        if not audio_files:
            return
        
        self.display_audio_list(audio_files)
        
        try:
            choice = input(f"\n请选择要上传的音频文件 (1-{len(audio_files)}): ").strip()
            if not choice.isdigit() or not (1 <= int(choice) <= len(audio_files)):
                print("❌ 无效选择")
                return
            
            selected_file = audio_files[int(choice) - 1]
            self.process_single_file(selected_file)
            
        except ValueError:
            print("❌ 请输入有效数字")
    
    def handle_batch_upload(self):
        """处理批量上传"""
        audio_files = self.scan_audio_files()
        if not audio_files:
            return
        
        print(f"\n📊 找到 {len(audio_files)} 个音频文件")
        confirm = input("确认批量上传所有文件？(y/N): ").strip().lower()
        
        if confirm not in ['y', 'yes']:
            print("❌ 已取消批量上传")
            return
        
        success_count = 0
        for i, file_info in enumerate(audio_files, 1):
            print(f"\n🔄 处理文件 {i}/{len(audio_files)}: {file_info['name']}")
            if self.process_single_file(file_info, show_details=False):
                success_count += 1
        
        print(f"\n📊 批量上传完成: {success_count}/{len(audio_files)} 成功")
    
    def process_single_file(self, file_info: Dict[str, Any], show_details: bool = True) -> bool:
        """处理单个文件"""
        try:
            audio_path = file_info['path']
            
            if show_details:
                print(f"\n🔄 处理文件: {file_info['name']}")
            
            # 查找缩略图
            thumbnail_path = self.find_thumbnail_for_audio(file_info)
            if thumbnail_path:
                if show_details:
                    print(f"✅ 找到缩略图: {thumbnail_path.name}")
            else:
                if show_details:
                    print("🔄 未找到匹配的缩略图，生成默认缩略图...")
                thumbnail_path = self.create_default_thumbnail(file_info['title'])
                if not thumbnail_path:
                    print("❌ 无法生成缩略图")
                    return False
            
            # 生成视频文件
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            video_filename = f"upload_{timestamp}_{audio_path.stem}.mp4"
            video_path = self.temp_dir / video_filename
            
            if not self.create_video_from_audio(audio_path, thumbnail_path, video_path):
                print("❌ 视频生成失败")
                return False
            
            # 准备上传信息
            title = file_info.get('title', audio_path.stem)
            description = f"""🎧 音频播客上传
            
📁 原始文件: {file_info['name']}
📅 修改时间: {file_info['modified'].strftime('%Y-%m-%d %H:%M')}
📊 文件大小: {file_info['size'] / (1024*1024):.1f}MB

---
通过YouTube音频上传工具自动上传
"""
            
            # 上传到YouTube
            if self.youtube_available:
                video_id = self.upload_to_youtube(video_path, title, description)
                if video_id:
                    # 记录YouTube链接映射
                    try:
                        from scripts.utils.youtube_link_mapper import YouTubeLinkMapper
                        mapper = YouTubeLinkMapper()
                        # 使用相对于项目根目录的路径
                        relative_audio_path = str(file_info['path'].relative_to(Path(__file__).parent.parent.parent))
                        mapper.add_mapping(relative_audio_path, video_id, title)
                    except Exception as e:
                        print(f"⚠️ 记录YouTube映射失败: {e}")
                    
                    # 清理临时视频文件
                    try:
                        video_path.unlink()
                    except:
                        pass
                    return True
                else:
                    return False
            else:
                print(f"✅ 视频文件已生成: {video_path}")
                print("💡 配置YouTube API后可自动上传")
                return True
                
        except Exception as e:
            print(f"❌ 处理文件失败: {e}")
            return False
    
    def handle_check_config(self):
        """检查配置状态"""
        print("\n🔍 配置状态检查")
        print("=" * 40)
        
        # 检查环境变量
        youtube_key = os.getenv('YOUTUBE_API_KEY')
        print(f"🔑 YOUTUBE_API_KEY: {'✅ 已配置' if youtube_key else '❌ 未配置'}")
        
        # 检查API连接
        print(f"🌐 YouTube API: {'✅ 可用' if self.youtube_available else '❌ 不可用'}")
        
        # 检查目录
        print(f"📁 音频目录: {'✅ 存在' if self.audio_dir.exists() else '❌ 不存在'}")
        print(f"📁 图片目录: {'✅ 存在' if self.image_dir.exists() else '❌ 不存在'}")
        print(f"📁 临时目录: {'✅ 存在' if self.temp_dir.exists() else '❌ 不存在'}")
        
        # 检查依赖
        print("\n📦 依赖库状态:")
        dependencies = [
            ('google-api-python-client', 'googleapiclient.discovery'),
            ('moviepy', 'moviepy.editor'),
            ('Pillow', 'PIL'),
            ('python-dotenv', 'dotenv')
        ]
        
        for name, module in dependencies:
            try:
                __import__(module)
                print(f"✅ {name}: 已安装")
            except ImportError:
                print(f"❌ {name}: 未安装")
        
        # 检查外部工具
        print("\n🛠️ 外部工具:")
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ ffmpeg: 已安装")
            else:
                print("❌ ffmpeg: 不可用")
        except:
            print("❌ ffmpeg: 未安装")
    
    def handle_cleanup(self):
        """清理临时文件"""
        print("\n🧹 清理临时文件...")
        
        if not self.temp_dir.exists():
            print("📋 临时目录不存在，无需清理")
            return
        
        temp_files = list(self.temp_dir.glob("*"))
        if not temp_files:
            print("📋 临时目录为空，无需清理")
            return
        
        print(f"📁 找到 {len(temp_files)} 个临时文件")
        for file_path in temp_files:
            print(f"   • {file_path.name}")
        
        confirm = input("确认删除所有临时文件？(y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            deleted_count = 0
            for file_path in temp_files:
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        deleted_count += 1
                    elif file_path.is_dir():
                        import shutil
                        shutil.rmtree(file_path)
                        deleted_count += 1
                except Exception as e:
                    print(f"❌ 删除失败 {file_path.name}: {e}")
            
            print(f"✅ 已删除 {deleted_count} 个临时文件")
        else:
            print("❌ 已取消清理操作")


def main():
    """主函数"""
    try:
        tester = YouTubeUploadTester()
        tester.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作，再见!")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()