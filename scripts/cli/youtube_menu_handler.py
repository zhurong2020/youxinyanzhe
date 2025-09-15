"""
YouTube功能菜单处理器
负责YouTube相关功能的用户界面和交互处理
遵循重构后的分层架构原则
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from scripts.cli.base_menu_handler import BaseMenuHandler
from scripts.core.content_pipeline import ContentPipeline


class YouTubeMenuHandler(BaseMenuHandler):
    """YouTube功能菜单处理器"""
    
    def __init__(self, pipeline: ContentPipeline):
        """
        初始化YouTube菜单处理器
        
        Args:
            pipeline: 内容管道实例
        """
        super().__init__(pipeline, "YouTube管理")
        self.credentials_file = Path("config/youtube_oauth_credentials.json")
        self.token_file = Path("config/youtube_oauth_token.json")
    
    def handle_youtube_processing_menu(self) -> Optional[str]:
        """
        处理YouTube内容处理主菜单
        
        Returns:
            处理结果或None
        """
        menu_title = "🎬 YouTube内容处理"
        menu_description = "📺 视频→文章→音频→上传的完整工作流程"
        
        options = [
            "1. 🎧 YouTube播客生成器",
            "2. 🎬 YouTube视频生成与上传",
            "3. 🔐 YouTube OAuth认证管理"
        ]
        
        handlers = [
            self._handle_podcast_generation,
            self._handle_audio_upload,
            self._handle_oauth_management
        ]
        
        return self.create_menu_loop_with_path(menu_title, menu_description, options, handlers, "4")
    
    def handle_youtube_podcast_menu(self) -> Optional[str]:
        """
        处理YouTube播客生成器独立菜单
        
        Returns:
            处理结果或None
        """
        return self._handle_podcast_generation()
    
    def _handle_podcast_generation(self) -> Optional[str]:
        """处理YouTube播客生成详细菜单"""
        menu_title = "🎧 YouTube播客生成器"
        menu_description = "🤖 将英文YouTube视频转换为中文播客文章"

        options = [
            "1. 📝 生成YouTube播客学习文章",
            "2. ⚙️ 查看配置状态",
            "3. 📖 使用说明和示例"
        ]

        handlers = [
            self._generate_podcast_article,
            self._check_podcast_config,
            self._show_podcast_usage
        ]

        return self.create_menu_loop_with_path(menu_title, menu_description, options, handlers, "4.1")
    
    def _generate_podcast_article(self) -> Optional[str]:
        """生成YouTube播客学习文章"""
        self.display_menu_header("📝 生成YouTube播客学习文章",
                                "将英文YouTube视频转换为中文播客文章")
        
        print("📋 功能说明：")
        print("   • 自动生成学习导读和Jekyll文章")
        print("   • 专为英语学习和全球视野系列设计")
        print("⚠️  前提条件：")
        print("   • 需要配置GEMINI_API_KEY (用于内容生成)")
        print("   • 可选配置YOUTUBE_API_KEY (用于视频信息获取)")
        print("   • 确保网络连接正常访问Podcastfy服务")
        
        try:
            # 获取YouTube URL
            youtube_url = input("\n请输入YouTube视频链接: ").strip()
            if not youtube_url:
                self.display_operation_cancelled()
                return None
            
            # 验证YouTube链接格式
            if "youtube.com/watch" not in youtube_url and "youtu.be/" not in youtube_url:
                print("❌ 请输入有效的YouTube视频链接")
                return None
            
            # 导入并调用播客生成逻辑
            from scripts.core.youtube_podcast_generator import YouTubePodcastGenerator
            
            # 创建生成器实例
            config = {}  # 使用默认配置
            generator = YouTubePodcastGenerator(config, self.pipeline)
            
            # 生成播客文章
            self.log_action("开始YouTube播客文章生成", youtube_url)
            print(f"\n🚀 正在处理视频: {youtube_url}")
            
            result = generator.generate_podcast_from_youtube(youtube_url)
            
            if result:
                self.display_success_message("YouTube播客文章生成成功")
                self.log_action("YouTube播客文章生成完成", result)
                print(f"📝 文章已保存: {result}")
                return result
            else:
                print("❌ YouTube播客文章生成失败")
                return None
                
        except Exception as e:
            self.handle_error(e, "YouTube播客文章生成")
            return None
    
    def _quick_generate_and_upload(self) -> Optional[str]:
        """YouTube视频生成与上传"""
        self.display_menu_header("🎬 YouTube视频生成与上传",
                                "将音频文件转换为视频并上传到YouTube")

        print("🎬 YouTube视频生成与上传工具")
        print("支持音频转视频、图片选择、音频压缩和上传管理")

        try:
            from scripts.tools.youtube.youtube_video_generator import YouTubeVideoGenerator
            from scripts.tools.youtube.youtube_video_enhanced import YouTubeVideoEnhanced

            # 初始化视频生成器
            generator = YouTubeVideoGenerator()
            enhanced = YouTubeVideoEnhanced(generator)

            # 显示主菜单
            while True:
                print("\n🔧 YouTube视频处理选项:")
                print("1. 扫描音频文件")
                print("2. 单个视频生成（增强版，可选择图片）")
                print("3. 批量视频生成")
                print("4. 查看输出目录")
                print("5. 清理输出文件")
                print("0. 返回上级菜单")

                try:
                    choice = int(input("\n请选择操作: "))

                    if choice == 1:  # 扫描音频文件
                        generator.handle_scan_audio()

                    elif choice == 2:  # 单个视频生成（增强版）
                        # 先扫描音频文件
                        audio_files = generator.scan_audio_files()
                        if not audio_files:
                            print("❌ 未找到音频文件")
                            continue

                        # 显示音频文件列表
                        print(f"\n📁 找到 {len(audio_files)} 个音频文件:")
                        for i, file_info in enumerate(audio_files[:20], 1):
                            size_mb = file_info['size'] / (1024 * 1024)
                            print(f"{i:2d}. {file_info['name']} ({size_mb:.1f}MB)")

                        if len(audio_files) > 20:
                            print(f"... 还有 {len(audio_files) - 20} 个文件未显示")

                        # 选择音频文件
                        try:
                            file_choice = input(f"\n请选择音频文件 (1-{min(20, len(audio_files))}): ").strip()
                            if not file_choice.isdigit() or not (1 <= int(file_choice) <= min(20, len(audio_files))):
                                print("❌ 无效选择")
                                continue

                            selected_audio = audio_files[int(file_choice) - 1]
                            # 使用增强版生成器
                            enhanced.generate_video_interactive(selected_audio)

                        except ValueError:
                            print("❌ 请输入有效数字")

                    elif choice == 3:  # 批量视频生成
                        generator.handle_batch_generation()

                    elif choice == 4:  # 查看输出目录
                        generator.handle_view_output()

                    elif choice == 5:  # 清理输出文件
                        generator.handle_cleanup()

                    elif choice == 0:  # 返回
                        break

                    else:
                        print("❌ 选择无效，请输入1-5或0返回")

                except ValueError:
                    print("❌ 请输入有效的数字")
                except KeyboardInterrupt:
                    print("\n⚠️ 用户中断操作")
                    break
                except Exception as e:
                    print(f"❌ 操作失败: {e}")

                input("\n按Enter键继续...")

        except ImportError as e:
            print(f"❌ 无法导入YouTube视频生成器: {e}")
            print("💡 请确保scripts/tools/youtube/youtube_video_generator.py文件存在")
        except Exception as e:
            print(f"❌ YouTube视频处理时出错: {e}")

        self.pause_for_user()
        return None
    
    def _check_podcast_config(self) -> Optional[str]:
        """查看播客配置状态"""
        self.display_menu_header("⚙️ 播客配置状态",
                                "检查播客生成所需的配置项")
        
        import os
        
        print("🔍 环境配置检查:")
        
        # 检查必需的API密钥
        config_items = [
            ("GEMINI_API_KEY", "Google Gemini API密钥", True),
            ("YOUTUBE_API_KEY", "YouTube API密钥", False),
            ("ELEVENLABS_API_KEY", "ElevenLabs API密钥", False)
        ]
        
        missing_required = []
        for env_var, description, required in config_items:
            value = os.getenv(env_var)
            status = "✅ 已配置" if value else ("❌ 未配置" if required else "⚠️ 未配置(可选)")
            print(f"   {status} {description}")
            
            if required and not value:
                missing_required.append(env_var)
        
        if missing_required:
            print(f"\n⚠️ 缺少必需配置项: {', '.join(missing_required)}")
            print("💡 请在 .env 文件中配置这些环境变量")
        else:
            print("\n✅ 所有必需的配置项都已设置")
        
        # 检查网络连接
        print("\n🌐 网络连接检查:")
        try:
            import requests
            response = requests.get("https://www.youtube.com", timeout=5)
            if response.status_code == 200:
                print("   ✅ YouTube访问正常")
            else:
                print("   ⚠️ YouTube访问异常")
        except:
            print("   ❌ 网络连接问题")
        
        self.pause_for_user()
        return None
    
    def _show_podcast_usage(self) -> Optional[str]:
        """显示播客功能使用说明"""
        self.display_menu_header("📖 播客功能使用说明",
                                "详细的使用指南和示例")
        
        usage_guide = """
