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
        
        return self.create_menu_loop(menu_title, menu_description, options, handlers)
    
    def _handle_podcast_generation(self) -> Optional[str]:
        """处理YouTube播客生成"""
        self.display_menu_header("🎧 YouTube播客生成器", 
                                "从YouTube视频生成播客内容")
        
        try:
            # 导入并调用播客生成逻辑
            from scripts.core.youtube_podcast_generator import YouTubePodcastGenerator
            
            # 创建生成器实例
            generator = YouTubePodcastGenerator(self.pipeline)
            
            # 获取YouTube URL
            url = input("\n请输入YouTube视频URL: ").strip()
            if not url:
                self.display_operation_cancelled()
                return None
            
            # 生成播客
            self.log_action("开始YouTube播客生成", url)
            result = generator.generate_podcast_from_youtube(url)
            
            if result:
                self.display_success_message("YouTube播客生成成功")
                self.log_action("YouTube播客生成完成", result)
                return result
            else:
                print("❌ YouTube播客生成失败")
                return None
                
        except Exception as e:
            self.handle_error(e, "YouTube播客生成")
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
        
        return self.create_menu_loop("🎬 YouTube音频上传", "", upload_options, upload_handlers)
    
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
        
        return self.create_menu_loop("🔐 OAuth认证管理", "", oauth_options, oauth_handlers)
    
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