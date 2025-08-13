"""
测试平台处理器模块
"""
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.core.processors.platform_processor import (
    PlatformProcessor, 
    WeChatAdapter, 
    GitHubPagesAdapter, 
    WordPressAdapter
)


class TestPlatformProcessor(unittest.TestCase):
    """测试PlatformProcessor类"""
    
    def setUp(self):
        """测试初始化"""
        self.mock_logger = MagicMock()
        self.project_root = Path("/test/project")
        self.platforms_config = {
            "wechat": {
                "enabled": True,
                "publish_mode": "guide"
            },
            "github_pages": {
                "enabled": True
            },
            "wordpress": {
                "enabled": False
            }
        }
        
    @patch('scripts.core.processors.platform_processor.WeChatAdapter')
    @patch('scripts.core.processors.platform_processor.GitHubPagesAdapter')
    def test_initialization(self, mock_github, mock_wechat):
        """测试初始化"""
        processor = PlatformProcessor(self.platforms_config, self.project_root, self.mock_logger)
        
        # 验证只有启用的平台被初始化
        self.assertEqual(len(processor.adapters), 2)  # wechat和github_pages
        mock_wechat.assert_called_once()
        mock_github.assert_called_once()
    
    def test_get_available_platforms(self):
        """测试获取可用平台列表"""
        with patch('scripts.core.processors.platform_processor.WeChatAdapter'), \
             patch('scripts.core.processors.platform_processor.GitHubPagesAdapter'):
            processor = PlatformProcessor(self.platforms_config, self.project_root, self.mock_logger)
            platforms = processor.get_available_platforms()
            
            self.assertIn("wechat", platforms)
            self.assertIn("github_pages", platforms)
            self.assertNotIn("wordpress", platforms)  # 未启用
    
    @patch('frontmatter.loads')
    @patch('frontmatter.dumps')
    def test_generate_platform_content_success(self, mock_dumps, mock_loads):
        """测试成功生成平台内容"""
        mock_post = MagicMock()
        mock_post.content = "Test content"
        mock_post.metadata = {"title": "Test"}
        mock_loads.return_value = mock_post
        mock_dumps.return_value = "---\ntitle: Test\n---\nAdapted content"
        
        mock_adapter = MagicMock()
        mock_adapter.generate_content.return_value = "Adapted content"
        
        with patch('scripts.core.processors.platform_processor.WeChatAdapter'):
            processor = PlatformProcessor(self.platforms_config, self.project_root, self.mock_logger)
            processor.adapters["test_platform"] = mock_adapter
            
            result = processor.generate_platform_content("test content", "test_platform")
            
            mock_adapter.generate_content.assert_called_once_with("Test content", {"title": "Test"})
            self.assertEqual(result, "---\ntitle: Test\n---\nAdapted content")
    
    def test_generate_platform_content_unavailable_platform(self):
        """测试不可用平台的内容生成"""
        with patch('scripts.core.processors.platform_processor.WeChatAdapter'):
            processor = PlatformProcessor(self.platforms_config, self.project_root, self.mock_logger)
            result = processor.generate_platform_content("test content", "nonexistent_platform")
            
            self.assertEqual(result, "test content")  # 返回原内容
    
    @patch('frontmatter.loads')
    def test_publish_to_platform_success(self, mock_loads):
        """测试成功发布到平台"""
        mock_post = MagicMock()
        mock_post.content = "Test content"
        mock_post.metadata = {"title": "Test"}
        mock_loads.return_value = mock_post
        
        mock_adapter = MagicMock()
        mock_adapter.publish.return_value = True
        
        with patch('scripts.core.processors.platform_processor.WeChatAdapter'):
            processor = PlatformProcessor(self.platforms_config, self.project_root, self.mock_logger)
            processor.adapters["test_platform"] = mock_adapter
            
            result = processor.publish_to_platform("test content", "test_platform")
            
            mock_adapter.publish.assert_called_once_with("Test content", {"title": "Test"})
            self.assertTrue(result)
    
    def test_publish_to_multiple_platforms(self):
        """测试发布到多个平台"""
        mock_adapter1 = MagicMock()
        mock_adapter1.publish.return_value = True
        mock_adapter2 = MagicMock()  
        mock_adapter2.publish.return_value = False
        
        with patch('scripts.core.processors.platform_processor.WeChatAdapter'), \
             patch('frontmatter.loads') as mock_loads:
            mock_post = MagicMock()
            mock_post.content = "Test content"
            mock_post.metadata = {"title": "Test"}
            mock_loads.return_value = mock_post
            
            processor = PlatformProcessor(self.platforms_config, self.project_root, self.mock_logger)
            processor.adapters = {
                "platform1": mock_adapter1,
                "platform2": mock_adapter2
            }
            
            results = processor.publish_to_multiple_platforms("test content", ["platform1", "platform2", "nonexistent"])
            
            self.assertEqual(results["platform1"], True)
            self.assertEqual(results["platform2"], False)
            self.assertEqual(results["nonexistent"], False)


