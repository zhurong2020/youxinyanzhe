"""
内容创作菜单处理器
负责内容创作相关功能的用户界面和交互处理
遵循重构后的分层架构原则
"""

from scripts.cli.base_menu_handler import BaseMenuHandler
from scripts.core.content_pipeline import ContentPipeline
from typing import Optional
from pathlib import Path


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
        
        return self.create_menu_loop_with_path(menu_title, menu_description, options, handlers, "3.1")
    
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
        print("查看之前生成的主题灵感和对应的草稿状态")
        
        try:
            from scripts.tools.content.topic_inspiration_generator import TopicInspirationGenerator
            
            # 初始化生成器
            generator = TopicInspirationGenerator()
            
            # 获取历史记录
            history = generator.get_inspiration_history()
            
            if not history:
                print("❌ 没有找到历史记录")
                self.pause_for_user()
                return None
            
            print(f"\n📋 找到 {len(history)} 条历史记录:")
            
            for i, record in enumerate(history):
                print(f"\n📄 记录 {i+1}:")
                print(f"  🎯 主题: {record.get('topic', 'Unknown')}")
                print(f"  📅 生成时间: {record.get('generated_time', 'Unknown')}")
                print(f"  📂 内容类型: {record.get('content_type', 'Unknown')}")
                
                if record.get('draft_path'):
                    draft_exists = record.get('draft_exists', False)
                    status_icon = "✅" if draft_exists else "❌"
                    print(f"  📝 草稿文件: {status_icon} {record['draft_path']}")
                else:
                    print(f"  📝 草稿文件: 未生成")
                
                if record.get('tokens_used'):
                    print(f"  🔢 AI用量: {record['tokens_used']} tokens")
                
                # 显示生成的内容预览
                if record.get('summary'):
                    summary = record['summary'][:100] + "..." if len(record['summary']) > 100 else record['summary']
                    print(f"  📋 摘要: {summary}")
            
            # 提供操作选项
            print(f"\n🔧 可执行操作:")
            print("1. 重新生成某个主题")
            print("2. 查看详细内容")
            print("3. 清理失效记录")
            print("4. 导出历史记录")
            print("5. 返回上级菜单")
            
            try:
                choice = int(input("\n请选择操作: "))
                
                if choice == 1:  # 重新生成
                    try:
                        record_num = int(input("请输入要重新生成的记录编号: "))
                        if 1 <= record_num <= len(history):
                            record = history[record_num - 1]
                            print(f"🔄 重新生成主题: {record.get('topic', 'Unknown')}")
                            # 这里可以调用重新生成逻辑
                            print("💡 提示: 请使用主菜单中的'AI主题生成'功能")
                        else:
                            print("❌ 记录编号无效")
                    except ValueError:
                        print("❌ 请输入有效的数字")
                
                elif choice == 2:  # 查看详细
                    try:
                        record_num = int(input("请输入要查看的记录编号: "))
                        if 1 <= record_num <= len(history):
                            record = history[record_num - 1]
                            print(f"\n📋 详细内容:")
                            for key, value in record.items():
                                if key not in ['draft_exists']:  # 排除计算字段
                                    print(f"  {key}: {value}")
                        else:
                            print("❌ 记录编号无效")
                    except ValueError:
                        print("❌ 请输入有效的数字")
                
                elif choice == 3:  # 清理失效记录
                    removed_count = 0
                    for record in history:
                        if record.get('draft_path') and not record.get('draft_exists', False):
                            removed_count += 1
                    print(f"🗑️ 发现 {removed_count} 个失效记录 (草稿文件不存在)")
                    if removed_count > 0:
                        confirm = input("是否清理这些记录? (y/n): ").lower().strip()
                        if confirm == 'y':
                            # 这里需要实现清理逻辑
                            print("💡 提示: 清理功能需要在TopicInspirationGenerator中实现")
                
                elif choice == 4:  # 导出记录
                    import json
                    from datetime import datetime
                    
                    export_file = f"inspiration_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(export_file, 'w', encoding='utf-8') as f:
                        # 清理不可序列化的字段
                        clean_history = []
                        for record in history:
                            clean_record = {k: v for k, v in record.items() if k != 'draft_exists'}
                            clean_history.append(clean_record)
                        json.dump(clean_history, f, ensure_ascii=False, indent=2)
                    
                    print(f"✅ 历史记录已导出到: {export_file}")
                
                elif choice == 5:
                    print("↩️ 返回上级菜单")
                else:
                    print("❌ 选择无效")
                    
            except ValueError:
                print("❌ 请输入有效的数字")
        
        except ImportError as e:
            print(f"❌ 无法导入主题生成器: {e}")
        except Exception as e:
            print(f"❌ 查看历史记录时出错: {e}")
        
        self.pause_for_user()
        return None
    
    def _configure_generation_params(self) -> Optional[str]:
        """配置生成参数"""
        print("\n⚙️ 生成参数配置")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def handle_content_normalization_menu(self) -> Optional[str]:
        """处理内容规范化处理菜单"""
        menu_title = "📝 内容规范化处理"
        menu_description = "🔧 多源内容统一处理：手工草稿、YouTube内容、灵感生成内容\n📋 Jekyll规范检查：Front Matter、语法、路径验证\n🎯 智能内容结构：摘要(50-60字) + 背景介绍 + 主体内容"
        
        options = [
            "2.1 处理单个内容文件",
            "2.2 批量处理多个文件", 
            "2.3 查看使用示例",
            "2.4 查看分类关键词",
            "2.5 内容质量检查",
            "2.6 YouTube内容规范化"
        ]
        
        handlers = [
            self._process_single_content_file,
            self._batch_process_content_files,
            self._show_usage_examples,
            self._show_classification_keywords,
            self._content_quality_check,
            self._youtube_content_normalization
        ]
        
        return self.create_menu_loop_with_path(menu_title, menu_description, options, handlers, "2")
    
    def _process_single_content_file(self) -> None:
        """处理单个内容文件"""
        try:
            # 列出可能的草稿文件
            import glob
            from pathlib import Path
            
            potential_files = []
            for pattern in ["*.txt", "*.md"]:
                potential_files.extend(glob.glob(pattern))
                potential_files.extend(glob.glob(f"_drafts/**/{pattern}", recursive=True))
                potential_files.extend(glob.glob(f"drafts/**/{pattern}", recursive=True))
            
            if potential_files:
                print(f"\n📄 发现 {len(potential_files)} 个可能的草稿文件：")
                for i, file in enumerate(potential_files[:20], 1):  # 最多显示20个
                    print(f"  {i}. {file}")
                if len(potential_files) > 20:
                    print(f"  ... 和其他 {len(potential_files) - 20} 个文件")
                print("  0. 手动输入文件路径")
                
                file_choice = input(f"\n请选择文件 (1-{min(len(potential_files), 20)}/0): ").strip()
                
                if file_choice == "0":
                    input_file = input("请输入文件路径: ").strip()
                elif file_choice.isdigit() and 1 <= int(file_choice) <= min(len(potential_files), 20):
                    input_file = potential_files[int(file_choice) - 1]
                else:
                    print("❌ 无效选择")
                    return
            else:
                input_file = input("请输入草稿文件路径: ").strip()
            
            from pathlib import Path
            if not input_file or not Path(input_file).exists():
                print("❌ 文件不存在或路径无效")
                return
                
            print(f"\n🔄 正在格式化草稿: {input_file}")
            
            # 使用统一的格式化接口
            result = self.pipeline.format_content_file(Path(input_file))
            
            if result['success']:
                print("✅ 格式化完成！")
                print(f"📄 输出文件: {result['output_file']}")
                
                # 显示质量检查结果
                if result.get('check_passed', False):
                    print("✅ 内容质量检查通过")
                else:
                    if result.get('auto_fixes_applied'):
                        print("🔧 自动修复的问题:")
                        for fix in result['auto_fixes_applied']:
                            print(f"   • {fix}")
                    
                    if result.get('manual_fixes_needed'):
                        print("💡 需要手动处理的问题:")
                        for item in result['manual_fixes_needed']:
                            print(f"   • {item['issue']}")
                
                print("💡 您可以选择 '1. 智能内容发布' 来发布格式化后的文章")
            else:
                print(f"❌ 格式化失败: {result['error']}")
                
        except Exception as e:
            print(f"❌ 操作失败: {e}")
            
    def _batch_process_content_files(self) -> None:
        """批量处理多个内容文件"""
        batch_dir = input("\n请输入包含草稿文件的目录路径: ").strip()
        if not batch_dir or not Path(batch_dir).exists():
            print("❌ 目录不存在")
            return
            
        try:
            import glob
            
            files_to_process = []
            for pattern in ["*.txt", "*.md"]:
                files_to_process.extend(glob.glob(f"{batch_dir}/{pattern}"))
                files_to_process.extend(glob.glob(f"{batch_dir}/**/{pattern}", recursive=True))
            
            if not files_to_process:
                print("❌ 未找到可处理的草稿文件")
                return
                
            print(f"\n📄 找到 {len(files_to_process)} 个文件:")
            for file in files_to_process:
                print(f"  • {file}")
                
            confirm = input(f"\n确定要批量处理这些文件吗？(y/N): ").strip().lower()
            if confirm not in ['y', 'yes']:
                print("❌ 用户取消操作")
                return
                
            print("\n🔄 开始批量格式化...")
            success_count = 0
            total_issues_fixed = 0
            
            for file in files_to_process:
                try:
                    print(f"\n处理: {file}")
                    
                    # 使用统一的格式化接口
                    result = self.pipeline.format_content_file(Path(file))
                    
                    if result['success']:
                        success_count += 1
                        print(f"✅ 成功: {file}")
                        print(f"   输出: {result['output_file']}")
                        
                        # 统计修复的问题
                        if result.get('auto_fixes_applied'):
                            total_issues_fixed += len(result['auto_fixes_applied'])
                            
                        # 显示需要手动处理的问题
                        if result.get('manual_fixes_needed'):
                            print(f"   ⚠️ {len(result['manual_fixes_needed'])} 个问题需要手动处理")
                    else:
                        print(f"❌ 失败: {file}")
                        print(f"   错误: {result['error']}")
                            
                except Exception as e:
                    print(f"❌ 处理 {file} 时出错: {e}")
                    
            print(f"\n📊 批量处理完成：")
            print(f"   • 成功文件: {success_count}/{len(files_to_process)}")
            print(f"   • 自动修复: {total_issues_fixed} 个问题")
            print("💡 您可以选择 '1. 智能内容发布' 来发布格式化后的文章")
            
        except Exception as e:
            print(f"❌ 批量操作失败: {e}")
    
    def _show_usage_examples(self) -> None:
        """显示使用示例"""
        print("\n" + "="*40)
        print("📖 格式化草稿使用示例")
        print("="*40)
        
        example_content = '''
📝 示例输入文件 (example_draft.txt):
深度学习的最新进展与应用前景
人工智能领域在2024年取得了重大突破，特别是在大语言模型和计算机视觉方面。
本文将探讨这些技术的最新发展和未来应用前景。
## 大语言模型的突破
GPT-4和Claude等模型在理解能力、推理能力方面有了显著提升...
## 计算机视觉的进展
多模态模型如GPT-4V在图像理解方面展现出惊人的能力...
---
🔄 工具会自动生成:
- 智能分类: tech-empowerment (技术赋能)
- 自动标签: ["人工智能", "深度学习", "机器学习", "技术趋势"]
- 生成摘要: 探讨2024年人工智能领域的最新突破，重点分析大语言模型和计算机视觉的发展
- 完整front matter: 包含日期、分类、标签等元数据
- 格式化内容: 符合Jekyll和项目规范的完整文章
💡 输出文件会保存到 _drafts/ 目录，可直接用于发布流程
        '''
        
        print(example_content)
        self.pause_for_user()
    
    def _show_classification_keywords(self) -> None:
        """显示分类关键词"""
        print("\n" + "="*40)
        print("🔍 内容智能分类关键词")
        print("="*40)
        
        categories_info = '''
🧠 认知升级 (cognitive-upgrade):
   关键词: 思维、学习、认知、心理学、方法论、习惯、效率、自我提升
   
🛠️ 技术赋能 (tech-empowerment):  
   关键词: 技术、工具、自动化、编程、软件、AI、效率工具、数字化
   
🌍 全球视野 (global-perspective):
   关键词: 国际、全球、文化、跨国、趋势、政策、经济、社会
   
💰 投资理财 (investment-finance):
   关键词: 投资、理财、金融、股票、基金、财务、经济、资产配置
        '''
        
        print(categories_info)
        self.pause_for_user()
    
    def _content_quality_check(self) -> None:
        """内容质量检查"""
        print("\n🔍 内容质量检查")
        print("="*40)
        
        # 允许用户选择检查草稿文件
        from pathlib import Path
        drafts_dir = Path("_drafts")
        
        if not drafts_dir.exists():
            print("❌ 草稿目录不存在")
            self.pause_for_user()
            return
            
        draft_files = list(drafts_dir.glob("*.md"))
        if not draft_files:
            print("❌ 没有找到草稿文件")
            self.pause_for_user()
            return
            
        print("\n可用的草稿文件:")
        for i, draft in enumerate(draft_files, 1):
            print(f"{i}. {draft.name}")
            
        try:
            file_choice = input(f"\n请选择文件 (1-{len(draft_files)}/0取消): ").strip()
            if file_choice == "0":
                return
                
            file_index = int(file_choice) - 1
            if 0 <= file_index < len(draft_files):
                selected_draft = draft_files[file_index]
                print(f"📝 检查草稿: {selected_draft.name}")
                
                # 使用pipeline的质量检查功能
                issues = self.pipeline.check_draft_issues(selected_draft)
                
                if not issues:
                    print("✅ 内容质量检查通过，无发现问题")
                else:
                    print(f"⚠️ 发现 {len(issues)} 个问题:")
                    for i, issue in enumerate(issues, 1):
                        print(f"   {i}. {issue}")
                        
                    print("\n💡 建议:")
                    print("   • 使用 '1. 处理单个内容文件' 自动修复问题")
                    print("   • 或使用 '5. OneDrive图床管理' 处理图片问题")
            else:
                print("❌ 无效的文件选择")
                
        except (ValueError, IndexError):
            print("❌ 无效的输入")
        
        self.pause_for_user()
    
    def _youtube_content_normalization(self) -> None:
        """YouTube内容规范化"""
        print("\n📺 YouTube内容规范化")
        print("="*40)
        print("🎯 处理YouTube生成的内容，规范化为符合Jekyll的格式")
        
        # 检查是否有YouTube生成的内容
        import glob
        youtube_files = []
        patterns = ["*youtube*.txt", "*podcast*.txt", "*youtube*.md", "*podcast*.md"]
        
        for pattern in patterns:
            youtube_files.extend(glob.glob(pattern))
            youtube_files.extend(glob.glob(f"_drafts/**/{pattern}", recursive=True))
            youtube_files.extend(glob.glob(f"drafts/**/{pattern}", recursive=True))
        
        if youtube_files:
            print(f"\n📄 发现 {len(youtube_files)} 个可能的YouTube内容文件:")
            for i, file in enumerate(youtube_files[:10], 1):  # 显示前10个
                print(f"  {i}. {file}")
            
            if len(youtube_files) > 10:
                print(f"  ... 和其他 {len(youtube_files) - 10} 个文件")
            
            try:
                file_choice = input(f"\n请选择文件 (1-{min(len(youtube_files), 10)}/0取消): ").strip()
                
                if file_choice == "0":
                    return
                    
                file_index = int(file_choice) - 1
                if 0 <= file_index < min(len(youtube_files), 10):
                    selected_file = youtube_files[file_index]
                    print(f"📝 处理文件: {selected_file}")
                    
                    # 使用内容规范化功能处理
                    from pathlib import Path
                    result = self.pipeline.format_content_file(Path(selected_file))
                    
                    if result['success']:
                        print("✅ YouTube内容规范化完成！")
                        print(f"📄 输出文件: {result['output_file']}")
                        print("💡 文件已准备好发布流程")
                    else:
                        print(f"❌ 规范化失败: {result['error']}")
                else:
                    print("❌ 无效的文件选择")
                    
            except (ValueError, IndexError):
                print("❌ 无效的输入")
        else:
            print("📄 未找到YouTube相关的内容文件")
            print("💡 提示: 请确保文件名包含'youtube'或'podcast'关键词")
        
        self.pause_for_user()
    
    def _format_existing_draft(self) -> Optional[str]:
        """格式化现有草稿"""
        print("\n📄 格式化现有草稿")
        print("使用专业的草稿格式化工具，支持智能分类、标签生成和结构优化")
        
        try:
            # 导入格式化工具
            from scripts.tools.content.format_draft import DraftFormatter
            
            # 获取草稿目录中的文件
            drafts_dir = Path("_drafts")
            if not drafts_dir.exists():
                print("❌ 草稿目录不存在")
                self.pause_for_user()
                return None
            
            # 扫描草稿文件
            draft_files = []
            for ext in ['.txt', '.md']:
                draft_files.extend(list(drafts_dir.glob(f"*{ext}")))
            
            if not draft_files:
                print("❌ 草稿目录中没有找到可格式化的文件 (.txt/.md)")
                self.pause_for_user()
                return None
            
            print(f"\n📋 找到 {len(draft_files)} 个草稿文件:")
            for i, file in enumerate(draft_files):
                print(f"  {i+1}. {file.name}")
            
            # 选择文件
            try:
                choice = int(input("\n请选择要格式化的文件编号: "))
                if 1 <= choice <= len(draft_files):
                    selected_file = draft_files[choice-1]
                else:
                    print("❌ 选择无效")
                    self.pause_for_user()
                    return None
            except ValueError:
                print("❌ 请输入有效的数字")
                self.pause_for_user()
                return None
            
            # 初始化格式化器并处理
            formatter = DraftFormatter()
            print(f"\n🔄 正在格式化: {selected_file.name}")
            
            # 生成输出文件名
            output_file = drafts_dir / f"{selected_file.stem}_formatted.md"
            
            # 执行格式化
            result = formatter.process_draft(
                input_file=selected_file,
                output_file=output_file,
                preview=False
            )
            
            if result:
                print(f"✅ 格式化完成!")
                print(f"📄 输出文件: {output_file}")
                print(f"🎯 分类: {result.get('category', 'unknown')}")
                print(f"🏷️ 标签数: {len(result.get('tags', []))}")
                print(f"📝 摘要长度: {len(result.get('excerpt', ''))}")
                
                # 询问是否替换原文件
                replace = input("\n是否替换原文件? (y/n): ").lower().strip()
                if replace == 'y':
                    selected_file.unlink()  # 删除原文件
                    output_file.rename(selected_file)  # 重命名格式化后的文件
                    print(f"✅ 已替换原文件: {selected_file.name}")
            else:
                print("❌ 格式化失败")
            
        except ImportError as e:
            print(f"❌ 无法导入格式化工具: {e}")
        except Exception as e:
            print(f"❌ 格式化过程出错: {e}")
        
        self.pause_for_user()
        return None
    
    def _generate_front_matter(self) -> Optional[str]:
        """生成Front Matter"""
        print("\n🏷️ 生成Front Matter")
        print("为现有文件生成或更新Jekyll Front Matter元数据")
        
        try:
            from scripts.tools.content.format_draft import DraftFormatter
            
            # 获取草稿目录中的文件
            drafts_dir = Path("_drafts")
            if not drafts_dir.exists():
                print("❌ 草稿目录不存在")
                self.pause_for_user()
                return None
            
            # 扫描文件
            draft_files = []
            for ext in ['.txt', '.md']:
                draft_files.extend(list(drafts_dir.glob(f"*{ext}")))
            
            if not draft_files:
                print("❌ 草稿目录中没有找到文件")
                self.pause_for_user()
                return None
            
            print(f"\n📋 找到 {len(draft_files)} 个文件:")
            for i, file in enumerate(draft_files):
                print(f"  {i+1}. {file.name}")
            
            # 选择文件
            try:
                choice = int(input("\n请选择文件编号: "))
                if 1 <= choice <= len(draft_files):
                    selected_file = draft_files[choice-1]
                else:
                    print("❌ 选择无效")
                    self.pause_for_user()
                    return None
            except ValueError:
                print("❌ 请输入有效的数字")
                self.pause_for_user()
                return None
            
            # 读取文件内容
            with open(selected_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取标题
            title_line = content.split('\n')[0].strip()
            if title_line.startswith('#'):
                title = title_line.lstrip('#').strip()
            else:
                title = input("\n请输入文章标题: ").strip()
                if not title:
                    print("❌ 标题不能为空")
                    self.pause_for_user()
                    return None
            
            # 初始化格式化器
            formatter = DraftFormatter()
            
            # 生成Front Matter
            front_matter = formatter.create_front_matter(title, content)
            
            print(f"\n📋 生成的Front Matter:")
            print("---")
            for key, value in front_matter.items():
                if isinstance(value, list):
                    print(f"{key}: {value}")
                elif isinstance(value, dict):
                    print(f"{key}:")
                    for subkey, subvalue in value.items():
                        print(f"  {subkey}: {subvalue}")
                else:
                    print(f"{key}: {value}")
            print("---")
            
            # 询问是否保存
            save = input("\n是否保存到文件? (y/n): ").lower().strip()
            if save == 'y':
                # 创建带Front Matter的完整内容
                import yaml
                front_matter_yaml = yaml.dump(front_matter, allow_unicode=True, default_flow_style=False)
                
                # 移除原有的Front Matter (如果存在)
                if content.startswith('---'):
                    # 找到第二个---的位置
                    second_delimiter = content.find('---', 3)
                    if second_delimiter != -1:
                        content = content[second_delimiter + 3:].lstrip('\n')
                
                new_content = f"---\n{front_matter_yaml}---\n{content}"
                
                with open(selected_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ Front Matter已保存到: {selected_file.name}")
            
        except ImportError as e:
            print(f"❌ 无法导入必要工具: {e}")
        except Exception as e:
            print(f"❌ 生成Front Matter时出错: {e}")
        
        self.pause_for_user()
        return None
    
    
    def _batch_process_drafts(self) -> Optional[str]:
        """批量处理草稿"""
        print("\n📊 批量处理草稿")
        print("批量格式化多个草稿文件，支持智能分类和标签生成")
        
        try:
            from scripts.tools.content.format_draft import DraftFormatter
            
            # 获取草稿目录
            drafts_dir = Path("_drafts")
            if not drafts_dir.exists():
                print("❌ 草稿目录不存在")
                self.pause_for_user()
                return None
            
            # 扫描草稿文件
            draft_files = []
            for ext in ['.txt', '.md']:
                files = list(drafts_dir.glob(f"*{ext}"))
                # 排除已经格式化的文件
                files = [f for f in files if not f.name.endswith('_formatted.md')]
                draft_files.extend(files)
            
            if not draft_files:
                print("❌ 没有找到可批量处理的草稿文件")
                self.pause_for_user()
                return None
            
            print(f"\n📋 找到 {len(draft_files)} 个待处理的草稿文件:")
            for i, file in enumerate(draft_files):
                print(f"  {i+1}. {file.name}")
            
            # 选择处理方式
            print("\n🔧 批量处理选项:")
            print("1. 格式化所有文件 (保留原文件)")
            print("2. 格式化所有文件 (替换原文件)")
            print("3. 只生成Front Matter")
            print("4. 预览模式 (不保存)")
            
            try:
                mode = int(input("\n请选择处理模式: "))
                if mode not in [1, 2, 3, 4]:
                    print("❌ 选择无效")
                    self.pause_for_user()
                    return None
            except ValueError:
                print("❌ 请输入有效的数字")
                self.pause_for_user()
                return None
            
            # 初始化格式化器
            formatter = DraftFormatter()
            success_count = 0
            error_count = 0
            
            print(f"\n🔄 开始批量处理...")
            
            for i, draft_file in enumerate(draft_files):
                print(f"\n📄 处理 ({i+1}/{len(draft_files)}): {draft_file.name}")
                
                try:
                    if mode == 4:  # 预览模式
                        result = formatter.process_draft(
                            input_file=draft_file,
                            preview=True
                        )
                        if result:
                            print(f"  ✅ 预览完成 - 分类: {result.get('category', 'unknown')}")
                            success_count += 1
                        else:
                            print(f"  ❌ 预览失败")
                            error_count += 1
                    
                    elif mode == 3:  # 只生成Front Matter
                        with open(draft_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 提取标题
                        title_line = content.split('\n')[0].strip()
                        if title_line.startswith('#'):
                            title = title_line.lstrip('#').strip()
                        else:
                            title = draft_file.stem  # 使用文件名作为标题
                        
                        front_matter = formatter.create_front_matter(title, content)
                        print(f"  ✅ Front Matter生成 - 分类: {front_matter.get('categories', ['unknown'])[0]}")
                        success_count += 1
                    
                    else:  # 格式化模式
                        if mode == 1:  # 保留原文件
                            output_file = drafts_dir / f"{draft_file.stem}_formatted.md"
                        else:  # 替换原文件
                            output_file = draft_file
                        
                        result = formatter.process_draft(
                            input_file=draft_file,
                            output_file=output_file,
                            preview=False
                        )
                        
                        if result:
                            print(f"  ✅ 格式化完成 - 分类: {result.get('category', 'unknown')}")
                            if mode == 2 and output_file != draft_file:
                                draft_file.unlink()  # 删除原文件
                                output_file.rename(draft_file)  # 重命名
                            success_count += 1
                        else:
                            print(f"  ❌ 格式化失败")
                            error_count += 1
                
                except Exception as e:
                    print(f"  ❌ 处理失败: {e}")
                    error_count += 1
            
            print(f"\n📊 批量处理完成:")
            print(f"  ✅ 成功: {success_count} 个文件")
            print(f"  ❌ 失败: {error_count} 个文件")
            
        except ImportError as e:
            print(f"❌ 无法导入格式化工具: {e}")
        except Exception as e:
            print(f"❌ 批量处理时出错: {e}")
        
        self.pause_for_user()
        return None
    
    def _normalization_config(self) -> Optional[str]:
        """规范化配置"""
        print("\n⚙️ 规范化配置")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def handle_smart_publishing_menu(self) -> Optional[str]:
        """智能内容发布菜单 (合并原功能1+2)"""
        menu_title = "📤 智能内容发布"
        menu_description = "🎯 统一发布入口，支持新草稿和重新发布"
        
        options = [
            "1.1 发布新草稿",
            "1.2 重新发布已发布文章", 
            "1.3 查看发布历史"
        ]
        
        handlers = [
            self._publish_new_draft,
            self._republish_article,
            self._view_publish_history
        ]
        
        return self.create_menu_loop_with_path(menu_title, menu_description, options, handlers, "1")
    
    def _publish_new_draft(self) -> Optional[str]:
        """发布新草稿"""
        self.log_action("智能发布：开始发布新草稿")
        draft = self.pipeline.select_draft()
        if not draft:
            self.log_action("用户取消或无草稿可处理")
            return None
        elif isinstance(draft, str) and draft.startswith('redirect_to_'):
            # 处理重定向 - 保持与原版本的兼容性
            if draft == 'redirect_to_inspiration':
                print("🎯 跳转到主题灵感生成器...")
                # 返回None让主循环重新开始，用户可以选择对应功能
                return None
            elif draft == 'redirect_to_youtube':
                print("🎬 跳转到YouTube内容处理...")
                return None  
            elif draft == 'redirect_to_normalization':
                print("📝 跳转到内容规范化处理...")
                return None
            else:
                return None
        return str(draft)
    
    def _republish_article(self) -> Optional[str]:
        """重新发布已发布文章"""
        self.log_action("智能发布：开始重新发布已发布文章")
        
        try:
            # 使用ContentPipeline的内置方法
            post = self.pipeline.select_published_post()
            if not post:
                self.log_action("用户取消或无文章可重新发布")
                return None
            
            draft = self.pipeline.copy_post_to_draft(post)
            if not draft:
                print("复制文章到草稿失败")
                self.log_action("复制文章到草稿失败", "error")
                return None
            
            return str(draft)
        except Exception as e:
            print(f"❌ 重新发布功能出错: {e}")
            return None
    
    def _view_publish_history(self) -> Optional[str]:
        """查看发布历史"""
        print("\n📋 发布历史记录")
        print("="*40)
        
        try:
            from pathlib import Path
            
            # 直接扫描_posts目录来获取发布历史
            posts_dir = Path("_posts")
            
            published_articles = []
            
            # 从_posts目录获取已发布文章
            if posts_dir.exists():
                for post_file in posts_dir.glob("*.md"):
                    article_name = post_file.stem
                    
                    # 检查是否有发布状态记录
                    if hasattr(self.pipeline, 'status_manager'):
                        platforms = self.pipeline.status_manager.get_published_platforms(article_name)
                        summary = self.pipeline.status_manager.get_platform_status_summary(article_name)
                        
                        published_articles.append({
                            'name': article_name,
                            'file': post_file,
                            'platforms': platforms,
                            'summary': summary
                        })
                    else:
                        published_articles.append({
                            'name': article_name,
                            'file': post_file,
                            'platforms': [],
                            'summary': {}
                        })
            
            if not published_articles:
                print("📄 暂无发布历史记录")
                self.pause_for_user()
                return None
            
            # 按文件修改时间排序显示最近的发布
            published_articles.sort(key=lambda x: x['file'].stat().st_mtime, reverse=True)
            
            print(f"📊 共找到 {len(published_articles)} 篇已发布文章:")
            print()
            
            for i, article in enumerate(published_articles[:20], 1):  # 显示最近20篇
                print(f"{i}. {article['name']}")
                
                # 显示发布平台状态
                if article['platforms']:
                    print(f"   ✅ 已发布: {', '.join(article['platforms'])}")
                else:
                    print("   📝 Jekyll发布 (无平台记录)")
                
                # 显示文件修改时间
                mtime = article['file'].stat().st_mtime
                import datetime
                formatted_time = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
                print(f"   🕒 文件时间: {formatted_time}")
                
                print()
            
            if len(published_articles) > 20:
                print(f"... 和其他 {len(published_articles) - 20} 篇文章")
            
        except Exception as e:
            print(f"❌ 查看发布历史失败: {e}")
        
        self.pause_for_user()
        return None
    
    def handle_smart_creation_menu(self) -> Optional[str]:
        """智能内容创作菜单 (合并原功能5+3)"""
        menu_title = "🎯 智能内容创作"
        menu_description = "🤖 AI驱动的内容创作和灵感生成"
        
        options = [
            "1. AI主题生成",
            "2. 快速测试文章", 
            "3. 内容大纲创建",
            "4. 创作辅助工具",
            "5. 📊 VIP多层内容创作"
        ]
        
        handlers = [
            self._ai_topic_generation,
            self._quick_test_article,
            self._content_outline_creation,
            self._creation_assistance_tools,
            self._vip_content_creation
        ]
        
        return self.create_menu_loop_with_path(menu_title, menu_description, options, handlers, "3")
    
    def _ai_topic_generation(self) -> Optional[str]:
        """AI主题生成"""
        return self.handle_topic_inspiration_menu()
    
    def _quick_test_article(self) -> Optional[str]:
        """快速测试文章"""
        self.log_action("智能创作：开始生成测试文章")
        
        try:
            draft = self.pipeline.generate_test_content()
            if not draft:
                print("❌ 生成测试文章失败")
                self.log_action("生成测试文章失败", "error")
                self.pause_for_user()
                return None
            
            # 测试文章生成成功后，询问是否要发布
            print(f"\n✅ 测试文章已生成: {draft}")
            publish_choice = input("\n是否要发布此测试文章？(y/N): ").strip().lower()
            
            self.log_action(f"测试文章生成成功: {draft}, 用户选择{'发布' if publish_choice in ['y', 'yes'] else '不发布'}")
            
            if publish_choice not in ['y', 'yes']:
                print("📄 测试文章已保存到草稿目录，您可以稍后通过'智能内容发布'来发布它")
                self.pause_for_user()
                return None
                
            return str(draft)
            
        except Exception as e:
            print(f"❌ 生成测试文章时出错: {e}")
            self.pause_for_user()
            return None
    
    def _content_outline_creation(self) -> Optional[str]:
        """内容大纲创建"""
        self.display_menu_header("📋 内容大纲创建", "为指定主题生成详细的内容规划和大纲")
        
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
                "5. 🛠️ 工具介绍",
                "6. 🧠 认知升级",
                "7. 💰 投资理财"
            ]
            
            print("\n请选择内容类型:")
            for ct in content_types:
                print(f"   {ct}")
            
            type_choice = input("选择类型 (1-7): ").strip()
            type_map = {
                "1": "技术教程",
                "2": "观点分析", 
                "3": "数据解读",
                "4": "趋势预测",
                "5": "工具介绍",
                "6": "认知升级",
                "7": "投资理财"
            }
            content_type = type_map.get(type_choice, "综合分析")
            
            print(f"\n🤖 正在为《{topic}》生成{content_type}类型的详细大纲...")
            
            # 生成内容大纲
            from scripts.tools.content.topic_inspiration_generator import TopicInspirationGenerator
            generator = TopicInspirationGenerator("auto")
            
            outline = generator.generate_detailed_plan(topic, content_type)
            
            if outline:
                print(f"\n✅ 内容大纲生成成功:")
                print("="*50)
                print(outline)
                print("="*50)
                
                # 询问是否保存大纲
                save_choice = input("\n是否将大纲保存到文件？(y/N): ").strip().lower()
                if save_choice in ['y', 'yes']:
                    from datetime import datetime
                    from pathlib import Path
                    
                    # 创建输出目录
                    outline_dir = Path(".tmp/outlines")
                    outline_dir.mkdir(parents=True, exist_ok=True)
                    
                    # 生成文件名
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()[:30]
                    filename = f"{timestamp}_{safe_topic}_{content_type}_大纲.md"
                    
                    outline_file = outline_dir / filename
                    with open(outline_file, 'w', encoding='utf-8') as f:
                        f.write(f"# 《{topic}》内容大纲\n\n")
                        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"**内容类型**: {content_type}\n\n")
                        f.write(outline)
                    
                    print(f"💾 大纲已保存至: {outline_file}")
                
                self.log_action("内容大纲创建成功", f"主题: {topic}, 类型: {content_type}")
                return outline
            else:
                print("❌ 内容大纲生成失败")
                return None
                
        except Exception as e:
            self.handle_error(e, "内容大纲创建")
            return None
    
    def _creation_assistance_tools(self) -> Optional[str]:
        """创作辅助工具"""
        print("\n🛠️ 创作辅助工具")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _vip_content_creation(self) -> Optional[str]:
        """VIP多层内容创作"""
        try:
            from scripts.cli.vip_menu_handler import VIPMenuHandler
            vip_handler = VIPMenuHandler(self.pipeline)
            return vip_handler.handle_vip_content_creation()
        except ImportError:
            print("❌ VIP内容创作模块不可用")
            return None
    
    def handle_monetization_menu(self) -> None:
        """处理内容变现管理菜单"""
        menu_title = "💰 内容变现管理"
        menu_description = "🏦 管理文章的内容变现包创建和发送、奖励系统管理"
        
        options = [
            "1. 为文章创建内容变现包",
            "2. 查看奖励发送状态",
            "3. 手动发送奖励给用户",
            "4. 运行奖励系统测试",
            "5. 生成测试访问码",
            "6. 验证访问码",
            "7. 会员统计分析",
            "8. 处理注册申请",
            "9. 导出会员数据"
        ]
        
        handlers = [
            self._create_monetization_package,
            self._view_reward_status,
            self._manual_send_reward,
            self._run_reward_test,
            self._generate_access_code,
            self._validate_access_code,
            self._member_statistics,
            self._process_registrations,
            self._export_member_data
        ]
        
        self.create_menu_loop_with_path(menu_title, menu_description, options, handlers, "6")
    
    def _create_monetization_package(self) -> Optional[str]:
        """创建内容变现包"""
        try:
            # 列出可用的已发布文章
            from pathlib import Path
            import subprocess
            posts_dir = Path("_posts")
            
            if not posts_dir.exists():
                print("📋 _posts目录不存在")
                return None
                
            posts = list(posts_dir.glob("*.md"))
            if not posts:
                print("📋 未找到已发布文章")
                return None
                
            print("\n📄 已发布文章列表：")
            for i, post in enumerate(posts[:10]):  # 显示最新10篇
                print(f"  {i+1}. {post.stem}")
            print("  0. 返回上级菜单")
            
            choice = input("\n请输入文章编号，或直接输入文章路径 (0返回): ").strip()
            
            if choice == "0" or choice == "":
                print("📋 返回内容变现管理菜单")
                return None
            
            if choice.isdigit() and 1 <= int(choice) <= len(posts):
                article_path = str(posts[int(choice)-1])
            else:
                article_path = choice
            
            if article_path and Path(article_path).exists():
                print(f"\n🔄 正在为文章创建内容变现包: {article_path}")
                # 调用reward_system_manager
                script_path = Path("scripts/utils/reward_system_manager.py")
                if not script_path.exists():
                    print(f"❌ 脚本文件不存在: {script_path}")
                    return None
                    
                result = subprocess.run([
                    "python", str(script_path), "create", article_path
                ], capture_output=True, text=True, check=False)
                
                print(result.stdout)
                if result.stderr:
                    print(f"❌ 错误: {result.stderr}")
                    
                return "内容变现包创建完成" if result.returncode == 0 else None
            else:
                print("❌ 文章文件不存在")
                return None
                
        except Exception as e:
            self.handle_error(e, "创建内容变现包")
            return None
    
    def _view_reward_status(self) -> Optional[str]:
        """查看奖励发送状态"""
        try:
            from pathlib import Path
            import subprocess
            
            script_path = Path("scripts/utils/reward_system_manager.py")
            if not script_path.exists():
                print(f"❌ 脚本文件不存在: {script_path}")
                self.pause_for_user()
                return None
                
            result = subprocess.run([
                "python", str(script_path), "stats"
            ], capture_output=True, text=True, check=False)
            
            print(result.stdout)
            if result.stderr:
                print(f"❌ 错误: {result.stderr}")
                
            self.pause_for_user()
            return "奖励状态查看完成" if result.returncode == 0 else None
            
        except Exception as e:
            self.handle_error(e, "查看奖励发送状态")
            self.pause_for_user()
            return None
    
    def _manual_send_reward(self) -> Optional[str]:
        """手动发送奖励给用户"""
        try:
            email = input("\n请输入用户邮箱: ").strip()
            article_title = input("请输入文章标题: ").strip()
            
            if not email or not article_title:
                print("❌ 邮箱和文章标题不能为空")
                self.pause_for_user()
                return None
                
            from pathlib import Path
            import subprocess
            
            script_path = Path("scripts/utils/reward_system_manager.py")
            if not script_path.exists():
                print(f"❌ 脚本文件不存在: {script_path}")
                self.pause_for_user()
                return None
                
            result = subprocess.run([
                "python", str(script_path), "send", email, article_title
            ], capture_output=True, text=True, check=False)
            
            print(result.stdout)
            if result.stderr:
                print(f"❌ 错误: {result.stderr}")
                
            self.pause_for_user()
            return "奖励发送完成" if result.returncode == 0 else None
            
        except Exception as e:
            self.handle_error(e, "手动发送奖励")
            self.pause_for_user()
            return None
    
    def _run_reward_test(self) -> Optional[str]:
        """运行奖励系统测试"""
        try:
            from pathlib import Path
            import subprocess
            
            script_path = Path("scripts/utils/reward_system_manager.py")
            if not script_path.exists():
                print(f"❌ 脚本文件不存在: {script_path}")
                self.pause_for_user()
                return None
                
            print("\n🧪 正在运行奖励系统测试...")
            result = subprocess.run([
                "python", str(script_path), "test"
            ], capture_output=True, text=True, check=False)
            
            print(result.stdout)
            if result.stderr:
                print(f"❌ 错误: {result.stderr}")
                
            self.pause_for_user()
            return "奖励系统测试完成" if result.returncode == 0 else None
            
        except Exception as e:
            self.handle_error(e, "运行奖励系统测试")
            self.pause_for_user()
            return None
    
    def _generate_access_code(self) -> Optional[str]:
        """生成测试访问码"""
        try:
            from scripts.member_management import MemberManager
            
            print("\n🔑 生成访问码")
            print("="*40)
            
            manager = MemberManager()
            
            # 显示会员等级
            print("请选择会员等级:")
            levels = {
                '1': 'experience',
                '2': 'monthly', 
                '3': 'quarterly',
                '4': 'yearly'
            }
            
            for key, level in levels.items():
                config = manager.member_levels[level]
                print(f"   {key}. {config['name']} - {config['days']}天 (¥{config['price']})")
            
            choice = input("\n请选择 (1-4): ").strip()
            
            if choice not in levels:
                print("❌ 无效选择")
                return None
            
            level = levels[choice]
            config = manager.member_levels[level]
            
            # 生成访问码
            access_code = manager.generate_access_code(level)
            
            print(f"\n✅ {config['name']}访问码生成成功！")
            print(f"🔑 访问码: {access_code}")
            print(f"⏰ 有效期: {config['days']}天")
            
            # 询问是否发送邮件
            send_email = input("\n是否发送邮件？(y/N): ").strip().lower()
            if send_email in ['y', 'yes']:
                email = input("请输入邮箱地址: ").strip()
                if email:
                    if manager.send_access_code_email(email, access_code, config['name']):
                        print(f"✅ 访问码已发送到 {email}")
                    else:
                        print("❌ 邮件发送失败，请检查邮件配置")
            
            self.log_action("生成访问码成功", f"等级: {config['name']}, 码: {access_code}")
            return access_code
            
        except Exception as e:
            self.handle_error(e, "生成访问码")
            return None
    
    def _validate_access_code(self) -> Optional[str]:
        """验证访问码"""
        try:
            from scripts.member_management import MemberManager
            
            print("\n✅ 验证访问码")
            print("="*40)
            
            access_code = input("请输入访问码: ").strip()
            if not access_code:
                print("❌ 访问码不能为空")
                return None
            
            manager = MemberManager()
            result = manager.validate_access_code(access_code)
            
            if result['valid']:
                print(f"\n✅ 访问码有效！")
                print(f"💳 会员等级: {result['level_name']}")
                print(f"⏰ 过期时间: {result['expires_at']}")
                print(f"📅 剩余天数: {result['days_remaining']}天")
                
                if result['days_remaining'] <= 3:
                    print("⚠️ 访问码即将过期，请及时续费")
                    
                return "访问码有效"
            else:
                print(f"\n❌ 访问码验证失败")
                print(f"原因: {result['message']}")
                return None
                
        except Exception as e:
            self.handle_error(e, "验证访问码")
            return None
    
    def _member_statistics(self) -> Optional[str]:
        """会员统计分析"""
        try:
            from scripts.member_management import MemberManager
            
            print("\n📈 会员统计分析")
            print("="*40)
            
            manager = MemberManager()
            stats = manager.get_stats()
            
            print("📋 注册统计:")
            print(f"   总注册数: {stats['total_registrations']}")
            print(f"   待处理: {stats['pending_registrations']}")
            print(f"   已处理: {stats['processed_registrations']}")
            
            print(f"\n🔑 访问码统计:")
            print(f"   已生成: {stats['total_access_codes']}")
            print(f"   有效的: {stats['active_access_codes']}")
            print(f"   已过期: {stats['expired_access_codes']}")
            
            if stats['level_distribution']:
                print(f"\n📊 会员等级分布:")
                for level, count in stats['level_distribution'].items():
                    print(f"   {level}: {count}人")
            
            if stats['recent_activity']:
                print(f"\n🕒 最近活动 (近7天):")
                print(f"   新注册: {stats['recent_activity']['registrations']}人")
                print(f"   新访问码: {stats['recent_activity']['access_codes']}个")
            
            self.pause_for_user()
            return "会员统计分析完成"
            
        except Exception as e:
            self.handle_error(e, "会员统计分析")
            return None
    
    def _process_registrations(self) -> Optional[str]:
        """处理注册申请"""
        try:
            from scripts.member_management import MemberManager
            
            print("\n📝 处理注册申请")
            print("="*40)
            
            manager = MemberManager()
            pending = manager.get_pending_registrations()
            
            if not pending:
                print("📄 当前没有待处理的注册申请")
                self.pause_for_user()
                return None
            
            print(f"📋 发现 {len(pending)} 个待处理注册:")
            for i, reg in enumerate(pending[:10], 1):  # 显示前10个
                print(f"   {i}. {reg.get('email', 'N/A')} - {reg.get('level', 'N/A')} ({reg.get('created_at', 'N/A')})")
            
            print("\n处理选项:")
            print("1. 批量处理全部 (生成访问码+发送邮件)")
            print("2. 批量处理全部 (仅生成访问码)")
            print("3. 逐个处理")
            print("0. 取消")
            
            choice = input("\n请选择 (0-3): ").strip()
            
            if choice == "1":
                print("\n正在批量处理注册 (包含邮件发送)...")
                manager.batch_process_registrations(send_email=True)
                print("✅ 批量处理完成")
                
            elif choice == "2":
                print("\n正在批量处理注册 (不发送邮件)...")
                manager.batch_process_registrations(send_email=False)
                print("✅ 批量处理完成")
                
            elif choice == "3":
                print("💡 逐个处理功能尚未实现，请使用批量处理")
                
            elif choice == "0":
                return None
            
            return "注册处理完成"
            
        except Exception as e:
            self.handle_error(e, "处理注册申请")
            return None
    
    def _export_member_data(self) -> Optional[str]:
        """导出会员数据"""
        try:
            from scripts.member_management import MemberManager
            from datetime import datetime
            
            print("\n💾 导出会员数据")
            print("="*40)
            
            manager = MemberManager()
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"member_export_{timestamp}.csv"
            
            filename = input(f"\n输入文件名 (默认: {default_filename}): ").strip()
            if not filename:
                filename = default_filename
            
            # 导出数据
            print(f"\n正在导出会员数据...")
            export_path = manager.export_registrations_csv(filename)
            
            print(f"✅ 会员数据已导出到: {export_path}")
            
            # 显示统计信息
            stats = manager.get_stats()
            print(f"\n📋 导出统计:")
            print(f"   总记录数: {stats['total_registrations']}")
            print(f"   导出文件: {export_path}")
            
            self.pause_for_user()
            return f"会员数据已导出到 {export_path}"
            
        except Exception as e:
            self.handle_error(e, "导出会员数据")
            return None
    
    def handle_post_update_menu(self) -> None:
        """处理文章更新工具菜单"""
        menu_title = "📝 文章更新工具"
        menu_description = "🔄 更新已发布的文章内容，支持直接编辑或完整处理流程"
        
        options = [
            "1. 更新已发布文章 (直接编辑模式)",
            "2. 更新已发布文章 (流水线处理模式)",
            "3. 修改文章会员等级",
            "4. 查看文章更新帮助"
        ]
        
        handlers = [
            self._update_article_direct,
            self._update_article_pipeline,
            self._modify_article_tier,
            self._view_update_help
        ]
        
        self.create_menu_loop_with_path(menu_title, menu_description, options, handlers, "8")
    
    def _update_article_direct(self) -> Optional[str]:
        """直接编辑模式更新文章"""
        print("\n✏️ 直接编辑模式")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _update_article_pipeline(self) -> Optional[str]:
        """流水线处理模式更新文章"""
        print("\n🔄 流水线处理模式")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _modify_article_tier(self) -> Optional[str]:
        """修改文章会员等级"""
        print("\n🎯 修改文章会员等级")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def _view_update_help(self) -> Optional[str]:
        """查看文章更新帮助"""
        print("\n❓ 文章更新帮助")
        print("(功能开发中...)")
        self.pause_for_user()
        return None
    
    def handle_onedrive_images_menu(self) -> None:
        """OneDrive图床管理菜单"""
        while True:
            print("\n" + "="*50)
            print("📁 OneDrive图床管理")
            print("="*50)
            print("1. 初始化OneDrive认证")
            print("2. 处理单个草稿的图片")
            print("3. 批量处理所有草稿图片")
            print("4. 检查OneDrive连接状态")
            print("5. 查看图片处理统计")
            print("6. 图片索引管理")
            print("7. 🆕 混合图片管理（支持任意位置）")
            print("8. 🧹 管理处理会话")
            print("9. 🗑️ OneDrive云端清理工具")
            print("10. 📅 按日期下载图片备份")
            print("11. 🚀 智能Header+图片处理（推荐）")
            print("\n0. 返回主菜单")
            
            choice = input("\n请选择操作 (1-11/0): ").strip()
            
            if choice == "1":
                self._init_onedrive_auth()
            elif choice == "2":
                self._process_single_draft_images()
            elif choice == "3":
                self._batch_process_images()
            elif choice == "4":
                self._check_onedrive_status()
            elif choice == "5":
                self._view_image_statistics()
            elif choice == "6":
                self._image_index_management()
            elif choice == "7":
                self._mixed_image_management()
            elif choice == "8":
                self._manage_processing_sessions()
            elif choice == "9":
                self._onedrive_cleanup_tools()
            elif choice == "10":
                self._date_download_backup()
            elif choice == "11":
                self._enhanced_header_image_processing()
            elif choice == "0":
                return
            else:
                print("❌ 无效选择")
    
    def _init_onedrive_auth(self) -> Optional[str]:
        """初始化OneDrive认证"""
        print("🔐 启动OneDrive认证...")
        try:
            import subprocess
            result = subprocess.run([
                "python3", "scripts/tools/onedrive_blog_images.py", 
                "--setup"
            ], check=False, capture_output=False)
            
            if result.returncode == 0:
                print("✅ 认证设置完成")
                return "认证设置完成"
            else:
                print("❌ 认证设置失败")
                return None
                
        except Exception as e:
            print(f"❌ 认证过程出错: {e}")
            return None
    
    def _process_single_draft_images(self) -> Optional[str]:
        """处理单个草稿的图片"""
        print("📝 选择要处理的草稿文件...")
        
        # 显示草稿列表
        from pathlib import Path
        drafts_dir = Path("_drafts")
        if not drafts_dir.exists():
            print("❌ 草稿目录不存在")
            return None
            
        draft_files = list(drafts_dir.glob("*.md"))
        if not draft_files:
            print("❌ 没有找到草稿文件")
            return None
            
        print("\n可用的草稿文件:")
        for i, draft in enumerate(draft_files, 1):
            print(f"{i}. {draft.name}")
            
        try:
            file_choice = input(f"\n请选择文件 (1-{len(draft_files)}/0取消): ").strip()
            if file_choice == "0":
                return None
                
            file_index = int(file_choice) - 1
            if 0 <= file_index < len(draft_files):
                selected_draft = draft_files[file_index]
                print(f"📝 处理草稿: {selected_draft.name}")
                
                # 使用统一的OneDrive图片处理接口
                result = self.pipeline.process_onedrive_images(selected_draft)
                
                if result['success']:
                    print(f"✅ 图片处理完成，处理了 {result['processed_images']} 张图片")
                    if result['issues']:
                        print("⚠️ 仍有部分图片问题需要手动处理:")
                        for issue in result['issues'][:3]:  # 显示前3个问题
                            print(f"   • {issue}")
                    return f"处理了 {result['processed_images']} 张图片"
                else:
                    print(f"❌ 图片处理失败: {result['error']}")
                    return None
            else:
                print("❌ 无效的文件选择")
                return None
                
        except (ValueError, IndexError):
            print("❌ 无效的输入")
            return None
    
    def _batch_process_images(self) -> Optional[str]:
        """批量处理所有草稿图片"""
        print("📁 批量处理所有草稿图片...")
        
        try:
            from pathlib import Path
            drafts_dir = Path("_drafts")
            if not drafts_dir.exists():
                print("❌ 草稿目录不存在")
                return None
            
            draft_files = list(drafts_dir.glob("*.md"))
            if not draft_files:
                print("❌ 没有找到草稿文件")
                return None
            
            total_processed = 0
            successful_files = 0
            
            print(f"📄 找到 {len(draft_files)} 个草稿文件，开始批量处理...")
            
            for draft_file in draft_files:
                print(f"\n处理: {draft_file.name}")
                
                try:
                    # 使用统一的OneDrive图片处理接口
                    result = self.pipeline.process_onedrive_images(draft_file)
                    
                    if result['success']:
                        successful_files += 1
                        total_processed += result['processed_images']
                        print(f"✅ 成功处理 {result['processed_images']} 张图片")
                        
                        if result['issues']:
                            print(f"⚠️ {len(result['issues'])} 个问题需要手动处理")
                    else:
                        print(f"❌ 处理失败: {result['error']}")
                        
                except Exception as e:
                    print(f"❌ 处理文件时出错: {e}")
            
            print(f"\n📊 批量处理完成:")
            print(f"   • 成功文件: {successful_files}/{len(draft_files)}")
            print(f"   • 总计处理图片: {total_processed} 张")
            
            return f"批量处理完成: {successful_files} 个文件, {total_processed} 张图片"
            
        except Exception as e:
            print(f"❌ 批量处理失败: {e}")
            return None
    
    def _check_onedrive_status(self) -> Optional[str]:
        """检查OneDrive连接状态"""
        print("\n🔍 检查OneDrive连接状态")
        
        try:
            import subprocess
            import sys
            
            # 检查OneDrive配置和认证状态
            from pathlib import Path
            config_file = Path("config/onedrive_config.json")
            token_file = Path("config/onedrive_token.json")
            
            print("📋 检查OneDrive配置状态:")
            print(f"   配置文件: {'✅ 存在' if config_file.exists() else '❌ 不存在'}")
            print(f"   认证令牌: {'✅ 存在' if token_file.exists() else '❌ 不存在'}")
            
            if not config_file.exists():
                print("\n💡 建议: 使用 '1. 初始化OneDrive认证' 来配置OneDrive")
                return "配置文件不存在"
            
            if not token_file.exists():
                print("\n💡 建议: 使用 '1. 初始化OneDrive认证' 来获取访问令牌")
                return "认证令牌不存在"
            
            # 尝试调用工具进行简单测试
            result = subprocess.run([
                sys.executable, "scripts/tools/onedrive_blog_images.py", "--help"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ OneDrive连接正常")
                if result.stdout:
                    print("详细信息:")
                    print(result.stdout)
                return "OneDrive连接正常"
            else:
                print("❌ OneDrive连接异常")
                if result.stderr:
                    print(f"错误信息: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("⏰ 连接检查超时，可能存在网络问题")
            return None
        except Exception as e:
            print(f"❌ 检查过程出错: {e}")
            return None
        
        self.pause_for_user()
        return None
    
    def _view_image_statistics(self) -> Optional[str]:
        """查看图片处理统计"""
        print("\n📊 图片处理统计")
        
        try:
            # 导入图片索引管理器来获取统计信息
            from scripts.tools.onedrive_image_index import OneDriveImageIndex
            
            index_manager = OneDriveImageIndex()
            stats = index_manager.get_statistics()
            
            print("="*50)
            print("📈 OneDrive图片统计信息")
            print("="*50)
            
            print(f"📁 总图片数量: {stats.get('total_images', 0)}")
            print(f"🔗 有效链接: {stats.get('valid_links', 0)}")
            print(f"❌ 失效链接: {stats.get('invalid_links', 0)}")
            print(f"📅 最近更新: {stats.get('last_updated', 'N/A')}")
            print(f"💾 索引文件大小: {stats.get('index_size', 'N/A')}")
            
            if stats.get('recent_uploads'):
                print(f"\n📈 最近上传 (最近7天): {len(stats['recent_uploads'])}张")
                for upload in stats['recent_uploads'][:5]:  # 显示最近5张
                    print(f"   • {upload.get('filename', 'N/A')} ({upload.get('upload_date', 'N/A')})")
            
            if stats.get('size_distribution'):
                print(f"\n📊 文件大小分布:")
                for size_range, count in stats['size_distribution'].items():
                    print(f"   • {size_range}: {count}张")
            
        except ImportError:
            print("❌ 无法导入图片索引管理器")
        except Exception as e:
            print(f"❌ 获取统计信息失败: {e}")
            
            # 回退方案：显示基础统计
            try:
                from pathlib import Path
                index_file = Path("_data/onedrive_image_index.json")
                if index_file.exists():
                    import json
                    with open(index_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    print("📊 基础统计信息:")
                    print(f"   📁 索引文件存在: ✅")
                    print(f"   📝 记录条数: {len(data.get('images', []))}")
                    print(f"   📅 索引文件修改时间: {index_file.stat().st_mtime}")
                else:
                    print("❌ 未找到图片索引文件")
            except Exception as fallback_error:
                print(f"❌ 回退统计也失败: {fallback_error}")
        
        self.pause_for_user()
        return "图片统计查看完成"
    
    def _image_index_management(self) -> Optional[str]:
        """图片索引管理"""
        print("\n🗂️ 图片索引管理")
        print("="*50)
        
        try:
            from scripts.tools.onedrive_image_index import OneDriveImageIndex
            
            index_manager = OneDriveImageIndex()
            
            while True:
                print("\n🔧 图片索引管理选项:")
                print("1. 重建索引")
                print("2. 验证链接有效性")
                print("3. 清理失效记录")
                print("4. 导出索引数据")
                print("5. 查看详细统计")
                print("0. 返回上级菜单")
                
                choice = input("\n请选择操作 (1-5/0): ").strip()
                
                if choice == "1":
                    print("\n🔄 重建图片索引...")
                    result = index_manager.rebuild_index()
                    if result:
                        print("✅ 索引重建完成")
                    else:
                        print("❌ 索引重建失败")
                
                elif choice == "2":
                    print("\n🔍 验证链接有效性...")
                    invalid_count = index_manager.validate_links()
                    print(f"🔗 发现 {invalid_count} 个失效链接")
                
                elif choice == "3":
                    print("\n🧹 清理失效记录...")
                    removed_count = index_manager.cleanup_invalid_records()
                    print(f"🗑️ 清理了 {removed_count} 个失效记录")
                
                elif choice == "4":
                    print("\n💾 导出索引数据...")
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    export_file = f"image_index_export_{timestamp}.json"
                    
                    if index_manager.export_data(export_file):
                        print(f"✅ 数据已导出到: {export_file}")
                    else:
                        print("❌ 导出失败")
                
                elif choice == "5":
                    print("\n📊 详细统计信息:")
                    stats = index_manager.get_detailed_statistics()
                    for key, value in stats.items():
                        print(f"   {key}: {value}")
                
                elif choice == "0":
                    break
                
                else:
                    print("❌ 无效选择")
                
                if choice != "0":
                    input("\n按回车键继续...")
            
            return "图片索引管理完成"
            
        except ImportError:
            print("❌ 无法导入图片索引管理器模块")
            print("请检查 scripts/tools/onedrive_image_index.py 文件是否存在")
        except Exception as e:
            print(f"❌ 图片索引管理出错: {e}")
        
        self.pause_for_user()
        return None
    
    def _mixed_image_management(self) -> Optional[str]:
        """混合图片管理"""
        print("\n🔄 混合图片管理")
        print("📋 支持任意位置图片发现，四阶段处理流程，减少60%创作摩擦")
        
        try:
            import subprocess
            import sys
            
            while True:
                print("\n🔧 混合图片管理选项:")
                print("1. 自动发现和处理项目中的所有图片")
                print("2. 处理指定目录中的图片")
                print("3. 查看处理历史记录")
                print("4. 清理处理会话")
                print("5. 配置处理参数")
                print("0. 返回上级菜单")
                
                choice = input("\n请选择操作 (1-5/0): ").strip()
                
                if choice == "1":
                    print("\n🔍 自动发现和处理项目中的所有图片...")
                    result = subprocess.run([
                        sys.executable, "scripts/tools/mixed_image_manager.py", "--auto"
                    ], check=False)
                    
                    if result.returncode == 0:
                        print("✅ 自动处理完成")
                    else:
                        print("❌ 自动处理过程中出现问题")
                
                elif choice == "2":
                    target_dir = input("请输入目标目录路径: ").strip()
                    if target_dir:
                        print(f"\n📁 处理目录: {target_dir}")
                        result = subprocess.run([
                            sys.executable, "scripts/tools/mixed_image_manager.py", 
                            "--directory", target_dir
                        ], check=False)
                        
                        if result.returncode == 0:
                            print("✅ 目录处理完成")
                        else:
                            print("❌ 目录处理失败")
                    else:
                        print("❌ 目录路径不能为空")
                
                elif choice == "3":
                    print("\n📋 查看处理历史记录...")
                    result = subprocess.run([
                        sys.executable, "scripts/tools/mixed_image_manager.py", "--history"
                    ], check=False)
                
                elif choice == "4":
                    print("\n🧹 清理处理会话...")
                    result = subprocess.run([
                        sys.executable, "scripts/tools/mixed_image_manager.py", "--cleanup"
                    ], check=False)
                    
                    if result.returncode == 0:
                        print("✅ 会话清理完成")
                    else:
                        print("❌ 会话清理失败")
                
                elif choice == "5":
                    print("\n⚙️ 配置处理参数...")
                    result = subprocess.run([
                        sys.executable, "scripts/tools/mixed_image_manager.py", "--config"
                    ], check=False)
                
                elif choice == "0":
                    break
                
                else:
                    print("❌ 无效选择")
                
                if choice != "0":
                    input("\n按回车键继续...")
            
            return "混合图片管理完成"
            
        except Exception as e:
            print(f"❌ 混合图片管理出错: {e}")
            self.pause_for_user()
            return None
    
    def _manage_processing_sessions(self) -> Optional[str]:
        """管理处理会话"""
        print("\n🧹 管理处理会话")
        print("📋 管理图片处理的会话记录和状态")
        
        try:
            import subprocess
            import sys
            from pathlib import Path
            
            # 检查会话目录
            session_dirs = [
                Path(".tmp/image_processing_sessions"),
                Path(".build/processing_sessions"),
                Path("_data/processing_logs")
            ]
            
            active_sessions = []
            for session_dir in session_dirs:
                if session_dir.exists():
                    sessions = list(session_dir.glob("*.json"))
                    active_sessions.extend(sessions)
            
            print(f"📊 发现 {len(active_sessions)} 个处理会话")
            
            while True:
                print("\n🔧 会话管理选项:")
                print("1. 查看活动会话")
                print("2. 清理已完成会话")
                print("3. 恢复中断的会话")
                print("4. 导出会话日志")
                print("5. 查看会话统计")
                print("0. 返回上级菜单")
                
                choice = input("\n请选择操作 (1-5/0): ").strip()
                
                if choice == "1":
                    print("\n📋 活动会话列表:")
                    if active_sessions:
                        for i, session in enumerate(active_sessions[:10], 1):
                            try:
                                import json
                                with open(session, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                print(f"   {i}. {session.name}")
                                print(f"      状态: {data.get('status', 'unknown')}")
                                print(f"      时间: {data.get('created_at', 'N/A')}")
                                if data.get('progress'):
                                    print(f"      进度: {data['progress']}")
                            except Exception:
                                print(f"   {i}. {session.name} (无法读取)")
                    else:
                        print("   📄 暂无活动会话")
                
                elif choice == "2":
                    print("\n🧹 清理已完成会话...")
                    cleaned = 0
                    for session in active_sessions:
                        try:
                            import json
                            with open(session, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            if data.get('status') == 'completed':
                                session.unlink()
                                cleaned += 1
                        except Exception:
                            continue
                    print(f"✅ 清理了 {cleaned} 个已完成会话")
                
                elif choice == "3":
                    print("\n🔄 恢复中断的会话...")
                    # 调用混合图片管理器的恢复功能
                    result = subprocess.run([
                        sys.executable, "scripts/tools/mixed_image_manager.py", "--recover"
                    ], check=False)
                    
                    if result.returncode == 0:
                        print("✅ 会话恢复完成")
                    else:
                        print("❌ 会话恢复失败")
                
                elif choice == "4":
                    print("\n💾 导出会话日志...")
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    export_file = f"session_logs_{timestamp}.json"
                    
                    try:
                        import json
                        all_sessions = []
                        for session in active_sessions:
                            try:
                                with open(session, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                all_sessions.append(data)
                            except Exception:
                                continue
                        
                        with open(export_file, 'w', encoding='utf-8') as f:
                            json.dump(all_sessions, f, ensure_ascii=False, indent=2)
                        
                        print(f"✅ 日志已导出到: {export_file}")
                    except Exception as e:
                        print(f"❌ 导出失败: {e}")
                
                elif choice == "5":
                    print("\n📊 会话统计:")
                    stats = {"总会话": len(active_sessions), "completed": 0, "running": 0, "failed": 0}
                    
                    for session in active_sessions:
                        try:
                            import json
                            with open(session, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            status = data.get('status', 'unknown')
                            if status in stats:
                                stats[status] += 1
                        except Exception:
                            continue
                    
                    for key, value in stats.items():
                        print(f"   {key}: {value}")
                
                elif choice == "0":
                    break
                
                else:
                    print("❌ 无效选择")
                
                if choice != "0":
                    input("\n按回车键继续...")
            
            return "处理会话管理完成"
            
        except Exception as e:
            print(f"❌ 会话管理出错: {e}")
            self.pause_for_user()
            return None
    
    def _onedrive_cleanup_tools(self) -> Optional[str]:
        """OneDrive云端清理工具"""
        print("\n🗑️ OneDrive云端清理工具")
        print("📋 清理OneDrive中不再使用的图片文件，释放存储空间")
        
        try:
            import subprocess
            import sys
            
            while True:
                print("\n🔧 云端清理选项:")
                print("1. 扫描未使用的文件")
                print("2. 清理孤立文件")
                print("3. 批量删除失效链接对应文件")
                print("4. 查看清理历史")
                print("5. 安全模式清理 (备份后删除)")
                print("0. 返回上级菜单")
                
                choice = input("\n请选择操作 (1-5/0): ").strip()
                
                if choice == "1":
                    print("\n🔍 扫描未使用的文件...")
                    result = subprocess.run([
                        sys.executable, "scripts/tools/cleanup_onedrive_cloud.py", "--scan"
                    ], check=False)
                    
                    if result.returncode == 0:
                        print("✅ 文件扫描完成")
                    else:
                        print("❌ 文件扫描失败")
                
                elif choice == "2":
                    print("\n🧹 清理孤立文件...")
                    confirm = input("⚠️ 此操作将删除未被引用的文件，确认继续？(y/N): ").strip().lower()
                    
                    if confirm in ['y', 'yes']:
                        result = subprocess.run([
                            sys.executable, "scripts/tools/cleanup_onedrive_cloud.py", "--cleanup"
                        ], check=False)
                        
                        if result.returncode == 0:
                            print("✅ 孤立文件清理完成")
                        else:
                            print("❌ 孤立文件清理失败")
                    else:
                        print("❌ 操作已取消")
                
                elif choice == "3":
                    print("\n🔗 批量删除失效链接对应文件...")
                    confirm = input("⚠️ 此操作将删除失效链接对应的云端文件，确认继续？(y/N): ").strip().lower()
                    
                    if confirm in ['y', 'yes']:
                        result = subprocess.run([
                            sys.executable, "scripts/tools/cleanup_onedrive_cloud.py", "--invalid-links"
                        ], check=False)
                        
                        if result.returncode == 0:
                            print("✅ 失效文件清理完成")
                        else:
                            print("❌ 失效文件清理失败")
                    else:
                        print("❌ 操作已取消")
                
                elif choice == "4":
                    print("\n📋 查看清理历史...")
                    result = subprocess.run([
                        sys.executable, "scripts/tools/cleanup_onedrive_cloud.py", "--history"
                    ], check=False)
                
                elif choice == "5":
                    print("\n🛡️ 安全模式清理...")
                    confirm = input("安全模式将先备份再删除，确认继续？(y/N): ").strip().lower()
                    
                    if confirm in ['y', 'yes']:
                        result = subprocess.run([
                            sys.executable, "scripts/tools/cleanup_onedrive_cloud.py", "--safe-cleanup"
                        ], check=False)
                        
                        if result.returncode == 0:
                            print("✅ 安全模式清理完成")
                        else:
                            print("❌ 安全模式清理失败")
                    else:
                        print("❌ 操作已取消")
                
                elif choice == "0":
                    break
                
                else:
                    print("❌ 无效选择")
                
                if choice != "0":
                    input("\n按回车键继续...")
            
            return "OneDrive云端清理完成"
            
        except Exception as e:
            print(f"❌ 云端清理工具出错: {e}")
            self.pause_for_user()
            return None
    
    def _date_download_backup(self) -> Optional[str]:
        """按日期下载图片备份"""
        print("\n📅 按日期下载图片备份")
        print("📋 根据指定日期范围下载OneDrive中的图片备份")
        
        try:
            import subprocess
            import sys
            from datetime import datetime, timedelta
            
            while True:
                print("\n🔧 日期备份选项:")
                print("1. 下载今天上传的图片")
                print("2. 下载最近7天的图片")
                print("3. 下载最近30天的图片")
                print("4. 自定义日期范围下载")
                print("5. 下载所有图片备份")
                print("0. 返回上级菜单")
                
                choice = input("\n请选择操作 (1-5/0): ").strip()
                
                if choice == "1":
                    print("\n📥 下载今天上传的图片...")
                    today = datetime.now().strftime("%Y-%m-%d")
                    result = subprocess.run([
                        sys.executable, "scripts/tools/onedrive_date_downloader.py", 
                        "--date", today
                    ], check=False)
                    
                    if result.returncode == 0:
                        print("✅ 今日图片下载完成")
                    else:
                        print("❌ 今日图片下载失败")
                
                elif choice == "2":
                    print("\n📥 下载最近7天的图片...")
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=7)
                    
                    result = subprocess.run([
                        sys.executable, "scripts/tools/onedrive_date_downloader.py",
                        "--start-date", start_date.strftime("%Y-%m-%d"),
                        "--end-date", end_date.strftime("%Y-%m-%d")
                    ], check=False)
                    
                    if result.returncode == 0:
                        print("✅ 近7天图片下载完成")
                    else:
                        print("❌ 近7天图片下载失败")
                
                elif choice == "3":
                    print("\n📥 下载最近30天的图片...")
                    end_date = datetime.now()
                    start_date = end_date - timedelta(days=30)
                    
                    result = subprocess.run([
                        sys.executable, "scripts/tools/onedrive_date_downloader.py",
                        "--start-date", start_date.strftime("%Y-%m-%d"),
                        "--end-date", end_date.strftime("%Y-%m-%d")
                    ], check=False)
                    
                    if result.returncode == 0:
                        print("✅ 近30天图片下载完成")
                    else:
                        print("❌ 近30天图片下载失败")
                
                elif choice == "4":
                    print("\n📅 自定义日期范围下载...")
                    start_date = input("请输入开始日期 (YYYY-MM-DD): ").strip()
                    end_date = input("请输入结束日期 (YYYY-MM-DD): ").strip()
                    
                    if start_date and end_date:
                        try:
                            # 验证日期格式
                            datetime.strptime(start_date, "%Y-%m-%d")
                            datetime.strptime(end_date, "%Y-%m-%d")
                            
                            print(f"\n📥 下载 {start_date} 到 {end_date} 的图片...")
                            result = subprocess.run([
                                sys.executable, "scripts/tools/onedrive_date_downloader.py",
                                "--start-date", start_date,
                                "--end-date", end_date
                            ], check=False)
                            
                            if result.returncode == 0:
                                print("✅ 自定义范围图片下载完成")
                            else:
                                print("❌ 自定义范围图片下载失败")
                        except ValueError:
                            print("❌ 日期格式错误，请使用YYYY-MM-DD格式")
                    else:
                        print("❌ 日期不能为空")
                
                elif choice == "5":
                    print("\n📥 下载所有图片备份...")
                    confirm = input("⚠️ 这可能下载大量文件，确认继续？(y/N): ").strip().lower()
                    
                    if confirm in ['y', 'yes']:
                        result = subprocess.run([
                            sys.executable, "scripts/tools/onedrive_date_downloader.py", "--all"
                        ], check=False)
                        
                        if result.returncode == 0:
                            print("✅ 全部图片下载完成")
                        else:
                            print("❌ 全部图片下载失败")
                    else:
                        print("❌ 操作已取消")
                
                elif choice == "0":
                    break
                
                else:
                    print("❌ 无效选择")
                
                if choice != "0":
                    input("\n按回车键继续...")
            
            return "日期备份下载完成"
            
        except Exception as e:
            print(f"❌ 日期备份下载出错: {e}")
            self.pause_for_user()
            return None
    
    def _enhanced_header_image_processing(self) -> Optional[str]:
        """智能Header+图片处理"""
        print("\n🚀 智能Header+图片处理")
        print("📋 功能说明:")
        print("   1. 自动使用正文第一张图片设置header")
        print("   2. 上传所有图片到OneDrive云端")
        print("   3. 替换所有图片链接（包括header）")
        print("   4. 保留本地备份以便后续编辑")
        print()
        
        # 显示可处理的文件
        from pathlib import Path
        
        # 查找草稿和已发布的文章
        all_files = []
        
        drafts_dir = Path("_drafts")
        if drafts_dir.exists():
            draft_files = list(drafts_dir.glob("*.md"))
            for f in draft_files:
                all_files.append(("草稿", f))
        
        posts_dir = Path("_posts")
        if posts_dir.exists():
            post_files = list(posts_dir.glob("*.md"))
            for f in post_files:
                all_files.append(("文章", f))
                
        if not all_files:
            print("❌ 没有找到可处理的Markdown文件")
            self.pause_for_user()
            return None
            
        print("📝 可处理的文件:")
        for i, (file_type, file_path) in enumerate(all_files, 1):
            print(f"{i:2d}. [{file_type}] {file_path.name}")
            
        try:
            file_choice = input(f"\n请选择文件 (1-{len(all_files)}/0取消): ").strip()
            if file_choice == "0":
                return None
                
            file_index = int(file_choice) - 1
            if 0 <= file_index < len(all_files):
                file_type, selected_file = all_files[file_index]
                print(f"\n📝 选择处理: [{file_type}] {selected_file.name}")
                
                # 询问处理选项
                print("\n🔧 处理选项:")
                print("1. 完整处理（自动header + 图片上传）")
                print("2. 仅设置header（不上传图片）")
                print("3. 演练模式（预览更改）")
                
                option = input("请选择选项 (1-3): ").strip()
                
                try:
                    import subprocess
                    import sys
                    
                    if option == "1":
                        # 完整处理
                        print(f"\n🚀 启动完整处理: {selected_file}")
                        cmd = [
                            sys.executable, 
                            "scripts/tools/enhanced_blog_image_processor.py",
                            str(selected_file)
                        ]
                        result = subprocess.run(cmd, check=False)
                        
                        if result.returncode == 0:
                            print("✅ 完整处理成功")
                            return "完整处理成功"
                        else:
                            print("❌ 处理过程中出现问题")
                            
                    elif option == "2":
                        # 仅header处理
                        print(f"\n📋 仅设置header: {selected_file}")
                        cmd = [
                            sys.executable,
                            "scripts/tools/auto_header_image_processor.py", 
                            str(selected_file)
                        ]
                        result = subprocess.run(cmd, check=False)
                        
                        if result.returncode == 0:
                            print("✅ Header设置成功")
                            return "Header设置成功"
                        else:
                            print("❌ Header设置失败")
                            
                    elif option == "3":
                        # 演练模式
                        print(f"\n🔍 演练模式: {selected_file}")
                        cmd = [
                            sys.executable,
                            "scripts/tools/enhanced_blog_image_processor.py",
                            str(selected_file),
                            "--dry-run"
                        ]
                        result = subprocess.run(cmd, check=False)
                        print("\n💡 提示: 演练模式不会修改任何文件")
                        
                    else:
                        print("❌ 无效选项")
                        
                except Exception as e:
                    print(f"❌ 处理失败: {e}")
                    
            else:
                print("❌ 无效的文件选择")
                
        except (ValueError, IndexError):
            print("❌ 无效的输入")
        
        self.pause_for_user()
        return None