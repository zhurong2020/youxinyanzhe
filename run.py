#!/usr/bin/env python
"""
内容处理流水线启动脚本
"""
import os
import sys
import argparse
import logging
from scripts.content_pipeline import ContentPipeline

# 禁用 tensorflow 警告
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 禁用特定警告
logging.getLogger('absl').setLevel(logging.ERROR)

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    parser = argparse.ArgumentParser(description="内容处理流水线")
    parser.add_argument("-v", "--verbose", 
                       action="store_true",
                       help="显示详细日志")
    args = parser.parse_args()
    
    pipeline = ContentPipeline("config/pipeline_config.yml", verbose=args.verbose)
    
    # 选择操作
    print("\n请选择操作：")
    print("1. 处理现有草稿")
    print("2. 重新发布已发布文章")
    print("3. 生成测试文章")
    
    choice = input("\n请输入选项 (1/2/3): ").strip()
    
    if choice == "1":
        # 处理现有草稿
        draft = pipeline.select_draft()
        if not draft:
            return
    elif choice == "2":
        # 重新发布已发布文章
        post = pipeline.select_published_post()
        if not post:
            return
        draft = pipeline.copy_post_to_draft(post)
        if not draft:
            print("复制文章到草稿失败")
            return
    elif choice == "3":
        # 生成测试文章
        draft = pipeline.generate_test_content()
        if not draft:
            print("生成测试文章失败")
            return
    else:
        print("无效的选择")
        return
    
    # 选择发布平台
    platforms = pipeline.select_platforms(draft)
    if not platforms:
        print("未选择任何发布平台")
        return
    
    # 询问是否启用内容变现功能
    enable_monetization = pipeline.ask_monetization_preference()
    
    # 处理并发布
    result = pipeline.process_draft(draft, platforms, enable_monetization=enable_monetization)
    
    # 处理返回结果（兼容旧的布尔值和新的字典格式）
    if isinstance(result, bool):
        # 兼容旧格式
        if result:
            print("✅ 处理完成!")
        else:
            print("⚠️ 处理未完全成功，请检查日志")
    elif isinstance(result, dict):
        # 新的详细格式
        if result['success']:
            platforms_str = ', '.join(result['successful_platforms']) if result['successful_platforms'] else '无'
            print(f"✅ 处理完成! 成功发布到: {platforms_str}")
            
            # 显示内容变现结果
            if result.get('monetization'):
                monetization = result['monetization']
                if monetization['success']:
                    print("💰 内容变现包创建成功!")
                    github_release = monetization.get('github_release', {})
                    if github_release.get('success'):
                        print(f"📦 GitHub Release: {github_release.get('release_url', 'N/A')}")
                        print(f"⬇️  下载链接: {github_release.get('download_url', 'N/A')}")
                        print("📧 现在可以通过 reward_system_manager.py 发送奖励给用户了")
                else:
                    print(f"⚠️ 内容变现包创建失败: {monetization.get('error', '未知错误')}")
        else:
            if 'error' in result:
                print(f"❌ 处理失败: {result['error']}")
            else:
                successful = result.get('successful_platforms', [])
                total = result.get('total_platforms', 0)
                if successful:
                    platforms_str = ', '.join(successful)
                    print(f"⚠️ 部分成功! 已发布到: {platforms_str} (共{total}个平台)")
                else:
                    print(f"❌ 发布失败! 所有{total}个平台都未成功")
    else:
        print("⚠️ 处理结果格式异常，请检查日志")

if __name__ == "__main__":
    main() 