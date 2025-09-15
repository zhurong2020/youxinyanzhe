#!/usr/bin/env python3
"""增强版YouTube视频生成器 - 支持图片选择"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import subprocess
import re
from datetime import datetime

class YouTubeVideoEnhanced:
    """增强版YouTube视频生成器"""

    def __init__(self, parent_generator=None):
        """初始化增强生成器"""
        self.parent = parent_generator
        self.image_dir = Path("assets/images/posts")
        self.output_dir = Path(".tmp/youtube_videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def select_thumbnail_for_audio(self, audio_file: Dict[str, Any]) -> Optional[Path]:
        """让用户选择缩略图"""

        print("\n🖼️ 选择视频封面图片")
        print("=" * 40)

        # 查找可用的图片文件
        available_images = []
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

        # 获取当前年月目录
        from datetime import datetime
        current_date = datetime.now()
        current_month_dir = self.image_dir / str(current_date.year) / f"{current_date.month:02d}"

        # 优先扫描当月目录
        if current_month_dir.exists():
            print(f"📁 扫描当月图片目录: {current_month_dir}")
            for image_file in current_month_dir.rglob("*"):
                if image_file.suffix.lower() in image_extensions:
                    available_images.append(image_file)

        # 如果当月没有图片，扫描最近的图片
        if not available_images:
            print("⚠️ 当月没有图片，扫描最近的图片...")
            for image_file in self.image_dir.rglob("*"):
                if image_file.suffix.lower() in image_extensions:
                    available_images.append(image_file)

        if not available_images:
            print("❌ 未找到可用的图片文件")
            return None

        # 按修改时间排序（最新的在前）
        available_images.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        # 显示选项
        print(f"\n📋 找到 {len(available_images)} 个图片文件:")

        # 限制显示数量
        display_limit = min(20, len(available_images))
        for i, img_path in enumerate(available_images[:display_limit], 1):
            # 计算相对路径
            try:
                rel_path = img_path.relative_to(Path.cwd())
            except:
                rel_path = img_path

            # 获取文件大小
            size_mb = img_path.stat().st_size / (1024 * 1024)

            print(f"{i:2}. {rel_path} ({size_mb:.1f}MB)")

        if len(available_images) > display_limit:
            print(f"... 还有 {len(available_images) - display_limit} 个文件未显示")

        # 添加额外选项
        print(f"\n0. 自动生成默认封面")
        print("q. 取消操作")

        # 获取用户选择
        while True:
            choice = input(f"\n请选择图片 (1-{display_limit}/0/q): ").strip().lower()

            if choice == 'q':
                print("❌ 已取消操作")
                return None

            if choice == '0':
                print("🎨 将自动生成默认封面")
                return None  # 返回None表示需要生成默认封面

            try:
                choice_num = int(choice)
                if 1 <= choice_num <= display_limit:
                    selected_image = available_images[choice_num - 1]
                    print(f"\n✅ 已选择: {selected_image.name}")
                    return selected_image
                else:
                    print("❌ 选择超出范围，请重新选择")
            except ValueError:
                print("❌ 请输入有效的数字")

    def process_audio_with_compression(self, audio_path: Path) -> Optional[Path]:
        """压缩音频文件"""

        print("\n🎵 音频优化处理")
        print("=" * 40)

        # 检查文件大小
        size_mb = audio_path.stat().st_size / (1024 * 1024)
        print(f"📊 原始文件: {audio_path.name} ({size_mb:.1f}MB)")

        # 如果是WAV文件或大于10MB，进行压缩
        if audio_path.suffix.lower() == '.wav' or size_mb > 10:
            print("🔄 正在压缩音频...")

            compressed_path = self.output_dir / f"{audio_path.stem}_compressed.mp3"

            try:
                # 使用ffmpeg压缩音频
                cmd = [
                    'ffmpeg', '-y',
                    '-i', str(audio_path),
                    '-acodec', 'libmp3lame',
                    '-ab', '128k',  # 128kbps比特率
                    '-ar', '44100',  # 44.1kHz采样率
                    str(compressed_path)
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                if result.returncode == 0:
                    new_size_mb = compressed_path.stat().st_size / (1024 * 1024)
                    compression_ratio = (1 - new_size_mb / size_mb) * 100
                    print(f"✅ 压缩完成: {new_size_mb:.1f}MB (节省 {compression_ratio:.1f}%)")
                    return compressed_path
                else:
                    print(f"⚠️ 压缩失败，使用原始文件")
                    return audio_path

            except Exception as e:
                print(f"⚠️ 压缩过程出错: {e}")
                return audio_path
        else:
            print("✅ 音频文件无需压缩")
            return audio_path

    def generate_video_interactive(self, audio_file: Dict[str, Any]) -> bool:
        """交互式生成视频"""

        try:
            print("\n" + "=" * 60)
            print(f"🎬 处理音频: {audio_file['name']}")
            print("=" * 60)

            # 1. 选择或生成缩略图
            thumbnail_path = self.select_thumbnail_for_audio(audio_file)

            if thumbnail_path is None:
                # 生成默认缩略图
                print("\n🎨 生成默认封面...")
                from scripts.tools.youtube.youtube_video_generator import YouTubeVideoGenerator
                generator = YouTubeVideoGenerator()
                thumbnail_path = generator.create_default_thumbnail(audio_file['title'])

            # 2. 压缩音频
            audio_path = audio_file['path']
            compressed_audio = self.process_audio_with_compression(audio_path)

            # 3. 生成视频
            print("\n🎬 生成视频文件...")
            safe_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5\-_]', '_', audio_file['title'])
            output_filename = f"{safe_name}.mp4"
            output_path = self.output_dir / output_filename

            # 使用ffmpeg合成视频
            cmd = [
                'ffmpeg', '-y',
                '-loop', '1',
                '-i', str(thumbnail_path),
                '-i', str(compressed_audio),
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-b:a', '128k',  # YouTube推荐比特率
                '-pix_fmt', 'yuv420p',
                '-shortest',
                '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2',
                str(output_path)
            ]

            print(f"   封面: {thumbnail_path.name}")
            print(f"   音频: {compressed_audio.name}")
            print(f"   输出: {output_path.name}")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                final_size_mb = output_path.stat().st_size / (1024 * 1024)
                print(f"\n✅ 视频生成成功!")
                print(f"📄 文件: {output_path}")
                print(f"📊 大小: {final_size_mb:.1f}MB")

                # 清理临时压缩文件
                if compressed_audio != audio_path and compressed_audio.exists():
                    compressed_audio.unlink()
                    print("🧹 已清理临时文件")

                # 询问是否上传到YouTube
                print("\n" + "=" * 40)
                upload_choice = input("📤 是否立即上传到YouTube？(y/N): ").strip().lower()

                if upload_choice in ['y', 'yes']:
                    self._upload_to_youtube(output_path, audio_file)
                else:
                    print("ℹ️ 视频已保存，稍后可通过菜单上传")

                return True
            else:
                print(f"❌ 视频生成失败: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ 处理失败: {e}")
            return False

    def _upload_to_youtube(self, video_path: Path, audio_file: Dict[str, Any]):
        """上传视频到YouTube"""
        try:
            print("\n🚀 开始上传到YouTube...")
            print("=" * 40)

            # 检查OAuth配置
            from pathlib import Path
            import json

            token_file = Path("config/youtube_oauth_token.json")
            if not token_file.exists():
                print("❌ YouTube OAuth未配置")
                print("💡 请先通过主菜单 → 4 → 2 → 3 配置OAuth认证")
                return False

            # 导入上传工具
            try:
                from scripts.tools.youtube.youtube_upload_tester import YouTubeUploadTester

                # 创建上传器
                uploader = YouTubeUploadTester()

                # 准备视频信息
                video_info = {
                    'path': video_path,
                    'name': video_path.name,
                    'title': audio_file.get('title', audio_file['name']),
                    'size': video_path.stat().st_size,
                    'format': video_path.suffix
                }

                print(f"📹 视频文件: {video_path.name}")
                print(f"📝 标题: {video_info['title']}")
                print(f"📊 大小: {video_info['size'] / (1024*1024):.1f}MB")

                # 准备上传信息
                title = video_info['title']
                description = f"""🎧 音频播客

