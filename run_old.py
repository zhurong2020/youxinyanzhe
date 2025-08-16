#!/usr/bin/env python
"""
有心工坊 - 为有心人打造的数字创作平台
YouXin Workshop - Digital Content Creation Platform for Caring Minds
"""
import os
import sys
import argparse
import logging
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from scripts.core.content_pipeline import ContentPipeline
from scripts.cli.menu_handler import MenuHandler
from scripts.cli.menu_router import MenuRouter

# 加载环境变量
load_dotenv()

# 禁用 tensorflow 警告
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 禁用特定警告
logging.getLogger('absl').setLevel(logging.ERROR)

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    parser = argparse.ArgumentParser(description="有心工坊 - 数字创作平台")
    parser.add_argument("-v", "--verbose", 
                       action="store_true",
                       help="显示详细日志")
    args = parser.parse_args()
    
    # 初始化一次，避免重复日志
    pipeline = ContentPipeline("config/pipeline_config.yml", verbose=args.verbose)
    
    # 初始化菜单处理器和路由器
    menu_handler = MenuHandler(pipeline)
    menu_router = MenuRouter(pipeline)
    
    # 记录用户会话开始
    import time
    session_id = int(time.time() * 1000) % 100000  # 简短的会话 ID
    pipeline.log(f"===== 用户会话开始 [{session_id}] =====", level="info", force=True)
    
    # session_count = 1  # 记录操作次数 - 暂未使用
    
    while True:  # 主循环，支持返回主菜单
        # 显示主菜单
        menu_handler.display_main_menu()
        
        # 获取用户选择
        choice = menu_handler.get_user_choice()
        
        # 验证并记录用户选择
        if not menu_handler.is_valid_choice(choice):
            menu_handler.display_invalid_choice_message(choice)
            continue
            
        menu_handler.log_user_action(choice)
        
        draft = None
        
        if choice == "1":
            # 智能内容发布 (合并1+2)
            draft = menu_router.route_smart_publishing()
            if not draft:
                continue  # 返回主菜单
        elif choice == "2":
            # 内容规范化处理 (保持原4)
            menu_router.route_content_normalization()
            continue  # 返回主菜单
        elif choice == "3":
            # 智能内容创作 (合并5+3)
            draft = menu_router.route_smart_creation()
            if not draft:
                continue  # 返回主菜单
        elif choice == "4":
            # YouTube内容处理 (合并8+13)
            menu_router.route_youtube_processing()
            continue  # 返回主菜单
        elif choice == "5":
            # OneDrive图床管理 (保持原14)
            menu_router.route_onedrive_images()
            continue  # 返回主菜单
        elif choice == "6":
            # 内容变现管理 (保持原6)
            menu_router.route_monetization()
            continue  # 返回主菜单
        elif choice == "7":
            # 语音和音频工具 (合并12+相关)
            menu_router.route_audio_tools()
            continue  # 返回主菜单
        elif choice == "8":
            # 文章更新工具 (保持原9)
            menu_router.route_post_update()
            continue  # 返回主菜单
        elif choice == "9":
            # 系统工具集合 (合并7+10+11)
            menu_router.route_system_tools()
            continue  # 返回主菜单
        elif choice == "0":
            menu_handler.display_exit_message()
            return
            
        # 到这里说明有有效的draft需要处理
        if draft is None:
            continue  # 返回主菜单如果没有草稿
            
        # 草稿预检机制 - 检查是否有需要预处理的问题
        pipeline.log("正在进行草稿质量预检...", level="info", force=True)
        draft_path = Path(draft) if isinstance(draft, str) else draft
        draft_issues = pipeline.check_draft_issues(draft_path)
        
        # 自动处理excerpt缺失问题
        excerpt_missing_issues = [issue for issue in draft_issues if "缺少excerpt字段" in issue]
        if excerpt_missing_issues:
            print("\n🤖 检测到缺少excerpt，正在自动生成...")
            with open(draft_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            if pipeline._auto_generate_excerpt_if_missing(draft_path, current_content):
                # 重新检查问题列表，移除已解决的excerpt问题
                draft_issues = pipeline.check_draft_issues(draft_path)
                print("🔄 已重新检查草稿质量...")
        
        if draft_issues:
            print(f"\n⚠️ 发现草稿质量问题：")
            for issue in draft_issues:
                print(f"   • {issue}")
            
            print(f"\n🔧 建议的处理方案：")
            if any("图片" in issue for issue in draft_issues):
                print(f"   1. 使用 '5. OneDrive图床管理' → '处理单个草稿' 来处理图片")
                print(f"   2. 或使用 '2. 内容规范化处理' 来完善内容格式")
            
            if any("格式" in issue or "分页" in issue or "长度" in issue for issue in draft_issues):
                print(f"   3. 使用 '2. 内容规范化处理' 来修复格式问题")
            
            # 添加摘要相关建议
            summary_issues = [issue for issue in draft_issues if any(keyword in issue for keyword in ["excerpt", "more", "摘要"])]
            if summary_issues:
                summary_suggestions = pipeline._get_summary_fix_suggestions(summary_issues)
                for suggestion in summary_suggestions:
                    print(f"   {suggestion}")
                
            print(f"\n💡 推荐工作流程：")
            print(f"   草稿预处理 → 2.内容规范化处理 → 1.智能内容发布")
            
            continue_choice = input(f"\n是否仍要继续发布？(y/N): ").strip().lower()
            if continue_choice not in ['y', 'yes']:
                print("📝 已取消发布，请先处理草稿问题")
                pipeline.log("用户选择取消发布，需先处理草稿质量问题", level="info", force=True)
                continue  # 返回主菜单
            else:
                print("⚠️ 继续发布可能导致内容不完整，建议发布后及时修复")
                pipeline.log("用户选择继续发布存在问题的草稿", level="warning", force=True)
        else:
            pipeline.log("✅ 草稿质量检查通过", level="info", force=True)
        
        # 处理发布流程（在while循环内）
        
        # 确保draft是Path类型
        if not isinstance(draft, Path):
            pipeline.log(f"错误：无效的草稿类型 {type(draft)}", level="error", force=True)
            continue
        
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
            
            # 自动返回主菜单 - 使用continue而不是return
            pipeline.log("未选择发布平台或文章已全部发布，返回主菜单", level="info", force=True)
            print("\n✅ 自动返回主菜单...")
            continue  # 返回到while循环开头
        
        # 记录选择的平台
        pipeline.log(f"用户选择发布平台: {', '.join(platforms)}", level="info", force=True)
        
        # 询问是否启用内容变现功能
        enable_monetization = pipeline.ask_monetization_preference()
        pipeline.log(f"内容变现功能: {'启用' if enable_monetization else '跳过'}", level="info", force=True)
        
        # 选择会员分级
        member_tier = pipeline.select_member_tier()
        if member_tier:
            pipeline.log(f"会员分级: {member_tier}", level="info", force=True)
        else:
            pipeline.log("跳过会员分级设置", level="info", force=True)
        
        # 处理并发布
        pipeline.log(f"开始发布处理 - 文章: {draft.name}, 平台: {', '.join(platforms)}", level="info", force=True)
        result = pipeline.process_draft(draft, platforms, enable_monetization=enable_monetization, member_tier=member_tier)
        
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
                
                # 检查是否有微信发布指导文件生成
                if 'wechat' in result.get('successful_platforms', []):
                    guidance_dir = Path(".tmp/output/wechat_guides")
                    if guidance_dir.exists():
                        latest_files = sorted(guidance_dir.glob("*_guide.md"), key=lambda p: p.stat().st_mtime, reverse=True)
                        if latest_files:
                            print(f"📧 微信发布指导文件: {latest_files[0]}")
                            print("💡 请按照指导文件完成微信公众号手动发布")
                
                # 显示内容变现结果
                if result.get('monetization'):
                    monetization = result['monetization']
                    if monetization['success']:
                        print("💰 内容变现包创建成功!")
                        github_release = monetization.get('github_release', {})
                        if github_release.get('success'):
                            print(f"📦 GitHub Release: {github_release.get('release_url', 'N/A')}")
                            print(f"⬇️  下载链接: {github_release.get('download_url', 'N/A')}")
                            # Check if guidance file was generated
                            guidance_dir = Path(".tmp/output/wechat_guides")
                            if guidance_dir.exists():
                                latest_files = sorted(guidance_dir.glob("*_guide.md"), key=lambda p: p.stat().st_mtime, reverse=True)
                                if latest_files:
                                    print(f"📧 微信发布指导文件已生成: {latest_files[0]}")
                            print("📧 内容变现管理请使用本程序 run.py 选项 6: 内容变现系统")
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
        
            # 发布完成后，自动返回主菜单（避免交互式输入卡死）
            print("\n" + "="*50)
            print("✅ 发布流程完成，自动返回主菜单...")
            pipeline.log("发布流程结束，返回主菜单", level="info", force=True)
            continue  # 返回到while循环开头，显示主菜单


def execute_script_with_logging(pipeline, script_path: Path, args: list, description: str) -> subprocess.CompletedProcess:
    """
    执行脚本并记录日志的辅助函数
    
    Args:
        pipeline: ContentPipeline实例，用于日志记录
        script_path: 脚本路径
        args: 脚本参数列表
        description: 操作描述
    
    Returns:
        subprocess.CompletedProcess: 执行结果
    """
    cmd = [sys.executable, str(script_path)] + args
    cmd_str = ' '.join(cmd)
    
    pipeline.log(f"开始执行: {description} - {cmd_str}", level="info", force=True)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5分钟超时
        
        if result.returncode == 0:
            pipeline.log(f"执行成功: {description}", level="info", force=True)
            if result.stdout.strip():
                # 记录关键输出信息（简化版）
                output_lines = result.stdout.strip().split('\n')
                key_lines = [line for line in output_lines if any(keyword in line for keyword in ['✅', '❌', '⚠️', 'ERROR', 'SUCCESS', '成功', '失败', '错误'])]
                if key_lines:
                    pipeline.log(f"关键输出: {'; '.join(key_lines[:3])}", level="info", force=True)  # 只记录前3行关键信息
        else:
            pipeline.log(f"执行失败: {description} (返回码: {result.returncode})", level="error", force=True)
            if result.stderr.strip():
                pipeline.log(f"错误详情: {result.stderr.strip()[:200]}...", level="error", force=True)  # 限制错误信息长度
        
        return result
        
    except subprocess.TimeoutExpired:
        pipeline.log(f"执行超时: {description}", level="error", force=True)
        return subprocess.CompletedProcess(cmd, -1, "", "执行超时")
    except Exception as e:
        pipeline.log(f"执行异常: {description} - {str(e)}", level="error", force=True)
        return subprocess.CompletedProcess(cmd, -1, "", str(e))


def handle_content_normalization_menu(pipeline):
    """处理内容规范化处理菜单"""
    print("\n" + "="*50)
    print("📝 内容规范化处理")
    print("="*50)
    print("📋 功能说明：")
    print("   • 多源内容统一处理：手工草稿、YouTube内容、灵感生成内容")
    print("   • Jekyll规范检查：Front Matter、语法、路径验证")
    print("   • 智能内容结构：摘要(50-60字) + 背景介绍 + 主体内容")
    print("   • 自动分类标签：四大内容体系智能分类")
    print("   • 质量验证检查：字符长度、链接、图片路径等")
    
    print("\n🎯 标准内容结构：")
    print("   📄 Front Matter → 摘要段落 → <!-- more --> → 背景介绍 → 主体内容")
    
    print("\n⚠️  使用说明：")
    print("   • 支持：.txt/.md文件、YouTube生成内容、主题灵感输出")
    print("   • 输出：符合Jekyll规范的发布就绪草稿")
    print("   • 检查：自动验证内容质量和结构完整性")
    
    print("\n请选择操作：")
    print("1. 处理单个内容文件")
    print("2. 批量处理多个文件")
    print("3. YouTube内容规范化")
    print("4. 灵感生成内容处理")
    print("5. 查看内容质量检查")
    print("6. 查看使用示例")
    print("0. 返回主菜单")
    
    sub_choice = input("\n请输入选项 (1-6/0): ").strip()
    pipeline.log(f"内容规范化处理 - 用户选择: {sub_choice}", level="info", force=True)
    
    if sub_choice == "1":
        # 格式化单个草稿文件
        try:
            # 列出可能的草稿文件
            import glob
            potential_files = []
            for pattern in ["*.txt", "*.md"]:
                potential_files.extend(glob.glob(pattern))
                potential_files.extend(glob.glob(f"_drafts/**/{pattern}", recursive=True))
                potential_files.extend(glob.glob(f"drafts/**/{pattern}", recursive=True))
            
            if potential_files:
                print(f"\n📄 发现 {len(potential_files)} 个可能的草稿文件：")
                for i, file in enumerate(potential_files[:20], 1):  # 最多显示20个
                    print(f"  {i}. {file}")
                if len(potential_files) > 20:
                    print(f"  ... 和其他 {len(potential_files) - 20} 个文件")
                print("  0. 手动输入文件路径")
                
                file_choice = input(f"\n请选择文件 (1-{min(len(potential_files), 20)}/0): ").strip()
                
                if file_choice == "0":
                    input_file = input("请输入文件路径: ").strip()
                elif file_choice.isdigit() and 1 <= int(file_choice) <= min(len(potential_files), 20):
                    input_file = potential_files[int(file_choice) - 1]
                else:
                    print("❌ 无效选择")
                    return
            else:
                input_file = input("请输入草稿文件路径: ").strip()
            
            if not input_file or not Path(input_file).exists():
                print("❌ 文件不存在或路径无效")
                return
                
            print(f"\n🔄 正在格式化草稿: {input_file}")
            
            # 使用统一的格式化接口
            result = pipeline.format_content_file(Path(input_file))
            
            if result['success']:
                print("✅ 格式化完成！")
                print(f"📄 输出文件: {result['output_file']}")
                
                # 显示质量检查结果
                if result.get('check_passed', False):
                    print("✅ 内容质量检查通过")
                else:
                    if result.get('auto_fixes_applied'):
                        print("🔧 自动修复的问题:")
                        for fix in result['auto_fixes_applied']:
                            print(f"   • {fix}")
                    
                    if result.get('manual_fixes_needed'):
                        print("💡 需要手动处理的问题:")
                        for item in result['manual_fixes_needed']:
                            print(f"   • {item['issue']}")
                
                print("💡 您可以选择 '1. 智能内容发布' 来发布格式化后的文章")
            else:
                print(f"❌ 格式化失败: {result['error']}")
                
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            
    elif sub_choice == "2":
        # 批量格式化多个文件
        batch_dir = input("\n请输入包含草稿文件的目录路径: ").strip()
        if not batch_dir or not Path(batch_dir).exists():
            print("❌ 目录不存在")
            return
            
        try:
            import glob
            files_to_process = []
            for pattern in ["*.txt", "*.md"]:
                files_to_process.extend(glob.glob(f"{batch_dir}/{pattern}"))
                files_to_process.extend(glob.glob(f"{batch_dir}/**/{pattern}", recursive=True))
            
            if not files_to_process:
                print("❌ 未找到可处理的草稿文件")
                return
                
            print(f"\n📄 找到 {len(files_to_process)} 个文件:")
            for file in files_to_process:
                print(f"  • {file}")
                
            confirm = input(f"\n确定要批量处理这些文件吗？(y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("❌ 用户取消操作")
                return
                
            print("\n🔄 开始批量格式化...")
            success_count = 0
            total_issues_fixed = 0
            
            for file in files_to_process:
                try:
                    print(f"\n处理: {file}")
                    
                    # 使用统一的格式化接口
                    result = pipeline.format_content_file(Path(file))
                    
                    if result['success']:
                        success_count += 1
                        print(f"✅ 成功: {file}")
                        print(f"   输出: {result['output_file']}")
                        
                        # 统计修复的问题
                        if result.get('auto_fixes_applied'):
                            total_issues_fixed += len(result['auto_fixes_applied'])
                            
                        # 显示需要手动处理的问题
                        if result.get('manual_fixes_needed'):
                            print(f"   ⚠️ {len(result['manual_fixes_needed'])} 个问题需要手动处理")
                    else:
                        print(f"❌ 失败: {file}")
                        print(f"   错误: {result['error']}")
                            
                except Exception as e:
                    print(f"❌ 处理 {file} 时出错: {e}")
                    
            print(f"\n📊 批量处理完成：")
            print(f"   • 成功文件: {success_count}/{len(files_to_process)}")
            print(f"   • 自动修复: {total_issues_fixed} 个问题")
            print("💡 您可以选择 '1. 智能内容发布' 来发布格式化后的文章")
            
        except Exception as e:
            print(f"❌ 批量操作失败: {e}")
            
    elif sub_choice == "3":
        # 查看使用示例
        print("\n" + "="*40)
        print("📖 格式化草稿使用示例")
        print("="*40)
        
        example_content = '''
📝 示例输入文件 (example_draft.txt):

深度学习的最新进展与应用前景

人工智能领域在2024年取得了重大突破，特别是在大语言模型和计算机视觉方面。
本文将探讨这些技术的最新发展和未来应用前景。

## 大语言模型的突破
GPT-4和Claude等模型在理解能力、推理能力方面有了显著提升...

## 计算机视觉的进展
多模态模型如GPT-4V在图像理解方面展现出惊人的能力...

---

🔄 工具会自动生成:

- 智能分类: tech-empowerment (技术赋能)
- 自动标签: ["人工智能", "深度学习", "机器学习", "技术趋势"]
- 生成摘要: 探讨2024年人工智能领域的最新突破，重点分析大语言模型和计算机视觉的发展
- 完整front matter: 包含日期、分类、标签等元数据
- 格式化内容: 符合Jekyll和项目规范的完整文章

💡 输出文件会保存到 _drafts/ 目录，可直接用于发布流程
        '''
        
        print(example_content)
        
    elif sub_choice == "4":
        # 查看分类关键词
        print("\n" + "="*40)
        print("🔍 内容智能分类关键词")
        print("="*40)
        
        categories_info = '''
🧠 认知升级 (cognitive-upgrade):
   关键词: 思维、学习、认知、心理学、方法论、习惯、效率、自我提升
   
🛠️ 技术赋能 (tech-empowerment):  
   关键词: 技术、工具、自动化、编程、软件、AI、效率工具、数字化
   
🌍 全球视野 (global-perspective):
   关键词: 国际、全球、文化、跨国、趋势、政策、经济、社会
   
💰 投资理财 (investment-finance):
   关键词: 投资、理财、金融、股票、基金、收益、风险、财务、资产

💡 分类算法会根据内容中这些关键词的出现频率和权重进行智能判断
💡 如果关键词评分接近，会根据文章长度等因素选择最合适的分类
        '''
        
        print(categories_info)
        
    elif sub_choice != "0":
        print("❌ 无效的选择，请重新输入")
    
    if sub_choice != "0":
        input("\n按Enter键返回主菜单...")


def handle_topic_inspiration_menu(pipeline):
    """处理主题灵感生成菜单 - 委托给CLI模块处理"""
    from scripts.cli.content_menu_handler import ContentMenuHandler
    
    content_handler = ContentMenuHandler(pipeline)
    return content_handler.handle_topic_inspiration_menu()




def handle_monetization_menu(pipeline):
    """处理内容变现管理菜单"""
    print("\n" + "="*40)
    print("💰 内容变现管理")
    print("="*40)
    print("📋 功能说明：")
    print("   • 管理文章的内容变现包创建和发送")
    print("   • 查看和管理奖励系统状态") 
    print("   • 发送内容包给打赏用户")
    print("\n⚠️  前提条件：")
    print("   • 需要配置GitHub Token (用于Release创建)")
    print("   • 需要配置邮件服务器 (用于发送奖励)")
    print("   • 确保相关环境变量已设置")
    
    print("\n请选择操作：")
    print("1. 为文章创建内容变现包")
    print("2. 查看奖励发送状态")
    print("3. 手动发送奖励给用户")
    print("4. 运行奖励系统测试")
    print("\n📋 会员管理系统：")
    print("5. 生成测试访问码")
    print("6. 验证访问码")
    print("7. 查看会员系统统计")
    print("8. 处理待处理注册")
    print("9. 导出会员数据")
    print("0. 返回主菜单")
    
    sub_choice = input("\n请输入选项 (1-9/0): ").strip()
    pipeline.log(f"内容变现管理 - 用户选择: {sub_choice}", level="info", force=True)
    
    if sub_choice == "1":
        # 为文章创建内容变现包
        try:
            # 列出可用的已发布文章
            posts_dir = Path("_posts")
            if posts_dir.exists():
                posts = list(posts_dir.glob("*.md"))
                if posts:
                    print("\n📄 已发布文章列表：")
                    for i, post in enumerate(posts[:10]):  # 显示最新10篇
                        print(f"  {i+1}. {post.stem}")
                    print("  0. 返回上级菜单")
                    
                    choice = input("\n请输入文章编号，或直接输入文章路径 (0返回): ").strip()
                    
                    if choice == "0" or choice == "":
                        print("📋 返回内容变现管理菜单")
                        return
                    
                    if choice.isdigit() and 1 <= int(choice) <= len(posts):
                        article_path = str(posts[int(choice)-1])
                    else:
                        article_path = choice
                    
                    if article_path and Path(article_path).exists():
                        print(f"\n🔄 正在为文章创建内容变现包: {article_path}")
                        # 调用reward_system_manager
                        script_path = Path("scripts/utils/reward_system_manager.py")
                        result = execute_script_with_logging(
                            pipeline, script_path, ["create", article_path], 
                            "创建内容变现包"
                        )
                        print(result.stdout)
                        if result.stderr:
                            print(f"❌ 错误: {result.stderr}")
                    else:
                        print("❌ 文章文件不存在")
                else:
                    print("📋 未找到已发布文章")
            else:
                print("📋 _posts目录不存在")
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            
    elif sub_choice == "2":
        # 查看奖励发送状态
        try:
            script_path = Path("scripts/utils/reward_system_manager.py")
            result = execute_script_with_logging(
                pipeline, script_path, ["stats"], 
                "查看奖励发送状态"
            )
            print(result.stdout)
            if result.stderr:
                print(f"❌ 错误: {result.stderr}")
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            
    elif sub_choice == "3":
        # 手动发送奖励给用户
        email = input("\n请输入用户邮箱: ").strip()
        article_title = input("请输入文章标题: ").strip()
        if email and article_title:
            try:
                script_path = Path("scripts/utils/reward_system_manager.py")
                result = execute_script_with_logging(
                    pipeline, script_path, ["send", email, article_title], 
                    "发送奖励给用户"
                )
                print(result.stdout)
                if result.stderr:
                    print(f"❌ 错误: {result.stderr}")
            except Exception as e:
                print(f"❌ 操作失败: {e}")
        else:
            print("❌ 邮箱和文章标题不能为空")
            
    elif sub_choice == "4":
        # 运行奖励系统测试
        try:
            script_path = Path("scripts/tools/testing/test_reward_system.py")
            print("\n🧪 运行奖励系统测试...")
            result = execute_script_with_logging(
                pipeline, script_path, [], 
                "奖励系统测试"
            )
            print(result.stdout)
            if result.stderr:
                print(f"❌ 错误: {result.stderr}")
        except Exception as e:
            print(f"❌ 操作失败: {e}")
    
    elif sub_choice == "5":
        # 生成测试访问码
        handle_generate_access_code(pipeline)
    
    elif sub_choice == "6":
        # 验证访问码
        handle_validate_access_code(pipeline)
    
    elif sub_choice == "7":
        # 查看会员系统统计
        handle_member_stats(pipeline)
    
    elif sub_choice == "8":
        # 处理待处理注册
        handle_process_registrations(pipeline)
    
    elif sub_choice == "9":
        # 导出会员数据
        handle_export_member_data(pipeline)
    
    elif sub_choice != "0":
        print("❌ 无效的选择，请重新输入")
    
    input("\n按Enter键返回主菜单...")


def handle_system_check_menu(pipeline):
    """处理系统状态检查菜单"""
    print("\n" + "="*40)
    print("🔍 系统状态检查")
    print("="*40)
    print("📋 功能说明：")
    print("   • 检查微信发布系统状态和输出文件")
    print("   • 检查GitHub Token有效性和过期时间")
    print("   • 检查ElevenLabs TTS服务配额状态和Pro功能")
    print("   • 验证系统各组件工作状态")
    
    print("\n请选择检查项目：")
    print("1. 微信系统状态检查")
    print("2. GitHub Token状态检查")
    print("3. ElevenLabs配额检查")
    print("4. 综合系统检查")
    print("0. 返回主菜单")
    
    sub_choice = input("\n请输入选项 (1-4/0): ").strip()
    pipeline.log(f"系统状态检查 - 用户选择: {sub_choice}", level="info", force=True)
    
    if sub_choice == "1":
        # 微信系统状态检查
        try:
            script_path = Path("scripts/tools/wechat_system_verify.py")
            print("\n🔍 检查微信发布系统状态...")
            result = execute_script_with_logging(
                pipeline, script_path, [], 
                "微信系统状态检查"
            )
            print(result.stdout)
            if result.stderr:
                print(f"❌ 错误: {result.stderr}")
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            
    elif sub_choice == "2":
        # GitHub Token状态检查
        try:
            script_path = Path("scripts/tools/checks/check_github_token.py")
            print("\n🔍 检查GitHub Token状态...")
            result = execute_script_with_logging(
                pipeline, script_path, [], 
                "GitHub Token状态检查"
            )
            print(result.stdout)
            if result.stderr:
                print(f"❌ 错误: {result.stderr}")
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            
    elif sub_choice == "3":
        # ElevenLabs配额检查
        try:
            print("\n🔍 检查ElevenLabs配额状态和Pro功能...")
            
            # 检查Pro配置文件
            import yaml
            pro_config_path = Path("config/elevenlabs_voices_pro.yml")
            standard_config_path = Path("config/elevenlabs_voices.yml")
            
            if pro_config_path.exists():
                with open(pro_config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                print("✅ 检测到ElevenLabs Pro配置文件")
                pro_features = config.get('elevenlabs_voices', {}).get('pro_features', {})
                if pro_features.get('enabled'):
                    print("🌟 Pro功能: 语音增强、高级控制、商业许可等")
            elif standard_config_path.exists():
                print("✅ 使用标准ElevenLabs配置")
            else:
                print("⚠️ 未找到ElevenLabs配置文件")
            
            # 直接检查ElevenLabs配额，不依赖完整的YouTubePodcastGenerator
            import os
            elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
            
            if not elevenlabs_api_key:
                print("❌ 未配置ElevenLabs API密钥")
                print("💡 请在.env文件中设置ELEVENLABS_API_KEY")
                return
                
            try:
                from elevenlabs import ElevenLabs
                elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key.strip())
                
                # 获取用户信息和配额
                user_info = elevenlabs_client.user.get()
                
                if hasattr(user_info, 'subscription'):
                    subscription = user_info.subscription
                    
                    # 获取配额信息
                    character_count = getattr(subscription, 'character_count', 0)
                    character_limit = getattr(subscription, 'character_limit', 0)
                    remaining_characters = character_limit - character_count
                    
                    # 计算使用百分比
                    usage_percentage = (character_count / character_limit * 100) if character_limit > 0 else 0
                    
                    print(f"📊 ElevenLabs配额状态:")
                    print(f"   已使用: {character_count:,} characters")
                    print(f"   总配额: {character_limit:,} characters")
                    print(f"   剩余额度: {remaining_characters:,} characters")
                    print(f"   使用率: {usage_percentage:.1f}%")
                    
                    # 配额预警
                    if usage_percentage > 90:
                        print("⚠️ ElevenLabs配额即将用完！")
                    elif usage_percentage > 75:
                        print("⚠️ ElevenLabs配额使用率较高")
                        
                    # 估算剩余可生成的音频时长（粗略估算：每分钟约100字符）
                    estimated_minutes = remaining_characters // 100
                    if estimated_minutes < 10:
                        print(f"⚠️ 预计剩余可生成音频约{estimated_minutes}分钟")
                    else:
                        print(f"💡 预计剩余可生成音频约{estimated_minutes}分钟")
                        
                else:
                    print("❌ 无法获取ElevenLabs订阅信息")
                    
            except ImportError:
                print("❌ ElevenLabs库未安装")
                print("💡 请运行: pip install elevenlabs")
            except Exception as api_error:
                error_str = str(api_error)
                if "missing_permissions" in error_str and "user_read" in error_str:
                    print("❌ ElevenLabs API密钥权限不足")
                    print("💡 API密钥缺少'user_read'权限，无法读取用户配额信息")
                    print("💡 请在ElevenLabs官网重新生成具有完整权限的API密钥")
                    print("\n🔧 解决方案:")
                    print("   1. 访问 https://elevenlabs.io/app/settings/api-keys")
                    print("   2. 删除当前API密钥并重新生成")
                    print("   3. 确保勾选所有权限，特别是'user_read'")
                    print("   4. 更新.env文件中的ELEVENLABS_API_KEY")
                    print("\n✅ 即使无法读取配额，Pro账户语音生成功能仍可正常使用")
                elif "401" in error_str:
                    print("❌ ElevenLabs API密钥无效或已过期")
                    print("💡 请检查API密钥是否正确配置在.env文件中")
                else:
                    print(f"❌ ElevenLabs API错误: {api_error}")
            
        except Exception as e:
            print(f"❌ ElevenLabs配额检查失败: {e}")
            
    elif sub_choice == "4":
        # 综合系统检查
        print("\n🔄 正在进行综合系统检查...")
        
        # 检查微信系统
        try:
            script_path = Path("scripts/tools/wechat_system_verify.py")
            result = execute_script_with_logging(
                pipeline, script_path, [], 
                "综合检查-微信系统"
            )
            print(result.stdout)
        except Exception as e:
            print(f"❌ 微信系统检查失败: {e}")
        
        print("\n" + "-"*40)
        
        # 检查GitHub Token
        try:
            script_path = Path("scripts/tools/checks/check_github_token.py")
            result = execute_script_with_logging(
                pipeline, script_path, [], 
                "综合检查-GitHub Token"
            )
            print(result.stdout)
        except Exception as e:
            print(f"❌ GitHub Token检查失败: {e}")
        
        print("-" * 40)
        
        # 检查YouTube OAuth状态
        try:
            script_path = Path("scripts/tools/checks/check_youtube_oauth.py")
            result = execute_script_with_logging(
                pipeline, script_path, [], 
                "综合检查-YouTube OAuth"
            )
            print(result.stdout)
        except Exception as e:
            print(f"❌ YouTube OAuth检查失败: {e}")
        
        print("\n" + "-"*40)
        
        # 检查ElevenLabs配额
        try:
            print("\n🔍 检查ElevenLabs配额状态...")
            
            # 直接检查ElevenLabs配额，不依赖完整的YouTubePodcastGenerator
            import os
            elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
            
            if not elevenlabs_api_key:
                print("❌ 未配置ElevenLabs API密钥")
            else:
                try:
                    from elevenlabs import ElevenLabs
                    elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key.strip())
                    
                    # 获取用户信息和配额
                    user_info = elevenlabs_client.user.get()
                    
                    if hasattr(user_info, 'subscription'):
                        subscription = user_info.subscription
                        
                        # 获取配额信息
                        character_count = getattr(subscription, 'character_count', 0)
                        character_limit = getattr(subscription, 'character_limit', 0)
                        remaining_characters = character_limit - character_count
                        
                        # 计算使用百分比
                        usage_percentage = (character_count / character_limit * 100) if character_limit > 0 else 0
                        
                        print(f"📊 ElevenLabs配额状态:")
                        print(f"   已使用: {character_count:,} characters")
                        print(f"   总配额: {character_limit:,} characters")
                        print(f"   剩余额度: {remaining_characters:,} characters")
                        print(f"   使用率: {usage_percentage:.1f}%")
                        
                        # 配额预警
                        if usage_percentage > 90:
                            print("⚠️ ElevenLabs配额即将用完！")
                        elif usage_percentage > 75:
                            print("⚠️ ElevenLabs配额使用率较高")
                            
                        # 估算剩余可生成的音频时长（粗略估算：每分钟约100字符）
                        estimated_minutes = remaining_characters // 100
                        if estimated_minutes < 10:
                            print(f"⚠️ 预计剩余可生成音频约{estimated_minutes}分钟")
                        else:
                            print(f"💡 预计剩余可生成音频约{estimated_minutes}分钟")
                            
                    else:
                        print("❌ 无法获取ElevenLabs订阅信息")
                        
                except ImportError:
                    print("❌ ElevenLabs库未安装")
                except Exception as api_error:
                    error_str = str(api_error)
                    if "missing_permissions" in error_str and "user_read" in error_str:
                        print("❌ ElevenLabs API密钥权限不足")
                        print("💡 API密钥缺少'user_read'权限，无法读取用户配额信息")
                        print("💡 请在ElevenLabs官网重新生成具有完整权限的API密钥")
                        print("\n🔧 解决方案:")
                        print("   1. 访问 https://elevenlabs.io/app/settings/api-keys")
                        print("   2. 删除当前API密钥并重新生成")
                        print("   3. 确保勾选所有权限，特别是'user_read'")
                        print("   4. 更新.env文件中的ELEVENLABS_API_KEY")
                        print("\n✅ 即使无法读取配额，Pro账户语音生成功能仍可正常使用")
                    elif "401" in error_str:
                        print("❌ ElevenLabs API密钥无效或已过期")
                        print("💡 请检查API密钥是否正确配置在.env文件中")
                    else:
                        print(f"❌ ElevenLabs API错误: {api_error}")
            
        except Exception as e:
            print(f"❌ ElevenLabs配额检查失败: {e}")
    
    input("\n按Enter键返回主菜单...")


def handle_post_update_menu(pipeline):
    """处理文章更新工具菜单"""
    print("\n" + "="*40)
    print("📝 文章更新工具")
    print("="*40)
    print("📋 功能说明：")
    print("   • 更新已发布的文章内容")
    print("   • 支持两种模式：直接编辑或完整处理流程")
    print("   • 自动处理Git提交")
    print("\n⚠️  使用说明：")
    print("   • 文章名称需包含日期前缀 (YYYY-MM-DD-)")
    print("   • 工具会自动查找匹配的文章文件")
    print("   • 支持直接编辑模式和流水线处理模式")
    
    print("\n请选择操作：")
    print("1. 更新已发布文章 (直接编辑模式)")
    print("2. 更新已发布文章 (流水线处理模式)")
    print("3. 修改文章会员等级")
    print("4. 查看文章更新帮助")
    print("0. 返回主菜单")
    
    sub_choice = input("\n请输入选项 (1-4/0): ").strip()
    choice_display = sub_choice if sub_choice else "(空选择)"
    pipeline.log(f"文章更新工具 - 用户选择: {choice_display}", level="info", force=True)
    
    if sub_choice in ["1", "2"]:
        # 列出可用的已发布文章
        posts_dir = Path("_posts")
        if posts_dir.exists():
            posts = list(posts_dir.glob("*.md"))
            if posts:
                print("\n📄 已发布文章列表：")
                for i, post in enumerate(posts[-10:]):  # 显示最新10篇
                    print(f"  {i+1}. {post.name}")
                
                print("\n💡 您可以:")
                print("   • 输入文章编号选择文章")
                print("   • 直接输入文章名称 (支持部分匹配)")
                print("   • 输入完整的文章名称 (包含日期前缀)")
                
                choice = input("\n请输入选择: ").strip()
                
                # 确定文章名称
                article_name = ""
                if choice.isdigit() and 1 <= int(choice) <= len(posts[-10:]):
                    article_name = posts[-(10-int(choice)+1)].stem  # 对应到实际索引
                else:
                    article_name = choice
                
                if article_name:
                    mode = "direct" if sub_choice == "1" else "pipeline"
                    commit_msg = input(f"\n请输入Git提交信息 (默认: Update post): ").strip()
                    if not commit_msg:
                        commit_msg = "Update post"
                    
                    try:
                        script_path = Path("scripts/update_post.py")
                        args = [article_name, "--mode", mode, "--message", commit_msg]
                        print(f"\n🔄 正在更新文章: {article_name} (模式: {mode})")
                        result = execute_script_with_logging(
                            pipeline, script_path, args, 
                            f"更新文章-{mode}模式"
                        )
                        print(result.stdout)
                        if result.stderr:
                            print(f"❌ 错误: {result.stderr}")
                    except Exception as e:
                        print(f"❌ 操作失败: {e}")
                else:
                    print("❌ 未选择文章")
            else:
                print("📋 未找到已发布文章")
        else:
            print("📋 _posts目录不存在")
    elif sub_choice == "0":
        # 返回主菜单
        pass
    elif sub_choice == "":
        # 用户未输入任何内容，提示并返回
        print("❌ 未选择任何选项")
    elif sub_choice == "3":
        # 修改文章会员等级
        print("\n📊 修改文章会员等级")
        print("="*40)
        
        # 列出已发布文章
        posts_dir = Path("_posts")
        if not posts_dir.exists():
            print("❌ 未找到_posts目录")
            return
            
        posts = list(posts_dir.glob("*.md"))
        if not posts:
            print("❌ 未找到已发布的文章")
            return
            
        # 显示文章列表
        print("\n📄 已发布文章列表：")
        for i, post in enumerate(posts[-10:]):  # 显示最新10篇
            print(f"  {i+1}. {post.name}")
        
        choice = input("\n请选择文章 (输入编号或文章名): ").strip()
        
        # 确定文章文件
        selected_post = None
        if choice.isdigit() and 1 <= int(choice) <= len(posts[-10:]):
            selected_post = posts[-(10-int(choice)+1)]
        else:
            # 根据名称搜索
            for post in posts:
                if choice in post.name:
                    selected_post = post
                    break
        
        if not selected_post:
            print("❌ 未找到指定的文章")
            return
            
        print(f"\n📝 选择的文章: {selected_post.name}")
        
        # 读取当前文章内容获取现有会员等级
        try:
            import yaml
            with open(selected_post, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析front matter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    front_matter = yaml.safe_load(parts[1])
                    current_level = front_matter.get('member_level', '免费')
                    print(f"当前会员等级: {current_level}")
                    
                    # 显示会员等级选项
                    print("\n请选择新的会员等级:")
                    print("0. 免费文章")
                    print("1. VIP1 体验会员")
                    print("2. VIP2 月度会员") 
                    print("3. VIP3 季度会员")
                    print("4. VIP4 年度会员")
                    
                    level_choice = input("\n请输入选项 (0-4): ").strip()
                    
                    level_map = {
                        '0': '免费',
                        '1': 'VIP1', 
                        '2': 'VIP2',
                        '3': 'VIP3',
                        '4': 'VIP4'
                    }
                    
                    if level_choice in level_map:
                        new_level = level_map[level_choice]
                        front_matter['member_level'] = new_level
                        
                        # 重新构建文件内容
                        new_front_matter = yaml.dump(front_matter, allow_unicode=True, default_flow_style=False)
                        new_content = f"---\n{new_front_matter}---\n{parts[2]}"
                        
                        # 写入文件
                        with open(selected_post, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        print(f"✅ 会员等级已更新: {current_level} → {new_level}")
                        
                        # Git提交
                        commit_msg = f"Update member level: {selected_post.name} → {new_level}"
                        try:
                            import subprocess
                            subprocess.run(["git", "add", str(selected_post)], check=True)
                            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                            print("✅ 更改已提交到Git")
                        except Exception as e:
                            print(f"⚠️ Git提交失败: {e}")
                    else:
                        print("❌ 无效的选择")
                else:
                    print("❌ 文章格式错误，未找到front matter")
        except Exception as e:
            print(f"❌ 处理文章失败: {e}")
            
    elif sub_choice == "4":
        # 显示帮助信息
        print("\n📖 文章更新工具帮助")
        print("="*40)
        print("🔧 使用方式:")
        print("   python scripts/update_post.py <文章名称> [选项]")
        print("\n📋 参数说明:")
        print("   文章名称：")
        print("     • 完整名称: 2025-01-18-tesla-ai-empire") 
        print("     • 部分匹配: tesla-ai-empire")
        print("     • 如果有多个匹配会提示选择")
        print("\n🛠️ 模式选项:")
        print("   --mode direct   : 直接编辑并提交 (默认)")
        print("   --mode pipeline : 使用完整处理流程")
        print("\n📝 提交信息:")
        print("   --message \"msg\" : 自定义Git提交信息")
        print("\n💡 工作流程:")
        print("   1. 查找匹配的文章文件")
        print("   2. 复制到草稿目录进行编辑")
        print("   3. 根据模式处理内容")
        print("   4. 更新原文章并提交Git")
    
    input("\n按Enter键返回主菜单...")


def handle_youtube_podcast_menu(pipeline):
    """处理YouTube播客生成器菜单 - 委托给CLI模块处理"""
    from scripts.cli.youtube_menu_handler import YouTubeMenuHandler
    
    youtube_handler = YouTubeMenuHandler(pipeline)
    return youtube_handler.handle_youtube_podcast_menu()
def handle_debug_menu(pipeline):
    """处理调试和维护工具菜单"""
    print("\n" + "="*40)
    print("🔧 调试和维护工具")
    print("="*40)
    print("📋 功能说明：")
    print("   • 微信API调试和测试工具")
    print("   • 系统组件验证和故障排查")
    print("   • 开发和维护专用工具")
    print("\n⚠️  注意事项：")
    print("   • 这些工具主要用于开发和调试")
    print("   • 某些功能需要开发者权限")
    print("   • 使用前请确保了解工具功能")
    
    print("\n请选择工具：")
    print("1. 微信API调试工具")
    print("2. 运行项目测试套件")
    print("3. 查看系统日志")
    print("4. 清理临时文件")
    print("0. 返回主菜单")
    
    sub_choice = input("\n请输入选项 (1-4/0): ").strip()
    pipeline.log(f"调试和维护工具 - 用户选择: {sub_choice}", level="info", force=True)
    
    if sub_choice == "1":
        # 微信API调试工具
        print("\n🔧 微信API调试工具")
        print("⚠️  前提条件：")
        print("   • 需要在.env文件中配置WECHAT_APPID和WECHAT_APPSECRET")
        print("   • 需要在微信公众号后台设置IP白名单")
        print("   • 确保账号有相应的API权限")
        
        confirm = input("\n是否继续运行微信API调试？(y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            try:
                script_path = Path("scripts/tools/wechat_api_debug.py")
                print("\n🔄 正在运行微信API调试...")
                result = execute_script_with_logging(
                    pipeline, script_path, [], 
                    "微信API调试"
                )
                print(result.stdout)
                if result.stderr:
                    print(f"❌ 错误: {result.stderr}")
            except Exception as e:
                print(f"❌ 操作失败: {e}")
        else:
            print("已取消操作")
            
    elif sub_choice == "2":
        # 运行项目测试套件
        print("\n🧪 运行项目测试套件")
        print("💡 这将运行所有项目测试，可能需要几分钟时间...")
        
        confirm = input("\n是否继续运行测试？(y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            try:
                test_script = Path("tests/run_tests.py")
                if test_script.exists():
                    print("\n🔄 正在运行测试套件...")
                    result = execute_script_with_logging(
                        pipeline, test_script, [], 
                        "运行项目测试套件"
                    )
                    print(result.stdout)
                    if result.stderr:
                        print(f"❌ 错误: {result.stderr}")
                else:
                    # 直接使用pytest
                    print("\n🔄 使用pytest运行测试...")
                    pipeline.log("开始执行: 使用pytest运行测试 - python -m pytest tests/ -v", level="info", force=True)
                    # 确保 subprocess 可用（解决 Pylance 作用域检测问题）
                    import subprocess
                    result = subprocess.run(
                        [sys.executable, "-m", "pytest", "tests/", "-v"], 
                        capture_output=True, 
                        text=True
                    )
                    if result.returncode == 0:
                        pipeline.log("执行成功: pytest测试", level="info", force=True)
                    else:
                        pipeline.log(f"执行失败: pytest测试 (返回码: {result.returncode})", level="error", force=True)
                    print(result.stdout)
                    if result.stderr:
                        print(f"❌ 错误: {result.stderr}")
            except Exception as e:
                print(f"❌ 操作失败: {e}")
        else:
            print("已取消操作")
            
    elif sub_choice == "3":
        # 查看系统日志
        print("\n📋 系统日志查看")
        log_file = Path(".build/logs/pipeline.log")
        if log_file.exists():
            lines = input("\n请输入要查看的行数 (默认50): ").strip()
            if not lines:
                lines = "50"
            
            try:
                if lines.isdigit():
                    with open(log_file, 'r', encoding='utf-8') as f:
                        all_lines = f.readlines()
                        recent_lines = all_lines[-int(lines):]
                        print(f"\n📄 最近{len(recent_lines)}行日志:")
                        print("-" * 60)
                        for line in recent_lines:
                            print(line.rstrip())
                        print("-" * 60)
                else:
                    print("❌ 请输入有效的行数")
            except Exception as e:
                print(f"❌ 读取日志失败: {e}")
        else:
            print("📋 日志文件不存在")
            
    elif sub_choice == "4":
        # 清理临时文件
        print("\n🧹 清理临时文件")
        print("📋 该操作将清理以下内容:")
        print("   • .tmp/ 临时文件目录")
        print("   • .build/logs/ 中的旧日志文件")
        print("   • Python缓存文件 (__pycache__)")
        print("   • 其他临时生成文件")
        
        confirm = input("\n⚠️  确认清理临时文件？(y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            try:
                cleaned_items = []
                
                # 清理.tmp目录
                tmp_dir = Path(".tmp")
                if tmp_dir.exists():
                    import shutil
                    shutil.rmtree(tmp_dir)
                    cleaned_items.append("临时文件目录 (.tmp)")
                
                # 清理旧日志文件 (保留最新5个)
                logs_dir = Path(".build/logs")
                if logs_dir.exists():
                    log_files = sorted(logs_dir.glob("*.log*"))
                    if len(log_files) > 5:
                        for log_file in log_files[:-5]:
                            log_file.unlink()
                        cleaned_items.append(f"旧日志文件 ({len(log_files)-5}个)")
                
                # 清理Python缓存
                import subprocess
                result = subprocess.run([sys.executable, "-c", 
                    "import os, shutil; [shutil.rmtree(os.path.join(root, '__pycache__')) for root, dirs, files in os.walk('.') if '__pycache__' in dirs]"], 
                    capture_output=True, text=True)
                if result.returncode == 0:
                    cleaned_items.append("Python缓存文件")
                
                if cleaned_items:
                    print("✅ 清理完成！已清理：")
                    for item in cleaned_items:
                        print(f"   • {item}")
                else:
                    print("📋 没有找到需要清理的文件")
                    
            except Exception as e:
                print(f"❌ 清理失败: {e}")
        else:
            print("已取消操作")
    
    input("\n按Enter键返回主菜单...")


def update_env_file(key, value=None):
    """更新.env file中的环境变量
    
    Args:
        key: 环境变量名
        value: 环境变量值，如果为None则删除该变量
    """
    env_file_path = '.env'
    
    try:
        # 读取现有.env文件
        env_lines = []
        if os.path.exists(env_file_path):
            with open(env_file_path, 'r', encoding='utf-8') as f:
                env_lines = f.readlines()
        
        # 查找并更新/删除指定的环境变量
        key_found = False
        updated_lines = []
        
        for line in env_lines:
            line_stripped = line.strip()
            
            # 检查是否是目标key的行（包括注释掉的）
            if (line_stripped.startswith(f'{key}=') or 
                line_stripped.startswith(f'# {key}=') or
                line_stripped.startswith(f'#{key}=')):
                
                key_found = True
                if value is not None:
                    # 启用并设置新值
                    updated_lines.append(f'{key}={value}\n')
                else:
                    # 注释掉该行（保留原值作为备份）
                    if not line_stripped.startswith('#'):
                        updated_lines.append(f'# {line}')
                    else:
                        updated_lines.append(line)  # 已经是注释，保持不变
            else:
                updated_lines.append(line)
        
        # 如果没找到key且value不为None，添加新的环境变量
        if not key_found and value is not None:
            updated_lines.append(f'{key}={value}\n')
        
        # 写回.env文件
        with open(env_file_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        return True
        
    except Exception as e:
        print(f"❌ 更新.env文件失败: {e}")
        return False


def create_export_script(config_type="default"):
    """创建环境变量导出脚本，用于在WSL命令行中设置环境变量
    
    Args:
        config_type: 配置类型 ("default", "qwen", "kimi")
    """
    script_path = Path(".tmp/set_llm_env.sh")
    script_path.parent.mkdir(exist_ok=True)
    
    try:
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write("#!/bin/bash\n")
            f.write("# LLM引擎环境变量设置脚本\n")
            f.write("# 使用方法: source .tmp/set_llm_env.sh\n\n")
            
            if config_type == "qwen":
                f.write("# 设置千问3-code引擎\n")
                f.write("export ANTHROPIC_BASE_URL='https://dashscope.aliyuncs.com/api/v2'\n")
                f.write("export ANTHROPIC_AUTH_TOKEN='YOUR_ANTHROPIC_API_KEY_HERE'\n")
                f.write("unset ANTHROPIC_API_KEY\n")
                f.write("echo '✅ 已设置千问3-code引擎环境变量'\n")
            elif config_type == "kimi":
                f.write("# 设置Kimi K2引擎\n")
                f.write("export ANTHROPIC_BASE_URL='https://api.moonshot.ai/anthropic'\n")
                f.write("export ANTHROPIC_AUTH_TOKEN='YOUR_KIMI_API_KEY_HERE'\n")
                f.write("unset ANTHROPIC_API_KEY\n")
                f.write("echo '✅ 已设置Kimi K2引擎环境变量'\n")
            else:  # default
                f.write("# 恢复Claude Pro默认模式\n")
                f.write("unset ANTHROPIC_BASE_URL\n")
                f.write("unset ANTHROPIC_AUTH_TOKEN\n")
                f.write("unset ANTHROPIC_API_KEY\n")
                f.write("echo '✅ 已恢复Claude Pro默认模式'\n")
            
            f.write("\n# 显示当前配置\n")
            f.write("echo '📊 当前LLM引擎配置:'\n")
            f.write("echo \"ANTHROPIC_BASE_URL: ${ANTHROPIC_BASE_URL:-'未设置 (默认)'}\"\n")
            f.write("echo \"ANTHROPIC_AUTH_TOKEN: ${ANTHROPIC_AUTH_TOKEN:0:8}...${ANTHROPIC_AUTH_TOKEN: -8}\" 2>/dev/null || echo \"ANTHROPIC_AUTH_TOKEN: 未设置\"\n")
            f.write("echo \"ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:0:8}...${ANTHROPIC_API_KEY: -4}\" 2>/dev/null || echo \"ANTHROPIC_API_KEY: 未设置\"\n")
        
        # 设置执行权限
        script_path.chmod(0o755)
        return str(script_path)
        
    except Exception as e:
        print(f"❌ 创建导出脚本失败: {e}")
        return None

def handle_llm_engine_menu(pipeline):
    """处理LLM引擎切换菜单 - 委托给CLI模块处理"""
    from scripts.cli.system_menu_handler import SystemMenuHandler
    
    system_handler = SystemMenuHandler(pipeline)
    return system_handler.handle_llm_engine_menu()


def handle_elevenlabs_menu(pipeline):
    """处理ElevenLabs语音测试菜单"""
    import subprocess
    
    while True:
        print("\n" + "="*50)
        print("🎙️ ElevenLabs语音测试工具")
        print("="*50)
        print("🔧 测试工具：")
        print("1. API权限检查")
        print("2. 声音测试器（完整功能）")
        print("3. 双人对话功能测试")
        print("\n📊 信息查看：")
        print("4. 查看配置状态")
        print("5. 查看测试结果")
        print("\n📖 帮助文档：")
        print("6. 快速开始指南")
        print("7. 功能使用说明")
        print("\n0. 返回主菜单")
        
        choice = input("\n请输入选项 (1-7/0): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            # API权限检查
            print("\n🔍 执行ElevenLabs API权限检查...")
            pipeline.log("执行ElevenLabs API权限检查", level="info", force=True)
            try:
                result = subprocess.run(
                    ["python", "scripts/tools/elevenlabs_permission_check.py"],
                    capture_output=False,
                    text=True
                )
                if result.returncode != 0:
                    print("⚠️ 权限检查执行异常，请检查ElevenLabs配置")
                    pipeline.log(f"ElevenLabs权限检查异常，返回码: {result.returncode}", level="warning", force=True)
            except Exception as e:
                print(f"❌ 执行权限检查失败: {e}")
                pipeline.log(f"ElevenLabs权限检查失败: {e}", level="error", force=True)
                
        elif choice == "2":
            # 声音测试器
            print("\n🎙️ 启动ElevenLabs声音测试器...")
            print("💡 提示: 推荐选择以下测试选项:")
            print("   • 选项2: 获取可用TTS模型")
            print("   • 选项4: 创建双人对话播客测试")
            print("   • 选项7: 完整测试流程")
            print()
            pipeline.log("启动ElevenLabs声音测试器", level="info", force=True)
            try:
                subprocess.run(["python", "scripts/tools/elevenlabs_voice_tester.py"])
            except Exception as e:
                print(f"❌ 启动声音测试器失败: {e}")
                pipeline.log(f"ElevenLabs声音测试器启动失败: {e}", level="error", force=True)
                
        elif choice == "3":
            # 双人对话功能测试
            print("\n🎭 执行双人对话功能测试...")
            pipeline.log("执行ElevenLabs双人对话功能测试", level="info", force=True)
            try:
                result = subprocess.run(
                    ["python", "scripts/tools/test_dual_voice_podcast.py"],
                    capture_output=False,
                    text=True
                )
                if result.returncode == 0:
                    print("\n✅ 双人对话功能测试完成")
                    pipeline.log("ElevenLabs双人对话功能测试成功", level="info", force=True)
                else:
                    print("\n⚠️ 双人对话功能测试异常")
                    pipeline.log(f"ElevenLabs双人对话功能测试异常，返回码: {result.returncode}", level="warning", force=True)
            except Exception as e:
                print(f"❌ 执行双人对话测试失败: {e}")
                pipeline.log(f"ElevenLabs双人对话测试失败: {e}", level="error", force=True)
                
        elif choice == "4":
            # 查看配置状态
            print("\n📊 ElevenLabs配置状态")
            print("="*40)
            
            # 检查环境变量
            elevenlabs_key = os.getenv('ELEVENLABS_API_KEY', '')
            print(f"🔑 API密钥: {'✅ 已配置 (' + elevenlabs_key[:10] + '...)' if elevenlabs_key else '❌ 未配置'}")
            
            # 检查配置文件
            config_file = Path("config/elevenlabs_voices.yml")
            template_file = Path("config/elevenlabs_voices_template.yml")
            
            print(f"📄 配置文件: {'✅ 存在' if config_file.exists() else '❌ 不存在'}")
            print(f"📄 模板文件: {'✅ 存在' if template_file.exists() else '❌ 不存在'}")
            
            # 检查测试结果目录
            test_dir = Path("tests/elevenlabs_voice_tests")
            print(f"📁 测试目录: {'✅ 存在' if test_dir.exists() else '❌ 不存在'}")
            
            if test_dir.exists():
                test_files = list(test_dir.glob("*"))
                print(f"📊 测试文件: {len(test_files)} 个")
                
            # 检查依赖库
            print("\n📦 依赖库状态:")
            try:
                import elevenlabs
                print("✅ elevenlabs: 已安装")
            except ImportError:
                print("❌ elevenlabs: 未安装")
                
            try:
                import pydub
                print("✅ pydub: 已安装 (音频合并支持)")
            except ImportError:
                print("❌ pydub: 未安装 (影响双人对话功能)")
                
            try:
                import yaml
                print("✅ PyYAML: 已安装 (配置文件支持)")
            except ImportError:
                print("❌ PyYAML: 未安装 (将使用默认配置)")
                
        elif choice == "5":
            # 查看测试结果
            print("\n📊 ElevenLabs测试结果")
            print("="*40)
            
            test_dir = Path("tests/elevenlabs_voice_tests")
            if not test_dir.exists():
                print("❌ 测试目录不存在，请先运行测试")
            else:
                test_files = list(test_dir.glob("*"))
                if not test_files:
                    print("📝 测试目录为空，请先运行测试")
                else:
                    print(f"📁 测试目录: {test_dir}")
                    print(f"📊 文件总数: {len(test_files)}")
                    print("\n📄 测试文件列表:")
                    
                    for file in sorted(test_files):
                        if file.is_file():
                            size = file.stat().st_size
                            if size > 1024:
                                size_str = f"{size/1024:.1f}KB"
                            else:
                                size_str = f"{size}B"
                            print(f"   • {file.name} ({size_str})")
                        else:
                            print(f"   📁 {file.name}/")
            
            # 检查主要测试音频文件
            main_test_files = [
                "tests/dual_voice_test.wav",
                "tests/single_voice_test.wav"
            ]
            
            print("\n🎧 主要测试音频:")
            for test_file in main_test_files:
                file_path = Path(test_file)
                if file_path.exists():
                    size = file_path.stat().st_size
                    size_str = f"{size/1024:.1f}KB" if size > 1024 else f"{size}B"
                    print(f"   ✅ {file_path.name} ({size_str})")
                else:
                    print(f"   ❌ {file_path.name} (不存在)")
                    
        elif choice == "6":
            # 快速开始指南
            print("\n📖 显示快速开始指南...")
            guide_file = Path("ELEVENLABS_QUICKSTART.md")
            if guide_file.exists():
                try:
                    with open(guide_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print("\n" + "="*60)
                    print(content)
                    print("="*60)
                except Exception as e:
                    print(f"❌ 读取指南失败: {e}")
            else:
                print("❌ 快速开始指南文件不存在")
                
        elif choice == "7":
            # 功能使用说明
            print("\n📖 显示功能使用说明...")
            status_file = Path("ELEVENLABS_STATUS.md")
            if status_file.exists():
                try:
                    with open(status_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print("\n" + "="*60)
                    print(content)
                    print("="*60)
                except Exception as e:
                    print(f"❌ 读取说明失败: {e}")
            else:
                print("❌ 功能使用说明文件不存在")
        else:
            print("❌ 无效的选择，请重新输入")
        
        if choice in ["6", "7"]:
            input("\n按Enter键继续...")


def handle_youtube_upload_menu(pipeline):
    """处理YouTube音频上传菜单 - 委托给CLI模块处理"""
    from scripts.cli.youtube_menu_handler import YouTubeMenuHandler
    
    youtube_handler = YouTubeMenuHandler(pipeline)
    return youtube_handler._handle_audio_upload()


def handle_generate_access_code(pipeline):
    """生成测试访问码"""
    print("\n" + "="*40)
    print("🔑 生成测试访问码")
    print("="*40)
    
    # 导入安全会员管理器
    try:
        from scripts.secure_member_manager import SecureMemberManager
        manager = SecureMemberManager()
    except ImportError:
        print("❌ 无法导入安全会员管理器，回退到普通管理器")
        from scripts.member_management import MemberManager
        manager = MemberManager()
    
    print("请选择会员等级:")
    print("1. 体验会员 (VIP1) - 7天有效期")
    print("2. 月度会员 (VIP2) - 30天有效期")
    print("3. 季度会员 (VIP3) - 90天有效期")
    print("4. 年度会员 (VIP4) - 365天有效期")
    print("5. 管理员码 (ADMIN) - 自定义有效期")
    print("0. 返回")
    
    choice = input("\n请输入选项 (1-5/0): ").strip()
    
    if choice == "0":
        return
    
    level_map = {
        '1': 'experience',
        '2': 'monthly', 
        '3': 'quarterly',
        '4': 'yearly'
    }
    
    if choice in level_map:
        level = level_map[choice]
        try:
            if hasattr(manager, 'generate_secure_access_code'):
                access_code = manager.generate_secure_access_code(level)
            else:
                access_code = manager.generate_access_code(level)
            
            print(f"\n✅ 生成的访问码: {access_code}")
            print(f"📋 会员等级: {manager.member_levels[level]['name']}")
            print(f"⏰ 有效期: {manager.member_levels[level]['days']}天")
            
            # 询问是否发送邮件
            email = input("\n📧 是否发送邮件？请输入邮箱地址（回车跳过）: ").strip()
            if email:
                success = manager.send_access_code_email(email, access_code, level)
                if success:
                    print("✅ 邮件发送成功")
                else:
                    print("❌ 邮件发送失败")
            
        except Exception as e:
            print(f"❌ 生成访问码失败: {e}")
    
    elif choice == "5":
        # 管理员码
        print("\n🔧 生成管理员访问码")
        days = input("请输入有效期天数 (默认30): ").strip()
        try:
            days = int(days) if days else 30
            from datetime import datetime, timedelta
            expiry_date = datetime.now() + timedelta(days=days)
            expiry_str = expiry_date.strftime('%Y%m%d')
            
            import random, string
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            admin_code = f"ADMIN_{expiry_str}_{random_part}"
            
            print(f"\n✅ 生成的管理员访问码: {admin_code}")
            print(f"⏰ 有效期: {days}天 (至 {expiry_date.strftime('%Y-%m-%d')})")
            print("🔧 管理员码具有最高权限，请妥善保管")
            
        except ValueError:
            print("❌ 无效的天数")
    else:
        print("❌ 无效的选择")


def handle_validate_access_code(pipeline):
    """验证访问码"""
    print("\n" + "="*40)
    print("🔍 验证访问码")
    print("="*40)
    
    code = input("请输入要验证的访问码: ").strip()
    if not code:
        print("❌ 访问码不能为空")
        return
    
    try:
        from scripts.secure_member_manager import SecureMemberManager
        manager = SecureMemberManager()
        
        # 使用安全验证
        if hasattr(manager, 'validate_secure_access_code'):
            result = manager.validate_secure_access_code(code)
        else:
            result = manager.validate_access_code(code)
        
        print("\n📋 验证结果:")
        if result['valid']:
            print("✅ 访问码有效")
            print(f"📊 会员等级: {result.get('level_name', result.get('level'))}")
            if 'expiry_date' in result:
                if hasattr(result['expiry_date'], 'strftime'):
                    print(f"⏰ 过期日期: {result['expiry_date'].strftime('%Y-%m-%d')}")
                else:
                    print(f"⏰ 过期日期: {result['expiry_date']}")
            if 'days_remaining' in result:
                print(f"📅 剩余天数: {result['days_remaining']}天")
            if result.get('security_check'):
                print(f"🔒 安全检查: {result['security_check']}")
        else:
            print("❌ 访问码无效")
            print(f"📋 原因: {result.get('reason', '未知原因')}")
            
    except ImportError:
        print("❌ 无法导入安全会员管理器，使用普通验证")
        try:
            from scripts.member_management import MemberManager
            manager = MemberManager()
            result = manager.validate_access_code(code)
            
            if result['valid']:
                print("✅ 基础格式验证通过")
                print(f"📊 会员等级: {result.get('level_name')}")
                print("⚠️  注意: 未进行安全验证，建议升级到安全管理器")
            else:
                print("❌ 访问码格式无效")
        except Exception as e:
            print(f"❌ 验证失败: {e}")
    except Exception as e:
        print(f"❌ 验证过程出错: {e}")


def handle_member_stats(pipeline):
    """查看会员系统统计"""
    print("\n" + "="*40)
    print("📊 会员系统统计")
    print("="*40)
    
    try:
        from scripts.secure_member_manager import SecureMemberManager
        manager = SecureMemberManager()
        
        # 获取基础统计
        basic_stats = manager.get_stats()
        print("📋 基础统计:")
        print(f"   • 总注册数: {basic_stats['total_registrations']}")
        print(f"   • 待处理注册: {basic_stats['pending_registrations']}")
        print(f"   • 已处理注册: {basic_stats['processed_registrations']}")
        print(f"   • 总收入: ¥{basic_stats['total_revenue']}")
        
        # 获取白名单统计
        if hasattr(manager, 'get_whitelist_stats'):
            whitelist_stats = manager.get_whitelist_stats()
            print("\n🔒 安全白名单统计:")
            print(f"   • 总访问码: {whitelist_stats['total_codes']}")
            print(f"   • 活跃访问码: {whitelist_stats['active_codes']}")
            print(f"   • 已撤销: {whitelist_stats['revoked_codes']}")
            print(f"   • 已过期: {whitelist_stats['expired_codes']}")
            
            if whitelist_stats['level_distribution']:
                print("\n📈 等级分布:")
                for level, count in whitelist_stats['level_distribution'].items():
                    level_name = manager.member_levels.get(level, {}).get('name', level)
                    print(f"   • {level_name}: {count}个")
        
        # 显示活跃访问码
        if hasattr(manager, 'list_active_codes'):
            active_codes = manager.list_active_codes()
            if active_codes:
                print(f"\n🔑 活跃访问码 ({len(active_codes)}个):")
                for code_info in active_codes[:10]:  # 显示前10个
                    level_name = manager.member_levels.get(code_info['level'], {}).get('name', code_info['level'])
                    print(f"   • {code_info['code'][:15]}... | {level_name} | 剩余{code_info.get('days_remaining', 0)}天")
                if len(active_codes) > 10:
                    print(f"   ... 还有 {len(active_codes) - 10} 个访问码")
            else:
                print("\n🔑 当前没有活跃的访问码")
                
    except ImportError:
        print("❌ 无法导入安全会员管理器，使用基础统计")
        try:
            from scripts.member_management import MemberManager
            manager = MemberManager()
            stats = manager.get_stats()
            
            print("📋 基础统计:")
            print(f"   • 总注册数: {stats['total_registrations']}")
            print(f"   • 待处理注册: {stats['pending_registrations']}")
            print(f"   • 已处理注册: {stats['processed_registrations']}")
            print(f"   • 总收入: ¥{stats['total_revenue']}")
            
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
    except Exception as e:
        print(f"❌ 统计过程出错: {e}")


def handle_process_registrations(pipeline):
    """处理待处理注册"""
    print("\n" + "="*40)
    print("📝 处理待处理注册")
    print("="*40)
    
    try:
        from scripts.member_management import MemberManager
        manager = MemberManager()
        
        pending = manager.get_pending_registrations()
        if not pending:
            print("📋 当前没有待处理的注册")
            return
        
        print(f"📋 发现 {len(pending)} 个待处理注册:")
        for i, reg in enumerate(pending[:5], 1):  # 显示前5个
            print(f"   {i}. {reg['email']} | {reg['memberLevel']} | ¥{reg['paymentAmount']}")
        
        if len(pending) > 5:
            print(f"   ... 还有 {len(pending) - 5} 个注册")
        
        print("\n处理选项:")
        print("1. 批量处理所有注册（生成访问码并发送邮件）")
        print("2. 批量处理但不发送邮件")
        print("0. 返回")
        
        choice = input("\n请选择 (1-2/0): ").strip()
        
        if choice == "1":
            print("\n🔄 开始批量处理并发送邮件...")
            manager.batch_process_registrations(send_email=True)
            print("✅ 批量处理完成")
        elif choice == "2":
            print("\n🔄 开始批量处理（不发送邮件）...")
            manager.batch_process_registrations(send_email=False)
            print("✅ 批量处理完成")
            
    except Exception as e:
        print(f"❌ 处理注册失败: {e}")


def handle_export_member_data(pipeline):
    """导出会员数据"""
    print("\n" + "="*40)
    print("📤 导出会员数据")
    print("="*40)
    
    try:
        from scripts.member_management import MemberManager
        manager = MemberManager()
        
        print("🔄 正在导出会员数据...")
        filepath = manager.export_registrations_csv()
        
        if filepath:
            print(f"✅ 数据导出成功: {filepath}")
            
            # 显示文件大小
            from pathlib import Path
            file_path = Path(filepath)
            if file_path.exists():
                file_size = file_path.stat().st_size
                print(f"📋 文件大小: {file_size:,} 字节")
                
                # 询问是否查看文件内容摘要
                view = input("\n是否查看导出数据摘要？(y/N): ").strip().lower()
                if view in ['y', 'yes']:
                    try:
                        import csv
                        with open(filepath, 'r', encoding='utf-8') as f:
                            reader = csv.DictReader(f)
                            rows = list(reader)
                            
                        print(f"\n📊 导出数据摘要:")
                        print(f"   • 总记录数: {len(rows)}")
                        if rows:
                            print("   • 字段:")
                            for field in rows[0].keys():
                                print(f"     - {field}")
                    except Exception as e:
                        print(f"❌ 读取文件摘要失败: {e}")
        else:
            print("❌ 导出失败")
            
    except Exception as e:
        print(f"❌ 导出过程出错: {e}")


def handle_onedrive_images_menu(pipeline):
    """OneDrive图床管理菜单"""
    while True:
        print("\n" + "="*50)
        print("📁 OneDrive图床管理")
        print("="*50)
        print("1. 初始化OneDrive认证")
        print("2. 处理单个草稿的图片")
        print("3. 批量处理所有草稿图片")
        print("4. 检查OneDrive连接状态")
        print("5. 查看图片处理统计")
        print("6. 图片索引管理")
        print("7. 🆕 混合图片管理（支持任意位置）")
        print("8. 🧹 管理处理会话")
        print("9. 🗑️ OneDrive云端清理工具")
        print("10. 📅 按日期下载图片备份")
        print("\n0. 返回主菜单")
        
        choice = input("\n请选择操作 (1-10/0): ").strip()
        
        if choice == "1":
            # 初始化认证
            print("🔐 启动OneDrive认证...")
            try:
                result = subprocess.run([
                    "python3", "scripts/tools/onedrive_blog_images.py", 
                    "--setup"
                ], check=False, capture_output=False)
                
                if result.returncode == 0:
                    print("✅ 认证设置完成")
                else:
                    print("❌ 认证设置失败")
                    
            except Exception as e:
                print(f"❌ 认证过程出错: {e}")
                
        elif choice == "2":
            # 处理单个草稿
            print("📝 选择要处理的草稿文件...")
            
            # 显示草稿列表
            drafts_dir = Path("_drafts")
            if not drafts_dir.exists():
                print("❌ 草稿目录不存在")
                continue
                
            draft_files = list(drafts_dir.glob("*.md"))
            if not draft_files:
                print("❌ 没有找到草稿文件")
                continue
                
            print("\n可用的草稿文件:")
            for i, draft in enumerate(draft_files, 1):
                print(f"{i}. {draft.name}")
                
            try:
                file_choice = input(f"\n请选择文件 (1-{len(draft_files)}/0取消): ").strip()
                if file_choice == "0":
                    continue
                    
                file_index = int(file_choice) - 1
                if 0 <= file_index < len(draft_files):
                    selected_draft = draft_files[file_index]
                    print(f"📝 处理草稿: {selected_draft.name}")
                    
                    # 使用统一的OneDrive图片处理接口
                    result = pipeline.process_onedrive_images(selected_draft)
                    
                    if result['success']:
                        print(f"✅ 图片处理完成，处理了 {result['processed_images']} 张图片")
                        if result['issues']:
                            print("⚠️ 仍有部分图片问题需要手动处理:")
                            for issue in result['issues'][:3]:  # 显示前3个问题
                                print(f"   • {issue}")
                    else:
                        print(f"❌ 图片处理失败: {result['error']}")
                else:
                    print("❌ 无效的文件选择")
                    
            except (ValueError, IndexError):
                print("❌ 无效的输入")
                
        elif choice == "3":
            # 批量处理
            print("📁 批量处理所有草稿图片...")
            
            try:
                drafts_dir = Path("_drafts")
                if not drafts_dir.exists():
                    print("❌ 草稿目录不存在")
                    continue
                
                draft_files = list(drafts_dir.glob("*.md"))
                if not draft_files:
                    print("❌ 没有找到草稿文件")
                    continue
                
                total_processed = 0
                successful_files = 0
                
                for draft_file in draft_files:
                    print(f"📝 处理: {draft_file.name}")
                    result = pipeline.process_onedrive_images(draft_file)
                    
                    if result['success']:
                        successful_files += 1
                        total_processed += result['processed_images']
                        if result['processed_images'] > 0:
                            print(f"   ✅ 处理了 {result['processed_images']} 张图片")
                        else:
                            print(f"   ✅ 无需图片处理")
                    else:
                        print(f"   ❌ 失败: {result['error']}")
                
                print(f"\n📊 批量处理完成:")
                print(f"   • 处理文件: {successful_files}/{len(draft_files)}")
                print(f"   • 处理图片: {total_processed} 张")
                    
            except Exception as e:
                print(f"❌ 批量处理出错: {e}")
                
        elif choice == "4":
            # 检查连接状态
            print("🔍 检查OneDrive连接状态...")
            
            try:
                # 尝试导入并测试连接
                import importlib.util
                
                # 动态导入OneDrive模块
                spec = importlib.util.spec_from_file_location(
                    "onedrive_blog_images",  # type: ignore 
                    "scripts/tools/onedrive_blog_images.py"
                )
                if spec and spec.loader:
                    onedrive_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(onedrive_module)
                    BlogImageManager = onedrive_module.BlogImageManager
                else:
                    print("❌ OneDrive模块导入失败")
                    continue
                
                manager = BlogImageManager()
                
                # 测试API连接
                response = manager.uploader._make_request('GET', '/me/drive')
                if response.status_code == 200:
                    drive_info = response.json()
                    total_gb = drive_info['quota']['total'] / (1024**3)
                    used_gb = drive_info['quota']['used'] / (1024**3)
                    free_gb = total_gb - used_gb
                    
                    print("✅ OneDrive连接正常")
                    print(f"📊 存储使用情况:")
                    print(f"   总容量: {total_gb:.1f}GB")
                    print(f"   已使用: {used_gb:.1f}GB")
                    print(f"   可用空间: {free_gb:.1f}GB")
                    print(f"   使用率: {(used_gb/total_gb)*100:.1f}%")
                else:
                    print(f"❌ OneDrive连接失败: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ 连接测试失败: {e}")
                print("💡 提示: 请先运行初始化认证")
                
        elif choice == "5":
            # 查看处理统计
            print("📊 图片处理统计...")
            
            # 检查日志文件
            log_file = Path(".build/logs/onedrive_blog_images.log")
            if log_file.exists():
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                    # 简单统计
                    upload_success = len([l for l in lines if 'Successfully uploaded' in l])
                    upload_fail = len([l for l in lines if 'Failed to process image' in l])
                    
                    print(f"📈 处理统计:")
                    print(f"   成功上传: {upload_success} 张图片")
                    print(f"   失败处理: {upload_fail} 张图片")
                    
                    # 显示最近几条日志
                    print(f"\n📋 最近日志 (最后10条):")
                    for line in lines[-10:]:
                        if any(keyword in line for keyword in ['Successfully uploaded', 'Failed to process', 'ERROR']):
                            print(f"   {line.strip()}")
                            
                except Exception as e:
                    print(f"❌ 读取日志失败: {e}")
            else:
                print("📝 暂无处理日志")
                
        elif choice == "6":
            # 图片索引管理
            handle_image_index_menu()
            
        elif choice == "7":
            # 混合图片管理（支持任意位置）
            print("🚀 启动混合图片管理系统...")
            handle_mixed_image_management_menu()
            
        elif choice == "8":
            # 管理处理会话
            print("🧹 管理图片处理会话...")
            handle_processing_sessions_menu()
            
        elif choice == "9":
            # OneDrive云端清理工具
            print("🗑️ 启动OneDrive云端清理工具...")
            handle_onedrive_cleanup_menu()
            
        elif choice == "10":
            # 按日期下载图片备份
            print("📅 启动按日期下载图片备份工具...")
            handle_onedrive_date_download_menu(pipeline)
            
        elif choice == "0":
            break
        else:
            print("❌ 无效选择，请重新输入")


def handle_image_index_menu():
    """图片索引管理菜单"""
    while True:
        print("\n" + "="*50)
        print("🗂️ 图片索引管理")
        print("="*50)
        print("1. 查看图片统计")
        print("2. 生成详细报告")
        print("3. 按文章查看图片")
        print("4. 按日期查看图片")
        print("5. 清理无效记录")
        print("\n0. 返回上级菜单")
        
        choice = input("\n请选择操作 (1-5/0): ").strip()
        
        if choice == "1":
            # 查看统计
            print("📊 正在获取图片统计...")
            try:
                result = subprocess.run([
                    "python3", "scripts/tools/onedrive_image_index.py", 
                    "--stats"
                ], check=False, capture_output=False)
                
                if result.returncode != 0:
                    print("⚠️ 获取统计信息时出现问题")
                    
            except Exception as e:
                print(f"❌ 统计获取失败: {e}")
                
        elif choice == "2":
            # 生成报告
            print("📄 正在生成详细报告...")
            try:
                result = subprocess.run([
                    "python3", "scripts/tools/onedrive_image_index.py", 
                    "--report"
                ], check=False, capture_output=False)
                
                if result.returncode != 0:
                    print("⚠️ 生成报告时出现问题")
                    
            except Exception as e:
                print(f"❌ 报告生成失败: {e}")
                
        elif choice == "3":
            # 按文章查看
            article = input("请输入文章文件名（不含扩展名）: ").strip()
            if article:
                print(f"🔍 查找文章 {article} 的图片...")
                try:
                    result = subprocess.run([
                        "python3", "scripts/tools/onedrive_image_index.py", 
                        "--article", article
                    ], check=False, capture_output=False)
                    
                    if result.returncode != 0:
                        print("⚠️ 查询过程中出现问题")
                        
                except Exception as e:
                    print(f"❌ 查询失败: {e}")
            else:
                print("❌ 请输入有效的文章名")
                
        elif choice == "4":
            # 按日期查看
            print("请输入日期范围 (格式: YYYY-MM-DD)")
            start_date = input("开始日期: ").strip()
            end_date = input("结束日期: ").strip()
            
            if start_date and end_date:
                print(f"🗓️ 查找 {start_date} 至 {end_date} 的图片...")
                try:
                    result = subprocess.run([
                        "python3", "scripts/tools/onedrive_image_index.py", 
                        "--date-range", start_date, end_date
                    ], check=False, capture_output=False)
                    
                    if result.returncode != 0:
                        print("⚠️ 查询过程中出现问题")
                        
                except Exception as e:
                    print(f"❌ 查询失败: {e}")
            else:
                print("❌ 请输入有效的日期范围")
                
        elif choice == "5":
            # 清理无效记录
            print("🧹 正在清理无效记录...")
            confirm = input("确认清理无效记录？(y/N): ").strip().lower()
            
            if confirm == 'y':
                try:
                    result = subprocess.run([
                        "python3", "scripts/tools/onedrive_image_index.py", 
                        "--cleanup"
                    ], check=False, capture_output=False)
                    
                    if result.returncode == 0:
                        print("✅ 清理完成")
                    else:
                        print("⚠️ 清理过程中出现问题")
                        
                except Exception as e:
                    print(f"❌ 清理失败: {e}")
            else:
                print("❌ 已取消清理操作")
                
        elif choice == "0":
            break
        else:
            print("❌ 无效选择，请重新输入")


def handle_mixed_image_management_menu():
    """混合图片管理菜单"""
    while True:
        print("\n" + "="*50)
        print("🚀 混合图片管理系统")
        print("="*50)
        print("✨ 支持任意位置图片发现和四阶段处理流程")
        print()
        print("1. 处理单个文章图片")
        print("2. 试运行模式（预览不修改）")
        print("3. 查看处理历史")
        print("4. 帮助和说明")
        print("\n0. 返回上级菜单")
        
        choice = input("\n请选择操作 (1-4/0): ").strip()
        
        if choice == "1":
            # 处理单个文章图片
            print("📝 选择要处理的文章...")
            
            # 显示草稿和文章列表
            draft_files = []
            post_files = []
            
            drafts_dir = Path("_drafts")
            if drafts_dir.exists():
                draft_files = list(drafts_dir.glob("*.md"))
            
            posts_dir = Path("_posts")
            if posts_dir.exists():
                post_files = list(posts_dir.glob("*.md"))
            
            all_files = draft_files + post_files
            if not all_files:
                print("❌ 没有找到文章文件")
                continue
            
            print("\n可用的文章文件:")
            for i, file_path in enumerate(all_files, 1):
                file_type = "草稿" if file_path.parent.name == "_drafts" else "文章"
                print(f"{i}. [{file_type}] {file_path.name}")
            
            try:
                file_choice = input(f"\n请选择文件 (1-{len(all_files)}/0取消): ").strip()
                if file_choice == "0":
                    continue
                
                file_index = int(file_choice) - 1
                if 0 <= file_index < len(all_files):
                    selected_file = all_files[file_index]
                    print(f"🔄 处理文章: {selected_file.name}")
                    
                    try:
                        result = subprocess.run([
                            "python3", "scripts/tools/mixed_image_manager.py",
                            str(selected_file)
                        ], check=False)
                        
                        if result.returncode == 0:
                            print("✅ 混合图片处理完成")
                        else:
                            print("❌ 处理过程中出现问题")
                    except Exception as e:
                        print(f"❌ 处理出错: {e}")
                else:
                    print("❌ 无效的文件选择")
            except (ValueError, IndexError):
                print("❌ 无效的输入")
        
        elif choice == "2":
            # 试运行模式
            print("🔍 试运行模式 - 预览处理过程但不修改文件")
            
            # 文件选择逻辑与选项1相同，但加上--dry-run参数
            draft_files = []
            post_files = []
            
            drafts_dir = Path("_drafts")
            if drafts_dir.exists():
                draft_files = list(drafts_dir.glob("*.md"))
            
            posts_dir = Path("_posts")
            if posts_dir.exists():
                post_files = list(posts_dir.glob("*.md"))
            
            all_files = draft_files + post_files
            if not all_files:
                print("❌ 没有找到文章文件")
                continue
            
            print("\n可用的文章文件:")
            for i, file_path in enumerate(all_files, 1):
                file_type = "草稿" if file_path.parent.name == "_drafts" else "文章"
                print(f"{i}. [{file_type}] {file_path.name}")
            
            try:
                file_choice = input(f"\n请选择文件 (1-{len(all_files)}/0取消): ").strip()
                if file_choice == "0":
                    continue
                
                file_index = int(file_choice) - 1
                if 0 <= file_index < len(all_files):
                    selected_file = all_files[file_index]
                    print(f"🔍 试运行处理: {selected_file.name}")
                    
                    try:
                        result = subprocess.run([
                            "python3", "scripts/tools/mixed_image_manager.py",
                            str(selected_file), "--dry-run"
                        ], check=False)
                        
                        if result.returncode == 0:
                            print("✅ 试运行完成")
                        else:
                            print("❌ 试运行过程中出现问题")
                    except Exception as e:
                        print(f"❌ 试运行出错: {e}")
                else:
                    print("❌ 无效的文件选择")
            except (ValueError, IndexError):
                print("❌ 无效的输入")
        
        elif choice == "3":
            # 查看处理历史
            print("📋 查看混合图片处理历史...")
            
            try:
                result = subprocess.run([
                    "python3", "scripts/tools/mixed_image_manager.py",
                    "--list-sessions"
                ], check=False)
            except Exception as e:
                print(f"❌ 查看历史出错: {e}")
        
        elif choice == "4":
            # 帮助和说明
            print("\n" + "="*60)
            print("📖 混合图片管理系统说明")
            print("="*60)
            print()
            print("🎯 核心特性:")
            print("  • 智能路径解析: 支持绝对路径、相对路径、任意临时目录")
            print("  • 四阶段管理: 临时创作 → 项目缓存 → 云端归档 → 安全清理")
            print("  • 完整备份机制: 处理前自动备份，支持失败回滚")
            print("  • 安全清理策略: 用户确认后才删除本地备份")
            print()
            print("🔄 处理流程:")
            print("  1. 发现图片: 在文章中找到本地图片引用")
            print("  2. 智能解析: 解析各种路径格式，包括临时目录中的图片")
            print("  3. 项目缓存: 将图片复制到 assets/images/processing/pending/")
            print("  4. 云端上传: 上传到OneDrive并获取直接链接")
            print("  5. 更新链接: 替换文章中的图片链接")
            print("  6. 等待确认: 移动到 uploaded/ 目录等待用户确认清理")
            print()
            print("⚠️  注意事项:")
            print("  • 首次使用需要先完成OneDrive认证")
            print("  • 建议先使用试运行模式预览处理结果")
            print("  • 处理完成后建议及时确认清理以释放存储空间")
            print("  • 支持从 Desktop、Downloads 等常见临时目录自动发现图片")
            print()
            input("按回车键返回...")
        
        elif choice == "0":
            break
        else:
            print("❌ 无效选择，请重新输入")


def handle_processing_sessions_menu():
    """处理会话管理菜单"""
    while True:
        print("\n" + "="*50)
        print("🧹 图片处理会话管理")
        print("="*50)
        print("📦 管理混合图片处理的中间状态和备份")
        print()
        print("1. 查看等待清理的会话")
        print("2. 确认清理指定会话")
        print("3. 查看失败的处理会话")
        print("4. 清理所有过期会话")
        print("\n0. 返回上级菜单")
        
        choice = input("\n请选择操作 (1-4/0): ").strip()
        
        if choice == "1":
            # 查看等待清理的会话
            print("📋 查看等待清理的会话...")
            
            try:
                result = subprocess.run([
                    "python3", "scripts/tools/mixed_image_manager.py",
                    "--list-sessions"
                ], check=False)
            except Exception as e:
                print(f"❌ 查看会话出错: {e}")
        
        elif choice == "2":
            # 确认清理指定会话
            print("🗑️ 确认清理指定会话...")
            
            session_id = input("请输入会话ID (或按回车取消): ").strip()
            if not session_id:
                continue
            
            try:
                result = subprocess.run([
                    "python3", "scripts/tools/mixed_image_manager.py",
                    "--confirm-cleanup", session_id
                ], check=False)
            except Exception as e:
                print(f"❌ 清理会话出错: {e}")
        
        elif choice == "3":
            # 查看失败的处理会话
            print("❌ 查看失败的处理会话...")
            
            failed_dir = Path("assets/images/processing/failed")
            if not failed_dir.exists():
                print("📭 没有失败的处理会话")
                continue
            
            failed_sessions = list(failed_dir.iterdir())
            if not failed_sessions:
                print("📭 没有失败的处理会话")
                continue
            
            print(f"\n发现 {len(failed_sessions)} 个失败的会话:")
            for session_dir in failed_sessions:
                if session_dir.is_dir():
                    print(f"  📁 {session_dir.name}")
                    error_file = session_dir / "error.txt"
                    if error_file.exists():
                        try:
                            error_content = error_file.read_text(encoding='utf-8')
                            print(f"     错误: {error_content.split('Error: ')[1].split('\\n')[0] if 'Error: ' in error_content else '未知错误'}")
                        except:
                            print("     错误: 读取错误信息失败")
                    print()
        
        elif choice == "4":
            # 清理所有过期会话
            print("🧹 清理所有过期会话...")
            print("⚠️  这将删除超过配置时间的所有处理会话！")
            
            confirm = input("请输入 'YES' 确认清理过期会话: ").strip()
            if confirm == "YES":
                try:
                    # 这里需要实现过期会话清理逻辑
                    print("🔄 清理过期会话功能开发中...")
                    print("💡 提示: 当前可手动删除 assets/images/processing/ 下的过期目录")
                except Exception as e:
                    print(f"❌ 清理过期会话出错: {e}")
            else:
                print("❌ 清理已取消")
        
        elif choice == "0":
            break
        else:
            print("❌ 无效选择，请重新输入")


# ========== 新增整合菜单处理函数 ==========

def handle_smart_publishing_menu(pipeline):
    """智能内容发布菜单 (合并原功能1+2)"""
    print("\n" + "="*50)
    print("📤 智能内容发布")
    print("="*50)
    print("🎯 统一发布入口，支持新草稿和重新发布")
    
    print("\n请选择发布类型：")
    print("1. 发布新草稿")
    print("2. 重新发布已发布文章") 
    print("3. 查看发布历史")
    print("0. 返回主菜单")
    
    choice = input("\n请选择 (1-3/0): ").strip()
    
    if choice == "1":
        # 发布新草稿 (原功能1)
        pipeline.log("智能发布：开始发布新草稿", level="info", force=True)
        draft = pipeline.select_draft()
        if not draft:
            pipeline.log("用户取消或无草稿可处理", level="info", force=True)
            return None
        elif isinstance(draft, str) and draft.startswith('redirect_to_'):
            # 处理重定向
            if draft == 'redirect_to_inspiration':
                handle_topic_inspiration_menu(pipeline)
                return None
            elif draft == 'redirect_to_youtube':
                handle_youtube_podcast_menu(pipeline)
                return None  
            elif draft == 'redirect_to_normalization':
                handle_content_normalization_menu(pipeline)
                return None
            else:
                return None
        return draft
        
    elif choice == "2":
        # 重新发布已发布文章 (原功能2)
        pipeline.log("智能发布：开始重新发布已发布文章", level="info", force=True)
        post = pipeline.select_published_post()
        if not post:
            pipeline.log("用户取消或无文章可重新发布", level="info", force=True)
            return None
        draft = pipeline.copy_post_to_draft(post)
        if not draft:
            print("复制文章到草稿失败")
            pipeline.log("复制文章到草稿失败", level="error", force=True)
            return None
        return draft
        
    elif choice == "3":
        # 查看发布历史
        print("\n📋 发布历史功能开发中...")
        # TODO: 实现发布历史查看功能
        return None
        
    elif choice == "0":
        return None
    else:
        print("❌ 无效选择，请重新输入")
        return handle_smart_publishing_menu(pipeline)


def handle_smart_creation_menu(pipeline):
    """智能内容创作菜单 (合并原功能5+3)"""
    print("\n" + "="*50)
    print("🎯 智能内容创作")
    print("="*50)
    print("🤖 AI驱动的内容创作和灵感生成")
    
    print("\n请选择创作类型：")
    print("1. AI主题生成")
    print("2. 快速测试文章") 
    print("3. 内容大纲创建")
    print("4. 创作辅助工具")
    print("5. 📊 VIP多层内容创作")  # 新增VIP内容创作
    print("0. 返回主菜单")
    
    choice = input("\n请选择 (1-5/0): ").strip()
    
    if choice == "1":
        # AI主题生成 (原主题灵感生成器)
        handle_topic_inspiration_menu(pipeline)
        return None
        
    elif choice == "2":
        # 快速测试文章 (原生成测试文章)
        pipeline.log("智能创作：开始生成测试文章", level="info", force=True)
        draft = pipeline.generate_test_content()
        if not draft:
            print("生成测试文章失败")
            pipeline.log("生成测试文章失败", level="error", force=True)
            return None
        
        # 测试文章生成成功后，询问是否要发布
        print(f"\n✅ 测试文章已生成: {draft}")
        publish_choice = input("\n是否要发布此测试文章？(y/N): ").strip().lower()
        pipeline.log(f"测试文章生成成功: {draft}, 用户选择{'发布' if publish_choice in ['y', 'yes'] else '不发布'}", level="info", force=True)
        if publish_choice not in ['y', 'yes']:
            print("📄 测试文章已保存到草稿目录，您可以稍后通过'智能内容发布'来发布它")
            return None
        return draft
        
    elif choice == "3":
        # 内容大纲创建
        print("\n📝 内容大纲创建功能开发中...")
        # TODO: 实现内容大纲创建功能
        return None
        
    elif choice == "4":
        # 创作辅助工具
        print("\n🛠️ 创作辅助工具功能开发中...")
        # TODO: 实现创作辅助工具
        return None
        
    elif choice == "5":
        # VIP多层内容创作
        return handle_vip_content_creation_menu(pipeline)
        
    elif choice == "0":
        return None
    else:
        print("❌ 无效选择，请重新输入")
        return handle_smart_creation_menu(pipeline)


def handle_vip_content_creation_menu(pipeline):
    """VIP多层内容创作菜单 - 委托给CLI模块处理"""
    from scripts.cli.vip_menu_handler import VIPMenuHandler
    
    vip_handler = VIPMenuHandler(pipeline)
    return vip_handler.handle_vip_content_creation()


def handle_youtube_processing_menu(pipeline):
    """YouTube内容处理菜单 - 委托给CLI模块处理"""
    from scripts.cli.youtube_menu_handler import YouTubeMenuHandler
    
    youtube_handler = YouTubeMenuHandler(pipeline)
    return youtube_handler.handle_youtube_processing_menu()


def handle_audio_tools_menu(pipeline):
    """语音和音频工具菜单 (合并原功能12+相关)"""
    print("\n" + "="*50)
    print("🔊 语音和音频工具")
    print("="*50)
    print("🎙️ TTS服务管理和音频处理工具")
    
    print("\n请选择工具：")
    print("1. TTS语音测试")
    print("2. 音频质量评估") 
    print("3. 语音服务切换")
    print("4. 音频格式转换")
    print("0. 返回主菜单")
    
    choice = input("\n请选择 (1-4/0): ").strip()
    
    if choice == "1":
        # TTS语音测试 (原ElevenLabs测试)
        handle_elevenlabs_menu(pipeline)
        
    elif choice == "2":
        # 音频质量评估
        print("\n📊 音频质量评估功能开发中...")
        # TODO: 实现音频质量评估
        
    elif choice == "3":
        # 语音服务切换 (支持豆包、Edge TTS等)
        print("\n🔄 语音服务切换功能开发中...")
        print("💡 规划支持：豆包(中文) + Edge TTS(英文) + ElevenLabs(备选)")
        # TODO: 实现混合TTS架构
        
    elif choice == "4":
        # 音频格式转换
        print("\n🎵 音频格式转换功能开发中...")
        # TODO: 实现音频格式转换
        
    elif choice == "0":
        return
    else:
        print("❌ 无效选择，请重新输入")
        handle_audio_tools_menu(pipeline)


def handle_system_tools_menu(pipeline):
    """系统工具集合菜单 (合并原功能7+10+11)"""
    print("\n" + "="*50)
    print("⚙️ 系统工具集合")
    print("="*50)
    print("🛠️ 系统维护和配置管理")
    
    print("\n请选择工具：")
    print("1. 系统状态检查")
    print("2. LLM引擎切换")
    print("3. 调试和维护")
    print("4. 配置管理")
    print("5. 日志查看")
    print("0. 返回主菜单")
    
    choice = input("\n请选择 (1-5/0): ").strip()
    
    if choice == "1":
        # 系统状态检查 (原功能7)
        handle_system_check_menu(pipeline)
        
    elif choice == "2":
        # LLM引擎切换 (原功能11)
        handle_llm_engine_menu(pipeline)
        
    elif choice == "3":
        # 调试和维护 (原功能10)
        handle_debug_menu(pipeline)
        
    elif choice == "4":
        # 配置管理
        print("\n⚙️ 配置管理功能开发中...")
        # TODO: 实现配置管理功能
        
    elif choice == "5":
        # 日志查看
        print("\n📋 日志查看功能开发中...")
        # TODO: 实现日志查看功能
        
    elif choice == "0":
        return
    else:
        print("❌ 无效选择，请重新输入")
        handle_system_tools_menu(pipeline)


def handle_onedrive_cleanup_menu():
    """OneDrive云端清理工具菜单"""
    while True:
        print("\n" + "="*50)
        print("🗑️ OneDrive云端清理工具")
        print("="*50)
        print("📋 功能说明：")
        print("   • 按日期范围删除OneDrive中的图片文件")
        print("   • 支持预览和安全删除机制")
        print("   • 自动更新本地索引记录")
        print()
        print("🕒 支持的日期格式：")
        print("   • 相对时间: 7d (7天), 24h (24小时)")
        print("   • 绝对日期: 2025-08-12")
        print("   • 日期范围: 2025-08-12:2025-08-15")
        print()
        print("请选择操作：")
        print("1. 列出所有云端文件")
        print("2. 预览指定日期范围的文件")
        print("3. 删除指定日期范围的文件")
        print("4. 查看工具使用指南")
        print("\n0. 返回上级菜单")
        
        choice = input("\n请选择操作 (1-4/0): ").strip()
        
        if choice == "1":
            # 列出所有文件
            print("📡 正在获取OneDrive文件列表...")
            try:
                import subprocess
                result = subprocess.run([
                    "python", "scripts/tools/cleanup_onedrive_cloud.py", "--list"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(result.stdout)
                else:
                    print(f"❌ 获取文件列表失败：\n{result.stderr}")
            except Exception as e:
                print(f"❌ 执行命令失败：{e}")
                
        elif choice == "2":
            # 预览文件
            date_range = input("请输入日期范围 (例如：7d, 24h, 2025-08-12): ").strip()
            if date_range:
                print(f"🔍 预览日期范围: {date_range}")
                try:
                    import subprocess
                    result = subprocess.run([
                        "python", "scripts/tools/cleanup_onedrive_cloud.py", 
                        "--preview", date_range
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        print(result.stdout)
                    else:
                        print(f"❌ 预览失败：\n{result.stderr}")
                except Exception as e:
                    print(f"❌ 执行命令失败：{e}")
            else:
                print("❌ 日期范围不能为空")
                
        elif choice == "3":
            # 删除文件
            date_range = input("请输入要删除的日期范围 (例如：7d, 24h, 2025-08-12): ").strip()
            if date_range:
                print("⚠️ 警告：此操作将永久删除OneDrive中的文件！")
                confirm = input("确认要继续吗？输入 'yes' 确认: ").strip().lower()
                
                if confirm == 'yes':
                    print(f"🗑️ 删除日期范围: {date_range}")
                    try:
                        import subprocess
                        result = subprocess.run([
                            "python", "scripts/tools/cleanup_onedrive_cloud.py", 
                            "--delete", date_range
                        ], capture_output=True, text=True)
                        
                        if result.returncode == 0:
                            print(result.stdout)
                        else:
                            print(f"❌ 删除失败：\n{result.stderr}")
                    except Exception as e:
                        print(f"❌ 执行命令失败：{e}")
                else:
                    print("❌ 操作已取消")
            else:
                print("❌ 日期范围不能为空")
                
        elif choice == "4":
            # 使用指南
            print("\n" + "="*50)
            print("📖 OneDrive云端清理工具使用指南")
            print("="*50)
            print("🕒 日期格式说明：")
            print("   • 相对时间：")
            print("     - 7d：最近7天")
            print("     - 24h：最近24小时")
            print("     - 30d：最近30天")
            print()
            print("   • 绝对日期：")
            print("     - 2025-08-12：指定日期当天")
            print("     - 2025-08-12:2025-08-15：日期范围")
            print()
            print("🛡️ 安全机制：")
            print("   • 删除前会显示详细的文件列表预览")
            print("   • 需要二次确认才能执行删除操作")
            print("   • 自动更新本地索引，保持数据一致性")
            print("   • 支持单独预览模式，安全查看待删除文件")
            print()
            print("⚠️ 注意事项：")
            print("   • 删除操作不可逆，请谨慎使用")
            print("   • 建议先使用预览功能确认文件列表")
            print("   • 仅删除图片文件，不会影响文件夹结构")
            print("   • 需要有效的OneDrive认证才能使用")
            
        elif choice == "0":
            break
        else:
            print("❌ 无效选择，请重新输入")
        
        if choice in ["1", "2", "3"]:
            input("\n按Enter键继续...")


def handle_onedrive_date_download_menu(pipeline):
    """OneDrive按日期下载图片备份菜单"""
    while True:
        print("\n" + "="*50)
        print("📅 OneDrive按日期下载图片备份")
        print("="*50)
        print("1. 查看可用的上传日期")
        print("2. 按日期范围下载图片（预览模式）")
        print("3. 按日期范围下载图片（实际下载）")
        print("4. 下载最近几天的图片")
        print("5. 使用指南")
        print("\n0. 返回OneDrive图床管理菜单")
        
        choice = input("\n请选择操作 (1-5/0): ").strip()
        
        if choice == "1":
            # 查看可用日期
            print("📅 查看可用的上传日期...")
            try:
                result = subprocess.run([
                    "python3", "scripts/tools/onedrive_date_downloader.py", 
                    "--list-dates"
                ], check=False, capture_output=False)
                
                if result.returncode != 0:
                    print("❌ 获取日期列表失败")
                    
            except Exception as e:
                print(f"❌ 执行失败: {e}")
                
        elif choice == "2":
            # 预览模式下载
            print("🔍 按日期范围下载图片（预览模式）")
            print("支持的日期格式：")
            print("  • 相对时间: 7d (7天前), 24h (24小时前)")
            print("  • 绝对日期: 2025-08-12")
            print("  • 留空表示不限制")
            
            start_date = input("\n开始日期 (留空表示最早): ").strip()
            end_date = input("结束日期 (留空表示最新): ").strip()
            limit = input("限制数量 (留空表示全部): ").strip()
            
            cmd = ["python3", "scripts/tools/onedrive_date_downloader.py", "--dry-run"]
            if start_date:
                cmd.extend(["--start-date", start_date])
            if end_date:
                cmd.extend(["--end-date", end_date])
            if limit and limit.isdigit():
                cmd.extend(["--limit", limit])
            
            try:
                print("\n🔍 执行预览...")
                result = subprocess.run(cmd, check=False, capture_output=False)
                
                if result.returncode != 0:
                    print("❌ 预览执行失败")
                    
            except Exception as e:
                print(f"❌ 执行失败: {e}")
                
        elif choice == "3":
            # 实际下载
            print("📥 按日期范围下载图片（实际下载）")
            print("⚠️ 这将实际下载文件到本地")
            print("支持的日期格式：")
            print("  • 相对时间: 7d (7天前), 24h (24小时前)")
            print("  • 绝对日期: 2025-08-12")
            print("  • 留空表示不限制")
            
            start_date = input("\n开始日期 (留空表示最早): ").strip()
            end_date = input("结束日期 (留空表示最新): ").strip()
            limit = input("限制数量 (留空表示全部): ").strip()
            download_dir = input("下载目录 (默认: temp/date_downloads): ").strip()
            
            if not download_dir:
                download_dir = "temp/date_downloads"
            
            # 确认操作
            confirm = input(f"\n确认下载到目录 '{download_dir}'？(y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ 操作取消")
                continue
            
            cmd = ["python3", "scripts/tools/onedrive_date_downloader.py", "--download-dir", download_dir]
            if start_date:
                cmd.extend(["--start-date", start_date])
            if end_date:
                cmd.extend(["--end-date", end_date])
            if limit and limit.isdigit():
                cmd.extend(["--limit", limit])
            
            try:
                print("\n📥 开始下载...")
                result = subprocess.run(cmd, check=False, capture_output=False)
                
                if result.returncode == 0:
                    print("✅ 下载完成")
                    pipeline.log(f"OneDrive图片按日期下载完成，目录：{download_dir}", level="info")
                else:
                    print("❌ 下载执行失败")
                    
            except Exception as e:
                print(f"❌ 执行失败: {e}")
                
        elif choice == "4":
            # 下载最近几天的图片
            print("📥 下载最近几天的图片")
            days = input("输入天数 (默认: 7): ").strip()
            if not days or not days.isdigit():
                days = "7"
            
            limit = input("限制数量 (留空表示全部): ").strip()
            download_dir = input("下载目录 (默认: temp/recent_downloads): ").strip()
            
            if not download_dir:
                download_dir = "temp/recent_downloads"
            
            # 确认操作
            confirm = input(f"\n确认下载最近{days}天的图片到 '{download_dir}'？(y/N): ").strip().lower()
            if confirm != 'y':
                print("❌ 操作取消")
                continue
            
            cmd = ["python3", "scripts/tools/onedrive_date_downloader.py", 
                   "--start-date", f"{days}d", "--download-dir", download_dir]
            if limit and limit.isdigit():
                cmd.extend(["--limit", limit])
            
            try:
                print(f"\n📥 开始下载最近{days}天的图片...")
                result = subprocess.run(cmd, check=False, capture_output=False)
                
                if result.returncode == 0:
                    print("✅ 下载完成")
                    pipeline.log(f"OneDrive最近{days}天图片下载完成，目录：{download_dir}", level="info")
                else:
                    print("❌ 下载执行失败")
                    
            except Exception as e:
                print(f"❌ 执行失败: {e}")
                
        elif choice == "5":
            # 使用指南
            print("\n" + "="*50)
            print("📖 OneDrive按日期下载图片使用指南")
            print("="*50)
            print()
            print("🎯 功能说明：")
            print("   本工具可以按日期范围从OneDrive云端下载已上传的图片备份")
            print("   特别适用于错误处理后的图片恢复场景")
            print()
            print("📅 支持的日期格式：")
            print("   • 相对时间: 7d (7天前), 24h (24小时前), 1h (1小时前)")
            print("   • 绝对日期: 2025-08-12, 2025-08-12T10:30:00")
            print("   • 日期范围: 通过开始日期和结束日期组合使用")
            print()
            print("💡 使用建议：")
            print("   1. 先使用'查看可用日期'了解可下载的时间范围")
            print("   2. 使用'预览模式'确认要下载的文件列表")
            print("   3. 确认无误后再执行'实际下载'")
            print("   4. 可以使用'限制数量'参数控制下载文件数")
            print()
            print("🛡️ 安全特性：")
            print("   • 使用OneDrive API安全下载，不会误删云端文件")
            print("   • 下载前有确认步骤，防止误操作")
            print("   • 自动创建下载目录，不会覆盖现有文件")
            print("   • 跳过已存在的文件，支持断点续传")
            print()
            print("🔧 适用场景：")
            print("   • 文章处理出错后恢复图片")
            print("   • 定期备份重要图片到本地")
            print("   • 迁移或同步图片资源")
            print("   • 清理前的图片备份")
            
        elif choice == "0":
            break
        else:
            print("❌ 无效选择，请重新输入")
        
        if choice in ["1", "2", "3", "4"]:
            input("\n按Enter键继续...")


def handle_youtube_oauth_menu(pipeline):
    """YouTube OAuth认证管理菜单"""
    print("\n" + "="*50)
    print("🔐 YouTube OAuth认证管理")
    print("="*50)
    print("📋 功能说明：")
    print("   • 管理YouTube上传所需的OAuth2认证")
    print("   • 检查认证状态和token有效性")
    print("   • 重新生成或修复认证问题")
    print("   • 提供详细的配置指导")
    
    # 检查当前OAuth状态
    try:
        from pathlib import Path
        import json
        
        credentials_file = Path("config/youtube_oauth_credentials.json")
        token_file = Path("config/youtube_oauth_token.json")
        
        # 简单状态检查
        credentials_exists = credentials_file.exists()
        token_exists = token_file.exists()
        
        # 检查token是否是占位符
        token_valid = False
        if token_exists:
            try:
                with open(token_file, 'r') as f:
                    token_data = json.load(f)
                token_valid = not (token_data.get('token', '').startswith('placeholder_token_'))
            except:
                pass
        
        print("\n📊 当前OAuth状态:")
        print(f"   凭据文件: {'✅ 存在' if credentials_exists else '❌ 缺失'}")
        print(f"   认证Token: {'✅ 有效' if token_valid else '❌ 无效/缺失'}")
        
        oauth_ready = credentials_exists and token_valid
        if oauth_ready:
            print("🎉 OAuth认证状态: ✅ 完全配置，可以上传")
        else:
            print("⚠️  OAuth认证状态: ❌ 需要配置")
            
    except Exception as e:
        print(f"⚠️ 状态检查失败: {e}")
        oauth_ready = False
    
    print("\n请选择操作：")
    print("1. 检查OAuth认证状态")
    print("2. 生成新的OAuth授权链接")
    print("3. 使用授权码完成认证")
    print("4. 测试YouTube API连接")
    print("5. 查看OAuth配置文档")
    print("6. 重置OAuth配置")
    print("0. 返回上级菜单")
    
    choice = input("\n请选择操作 (1-6/0): ").strip()
    
    if choice == "1":
        # 检查OAuth认证状态
        try:
            import subprocess
            result = subprocess.run([
                "python", "scripts/tools/oauth/check_oauth_status.py"
            ], capture_output=False, text=True)
            
        except Exception as e:
            print(f"❌ 状态检查失败: {e}")
            
    elif choice == "2":
        # 生成新的OAuth授权链接
        print("\n🔐 生成OAuth授权链接")
        print("=" * 40)
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            
            SCOPES = [
                'https://www.googleapis.com/auth/youtube.readonly',
                'https://www.googleapis.com/auth/youtube.upload'
            ]
            
            credentials_file = 'config/youtube_oauth_credentials.json'
            if not Path(credentials_file).exists():
                print("❌ OAuth凭据文件不存在")
                print("💡 请先配置Google Cloud OAuth凭据文件")
                return
                
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            flow.redirect_uri = 'http://localhost:8080'
            
            auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
            print("✅ OAuth授权链接已生成")
            print("\n请访问以下URL完成授权:")
            print(f"{auth_url}")
            print("\n📋 操作步骤:")
            print("1. 复制上面的链接到浏览器打开")
            print("2. 使用Google账号登录并授权")
            print("3. 授权后会跳转到localhost:8080页面")
            print("4. 复制地址栏中'code='后的授权码")
            print("5. 选择选项3使用授权码完成认证")
            
        except Exception as e:
            print(f"❌ 生成授权链接失败: {e}")
            
    elif choice == "3":
        # 使用授权码完成认证
        print("\n🔑 使用授权码完成认证")
        print("=" * 40)
        
        auth_code = input("请输入授权码: ").strip()
        if not auth_code:
            print("❌ 授权码不能为空")
            return
            
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            import json
            
            SCOPES = [
                'https://www.googleapis.com/auth/youtube.readonly',
                'https://www.googleapis.com/auth/youtube.upload'
            ]
            
            credentials_file = 'config/youtube_oauth_credentials.json'
            token_file = 'config/youtube_oauth_token.json'
            
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            flow.redirect_uri = 'http://localhost:8080'
            
            print("📝 正在使用授权码获取访问令牌...")
            credentials = flow.fetch_token(code=auth_code)
            
            # 保存token
            token_data = json.loads(flow.credentials.to_json())
            with open(token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            print("✅ OAuth认证完成！")
            print(f"💾 Token已保存到: {token_file}")
            print("🎉 现在可以使用YouTube上传功能了")
            
        except Exception as e:
            print(f"❌ 认证失败: {e}")
            
    elif choice == "4":
        # 测试YouTube API连接
        print("\n🧪 测试YouTube API连接")
        print("=" * 40)
        
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request
            import json
            
            token_file = 'config/youtube_oauth_token.json'
            if not Path(token_file).exists():
                print("❌ Token文件不存在，请先完成OAuth认证")
                return
                
            with open(token_file, 'r') as f:
                token_data = json.load(f)
            
            creds = Credentials.from_authorized_user_info(token_data)
            
            if not creds.valid:
                if creds.refresh_token:
                    print("🔄 刷新过期的OAuth令牌...")
                    creds.refresh(Request())
                    print("✅ OAuth令牌刷新成功")
                else:
                    print("❌ OAuth令牌无效且无法刷新")
                    return
            
            youtube = build('youtube', 'v3', credentials=creds)
            
            # 测试API调用
            channels_response = youtube.channels().list(
                part='snippet,contentDetails',
                mine=True
            ).execute()
            
            if channels_response.get('items'):
                channel = channels_response['items'][0]
                print("✅ YouTube API连接测试成功")
                print(f"📺 频道名称: {channel['snippet']['title']}")
                print(f"🆔 频道ID: {channel['id']}")
                print("🎉 具备完整的YouTube上传权限")
            else:
                print("⚠️ 未找到YouTube频道")
                
        except Exception as e:
            print(f"❌ API连接测试失败: {e}")
            
    elif choice == "5":
        # 查看OAuth配置文档
        print("\n📖 YouTube OAuth配置文档")
        print("=" * 50)
        print("🎯 OAuth2认证配置步骤:")
        print()
        print("1️⃣ 创建Google Cloud项目")
        print("   • 访问: https://console.cloud.google.com/")
        print("   • 创建新项目或选择现有项目")
        print("   • 启用YouTube Data API v3")
        print()
        print("2️⃣ 创建OAuth2凭据")
        print("   • 转到 APIs & Services > Credentials")
        print("   • 点击 Create Credentials > OAuth client ID")
        print("   • 应用类型选择: Desktop application")
        print("   • 下载JSON文件到 config/youtube_oauth_credentials.json")
        print()
        print("3️⃣ 配置OAuth范围")
        print("   • YouTube.readonly: 读取频道信息")
        print("   • YouTube.upload: 上传视频权限")
        print()
        print("4️⃣ 完成认证流程")
        print("   • 选择选项2生成授权链接")
        print("   • 浏览器中完成Google账号授权")
        print("   • 选择选项3使用授权码完成认证")
        print()
        print("⚠️ 注意事项:")
        print("   • 确保redirect_uri包含 http://localhost:8080")
        print("   • 首次认证需要Google账号授权")
        print("   • Token会自动刷新，无需重复认证")
        
    elif choice == "6":
        # 重置OAuth配置
        print("\n🔄 重置OAuth配置")
        print("=" * 40)
        print("⚠️ 这将删除现有的OAuth Token文件")
        print("⚠️ 您需要重新完成OAuth认证流程")
        
        confirm = input("\n确认重置? (y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            try:
                token_file = Path("config/youtube_oauth_token.json")
                if token_file.exists():
                    token_file.unlink()
                    print("✅ OAuth Token文件已删除")
                else:
                    print("ℹ️ Token文件不存在")
                    
                print("🔄 请重新执行OAuth认证流程:")
                print("   1. 选择选项2生成授权链接")
                print("   2. 选择选项3使用授权码完成认证")
                
            except Exception as e:
                print(f"❌ 重置失败: {e}")
        else:
            print("ℹ️ 操作已取消")
            
    elif choice == "0":
        return
    else:
        print("❌ 无效选择，请重新输入")
    
    input("\n按Enter键继续...")


if __name__ == "__main__":
    main() 