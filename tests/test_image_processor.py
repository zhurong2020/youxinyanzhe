"""
测试图片处理器模块
"""
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.core.processors.image_processor import ImageProcessor


class TestImageProcessor(unittest.TestCase):
    """测试ImageProcessor类"""
    
    def setUp(self):
        """测试初始化"""
        self.mock_logger = MagicMock()
        self.processor = ImageProcessor(self.mock_logger)
        
        # 创建临时目录
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """测试清理"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """测试初始化"""
        # 测试有logger的情况
        processor_with_logger = ImageProcessor(self.mock_logger)
        self.assertEqual(processor_with_logger.logger, self.mock_logger)
        
        # 测试无logger的情况
        processor_without_logger = ImageProcessor()
        self.assertIsNotNone(processor_without_logger.logger)
    
    def test_check_image_paths(self):
        """测试图片路径检查"""
        content = """
        ![Test Image](assets/images/test.png)
        ![Valid Image]({{ site.baseurl }}/assets/images/valid.png)
        ![Absolute Path](/assets/images/absolute.png)
        ![HTTP Image](https://example.com/image.png)
        <img src="assets/images/html.png" alt="HTML Image">
        """
        
        problematic_images = self.processor.check_image_paths(content)
        
        # 应该检测到问题的图片路径
        self.assertIn('assets/images/test.png', problematic_images)
        self.assertIn('/assets/images/absolute.png', problematic_images)
        self.assertIn('assets/images/html.png', problematic_images)
        
        # 不应该包含有效的路径
        self.assertNotIn('{{ site.baseurl }}/assets/images/valid.png', problematic_images)
        self.assertNotIn('https://example.com/image.png', problematic_images)
    
    def test_is_onedrive_url(self):
        """测试OneDrive URL检测"""
        # 有效的OneDrive URL
        self.assertTrue(self.processor._is_onedrive_url('https://1drv.ms/i/s!example'))
        self.assertTrue(self.processor._is_onedrive_url('https://onedrive.live.com/embed?resid=123'))
        
        # 无效的URL
        self.assertFalse(self.processor._is_onedrive_url('https://example.com/image.png'))
        self.assertFalse(self.processor._is_onedrive_url('https://google.com'))
    
    def test_extract_onedrive_id(self):
        """测试OneDrive ID提取"""
        # 测试带resid的URL
        url_with_resid = 'https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169891&authkey=test'
        unique_id = self.processor._extract_onedrive_id(url_with_resid)
        self.assertEqual(unique_id, '69891')
        
        # 测试无resid的URL，应该返回哈希值
        url_without_resid = 'https://1drv.ms/i/s!example'
        unique_id = self.processor._extract_onedrive_id(url_without_resid)
        self.assertEqual(len(unique_id), 5)  # MD5哈希值截取5位
    
    def test_get_extension_from_content_type(self):
        """测试根据content-type获取扩展名"""
        self.assertEqual(self.processor._get_extension_from_content_type('image/jpeg'), '.jpg')
        self.assertEqual(self.processor._get_extension_from_content_type('image/png'), '.png')
        self.assertEqual(self.processor._get_extension_from_content_type('image/gif'), '.gif')
        self.assertEqual(self.processor._get_extension_from_content_type('unknown/type'), '.jpg')  # 默认
    
    def test_replace_images_in_content(self):
        """测试内容中的图片替换"""
        content = """
        ![Test Image](old_image.png)
        ![Another Image](keep_image.png)
        ![Replace This](/assets/old_path.jpg)
        """
        
        images = {
            'old_image.png': 'new_image.png',
            '/assets/old_path.jpg': '/assets/new_path.jpg'
        }
        
        result = self.processor.replace_images_in_content(content, images, self.temp_dir)
        
        # 验证替换结果
        self.assertIn('new_image.png', result)
        self.assertIn('/assets/new_path.jpg', result)
        self.assertIn('keep_image.png', result)  # 未替换的保持不变
        self.assertNotIn('old_image.png', result)
        self.assertNotIn('/assets/old_path.jpg', result)
    
    def test_update_header_images(self):
        """测试更新header图片"""
        post = {
            'title': 'Test Post',
            'header': {
                'image': 'old_header.jpg',
                'teaser': 'old_teaser.png',
                'overlay_image': 'keep_this.jpg'
            }
        }
        
        images = {
            'old_header.jpg': 'new_header.jpg',
            'old_teaser.png': 'new_teaser.png'
        }
        
        updated_post = self.processor.update_header_images(post, images)
        
        # 验证更新结果
        self.assertEqual(updated_post['header']['image'], 'new_header.jpg')
        self.assertEqual(updated_post['header']['teaser'], 'new_teaser.png')
        self.assertEqual(updated_post['header']['overlay_image'], 'keep_this.jpg')  # 未替换的保持不变
    
    def test_is_same_onedrive_image(self):
        """测试OneDrive图片匹配"""
        url = 'https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169891'
        
        # 包含相同ID的图片名称应该匹配
        self.assertTrue(self.processor.is_same_onedrive_image(url, 'onedrive_69891.jpg'))
        
        # 不包含ID的图片名称不应该匹配
        self.assertFalse(self.processor.is_same_onedrive_image(url, 'other_image.jpg'))
        
        # 非OneDrive URL不应该匹配
        non_onedrive_url = 'https://example.com/image.jpg'
        self.assertFalse(self.processor.is_same_onedrive_image(non_onedrive_url, 'any_image.jpg'))
    
    @patch('requests.get')
    def test_download_onedrive_image_success(self, mock_get):
        """测试成功下载OneDrive图片"""
        # Mock响应
        mock_response = MagicMock()
        mock_response.headers = {'content-type': 'image/jpeg'}
        mock_response.raise_for_status.return_value = None
        mock_response.iter_content.return_value = [b'fake_image_data']
        mock_get.return_value = mock_response
        
        url = 'https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169891'
        filename = self.processor._download_onedrive_image(url, self.temp_dir)
        
        # 验证下载成功
        self.assertIsNotNone(filename)
        self.assertTrue(filename.startswith('onedrive_'))
        self.assertTrue(filename.endswith('.jpg'))
        
        # 验证文件确实被创建
        file_path = self.temp_dir / filename
        self.assertTrue(file_path.exists())
    
    @patch('requests.get')
    def test_download_onedrive_image_failure(self, mock_get):
        """测试下载OneDrive图片失败"""
        # Mock异常
        mock_get.side_effect = Exception('Network error')
        
        url = 'https://1drv.ms/i/s!example'
        filename = self.processor._download_onedrive_image(url, self.temp_dir)
        
        # 验证下载失败返回None
        self.assertIsNone(filename)
    
    @patch('builtins.open', new_callable=mock_open, read_data="""---
title: Test Post
header:
  image: https://1drv.ms/i/s!test
---
![Content Image](https://onedrive.live.com/embed?resid=123)
""")
    @patch('frontmatter.loads')
    def test_process_post_images(self, mock_frontmatter, mock_file):
        """测试处理文章图片"""
        # Mock frontmatter解析结果
        mock_post = MagicMock()
        mock_post.get.return_value = {'image': 'https://1drv.ms/i/s!test'}
        mock_frontmatter.return_value = mock_post
        
        # Mock文件路径
        post_path = Path('test_post.md')
        
        with patch.object(self.processor, '_download_onedrive_image', return_value=None):
            result = self.processor.process_post_images(post_path)
        
        # 验证返回空字典（功能已移除）
        self.assertEqual(result, {})


if __name__ == '__main__':
    unittest.main()