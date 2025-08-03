#!/usr/bin/env python3
"""
YouTube单个文件上传 - 命令行版本
用法: python upload_single.py [文件编号]
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def main():
    """主函数"""
    try:
        from scripts.tools.youtube_upload_tester import YouTubeUploadTester
        
        # 创建上传器实例
        tester = YouTubeUploadTester()
        
        # 扫描音频文件
        audio_files = tester.scan_audio_files()
        if not audio_files:
            print("❌ 未找到音频文件")
            return
        
        # 显示文件列表
        print("🎬 YouTube单个文件上传")
        print("=" * 50)
        print(f"📁 找到 {len(audio_files)} 个音频文件:")
        print()
        
        for i, file_info in enumerate(audio_files, 1):
            size_mb = file_info['size'] / (1024 * 1024)
            print(f"{i}. {file_info['name']} ({size_mb:.1f}MB)")
        
        # 获取命令行参数
        if len(sys.argv) > 1:
            try:
                file_index = int(sys.argv[1])
                if not (1 <= file_index <= len(audio_files)):
                    print(f"❌ 请输入 1-{len(audio_files)} 之间的数字")
                    return
            except ValueError:
                print("❌ 请输入有效数字")
                return
        else:
            print(f"\\n用法: python upload_single.py [1-{len(audio_files)}]")
            print("例如: python upload_single.py 2  # 上传第2个文件")
            return
        
        # 选择的文件
        selected_file = audio_files[file_index - 1]
        
        print(f"\\n🎯 选择上传: {selected_file['name']}")
        print(f"📊 文件大小: {selected_file['size'] / (1024 * 1024):.1f}MB")
        print("🚀 开始上传流程...")
        print("-" * 50)
        
        # 执行上传
        result = tester.process_single_file(selected_file, show_details=True)
        
        print("\\n" + "=" * 50)
        if result:
            print("🎉 上传成功!")
            print("💡 视频已设置为不公开，可通过链接访问")
        else:
            print("❌ 上传失败")
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
    except Exception as e:
        print(f"❌ 程序错误: {e}")

if __name__ == "__main__":
    main()