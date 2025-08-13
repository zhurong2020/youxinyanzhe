"""
测试菜单处理器模块
"""
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.cli.menu_handler import MenuHandler
from scripts.core.content_pipeline import ContentPipeline


class TestMenuHandler(unittest.TestCase):
    """测试MenuHandler类"""
    
    def setUp(self):
        """测试初始化"""
        # Mock ContentPipeline以避免真实初始化
        self.mock_pipeline = MagicMock(spec=ContentPipeline)
        self.menu_handler = MenuHandler(self.mock_pipeline)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.menu_handler.pipeline, self.mock_pipeline)
        self.assertIsInstance(self.menu_handler.choice_names, dict)
        self.assertEqual(len(self.menu_handler.choice_names), 10)  # 0-9选项
    
    def test_is_valid_choice(self):
        """测试选择验证"""
        # 有效选择
        self.assertTrue(self.menu_handler.is_valid_choice('1'))
        self.assertTrue(self.menu_handler.is_valid_choice('9'))
        self.assertTrue(self.menu_handler.is_valid_choice('0'))
        
        # 无效选择
        self.assertFalse(self.menu_handler.is_valid_choice('a'))
        self.assertFalse(self.menu_handler.is_valid_choice('10'))
        self.assertFalse(self.menu_handler.is_valid_choice(''))
    
    def test_get_operation_name(self):
        """测试获取操作名称"""
        self.assertEqual(self.menu_handler.get_operation_name('1'), '智能内容发布')
        self.assertEqual(self.menu_handler.get_operation_name('9'), '系统工具集合')
        self.assertEqual(self.menu_handler.get_operation_name('0'), '退出')
        self.assertEqual(self.menu_handler.get_operation_name('x'), '无效选择')
    
    def test_log_user_action(self):
        """测试用户操作日志"""
        self.menu_handler.log_user_action('1')
        self.mock_pipeline.log.assert_called_once_with(
            "用户选择操作: 1 (智能内容发布)", level="info", force=True
        )
    
    @patch('builtins.print')
    def test_display_main_menu(self, mock_print):
        """测试主菜单显示"""
        self.menu_handler.display_main_menu()
        
        # 验证print被调用
        self.assertTrue(mock_print.called)
        
        # 验证包含关键内容
        print_calls = [str(call.args[0]) for call in mock_print.call_args_list if call.args]
        menu_text = ' '.join(print_calls)
        
        self.assertIn('有心工坊', menu_text)
        self.assertIn('智能内容发布', menu_text)
        self.assertIn('系统工具集合', menu_text)
    
    @patch('builtins.input', return_value='1')
    def test_get_user_choice(self, mock_input):
        """测试获取用户选择"""
        choice = self.menu_handler.get_user_choice()
        self.assertEqual(choice, '1')
        mock_input.assert_called_once_with("\n请输入选项 (1-9/0): ")
    
    @patch('builtins.print')
    def test_display_invalid_choice_message(self, mock_print):
        """测试无效选择提示"""
        self.menu_handler.display_invalid_choice_message('x')
        self.assertTrue(mock_print.called)
        
        # 验证错误消息内容
        print_calls = [str(call.args[0]) for call in mock_print.call_args_list if call.args]
        error_text = ' '.join(print_calls)
        self.assertIn('无效选择', error_text)
        self.assertIn('x', error_text)
    
    @patch('builtins.print')
    def test_display_exit_message(self, mock_print):
        """测试退出消息"""
        self.menu_handler.display_exit_message()
        
        # 验证print和log都被调用
        self.assertTrue(mock_print.called)
        self.mock_pipeline.log.assert_called_once_with(
            "用户退出系统", level="info", force=True
        )


if __name__ == '__main__':
    unittest.main()