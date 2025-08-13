"""
发布状态管理模块
负责跟踪和管理文章在各平台的发布状态
"""
import yaml
import logging
from pathlib import Path
from typing import List
from datetime import datetime


class PublishingStatusManager:
    """发布状态管理器"""
    
    def __init__(self, drafts_dir: Path):
        """
        初始化发布状态管理器
        
        Args:
            drafts_dir: 草稿目录路径
        """
        self.drafts_dir = Path(drafts_dir)
        self.status_dir = self.drafts_dir / ".publishing"
        self.status_dir.mkdir(exist_ok=True)
        
    def get_status_file_path(self, article_name: str) -> Path:
        """
        获取文章状态文件路径
        
        Args:
            article_name: 文章名称
            
        Returns:
            状态文件路径
        """
        # 移除文件扩展名
        article_name = article_name.replace('.md', '')
        return self.status_dir / f"{article_name}.yml"
    
    def get_published_platforms(self, article_name: str) -> List[str]:
        """
        获取文章已发布的平台列表
        
        Args:
            article_name: 文章名称
            
        Returns:
            已发布的平台列表
        """
        status_file = self.get_status_file_path(article_name)
        
        if not status_file.exists():
            return []
            
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                status_data = yaml.safe_load(f) or {}
            return status_data.get('published_platforms', [])
        except Exception:
            return []
    
    def update_published_platforms(self, article_name: str, platforms: List[str]) -> None:
        """
        更新文章的发布平台列表
        
        Args:
            article_name: 文章名称
            platforms: 新增的发布平台列表
        """
        status_file = self.get_status_file_path(article_name)
        
        # 读取现有状态
        status_data = {}
        if status_file.exists():
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = yaml.safe_load(f) or {}
            except Exception:
                status_data = {}
        
        # 更新发布平台列表（合并，避免重复）
        existing_platforms = set(status_data.get('published_platforms', []))
        new_platforms = set(platforms)
        all_platforms = list(existing_platforms.union(new_platforms))
        
        # 更新状态数据
        status_data.update({
            'article_name': article_name,
            'published_platforms': all_platforms,
            'last_updated': datetime.now().isoformat(),
            'total_publications': len(all_platforms)
        })
        
        # 保存状态文件
        try:
            with open(status_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(status_data, f, default_flow_style=False, 
                             allow_unicode=True, sort_keys=False)
        except Exception as e:
            logging.error(f"保存发布状态失败: {e}")
    
    def get_available_platforms(self, article_name: str, all_platforms: List[str]) -> List[str]:
        """
        获取文章可发布的平台列表（排除已发布的）
        
        Args:
            article_name: 文章名称
            all_platforms: 所有可用平台列表
            
        Returns:
            可发布的平台列表
        """
        published_platforms = set(self.get_published_platforms(article_name))
        available_platforms = [p for p in all_platforms if p not in published_platforms]
        return available_platforms
    
    def initialize_legacy_post_status(self, posts_dir: Path) -> int:
        """
        初始化存量已发布文档的状态
        
        Args:
            posts_dir: 已发布文档目录
            
        Returns:
            初始化的文档数量
        """
        if not posts_dir.exists():
            return 0
            
        legacy_count = 0
        for post_file in posts_dir.glob("*.md"):
            article_name = post_file.stem
            
            # 检查是否已有状态文件
            if self.get_status_file_path(article_name).exists():
                continue
                
            # 为存量文档创建状态记录（默认已在github_pages发布）
            self.update_published_platforms(article_name, ['github_pages'])
            legacy_count += 1
            
        if legacy_count > 0:
            logging.info(f"已为 {legacy_count} 个存量文档初始化发布状态")
        
        return legacy_count
    
    def get_platform_status_summary(self, article_name: str) -> dict:
        """
        获取文章发布状态摘要
        
        Args:
            article_name: 文章名称
            
        Returns:
            状态摘要字典
        """
        status_file = self.get_status_file_path(article_name)
        
        if not status_file.exists():
            return {
                'exists': False,
                'published_platforms': [],
                'total_publications': 0,
                'last_updated': None
            }
        
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                status_data = yaml.safe_load(f) or {}
            
            return {
                'exists': True,
                'published_platforms': status_data.get('published_platforms', []),
                'total_publications': status_data.get('total_publications', 0),
                'last_updated': status_data.get('last_updated'),
                'article_name': status_data.get('article_name', article_name)
            }
        except Exception as e:
            logging.warning(f"读取状态文件失败: {e}")
            return {
                'exists': True,
                'published_platforms': [],
                'total_publications': 0,
                'last_updated': None,
                'error': str(e)
            }
    
    def remove_platform_status(self, article_name: str, platform: str) -> bool:
        """
        从文章发布状态中移除特定平台
        
        Args:
            article_name: 文章名称
            platform: 要移除的平台名称
            
        Returns:
            是否成功移除
        """
        status_file = self.get_status_file_path(article_name)
        
        if not status_file.exists():
            return False
        
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                status_data = yaml.safe_load(f) or {}
            
            published_platforms = status_data.get('published_platforms', [])
            
            if platform in published_platforms:
                published_platforms.remove(platform)
                status_data['published_platforms'] = published_platforms
                status_data['total_publications'] = len(published_platforms)
                status_data['last_updated'] = datetime.now().isoformat()
                
                with open(status_file, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(status_data, f, default_flow_style=False,
                                 allow_unicode=True, sort_keys=False)
                
                logging.info(f"已从文章 {article_name} 的发布状态中移除平台 {platform}")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"移除平台状态失败: {e}")
            return False