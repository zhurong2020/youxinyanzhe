"""
测试发布状态管理模块
"""
import unittest
import tempfile
import shutil
import yaml
from pathlib import Path
# unittest.mock可能在未来扩展中使用
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.core.managers.publish_manager import PublishingStatusManager


class TestPublishingStatusManager(unittest.TestCase):
    """测试PublishingStatusManager类"""
    
    def setUp(self):
        """测试初始化"""
        # 创建临时目录作为测试环境
        self.temp_dir = Path(tempfile.mkdtemp())
        self.drafts_dir = self.temp_dir / "drafts"
        self.drafts_dir.mkdir()
        
        # 创建测试用的posts目录
        self.posts_dir = self.temp_dir / "posts"
        self.posts_dir.mkdir()
        
        # 初始化发布状态管理器
        self.manager = PublishingStatusManager(self.drafts_dir)
        
    def tearDown(self):
        """测试清理"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.manager.drafts_dir, self.drafts_dir)
        self.assertTrue(self.manager.status_dir.exists())
        self.assertEqual(self.manager.status_dir.name, ".publishing")
    
    def test_get_status_file_path(self):
        """测试状态文件路径生成"""
        # 测试普通文件名
        path = self.manager.get_status_file_path("test-article")
        expected = self.manager.status_dir / "test-article.yml"
        self.assertEqual(path, expected)
        
        # 测试带.md扩展名的文件名
        path = self.manager.get_status_file_path("test-article.md")
        expected = self.manager.status_dir / "test-article.yml"
        self.assertEqual(path, expected)
    
    def test_get_published_platforms_empty(self):
        """测试获取空的已发布平台列表"""
        platforms = self.manager.get_published_platforms("nonexistent-article")
        self.assertEqual(platforms, [])
    
    def test_update_and_get_published_platforms(self):
        """测试更新和获取已发布平台"""
        article_name = "test-article"
        platforms = ["wechat", "github_pages"]
        
        # 更新发布平台
        self.manager.update_published_platforms(article_name, platforms)
        
        # 获取发布平台
        retrieved_platforms = self.manager.get_published_platforms(article_name)
        self.assertEqual(set(retrieved_platforms), set(platforms))
        
        # 验证状态文件存在
        status_file = self.manager.get_status_file_path(article_name)
        self.assertTrue(status_file.exists())
        
        # 验证文件内容
        with open(status_file, 'r', encoding='utf-8') as f:
            status_data = yaml.safe_load(f)
        
        self.assertEqual(status_data['article_name'], article_name)
        self.assertEqual(set(status_data['published_platforms']), set(platforms))
        self.assertEqual(status_data['total_publications'], len(platforms))
        self.assertIsNotNone(status_data['last_updated'])
    
    def test_update_published_platforms_merge(self):
        """测试发布平台列表合并"""
        article_name = "test-article"
        
        # 第一次更新
        self.manager.update_published_platforms(article_name, ["wechat"])
        platforms1 = self.manager.get_published_platforms(article_name)
        self.assertEqual(platforms1, ["wechat"])
        
        # 第二次更新，应该合并而不是覆盖
        self.manager.update_published_platforms(article_name, ["github_pages"])
        platforms2 = self.manager.get_published_platforms(article_name)
        self.assertEqual(set(platforms2), {"wechat", "github_pages"})
        
        # 重复更新，不应该重复添加
        self.manager.update_published_platforms(article_name, ["wechat"])
        platforms3 = self.manager.get_published_platforms(article_name)
        self.assertEqual(set(platforms3), {"wechat", "github_pages"})
    
    def test_get_available_platforms(self):
        """测试获取可用平台列表"""
        article_name = "test-article"
        all_platforms = ["wechat", "github_pages", "youtube", "douban"]
        
        # 文章未发布时，所有平台都可用
        available = self.manager.get_available_platforms(article_name, all_platforms)
        self.assertEqual(set(available), set(all_platforms))
        
        # 文章已发布到部分平台
        self.manager.update_published_platforms(article_name, ["wechat", "github_pages"])
        available = self.manager.get_available_platforms(article_name, all_platforms)
        self.assertEqual(set(available), {"youtube", "douban"})
    
    def test_initialize_legacy_post_status(self):
        """测试初始化存量文档状态"""
        # 创建测试文档
        (self.posts_dir / "article1.md").write_text("# Article 1")
        (self.posts_dir / "article2.md").write_text("# Article 2")
        
        # 初始化存量状态
        count = self.manager.initialize_legacy_post_status(self.posts_dir)
        self.assertEqual(count, 2)
        
        # 验证状态文件已创建
        platforms1 = self.manager.get_published_platforms("article1")
        platforms2 = self.manager.get_published_platforms("article2")
        
        self.assertEqual(platforms1, ["github_pages"])
        self.assertEqual(platforms2, ["github_pages"])
        
        # 再次运行不应该重复创建
        count2 = self.manager.initialize_legacy_post_status(self.posts_dir)
        self.assertEqual(count2, 0)
    
    def test_get_platform_status_summary(self):
        """测试获取平台状态摘要"""
        article_name = "test-article"
        
        # 不存在的文章
        summary = self.manager.get_platform_status_summary(article_name)
        self.assertFalse(summary['exists'])
        self.assertEqual(summary['published_platforms'], [])
        self.assertEqual(summary['total_publications'], 0)
        
        # 已发布的文章
        self.manager.update_published_platforms(article_name, ["wechat", "github_pages"])
        summary = self.manager.get_platform_status_summary(article_name)
        
        self.assertTrue(summary['exists'])
        self.assertEqual(set(summary['published_platforms']), {"wechat", "github_pages"})
        self.assertEqual(summary['total_publications'], 2)
        self.assertEqual(summary['article_name'], article_name)
        self.assertIsNotNone(summary['last_updated'])
    
    def test_remove_platform_status(self):
        """测试移除平台状态"""
        article_name = "test-article"
        
        # 设置初始状态
        self.manager.update_published_platforms(article_name, ["wechat", "github_pages", "youtube"])
        
        # 移除一个平台
        result = self.manager.remove_platform_status(article_name, "github_pages")
        self.assertTrue(result)
        
        # 验证平台已被移除
        platforms = self.manager.get_published_platforms(article_name)
        self.assertEqual(set(platforms), {"wechat", "youtube"})
        
        # 移除不存在的平台
        result = self.manager.remove_platform_status(article_name, "nonexistent")
        self.assertFalse(result)
        
        # 移除不存在文章的平台
        result = self.manager.remove_platform_status("nonexistent-article", "wechat")
        self.assertFalse(result)
    
    def test_error_handling(self):
        """测试错误处理"""
        # 创建一个损坏的状态文件
        article_name = "corrupted-article"
        status_file = self.manager.get_status_file_path(article_name)
        status_file.write_text("invalid: yaml: content: [unclosed")
        
        # 应该返回空列表而不是抛出异常
        platforms = self.manager.get_published_platforms(article_name)
        self.assertEqual(platforms, [])
        
        # 状态摘要应该处理错误
        summary = self.manager.get_platform_status_summary(article_name)
        self.assertTrue(summary['exists'])
        self.assertEqual(summary['published_platforms'], [])
        self.assertIn('error', summary)


if __name__ == '__main__':
    unittest.main()