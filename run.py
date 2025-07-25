#!/usr/bin/env python
"""
内容处理流水线启动脚本
"""
import os
import sys
import argparse
import logging
from scripts.core.content_pipeline import ContentPipeline

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
    
    # 初始化一次，避免重复日志
    pipeline = ContentPipeline("config/pipeline_config.yml", verbose=args.verbose)
    
    # 记录用户会话开始
    import time
    session_id = int(time.time() * 1000) % 100000  # 简短的会话 ID
    pipeline.log(f"===== 用户会话开始 [{session_id}] =====", level="info", force=True)
    
    session_count = 1  # 记录操作次数
    
    while True:  # 主循环，支持返回主菜单
        # 选择操作
        print("\n" + "="*50)
        print("📝 有心言者 - 内容发布系统")
        print("="*50)
        print("请选择操作：")
        print("1. 处理现有草稿")
        print("2. 重新发布已发布文章")
        print("3. 生成测试文章")
        print("0. 退出")
        
        choice = input("\n请输入选项 (1/2/3/0): ").strip()
        pipeline.log(f"用户选择操作: {choice} ({['处理现有草稿', '重新发布已发布文章', '生成测试文章', '退出'][int(choice) if choice.isdigit() and choice in '0123' else -1]})", level="info", force=True)
        
        draft = None
        
        if choice == "1":
            # 处理现有草稿
            pipeline.log("开始处理现有草稿", level="info", force=True)
            draft = pipeline.select_draft()
            if not draft:
                pipeline.log("用户取消或无草稿可处理", level="info", force=True)
                continue  # 返回主菜单
        elif choice == "2":
            # 重新发布已发布文章
            pipeline.log("开始重新发布已发布文章", level="info", force=True)
            post = pipeline.select_published_post()
            if not post:
                pipeline.log("用户取消或无文章可重新发布", level="info", force=True)
                continue  # 返回主菜单
            draft = pipeline.copy_post_to_draft(post)
            if not draft:
                print("复制文章到草稿失败")
                pipeline.log("复制文章到草稿失败", level="error", force=True)
                continue  # 返回主菜单
        elif choice == "3":
            # 生成测试文章
            pipeline.log("开始生成测试文章", level="info", force=True)
            draft = pipeline.generate_test_content()
            if not draft:
                print("生成测试文章失败")
                pipeline.log("生成测试文章失败", level="error", force=True)
                continue  # 返回主菜单
            
            # 测试文章生成成功后，询问是否要发布
            print(f"\n✅ 测试文章已生成: {draft}")
            publish_choice = input("\n是否要发布此测试文章？(y/N): ").strip().lower()
            pipeline.log(f"测试文章生成成功: {draft}, 用户选择{'发布' if publish_choice in ['y', 'yes'] else '不发布'}", level="info", force=True)
            if publish_choice not in ['y', 'yes']:
                print("📄 测试文章已保存到草稿目录，您可以稍后选择 '1. 处理现有草稿' 来发布它")
                continue  # 返回主菜单
        elif choice == "0":
            print("👋 再见！")
            pipeline.log("用户退出系统", level="info", force=True)
            return
        else:
            print("❌ 无效的选择，请重新输入")
            pipeline.log(f"用户输入无效选择: {choice}", level="warning", force=True)
            continue  # 返回主菜单
            
        # 到这里说明有有效的draft需要处理
        break
        
    # 处理发布流程
    
    # 选择发布平台
    pipeline.log(f"开始为文章 '{draft.name}' 选择发布平台", level="info", force=True)
    platforms = pipeline.select_platforms(draft)
    if not platforms:
        # 检查是否是因为已经全部发布
        article_name = draft.stem
        published_platforms = pipeline.status_manager.get_published_platforms(article_name)
        all_enabled_platforms = [name for name, config in pipeline.config["platforms"].items() 
                               if config.get("enabled", False)]
        
        if set(published_platforms) >= set(all_enabled_platforms):
            print("📋 该文章已在所有启用的平台发布，无需重复发布")
            
            # 询问是否仍要进行内容变现处理
            if pipeline.reward_manager:
                print("\n💡 提示：您仍可以为此文章创建内容变现包")
                create_package = input("是否创建内容变现包？(y/N): ").strip().lower()
                if create_package in ['y', 'yes']:
                    try:
                        success, result = pipeline.reward_manager.create_article_package(str(draft), upload_to_github=True)
                        if success:
                            print("💰 内容变现包创建成功!")
                            github_release = result.get('github_release', {})
                            if github_release.get('success'):
                                print(f"📦 GitHub Release: {github_release.get('release_url', 'N/A')}")
                                print(f"⬇️  下载链接: {github_release.get('download_url', 'N/A')}")
                        else:
                            print(f"⚠️ 创建失败: {result.get('error', '未知错误')}")
                    except Exception as e:
                        print(f"❌ 处理异常: {e}")
        else:
            print("📋 未选择任何发布平台")
        
        # 询问是否返回主菜单
        pipeline.log("未选择发布平台或文章已全部发布，返回主菜单", level="info", force=True)
        back_to_menu = input("\n按Enter键返回主菜单...")
        main()  # 重新开始主循环
        return
    
    # 记录选择的平台
    pipeline.log(f"用户选择发布平台: {', '.join(platforms)}", level="info", force=True)
    
    # 询问是否启用内容变现功能
    enable_monetization = pipeline.ask_monetization_preference()
    pipeline.log(f"内容变现功能: {'启用' if enable_monetization else '跳过'}", level="info", force=True)
    
    # 处理并发布
    pipeline.log(f"开始发布处理 - 文章: {draft.name}, 平台: {', '.join(platforms)}", level="info", force=True)
    result = pipeline.process_draft(draft, platforms, enable_monetization=enable_monetization)
    
    # 处理返回结果（兼容旧的布尔值和新的字典格式）
    if isinstance(result, bool):
        # 兼容旧格式
        if result:
            print("✅ 处理完成!")
            pipeline.log("发布处理完成", level="info", force=True)
        else:
            print("⚠️ 处理未完全成功，请检查日志")
            pipeline.log("发布处理未完全成功", level="warning", force=True)
    elif isinstance(result, dict):
        # 新的详细格式
        if result['success']:
            platforms_str = ', '.join(result['successful_platforms']) if result['successful_platforms'] else '无'
            print(f"✅ 处理完成! 成功发布到: {platforms_str}")
            pipeline.log(f"发布成功 - 平台: {platforms_str}", level="info", force=True)
            
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
                        pipeline.log(f"内容变现包创建成功: {github_release.get('release_url', 'N/A')}", level="info", force=True)
                else:
                    print(f"⚠️ 内容变现包创建失败: {monetization.get('error', '未知错误')}")
                    pipeline.log(f"内容变现包创建失败: {monetization.get('error', '未知错误')}", level="warning", force=True)
        else:
            if 'error' in result:
                print(f"❌ 处理失败: {result['error']}")
                pipeline.log(f"发布失败: {result['error']}", level="error", force=True)
            else:
                successful = result.get('successful_platforms', [])
                total = result.get('total_platforms', 0)
                if successful:
                    platforms_str = ', '.join(successful)
                    print(f"⚠️ 部分成功! 已发布到: {platforms_str} (共{total}个平台)")
                    pipeline.log(f"部分发布成功: {platforms_str} (共{total}个平台)", level="warning", force=True)
                else:
                    print(f"❌ 发布失败! 所有{total}个平台都未成功")
                    pipeline.log(f"发布完全失败: 所有{total}个平台都未成功", level="error", force=True)
    else:
        print("⚠️ 处理结果格式异常，请检查日志")
        pipeline.log("处理结果格式异常", level="error", force=True)

if __name__ == "__main__":
    main() 