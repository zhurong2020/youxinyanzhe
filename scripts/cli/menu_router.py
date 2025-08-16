"""
菜单路由器模块
统一管理所有菜单功能的路由和委托
"""
from typing import Optional
from scripts.core.content_pipeline import ContentPipeline


class MenuRouter:
    """菜单路由器 - 统一管理菜单功能分发"""
    
    def __init__(self, pipeline: ContentPipeline):
        """
        初始化菜单路由器
        
        Args:
            pipeline: 内容管道实例
        """
        self.pipeline = pipeline
        self._handlers = {}
        self._initialize_handlers()
    
    def _initialize_handlers(self) -> None:
        """初始化所有菜单处理器"""
        # 延迟导入避免循环依赖
        from scripts.cli.content_menu_handler import ContentMenuHandler
        from scripts.cli.youtube_menu_handler import YouTubeMenuHandler
        from scripts.cli.vip_menu_handler import VIPMenuHandler
        from scripts.cli.system_menu_handler import SystemMenuHandler
        
        # 注册处理器
        self._handlers['content'] = ContentMenuHandler(self.pipeline)
        self._handlers['youtube'] = YouTubeMenuHandler(self.pipeline)
        self._handlers['vip'] = VIPMenuHandler(self.pipeline)
        self._handlers['system'] = SystemMenuHandler(self.pipeline)
    
    def route_smart_publishing(self) -> Optional[str]:
        """路由智能内容发布功能"""
        handler = self._handlers['content']
        handler.push_menu_path("1", "智能内容发布")
        try:
            return handler.handle_smart_publishing_menu()
        finally:
            handler.pop_menu_path()
    
    def route_content_normalization(self) -> None:
        """路由内容规范化处理功能"""
        handler = self._handlers['content']
        handler.push_menu_path("2", "内容规范化处理")
        try:
            return handler.handle_content_normalization_menu()
        finally:
            handler.pop_menu_path()
    
    def route_smart_creation(self) -> Optional[str]:
        """路由智能内容创作功能"""
        handler = self._handlers['content']
        handler.push_menu_path("3", "智能内容创作")
        try:
            return handler.handle_smart_creation_menu()
        finally:
            handler.pop_menu_path()
    
    def route_youtube_processing(self) -> None:
        """路由YouTube内容处理功能"""
        handler = self._handlers['youtube']
        handler.push_menu_path("4", "YouTube内容处理")
        try:
            return handler.handle_youtube_processing_menu()
        finally:
            handler.pop_menu_path()
    
    def route_onedrive_images(self) -> None:
        """路由OneDrive图床管理功能"""
        handler = self._handlers['content']
        handler.push_menu_path("5", "OneDrive图床管理")
        try:
            return handler.handle_onedrive_images_menu()
        finally:
            handler.pop_menu_path()
    
    def route_monetization(self) -> None:
        """路由内容变现管理功能"""
        handler = self._handlers['content']
        handler.push_menu_path("6", "内容变现管理")
        try:
            return handler.handle_monetization_menu()
        finally:
            handler.pop_menu_path()
    
    def route_audio_tools(self) -> None:
        """路由语音和音频工具功能"""
        handler = self._handlers['system']
        handler.push_menu_path("7", "语音和音频工具")
        try:
            return handler.handle_audio_tools_menu()
        finally:
            handler.pop_menu_path()
    
    def route_post_update(self) -> None:
        """路由文章更新工具功能"""
        handler = self._handlers['content']
        handler.push_menu_path("8", "文章更新工具")
        try:
            return handler.handle_post_update_menu()
        finally:
            handler.pop_menu_path()
    
    def route_system_tools(self) -> None:
        """路由系统工具集合功能"""
        handler = self._handlers['system']
        handler.push_menu_path("9", "系统工具集合")
        try:
            return handler.handle_system_tools_menu()
        finally:
            handler.pop_menu_path()