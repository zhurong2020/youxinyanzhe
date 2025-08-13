"""
测试内容处理工作流模块
"""
import unittest
from unittest.mock import Mock, patch, mock_open
from pathlib import Path
import tempfile
import os
import logging
from typing import Dict, Any

# 添加项目根目录到Python路径
import sys
sys.path.append('/home/wuxia/projects/youxinyanzhe')

from scripts.core.workflows.content_workflow import (
    WorkflowEngine,
    ContentProcessingWorkflow,
    WorkflowStep,
    WorkflowResult,
    WorkflowStepStatus,
    WorkflowRegistry,
    workflow_registry
)


class TestWorkflowStep(unittest.TestCase):
    """测试工作流步骤"""
    
    def test_workflow_step_creation(self):
        """测试工作流步骤创建"""
        def dummy_function():
            return "test"
        
        step = WorkflowStep(
            name="test_step",
            description="Test Step", 
            function=dummy_function,
            required=True
        )
        
        self.assertEqual(step.name, "test_step")
        self.assertEqual(step.description, "Test Step")
        self.assertEqual(step.function, dummy_function)
        self.assertTrue(step.required)
        self.assertEqual(step.status, WorkflowStepStatus.PENDING)
        self.assertIsNone(step.result)
        self.assertIsNone(step.error)


class TestWorkflowResult(unittest.TestCase):
    """测试工作流结果"""
    
    def test_workflow_result_creation(self):
        """测试工作流结果创建"""
        result = WorkflowResult(
            success=True,
            steps_completed=5,
            steps_failed=0,
            steps_skipped=1,
            results={"step1": "result1"},
            errors=[]
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.steps_completed, 5)
        self.assertEqual(result.steps_failed, 0)
        self.assertEqual(result.steps_skipped, 1)
        self.assertEqual(result.results, {"step1": "result1"})
        self.assertEqual(result.errors, [])


class TestWorkflowEngine(unittest.TestCase):
    """测试工作流引擎抽象基类"""
    
    def setUp(self):
        """设置测试环境"""
        self.logger = Mock(spec=logging.Logger)
        
        # 创建一个具体的工作流实现用于测试
        class TestWorkflow(WorkflowEngine):
            def execute(self, context):
                return WorkflowResult(
                    success=True,
                    steps_completed=1,
                    steps_failed=0,
                    steps_skipped=0,
                    results={},
                    errors=[]
                )
        
        self.workflow = TestWorkflow(self.logger)
    
    def test_workflow_engine_initialization(self):
        """测试工作流引擎初始化"""
        self.assertEqual(self.workflow.logger, self.logger)
        self.assertEqual(len(self.workflow.steps), 0)
    
    def test_add_step(self):
        """测试添加步骤"""
        def dummy_function():
            return "test"
        
        step = self.workflow.add_step(
            "test_step", 
            "Test Description", 
            dummy_function, 
            required=False
        )
        
        self.assertEqual(len(self.workflow.steps), 1)
        self.assertEqual(step.name, "test_step")
        self.assertEqual(step.description, "Test Description")
        self.assertEqual(step.function, dummy_function)
        self.assertFalse(step.required)
    
    def test_log_method(self):
        """测试日志记录方法"""
        with patch('builtins.print') as mock_print:
            self.workflow.log("Test message", level="info")
            self.logger.info.assert_called_once_with("Test message")
            mock_print.assert_not_called()
            
            # 测试强制打印
            self.workflow.log("Test message 2", level="warning", force=True)
            self.logger.warning.assert_called_once_with("Test message 2")
            mock_print.assert_called_once_with("[WARNING] Test message 2")


