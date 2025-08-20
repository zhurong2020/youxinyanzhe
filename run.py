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
            
            if published_platforms and set(published_platforms) >= set(all_enabled_platforms):
                print(f"\n✅ 文章 '{article_name}' 已在所有启用的平台发布完成")
                print(f"📊 已发布平台: {', '.join(published_platforms)}")
                pipeline.log(f"文章已在所有平台发布完成: {article_name}", level="info", force=True)
            else:
                print(f"\n🤔 未选择任何发布平台")
                pipeline.log("用户未选择发布平台", level="info", force=True)
            continue  # 返回主菜单
        
        # 询问是否启用内容变现功能
        enable_monetization = pipeline.ask_monetization_preference()
        pipeline.log(f"内容变现功能: {'启用' if enable_monetization else '跳过'}", level="info", force=True)
        
        # 选择会员分级
        member_tier = pipeline.select_member_tier() if enable_monetization else None
        if member_tier:
            pipeline.log(f"会员分级: {member_tier}", level="info", force=True)
        else:
            pipeline.log("跳过会员分级设置", level="info", force=True)
        
        # 执行发布流程
        pipeline.log(f"开始发布到平台: {', '.join(platforms)}", level="info", force=True)
        try:
            result = pipeline.process_draft(draft, platforms, enable_monetization=enable_monetization, member_tier=member_tier)
            
            # 处理返回结果（兼容字典格式）
            if isinstance(result, dict):
                success = result.get('success', False)
            else:
                # 兼容可能的布尔值返回
                success = bool(result)
                
            if success:
                pipeline.log(f"✅ 发布成功完成: {draft.name}", level="info", force=True)
            else:
                pipeline.log(f"❌ 发布过程中出现问题: {draft.name}", level="warning", force=True)
        except Exception as e:
            pipeline.log(f"❌ 发布过程中发生错误: {str(e)}", level="error", force=True)
            print(f"\n❌ 发布过程中发生错误: {str(e)}")


def run_shell_command(cmd, description="Command", timeout=300, check_result=True):
    """
    运行shell命令的辅助函数
    
    Args:
        cmd: 命令列表或字符串
        description: 命令描述
        timeout: 超时时间（秒）
        check_result: 是否检查执行结果
    
    Returns:
        subprocess.CompletedProcess对象
    """
    # 临时导入，避免循环依赖
    pipeline = ContentPipeline("config/pipeline_config.yml", verbose=False)
    
    try:
        pipeline.log(f"执行命令: {description}", level="info", force=True)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=check_result
        )
        
        if result.stdout:
            pipeline.log(f"命令输出: {result.stdout[:500]}", level="info", force=True)
        if result.stderr:
            pipeline.log(f"命令错误: {result.stderr[:500]}", level="warning", force=True)
        
        return result
        
    except subprocess.TimeoutExpired:
        pipeline.log(f"执行超时: {description}", level="error", force=True)
        return subprocess.CompletedProcess(cmd, -1, "", "执行超时")
    except Exception as e:
        pipeline.log(f"执行异常: {description} - {str(e)}", level="error", force=True)
        return subprocess.CompletedProcess(cmd, -1, "", str(e))


if __name__ == "__main__":
    main()