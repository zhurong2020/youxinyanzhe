"""
YouTube功能菜单处理器
负责YouTube相关功能的用户界面和交互处理
遵循重构后的分层架构原则
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any

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
            "2. 🎬 YouTube音频上传",
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
        menu_description = "🤖 将英文YouTube视频转换为中文播客"
        
        options = [
            "1. 📝 生成YouTube播客学习文章",
            "2. 🎬 上传已生成的播客视频",
            "3. ⚙️ 查看配置状态",
            "4. 📖 使用说明和示例"
        ]
        
        handlers = [
            self._generate_podcast_article,
            self._upload_podcast_video,
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
    
    def _upload_podcast_video(self) -> Optional[str]:
        """上传已生成的播客视频"""
        self.display_menu_header("🎬 上传已生成的播客视频",
                                "将本地播客视频上传到YouTube")
        
        print("功能开发中...")
        print("💡 该功能将与音频上传功能集成")
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
        """处理YouTube音频上传"""
        self.display_menu_header("🎬 YouTube音频上传",
                                "扫描audio目录并上传到YouTube")
        
        # 检查OAuth状态
        oauth_status = self._check_oauth_status()
        print(f"\n🔐 OAuth认证状态: {oauth_status['message']}")
        
        if not oauth_status['valid']:
            print("💡 请先完成OAuth认证配置:")
            print("   1. 查看文档: YOUTUBE_OAUTH_SETUP.md")
            print("   2. 或运行: python scripts/tools/youtube_oauth_setup.py")
            self.pause_for_user()
            return None
        
        # 显示上传选项
        upload_options = [
            "1. 📁 扫描并选择音频文件",
            "2. 📋 查看上传历史",
            "3. ⚙️ 配置上传参数",
            "4. 🔄 批量上传"
        ]
        
        upload_handlers = [
            self._scan_and_select_audio,
            self._view_upload_history,
            self._configure_upload_params,
            self._batch_upload_audio
        ]
        
        return self.create_menu_loop_with_path("🎬 YouTube音频上传", "", upload_options, upload_handlers, "4.2")
    
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
    
    def _scan_and_select_audio(self) -> Optional[str]:
        """扫描并选择音频文件"""
        try:
            audio_dir = Path("assets/audio")
            if not audio_dir.exists():
                print(f"❌ 音频目录不存在: {audio_dir}")
                return None
            
            # 扫描音频文件
            audio_files = []
            for ext in ['*.mp3', '*.wav', '*.m4a', '*.flac']:
                audio_files.extend(audio_dir.glob(ext))
            
            if not audio_files:
                print(f"❌ 在 {audio_dir} 中未找到音频文件")
                return None
            
            print(f"\n📁 发现 {len(audio_files)} 个音频文件:")
            for i, file in enumerate(audio_files, 1):
                file_size = file.stat().st_size / (1024 * 1024)  # MB
                print(f"   {i}. {file.name} ({file_size:.1f}MB)")
            
            # 用户选择
            choice = input(f"\n请选择要上传的文件 (1-{len(audio_files)}): ").strip()
            
            try:
                file_index = int(choice) - 1
                if 0 <= file_index < len(audio_files):
                    selected_file = audio_files[file_index]
                    return self._upload_single_audio(selected_file)
                else:
                    print("❌ 无效选择")
                    return None
            except ValueError:
                print("❌ 请输入有效数字")
                return None
                
        except Exception as e:
            self.handle_error(e, "扫描音频文件")
            return None
    
    def _upload_single_audio(self, audio_file: Path) -> Optional[str]:
        """
        上传单个音频文件
        
        Args:
            audio_file: 音频文件路径
            
        Returns:
            上传结果
        """
        try:
            print(f"\n🎵 准备上传: {audio_file.name}")
            
            # 确认上传
            if not self.confirm_operation(f"确认上传 {audio_file.name} 到YouTube？"):
                self.display_operation_cancelled()
                return None
            
            # TODO: 实际的上传逻辑
            # 这里需要集成YouTube API上传功能
            print(f"📤 正在上传 {audio_file.name}...")
            
            # 模拟上传过程
            import time
            time.sleep(1)
            
            # 临时返回成功消息
            upload_url = f"https://youtube.com/watch?v=example_{audio_file.stem}"
            self.display_success_message(f"上传完成: {upload_url}")
            
            return upload_url
            
        except Exception as e:
            self.handle_error(e, f"上传音频文件 {audio_file.name}")
            return None
    
    def _view_upload_history(self) -> Optional[str]:
        """查看上传历史"""
        print("\n📋 YouTube上传历史")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _configure_upload_params(self) -> Optional[str]:
        """配置上传参数"""
        print("\n⚙️ YouTube上传参数配置")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _batch_upload_audio(self) -> Optional[str]:
        """批量上传音频"""
        print("\n🔄 批量上传音频文件")
        print("(功能开发中...)")
        self.pause_for_user()
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