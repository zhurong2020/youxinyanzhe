#!/usr/bin/env python3
"""
音频链接替换器
用于将文章中的本地音频链接替换为YouTube嵌入代码
"""

import re
import sys
from pathlib import Path
from typing import Optional, Tuple

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.youtube_link_mapper import YouTubeLinkMapper

class AudioLinkReplacer:
    """音频链接替换器"""
    
    def __init__(self):
        self.mapper = YouTubeLinkMapper()
        # 匹配Jekyll音频标签的正则表达式
        self.audio_pattern = re.compile(
            r'<audio\s+controls>\s*<source\s+src="([^"]*assets/audio/[^"]*\.mp3)"\s+type="audio/mpeg">\s*[^<]*</audio>',
            re.MULTILINE | re.DOTALL
        )
    
    def extract_audio_path(self, src_attr: str) -> Optional[str]:
        """
        从src属性中提取音频文件路径
        
        Args:
            src_attr: src属性值，如 "{{ site.baseurl }}/assets/audio/file.mp3"
        
        Returns:
            Optional[str]: 提取的音频文件路径，如 "assets/audio/file.mp3"
        """
        # 移除Jekyll变量
        clean_path = src_attr.replace("{{ site.baseurl }}/", "").replace("{{site.baseurl}}/", "")
        
        # 确保路径以assets/audio/开头
        if clean_path.startswith("assets/audio/") and clean_path.endswith(".mp3"):
            return clean_path
        
        return None
    
    def create_youtube_embed(self, video_id: str, title: str = "") -> str:
        """
        创建YouTube嵌入代码
        
        Args:
            video_id: YouTube视频ID
            title: 视频标题（可选）
        
        Returns:
            str: YouTube嵌入HTML代码
        """
        title_attr = f' title="{title}"' if title else ""
        
        return f'''<div class="youtube-audio-embed">
  <iframe width="100%" height="315" frameborder="0" 
          src="https://www.youtube.com/embed/{video_id}"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
          allowfullscreen{title_attr}>
  </iframe>
  <p><em>🎧 中文播客导读 - 建议1.5倍速播放</em></p>
</div>'''
    
    def replace_audio_links(self, content: str, article_title: str = "") -> Tuple[str, int]:
        """
        替换文章中的音频链接
        
        Args:
            content: 文章内容
            article_title: 文章标题（用于日志）
        
        Returns:
            Tuple[str, int]: (替换后的内容, 替换数量)
        """
        replaced_count = 0
        
        def replace_match(match):
            nonlocal replaced_count
            
            full_match = match.group(0)
            src_attr = match.group(1)
            
            # 提取音频文件路径
            audio_path = self.extract_audio_path(src_attr)
            if not audio_path:
                print(f"⚠️ 无法解析音频路径: {src_attr}")
                return full_match
            
            # 查找YouTube映射
            mapping_info = self.mapper.get_mapping_info(audio_path)
            if not mapping_info:
                print(f"⚠️ 未找到YouTube映射: {audio_path}")
                return full_match
            
            # 替换为YouTube嵌入
            video_id = mapping_info["video_id"]
            title = mapping_info.get("title", "")
            youtube_embed = self.create_youtube_embed(video_id, title)
            
            print(f"✅ 替换音频链接: {audio_path} -> YouTube视频 {video_id}")
            replaced_count += 1
            
            return youtube_embed
        
        # 执行替换
        new_content = self.audio_pattern.sub(replace_match, content)
        
        if replaced_count > 0:
            print(f"🎬 文章「{article_title}」共替换 {replaced_count} 个音频链接为YouTube嵌入")
        
        return new_content, replaced_count
    
    def process_article_file(self, file_path: Path) -> bool:
        """
        处理文章文件，替换其中的音频链接
        
        Args:
            file_path: 文章文件路径
        
        Returns:
            bool: 是否成功处理
        """
        try:
            # 读取文章内容
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # 替换音频链接
            new_content, replaced_count = self.replace_audio_links(
                original_content, file_path.stem
            )
            
            # 如果有替换，写回文件
            if replaced_count > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"💾 已保存文章: {file_path}")
                return True
            else:
                print(f"ℹ️ 文章无需替换: {file_path}")
                return True
                
        except Exception as e:
            print(f"❌ 处理文章失败 {file_path}: {e}")
            return False
    
    def preview_replacements(self, content: str) -> None:
        """
        预览将要进行的替换（不实际替换）
        
        Args:
            content: 文章内容
        """
        matches = self.audio_pattern.findall(content)
        
        if not matches:
            print("📋 未找到音频标签")
            return
        
        print(f"📋 找到 {len(matches)} 个音频标签:")
        
        for i, src_attr in enumerate(matches, 1):
            audio_path = self.extract_audio_path(src_attr)
            if audio_path:
                mapping_info = self.mapper.get_mapping_info(audio_path)
                if mapping_info:
                    print(f"  {i}. ✅ {audio_path} -> YouTube视频 {mapping_info['video_id']}")
                else:
                    print(f"  {i}. ❌ {audio_path} (无YouTube映射)")
            else:
                print(f"  {i}. ⚠️ 无法解析路径: {src_attr}")


def main():
    """命令行测试接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="音频链接替换器")
    parser.add_argument('file_path', help='要处理的文章文件路径')
    parser.add_argument('--preview', action='store_true', help='仅预览，不实际替换')
    
    args = parser.parse_args()
    
    file_path = Path(args.file_path)
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    replacer = AudioLinkReplacer()
    
    if args.preview:
        # 预览模式
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📖 预览文章: {file_path}")
        replacer.preview_replacements(content)
    else:
        # 实际处理模式
        print(f"🔄 处理文章: {file_path}")
        success = replacer.process_article_file(file_path)
        if success:
            print("✅ 处理完成")
        else:
            print("❌ 处理失败")


if __name__ == "__main__":
    main()