#!/usr/bin/env python3
"""
YouTube单个文件上传工具
简化的交互式上传界面
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
        
        print("🎬 YouTube单个文件上传工具")
        print("=" * 50)
        
        # 创建上传器实例
        tester = YouTubeUploadTester()
        
        # 扫描音频文件
        audio_files = tester.scan_audio_files()
        if not audio_files:
            print("❌ 未找到音频文件")
            return
        
        # 显示文件列表
        print(f"\n📁 找到 {len(audio_files)} 个音频文件:")
        print("-" * 60)
        
        for i, file_info in enumerate(audio_files, 1):
            size_mb = file_info['size'] / (1024 * 1024)
            modified = file_info['modified'].strftime('%Y-%m-%d %H:%M')
            
            print(f"{i:2d}. {file_info['name']}")
            print(f"    📊 大小: {size_mb:.1f}MB | 📅 修改: {modified}")
            
            if file_info['type'] == 'youtube_podcast':
                print(f"    📝 标题: {file_info['title']}")
                if file_info['date']:
                    print(f"    📅 日期: {file_info['date']}")
            print()
        
        # 获取用户选择
        while True:
            try:
                choice = input(f"请选择要上传的文件 (1-{len(audio_files)}, 0=退出): ").strip()
                
                if choice == '0':
                    print("👋 再见!")
                    return
                
                if not choice.isdigit():
                    print("❌ 请输入有效数字")
                    continue
                
                file_index = int(choice)
                if not (1 <= file_index <= len(audio_files)):
                    print(f"❌ 请输入 1-{len(audio_files)} 之间的数字")
                    continue
                
                # 选择的文件
                selected_file = audio_files[file_index - 1]
                break
                
            except KeyboardInterrupt:
                print("\n👋 用户取消操作")
                return
            except Exception as e:
                print(f"❌ 输入错误: {e}")
                continue
        
        # 确认上传
        print(f"\n🎯 选择的文件: {selected_file['name']}")
        print(f"📊 文件大小: {selected_file['size'] / (1024 * 1024):.1f}MB")
        
        confirm = input("确认上传到YouTube? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("❌ 取消上传")
            return
        
        # 执行上传
        print("\n🚀 开始上传流程...")
        print("-" * 50)
        
        result = tester.process_single_file(selected_file, show_details=True)
        
        print("\n" + "=" * 50)
        if result:
            print("🎉 上传成功!")
            print("💡 视频已设置为不公开，可通过链接访问")
        else:
            print("❌ 上传失败")
            print("💡 请检查网络连接和API配额")
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
    except Exception as e:
        print(f"❌ 程序错误: {e}")

if __name__ == "__main__":
    main()