📁 原始文件: {audio_file['name']}
📊 文件大小: {audio_file['size'] / (1024*1024):.1f}MB
🎵 格式: {audio_file['format']}

---
通过有心工坊YouTube视频生成器创建
访问我们: https://youxinyanzhe.github.io
"""

                # 执行上传
                result = uploader.upload_to_youtube(video_path, title, description)

                if result:
                    # result 可能是视频ID或完整URL
                    video_id = None
                    video_url = None

                    if result.startswith('http'):
                        # 返回的是完整URL
                        video_url = result
                        if 'watch?v=' in result:
                            video_id = result.split('watch?v=')[1].split('&')[0]
                        elif 'youtu.be/' in result:
                            video_id = result.split('youtu.be/')[1].split('?')[0]
                    else:
                        # 返回的是视频ID
                        video_id = result
                        video_url = f"https://www.youtube.com/watch?v={video_id}"

                    print("\n✅ 上传成功!")
                    print(f"🔗 视频链接: {video_url}")

                    # 保存上传记录
                    upload_record_file = self.output_dir / "upload_history.txt"
                    with open(upload_record_file, 'a', encoding='utf-8') as f:
                        from datetime import datetime
                        f.write(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"文件: {video_path.name}\n")
                        f.write(f"链接: {video_url}\n")
                        f.write("-" * 40 + "\n")

                    if video_id:
                        # 询问是否更新博文
                        print("\n" + "=" * 40)
                        update_choice = input("📝 是否将YouTube链接添加到对应的博文？(y/N): ").strip().lower()

                        if update_choice in ['y', 'yes']:
                            self._update_blog_post(audio_file, video_id, video_url, title)

                    return True
                else:
                    print("❌ 上传失败")
                    return False

            except ImportError:
                print("⚠️ YouTube上传工具未安装")
                print("💡 运行: pip install google-api-python-client google-auth-oauthlib")
                return False

        except Exception as e:
            print(f"❌ 上传过程出错: {e}")
            return False

    def _update_blog_post(self, audio_file: Dict[str, Any], video_id: str, video_url: str, title: str):
        """更新博文，添加YouTube链接"""
        try:
            print("\n🔍 查找对应的博文...")

            from scripts.tools.youtube.youtube_post_updater import YouTubePostUpdater

            updater = YouTubePostUpdater()

            # 使用音频文件名查找博文
            audio_name = audio_file.get('name', '')
            post_path = updater.find_post_by_audio(audio_name)

            if not post_path:
                print(f"❌ 未找到与 {audio_name} 对应的博文")

                # 提供手动选择选项
                manual_choice = input("是否手动选择博文？(y/N): ").strip().lower()
                if manual_choice in ['y', 'yes']:
                    # 列出最近的博文
                    posts_dir = Path("_posts")
                    drafts_dir = Path("_drafts")

                    all_posts = []

                    # 获取_posts目录中的文件
                    if posts_dir.exists():
                        post_files = list(posts_dir.glob("*.md"))
                        # 按文件名排序（因为文件名包含日期）
                        post_files.sort(reverse=True)
                        all_posts.extend(post_files[:15])  # 获取最新的15个

                    # 获取_drafts目录中的文件
                    if drafts_dir.exists():
                        draft_files = list(drafts_dir.glob("*.md"))
                        draft_files.sort(reverse=True)
                        all_posts.extend(draft_files[:5])  # 获取最新的5个草稿

                    if all_posts:
                        print("\n📄 最近的博文:")
                        # 重新排序合并后的列表
                        all_posts.sort(key=lambda x: x.name, reverse=True)
                        # 只显示前20个
                        for i, post in enumerate(all_posts[:20], 1):
                            # 标识是否为草稿
                            prefix = "[草稿] " if "_drafts" in str(post) else ""
                            print(f"  {i:2}. {prefix}{post.name}")

                        try:
                            choice = int(input(f"\n选择博文 (1-{len(all_posts)}): "))
                            if 1 <= choice <= len(all_posts):
                                post_path = all_posts[choice - 1]
                        except ValueError:
                            print("❌ 无效选择")
                            return

            if post_path and post_path.exists():
                # 添加YouTube链接到博文
                success = updater.add_youtube_link_to_post(
                    post_path,
                    video_id,
                    video_url,
                    title,
                    audio_name
                )

                if success:
                    print(f"✅ 博文更新成功: {post_path.name}")
                else:
                    print("❌ 博文更新失败")
            else:
                print("⚠️ 未更新博文（未找到匹配文件）")

        except Exception as e:
            print(f"❌ 更新博文时出错: {e}")


def main():
    """主函数 - 用于测试"""
    print("🎬 增强版YouTube视频生成器")
    print("=" * 60)

    # 测试用的音频文件信息
    test_audio = {
        'name': '查理·科克事件：真相与启示.wav',
        'path': Path('assets/audio/查理·科克事件：真相与启示.wav'),
        'title': '查理·科克事件：真相与启示',
        'size': 27000000,
        'format': '.wav',
        'modified': datetime.now()
    }

    if test_audio['path'].exists():
        enhancer = YouTubeVideoEnhanced()
        enhancer.generate_video_interactive(test_audio)
    else:
        print("❌ 测试音频文件不存在")


if __name__ == "__main__":
    main()