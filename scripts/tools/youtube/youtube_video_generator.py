#!/usr/bin/env python3
"""
YouTube视频生成器 - 简化版
只生成视频文件，不上传，避免OAuth认证复杂性
"""

import os
import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class YouTubeVideoGenerator:
    """YouTube视频生成器（仅生成，不上传）"""
    
    def __init__(self):
        """初始化生成器"""
        self.audio_dir = Path("assets/audio")
        self.image_dir = Path("assets/images")
        self.output_dir = Path("youtube_videos")
        self.output_dir.mkdir(exist_ok=True)
        
        print(f"📁 输出目录: {self.output_dir}")
    
    def scan_audio_files(self) -> List[Dict[str, Any]]:
        """扫描音频文件"""
        if not self.audio_dir.exists():
            print(f"❌ 音频目录不存在: {self.audio_dir}")
            return []
        
        audio_files = []
        supported_formats = ['.mp3', '.wav', '.m4a', '.aac']
        
        for file_path in self.audio_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                file_info = {
                    'path': file_path,
                    'name': file_path.name,
                    'size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime),
                    'format': file_path.suffix.lower()
                }
                
                # 解析文件名
                file_info.update(self.parse_filename(file_path.name))
                audio_files.append(file_info)
        
        # 按修改时间排序
        audio_files.sort(key=lambda x: x['modified'], reverse=True)
        return audio_files
    
    def parse_filename(self, filename: str) -> Dict[str, str]:
        """从文件名解析信息"""
        info = {
            'title': filename,
            'date': '',
            'type': 'unknown'
        }
        
        # 解析YouTube播客文件名格式
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
        
        return None
    
    def create_default_thumbnail(self, title: str) -> Path:
        """创建默认缩略图"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建1280x720的图片
            img = Image.new('RGB', (1280, 720), color='#1a1a1a')
            draw = ImageDraw.Draw(img)
            
            # 尝试使用系统字体
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            except:
                font = ImageFont.load_default()
            
            # 绘制标题
            text_lines = self.wrap_text(title, 30)
            y_offset = 300
            
            for line in text_lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (1280 - text_width) // 2
                draw.text((x, y_offset), line, fill='white', font=font)
                y_offset += 60
            
            # 保存图片
            thumbnail_path = self.output_dir / f"thumbnail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            img.save(thumbnail_path, 'JPEG', quality=95)
            return thumbnail_path
            
        except ImportError:
            print("⚠️ PIL库未安装，使用简单的默认缩略图")
            return self.create_simple_thumbnail()
        except Exception as e:
            print(f"❌ 生成缩略图失败: {e}")
            return self.create_simple_thumbnail()
    
    def create_simple_thumbnail(self) -> Path:
        """创建简单的默认缩略图（纯色）"""
        try:
            from PIL import Image
            
            # 创建简单的黑色背景
            img = Image.new('RGB', (1280, 720), color='#000000')
            thumbnail_path = self.output_dir / f"simple_thumbnail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            img.save(thumbnail_path, 'JPEG', quality=95)
            return thumbnail_path
            
        except:
            # 如果PIL不可用，创建一个空文件作为占位符
            thumbnail_path = self.output_dir / f"placeholder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            thumbnail_path.write_text("Placeholder thumbnail")
            return thumbnail_path
    
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
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', str(thumbnail_path),
                '-i', str(audio_path),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                '-loglevel', 'error',
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
            
            audio_clip = AudioFileClip(str(audio_path))
            image_clip = ImageClip(str(thumbnail_path)).set_duration(audio_clip.duration)
            image_clip = image_clip.resize(height=720)
            
            video_clip = image_clip.set_audio(audio_clip)
            video_clip.write_videofile(
                str(output_path),
                fps=1,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            audio_clip.close()
            image_clip.close()
            video_clip.close()
            
            print(f"✅ moviepy视频生成成功: {output_path}")
            return True
            
        except ImportError:
            print("❌ moviepy未安装，无法生成视频")
            print("💡 安装命令: pip install moviepy")
            return False
        except Exception as e:
            print(f"❌ moviepy生成失败: {e}")
            return False
    
    def generate_video_for_file(self, file_info: Dict[str, Any]) -> bool:
        """为单个音频文件生成视频"""
        try:
            audio_path = file_info['path']
            print(f"\n🔄 处理文件: {file_info['name']}")
            
            # 查找或生成缩略图
            thumbnail_path = self.find_thumbnail_for_audio(file_info)
            if thumbnail_path:
                print(f"✅ 找到缩略图: {thumbnail_path.name}")
            else:
                print("🔄 生成默认缩略图...")
                thumbnail_path = self.create_default_thumbnail(file_info['title'])
            
            # 生成输出文件名
            safe_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5\-_]', '_', file_info['title'])
            output_filename = f"{safe_name}.mp4"
            output_path = self.output_dir / output_filename
            
            # 生成视频
            if self.create_video_from_audio(audio_path, thumbnail_path, output_path):
                print(f"✅ 视频已保存: {output_path}")
                
                # 生成YouTube上传信息文件
                info_file = output_path.with_suffix('.txt')
                self.create_upload_info_file(file_info, info_file)
                
                return True
            else:
                print("❌ 视频生成失败")
                return False
                
        except Exception as e:
            print(f"❌ 处理文件失败: {e}")
            return False
    
    def create_upload_info_file(self, file_info: Dict[str, Any], info_file: Path):
        """创建上传信息文件"""
        title = file_info.get('title', file_info['name'])
        description = f"""🎧 音频播客

