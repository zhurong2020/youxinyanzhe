#!/usr/bin/env python3
"""测试YouTube视频生成功能"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from scripts.tools.youtube.youtube_video_generator import YouTubeVideoGenerator

def test_youtube_generation():
    """测试YouTube视频生成"""

    print("🎬 YouTube视频生成测试")
    print("=" * 60)

    # 初始化生成器
    generator = YouTubeVideoGenerator()

    # 扫描音频文件
    print("\n📋 扫描音频文件...")
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

    print(f"\n✅ 找到目标文件: {target_file['name']}")
    print(f"   📊 大小: {target_file['size'] / (1024*1024):.1f}MB")
    print(f"   🎵 格式: {target_file['format']}")

    # 生成视频
    print("\n🔄 开始生成视频...")
    print("   这将执行以下步骤:")
    print("   1. 查找或生成缩略图")
    print("   2. 压缩音频(如需要)")
    print("   3. 生成视频文件")
    print("   4. 创建上传信息文件")

    confirm = input("\n确认生成视频？(y/N): ").strip().lower()
    if confirm in ['y', 'yes']:
        success = generator.generate_video_for_file(target_file)
        if success:
            print("\n✅ 视频生成成功!")
            print(f"📁 输出目录: {generator.output_dir}")
        else:
            print("\n❌ 视频生成失败")
    else:
        print("❌ 已取消")

if __name__ == "__main__":
    test_youtube_generation()