==================================================
🎧 YouTube播客生成器 - 使用指南
==================================================

🎯 功能概述:
  • 将英文YouTube视频转换为中文播客文章
  • 自动生成学习导读和Jekyll格式文章
  • 专为英语学习和全球视野内容设计

📋 使用步骤:
  1. 确保环境配置完整(GEMINI_API_KEY等)
  2. 选择"生成YouTube播客学习文章"
  3. 输入YouTube视频链接
  4. 等待处理完成(通常需要2-5分钟)
  5. 检查生成的文章文件

🔧 环境配置:
  • GEMINI_API_KEY: 必需，用于AI内容生成
  • YOUTUBE_API_KEY: 可选，用于获取视频元数据
  • 网络访问: 需要访问YouTube和Podcastfy服务

📝 支持的视频类型:
  • 英文教育内容视频
  • TED演讲、学术讲座
  • 新闻分析、文化交流内容
  • 技术教程和行业分享

⚠️ 注意事项:
  • 视频长度建议在5-60分钟之间
  • 确保视频有清晰的英文音频
  • 生成过程需要稳定的网络连接
  • 生成的内容需要人工审核和润色

💡 最佳实践:
  • 选择高质量的教育内容视频
  • 定期检查API配额使用情况
  • 保存生成的文章到合适的分类目录
  • 根据需要调整文章格式和内容
        """
        
        print(usage_guide)
        self.pause_for_user()
        return None
    
    def _handle_audio_upload(self) -> Optional[str]:
        """YouTube视频生成与上传"""
        self.display_menu_header("🎬 YouTube视频生成与上传",
                                "将音频文件转换为视频并上传到YouTube")

        # 检查OAuth状态
        oauth_status = self._check_oauth_status()
        print(f"\n🔐 OAuth认证状态: {oauth_status['message']}")

        if not oauth_status['valid']:
            print("💡 请先完成OAuth认证配置:")
            print("   1. 通过主菜单 → 4 → 3 配置OAuth")
            print("   2. 或运行: python scripts/tools/youtube_oauth_setup.py")
            self.pause_for_user()
            return None

        # 显示视频生成与上传选项
        upload_options = [
            "1. 🚀 快速生成并上传（单个文件）",
            "2. 🔄 批量处理音频文件",
            "3. 📋 查看上传历史",
            "4. ⚙️ 配置上传参数",
            "5. 🗂️ 管理输出文件"
        ]

        upload_handlers = [
            self._quick_generate_and_upload,
            self._batch_process_audio,
            self._view_upload_history,
            self._configure_upload_params,
            self._manage_output_files
        ]

        return self.create_menu_loop_with_path("🎬 YouTube视频生成与上传",
                                              "音频文件 → 视频 → YouTube",
                                              upload_options, upload_handlers, "4.2")
    
    def _handle_oauth_management(self) -> Optional[str]:
        """处理OAuth认证管理"""
        self.display_menu_header("🔐 YouTube OAuth认证管理",
                                "管理YouTube API认证配置")
        
        # 显示当前OAuth状态
        oauth_status = self._check_oauth_status()
        print(f"\n当前状态: {oauth_status['message']}")
        
        if oauth_status['valid']:
            print(f"认证文件: {self.credentials_file}")
            print(f"令牌文件: {self.token_file}")
        
        oauth_options = [
            "1. 🔍 检查OAuth状态",
            "2. 🔧 重新配置OAuth",
            "3. 🗑️ 清除OAuth配置",
            "4. 📋 显示配置指南"
        ]
        
        oauth_handlers = [
            self._check_oauth_detailed,
            self._reconfigure_oauth,
            self._clear_oauth_config,
            self._show_oauth_guide
        ]
        
        return self.create_menu_loop_with_path("🔐 OAuth认证管理", "", oauth_options, oauth_handlers, "4.3")
    
    def _check_oauth_status(self) -> Dict[str, Any]:
        """
        检查OAuth配置状态
        
        Returns:
            包含状态信息的字典
        """
        try:
            if not (self.credentials_file.exists() and self.token_file.exists()):
                return {
                    'valid': False,
                    'message': "❌ 需要配置",
                    'details': "OAuth文件不存在"
                }
            
            # 检查token文件内容
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
            
            # 检查是否为模板数据
            if token_data.get('token', '').startswith('your-oauth'):
                return {
                    'valid': False,
                    'message': "⚠️ 包含模板数据，需要重新认证",
                    'details': "Token文件包含示例数据"
                }
            
            return {
                'valid': True,
                'message': "✅ 已配置",
                'details': "OAuth配置正常"
            }
            
        except Exception as e:
            return {
                'valid': False,
                'message': "❌ 文件损坏，需要重新配置",
                'details': str(e)
            }
    
    
    def _view_upload_history(self) -> Optional[str]:
        """查看上传历史"""
        try:
            from pathlib import Path
            import json
            
            print("\n📋 YouTube上传历史")
            print("="*40)
            
            # 检查上传记录文件
            upload_log = Path(".tmp/youtube_uploads/upload_history.json")
            temp_dir = Path(".tmp/youtube_uploads")
            
            if upload_log.exists():
                try:
                    with open(upload_log, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                    
                    if history:
                        print(f"🎥 共找到 {len(history)} 条上传记录:")
                        
                        # 显示最近10条记录
                        for i, record in enumerate(history[-10:], 1):
                            upload_time = record.get('upload_time', '未知')
                            filename = record.get('filename', '未知文件')
                            video_url = record.get('video_url', '')
                            status = record.get('status', '未知')
                            
                            status_emoji = "✅" if status == 'success' else "❌"
                            print(f"   {i}. {status_emoji} {filename}")
                            print(f"      时间: {upload_time}")
                            if video_url:
                                print(f"      链接: {video_url}")
                            print()
                    else:
                        print("📄 上传记录为空")
                        
                except json.JSONDecodeError:
                    print("❌ 无法解析上传记录文件")
            else:
                print("📄 暂无上传记录")
                
            # 检查临时文件
            if temp_dir.exists():
                temp_files = list(temp_dir.glob("*.mp4")) + list(temp_dir.glob("*.avi"))
                if temp_files:
                    print(f"\n📁 临时视频文件 ({len(temp_files)} 个):")
                    for temp_file in temp_files[-5:]:
                        print(f"   • {temp_file.name}")
            
            self.pause_for_user()
            return "上传历史查看完成"
            
        except Exception as e:
            self.handle_error(e, "查看上传历史")
            return None
    
    def _configure_upload_params(self) -> Optional[str]:
        """配置上传参数"""
        try:
            from pathlib import Path
            import json
            
            print("\n⚙️ YouTube上传参数配置")
            print("="*40)
            
            config_file = Path("config/youtube_upload_config.json")
            
            # 默认配置
            default_config = {
                "title_template": "{filename} - 有心工坊音频",
                "description_template": "来自有心工坊的优质音频内容\n\n访问我们: https://youxinyanzhe.github.io",
                "tags": ["教育", "学习", "有心工坊"],
                "privacy": "public",
                "category": "22",  # People & Blogs
                "thumbnail_default": "assets/images/default_thumbnail.jpg"
            }
            
            # 加载现有配置
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        current_config = json.load(f)
                except:
                    current_config = default_config
            else:
                current_config = default_config
            
            print("📄 当前配置:")
            for key, value in current_config.items():
                if isinstance(value, list):
                    print(f"   {key}: {', '.join(value)}")
                else:
                    print(f"   {key}: {value}")
            
            # 配置菜单
            while True:
                print("\n可修改的选项:")
                print("1. 📝 修改标题模板")
                print("2. 📄 修改描述模板")
                print("3. 🏷️ 修改标签")
                print("4. 🔒 修改隐私设置")
                print("5. 💾 保存配置")
                print("0. 返回")
                
                choice = input("\n请选择 (0-5): ").strip()
                
                if choice == "0":
                    break
                elif choice == "1":
                    new_title = input(f"输入新标题模板 (当前: {current_config['title_template']}): ").strip()
                    if new_title:
                        current_config['title_template'] = new_title
                        print("✅ 标题模板已更新")
                elif choice == "2":
                    print("输入新描述模板 (空行结束):")
                    description_lines = []
                    while True:
                        line = input()
                        if not line:
                            break
                        description_lines.append(line)
                    if description_lines:
                        current_config['description_template'] = '\n'.join(description_lines)
                        print("✅ 描述模板已更新")
                elif choice == "3":
                    tags_input = input(f"输入标签 (逗号分隔, 当前: {', '.join(current_config['tags'])}): ").strip()
                    if tags_input:
                        current_config['tags'] = [tag.strip() for tag in tags_input.split(',')]
                        print("✅ 标签已更新")
                elif choice == "4":
                    print("选择隐私设置:")
                    print("1. public (公开)")
                    print("2. unlisted (不公开列表)")
                    print("3. private (私人)")
                    privacy_choice = input("选择 (1-3): ").strip()
                    privacy_map = {"1": "public", "2": "unlisted", "3": "private"}
                    if privacy_choice in privacy_map:
                        current_config['privacy'] = privacy_map[privacy_choice]
                        print("✅ 隐私设置已更新")
                elif choice == "5":
                    # 保存配置
                    config_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(config_file, 'w', encoding='utf-8') as f:
                        json.dump(current_config, f, indent=2, ensure_ascii=False)
                    print(f"✅ 配置已保存到 {config_file}")
                    return "上传参数配置完成"
            
            return None
            
        except Exception as e:
            self.handle_error(e, "配置上传参数")
            return None
    
    def _batch_process_audio(self) -> Optional[str]:
        """批量处理音频文件"""
        try:
            from scripts.tools.youtube.youtube_video_generator import YouTubeVideoGenerator

            print("\n🔄 批量处理音频文件")
            print("="*40)

            generator = YouTubeVideoGenerator()
            generator.handle_batch_generation()

            self.pause_for_user()
            return "批量处理完成"

        except Exception as e:
            self.handle_error(e, "批量处理音频")
            return None

    def _manage_output_files(self) -> Optional[str]:
        """管理输出文件"""
        try:
            from scripts.tools.youtube.youtube_video_generator import YouTubeVideoGenerator

            print("\n🗂️ 管理输出文件")
            print("="*40)

            generator = YouTubeVideoGenerator()

            while True:
                print("\n选择操作:")
                print("1. 📋 查看输出目录")
                print("2. 🧹 清理输出文件")
                print("0. 返回")

                choice = input("\n请选择 (0-2): ").strip()

                if choice == "1":
                    generator.handle_view_output()
                elif choice == "2":
                    generator.handle_cleanup()
                elif choice == "0":
                    break
                else:
                    print("❌ 无效选择")

                if choice != "0":
                    input("\n按Enter键继续...")

            return None

        except Exception as e:
            self.handle_error(e, "管理输出文件")
            return None
    
    def _check_oauth_detailed(self) -> Optional[str]:
        """详细检查OAuth状态"""
        oauth_status = self._check_oauth_status()
        
        print(f"\n🔍 OAuth配置详细状态:")
        print(f"   状态: {oauth_status['message']}")
        print(f"   详情: {oauth_status['details']}")
        print(f"   凭据文件: {self.credentials_file} ({'存在' if self.credentials_file.exists() else '不存在'})")
        print(f"   令牌文件: {self.token_file} ({'存在' if self.token_file.exists() else '不存在'})")
        
        self.pause_for_user()
        return None
    
    def _reconfigure_oauth(self) -> Optional[str]:
        """重新配置OAuth"""
        print("\n🔧 重新配置OAuth认证")
        print("请运行以下命令进行配置:")
        print("   python scripts/tools/youtube_oauth_setup.py")
        self.pause_for_user()
        return None
    
    def _clear_oauth_config(self) -> Optional[str]:
        """清除OAuth配置"""
        if not self.confirm_operation("确认清除所有OAuth配置文件？"):
            self.display_operation_cancelled()
            return None
        
        try:
            if self.credentials_file.exists():
                self.credentials_file.unlink()
                print(f"✅ 已删除: {self.credentials_file}")
            
            if self.token_file.exists():
                self.token_file.unlink()
                print(f"✅ 已删除: {self.token_file}")
            
            self.display_success_message("OAuth配置已清除")
            
        except Exception as e:
            self.handle_error(e, "清除OAuth配置")
        
        return None
    
    def _show_oauth_guide(self) -> Optional[str]:
        """显示OAuth配置指南"""
        print("\n📋 YouTube OAuth配置指南")
        print("="*40)
        print("1. 前往 Google Cloud Console")
        print("2. 创建新项目或选择现有项目")
        print("3. 启用 YouTube Data API v3")
        print("4. 创建OAuth 2.0凭据")
        print("5. 下载凭据文件并重命名为 youtube_oauth_credentials.json")
        print("6. 运行配置脚本: python scripts/tools/youtube_oauth_setup.py")
        print("\n详细文档: docs/YOUTUBE_OAUTH_SETUP.md")
        
        self.pause_for_user()
        return None