📁 原始文件: {file_info['name']}
📅 修改时间: {file_info['modified'].strftime('%Y-%m-%d %H:%M')}
📊 文件大小: {file_info['size'] / (1024*1024):.1f}MB
🎵 格式: {file_info['format']}

建议YouTube设置:
- 标题: {title}
- 分类: 教育
- 语言: 中文
- 隐私: 不公开（通过链接可访问）
- 标签: 播客,音频,学习,中文

---
通过YouTube视频生成器创建
"""
        
        info_file.write_text(description, encoding='utf-8')
        print(f"📝 上传信息已保存: {info_file}")
    
    def main_menu(self):
        """主菜单"""
        print("=" * 60)
        print("🎬 YouTube视频生成器（无上传版）")
        print("=" * 60)
        print("📋 功能:")
        print("   • 扫描 assets/audio/ 目录下的音频文件")
        print("   • 生成缩略图（自动匹配或创建默认）")
        print("   • 生成YouTube就绪的视频文件")
        print("   • 创建上传信息文件")
        print("   • 保存到 youtube_videos/ 目录")
        print("\n💡 优势: 无需OAuth认证，直接生成视频供手动上传")
        print("=" * 60)
        
        while True:
            print("\n🔧 操作选项:")
            print("1. 扫描并显示音频文件")
            print("2. 为单个音频文件生成视频")
            print("3. 批量生成所有视频文件")
            print("4. 查看输出目录")
            print("5. 清理输出目录")
            print("0. 退出")
            
            choice = input("\n请选择操作 (0-5): ").strip()
            
            if choice == "0":
                print("👋 再见!")
                break
            elif choice == "1":
                self.handle_scan_audio()
            elif choice == "2":
                self.handle_single_generation()
            elif choice == "3":
                self.handle_batch_generation()
            elif choice == "4":
                self.handle_view_output()
            elif choice == "5":
                self.handle_cleanup()
            else:
                print("❌ 无效选择，请重新输入")
    
    def handle_scan_audio(self):
        """扫描音频文件"""
        print("\n🔍 扫描音频文件...")
        audio_files = self.scan_audio_files()
        
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
    
    def handle_single_generation(self):
        """单个文件生成"""
        audio_files = self.scan_audio_files()
        if not audio_files:
            return
        
        self.handle_scan_audio()
        
        try:
            choice = input(f"\n请选择要生成视频的音频文件 (1-{len(audio_files)}): ").strip()
            if not choice.isdigit() or not (1 <= int(choice) <= len(audio_files)):
                print("❌ 无效选择")
                return
            
            selected_file = audio_files[int(choice) - 1]
            self.generate_video_for_file(selected_file)
            
        except ValueError:
            print("❌ 请输入有效数字")
    
    def handle_batch_generation(self):
        """批量生成"""
        audio_files = self.scan_audio_files()
        if not audio_files:
            return
        
        print(f"\n📊 找到 {len(audio_files)} 个音频文件")
        confirm = input("确认批量生成所有视频文件？(y/N): ").strip().lower()
        
        if confirm not in ['y', 'yes']:
            print("❌ 已取消批量生成")
            return
        
        success_count = 0
        for i, file_info in enumerate(audio_files, 1):
            print(f"\n🔄 处理文件 {i}/{len(audio_files)}: {file_info['name']}")
            if self.generate_video_for_file(file_info):
                success_count += 1
        
        print(f"\n📊 批量生成完成: {success_count}/{len(audio_files)} 成功")
        print(f"📁 所有视频文件保存在: {self.output_dir}")
    
    def handle_view_output(self):
        """查看输出目录"""
        print(f"\n📁 输出目录: {self.output_dir}")
        
        if not self.output_dir.exists():
            print("📋 输出目录不存在")
            return
        
        files = list(self.output_dir.glob("*"))
        if not files:
            print("📋 输出目录为空")
            return
        
        print(f"📊 找到 {len(files)} 个文件:")
        
        video_files = []
        info_files = []
        other_files = []
        
        for file_path in files:
            if file_path.suffix.lower() == '.mp4':
                video_files.append(file_path)
            elif file_path.suffix.lower() == '.txt':
                info_files.append(file_path)
            else:
                other_files.append(file_path)
        
        if video_files:
            print(f"\n🎬 视频文件 ({len(video_files)}个):")
            for video in sorted(video_files):
                size_mb = video.stat().st_size / (1024 * 1024)
                print(f"   • {video.name} ({size_mb:.1f}MB)")
        
        if info_files:
            print(f"\n📝 信息文件 ({len(info_files)}个):")
            for info in sorted(info_files):
                print(f"   • {info.name}")
        
        if other_files:
            print(f"\n📄 其他文件 ({len(other_files)}个):")
            for other in sorted(other_files):
                print(f"   • {other.name}")
    
    def handle_cleanup(self):
        """清理输出目录"""
        print(f"\n🧹 清理输出目录: {self.output_dir}")
        
        if not self.output_dir.exists():
            print("📋 输出目录不存在，无需清理")
            return
        
        files = list(self.output_dir.glob("*"))
        if not files:
            print("📋 输出目录为空，无需清理")
            return
        
        print(f"📁 找到 {len(files)} 个文件")
        for file_path in files:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"   • {file_path.name} ({size_mb:.1f}MB)")
        
        confirm = input("确认删除所有文件？(y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            deleted_count = 0
            for file_path in files:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ 删除失败 {file_path.name}: {e}")
            
            print(f"✅ 已删除 {deleted_count} 个文件")
        else:
            print("❌ 已取消清理操作")


def main():
    """主函数"""
    try:
        generator = YouTubeVideoGenerator()
        generator.main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作，再见!")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")


if __name__ == "__main__":
    main()