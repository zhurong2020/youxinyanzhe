#!/usr/bin/env python3
"""
YouTube视频链接更新工具
将上传的YouTube视频链接添加到对应的博文中
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any
import frontmatter
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class YouTubePostUpdater:
    """YouTube博文更新器"""

    def __init__(self):
        self.project_root = project_root
        self.posts_dir = self.project_root / "_posts"
        self.drafts_dir = self.project_root / "_drafts"

    def find_post_by_audio(self, audio_file_name: str) -> Optional[Path]:
        """
        根据音频文件名查找对应的博文

        Args:
            audio_file_name: 音频文件名（如：查理·科克事件：真相与启示.wav）

        Returns:
            找到的博文路径，如果没找到返回None
        """
        # 提取音频文件的基本名称（去掉扩展名）
        audio_base = Path(audio_file_name).stem

        # 多种匹配策略
        # 1. 对于简单文件名如 "charliekirk.wav"，尝试查找包含该词的文件
        if audio_base.replace('_', '').replace('-', '').isalnum():
            # 简单文件名，直接搜索
            search_keyword = audio_base.lower()
        else:
            # 复杂文件名，清理特殊字符
            search_keyword = audio_base.replace('：', '').replace(':', '').replace('·', '').replace('_', '').replace('-', '').lower()

        # 搜索已发布的文章
        all_posts = []
        for post_file in self.posts_dir.glob("*.md"):
            all_posts.append(post_file)

        # 搜索草稿
        for draft_file in self.drafts_dir.glob("*.md"):
            all_posts.append(draft_file)

        # 查找匹配的文章
        for post_file in all_posts:
            post_name = post_file.stem.lower()

            # 更智能的匹配策略
            # 1. 对于 "charliekirk" 这样的简单名称
            if 'charliekirk' in search_keyword or search_keyword == 'charliekirk':
                if 'charlie' in post_name and 'kirk' in post_name:
                    print(f"📄 找到匹配的博文: {post_file.name}")
                    return post_file

            # 2. 单独的 charlie 或 kirk
            if search_keyword in ['charlie', 'kirk']:
                if search_keyword in post_name:
                    print(f"📄 找到匹配的博文: {post_file.name}")
                    return post_file

            # 3. 移除连字符后的匹配
            clean_post_name = post_name.replace('-', '').replace('_', '')
            if search_keyword in clean_post_name:
                print(f"📄 找到匹配的博文: {post_file.name}")
                return post_file

            # 4. 部分匹配（前5个字符）
            if len(search_keyword) > 5 and search_keyword[:5] in clean_post_name:
                print(f"📄 找到匹配的博文: {post_file.name}")
                return post_file

            # 检查文章内容
            try:
                with open(post_file, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                    title = post.get('title', '').lower()

                    # 检查标题是否匹配
                    if any(term in title for term in search_terms.split()):
                        print(f"📄 找到匹配的博文（通过标题）: {post_file.name}")
                        return post_file
            except Exception:
                continue

        return None

    def add_youtube_link_to_post(self, post_path: Path, video_id: str, video_url: str,
                                 title: str = "", audio_file: str = "") -> bool:
        """
        将YouTube链接添加到博文中

        Args:
            post_path: 博文文件路径
            video_id: YouTube视频ID
            video_url: YouTube完整链接
            title: 视频标题
            audio_file: 原始音频文件名

        Returns:
            是否成功添加
        """
        try:
            # 读取博文
            with open(post_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)

            content = post.content

            # 检查是否已经包含此YouTube链接
            if video_url in content or video_id in content:
                print(f"⚠️ YouTube链接已存在于博文中: {post_path.name}")
                return True

            # 构造YouTube播客区块（响应式iframe）
            youtube_section = f"""
## 🎧 播客收听 (YouTube版)

<div class="video-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000;">
  <iframe src='https://www.youtube.com/embed/{video_id}?rel=0&showinfo=0&color=white&iv_load_policy=3'
          style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
          frameborder='0'
          allowfullscreen>
  </iframe>
</div>

**视频**: [{title or "音频播客"}]({video_url})
**平台**: YouTube | **类型**: 音频播客 | **隐私**: 不公开（通过链接访问）

> 💡 **提示**: 此视频设为"不公开"状态，只有通过本站链接才能访问。如需下载音频，请使用上方的直接播放器。
"""

            # 查找合适的插入位置
            insert_position = self._find_insert_position(content)

            if insert_position == -1:
                # 添加到文末
                post.content = content + '\n' + youtube_section
            else:
                # 在指定位置插入
                lines = content.split('\n')
                lines.insert(insert_position, youtube_section)
                post.content = '\n'.join(lines)

            # 保存修改后的文件
            content_str = frontmatter.dumps(post)
            with open(post_path, 'w', encoding='utf-8') as f:
                f.write(content_str)

            print(f"✅ YouTube链接已添加到博文: {post_path.name}")

            # 同时更新映射记录
            from scripts.utils.youtube_link_mapper import YouTubeLinkMapper
            mapper = YouTubeLinkMapper()

            # 保存映射关系
            relative_audio_path = f"assets/audio/{audio_file}" if audio_file else ""
            if relative_audio_path:
                mapper.add_mapping(relative_audio_path, video_id, title)

            return True

        except Exception as e:
            print(f"❌ 添加YouTube链接失败: {e}")
            return False

    def _find_insert_position(self, content: str) -> int:
        """
        在博文内容中找到合适的插入位置

        Args:
            content: 博文内容

        Returns:
            插入位置的索引，-1表示添加到末尾
        """
        lines = content.split('\n')

        # 1. 查找现有的音频播放器部分（优先插入位置）
        for i, line in enumerate(lines):
            if '<audio' in line and 'controls' in line:
                # 找到音频播放器，在其后插入
                # 继续向下查找，直到找到下一个段落或标题
                for j in range(i + 1, min(i + 10, len(lines))):
                    if lines[j].strip() == '' and j + 1 < len(lines) and lines[j + 1].strip() != '':
                        return j + 1
                return i + 5  # 默认在音频播放器后5行

        # 2. 查找"🎧"播客部分
        for i, line in enumerate(lines):
            if '🎧' in line and ('播客' in line or 'Podcast' in line):
                # 在播客部分后插入
                return i + 2

        # 3. 查找"<!-- more -->"标记
        for i, line in enumerate(lines):
            if '<!-- more -->' in line:
                # 在more标记后的第一个空行插入
                for j in range(i + 1, min(i + 20, len(lines))):
                    if lines[j].strip() == '':
                        return j
                return i + 2

        # 4. 默认添加到末尾
        return -1


def main():
    """主函数 - 命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="将YouTube视频链接添加到博文")
    parser.add_argument('--audio', required=True, help='音频文件名')
    parser.add_argument('--video-id', required=True, help='YouTube视频ID')
    parser.add_argument('--url', help='YouTube视频完整URL')
    parser.add_argument('--title', default='', help='视频标题')
    parser.add_argument('--post', help='指定博文路径（可选）')

    args = parser.parse_args()

    # 构造完整URL
    video_url = args.url or f"https://www.youtube.com/watch?v={args.video_id}"

    updater = YouTubePostUpdater()

    # 查找博文
    if args.post:
        post_path = Path(args.post)
    else:
        post_path = updater.find_post_by_audio(args.audio)

    if not post_path or not post_path.exists():
        print(f"❌ 未找到对应的博文: {args.audio}")
        return 1

    # 添加链接
    success = updater.add_youtube_link_to_post(
        post_path,
        args.video_id,
        video_url,
        args.title,
        args.audio
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())