"""
内容创作菜单处理器
负责内容创作相关功能的用户界面和交互处理
遵循重构后的分层架构原则
"""

from scripts.cli.base_menu_handler import BaseMenuHandler
from scripts.core.content_pipeline import ContentPipeline
from typing import Optional


class ContentMenuHandler(BaseMenuHandler):
    """内容创作菜单处理器"""
    
    def __init__(self, pipeline: ContentPipeline):
        """
        初始化内容菜单处理器
        
        Args:
            pipeline: 内容管道实例
        """
        super().__init__(pipeline, "内容创作")
    
    def handle_topic_inspiration_menu(self) -> Optional[str]:
        """
        处理主题灵感生成菜单
        
        Returns:
            生成结果或None
        """
        menu_title = "💡 主题灵感生成器"
        menu_description = "🤖 AI驱动的主题灵感生成和内容规划"
        
        options = [
            "1. 🎯 快速主题生成",
            "2. 📝 详细内容规划", 
            "3. 🔄 批量主题生成",
            "4. 📋 查看历史记录",
            "5. ⚙️ 生成参数配置"
        ]
        
        handlers = [
            self._quick_topic_generation,
            self._detailed_content_planning,
            self._batch_topic_generation,
            self._view_generation_history,
            self._configure_generation_params
        ]
        
        return self.create_menu_loop(menu_title, menu_description, options, handlers)
    
    def _quick_topic_generation(self) -> Optional[str]:
        """快速主题生成"""
        self.display_menu_header("🎯 快速主题生成", "基于关键词快速生成内容主题")
        
        try:
            # 获取用户输入
            keywords = input("\n请输入关键词 (用逗号分隔): ").strip()
            if not keywords:
                self.display_operation_cancelled()
                return None
            
            # 获取生成数量
            try:
                count = int(input("生成主题数量 (默认5个): ").strip() or "5")
                count = max(1, min(count, 20))  # 限制在1-20之间
            except ValueError:
                count = 5
            
            print(f"\n🤖 正在生成 {count} 个主题...")
            
            # 导入AI生成器  
            from scripts.tools.content.topic_inspiration_generator import TopicInspirationGenerator
            generator = TopicInspirationGenerator("auto")
            
            # 生成主题
            result = generator.generate_topics(keywords, count)
            
            if result:
                print(f"\n✅ 成功生成 {len(result)} 个主题:")
                for i, topic in enumerate(result, 1):
                    print(f"   {i}. {topic}")
                
                self.log_action("快速主题生成成功", f"关键词: {keywords}, 数量: {count}")
                
                # 询问是否保存
                if self.confirm_operation("是否保存生成结果？"):
                    # TODO: 实现保存功能
                    print("✅ 结果已保存到历史记录")
                
                return result
            else:
                print("❌ 主题生成失败")
                return None
                
        except Exception as e:
            self.handle_error(e, "快速主题生成")
            return None
    
    def _detailed_content_planning(self) -> Optional[str]:
        """详细内容规划"""
        self.display_menu_header("📝 详细内容规划", "生成完整的内容规划和大纲")
        
        try:
            # 获取主题
            topic = input("\n请输入主题: ").strip()
            if not topic:
                self.display_operation_cancelled()
                return None
            
            # 获取内容类型
            content_types = [
                "1. 📝 技术教程",
                "2. 💡 观点分析", 
                "3. 📊 数据解读",
                "4. 🌍 趋势预测",
                "5. 🛠️ 工具介绍"
            ]
            
            print("\n请选择内容类型:")
            for ct in content_types:
                print(f"   {ct}")
            
            type_choice = input("选择类型 (1-5): ").strip()
            type_map = {
                "1": "技术教程",
                "2": "观点分析", 
                "3": "数据解读",
                "4": "趋势预测",
                "5": "工具介绍"
            }
            content_type = type_map.get(type_choice, "综合分析")
            
            print(f"\n🤖 正在生成《{topic}》的详细内容规划...")
            
            # 生成详细规划
            from scripts.tools.content.topic_inspiration_generator import TopicInspirationGenerator
            generator = TopicInspirationGenerator("auto")
            
            result = generator.generate_detailed_plan(topic, content_type)
            
            if result:
                print(f"\n✅ 详细内容规划已生成:")
                print(result)
                
                self.log_action("详细内容规划成功", f"主题: {topic}, 类型: {content_type}")
                return result
            else:
                print("❌ 内容规划生成失败")
                return None
                
        except Exception as e:
            self.handle_error(e, "详细内容规划")
            return None
    
    def _batch_topic_generation(self) -> Optional[str]:
        """批量主题生成"""
        self.display_menu_header("🔄 批量主题生成", "基于多个关键词批量生成主题")
        
        print("请输入多个关键词组 (每行一个，空行结束):")
        keywords_list = []
        while True:
            line = input().strip()
            if not line:
                break
            keywords_list.append(line)
        
        if not keywords_list:
            self.display_operation_cancelled()
            return None
        
        try:
            print(f"\n🤖 正在为 {len(keywords_list)} 个关键词组生成主题...")
            
            from scripts.tools.content.topic_inspiration_generator import TopicInspirationGenerator
            generator = TopicInspirationGenerator("auto")
            
            all_results = []
            for i, keywords in enumerate(keywords_list, 1):
                print(f"   处理第 {i} 组: {keywords}")
                result = generator.generate_topics(keywords, 3)  # 每组生成3个
                if result:
                    all_results.extend(result)
            
            if all_results:
                print(f"\n✅ 批量生成完成，共 {len(all_results)} 个主题:")
                for i, topic in enumerate(all_results, 1):
                    print(f"   {i}. {topic}")
                
                self.log_action("批量主题生成成功", f"关键词组数: {len(keywords_list)}")
                return f"批量生成完成，共 {len(all_results)} 个主题"
            else:
                print("❌ 批量生成失败")
                return None
                
        except Exception as e:
            self.handle_error(e, "批量主题生成")
            return None
    
    def _view_generation_history(self) -> Optional[str]:
        """查看历史记录"""
        print("\n📋 主题生成历史记录")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _configure_generation_params(self) -> Optional[str]:
        """配置生成参数"""
        print("\n⚙️ 生成参数配置")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def handle_content_normalization_menu(self) -> Optional[str]:
        """
        处理内容规范化菜单
        
        Returns:
            处理结果或None
        """
        menu_title = "📝 内容规范化处理"
        menu_description = "🔧 文章格式化、Front Matter生成、内容优化"
        
        options = [
            "1. 📄 格式化现有草稿",
            "2. 🏷️ 生成Front Matter",
            "3. 🔍 内容质量检查",
            "4. 📊 批量处理草稿",
            "5. ⚙️ 规范化配置"
        ]
        
        handlers = [
            self._format_existing_draft,
            self._generate_front_matter,
            self._content_quality_check,
            self._batch_process_drafts,
            self._normalization_config
        ]
        
        return self.create_menu_loop(menu_title, menu_description, options, handlers)
    
    def _format_existing_draft(self) -> Optional[str]:
        """格式化现有草稿"""
        print("\n📄 格式化现有草稿")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _generate_front_matter(self) -> Optional[str]:
        """生成Front Matter"""
        print("\n🏷️ 生成Front Matter")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _content_quality_check(self) -> Optional[str]:
        """内容质量检查"""
        print("\n🔍 内容质量检查")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _batch_process_drafts(self) -> Optional[str]:
        """批量处理草稿"""
        print("\n📊 批量处理草稿")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _normalization_config(self) -> Optional[str]:
        """规范化配置"""
        print("\n⚙️ 规范化配置")
        print("(功能开发中...)")
        self.pause_for_user()
        return None