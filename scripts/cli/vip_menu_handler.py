"""
VIP内容创作菜单处理模块
负责VIP多层内容创作的用户界面和交互处理
遵循重构后的分层架构原则
"""

from scripts.core.content_pipeline import ContentPipeline
from scripts.tools.content.vip_content_creator import VIPContentCreator
from typing import Optional


class VIPMenuHandler:
    """VIP内容创作菜单处理器 - 负责VIP创作相关的用户界面逻辑"""
    
    def __init__(self, pipeline: ContentPipeline):
        """
        初始化VIP菜单处理器
        
        Args:
            pipeline: 内容管道实例
        """
        self.pipeline = pipeline
        self.vip_creator = VIPContentCreator(pipeline)
    
    def display_vip_creation_menu(self) -> None:
        """显示VIP内容创作主菜单"""
        print("\n" + "="*50)
        print("📊 VIP多层内容创作")
        print("="*50)
        print("🎯 基于《草稿管理规范》的标准化多层VIP内容创作")
        print("\n📋 功能说明：")
        print("- 创建完整的四层内容架构 (免费 + VIP2 + VIP3 + VIP4)")
        print("- 自动生成标准化的Front Matter")
        print("- 遵循草稿管理和发布流程规范")
        print("- 支持Tesla投资系列的成功模式")
        
        print("\n请选择操作：")
        print("1. 🆕 创建新的VIP内容系列")
        print("2. 📁 管理现有VIP内容")
        print("3. 📊 查看VIP内容配置")
        print("4. 📋 显示创作流程指南")
        print("0. 返回上级菜单")
    
    def get_vip_choice(self) -> str:
        """
        获取VIP菜单用户选择
        
        Returns:
            用户输入的选项字符串
        """
        return input("\n请选择 (1-4/0): ").strip()
    
    def handle_vip_content_creation(self) -> Optional[str]:
        """
        处理VIP内容创作主流程
        
        Returns:
            创建成功时返回策略文件路径，否则返回None
        """
        while True:
            self.display_vip_creation_menu()
            choice = self.get_vip_choice()
            
            if choice == "1":
                return self._handle_create_new_series()
            elif choice == "2":
                self._handle_manage_existing_content()
            elif choice == "3":
                self._handle_view_configuration()
            elif choice == "4":
                self._handle_show_workflow_guide()
            elif choice == "0":
                return None
            else:
                print("❌ 无效选择，请重新输入")
    
    def _handle_create_new_series(self) -> Optional[str]:
        """
        处理创建新VIP内容系列
        
        Returns:
            创建成功时返回策略文件路径，否则返回None
        """
        try:
            strategy_file = self.vip_creator.create_vip_content_series()
            if strategy_file:
                self.pipeline.log(f"VIP内容系列创建成功: {strategy_file}", level="info", force=True)
                return strategy_file
            else:
                print("❌ VIP内容系列创建已取消")
                return None
        except Exception as e:
            print(f"❌ 创建VIP内容系列时出错: {e}")
            self.pipeline.log(f"VIP内容创建失败: {e}", level="error", force=True)
            return None
    
    def _handle_manage_existing_content(self) -> None:
        """处理管理现有VIP内容"""
        try:
            self.vip_creator.manage_existing_vip_content()
        except Exception as e:
            print(f"❌ 管理VIP内容时出错: {e}")
            self.pipeline.log(f"VIP内容管理失败: {e}", level="error", force=True)
    
    def _handle_view_configuration(self) -> None:
        """处理查看VIP内容配置"""
        print("\n" + "="*40)
        print("📊 VIP内容配置概览")
        print("="*40)
        
        config = self.vip_creator.vip_config
        for tier_config in config['tiers'].values():
            print(f"\n{tier_config['display_name']} ({tier_config['price']}):")
            print(f"  技术字段: {tier_config['technical_field']}")
            print(f"  最小字数: {tier_config['min_length']}")
            print(f"  服务描述: {tier_config['description']}")
            print(f"  目标用户: {tier_config['target_audience']}")
        
        print(f"\n支持的内容分类:")
        for cat_key, cat_name in config['categories'].items():
            print(f"  {cat_key}: {cat_name}")
    
    def _handle_show_workflow_guide(self) -> None:
        """处理显示创作流程指南"""
        print("\n" + "="*50)
        print("📋 VIP多层内容创作流程指南")
        print("="*50)
        print("\n🎯 创作流程概览:")
        print("1. 📋 主题确定和资源评估")
        print("2. 📝 创建内容策略文档")
        print("3. 📁 生成标准化草稿结构")
        print("4. ✍️ 按层级创作内容")
        print("5. 🔍 质量检查和优化")
        print("6. 🚀 分步发布策略")
        print("7. 📊 草稿管理和归档")
        
        print("\n📊 内容层级标准:")
        print("🆓 免费内容: 3000+字, 40%价值, 建立信任")
        print("💎 VIP2: 8000+字, 专业数据+实用工具")
        print("🔥 VIP3: 12000+字, 机构策略+高管洞察") 
        print("👑 VIP4: 20000+字等值, 独家资源+专业服务")
        
        print("\n🔗 相关文档:")
        print("- docs/DRAFT_MANAGEMENT_GUIDELINES.md")
        print("- config/vip_content_config.yml")
        print("- Tesla投资系列作为成功案例参考")
        
        input("\n按回车键继续...")
    
    def log_vip_action(self, action: str, details: str = "") -> None:
        """
        记录VIP相关操作日志
        
        Args:
            action: 操作类型
            details: 操作详情
        """
        log_message = f"VIP内容创作: {action}"
        if details:
            log_message += f" - {details}"
        self.pipeline.log(log_message, level="info", force=True)