class TestContentProcessingWorkflow(unittest.TestCase):
    """测试内容处理工作流"""
    
    def setUp(self):
        """设置测试环境"""
        self.logger = Mock(spec=logging.Logger)
        self.workflow = ContentProcessingWorkflow(self.logger)
        
        # 创建临时文件
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        self.temp_file.write("---\ntitle: Test Article\ndate: 2023-01-01\n---\n\nThis is test content with more than 100 characters to ensure it passes the length validation check.")
        self.temp_file.close()
        self.temp_path = Path(self.temp_file.name)
    
    def tearDown(self):
        """清理测试环境"""
        if self.temp_path.exists():
            os.unlink(self.temp_path)
    
    def test_workflow_initialization(self):
        """测试工作流初始化"""
        self.assertEqual(self.workflow.logger, self.logger)
        self.assertEqual(len(self.workflow.steps), 9)  # 默认步骤数量
        
        # 检查默认步骤
        step_names = [step.name for step in self.workflow.steps]
        expected_steps = [
            "validate_input", "load_content", "parse_frontmatter",
            "validate_content", "process_images", "enhance_content",
            "generate_platforms_content", "publish_to_platforms", "update_status"
        ]
        self.assertEqual(step_names, expected_steps)
    
    def test_validate_input_success(self):
        """测试输入验证成功"""
        context = {
            'draft_path': self.temp_path,
            'platforms': ['wechat', 'github']
        }
        results = {}
        
        result = self.workflow._validate_input(context, results)
        self.assertEqual(result, {"valid": True})
    
    def test_validate_input_missing_parameter(self):
        """测试输入验证缺少参数"""
        context = {'draft_path': self.temp_path}  # 缺少platforms
        results = {}
        
        with self.assertRaises(ValueError) as cm:
            self.workflow._validate_input(context, results)
        self.assertIn("缺少必需参数: platforms", str(cm.exception))
    
    def test_validate_input_file_not_exists(self):
        """测试输入验证文件不存在"""
        context = {
            'draft_path': Path("/nonexistent/file.md"),
            'platforms': ['wechat']
        }
        results = {}
        
        with self.assertRaises(ValueError) as cm:
            self.workflow._validate_input(context, results)
        self.assertIn("草稿文件不存在", str(cm.exception))
    
    def test_load_content_success(self):
        """测试加载内容成功"""
        context = {'draft_path': self.temp_path}
        results = {}
        
        content = self.workflow._load_content(context, results)
        self.assertIn("This is test content", content)
        self.assertGreater(len(content), 100)
    
    def test_load_content_too_short(self):
        """测试内容过短"""
        # 创建内容过短的文件
        short_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8')
        short_file.write("短内容")
        short_file.close()
        
        try:
            context = {'draft_path': Path(short_file.name)}
            results = {}
            
            with self.assertRaises(ValueError) as cm:
                self.workflow._load_content(context, results)
            self.assertIn("文章内容过短", str(cm.exception))
        finally:
            os.unlink(short_file.name)
    
    def test_parse_frontmatter_default(self):
        """测试默认的Front Matter解析"""
        context = {}
        results = {'load_content': 'test content'}
        
        result = self.workflow._parse_frontmatter(context, results)
        self.assertTrue(result['frontmatter_parsed'])
        self.assertEqual(result['content'], 'test content')
    
    def test_validate_content_default(self):
        """测试默认的内容验证"""
        context = {}
        results = {}
        
        result = self.workflow._validate_content(context, results)
        self.assertTrue(result['content_valid'])
    
    def test_generate_platforms_content(self):
        """测试平台内容生成"""
        context = {'platforms': ['wechat', 'github']}
        results = {'load_content': 'test content'}
        
        result = self.workflow._generate_platforms_content(context, results)
        platform_contents = result['platform_contents']
        
        self.assertIn('wechat', platform_contents)
        self.assertIn('github', platform_contents)
        self.assertEqual(platform_contents['wechat'], 'test content')
        self.assertEqual(platform_contents['github'], 'test content')
    
    def test_publish_to_platforms(self):
        """测试平台发布"""
        context = {'platforms': ['wechat']}
        results = {
            'generate_platforms_content': {
                'platform_contents': {'wechat': 'test content'}
            }
        }
        
        result = self.workflow._publish_to_platforms(context, results)
        self.assertTrue(result['publish_results']['wechat'])
    
    def test_update_status(self):
        """测试状态更新"""
        context = {'platforms': ['wechat', 'github']}
        results = {
            'publish_to_platforms': {
                'publish_results': {'wechat': True, 'github': False}
            }
        }
        
        result = self.workflow._update_status(context, results)
        self.assertEqual(result['successful_platforms'], ['wechat'])
        self.assertEqual(result['total_platforms'], 2)
        self.assertTrue(result['status_updated'])
    
    def test_execute_successful_workflow(self):
        """测试成功的工作流执行"""
        context = {
            'draft_path': self.temp_path,
            'platforms': ['wechat']
        }
        
        with patch('builtins.print'):
            result = self.workflow.execute(context)
        
        self.assertTrue(result.success)
        self.assertEqual(result.steps_failed, 0)
        self.assertGreater(result.steps_completed, 0)
        self.assertIn('validate_input', result.results)
        self.assertIn('load_content', result.results)
    
    def test_execute_with_required_step_failure(self):
        """测试必需步骤失败的工作流执行"""
        # 找到第一个必需步骤并让它直接引发异常
        validate_input_step = self.workflow.steps[0]  # validate_input
        self.assertTrue(validate_input_step.required)
        
        # 直接修改步骤的function来引发异常
        def failing_function(_, __):
            raise ValueError("Test error")
        
        validate_input_step.function = failing_function
        
        context = {
            'draft_path': self.temp_path,
            'platforms': ['wechat']
        }
        
        with patch('builtins.print'):
            result = self.workflow.execute(context)
        
        self.assertFalse(result.success)
        self.assertEqual(result.steps_failed, 1)
        self.assertGreater(len(result.errors), 0)
        
        # 验证第一个步骤失败后工作流停止
        self.assertEqual(result.steps_completed, 0)
    
    def test_execute_with_optional_step_failure(self):
        """测试可选步骤失败的工作流执行"""
        # 找到process_images步骤并使其失败
        process_images_step = next(step for step in self.workflow.steps if step.name == "process_images")
        self.assertFalse(process_images_step.required)  # 确认是可选步骤
        
        # 直接修改步骤的function来引发异常
        def failing_function(_, __):
            raise Exception("Image processing failed")
        
        process_images_step.function = failing_function
        
        context = {
            'draft_path': self.temp_path,
            'platforms': ['wechat']
        }
        
        with patch('builtins.print'):
            result = self.workflow.execute(context)
        
        # 工作流应该继续执行，因为process_images是可选的
        self.assertTrue(result.success)
        self.assertEqual(result.steps_skipped, 1)
        self.assertEqual(result.steps_failed, 0)
        self.assertGreater(result.steps_completed, 4)  # 应该完成其他步骤


