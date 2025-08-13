"""
菜单系统处理模块
负责用户界面显示和交互处理
"""
from scripts.core.content_pipeline import ContentPipeline


class MenuHandler:
    """菜单处理器 - 负责用户界面和交互逻辑"""
    
    def __init__(self, pipeline: ContentPipeline):
        """
        初始化菜单处理器
        
        Args:
            pipeline: 内容管道实例
        """
        self.pipeline = pipeline
        self.choice_names = {
            '1': '智能内容发布', '2': '内容规范化处理', '3': '智能内容创作',
            '4': 'YouTube内容处理', '5': 'OneDrive图床管理', '6': '内容变现管理',
            '7': '语音和音频工具', '8': '文章更新工具', '9': '系统工具集合', '0': '退出'
        }
    
    def display_main_menu(self) -> None:
        """显示主菜单"""
        print("\n" + "="*60)
        print("🛠️ 有心工坊 v2.0")
        print("   YouXin Workshop")
        print()
        print("💡 为有心人打造的数字创作平台")
        print("📝 学习 · 分享 · 进步")
        print("="*60)
        print("📝 内容工作流程：")
        print("1. 智能内容发布")      # 合并1+2
        print("2. 内容规范化处理")    # 保持原4
        print("3. 智能内容创作")      # 合并5+3，提升位置
        print("4. YouTube内容处理")   # 合并8+13
        print("\n🛠️ 系统管理：")
        print("5. OneDrive图床管理")  # 保持原14
        print("6. 内容变现管理")      # 保持原6
        print("7. 语音和音频工具")    # 合并12+相关
        print("8. 文章更新工具")      # 保持原9
        print("9. 系统工具集合")      # 合并7+10+11
        print("\n0. 退出")
    
    def get_user_choice(self) -> str:
        """
        获取用户选择
        
        Returns:
            用户输入的选项字符串
        """
        return input("\n请输入选项 (1-9/0): ").strip()
    
    def log_user_action(self, choice: str) -> None:
        """
        记录用户选择的操作
        
        Args:
            choice: 用户选择的选项
        """
        operation_name = self.choice_names.get(choice, '无效选择')
        self.pipeline.log(f"用户选择操作: {choice} ({operation_name})", level="info", force=True)
    
    def is_valid_choice(self, choice: str) -> bool:
        """
        验证用户选择是否有效
        
        Args:
            choice: 用户选择
            
        Returns:
            选择是否有效
        """
        return choice in self.choice_names
    
    def get_operation_name(self, choice: str) -> str:
        """
        获取操作名称
        
        Args:
            choice: 用户选择
            
        Returns:
            操作名称
        """
        return self.choice_names.get(choice, '无效选择')
    
    def display_invalid_choice_message(self, choice: str) -> None:
        """
        显示无效选择提示
        
        Args:
            choice: 无效的选择
        """
        print(f"\n❌ 无效选择: {choice}")
        print("请输入 1-9 之间的数字，或输入 0 退出")
    
    def display_exit_message(self) -> None:
        """显示退出消息"""
        print("\n👋 感谢使用有心工坊！再见～")
        self.pipeline.log("用户退出系统", level="info", force=True)