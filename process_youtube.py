#!/usr/bin/env python3
"""处理YouTube视频生成"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from scripts.tools.youtube.youtube_video_generator import YouTubeVideoGenerator

def process_youtube():
    """处理YouTube视频生成"""

    print("🎬 YouTube视频生成")
    print("=" * 60)

    # 初始化生成器
    generator = YouTubeVideoGenerator()

    # 扫描音频文件
    audio_files = generator.scan_audio_files()

    # 查找目标文件
    target_file = None
    for file_info in audio_files:
        if "查理·科克事件" in file_info['name']:
            target_file = file_info
            break

    if not target_file:
        print("❌ 未找到目标音频文件")
        return

    print(f"\n📋 处理文件: {target_file['name']}")
    print(f"   📊 大小: {target_file['size'] / (1024*1024):.1f}MB")
    print(f"   🎵 格式: {target_file['format']}")
    print("\n🔄 开始生成视频...")

    # 直接生成视频
    success = generator.generate_video_for_file(target_file)

    if success:
        print("\n✅ 视频生成完成!")
        print(f"📁 输出目录: {generator.output_dir}")

        # 显示生成的文件
        output_files = list(generator.output_dir.glob("*查理*"))
        if output_files:
            print("\n📄 生成的文件:")
            for f in output_files:
                print(f"   - {f.name} ({f.stat().st_size / (1024*1024):.1f}MB)")
    else:
        print("\n❌ 视频生成失败")

if __name__ == "__main__":
    process_youtube()