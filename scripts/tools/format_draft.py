#!/usr/bin/env python3
"""
手工草稿快速排版工具
用于将手工编写的草稿内容快速格式化为符合项目规范的Jekyll文章
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import re

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

class DraftFormatter:
    """草稿格式化器"""
    
    def __init__(self):
        """初始化格式化器"""
        self.project_root = project_root
        self.drafts_dir = self.project_root / "_drafts"
        self.config_dir = self.project_root / "config"
        
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
        best_category = max(category_scores, key=category_scores.get)
        
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

    def generate_excerpt(self, content: str) -> str:
        """
        生成文章摘要
        
        Args:
            content: 文章内容
            
        Returns:
            生成的摘要（50-60字符）
        """
        # 移除markdown格式和特殊字符
        clean_content = re.sub(r'[#*`\[\](){}]', '', content)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # 取前100字符，然后找到合适的截断点
        excerpt = clean_content[:100]
        
        # 在句号、感叹号、问号处截断
        for punct in ['。', '！', '？', '.', '!', '?']:
            if punct in excerpt[30:80]:  # 在合理位置寻找标点
                excerpt = excerpt[:excerpt.find(punct, 30) + 1]
                break
        
        # 如果还是太长，强制截断到60字符
        if len(excerpt) > 60:
            excerpt = excerpt[:57] + "..."
        
        return excerpt

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
        
        # 构建front matter
        front_matter = {
            "title": title,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "categories": [detected_category],
            "tags": generated_tags,
            "excerpt": excerpt,
            "header": {
                "teaser": "/assets/images/default-teaser.jpg"  # 默认头图
            }
        }
        
        # 添加默认配置
        front_matter.update(self.default_config)
        
        return front_matter

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

    def add_more_tag(self, content: str) -> str:
        """
        在适当位置添加<!-- more -->标签
        
        Args:
            content: 文章内容
            
        Returns:
            添加more标签的内容
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
            print("⚠️ 检测到已存在front matter，将保留现有格式")
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
        
        # 格式化内容
        formatted_content = self.format_content(raw_content)
        
        # 添加页脚
        final_content = self.add_footer(formatted_content, front_matter['categories'][0])
        
        # 生成YAML front matter
        yaml_lines = ['---']
        for key, value in front_matter.items():
            if isinstance(value, str):
                yaml_lines.append(f'{key}: "{value}"')
            elif isinstance(value, bool):
                yaml_lines.append(f'{key}: {str(value).lower()}')
            elif isinstance(value, list):
                yaml_lines.append(f'{key}: {json.dumps(value, ensure_ascii=False)}')
            elif isinstance(value, dict):
                yaml_lines.append(f'{key}:')
                for sub_key, sub_value in value.items():
                    yaml_lines.append(f'  {sub_key}: "{sub_value}"')
            else:
                yaml_lines.append(f'{key}: {value}')
        yaml_lines.append('---')
        yaml_lines.append('')
        
        # 组合最终内容
        full_content = '\n'.join(yaml_lines) + final_content
        
        # 确定输出文件路径
        if not output_file:
            today = datetime.now().strftime('%Y-%m-%d')
            safe_title = re.sub(r'[^\w\s-]', '', title).strip()
            safe_title = re.sub(r'[-\s]+', '-', safe_title).lower()[:50]
            output_file = self.drafts_dir / f"{today}-{safe_title}.md"
        
        # 确保输出目录存在
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        print(f"✅ 格式化完成: {output_file}")
        print(f"📊 统计信息:")
        print(f"   标题: {title}")
        print(f"   分类: {front_matter['categories'][0]}")
        print(f"   标签: {', '.join(front_matter['tags'])}")
        print(f"   摘要: {front_matter['excerpt']}")
        print(f"   内容长度: {len(final_content)} 字符")
        
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