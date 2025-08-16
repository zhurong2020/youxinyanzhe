"""
基础菜单处理器模块
提供所有菜单处理器的公共功能和标准接口
遵循重构后的分层架构原则
"""

from scripts.core.content_pipeline import ContentPipeline
from typing import List, Optional, Callable, Any


class BaseMenuHandler:
    """基础菜单处理器 - 提供公共菜单功能"""
    
    def __init__(self, pipeline: ContentPipeline, module_name: str = ""):
        """
        初始化基础菜单处理器
        
        Args:
            pipeline: 内容管道实例
            module_name: 模块名称，用于日志记录
        """
        self.pipeline = pipeline
        self.module_name = module_name
        self.menu_path = []  # 面包屑路径跟踪
    
    def push_menu_path(self, menu_id: str, menu_name: str) -> None:
        """
        添加菜单路径
        
        Args:
            menu_id: 菜单ID (如 "1", "1.1")
            menu_name: 菜单名称
        """
        self.menu_path.append({"id": menu_id, "name": menu_name})
    
    def pop_menu_path(self) -> None:
        """移除最后一层菜单路径"""
        if self.menu_path:
            self.menu_path.pop()
    
    def get_breadcrumb(self) -> str:
        """
        获取面包屑导航字符串
        
        Returns:
            面包屑导航路径
        """
        if not self.menu_path:
            return ""
        
        return " → ".join([f"{item['id']} {item['name']}" for item in self.menu_path])
    
    def display_menu_header(self, title: str, description: str = "", menu_id: str = "") -> None:
        """
        显示标准菜单头部
        
        Args:
            title: 菜单标题
            description: 菜单描述
            menu_id: 菜单ID，用于路径跟踪
        """
        print("\n" + "="*60)
        
        # 显示面包屑导航
        breadcrumb = self.get_breadcrumb()
        if breadcrumb:
            print(f"📍 路径: {breadcrumb}")
            if menu_id:
                print(f"📍 当前: {menu_id} {title}")
            print("="*60)
        
        print(title)
        print("="*60)
        if description:
            print(description)
    
    def display_menu_options(self, options: List[str]) -> None:
        """
        显示菜单选项列表
        
        Args:
            options: 选项列表
        """
        print("\n请选择操作：")
        for option in options:
            print(option)
        print("0. 返回上级菜单")
    
    def get_user_choice(self, max_choice: int) -> str:
        """
        获取用户选择并验证
        
        Args:
            max_choice: 最大选择数字
            
        Returns:
            用户输入的有效选择
        """
        return input(f"\n请选择 (1-{max_choice}/0): ").strip()
    
    def is_valid_choice(self, choice: str, max_choice: int) -> bool:
        """
        验证用户选择是否有效
        
        Args:
            choice: 用户选择
            max_choice: 最大有效选择
            
        Returns:
            选择是否有效
        """
        if choice == "0":
            return True
        
        try:
            choice_num = int(choice)
            return 1 <= choice_num <= max_choice
        except ValueError:
            return False
    
    def display_invalid_choice_message(self, choice: str, max_choice: int) -> None:
        """
        显示无效选择提示
        
        Args:
            choice: 无效的选择
            max_choice: 最大有效选择
        """
        print(f"\n❌ 无效选择: {choice}")
        print(f"请输入 1-{max_choice} 之间的数字，或输入 0 返回上级菜单")
    
    def log_action(self, action: str, details: str = "") -> None:
        """
        记录用户操作
        
        Args:
            action: 操作类型
            details: 操作详情
        """
        log_message = f"{self.module_name}: {action}" if self.module_name else action
        if details:
            log_message += f" - {details}"
        self.pipeline.log(log_message, level="info", force=True)
    
    def handle_error(self, error: Exception, operation: str) -> None:
        """
        统一错误处理
        
        Args:
            error: 异常对象
            operation: 出错的操作名称
        """
        error_msg = f"❌ {operation}时出错: {error}"
        print(error_msg)
        self.log_action(f"{operation}失败", str(error))
    
    def confirm_operation(self, message: str) -> bool:
        """
        确认操作
        
        Args:
            message: 确认消息
            
        Returns:
            用户是否确认
        """
        response = input(f"\n{message} (y/N): ").strip().lower()
        return response in ['y', 'yes', '是']
    
    def display_success_message(self, message: str) -> None:
        """
        显示成功消息
        
        Args:
            message: 成功消息
        """
        print(f"\n✅ {message}")
    
    def display_operation_cancelled(self) -> None:
        """显示操作取消消息"""
        print("\n⚠️ 操作已取消")
    
    def pause_for_user(self, message: str = "按回车键继续...") -> None:
        """
        暂停等待用户确认
        
        Args:
            message: 提示消息
        """
        input(f"\n{message}")
    
    def create_menu_loop(self, menu_title: str, menu_description: str, 
                        options: List[str], handlers: List[Callable]) -> Optional[Any]:
        """
        创建标准菜单循环
        
        Args:
            menu_title: 菜单标题
            menu_description: 菜单描述
            options: 选项列表
            handlers: 对应的处理函数列表
            
        Returns:
            处理函数的返回值，或None表示退出
        """
        if len(options) != len(handlers):
            raise ValueError("选项和处理函数数量不匹配")
        
        max_choice = len(options)
        
        while True:
            self.display_menu_header(menu_title, menu_description)
            self.display_menu_options(options)
            
            choice = self.get_user_choice(max_choice)
            
            if choice == "0":
                return None
            
            if not self.is_valid_choice(choice, max_choice):
                self.display_invalid_choice_message(choice, max_choice)
                continue
            
            try:
                choice_index = int(choice) - 1
                result = handlers[choice_index]()
                
                # 如果处理函数返回值，则退出菜单循环
                if result is not None:
                    return result
                    
            except Exception as e:
                self.handle_error(e, f"执行选项{choice}")
                continue
    
    def create_menu_loop_with_path(self, menu_title: str, menu_description: str, 
                                  options: List[str], handlers: List[Callable], 
                                  menu_id: str) -> Optional[Any]:
        """
        创建带路径跟踪的标准菜单循环
        
        Args:
            menu_title: 菜单标题
            menu_description: 菜单描述
            options: 选项列表
            handlers: 对应的处理函数列表
            menu_id: 菜单ID
            
        Returns:
            处理函数的返回值，或None表示退出
        """
        if len(options) != len(handlers):
            raise ValueError("选项和处理函数数量不匹配")
        
        max_choice = len(options)
        
        while True:
            self.display_menu_header(menu_title, menu_description, menu_id)
            self.display_menu_options(options)
            
            choice = self.get_user_choice(max_choice)
            
            if choice == "0":
                return None
            
            if not self.is_valid_choice(choice, max_choice):
                self.display_invalid_choice_message(choice, max_choice)
                continue
            
            try:
                choice_index = int(choice) - 1
                
                # 记录选择的子菜单路径
                selected_option = options[choice_index]
                option_id = selected_option.split()[0]  # 提取类似"1.1"的ID
                option_name = " ".join(selected_option.split()[1:])  # 提取名称
                
                self.log_action(f"用户选择: {option_id} {option_name}")
                
                result = handlers[choice_index]()
                
                # 如果处理函数返回值，则退出菜单循环
                if result is not None:
                    return result
                    
            except Exception as e:
                self.handle_error(e, f"执行选项{choice}")
                continue