class TestWorkflowRegistry(unittest.TestCase):
    """测试工作流注册器"""
    
    def setUp(self):
        """设置测试环境"""
        self.registry = WorkflowRegistry()
    
    def test_register_and_get_workflow(self):
        """测试注册和获取工作流"""
        class TestWorkflow(WorkflowEngine):
            def execute(self, _: Dict[str, Any]) -> WorkflowResult:
                return WorkflowResult(
                    success=True,
                    steps_completed=0,
                    steps_failed=0,
                    steps_skipped=0,
                    results={},
                    errors=[]
                )
        
        self.registry.register("test_workflow", TestWorkflow)
        retrieved_class = self.registry.get("test_workflow")
        
        self.assertEqual(retrieved_class, TestWorkflow)
    
    def test_get_nonexistent_workflow(self):
        """测试获取不存在的工作流"""
        result = self.registry.get("nonexistent")
        self.assertIsNone(result)
    
    def test_list_workflows(self):
        """测试列出工作流"""
        class TestWorkflow1(WorkflowEngine):
            def execute(self, _: Dict[str, Any]) -> WorkflowResult:
                return WorkflowResult(
                    success=True,
                    steps_completed=0,
                    steps_failed=0,
                    steps_skipped=0,
                    results={},
                    errors=[]
                )
        
        class TestWorkflow2(WorkflowEngine):
            def execute(self, _: Dict[str, Any]) -> WorkflowResult:
                return WorkflowResult(
                    success=True,
                    steps_completed=0,
                    steps_failed=0,
                    steps_skipped=0,
                    results={},
                    errors=[]
                )
        
        self.registry.register("workflow1", TestWorkflow1)
        self.registry.register("workflow2", TestWorkflow2)
        
        workflows = self.registry.list_workflows()
        self.assertIn("workflow1", workflows)
        self.assertIn("workflow2", workflows)
        self.assertEqual(len(workflows), 2)


class TestGlobalWorkflowRegistry(unittest.TestCase):
    """测试全局工作流注册器"""
    
    def test_default_registration(self):
        """测试默认注册的工作流"""
        workflows = workflow_registry.list_workflows()
        self.assertIn("content_processing", workflows)
        
        workflow_class = workflow_registry.get("content_processing")
        self.assertEqual(workflow_class, ContentProcessingWorkflow)


if __name__ == '__main__':
    unittest.main()