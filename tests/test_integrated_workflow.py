"""
测试集成内容处理工作流模块
"""
import unittest
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path
import tempfile
import os
import logging

# 添加项目根目录到Python路径
import sys
sys.path.append('/home/wuxia/projects/workshop')

from scripts.core.workflows.integrated_workflow import IntegratedContentWorkflow
from scripts.core.workflows.content_workflow import WorkflowResult, WorkflowStepStatus
from scripts.core.processors.ai_processor import AIProcessor
from scripts.core.processors.platform_processor import PlatformProcessor
from scripts.core.processors.image_processor import ImageProcessor
from scripts.core.managers.publish_manager import PublishingStatusManager


class TestIntegratedContentWorkflow(unittest.TestCase):
    """测试集成内容处理工作流"""
    
    def setUp(self):
        """设置测试环境"""
        self.logger = Mock(spec=logging.Logger)
        self.ai_processor = Mock(spec=AIProcessor)
        self.platform_processor = Mock(spec=PlatformProcessor)
        self.image_processor = Mock(spec=ImageProcessor)
        self.status_manager = Mock(spec=PublishingStatusManager)
        
        self.workflow = IntegratedContentWorkflow(
            ai_processor=self.ai_processor,
            platform_processor=self.platform_processor,
            image_processor=self.image_processor,
            status_manager=self.status_manager,
            logger=self.logger
        )
        
        # 创建测试文件
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        self.temp_file.write("""---
title: "Test Article with Quotes"
date: 2023-01-01
excerpt: "Test excerpt"
categories: ["tech"]
tags: ["test", "article"]
---

This is test content with more than 100 characters to ensure it passes validation. It contains multiple lines and should be processed correctly by the workflow engine.""")
        self.temp_file.close()
        self.temp_path = Path(self.temp_file.name)
    
    def tearDown(self):
        """清理测试环境"""
        if self.temp_path.exists():
            os.unlink(self.temp_path)
    
    def test_workflow_initialization(self):
        """测试工作流初始化"""
        self.assertEqual(self.workflow.ai_processor, self.ai_processor)
        self.assertEqual(self.workflow.platform_processor, self.platform_processor)
        self.assertEqual(self.workflow.image_processor, self.image_processor)
        self.assertEqual(self.workflow.status_manager, self.status_manager)
        self.assertEqual(self.workflow.logger, self.logger)
    
    def test_workflow_initialization_with_none_processors(self):
        """测试使用None处理器的工作流初始化"""
        workflow = IntegratedContentWorkflow()
        
        self.assertIsNone(workflow.ai_processor)
        self.assertIsNone(workflow.platform_processor)
        self.assertIsNone(workflow.image_processor)
        self.assertIsNone(workflow.status_manager)
        self.assertIsNotNone(workflow.logger)  # 应该有默认logger
    
    @patch('frontmatter.loads')
    def test_parse_frontmatter_success(self, mock_frontmatter):
        """测试Front Matter解析成功"""
        # 模拟frontmatter.loads的返回值
        mock_post = Mock()
        mock_post.metadata = {'title': 'Test', 'date': '2023-01-01'}
        mock_post.content = 'Test content'
        mock_frontmatter.return_value = mock_post
        
        context = {}
        results = {'load_content': 'test content with frontmatter'}
        
        result = self.workflow._parse_frontmatter(context, results)
        
        self.assertEqual(result['post'], mock_post)
        self.assertEqual(result['frontmatter'], mock_post.metadata)
        self.assertEqual(result['content_body'], mock_post.content)
        self.assertNotIn('content_fixed', result)
    
    @patch('frontmatter.loads')
    def test_parse_frontmatter_with_fix(self, mock_frontmatter):
        """测试Front Matter解析需要修复的情况"""
        # 第一次调用失败，第二次调用成功
        mock_post = Mock()
        mock_post.metadata = {'title': 'Test', 'date': '2023-01-01'}
        mock_post.content = 'Test content'
        
        mock_frontmatter.side_effect = [Exception("Parse error"), mock_post]
        
        context = {}
        results = {'load_content': 'content with bad frontmatter'}
        
        with patch.object(self.workflow, '_fix_frontmatter_quotes', return_value='fixed content'):
            result = self.workflow._parse_frontmatter(context, results)
        
        self.assertEqual(result['post'], mock_post)
        self.assertTrue(result.get('content_fixed', False))
    
    @patch('frontmatter.loads')
    def test_parse_frontmatter_unfixable(self, mock_frontmatter):
        """测试Front Matter解析无法修复的情况"""
        mock_frontmatter.side_effect = [Exception("Parse error"), Exception("Still bad")]
        
        context = {}
        results = {'load_content': 'unfixable content'}
        
        with patch.object(self.workflow, '_fix_frontmatter_quotes', return_value='still bad'):
            with self.assertRaises(ValueError) as cm:
                self.workflow._parse_frontmatter(context, results)
            self.assertIn("Front matter解析失败", str(cm.exception))
    
    def test_validate_content_success(self):
        """测试内容验证成功"""
        mock_post = Mock()
        mock_post.metadata = {'title': 'Test Article', 'date': '2023-01-01'}
        # 确保内容长度超过100个字符
        long_content = 'This is a test article with sufficient content length to pass validation checks. ' * 2
        mock_post.content = long_content
        
        context = {}
        results = {'parse_frontmatter': {'post': mock_post}}
        
        result = self.workflow._validate_content(context, results)
        
        self.assertTrue(result['content_valid'])
        self.assertTrue(result['required_fields_present'])
        self.assertEqual(result['content_length'], len(long_content))
    
    def test_validate_content_missing_fields(self):
        """测试内容验证缺少必需字段"""
        mock_post = Mock()
        mock_post.metadata = {'title': 'Test Article'}  # 缺少date
        mock_post.content = 'Test content with sufficient length'
        
        context = {}
        results = {'parse_frontmatter': {'post': mock_post}}
        
        with self.assertRaises(ValueError) as cm:
            self.workflow._validate_content(context, results)
        self.assertIn("缺少必需字段: date", str(cm.exception))
    
    def test_validate_content_too_short(self):
        """测试内容过短"""
        mock_post = Mock()
        mock_post.metadata = {'title': 'Test', 'date': '2023-01-01'}
        mock_post.content = 'Short'
        
        context = {}
        results = {'parse_frontmatter': {'post': mock_post}}
        
        with self.assertRaises(ValueError) as cm:
            self.workflow._validate_content(context, results)
        self.assertIn("文章内容过短", str(cm.exception))
    
    def test_process_images_success(self):
        """测试图片处理成功"""
        self.image_processor.check_image_paths.return_value = ['image1.jpg', 'image2.png']
        
        context = {'draft_path': self.temp_path}
        results = {'load_content': 'content with images'}
        
        result = self.workflow._process_images(context, results)
        
        self.assertTrue(result['images_processed'])
        self.assertEqual(result['problematic_images_count'], 2)
        self.assertEqual(result['problematic_images'], ['image1.jpg', 'image2.png'])
        self.assertNotIn('skipped', result)
    
    def test_process_images_no_processor(self):
        """测试没有图片处理器的情况"""
        workflow = IntegratedContentWorkflow()  # 没有图片处理器
        
        context = {'draft_path': self.temp_path}
        results = {'load_content': 'content'}
        
        result = workflow._process_images(context, results)
        
        self.assertFalse(result['images_processed'])
        self.assertTrue(result['skipped'])
    
    def test_process_images_exception(self):
        """测试图片处理异常"""
        self.image_processor.check_image_paths.side_effect = Exception("Image processing error")
        
        context = {'draft_path': self.temp_path}
        results = {'load_content': 'content'}
        
        result = self.workflow._process_images(context, results)
        
        self.assertFalse(result['images_processed'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'Image processing error')
    
    def test_enhance_content_success(self):
        """测试AI内容增强成功"""
        mock_post = Mock()
        mock_post.metadata = {}
        mock_post.content = 'Original content'
        
        self.ai_processor.polish_content.return_value = 'Polished content'
        self.ai_processor.generate_excerpt.return_value = 'Generated excerpt'
        self.ai_processor.generate_categories_and_tags.return_value = (['tech'], ['ai', 'test'])
        
        context = {
            'enable_polish': True,
            'enable_categorization': True,
            'available_categories': {'tech': ['ai', 'ml']}
        }
        results = {
            'load_content': 'original content',
            'parse_frontmatter': {'post': mock_post}
        }
        
        result = self.workflow._enhance_content(context, results)
        
        self.assertTrue(result['content_enhanced'])
        enhanced_results = result['enhanced_results']
        self.assertEqual(enhanced_results['polished_content'], 'Polished content')
        self.assertEqual(enhanced_results['generated_excerpt'], 'Generated excerpt')
        self.assertEqual(enhanced_results['suggested_categories'], ['tech'])
        self.assertEqual(enhanced_results['suggested_tags'], ['ai', 'test'])
    
    def test_enhance_content_no_processor(self):
        """测试没有AI处理器的情况"""
        workflow = IntegratedContentWorkflow()
        
        context = {}
        results = {'load_content': 'content', 'parse_frontmatter': {'post': Mock()}}
        
        result = workflow._enhance_content(context, results)
        
        self.assertFalse(result['content_enhanced'])
        self.assertTrue(result['skipped'])
    
    def test_enhance_content_exception(self):
        """测试AI增强异常"""
        self.ai_processor.polish_content.side_effect = Exception("AI error")
        
        mock_post = Mock()
        mock_post.metadata = {}
        mock_post.content = 'content'
        
        context = {'enable_polish': True}
        results = {
            'load_content': 'content',
            'parse_frontmatter': {'post': mock_post}
        }
        
        result = self.workflow._enhance_content(context, results)
        
        self.assertFalse(result['content_enhanced'])
        self.assertIn('error', result)
    
    def test_generate_platforms_content_success(self):
        """测试平台内容生成成功"""
        self.platform_processor.generate_platform_content.side_effect = [
            'wechat adapted content',
            'github adapted content'
        ]
        
        context = {'platforms': ['wechat', 'github']}
        results = {'load_content': 'base content'}
        
        result = self.workflow._generate_platforms_content(context, results)
        
        platform_contents = result['platform_contents']
        self.assertEqual(platform_contents['wechat'], 'wechat adapted content')
        self.assertEqual(platform_contents['github'], 'github adapted content')
    
    def test_generate_platforms_content_with_enhanced_content(self):
        """测试使用增强内容生成平台内容"""
        self.platform_processor.generate_platform_content.return_value = 'adapted enhanced content'
        
        context = {'platforms': ['wechat']}
        results = {
            'load_content': 'base content',
            'enhance_content': {
                'enhanced_results': {'polished_content': 'enhanced content'}
            }
        }
        
        result = self.workflow._generate_platforms_content(context, results)
        
        # 验证使用了增强后的内容
        self.platform_processor.generate_platform_content.assert_called_with('enhanced content', 'wechat')
    
    def test_generate_platforms_content_no_processor(self):
        """测试没有平台处理器的情况"""
        workflow = IntegratedContentWorkflow()
        
        context = {'platforms': ['wechat', 'github']}
        results = {'load_content': 'content'}
        
        result = workflow._generate_platforms_content(context, results)
        
        platform_contents = result['platform_contents']
        self.assertEqual(platform_contents['wechat'], 'content')
        self.assertEqual(platform_contents['github'], 'content')
    
    def test_publish_to_platforms_success(self):
        """测试平台发布成功"""
        self.platform_processor.publish_to_platform.side_effect = [True, False]
        
        context = {'platforms': ['wechat', 'github']}
        results = {
            'load_content': 'content',
            'generate_platforms_content': {
                'platform_contents': {'wechat': 'wechat content', 'github': 'github content'}
            }
        }
        
        result = self.workflow._publish_to_platforms(context, results)
        
        self.assertEqual(result['publish_results'], {'wechat': True, 'github': False})
        self.assertEqual(result['successful_platforms'], ['wechat'])
        self.assertEqual(result['total_platforms'], 2)
    
    def test_publish_to_platforms_no_processor(self):
        """测试没有平台处理器的情况"""
        workflow = IntegratedContentWorkflow()
        
        context = {'platforms': ['wechat']}
        results = {}
        
        result = workflow._publish_to_platforms(context, results)
        
        self.assertEqual(result['publish_results'], {})
        self.assertEqual(result['successful_platforms'], [])
    
    def test_publish_to_platforms_exception(self):
        """测试平台发布异常"""
        self.platform_processor.publish_to_platform.side_effect = Exception("Publish error")
        
        context = {'platforms': ['wechat']}
        results = {'load_content': 'content'}
        
        result = self.workflow._publish_to_platforms(context, results)
        
        self.assertEqual(result['publish_results']['wechat'], False)
        self.assertEqual(result['successful_platforms'], [])
    
    def test_update_status_success(self):
        """测试状态更新成功"""
        context = {'draft_path': self.temp_path}
        results = {
            'publish_to_platforms': {
                'successful_platforms': ['wechat', 'github'],
                'total_platforms': 3
            }
        }
        
        result = self.workflow._update_status(context, results)
        
        self.assertTrue(result['status_updated'])
        self.assertEqual(result['successful_platforms'], ['wechat', 'github'])
        self.assertEqual(result['total_platforms'], 3)
        
        # 验证状态管理器被调用
        self.status_manager.update_published_platforms.assert_called_once_with(
            self.temp_path.stem, ['wechat', 'github']
        )
    
    def test_update_status_no_manager(self):
        """测试没有状态管理器的情况"""
        workflow = IntegratedContentWorkflow()
        
        context = {'draft_path': self.temp_path}
        results = {}
        
        result = workflow._update_status(context, results)
        
        self.assertFalse(result['status_updated'])
    
    def test_update_status_exception(self):
        """测试状态更新异常"""
        self.status_manager.update_published_platforms.side_effect = Exception("Status error")
        
        context = {'draft_path': self.temp_path}
        results = {'publish_to_platforms': {'successful_platforms': []}}
        
        result = self.workflow._update_status(context, results)
        
        self.assertFalse(result['status_updated'])
        self.assertIn('error', result)
    
    def test_fix_frontmatter_quotes(self):
        """测试Front Matter引号修复"""
        content = """---
title: Article with "quotes" and special: characters
description: This has 'mixed quotes' and: colons
---

Content here"""
        
        fixed_content = self.workflow._fix_frontmatter_quotes(content)
        
        self.assertIn('title: "Article with \\"quotes\\" and special: characters"', fixed_content)
        self.assertIn('description: "This has \'mixed quotes\' and: colons"', fixed_content)
    
    def test_integrated_workflow_execution(self):
        """测试集成工作流完整执行"""
        # 配置所有mock的返回值
        self.image_processor.check_image_paths.return_value = []
        
        mock_post = Mock()
        mock_post.metadata = {'title': 'Test', 'date': '2023-01-01'}
        # 确保内容长度超过100个字符
        mock_post.content = 'Test content with sufficient length for validation ' * 3
        
        self.ai_processor.generate_excerpt.return_value = 'Generated excerpt'
        self.platform_processor.generate_platform_content.return_value = 'Adapted content'
        self.platform_processor.publish_to_platform.return_value = True
        
        with patch('frontmatter.loads', return_value=mock_post):
            with patch('builtins.print'):
                context = {
                    'draft_path': self.temp_path,
                    'platforms': ['wechat'],
                    'enable_categorization': False  # 简化测试
                }
                
                result = self.workflow.execute(context)
        
        self.assertTrue(result.success)
        self.assertEqual(result.steps_failed, 0)
        self.assertGreater(result.steps_completed, 5)


if __name__ == '__main__':
    unittest.main()