class TestWeChatAdapter(unittest.TestCase):
    """测试WeChatAdapter类"""
    
    def setUp(self):
        """测试初始化"""
        self.mock_logger = MagicMock()
        self.project_root = Path("/test/project")
        self.config = {
            "publish_mode": "guide"
        }
    
    @patch('scripts.core.processors.platform_processor.WechatPublisher')
    def test_initialization_success(self, mock_publisher_class):
        """测试成功初始化"""
        mock_publisher = MagicMock()
        mock_publisher_class.return_value = mock_publisher
        
        adapter = WeChatAdapter(self.config, self.project_root, self.mock_logger)
        
        self.assertIsNotNone(adapter.wechat_publisher)
        mock_publisher_class.assert_called_once_with(None)  # gemini_model from config
    
    @patch('scripts.core.processors.platform_processor.WechatPublisher')
    def test_initialization_failure(self, mock_publisher_class):
        """测试初始化失败"""
        mock_publisher_class.side_effect = Exception("Init failed")
        
        adapter = WeChatAdapter(self.config, self.project_root, self.mock_logger)
        
        self.assertIsNone(adapter.wechat_publisher)
    
    def test_publish_no_publisher(self):
        """测试没有发布器时的发布"""
        with patch('scripts.core.processors.platform_processor.WechatPublisher') as mock_publisher_class:
            mock_publisher_class.side_effect = Exception("Init failed")
            adapter = WeChatAdapter(self.config, self.project_root, self.mock_logger)
            
            result = adapter.publish("test content", {"title": "Test"})
            self.assertFalse(result)
    
    @patch('scripts.core.processors.platform_processor.WechatPublisher')
    def test_publish_api_mode_success(self, mock_publisher_class):
        """测试API模式成功发布"""
        mock_publisher = MagicMock()
        mock_publisher.publish_to_draft.return_value = "media123"
        mock_publisher_class.return_value = mock_publisher
        
        config = {"publish_mode": "api"}
        adapter = WeChatAdapter(config, self.project_root, self.mock_logger)
        
        result = adapter.publish("test content", {"title": "Test"})
        
        self.assertTrue(result)
        mock_publisher.publish_to_draft.assert_called_once()
    
    @patch('scripts.core.processors.platform_processor.WechatPublisher')
    def test_publish_guide_mode_success(self, mock_publisher_class):
        """测试指南模式成功发布"""
        mock_publisher = MagicMock()
        mock_publisher.generate_publishing_guide.return_value = True
        mock_publisher_class.return_value = mock_publisher
        
        config = {"publish_mode": "guide"}
        adapter = WeChatAdapter(config, self.project_root, self.mock_logger)
        
        result = adapter.publish("test content", {"title": "Test"})
        
        self.assertTrue(result)
        mock_publisher.generate_publishing_guide.assert_called_once()
    
    def test_generate_content(self):
        """测试生成内容"""
        with patch('scripts.core.processors.platform_processor.WechatPublisher'):
            adapter = WeChatAdapter(self.config, self.project_root, self.mock_logger)
            result = adapter.generate_content("test content", {"title": "Test"})
            
            # 目前直接返回原内容
            self.assertEqual(result, "test content")


class TestGitHubPagesAdapter(unittest.TestCase):
    """测试GitHubPagesAdapter类"""
    
    def test_publish(self):
        """测试发布到GitHub Pages"""
        config = {"enabled": True}
        adapter = GitHubPagesAdapter(config)
        
        result = adapter.publish("test content", {"title": "Test"})
        self.assertTrue(result)  # 目前总是返回True
    
    def test_generate_content(self):
        """测试生成内容"""
        config = {"enabled": True}
        adapter = GitHubPagesAdapter(config)
        
        result = adapter.generate_content("test content", {"title": "Test"})
        self.assertEqual(result, "test content")  # 目前直接返回原内容


class TestWordPressAdapter(unittest.TestCase):
    """测试WordPressAdapter类"""
    
    def test_publish(self):
        """测试发布到WordPress"""
        config = {"enabled": True}
        adapter = WordPressAdapter(config)
        
        result = adapter.publish("test content", {"title": "Test"})
        self.assertFalse(result)  # 功能待实现，返回False
    
    def test_generate_content(self):
        """测试生成内容"""
        config = {"enabled": True}
        adapter = WordPressAdapter(config)
        
        result = adapter.generate_content("test content", {"title": "Test"})
        self.assertEqual(result, "test content")  # 目前直接返回原内容


if __name__ == '__main__':
    unittest.main()