#!/usr/bin/env python3
"""
手工草稿快速排版工具
用于将手工编写的草稿内容快速格式化为符合项目规范的Jekyll文章
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import re

# 添加项目根目录到 Python 路径
# format_draft.py在scripts/tools/content/，需要向上四级到达项目根目录
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

class DraftFormatter:
    """草稿格式化器"""
    
    def __init__(self):
        """初始化格式化器"""
        self.project_root = project_root
        self.drafts_dir = self.project_root / "_drafts"
        self.config_dir = self.project_root / "config"
        
        # 初始化内容质量检查管道
        try:
            from scripts.core.content_pipeline import ContentPipeline
            self.content_pipeline = ContentPipeline()
            self.unified_check_available = True
            print("✅ 统一内容质量检查系统已启用")
        except ImportError as e:
            print(f"⚠️ ContentPipeline不可用，使用基础检查 (原因: {e})")
            self.content_pipeline = None
            self.unified_check_available = False
        except Exception as e:
            print(f"⚠️ 内容质量检查系统初始化失败: {e}")
            self.content_pipeline = None
            self.unified_check_available = False
        
        # 默认分类映射
        self.category_mapping = {
            '认知': 'cognitive-upgrade',
            '认知升级': 'cognitive-upgrade',
            '思维': 'cognitive-upgrade',
            '学习': 'cognitive-upgrade',
            
            '技术': 'tech-empowerment',
            '工具': 'tech-empowerment',
            '效率': 'tech-empowerment',
            '自动化': 'tech-empowerment',
            
            '全球': 'global-perspective',
            '国际': 'global-perspective',
            '文化': 'global-perspective',
            '视野': 'global-perspective',
            
            '投资': 'investment-finance',
            '理财': 'investment-finance',
            '金融': 'investment-finance',
            '财务': 'investment-finance'
        }
        
        # 默认模板配置
        self.default_config = {
            "layout": "single",
            "author_profile": True,
            "breadcrumbs": True,
            "comments": True,
            "related": True,
            "share": True,
            "toc": True,
            "toc_icon": "list",
            "toc_label": "本页内容",
            "toc_sticky": True
        }

    def detect_category(self, title: str, content: str) -> str:
        """
        智能检测文章分类
        
        Args:
            title: 文章标题
            content: 文章内容
            
        Returns:
            检测到的分类
        """
        text = (title + " " + content).lower()
        
        # 分类关键词权重
        category_scores = {
            'cognitive-upgrade': 0,
            'tech-empowerment': 0,
            'global-perspective': 0,
            'investment-finance': 0
        }
        
        # 认知升级关键词
        cognitive_keywords = ['思维', '学习', '认知', '心理', '决策', '模型', '方法', '成长', '智慧']
        for keyword in cognitive_keywords:
            category_scores['cognitive-upgrade'] += text.count(keyword) * 2
        
        # 技术赋能关键词
        tech_keywords = ['技术', '工具', 'ai', '自动化', '效率', '软件', '系统', '平台', 'app', 'api']
        for keyword in tech_keywords:
            category_scores['tech-empowerment'] += text.count(keyword) * 2
        
        # 全球视野关键词
        global_keywords = ['全球', '国际', '文化', '美国', '中国', '欧洲', '趋势', '观察', '差异', '视野']
        for keyword in global_keywords:
            category_scores['global-perspective'] += text.count(keyword) * 2
            
        # 投资理财关键词
        finance_keywords = ['投资', '理财', '金融', '股票', '基金', '收益', '风险', '财务', '资产', '市场']
        for keyword in finance_keywords:
            category_scores['investment-finance'] += text.count(keyword) * 2
        
        # 返回得分最高的分类
        best_category = max(category_scores.items(), key=lambda x: x[1])[0]
        
        # 如果所有分类得分都很低，根据长度返回默认分类
        if category_scores[best_category] < 3:
            if len(content) > 2000:
                return 'global-perspective'  # 长文章通常是全球视野
            else:
                return 'cognitive-upgrade'   # 短文章通常是认知升级
        
        return best_category

    def generate_tags(self, title: str, content: str, category: str) -> List[str]:
        """
        智能生成标签
        
        Args:
            title: 文章标题
            content: 文章内容  
            category: 分类
            
        Returns:
            生成的标签列表
        """
        tags = set()
        text = (title + " " + content).lower()
        
        # 基础标签映射
        tag_keywords = {
            '学习': ['学习方法', '终身学习', '知识管理'],
            '思维': ['思维模型', '批判思维', '逻辑思维'],
            'ai': ['人工智能', 'AI工具', '机器学习'],
            '工具': ['生产力工具', '效率工具', '软件推荐'],
            '投资': ['投资策略', '理财规划', '财务管理'],
            '美国': ['美国市场', '美股投资', '美国文化'],
            '技术': ['技术趋势', '科技创新', '数字化转型'],
            '全球': ['全球化', '国际视野', '跨文化交流']
        }
        
        # 根据关键词生成标签
        for keyword, tag_list in tag_keywords.items():
            if keyword in text:
                tags.update(tag_list)
        
        # 根据分类添加默认标签
        category_default_tags = {
            'cognitive-upgrade': ['个人成长', '认知提升'],
            'tech-empowerment': ['技术工具', '效率提升'],
            'global-perspective': ['全球视野', '国际趋势'],
            'investment-finance': ['投资理财', '财务规划']
        }
        
        tags.update(category_default_tags.get(category, []))
        
        # 限制标签数量（3-6个）
        return list(tags)[:6] if len(tags) > 6 else list(tags)

    def generate_excerpt(self, content: str, target_length: int = 60) -> str:
        """
        生成文章摘要
        
        Args:
            content: 文章内容
            target_length: 目标长度（默认60字符）
            
        Returns:
            生成的摘要
        """
        # 移除markdown格式和特殊字符
        clean_content = re.sub(r'[#*`\[\](){}]', '', content)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # 取更多内容来寻找合适的截断点
        search_length = max(150, target_length * 2)
        excerpt = clean_content[:search_length]
        
        # 在句号、感叹号、问号处截断
        min_length = max(30, target_length - 20)  # 最小长度
        max_length = target_length + 20           # 最大长度
        
        for punct in ['。', '！', '？', '.', '!', '?']:
            if punct in excerpt[min_length:max_length]:  # 在合理位置寻找标点
                punct_pos = excerpt.find(punct, min_length)
                if punct_pos != -1:
                    excerpt = excerpt[:punct_pos + 1]
                    break
        
        # 如果还是太长，强制截断
        if len(excerpt) > target_length + 10:
            excerpt = excerpt[:target_length - 3] + "..."
        
        # 如果太短，尝试添加更多内容
        if len(excerpt) < target_length - 10:
            # 取更多内容并强制截断
            excerpt = clean_content[:target_length - 3] + "..."
        
        return excerpt

    def find_first_image(self, content: str) -> Optional[str]:
        """
        查找文章内容中的第一张图片
        
        Args:
            content: 文章内容
            
        Returns:
            第一张图片的路径，如果没有则返回None
        """
        # 查找markdown格式的图片
        image_pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')
        
        for match in image_pattern.finditer(content):
            img_path = match.group(2).strip()
            
            # 跳过空路径
            if not img_path:
                continue
                
            # 跳过网络链接，保留本地图片路径
            if img_path.startswith(('http://', 'https://')):
                # 但如果是OneDrive链接，可以使用
                if '1drv.ms' in img_path or 'sharepoint.com' in img_path:
                    return img_path
                continue
                
            return img_path
        
        return None

    def create_front_matter(self, title: str, content: str, 
                           category: Optional[str] = None, 
                           tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        创建front matter
        
        Args:
            title: 文章标题
            content: 文章内容
            category: 指定分类（可选）
            tags: 指定标签（可选）
            
        Returns:
            front matter字典
        """
        # 检测或使用指定的分类
        detected_category = category if category else self.detect_category(title, content)
        
        # 生成或使用指定的标签
        generated_tags = tags if tags else self.generate_tags(title, content, detected_category)
        
        # 生成摘要
        excerpt = self.generate_excerpt(content)
        
        # 查找第一张图片
        first_image = self.find_first_image(content)
        
        # 创建header字段
        if first_image:
            # 如果是OneDrive链接，直接使用
            if '1drv.ms' in first_image or 'sharepoint.com' in first_image:
                header_image = first_image
            else:
                # 本地图片，转换为OneDrive示例链接（实际使用中会被后续处理替换）
                header_image = "https://1drv.ms/i/c/5644dab129afda10/IQTq4kEOrERvRLHS_4L9uCK_ARjvU4zbducjMUCRTRR8Pdk"
        else:
            # 没有图片时使用默认OneDrive链接
            header_image = "https://1drv.ms/i/c/5644dab129afda10/IQTq4kEOrERvRLHS_4L9uCK_ARjvU4zbducjMUCRTRR8Pdk"
        
        # 构建front matter - 只包含必需字段
        front_matter = {
            "title": title,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "header": {
                "teaser": header_image  # 只保留teaser，其他header字段在发布时自动添加
            }
        }

        # 注意：不添加默认配置，这些会在发布时自动处理
        # 不添加categories、tags和excerpt，这些也会在发布时生成

        return front_matter

    def fix_header_field(self, front_matter: Dict[str, Any], body_content: str) -> bool:
        """
        检查并修复front matter中的header字段和其他必需字段
        
        Args:
            front_matter: 前置数据字典
            body_content: 文章正文内容
            
        Returns:
            是否进行了修复
        """
        header = front_matter.get('header', {})
        needs_update = False
        
        # 检查header字段
        required_header_fields = {
            'overlay_color': '#333',
            'overlay_filter': 0.5,
            'overlay_image': None,  # 需要确定图片
            'teaser': None  # 需要确定图片
        }
        
        # 情况1: 没有header字段
        if not header:
            needs_update = True
            print("📋 发现缺失header字段")
        else:
            # 情况2: header字段不完整
            missing_fields = []
            for field in required_header_fields:
                if field not in header:
                    missing_fields.append(field)
                    needs_update = True
            
            if missing_fields:
                print(f"📋 发现缺失header子字段: {', '.join(missing_fields)}")
        
        # 检查其他必需字段
        other_issues = []
        
        # 检查tags字段
        if 'tags' not in front_matter or not front_matter.get('tags'):
            title = front_matter.get('title', '')
            if title:
                # 生成tags
                generated_tags = self.generate_tags(title, body_content, front_matter.get('categories', ['cognitive-upgrade'])[0])
                front_matter['tags'] = generated_tags
                needs_update = True
                other_issues.append("tags字段")
        
        # 检查excerpt字段
        if 'excerpt' not in front_matter or not front_matter.get('excerpt'):
            excerpt = self.generate_excerpt(body_content)
            front_matter['excerpt'] = excerpt
            needs_update = True
            other_issues.append("excerpt字段")
        else:
            # 检查excerpt长度
            current_excerpt = front_matter['excerpt']
            if len(current_excerpt) < 50:
                # 重新生成更长的excerpt
                excerpt = self.generate_excerpt(body_content, target_length=55)
                front_matter['excerpt'] = excerpt
                needs_update = True
                other_issues.append("excerpt长度不足")
        
        if other_issues:
            print(f"📋 发现其他缺失字段: {', '.join(other_issues)}")
        
        if not needs_update:
            return False
        
        # 修复header字段
        if needs_update and (not header or any(field not in header for field in required_header_fields)):
            # 确定使用的图片
            header_image = self.determine_header_image(header, body_content)
            
            # 修复header字段
            if 'header' not in front_matter:
                front_matter['header'] = {}
            
            # 设置必需字段
            front_matter['header']['overlay_color'] = header.get('overlay_color', '#333')
            front_matter['header']['overlay_filter'] = header.get('overlay_filter', 0.5)
            front_matter['header']['overlay_image'] = header.get('overlay_image', header_image)
            front_matter['header']['teaser'] = header.get('teaser', header_image)
        
        return True
    
    def determine_header_image(self, existing_header: Dict[str, Any], body_content: str) -> str:
        """
        确定应该使用的header图片
        
        Args:
            existing_header: 现有的header字段
            body_content: 文章正文内容
            
        Returns:
            图片URL
        """
        # 优先级1: 如果已有overlay_image或teaser，使用现有的
        if existing_header.get('overlay_image'):
            print(f"🖼️ 使用现有overlay_image: {existing_header['overlay_image']}")
            return existing_header['overlay_image']
        
        if existing_header.get('teaser'):
            print(f"🖼️ 使用现有teaser: {existing_header['teaser']}")
            return existing_header['teaser']
        
        # 优先级2: 查找正文中的第一张图片
        first_image = self.find_first_image(body_content)
        if first_image:
            if '1drv.ms' in first_image or 'sharepoint.com' in first_image:
                print(f"🖼️ 使用正文第一张OneDrive图片: {first_image}")
                return first_image
            else:
                print(f"🖼️ 使用正文第一张图片: {first_image}")
                # 直接使用本地图片路径，后续由OneDrive处理器自动处理
                return first_image
        
        # 优先级3: 使用默认OneDrive链接
        print("🖼️ 未找到图片，使用默认OneDrive链接")
        return "https://1drv.ms/i/c/5644dab129afda10/IQTq4kEOrERvRLHS_4L9uCK_ARjvU4zbducjMUCRTRR8Pdk"

    def format_content(self, content: str) -> str:
        """
        格式化文章内容
        
        Args:
            content: 原始内容
            
        Returns:
            格式化后的内容
        """
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            
            # 跳过空行
            if not line:
                formatted_lines.append('')
                continue
            
            # 处理标题（确保标题格式正确）
            if line.startswith('#'):
                # 确保标题后有空格
                if not line[1:].startswith(' '):
                    line = line[0] + ' ' + line[1:]
                formatted_lines.append(line)
            
            # 处理列表项
            elif line.startswith('-') or line.startswith('*'):
                if not line[1:].startswith(' '):
                    line = line[0] + ' ' + line[1:]
                formatted_lines.append(line)
            
            # 处理编号列表
            elif re.match(r'^\d+\.', line):
                formatted_lines.append(line)
            
            # 普通段落
            else:
                formatted_lines.append(line)
        
        # 在适当位置添加<!-- more -->标签
        content_with_more = self.add_more_tag('\n'.join(formatted_lines))
        
        return content_with_more

    def create_content_structure(self, content: str, title: str) -> str:
        """
        创建标准内容结构：摘要 + <!-- more --> + 背景介绍(可选) + 主体内容
        
        Args:
            content: 原始内容
            title: 文章标题
            
        Returns:
            结构化的内容
        """
        lines = content.split('\n')
        clean_lines = [line.strip() for line in lines if line.strip()]
        
        if not clean_lines:
            return content
        
        # 生成开头摘要 (50-60字符)
        summary = self.generate_opening_summary(content, title)
        
        # 判断是否需要背景介绍
        needs_background = self.needs_background_introduction(content, title)
        
        # 构建结构化内容
        structured_content = [summary, '', '<!-- more -->', '']
        
        # 如果需要背景介绍，添加背景介绍部分
        if needs_background:
            background = self.generate_background_introduction(content, title)
            structured_content.extend(['## 背景介绍', '', background, ''])
        
        # 添加主体内容
        structured_content.extend(['## 主要内容', ''] + clean_lines)
        
        return '\n'.join(structured_content)

    def format_basic_structure(self, content: str) -> str:
        """
        对结构化内容进行基础格式化
        
        Args:
            content: 结构化内容
            
        Returns:
            格式化后的内容
        """
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            # 保留空行和特殊标记
            if not line.strip() or line.strip() == '<!-- more -->':
                formatted_lines.append(line)
                continue
            
            # 处理标题（确保标题格式正确）
            if line.startswith('#'):
                if not line[1:].startswith(' '):
                    line = line[0] + ' ' + line[1:]
                formatted_lines.append(line)
            
            # 处理列表项
            elif line.startswith('-') or line.startswith('*'):
                if not line[1:].startswith(' '):
                    line = line[0] + ' ' + line[1:]
                formatted_lines.append(line)
            
            # 处理编号列表
            elif re.match(r'^\d+\.', line):
                formatted_lines.append(line)
            
            # 普通段落
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)

    def generate_opening_summary(self, content: str, title: str) -> str:
        """
        生成开头摘要段落 (50-60字符)
        
        Args:
            content: 文章内容
            title: 文章标题
            
        Returns:
            摘要段落
        """
        # 移除markdown格式
        clean_content = re.sub(r'[#*`\[\](){}]', '', content)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # 提取关键句子
        sentences = re.split(r'[。！？.!?]', clean_content)
        key_sentences = [s.strip() for s in sentences[:3] if len(s.strip()) > 10]
        
        if key_sentences:
            # 从第一句开始构建摘要
            summary = key_sentences[0]
            
            # 确保长度在50-60字符
            if len(summary) > 60:
                summary = summary[:57] + "..."
            elif len(summary) < 50 and len(key_sentences) > 1:
                # 尝试添加第二句的部分内容
                remaining = 57 - len(summary) - 1  # 预留省略号空间
                if remaining > 10:
                    addition = key_sentences[1][:remaining]
                    summary = summary + "，" + addition + "..."
        else:
            # 回退方案：基于标题生成摘要
            summary = f"本文探讨{title}相关的核心观点和实用方法，为读者提供有价值的思考和参考。"
        
        return summary

    def needs_background_introduction(self, content: str, title: str) -> bool:
        """
        判断是否需要背景介绍段落
        
        Args:
            content: 文章内容
            title: 文章标题
            
        Returns:
            是否需要背景介绍
        """
        # 检查内容复杂性指标
        complexity_indicators = 0
        
        # 1. 内容长度 (超过1500字符认为复杂)
        if len(content) > 1500:
            complexity_indicators += 1
        
        # 2. 专业术语密度
        technical_terms = ['api', 'ai', '算法', '模型', '架构', '系统', '平台', '框架', '技术', '方案', '策略', '机制']
        text_lower = content.lower()
        term_count = sum(1 for term in technical_terms if term in text_lower)
        if term_count >= 3:
            complexity_indicators += 1
        
        # 3. 数据和数字密度
        numbers = re.findall(r'\d+%|\d+\.\d+%|\d+万|\d+亿|\$\d+', content)
        if len(numbers) >= 3:
            complexity_indicators += 1
        
        # 4. 外部引用 (URL、引用等)
        references = re.findall(r'http[s]?://|据.*报道|研究显示|调查表明', content)
        if len(references) >= 2:
            complexity_indicators += 1
        
        # 5. 多级标题结构
        headers = re.findall(r'^#{2,4}\s', content, re.MULTILINE)
        if len(headers) >= 3:
            complexity_indicators += 1
        
        # 如果复杂性指标达到2个或以上，需要背景介绍
        return complexity_indicators >= 2

    def generate_background_introduction(self, content: str, title: str) -> str:
        """
        生成背景介绍段落
        
        Args:
            content: 文章内容
            title: 文章标题
            
        Returns:
            背景介绍内容
        """
        # 提取可能的背景信息
        background_elements = []
        
        # 1. 时间背景
        time_patterns = [
            r'(\d{4}年\d{1,2}月)', r'(近期|最近|今年)', r'(去年|上个月)',
            r'(\d{1,2}月\d{1,2}日)', r'(本周|上周)'
        ]
        for pattern in time_patterns:
            matches = re.findall(pattern, content)
            if matches:
                background_elements.append(f"时间背景：{matches[0]}")
                break
        
        # 2. 事件背景
        event_keywords = ['发布', '宣布', '推出', '更新', '升级', '变化', '调整']
        for keyword in event_keywords:
            if keyword in content:
                # 找到包含关键词的句子
                sentences = re.split(r'[。！？.!?]', content)
                for sentence in sentences:
                    if keyword in sentence and len(sentence.strip()) > 20:
                        background_elements.append(f"事件背景：{sentence.strip()}")
                        break
                break
        
        # 3. 概念解释 (如果标题包含专业术语)
        technical_terms = {
            'AI': '人工智能技术',
            'API': '应用程序编程接口',
            'TTS': '文本转语音技术',
            'OAuth': '开放授权协议',
            'CDN': '内容分发网络'
        }
        for term, explanation in technical_terms.items():
            if term.lower() in title.lower():
                background_elements.append(f"概念说明：{term}是指{explanation}")
                break
        
        # 构建背景介绍
        if background_elements:
            intro = "为了更好地理解本文内容，这里先提供一些背景信息：\n\n"
            intro += "\n".join(f"- {element}" for element in background_elements)
            return intro
        else:
            return f"本文将详细分析{title}的相关内容，帮助读者深入理解相关概念和应用场景。"

    def add_more_tag(self, content: str) -> str:
        """
        保持原有的more标签添加逻辑（作为备选方案）
        """
        lines = content.split('\n')
        
        # 寻找第一个合适的段落结束位置（大约200-400字符处）
        char_count = 0
        for i, line in enumerate(lines):
            char_count += len(line)
            
            # 在200-400字符之间寻找段落结束
            if 200 <= char_count <= 400 and line.strip() == '':
                lines.insert(i + 1, '<!-- more -->')
                break
            # 如果超过400字符，强制插入
            elif char_count > 400 and line.strip() == '':
                lines.insert(i + 1, '<!-- more -->')
                break
        else:
            # 如果没找到合适位置，在第3段后插入
            paragraph_count = 0
            for i, line in enumerate(lines):
                if line.strip() != '' and not line.startswith('#'):
                    paragraph_count += 1
                    if paragraph_count == 3 and i + 1 < len(lines):
                        lines.insert(i + 1, '')
                        lines.insert(i + 2, '<!-- more -->')
                        break
        
        return '\n'.join(lines)

    def add_footer(self, content: str, category: str) -> str:
        """
        添加页脚内容
        
        Args:
            content: 文章内容
            category: 文章分类
            
        Returns:
            添加页脚的内容
        """
        footer_templates = {
            'investment-finance': '''
---

{% assign investment_tags = 'QDII基金,指数投资,标普500,纳斯达克,美股投资,投资理财,财务规划,资产配置' | split: ',' %}
{% assign current_tags = page.tags %}
{% assign has_investment = false %}
{% for tag in investment_tags %}
  {% if current_tags contains tag %}
    {% assign has_investment = true %}
    {% break %}
  {% endif %}
{% endfor %}

{% if has_investment %}
> **⚠️ 投资风险提示**
> 
> 本文涉及投资内容仅供教育和信息目的，不构成投资建议。投资有风险，入市需谨慎。
> 
> - 任何投资决策应基于个人财务状况和风险承受能力
> - 过往表现不代表未来结果
> - 建议在做出投资决策前咨询专业财务顾问
> - 请自行承担投资风险和责任
{% endif %}''',
            
            'tech-empowerment': '''
---

> **💡 工具使用提示**
> 
> 文中提到的工具和方法仅供参考，使用前请：
> - 确保了解相关风险和限制
> - 遵守相关服务条款和法律法规  
> - 根据个人需求选择合适的解决方案''',
            
            'global-perspective': '''
---

> **🌍 观点声明**
> 
> 本文观点基于公开信息和个人分析，仅供读者参考和思考。
> 不同文化背景和立场可能产生不同理解，欢迎理性讨论。''',
            
            'cognitive-upgrade': '''
---

> **🧠 学习建议**
> 
> 认知升级是个人化的过程，文中方法仅供参考。
> 建议结合个人实际情况，循序渐进地实践和改进。'''
        }
        
        footer = footer_templates.get(category, '')
        return content + footer

    def process_draft(self, input_file: Path, output_file: Optional[Path] = None,
                     title: Optional[str] = None, category: Optional[str] = None,
                     tags: Optional[List[str]] = None) -> Path:
        """
        处理草稿文件
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径（可选）
            title: 指定标题（可选）
            category: 指定分类（可选）
            tags: 指定标签（可选）
            
        Returns:
            输出文件路径
        """
        # 读取原始内容
        with open(input_file, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        # 检查是否已有front matter
        if raw_content.startswith('---'):
            print("⚠️ 检测到已存在front matter，检查header字段完整性")
            
            # 解析现有的front matter
            try:
                # 分离front matter和内容
                parts = raw_content.split('---', 2)
                if len(parts) >= 3:
                    yaml_content = parts[1]
                    body_content = parts[2].strip()
                    
                    import yaml
                    front_matter = yaml.safe_load(yaml_content)
                    
                    # 检查并修复header字段
                    header_updated = self.fix_header_field(front_matter, body_content)
                    
                    if header_updated:
                        # 重新生成文件
                        yaml_content = yaml.dump(front_matter, default_flow_style=False, 
                                               allow_unicode=True, sort_keys=False)
                        updated_content = f"---\n{yaml_content}---\n{body_content}"
                        
                        with open(input_file, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        
                        print("🔧 已修复header字段")
                    else:
                        print("✅ header字段已完整")
                        
            except Exception as e:
                print(f"⚠️ 解析front matter失败: {e}")
                
            print(f"✅ 格式化完成: {input_file}")
            return input_file
        
        # 提取标题（如果未指定）
        if not title:
            # 尝试从第一行提取标题
            lines = raw_content.strip().split('\n')
            if lines and lines[0].startswith('#'):
                title = lines[0].lstrip('# ').strip()
                # 移除标题行
                raw_content = '\n'.join(lines[1:]).strip()
            else:
                # 使用文件名作为标题
                title = input_file.stem.replace('-', ' ').replace('_', ' ').title()
        
        # 创建front matter
        front_matter = self.create_front_matter(title, raw_content, category, tags)

        # 不再自动创建结构化内容，直接使用原始内容
        # 只进行基础格式化（修复标点、段落等）
        formatted_content = self.format_basic_structure(raw_content)

        # 不自动添加页脚，让发布时处理
        final_content = formatted_content
        
        # 生成YAML front matter - 使用yaml库来正确格式化
        import yaml
        yaml_content = yaml.dump(front_matter, default_flow_style=False,
                                 allow_unicode=True, sort_keys=False)

        # 组合最终内容
        full_content = f"---\n{yaml_content}---\n\n{final_content}"
        
        # 确定输出文件路径
        if not output_file:
            # 默认就地更新原文件
            output_file = input_file
        
        # 确保输出目录存在
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"✅ 格式化完成: {output_file}")
        print(f"📊 统计信息:")
        print(f"   标题: {title}")
        print(f"   内容长度: {len(final_content)} 字符")
        
        # 执行统一的内容质量检查
        if self.unified_check_available:
            print(f"\n🔍 正在进行内容质量检查...")
            check_results = self.content_pipeline.comprehensive_content_check(
                output_file, auto_fix=True
            )
            
            if check_results['check_passed']:
                print("✅ 内容质量检查通过！")
            else:
                print("⚠️ 发现内容质量问题：")
                
                # 显示自动修复的问题
                if check_results['auto_fixes_applied']:
                    print(f"🔧 已自动修复：")
                    for fix in check_results['auto_fixes_applied']:
                        print(f"   • {fix}")
                
                # 显示需要手动处理的问题
                if check_results['manual_fixes_needed']:
                    print(f"\n💡 需要手动处理的问题：")
                    for item in check_results['manual_fixes_needed']:
                        print(f"   • {item['issue']}")
                        for suggestion in item['suggestions']:
                            print(f"     {suggestion}")
                
                print(f"\n📋 建议：使用 '2. 内容规范化处理' → '5. 查看内容质量检查' 了解详情")
        else:
            print("\n💡 提示：安装完整依赖可启用高级内容质量检查")
        
        return output_file

def main():
    parser = argparse.ArgumentParser(description="手工草稿快速排版工具")
    parser.add_argument("input", help="输入文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-t", "--title", help="指定文章标题")
    parser.add_argument("-c", "--category", 
                       choices=['cognitive-upgrade', 'tech-empowerment', 'global-perspective', 'investment-finance'],
                       help="指定文章分类")
    parser.add_argument("--tags", nargs='+', help="指定标签（多个标签用空格分隔）")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    # 检查输入文件
    input_file = Path(args.input)
    if not input_file.exists():
        print(f"❌ 输入文件不存在: {input_file}")
        sys.exit(1)
    
    # 创建格式化器
    formatter = DraftFormatter()
    
    try:
        output_file = args.output
        if output_file:
            output_file = Path(output_file)
        
        # 处理草稿
        result_file = formatter.process_draft(
            input_file=input_file,
            output_file=output_file,
            title=args.title,
            category=args.category,
            tags=args.tags
        )
        
        print(f"\n🎉 处理完成！")
        print(f"📄 格式化后的文件: {result_file}")
        print(f"💡 现在可以使用 run.py 的「处理现有草稿」功能发布到各平台")
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()