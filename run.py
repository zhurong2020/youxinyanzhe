#!/usr/bin/env python
"""
内容处理流水线启动脚本
"""
import os
import sys
import argparse
import logging
import subprocess
import yaml
from pathlib import Path
from dotenv import load_dotenv
from scripts.core.content_pipeline import ContentPipeline

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
    
    # session_count = 1  # 记录操作次数 - 暂未使用
    
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
        print("6. YouTube播客生成器")
        print("7. 文章更新工具")
        print("8. 调试和维护工具")
        print("9. LLM引擎切换")
        print("10. ElevenLabs语音测试")
        print("11. YouTube音频上传")
        print("\n0. 退出")
        
        choice = input("\n请输入选项 (1-11/0): ").strip()
        
        # 记录用户选择的操作
        choice_names = {
            '1': '处理现有草稿', '2': '重新发布已发布文章', '3': '生成测试文章',
            '4': '内容变现管理', '5': '系统状态检查', '6': 'YouTube播客生成器',
            '7': '文章更新工具', '8': '调试和维护工具', '9': 'LLM引擎切换', 
            '10': 'ElevenLabs语音测试', '11': 'YouTube音频上传', '0': '退出'
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
            # YouTube播客生成器
            handle_youtube_podcast_menu(pipeline)
            continue  # 返回主菜单
        elif choice == "7":
            # 文章更新工具
            handle_post_update_menu(pipeline)
            continue  # 返回主菜单
        elif choice == "8":
            # 调试和维护工具
            handle_debug_menu(pipeline)
            continue  # 返回主菜单
        elif choice == "9":
            # LLM引擎切换
            handle_llm_engine_menu(pipeline)
            continue  # 返回主菜单
        elif choice == "10":
            # ElevenLabs语音测试
            handle_elevenlabs_menu(pipeline)
            continue  # 返回主菜单
        elif choice == "11":
            # YouTube音频上传
            handle_youtube_upload_menu(pipeline)
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
        input("\n按Enter键返回主菜单...")
        main()  # 重新开始主循环
        return
    
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
    
    # 发布完成后，询问是否返回主菜单
    print("\n" + "="*50)
    pipeline.log("发布流程结束，等待用户选择", level="info", force=True)
    input("按Enter键返回主菜单...")
    main()  # 重新开始主循环
    return


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
            script_path = Path("scripts/tools/check_github_token.py")
            result = execute_script_with_logging(
                pipeline, script_path, [], 
                "综合检查-GitHub Token"
            )
            print(result.stdout)
        except Exception as e:
            print(f"❌ GitHub Token检查失败: {e}")
        
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


def handle_youtube_podcast_menu(pipeline):
    """处理YouTube播客生成器菜单"""
    print("\n" + "="*40)
    print("🎧 YouTube播客生成器")
    print("="*40)
    print("📋 功能说明：")
    print("   • 将英文YouTube视频转换为中文播客")
    print("   • 自动生成学习导读和Jekyll文章")
    print("   • 专为英语学习和全球视野系列设计")
    print("\n⚠️  前提条件：")
    print("   • 需要配置GEMINI_API_KEY (用于内容生成)")
    print("   • 可选配置YOUTUBE_API_KEY (用于视频信息获取)")
    print("   • 确保网络连接正常访问Podcastfy服务")
    
    print("\n请选择操作：")
    print("1. 生成YouTube播客学习文章")
    print("2. 上传已生成的播客视频")
    print("3. 查看配置状态")
    print("4. 使用说明和示例")
    print("0. 返回主菜单")
    
    sub_choice = input("\n请输入选项 (1-4/0): ").strip()
    pipeline.log(f"YouTube播客生成器 - 用户选择: {sub_choice}", level="info", force=True)
    
    if sub_choice == "1":
        # 生成YouTube播客学习文章
        try:
            youtube_url = input("\n请输入YouTube视频链接: ").strip()
            if not youtube_url:
                print("❌ YouTube链接不能为空")
                input("按Enter键返回菜单...")
                return
            
            # 验证YouTube链接格式
            if not ("youtube.com" in youtube_url or "youtu.be" in youtube_url):
                print("❌ 请输入有效的YouTube链接")
                print("✅ 支持的格式:")
                print("   • https://www.youtube.com/watch?v=VIDEO_ID")
                print("   • https://youtu.be/VIDEO_ID")
                print("   • https://www.youtube.com/embed/VIDEO_ID")
                input("按Enter键返回菜单...")
                return
            
            # 进一步验证URL格式
            import re
            youtube_patterns = [
                r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
                r'youtube\.com\/v\/([^&\n?#]+)'
            ]
            
            video_id_found = False
            for pattern in youtube_patterns:
                if re.search(pattern, youtube_url):
                    video_id_found = True
                    break
            
            if not video_id_found:
                print("❌ 无法从URL中提取视频ID，请检查链接格式")
                print("✅ 正确示例: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
                input("按Enter键返回菜单...")
                return
            
            custom_title = input("请输入自定义标题 (可选，留空使用自动生成): ").strip()
            
            # 语音设置选项
            print("\n🎤 播客语音设置:")
            print("1. 中文播客 (推荐)")
            print("2. 英文播客")
            print("3. 日文播客")  
            print("4. 韩文播客")
            
            voice_choice = input("请选择播客语言 (1-4，默认1): ").strip()
            language_map = {
                "1": "zh-CN", "2": "en-US", "3": "ja-JP", "4": "ko-KR", "": "zh-CN"
            }
            target_language = language_map.get(voice_choice, "zh-CN")
            
            print("\n🔊 TTS模型选择:")
            print("1. Edge TTS (免费，推荐)")
            print("2. OpenAI TTS (需要API密钥)")
            print("3. Google Multi-speaker (最佳质量)")
            print("4. ElevenLabs (最高质量，需要API密钥)")
            
            tts_choice = input("请选择TTS模型 (1-4，默认1): ").strip()
            tts_map = {
                "1": "edge", "2": "openai", "3": "geminimulti", "4": "elevenlabs", "": "edge"
            }
            tts_model = tts_map.get(tts_choice, "edge")
            
            print("\n🎭 播客对话风格:")
            print("1. 轻松聊天 (casual,informative)")
            print("2. 学术讨论 (academic,analytical)")
            print("3. 新闻播报 (news,professional)")
            print("4. 深度分析 (deep-dive,expert)")
            print("5. 自定义风格")
            
            style_choice = input("请选择对话风格 (1-5，默认1): ").strip()
            style_map = {
                "1": "casual,informative",
                "2": "academic,analytical", 
                "3": "news,professional",
                "4": "deep-dive,expert",
                "": "casual,informative"
            }
            
            if style_choice == "5":
                conversation_style = input("请输入自定义风格 (例: casual,funny,engaging): ").strip()
                if not conversation_style:
                    conversation_style = "casual,informative"
            else:
                conversation_style = style_map.get(style_choice, "casual,informative")
            
            # YouTube上传选项
            upload_to_youtube = False
            youtube_key = os.getenv('YOUTUBE_API_KEY')
            pipeline.log(f"YouTube API Key 检查: {'已配置' if youtube_key else '未配置'}", level="debug")
            if youtube_key and youtube_key.strip():
                print("\n📤 播客存储选项:")
                print("1. 仅本地存储 (assets/audio/)")
                print("2. 上传到YouTube (推荐，节省空间)")
                
                upload_choice = input("请选择存储方式 (1-2，默认1): ").strip()
                if upload_choice == "2":
                    upload_to_youtube = True
                    print("✅ 将上传播客到YouTube")
                else:
                    print("📁 播客将保存在本地")
            else:
                print("\n💡 提示：配置YOUTUBE_API_KEY可启用YouTube播客上传功能")
            
            print(f"\n🔄 开始处理YouTube视频...")
            print(f"📝 语言: {target_language}, TTS: {tts_model}")
            print(f"📤 存储: {'YouTube' if upload_to_youtube else '本地'}")
            print("📝 这可能需要1-3分钟，请耐心等待...")
            
            # 导入并使用YouTube播客生成器
            try:
                from scripts.core.youtube_podcast_generator import YouTubePodcastGenerator
                
                # 获取配置
                config = {
                    'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
                    'YOUTUBE_API_KEY': os.getenv('YOUTUBE_API_KEY'),  # 可选
                    'ELEVENLABS_API_KEY': os.getenv('ELEVENLABS_API_KEY')  # 可选，高质量TTS
                }
                
                if not config['GEMINI_API_KEY']:
                    print("❌ 未配置GEMINI_API_KEY，请在.env文件中设置")
                    return
                
                # 创建生成器实例，传递pipeline用于统一日志
                generator = YouTubePodcastGenerator(config, pipeline)
                pipeline.log(f"开始处理YouTube视频: {youtube_url}", level="info", force=True)
                
                # 生成播客和文章
                result = generator.generate_from_youtube(
                    youtube_url, 
                    custom_title, 
                    tts_model, 
                    target_language,
                    conversation_style,
                    upload_to_youtube
                )
                
                if result['status'] == 'success':
                    print("✅ YouTube播客生成成功!")
                    print(f"📄 文章路径: {result['article_path']}")
                    print(f"🎧 音频路径: {result['audio_path']}")
                    print(f"🖼️  缩略图: {result['thumbnail_path']}")
                    print(f"📺 原视频: {result['video_title']}")
                    print(f"📝 文章标题: {result['article_title']}")
                    
                    # 显示YouTube播客信息
                    if result.get('youtube_video_id'):
                        print(f"🎭 YouTube播客: {result['youtube_podcast_url']}")
                        print("✨ 播客已上传到YouTube，节省本地存储空间！")
                    
                    pipeline.log(f"YouTube播客生成成功: {result['article_title']}", level="info", force=True)
                    
                    # 询问是否要发布
                    publish_choice = input("\n是否要发布此文章到各平台？(y/N): ").strip().lower()
                    if publish_choice in ['y', 'yes']:
                        print("📝 请返回主菜单选择 '1. 处理现有草稿' 来发布文章")
                        pipeline.log("用户选择发布文章，提示返回主菜单", level="info", force=True)
                    else:
                        print("📄 文章已保存到草稿目录，您可以稍后发布")
                        
                else:
                    print(f"❌ 生成失败: {result.get('error', '未知错误')}")
                    pipeline.log(f"YouTube播客生成失败: {result.get('error', '未知错误')}", level="error", force=True)
                    
            except ImportError as e:
                print(f"❌ 导入模块失败: {e}")
                print("请确保已安装必要的依赖: pip install gradio-client google-generativeai google-api-python-client")
            except Exception as e:
                print(f"❌ 生成过程失败: {e}")
                pipeline.log(f"YouTube播客生成异常: {e}", level="error", force=True)
                
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            
    elif sub_choice == "2":
        # 上传已生成的播客视频
        print("\n🎬 上传已生成的播客视频")
        print("="*40)
        
        # 检查.tmp/output/videos目录下的视频文件
        videos_dir = Path(".tmp/output/videos")
        if not videos_dir.exists():
            print("❌ 视频输出目录不存在")
            input("\n按Enter键返回菜单...")
            return
            
        video_files = list(videos_dir.glob("*.mp4"))
        if not video_files:
            print("❌ 未找到已生成的播客视频文件")
            print("💡 请先使用选项1生成播客文章和视频")
            input("\n按Enter键返回菜单...")
            return
            
        print(f"📁 找到 {len(video_files)} 个播客视频文件:")
        for i, video_file in enumerate(video_files, 1):
            file_size = video_file.stat().st_size / (1024*1024)  # MB
            from datetime import datetime
            modified_time = datetime.fromtimestamp(video_file.stat().st_mtime)
            print(f"  {i}. {video_file.name}")
            print(f"     大小: {file_size:.1f}MB | 生成时间: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
        try:
            choice = input(f"\n请选择要上传的视频 (1-{len(video_files)}): ").strip()
            if not choice.isdigit() or not (1 <= int(choice) <= len(video_files)):
                print("❌ 无效的选择")
                input("\n按Enter键返回菜单...")
                return
                
            selected_video = video_files[int(choice) - 1]
            print(f"\n📤 准备上传视频: {selected_video.name}")
            pipeline.log(f"准备上传播客视频: {selected_video.name}", level="info", force=True)
            
            # 从文件名解析信息
            video_name = selected_video.stem
            pipeline.log(f"解析视频文件名: {video_name}", level="debug", force=True)
            # 格式: youtube-YYYYMMDD-title-podcast
            if video_name.startswith("youtube-") and video_name.endswith("-podcast"):
                base_name = video_name[8:-8]  # 移除youtube-前缀和-podcast后缀
                date_part = base_name[:8]
                title_part = base_name[9:]  # 跳过日期和连字符
                
                pipeline.log(f"解析结果 - base_name: {base_name}, date_part: {date_part}, title_part: {title_part}", level="debug", force=True)
                
                # 查找对应的文章文件获取详细信息
                # date_part格式: YYYYMMDD (例如: 20250804)
                year = date_part[:4]    # 2025
                month = date_part[4:6]  # 08
                day = date_part[6:8]    # 04
                draft_file = Path(f"_drafts/{year}-{month}-{day}-youtube-{title_part}.md")
                pipeline.log(f"查找文章文件: {draft_file}", level="debug", force=True)
                if draft_file.exists():
                    print(f"✅ 找到对应的文章文件: {draft_file.name}")
                    
                    # 导入YouTube播客生成器来处理上传
                    try:
                        from scripts.core.youtube_podcast_generator import YouTubePodcastGenerator
                        
                        config = {
                            'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
                            'YOUTUBE_API_KEY': os.getenv('YOUTUBE_API_KEY'),
                            'ELEVENLABS_API_KEY': os.getenv('ELEVENLABS_API_KEY')
                        }
                        
                        generator = YouTubePodcastGenerator(config, pipeline)
                        
                        # 读取文章获取视频信息
                        with open(draft_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # 简单解析前置元数据
                        import re
                        title_match = re.search(r'title:\s*"([^"]+)"', content)
                        youtube_match = re.search(r'\[([^\]]+)\]\(https://www\.youtube\.com/watch\?v=([^)]+)\)', content)
                        
                        if title_match and youtube_match:
                            article_title = title_match.group(1)
                            original_title = youtube_match.group(1)
                            video_id = youtube_match.group(2)
                            
                            print(f"📺 原视频: {original_title}")
                            print(f"📝 文章标题: {article_title}")
                            print(f"🆔 视频ID: {video_id}")
                            
                            # 准备上传参数
                            video_info = {
                                'title': original_title,
                                'id': video_id
                            }
                            
                            content_guide = {
                                'title': article_title,
                                'excerpt': '通过播客学习英语，理解全球视野',
                                'outline': ['核心观点', '语言学习', '文化背景'],
                                'learning_tips': {
                                    'vocabulary': ['关键词汇'],
                                    'expressions': ['常用表达'],
                                    'cultural_context': '文化背景信息'
                                },
                                'tags': ['英语学习', '播客', '全球视野']
                            }
                            
                            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                            
                            confirm = input("\n确认上传到YouTube？(y/N): ").strip().lower()
                            if confirm in ['y', 'yes']:
                                print("🚀 开始上传到YouTube...")
                                video_upload_id = generator.upload_to_youtube(
                                    str(selected_video), video_info, content_guide, youtube_url
                                )
                                
                                if video_upload_id:
                                    youtube_link = f"https://www.youtube.com/watch?v={video_upload_id}"
                                    print(f"✅ 上传成功!")
                                    print(f"🔗 YouTube链接: {youtube_link}")
                                    
                                    # 更新文章中的YouTube链接
                                    updated_content = content.replace(
                                        "<!-- YouTube播客优先显示 -->",
                                        f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{video_upload_id}" frameborder="0" allowfullscreen></iframe>'
                                    )
                                    
                                    with open(draft_file, 'w', encoding='utf-8') as f:
                                        f.write(updated_content)
                                    
                                    print("📝 文章已更新，添加了YouTube播放器")
                                else:
                                    print("❌ 上传失败")
                                    print("💡 可能的原因：")
                                    print("   • 网络连接问题（文件较大，上传超时）")
                                    print("   • YouTube服务器临时不可用")
                                    print("   • OAuth权限不足")
                                    print("📋 请查看日志获取详细错误信息：")
                                    print("   tail -20 .build/logs/pipeline.log")
                            else:
                                print("❌ 已取消上传")
                        else:
                            print("❌ 无法解析文章中的视频信息")
                    except ImportError as e:
                        print(f"❌ 导入YouTube模块失败: {e}")
                    except Exception as e:
                        print(f"❌ 上传过程失败: {e}")
                        pipeline.log(f"YouTube视频上传失败: {e}", level="error", force=True)
                else:
                    print(f"❌ 未找到对应的文章文件: {draft_file}")
                    pipeline.log(f"未找到对应的文章文件: {draft_file}", level="error", force=True)
                    print(f"💡 预期的文章文件路径: {draft_file}")
                    print("💡 请检查文章文件是否存在于_drafts目录下")
            else:
                print("❌ 无法识别的视频文件名格式")
                pipeline.log(f"无法识别的视频文件名格式: {video_name}", level="error", force=True)
                print(f"💡 预期格式: youtube-YYYYMMDD-title-podcast")
                print(f"💡 实际格式: {video_name}")
                
        except ValueError:
            print("❌ 请输入有效的数字")
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            
        input("\n按Enter键返回菜单...")
        
    elif sub_choice == "3":
        # 查看配置状态
        print("\n🔍 配置状态检查")
        print("="*40)
        
        # 检查环境变量
        gemini_key = os.getenv('GEMINI_API_KEY')
        youtube_key = os.getenv('YOUTUBE_API_KEY')
        elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
        
        print(f"GEMINI_API_KEY: {'✅ 已配置' if gemini_key else '❌ 未配置'}")
        print(f"YOUTUBE_API_KEY: {'✅ 已配置' if youtube_key else '⚠️  未配置 (可选)'}")
        print(f"ELEVENLABS_API_KEY: {'✅ 已配置' if elevenlabs_key else '⚠️  未配置 (可选，但推荐)'}")
        
        # ElevenLabs配额检查
        if elevenlabs_key:
            print(f"\n📊 ElevenLabs配额检查")
            print("-" * 30)
            try:
                from scripts.core.youtube_podcast_generator import YouTubePodcastGenerator
                
                config = {
                    'GEMINI_API_KEY': gemini_key,
                    'YOUTUBE_API_KEY': youtube_key,
                    'ELEVENLABS_API_KEY': elevenlabs_key
                }
                
                # 创建临时实例仅用于配额检查
                temp_generator = YouTubePodcastGenerator(config, pipeline)
                if temp_generator.elevenlabs_available:
                    print("✅ ElevenLabs配额信息已显示在上方日志中")
                else:
                    print("⚠️  ElevenLabs API配置失败，无法查询配额")
                    
            except Exception as e:
                print(f"❌ 配额检查失败: {e}")
                pipeline.log(f"ElevenLabs配额检查异常: {e}", level="error", force=True)
        
        # 检查依赖
        try:
            import gradio_client
            print("gradio_client: ✅ 已安装")
        except ImportError:
            print("gradio_client: ❌ 未安装")
            
        try:
            import google.generativeai
            print("google-generativeai: ✅ 已安装")
        except ImportError:
            print("google-generativeai: ❌ 未安装")
            
        try:
            from googleapiclient.discovery import build
            print("google-api-python-client: ✅ 已安装")
        except ImportError:
            print("google-api-python-client: ❌ 未安装")
            
        try:
            import elevenlabs
            print("elevenlabs: ✅ 已安装")
        except ImportError:
            print("elevenlabs: ❌ 未安装 (可选，但推荐安装获得最高音质)")
        
        # 检查目录
        dirs_to_check = ['assets/audio', 'assets/images/posts', '_drafts']
        for dir_path in dirs_to_check:
            path = Path(dir_path)
            print(f"{dir_path}: {'✅ 存在' if path.exists() else '❌ 不存在'}")
            
    elif sub_choice == "4":
        # 使用说明和示例
        print("\n📖 YouTube播客生成器使用说明")
        print("="*40)
        print("🎯 功能概述:")
        print("   • 输入英文YouTube视频链接")
        print("   • 自动生成中文播客音频")
        print("   • 创建包含导读的Jekyll文章")
        print("   • 自动分类到全球视野系列")
        
        print("\n🔧 使用步骤:")
        print("   1. 配置.env文件中的GEMINI_API_KEY")
        print("   2. 选择 '1. 生成YouTube播客学习文章'")
        print("   3. 输入YouTube视频链接")
        print("   4. 等待1-3分钟自动处理")
        print("   5. 选择是否发布到各平台")
        
        print("\n📋 文章结构:")
        print("   • 📺 原始视频信息和链接")
        print("   • 🎧 中文播客音频播放器")
        print("   • 📋 内容大纲和要点")
        print("   • 🌍 英语学习指南")
        print("   • 🎯 学习建议和使用方法")
        
        print("\n💡 支持的YouTube链接格式:")
        print("   • https://www.youtube.com/watch?v=VIDEO_ID")
        print("   • https://youtu.be/VIDEO_ID")
        print("   • https://www.youtube.com/embed/VIDEO_ID")
        
        print("\n⚠️  注意事项:")
        print("   • 视频语言建议为英文")
        print("   • 内容长度建议在60分钟以内")
        print("   • 需要稳定的网络连接")
        print("   • 首次使用可能需要安装额外依赖")
    
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
    """处理LLM引擎切换菜单"""
    print("\n" + "="*40)
    print("🤖 LLM引擎切换管理")
    print("="*40)
    print("📋 功能说明：")
    print("   • 管理AI引擎使用模式")
    print("   • Claude Pro订阅 + 备用API引擎切换")
    print("   • 查看当前引擎状态和模型信息")
    print("\n💡 使用模式说明：")
    print("   • Claude: 使用您的Claude Pro订阅 ($20/月)")
    print("   • 千问3-code: 备用API引擎 (阿里云)")
    print("   • Kimi K2: 备用API引擎 (月之暗面, 高性价比)")
    print("\n⚠️  注意事项：")
    print("   • 当Claude Pro达到月度限制时，可切换到备用引擎")
    print("   • 备用引擎按使用量付费，适合突发需求")
    
    # 检查当前状态
    current_base_url = os.getenv('ANTHROPIC_BASE_URL', '')
    # current_auth_token = os.getenv('ANTHROPIC_AUTH_TOKEN', '')  # 暂未使用
    current_api_key = os.getenv('ANTHROPIC_API_KEY', '')
    
    if current_base_url and 'dashscope.aliyuncs.com' in current_base_url:
        current_engine = "千问3-code (Qwen)"
        engine_status = "🟢 活跃"
        model_info = "qwen3-code (1万亿参数MoE)"
    elif current_base_url and 'moonshot.ai' in current_base_url:
        current_engine = "Kimi K2 (Moonshot)"
        engine_status = "🟢 活跃"
        model_info = "kimi-k2 (1万亿参数MoE, 128K上下文)"
    elif current_api_key and current_api_key.startswith('sk-ant-'):
        current_engine = "Claude API"
        engine_status = "🟢 活跃"
        model_info = "claude-3.5-sonnet (API模式)"
    else:
        current_engine = "Claude Pro (默认)"
        engine_status = "🟢 活跃"
        model_info = "claude-3.5-sonnet (Pro订阅)"
    
    print(f"\n📊 当前状态：")
    print(f"   • 当前引擎: {current_engine}")
    print(f"   • 状态: {engine_status}")
    print(f"   • 模型信息: {model_info}")
    
    print("\n请选择操作：")
    print("1. 恢复Claude Pro模式 (默认)")
    print("2. 切换到千问3-code引擎")
    print("3. 切换到Kimi K2引擎")
    print("4. 查看引擎配置详情")
    print("5. 测试当前引擎连接")
    print("6. 重置引擎配置")
    print("7. 生成WSL环境变量设置脚本")
    print("0. 返回主菜单")
    
    sub_choice = input("\n请输入选项 (1-7/0): ").strip()
    pipeline.log(f"LLM引擎切换 - 用户选择: {sub_choice}", level="info", force=True)
    
    if sub_choice == "1":
        # 恢复Claude Pro模式
        print("\n🔄 恢复Claude Pro模式...")
        try:
            # 清除所有API配置，恢复默认Claude Pro模式
            env_vars_to_clear = ['ANTHROPIC_BASE_URL', 'ANTHROPIC_AUTH_TOKEN', 'ANTHROPIC_API_KEY']
            cleared_vars = []
            
            # 清除运行时环境变量
            for var in env_vars_to_clear:
                if var in os.environ:
                    del os.environ[var]
                    cleared_vars.append(var)
            
            # 持久化到.env文件
            for var in env_vars_to_clear:
                update_env_file(var, None)  # 删除.env文件中的配置
            
            # 生成WSL导出脚本
            script_path = create_export_script("default")
            
            print("✅ 已恢复Claude Pro模式")
            print("📝 配置详情：")
            print("   • 使用模式: Claude Pro订阅 ($20/月)")
            print("   • 认证方式: 浏览器登录 (非API)")
            print("   • 计费方式: 包月订阅")
            print("   • 使用限制: Claude Pro用户限制")
            if cleared_vars:
                print("   • 已清除的运行时配置:", ", ".join(cleared_vars))
            print("   • 📁 已从.env文件中移除相关配置")
            
            if script_path:
                print(f"   • 🚀 WSL导出脚本: {script_path}")
            
            print("\n⚠️  重要提示：")
            print("   • 当前run.py进程中配置已生效")
            print("   • Claude Code终端需要重启才能完全生效")
            print("   • 建议方案1：关闭并重新打开Claude Code终端")
            if script_path:
                print(f"   • 建议方案2：在WSL中运行: source {script_path}")
            
            pipeline.log("LLM引擎恢复到Claude Pro模式，已持久化到.env文件", level="info", force=True)
            
        except Exception as e:
            print(f"❌ 恢复失败: {e}")
            pipeline.log(f"LLM引擎恢复到Claude Pro失败: {e}", level="error", force=True)
    
    elif sub_choice == "2":
        # 切换到千问3-code引擎
        print("\n🔄 切换到千问3-code引擎...")
        try:
            # 设置千问配置
            qwen_api_key = os.getenv('QWEN_API_KEY', 'YOUR_QWEN_API_KEY_HERE')
            qwen_base_url = "https://dashscope.aliyuncs.com/api/v2"
            
            # 清除Claude配置（运行时）
            if 'ANTHROPIC_API_KEY' in os.environ:
                del os.environ['ANTHROPIC_API_KEY']
            
            # 设置千问配置（运行时）
            os.environ['ANTHROPIC_BASE_URL'] = qwen_base_url
            os.environ['ANTHROPIC_AUTH_TOKEN'] = qwen_api_key
            
            # 持久化到.env文件
            update_env_file('ANTHROPIC_API_KEY', None)  # 删除Claude API配置
            update_env_file('ANTHROPIC_BASE_URL', qwen_base_url)
            update_env_file('ANTHROPIC_AUTH_TOKEN', qwen_api_key)
            
            # 生成WSL导出脚本
            script_path = create_export_script("qwen")
            
            print("✅ 已切换到千问3-code引擎")
            print("📝 配置详情：")
            print(f"   • ANTHROPIC_BASE_URL: {qwen_base_url}")
            print(f"   • ANTHROPIC_AUTH_TOKEN: {qwen_api_key[:8]}...{qwen_api_key[-8:]}")
            print("   • ANTHROPIC_API_KEY: 🚫 已清除")
            print("   • 📁 配置已持久化到.env文件")
            
            if script_path:
                print(f"   • 🚀 WSL导出脚本: {script_path}")
            
            print("\n⚠️  重要提示：")
            print("   • 当前run.py进程中配置已生效")
            print("   • Claude Code终端需要重启才能完全生效")
            print("   • 建议方案1：关闭并重新打开Claude Code终端")
            if script_path:
                print(f"   • 建议方案2：在WSL中运行: source {script_path}")
            
            pipeline.log("LLM引擎切换到千问3-code，已持久化到.env文件", level="info", force=True)
            
        except Exception as e:
            print(f"❌ 切换失败: {e}")
            pipeline.log(f"LLM引擎切换到千问3-code失败: {e}", level="error", force=True)
    
    elif sub_choice == "3":
        # 切换到Kimi K2引擎
        print("\n🔄 切换到Kimi K2引擎...")
        try:
            # 设置Kimi K2配置
            kimi_api_key = os.getenv('KIMI_API_KEY', 'YOUR_KIMI_API_KEY_HERE')
            kimi_base_url = "https://api.moonshot.ai/anthropic"
            
            # 清除其他配置（运行时）
            if 'ANTHROPIC_API_KEY' in os.environ:
                del os.environ['ANTHROPIC_API_KEY']
            
            # 设置Kimi K2配置（运行时）
            os.environ['ANTHROPIC_BASE_URL'] = kimi_base_url
            os.environ['ANTHROPIC_AUTH_TOKEN'] = kimi_api_key
            
            # 持久化到.env文件
            update_env_file('ANTHROPIC_API_KEY', None)  # 删除Claude API配置
            update_env_file('ANTHROPIC_BASE_URL', kimi_base_url)
            update_env_file('ANTHROPIC_AUTH_TOKEN', kimi_api_key)
            
            # 生成WSL导出脚本
            script_path = create_export_script("kimi")
            
            print("✅ 已切换到Kimi K2引擎")
            print("📝 配置详情：")
            print(f"   • ANTHROPIC_BASE_URL: {kimi_base_url}")
            print(f"   • ANTHROPIC_AUTH_TOKEN: {kimi_api_key[:8]}...{kimi_api_key[-8:]}")
            print("   • ANTHROPIC_API_KEY: 🚫 已清除")
            print("   • 模型特性: 1万亿参数MoE, 128K上下文长度")
            print("   • 定价: $0.6/M输入, $2.5/M输出")
            print("   • SWE-Bench得分: 65.8%")
            print("   • 📁 配置已持久化到.env文件")
            
            if script_path:
                print(f"   • 🚀 WSL导出脚本: {script_path}")
            
            print("\n⚠️  重要提示：")
            print("   • 当前run.py进程中配置已生效")
            print("   • Claude Code终端需要重启才能完全生效")
            print("   • 建议方案1：关闭并重新打开Claude Code终端")
            if script_path:
                print(f"   • 建议方案2：在WSL中运行: source {script_path}")
            
            pipeline.log("LLM引擎切换到Kimi K2，已持久化到.env文件", level="info", force=True)
            
        except Exception as e:
            print(f"❌ 切换失败: {e}")
            pipeline.log(f"LLM引擎切换到Kimi K2失败: {e}", level="error", force=True)
    
    elif sub_choice == "4":
        # 查看引擎配置详情
        print("\n🔍 引擎配置详情")
        print("="*40)
        
        # 检查环境变量
        anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
        anthropic_base_url = os.getenv('ANTHROPIC_BASE_URL', '')
        anthropic_auth_token = os.getenv('ANTHROPIC_AUTH_TOKEN', '')
        
        print("📊 环境变量状态：")
        print(f"ANTHROPIC_API_KEY: {'✅ 已设置 (' + anthropic_api_key[:8] + '...' + anthropic_api_key[-4:] + ')' if anthropic_api_key else '❌ 未设置'}")
        print(f"ANTHROPIC_BASE_URL: {'✅ ' + anthropic_base_url if anthropic_base_url else '❌ 未设置 (使用默认)'}")
        print(f"ANTHROPIC_AUTH_TOKEN: {'✅ 已设置 (' + anthropic_auth_token[:8] + '...' + anthropic_auth_token[-8:] + ')' if anthropic_auth_token else '❌ 未设置'}")
        
        print("\n🎯 引擎识别：")
        if anthropic_base_url and 'dashscope.aliyuncs.com' in anthropic_base_url:
            print("   • 当前配置：千问3-code (阿里云)")
            print("   • 模型：qwen3-code")
            print("   • 提供商：阿里云DashScope")
            print("   • 特性：1万亿参数MoE架构")
        elif anthropic_base_url and 'moonshot.ai' in anthropic_base_url:
            print("   • 当前配置：Kimi K2 (月之暗面)")
            print("   • 模型：kimi-k2")
            print("   • 提供商：Moonshot AI")
            print("   • 特性：1万亿参数MoE, 128K上下文, SWE-Bench 65.8%")
        elif anthropic_api_key and anthropic_api_key.startswith('sk-ant-'):
            print("   • 当前配置：Claude API模式")
            print("   • 提供商：Anthropic")
            print("   • 计费：按token使用量")
            print("   • 特性：多模态能力, 高质量推理")
        else:
            print("   • 当前配置：Claude Pro模式 (默认)")
            print("   • 提供商：Anthropic")
            print("   • 计费：$20/月订阅")
            print("   • 特性：浏览器登录, 包月使用")
        
        print("\n💡 配置说明：")
        print("   • Claude Pro: 默认模式，使用您的$20/月订阅")
        print("   • 千问3-code: 备用API，使用 ANTHROPIC_BASE_URL + AUTH_TOKEN")
        print("   • Kimi K2: 备用API，使用 ANTHROPIC_BASE_URL + AUTH_TOKEN")
        print("   • 三种模式互斥，同时只能使用一种")
        
        print("\n💰 成本对比：")
        print("   • Claude Pro: $20/月固定 (推荐日常使用)")
        print("   • 千问3-code: 按量付费 (备用选择)")
        print("   • Kimi K2: $0.6/M输入, $2.5/M输出 (高性价比备用)")
    
    elif sub_choice == "5":
        # 测试当前引擎连接
        print("\n🧪 测试当前引擎连接...")
        try:
            # 这里可以添加实际的连接测试代码
            # 目前只显示配置状态，因为实际测试需要调用相应的API
            
            anthropic_api_key = os.getenv('ANTHROPIC_API_KEY', '')
            anthropic_base_url = os.getenv('ANTHROPIC_BASE_URL', '')
            anthropic_auth_token = os.getenv('ANTHROPIC_AUTH_TOKEN', '')
            
            if anthropic_base_url and anthropic_auth_token:
                if 'dashscope.aliyuncs.com' in anthropic_base_url:
                    print("🟡 千问3-code引擎配置检测")
                    print(f"   • Base URL: {anthropic_base_url}")
                    print(f"   • Auth Token: 已配置")
                    print("   • 模型: qwen3-code (1万亿参数MoE)")
                    print("   • 状态: 配置完整，建议手动测试")
                elif 'moonshot.ai' in anthropic_base_url:
                    print("🟡 Kimi K2引擎配置检测")
                    print(f"   • Base URL: {anthropic_base_url}")
                    print(f"   • Auth Token: 已配置")
                    print("   • 模型: kimi-k2 (1万亿参数MoE, 128K上下文)")
                    print("   • 定价: $0.6/M输入, $2.5/M输出")
                    print("   • 状态: 配置完整，建议手动测试")
                else:
                    print("🟡 未知引擎配置检测")
                    print(f"   • Base URL: {anthropic_base_url}")
                    print("   • 状态: 配置存在但引擎未识别")
            elif anthropic_api_key:
                print("🟡 Claude API模式配置检测")
                print("   • API Key: 已配置")
                print("   • 模型: claude-3.5-sonnet (多模态)")
                print("   • 计费: 按token使用量")
                print("   • 状态: 配置完整，建议手动测试")
            else:
                print("🟢 Claude Pro模式 (默认)")
                print("   • 认证: 浏览器登录")
                print("   • 模型: claude-3.5-sonnet")
                print("   • 计费: $20/月订阅")
                print("   • 状态: 默认模式，无需额外配置")
            
            print("\n💡 提示：")
            print("   • 完整的连接测试需要实际调用API")
            print("   • 可以通过运行内容生成功能来验证引擎")
            print("   • 如果遇到错误，请检查API密钥有效性")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    elif sub_choice == "6":
        # 重置引擎配置
        print("\n🔄 重置引擎配置...")
        print("⚠️  此操作将清除所有LLM引擎相关的环境变量")
        
        confirm = input("\n确认重置配置？(y/N): ").strip().lower()
        if confirm in ['y', 'yes']:
            try:
                # 清除所有相关环境变量
                env_vars_to_clear = ['ANTHROPIC_API_KEY', 'ANTHROPIC_BASE_URL', 'ANTHROPIC_AUTH_TOKEN']
                cleared_vars = []
                
                # 清除运行时环境变量
                for var in env_vars_to_clear:
                    if var in os.environ:
                        del os.environ[var]
                        cleared_vars.append(var)
                
                # 从.env文件中清除
                for var in env_vars_to_clear:
                    update_env_file(var, None)
                
                if cleared_vars:
                    print("✅ 配置重置完成")
                    print("📝 已清除的运行时环境变量：")
                    for var in cleared_vars:
                        print(f"   • {var}")
                else:
                    print("📋 没有需要清除的运行时配置")
                
                print("   • 📁 已从.env文件中移除相关配置")
                print("\n💡 引擎已恢复为默认Claude Pro模式")
                print("⚠️  建议：关闭并重新打开Claude Code终端以完全生效")
                pipeline.log("LLM引擎配置已重置，已持久化到.env文件", level="info", force=True)
                
            except Exception as e:
                print(f"❌ 重置失败: {e}")
                pipeline.log(f"LLM引擎配置重置失败: {e}", level="error", force=True)
        else:
            print("已取消重置操作")
    
    elif sub_choice == "7":
        # 生成WSL环境变量设置脚本
        print("\n🚀 生成WSL环境变量设置脚本")
        print("="*40)
        print("📋 功能说明：")
        print("   • 生成可在WSL命令行中执行的环境变量设置脚本")
        print("   • 解决Claude Code终端重启才能生效的问题")
        print("   • 支持所有引擎模式的快速切换")
        
        print("\n请选择要生成的脚本类型：")
        print("1. Claude Pro默认模式脚本")
        print("2. 千问3-code引擎脚本")
        print("3. Kimi K2引擎脚本")
        print("4. 生成所有脚本")
        print("0. 返回上级菜单")
        
        script_choice = input("\n请输入选项 (1-4/0): ").strip()
        
        if script_choice == "0":
            pass  # 返回上级菜单
        elif script_choice == "1":
            script_path = create_export_script("default")
            if script_path:
                print(f"✅ Claude Pro默认模式脚本已生成: {script_path}")
                print(f"💡 使用方法: source {script_path}")
                pipeline.log(f"生成Claude Pro模式WSL脚本: {script_path}", level="info", force=True)
        elif script_choice == "2":
            script_path = create_export_script("qwen")
            if script_path:
                # 为千问脚本创建单独文件
                qwen_script = Path(".tmp/set_qwen_env.sh")
                with open(script_path, 'r') as f:
                    content = f.read()
                with open(qwen_script, 'w') as f:
                    f.write(content)
                qwen_script.chmod(0o755)
                print(f"✅ 千问3-code引擎脚本已生成: {qwen_script}")
                print(f"💡 使用方法: source {qwen_script}")
                pipeline.log(f"生成千问3-code模式WSL脚本: {qwen_script}", level="info", force=True)
        elif script_choice == "3":
            script_path = create_export_script("kimi")
            if script_path:
                # 为Kimi脚本创建单独文件
                kimi_script = Path(".tmp/set_kimi_env.sh")
                with open(script_path, 'r') as f:
                    content = f.read()
                with open(kimi_script, 'w') as f:
                    f.write(content)
                kimi_script.chmod(0o755)
                print(f"✅ Kimi K2引擎脚本已生成: {kimi_script}")
                print(f"💡 使用方法: source {kimi_script}")
                pipeline.log(f"生成Kimi K2模式WSL脚本: {kimi_script}", level="info", force=True)
        elif script_choice == "4":
            # 生成所有脚本
            scripts = {}
            scripts['default'] = create_export_script("default")
            scripts['qwen'] = create_export_script("qwen")  
            scripts['kimi'] = create_export_script("kimi")
            
            # 创建单独的命名脚本
            if scripts['default']:
                default_script = Path(".tmp/set_claude_pro_env.sh")
                with open(scripts['default'], 'r') as f:
                    content = f.read()
                with open(default_script, 'w') as f:
                    f.write(content)
                default_script.chmod(0o755)
                scripts['default_named'] = default_script
                
            if scripts['qwen']:
                qwen_script = Path(".tmp/set_qwen_env.sh")
                with open(scripts['qwen'], 'r') as f:
                    content = f.read()
                with open(qwen_script, 'w') as f:
                    f.write(content)
                qwen_script.chmod(0o755)
                scripts['qwen_named'] = qwen_script
                
            if scripts['kimi']:
                kimi_script = Path(".tmp/set_kimi_env.sh")
                with open(scripts['kimi'], 'r') as f:
                    content = f.read()
                with open(kimi_script, 'w') as f:
                    f.write(content)
                kimi_script.chmod(0o755)
                scripts['kimi_named'] = kimi_script
            
            print("✅ 所有引擎脚本已生成完成")
            print("📁 脚本位置:")
            if scripts.get('default_named'):
                print(f"   • Claude Pro: {scripts['default_named']}")
            if scripts.get('qwen_named'):
                print(f"   • 千问3-code: {scripts['qwen_named']}")
            if scripts.get('kimi_named'):
                print(f"   • Kimi K2: {scripts['kimi_named']}")
            
            print("\n💡 使用方法:")
            print("   • 切换到Claude Pro: source .tmp/set_claude_pro_env.sh")
            print("   • 切换到千问3-code: source .tmp/set_qwen_env.sh")
            print("   • 切换到Kimi K2: source .tmp/set_kimi_env.sh")
            
            pipeline.log("生成所有LLM引擎WSL脚本", level="info", force=True)
        else:
            print("❌ 无效的选择")
    
    input("\n按Enter键返回主菜单...")


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
    """处理YouTube音频上传菜单"""
    print("\n" + "="*40)
    print("🎬 YouTube音频上传")
    print("="*40)
    print("📋 功能说明：")
    print("   • 扫描assets/audio/目录下的音频文件")
    print("   • 自动生成缩略图(音频+静态图片)")
    print("   • 上传到YouTube(不公开，通过链接访问)")
    print("   • 支持FFmpeg和MoviePy双重备用方案")
    
    # 检查OAuth配置状态
    try:
        from pathlib import Path
        credentials_file = Path("config/youtube_oauth_credentials.json")
        token_file = Path("config/youtube_oauth_token.json")
        
        # 检查OAuth文件是否存在且不是模板数据
        oauth_valid = False
        if credentials_file.exists() and token_file.exists():
            try:
                import json
                with open(token_file, 'r') as f:
                    token_data = json.load(f)
                # 检查是否为模板数据
                if token_data.get('token', '').startswith('your-oauth'):
                    oauth_status = "⚠️ 包含模板数据，需要重新认证"
                else:
                    oauth_status = "✅ 已配置"
                    oauth_valid = True
            except Exception:
                oauth_status = "❌ 文件损坏，需要重新配置"
        else:
            oauth_status = "❌ 需要配置"
            
        print(f"\n🔐 OAuth认证状态: {oauth_status}")
        
        if not oauth_valid:
            print("💡 请先完成OAuth认证配置:")
            print("   1. 查看文档: YOUTUBE_OAUTH_SETUP.md")
            print("   2. 或运行: python scripts/tools/youtube_oauth_setup.py")
            input("\n按Enter键返回主菜单...")
            return
            
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        input("\n按Enter键返回主菜单...")
        return
    
    print("\n请选择功能：")
    print("1. 上传音频文件到YouTube")
    print("2. 查看assets/audio目录文件")
    print("3. 检查配置状态")
    print("4. 使用说明")
    print("0. 返回主菜单")
    
    sub_choice = input("\n请输入选项 (1-4/0): ").strip()
    pipeline.log(f"YouTube音频上传 - 用户选择: {sub_choice}", level="info", force=True)
    
    if sub_choice == "1":
        # 上传音频文件到YouTube
        try:
            print("\n🎵 音频文件上传到YouTube")
            print("="*40)
            print("📋 功能说明：")
            print("   • 选择assets/audio目录中的音频文件")
            print("   • 自动添加封面图片并转换为视频")
            print("   • 上传到YouTube并获取链接")
            print("   • 可选择性集成到相关博文中")
            
            # 导入YouTube播客生成器
            from scripts.core.youtube_podcast_generator import YouTubePodcastGenerator
            
            # 获取配置
            generator_config = pipeline.config.get('youtube_podcast', {})
            generator = YouTubePodcastGenerator(generator_config, pipeline)
            
            # 执行完整的上传流程
            upload_result = generator.upload_audio_to_youtube()
            
            if upload_result and upload_result.get('success'):
                print("\n🎉 音频上传成功!")
                print(f"🔗 YouTube链接: {upload_result['youtube_url']}")
                
                # 询问是否要集成到博文
                integrate_choice = input("\n是否要将YouTube链接集成到相关博文中? (y/N): ").strip().lower()
                if integrate_choice in ['y', 'yes']:
                    if generator.integrate_youtube_link_to_post(upload_result):
                        print("✅ 博文集成成功!")
                    else:
                        print("⚠️ 博文集成失败或用户取消")
                else:
                    print("📋 您可以稍后手动添加YouTube链接到相关博文中")
                    print(f"🔗 链接: {upload_result['youtube_url']}")
                
                pipeline.log(f"音频上传成功: {upload_result['title']}", level="info", force=True)
            elif upload_result and upload_result.get('cancelled'):
                print("ℹ️ 用户取消操作")
                pipeline.log("用户取消音频上传操作", level="info", force=True)
            else:
                error_message = upload_result.get('message', '未知错误') if upload_result else '未知错误'
                print(f"❌ 音频上传失败: {error_message}")
                pipeline.log(f"音频上传失败: {error_message}", level="warning", force=True)
            
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            pipeline.log(f"YouTube音频上传异常: {e}", level="error", force=True)
            
    elif sub_choice == "2":
        # 查看assets/audio目录文件
        try:
            print("\n📁 查看音频文件列表")
            print("="*40)
            
            # 直接查看音频文件，无需依赖复杂配置
            from pathlib import Path
            
            audio_dir = Path("assets/audio")
            if not audio_dir.exists():
                print("❌ assets/audio目录不存在")
                return
            
            # 支持的音频格式
            audio_extensions = ['.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac']
            audio_files = []
            
            for ext in audio_extensions:
                audio_files.extend(audio_dir.glob(f"*{ext}"))
            
            # 按修改时间排序（最新的在前）
            audio_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            if not audio_files:
                print("❌ 未找到任何音频文件")
                print("💡 请确保assets/audio目录存在并包含音频文件")
            else:
                print(f"📊 找到 {len(audio_files)} 个音频文件:")
                from datetime import datetime
                for i, file_path in enumerate(audio_files, 1):
                    file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                    mod_time = datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
                    print(f"  {i}. {file_path.name}")
                    print(f"     大小: {file_size:.1f}MB | 修改时间: {mod_time}")
                    
                print(f"\n💡 如需上传，请选择选项1进行完整的上传流程")
            
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            pipeline.log(f"YouTube音频上传 - 查看文件失败: {e}", level="error", force=True)
            
    elif sub_choice == "3":
        # 检查配置状态
        try:
            print("\n🔍 配置状态检查")
            print("="*40)
            
            # 检查环境变量
            import os
            gemini_key = os.getenv('GEMINI_API_KEY')
            youtube_key = os.getenv('YOUTUBE_API_KEY')
            elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
            
            print("📊 API密钥配置状态:")
            print(f"   GEMINI_API_KEY: {'✅ 已配置' if gemini_key else '❌ 未配置'}")
            print(f"   YOUTUBE_API_KEY: {'✅ 已配置' if youtube_key else '❌ 未配置 (必需)'}")
            print(f"   ELEVENLABS_API_KEY: {'✅ 已配置' if elevenlabs_key else '⚠️  未配置 (可选)'}")
            
            # 检查OAuth认证文件（多个可能位置）
            oauth_credentials_paths = [
                Path("credentials.json"),
                Path("config/youtube_oauth_credentials.json")
            ]
            oauth_token_paths = [
                Path("token.json"), 
                Path("config/youtube_oauth_token.json")
            ]
            
            credentials_found = any(p.exists() for p in oauth_credentials_paths)
            token_found = any(p.exists() for p in oauth_token_paths)
            
            print(f"\n🔐 OAuth认证状态:")
            print(f"   credentials文件: {'✅ 存在' if credentials_found else '❌ 缺失'}")
            print(f"   token文件: {'✅ 存在' if token_found else '❌ 未认证'}")
            
            if credentials_found:
                for p in oauth_credentials_paths:
                    if p.exists():
                        print(f"     └─ 找到: {p}")
                        break
            if token_found:
                for p in oauth_token_paths:
                    if p.exists():
                        print(f"     └─ 找到: {p}")
                        break
            
            # 检查必要工具
            print(f"\n🛠️  系统工具状态:")
            try:
                import subprocess
                ffmpeg_result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
                print(f"   ffmpeg: {'✅ 可用' if ffmpeg_result.returncode == 0 else '❌ 不可用'}")
            except:
                print(f"   ffmpeg: ❌ 不可用")
            
            try:
                from PIL import Image
                print(f"   PIL (图片处理): ✅ 可用")
            except:
                print(f"   PIL (图片处理): ❌ 不可用")
            
            # 检查音频目录
            audio_dir = Path("assets/audio")
            if audio_dir.exists():
                audio_files = list(audio_dir.glob("*.mp3")) + list(audio_dir.glob("*.wav")) + list(audio_dir.glob("*.m4a"))
                print(f"\n📁 音频文件状态:")
                print(f"   assets/audio目录: ✅ 存在")
                print(f"   音频文件数量: {len(audio_files)} 个")
            else:
                print(f"\n📁 音频文件状态:")
                print(f"   assets/audio目录: ❌ 不存在")
            
            # 总体状态评估
            print(f"\n📋 系统就绪状态:")
            ready_status = []
            if youtube_key: ready_status.append("✅ YouTube API")
            else: ready_status.append("❌ YouTube API")
            
            if credentials_found and token_found: ready_status.append("✅ OAuth认证")
            else: ready_status.append("❌ OAuth认证")
            
            if audio_dir.exists(): ready_status.append("✅ 音频目录")
            else: ready_status.append("❌ 音频目录")
            
            print(f"   " + " | ".join(ready_status))
            
            if all("✅" in status for status in ready_status):
                print(f"\n🎉 系统配置完整，可以开始上传音频文件！")
            else:
                print(f"\n⚠️  请根据上述检查结果完善系统配置")
                if not credentials_found:
                    print(f"   💡 OAuth credentials文件缺失，请配置Google Cloud OAuth凭据")
                if not token_found:
                    print(f"   💡 OAuth token文件缺失，首次运行时会自动生成")
            
        except Exception as e:
            print(f"❌ 配置检查失败: {e}")
            pipeline.log(f"YouTube音频上传 - 配置检查失败: {e}", level="error", force=True)
            
    elif sub_choice == "4":
        # 使用说明
        print("\n📖 YouTube音频上传使用说明")
        print("="*50)
        print("🎯 功能概述:")
        print("   • 选择assets/audio目录中的音频文件")
        print("   • 自动添加封面图片并转换为视频")
        print("   • 上传到YouTube并获取分享链接")
        print("   • 可选择性集成到相关博文中")
        
        print("\n🔧 系统要求:")
        print("   • Google Cloud项目已创建")
        print("   • YouTube Data API v3已启用")
        print("   • OAuth2凭据已配置 (credentials.json)")
        print("   • ffmpeg工具可用于音视频处理")
        print("   • (可选) PIL库用于图片处理")
        
        print("\n📋 使用流程:")
        print("   1. 确保配置完整 (选择选项3检查)")
        print("   2. 将音频文件放在assets/audio/目录")
        print("   3. 运行选项1开始上传流程")
        print("   4. 选择要上传的音频文件")
        print("   5. 选择或生成封面图片")
        print("   6. 填写视频标题和描述")
        print("   7. 确认上传并等待处理完成")
        print("   8. 可选择将YouTube链接集成到博文")
        
        print("\n🖼️ 封面图片选项:")
        print("   • 默认播客封面: 自动生成带标题的封面")
        print("   • 现有图片: 从assets/images选择")
        print("   • 纯色背景: 简单的纯色封面")
        
        print("\n🎯 支持格式:")
        print("   • 输入音频: MP3, WAV, M4A, AAC, OGG, FLAC")
        print("   • 输出视频: MP4 (720p)")
        print("   • 封面图片: JPG (720x720)")
        
        print("\n🔗 博文集成功能:")
        print("   • 自动识别相关博文")
        print("   • 智能匹配音频文件名和博文标题")
        print("   • 生成完整的YouTube嵌入代码")
        print("   • 在合适位置插入播客区块")
        
        print("\n💡 最佳实践:")
        print("   • 音频文件命名要有意义")
        print("   • 提供准确的视频标题和描述")
        print("   • 选择与内容相关的封面图片")
        print("   • 上传后及时将链接添加到博文")
        
        print("\n⚠️  注意事项:")
        print("   • 首次使用需要完成OAuth认证")
        print("   • 上传的视频默认为不公开")
        print("   • 请遵守YouTube社区准则")
        print("   • 处理大文件可能需要较长时间")
        
    elif sub_choice == "0":
        return
    else:
        print("❌ 无效的选择，请重新输入")
    
    input("\n按Enter键继续...")


# ========================================
# 会员管理系统处理函数
# ========================================

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


if __name__ == "__main__":
    main() 