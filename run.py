#!/usr/bin/env python
"""
内容处理流水线启动脚本
"""
import os
import sys
import argparse
import logging
import subprocess
from pathlib import Path
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
        print("📝 内容发布：")
        print("1. 处理现有草稿")
        print("2. 重新发布已发布文章")
        print("3. 生成测试文章")
        print("\n🛠️ 系统工具：")
        print("4. 内容变现管理")
        print("5. 系统状态检查")
        print("6. 文章更新工具")
        print("7. 调试和维护工具")
        print("\n0. 退出")
        
        choice = input("\n请输入选项 (1-7/0): ").strip()
        
        # 记录用户选择的操作
        choice_names = {
            '1': '处理现有草稿', '2': '重新发布已发布文章', '3': '生成测试文章',
            '4': '内容变现管理', '5': '系统状态检查', '6': '文章更新工具', 
            '7': '调试和维护工具', '0': '退出'
        }
        operation_name = choice_names.get(choice, '无效选择')
        pipeline.log(f"用户选择操作: {choice} ({operation_name})", level="info", force=True)
        
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
        elif choice == "4":
            # 内容变现管理
            handle_monetization_menu(pipeline)
            continue  # 返回主菜单
        elif choice == "5":
            # 系统状态检查
            handle_system_check_menu(pipeline)
            continue  # 返回主菜单
        elif choice == "6":
            # 文章更新工具
            handle_post_update_menu(pipeline)
            continue  # 返回主菜单
        elif choice == "7":
            # 调试和维护工具
            handle_debug_menu(pipeline)
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
    print("0. 返回主菜单")
    
    sub_choice = input("\n请输入选项 (1-4/0): ").strip()
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
            script_path = Path("scripts/tools/test_reward_system.py")
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
    
    input("\n按Enter键返回主菜单...")


def handle_system_check_menu(pipeline):
    """处理系统状态检查菜单"""
    print("\n" + "="*40)
    print("🔍 系统状态检查")
    print("="*40)
    print("📋 功能说明：")
    print("   • 检查微信发布系统状态和输出文件")
    print("   • 检查GitHub Token有效性和过期时间")
    print("   • 验证系统各组件工作状态")
    
    print("\n请选择检查项目：")
    print("1. 微信系统状态检查")
    print("2. GitHub Token状态检查")
    print("3. 综合系统检查")
    print("0. 返回主菜单")
    
    sub_choice = input("\n请输入选项 (1-3/0): ").strip()
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
            script_path = Path("scripts/tools/check_github_token.py")
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
            script_path = Path("scripts/tools/check_github_token.py")
            result = execute_script_with_logging(
                pipeline, script_path, [], 
                "综合检查-GitHub Token"
            )
            print(result.stdout)
        except Exception as e:
            print(f"❌ GitHub Token检查失败: {e}")
    
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
    print("3. 查看文章更新帮助")
    print("0. 返回主菜单")
    
    sub_choice = input("\n请输入选项 (1-3/0): ").strip()
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
                    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                                          capture_output=True, text=True)
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


if __name__ == "__main__":
    main() 