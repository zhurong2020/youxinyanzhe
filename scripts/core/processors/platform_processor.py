"""
平台发布处理器模块
负责统一管理各种平台的内容发布功能
"""
import logging
import frontmatter
from pathlib import Path
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

# 导入现有的平台发布器
from ..wechat_publisher import WechatPublisher


class PlatformAdapter(ABC):
    """平台适配器抽象基类"""
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
    @abstractmethod
    def publish(self, content: str, metadata: Dict[str, Any]) -> bool:
        """发布内容到平台"""
        pass
    
    @abstractmethod
    def generate_content(self, content: str, metadata: Dict[str, Any]) -> str:
        """为特定平台生成适配内容"""
        pass
    
    def log(self, message: str, level: str = "info", force: bool = False) -> None:
        """记录日志"""
        if self.logger:
            getattr(self.logger, level)(message)
            if force:
                print(f"[{level.upper()}] {message}")


class WeChatAdapter(PlatformAdapter):
    """微信公众号适配器"""
    
    def __init__(self, config: Dict[str, Any], project_root: Path, logger: Optional[logging.Logger] = None):
        super().__init__(config, logger)
        self.project_root = project_root
        self.wechat_publisher = None
        self._initialize_publisher()
    
    def _initialize_publisher(self):
        """初始化微信发布器"""
        try:
            self.wechat_publisher = WechatPublisher(self.project_root, self.logger)
            self.log("微信发布器初始化成功", level="info")
        except Exception as e:
            self.log(f"微信发布器初始化失败: {str(e)}", level="error")
            self.wechat_publisher = None
    
    def publish(self, content: str, metadata: Dict[str, Any]) -> bool:
        """发布到微信公众号"""
        if not self.wechat_publisher:
            self.log("微信发布器未初始化，跳过发布", level="error", force=True)
            return False
        
        try:
            publish_mode = self.config.get("publish_mode", "guide")
            self.log(f"微信发布模式: {publish_mode.upper()}", level="info", force=True)
            
            if publish_mode == "api":
                # API模式：直接发布到草稿箱
                media_id = self.wechat_publisher.publish_to_draft(
                    project_root=self.project_root,
                    front_matter=metadata,
                    markdown_content=content
                )
                if media_id:
                    self.log(f"✅ 成功创建微信草稿，Media ID: {media_id}", level="info", force=True)
                    return True
                else:
                    self.log("❌ 微信草稿创建失败", level="error", force=True)
                    return False
            else:
                # guide模式：生成发布指南
                guide_generated = self.wechat_publisher.generate_publishing_guide(
                    project_root=self.project_root,
                    front_matter=metadata,
                    markdown_content=content
                )
                if guide_generated:
                    self.log("✅ 微信发布指南生成成功", level="info", force=True)
                    return True
                else:
                    self.log("❌ 微信发布指南生成失败", level="error", force=True)
                    return False
                    
        except Exception as e:
            self.log(f"微信发布失败: {str(e)}", level="error", force=True)
            return False
    
    def generate_content(self, content: str, metadata: Dict[str, Any]) -> str:
        """为微信平台生成适配内容"""
        # 微信平台的内容格式化
        # 可以添加微信特有的格式优化
        return content


class GitHubPagesAdapter(PlatformAdapter):
    """GitHub Pages适配器"""
    
    def publish(self, content: str, metadata: Dict[str, Any]) -> bool:
        """发布到GitHub Pages（Jekyll）"""
        # GitHub Pages发布逻辑
        # 这里可以实现将内容移动到_posts目录的逻辑
        _ = content, metadata  # 避免未使用参数警告
        return True
    
    def generate_content(self, content: str, metadata: Dict[str, Any]) -> str:
        """为GitHub Pages生成适配内容"""
        # Jekyll格式的内容处理
        _ = metadata  # 避免未使用参数警告
        return content


class WordPressAdapter(PlatformAdapter):
    """WordPress适配器"""
    
    def publish(self, content: str, metadata: Dict[str, Any]) -> bool:
        """发布到WordPress"""
        # WordPress发布逻辑（通过REST API）
        _ = content, metadata  # 避免未使用参数警告
        self.log("WordPress发布功能待实现", level="warning")
        return False
    
    def generate_content(self, content: str, metadata: Dict[str, Any]) -> str:
        """为WordPress生成适配内容"""
        # WordPress特有的格式处理
        _ = metadata  # 避免未使用参数警告
        return content


class PlatformProcessor:
    """平台处理器 - 统一管理各平台发布"""
    
    def __init__(self, platforms_config: Dict[str, Dict[str, Any]], project_root: Path, logger: Optional[logging.Logger] = None):
        """
        初始化平台处理器
        
        Args:
            platforms_config: 平台配置字典
            project_root: 项目根目录
            logger: 日志记录器
        """
        self.platforms_config = platforms_config
        self.project_root = project_root
        self.logger = logger or logging.getLogger(__name__)
        self.adapters: Dict[str, PlatformAdapter] = {}
        self._initialize_adapters()
    
    def _initialize_adapters(self):
        """初始化所有平台适配器"""
        for platform_name, config in self.platforms_config.items():
            if not config.get("enabled", False):
                continue
                
            try:
                if platform_name == "wechat":
                    self.adapters[platform_name] = WeChatAdapter(config, self.project_root, self.logger)
                elif platform_name == "github_pages":
                    self.adapters[platform_name] = GitHubPagesAdapter(config, self.logger)
                elif platform_name == "wordpress":
                    self.adapters[platform_name] = WordPressAdapter(config, self.logger)
                else:
                    self.log(f"未知平台类型: {platform_name}", level="warning")
                    
            except Exception as e:
                self.log(f"初始化{platform_name}适配器失败: {str(e)}", level="error")
    
    def log(self, message: str, level: str = "info", force: bool = False) -> None:
        """记录日志"""
        if self.logger:
            getattr(self.logger, level)(message)
            if force:
                print(f"[{level.upper()}] {message}")
    
    def get_available_platforms(self) -> List[str]:
        """获取可用的平台列表"""
        return list(self.adapters.keys())
    
    def generate_platform_content(self, content: str, platform: str) -> str:
        """为特定平台生成适配内容"""
        if platform not in self.adapters:
            self.log(f"平台 {platform} 不可用", level="warning")
            return content
            
        try:
            post = frontmatter.loads(content)
            adapter = self.adapters[platform]
            adapted_content = adapter.generate_content(post.content, post.metadata)
            
            # 重新构建包含front matter的完整内容
            post.content = adapted_content
            return frontmatter.dumps(post)
            
        except Exception as e:
            self.log(f"为平台 {platform} 生成内容失败: {str(e)}", level="error")
            return content
    
    def publish_to_platform(self, content: str, platform: str) -> bool:
        """发布内容到指定平台"""
        if platform not in self.adapters:
            self.log(f"平台 {platform} 不可用", level="warning")
            return False
            
        try:
            post = frontmatter.loads(content)
            adapter = self.adapters[platform]
            return adapter.publish(post.content, post.metadata)
            
        except Exception as e:
            self.log(f"发布到平台 {platform} 失败: {str(e)}", level="error")
            return False
    
    def publish_to_multiple_platforms(self, content: str, platforms: List[str]) -> Dict[str, bool]:
        """发布内容到多个平台"""
        results = {}
        
        for platform in platforms:
            if platform in self.adapters:
                self.log(f"正在发布到 {platform}...", level="info", force=True)
                results[platform] = self.publish_to_platform(content, platform)
            else:
                self.log(f"平台 {platform} 不可用，跳过", level="warning")
                results[platform] = False
        
        return results