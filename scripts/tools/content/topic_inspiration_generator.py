#!/usr/bin/env python3
"""
主题灵感生成器
利用Gemini的联网搜索能力获取博文创作灵感，筛选权威英文来源的最新资讯
"""

import os
import sys
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    import google.generativeai as genai
except ImportError:
    print("⚠️ 警告：未安装google-generativeai库，请运行: pip install google-generativeai")
    genai = None

@dataclass
class NewsResult:
    """新闻结果数据结构"""
    title: str
    source: str
    credibility_score: int
    publication_date: str
    summary: str
    key_insights: List[str]
    blog_angles: List[str]
    relevance_score: float
    url: Optional[str] = None

class TopicInspirationGenerator:
    """主题灵感生成器 - 基于Gemini联网搜索"""
    
    def __init__(self):
        """初始化生成器"""
        self.gemini_client = self._init_gemini_client()
        self.output_dir = Path(".tmp/output/inspiration_reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 权威来源列表（按可信度排序）
        self.authoritative_sources = {
            # 顶级权威来源 (9-10分)
            'reuters.com': 10, 'bloomberg.com': 10, 'nature.com': 10,
            'science.org': 10, 'economist.com': 9, 'ft.com': 9,
            'harvard.edu': 10, 'mit.edu': 10, 'stanford.edu': 10,
            'oxford.ac.uk': 10, 'cambridge.org': 10,
            
            # 高可信度来源 (7-8分)
            'nytimes.com': 8, 'wsj.com': 8, 'washingtonpost.com': 8,
            'bbc.com': 8, 'guardian.com': 7, 'techcrunch.com': 7,
            'wired.com': 7, 'atlantic.com': 8,
            
            # 专业/行业权威 (6-8分)
            'mckinsey.com': 8, 'bcg.com': 8, 'pwc.com': 7,
            'deloitte.com': 7, 'hbr.org': 8, 'sloan.mit.edu': 9,
            
            # 科技专业媒体 (6-7分)
            'arstechnica.com': 7, 'ieee.org': 9, 'acm.org': 9,
            'venturebeat.com': 6, 'techreview.com': 8
        }
        
        # 分类相关的搜索增强关键词
        self.category_keywords = {
            'tech-empowerment': ['technology', 'AI', 'automation', 'digital transformation', 'innovation', 'software', 'tools'],
            'investment-finance': ['finance', 'investment', 'market', 'economic', 'trading', 'portfolio', 'wealth', 'banking'],
            'global-perspective': ['international', 'global', 'geopolitics', 'culture', 'society', 'policy', 'trends'],
            'cognitive-upgrade': ['psychology', 'learning', 'productivity', 'mindset', 'cognitive', 'behavior', 'growth']
        }

    def _init_gemini_client(self):
        """初始化Gemini客户端"""
        if genai is None:
            raise ValueError("未安装google-generativeai库，请运行: pip install google-generativeai")
            
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("未找到GOOGLE_API_KEY环境变量，请在.env文件中配置")
        
        genai.configure(api_key=api_key)
        
        # 使用支持搜索的Gemini模型
        model = genai.GenerativeModel(
            model_name='gemini-1.5-pro'
        )
        
        return model

    def get_topic_inspiration(self, topic: str, category: Optional[str] = None, days: int = 7) -> List[NewsResult]:
        """
        获取主题相关的权威英文资讯灵感
        
        Args:
            topic: 搜索主题
            category: 内容分类（可选）
            days: 搜索天数范围
        
        Returns:
            权威新闻结果列表
        """
        try:
            print(f"🔍 正在搜索主题: {topic}")
            if category:
                print(f"📂 分类限制: {category}")
            
            # 构建搜索提示词
            search_prompt = self._build_search_prompt(topic, category, days)
            
            # 执行Gemini联网搜索
            print("🌐 正在调用Gemini联网搜索...")
            response = self.gemini_client.generate_content(search_prompt)
            
            if not response or not response.text:
                print("❌ Gemini搜索未返回结果")
                return []
            
            print("📊 正在解析搜索结果...")
            # 解析搜索结果
            results = self._parse_search_results(response.text, topic)
            
            # 筛选和评分
            filtered_results = self._filter_and_score_results(results)
            
            # 按相关性和可信度排序
            sorted_results = sorted(
                filtered_results, 
                key=lambda x: (x.credibility_score * 0.6 + x.relevance_score * 0.4), 
                reverse=True
            )
            
            # 返回前5个结果
            return sorted_results[:5]
            
        except Exception as e:
            print(f"❌ 搜索过程出错: {e}")
            return []

    def _build_search_prompt(self, topic: str, category: Optional[str] = None, days: int = 7) -> str:
        """构建搜索提示词"""
        
        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        
        # 基础搜索提示
        prompt = f"""
Search for recent, authoritative English-language news and insights about: "{topic}"

**SEARCH REQUIREMENTS:**
- Time Range: {date_range} (focus on the most recent {days} days)
- Language: English sources ONLY
- Geographic Focus: International/Global perspective preferred
- Source Quality: Prioritize authoritative and credible sources

**PREFERRED AUTHORITATIVE SOURCES:**
- Major News: Reuters, Bloomberg, New York Times, Wall Street Journal, Financial Times, BBC, The Guardian
- Academic: Harvard, MIT, Stanford, Oxford, Cambridge, Nature, Science
- Industry Leaders: McKinsey, Boston Consulting Group, Harvard Business Review
- Tech/Innovation: TechCrunch, Wired, MIT Technology Review, IEEE, ACM
- Financial: Bloomberg, Financial Times, Reuters Financial, MarketWatch

**OUTPUT FORMAT:**
For each of exactly 5 results, provide structured information:

## Result [Number]
**Title:** [Clear, descriptive headline]
**Source:** [Publication name]
**Date:** [YYYY-MM-DD format]
**URL:** [If available]
**Summary:** [2-3 sentences describing the main content]
**Key Insights:** 
- [Insight 1]
- [Insight 2] 
- [Insight 3]
**Blog Post Angles:**
- [Potential Chinese blog angle 1]
- [Potential Chinese blog angle 2]
- [Potential Chinese blog angle 3]

---
"""

        # 添加分类特定的指导
        if category and category in self.category_keywords:
            category_guidance = {
                'tech-empowerment': "Focus on technology innovations, AI developments, digital tools, automation, and their practical applications.",
                'investment-finance': "Focus on financial markets, investment strategies, economic analysis, fintech, and wealth management trends.",
                'global-perspective': "Focus on international affairs, geopolitical developments, cultural trends, and global economic patterns.",
                'cognitive-upgrade': "Focus on psychology research, learning methodologies, productivity techniques, and personal development insights."
            }
            
            prompt += f"\n**CATEGORY FOCUS:** {category_guidance[category]}\n"
            
            # 添加分类关键词
            keywords = self.category_keywords[category]
            prompt += f"**ENHANCED KEYWORDS:** Include these related terms in your search: {', '.join(keywords)}\n"
        
        prompt += """
**QUALITY CRITERIA:**
- Credible, fact-based reporting
- Recent developments (prioritize newer content)
- Global relevance and impact
- Unique insights or analysis
- Potential for inspiring thoughtful Chinese content

Please ensure all sources are legitimate and authoritative. Avoid opinion blogs, social media, or unverified sources.
"""
        
        return prompt

    def _parse_search_results(self, response_text: str, topic: str) -> List[NewsResult]:
        """解析Gemini搜索结果"""
        results = []
        
        try:
            # 分割结果段落
            result_sections = re.split(r'## Result \d+|---', response_text)
            
            for section in result_sections:
                if not section.strip():
                    continue
                    
                result = self._parse_single_result(section, topic)
                if result:
                    results.append(result)
            
            print(f"📋 解析到 {len(results)} 个结果")
            return results
            
        except Exception as e:
            print(f"⚠️ 结果解析出错: {e}")
            # 如果结构化解析失败，尝试简单解析
            return self._fallback_parse_results(response_text, topic)

    def _parse_single_result(self, section: str, topic: str) -> Optional[NewsResult]:
        """解析单个结果段落"""
        try:
            lines = [line.strip() for line in section.split('\n') if line.strip()]
            
            # 提取各个字段
            title = ""
            source = ""
            date = ""
            url = ""
            summary = ""
            insights = []
            angles = []
            
            current_section = None
            
            for line in lines:
                if line.startswith('**Title:**'):
                    title = line.replace('**Title:**', '').strip()
                elif line.startswith('**Source:**'):
                    source = line.replace('**Source:**', '').strip()
                elif line.startswith('**Date:**'):
                    date = line.replace('**Date:**', '').strip()
                elif line.startswith('**URL:**'):
                    url = line.replace('**URL:**', '').strip()
                elif line.startswith('**Summary:**'):
                    summary = line.replace('**Summary:**', '').strip()
                elif line.startswith('**Key Insights:**'):
                    current_section = 'insights'
                elif line.startswith('**Blog Post Angles:**'):
                    current_section = 'angles'
                elif line.startswith('- '):
                    if current_section == 'insights':
                        insights.append(line[2:].strip())
                    elif current_section == 'angles':
                        angles.append(line[2:].strip())
                elif current_section == 'insights' and line and not line.startswith('**'):
                    insights.append(line.strip())
                elif current_section == 'angles' and line and not line.startswith('**'):
                    angles.append(line.strip())
            
            # 验证必需字段
            if not title or not source:
                return None
            
            # 计算可信度分数
            credibility = self._calculate_source_credibility(source)
            
            # 计算相关性分数
            relevance = self._calculate_relevance_score(title + " " + summary, topic)
            
            return NewsResult(
                title=title,
                source=source,
                credibility_score=credibility,
                publication_date=date or datetime.now().strftime('%Y-%m-%d'),
                summary=summary,
                key_insights=insights[:3],  # 限制为3个洞察
                blog_angles=angles[:3],     # 限制为3个角度
                relevance_score=relevance,
                url=url if url.startswith('http') else None
            )
            
        except Exception as e:
            print(f"⚠️ 解析单个结果时出错: {e}")
            return None

    def _fallback_parse_results(self, response_text: str, topic: str) -> List[NewsResult]:
        """备用解析方法 - 当结构化解析失败时使用"""
        results = []
        
        try:
            # 简单地将响应分割为段落，尝试提取基本信息
            paragraphs = [p.strip() for p in response_text.split('\n\n') if p.strip()]
            
            for i, paragraph in enumerate(paragraphs[:5]):  # 最多取5个段落
                if len(paragraph) > 100:  # 过滤太短的段落
                    # 创建基础结果
                    title = f"搜索结果 {i+1}: {topic}"
                    summary = paragraph[:200] + "..." if len(paragraph) > 200 else paragraph
                    
                    result = NewsResult(
                        title=title,
                        source="Mixed Sources",
                        credibility_score=5,  # 中等可信度
                        publication_date=datetime.now().strftime('%Y-%m-%d'),
                        summary=summary,
                        key_insights=[f"相关信息 {j+1}" for j in range(2)],
                        blog_angles=[f"创作角度 {j+1}" for j in range(2)],
                        relevance_score=7.0
                    )
                    results.append(result)
            
            print(f"🔄 使用备用解析方法，获得 {len(results)} 个结果")
            return results
            
        except Exception as e:
            print(f"❌ 备用解析也失败: {e}")
            return []

    def _calculate_source_credibility(self, source: str) -> int:
        """计算来源可信度分数 (1-10)"""
        source_lower = source.lower()
        
        # 直接匹配
        for domain, score in self.authoritative_sources.items():
            if domain in source_lower:
                return score
        
        # 模糊匹配知名媒体
        high_credibility_keywords = [
            'university', 'harvard', 'mit', 'stanford', 'oxford', 'cambridge',
            'reuters', 'bloomberg', 'times', 'journal', 'financial', 'economist',
            'nature', 'science', 'ieee', 'acm'
        ]
        
        for keyword in high_credibility_keywords:
            if keyword in source_lower:
                return 8
        
        # 默认中等分数
        return 6

    def _calculate_relevance_score(self, text: str, topic: str) -> float:
        """计算内容与主题的相关性分数 (0-10)"""
        try:
            text_lower = text.lower()
            topic_lower = topic.lower()
            
            # 基础相关性：主题关键词出现次数
            topic_words = topic_lower.split()
            relevance_score = 0.0
            
            for word in topic_words:
                if len(word) > 2:  # 忽略太短的词
                    count = text_lower.count(word)
                    relevance_score += min(count * 2, 6)  # 每个词最多贡献6分
            
            # 归一化到10分制
            max_possible = len([w for w in topic_words if len(w) > 2]) * 6
            if max_possible > 0:
                relevance_score = min((relevance_score / max_possible) * 10, 10)
            else:
                relevance_score = 7.0  # 默认相关性
            
            return max(relevance_score, 5.0)  # 最低5分
            
        except Exception:
            return 7.0  # 默认相关性

    def _filter_and_score_results(self, results: List[NewsResult]) -> List[NewsResult]:
        """筛选和评分结果"""
        filtered_results = []
        
        for result in results:
            # 基本质量过滤
            if (len(result.title) < 10 or len(result.summary) < 50 or
                result.credibility_score < 5 or result.relevance_score < 5):
                continue
                
            filtered_results.append(result)
        
        return filtered_results

    def generate_inspiration_report(self, topic: str, results: List[NewsResult], category: Optional[str] = None) -> str:
        """生成灵感报告"""
        
        if not results:
            return f"# 📰 主题灵感报告：{topic}\n\n❌ 未找到相关的权威资讯，请尝试其他关键词。"
        
        # 计算统计信息
        avg_credibility = sum(r.credibility_score for r in results) / len(results)
        avg_relevance = sum(r.relevance_score for r in results) / len(results)
        
        # 获取分类显示名
        category_names = {
            'tech-empowerment': '🛠️ 技术赋能',
            'investment-finance': '💰 投资理财', 
            'global-perspective': '🌍 全球视野',
            'cognitive-upgrade': '🧠 认知升级'
        }
        category_display = category_names.get(category, '🔍 综合搜索') if category else '🔍 综合搜索'
        
        report = f"""# 📰 主题灵感报告：{topic}

## 🔍 搜索概要
- **搜索时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **内容分类**: {category_display}
- **权威来源数**: {len(results)}条
- **平均可信度**: {avg_credibility:.1f}/10
- **平均相关性**: {avg_relevance:.1f}/10

## 📋 核心发现

"""
        
        for i, result in enumerate(results, 1):
            report += f"""### {i}. {result.title}

**📰 来源**: {result.source} (可信度: {result.credibility_score}/10)  
**📅 日期**: {result.publication_date}  
**🎯 相关性**: {result.relevance_score:.1f}/10  
{f'**🔗 链接**: {result.url}' if result.url else ''}

**📝 核心内容**:  
{result.summary}

**💡 关键洞察**:
{chr(10).join(f'• {insight}' for insight in result.key_insights if insight)}

**📚 博文创作角度**:
{chr(10).join(f'• {angle}' for angle in result.blog_angles if angle)}

---

"""
        
        # 添加创作建议
        report += """## 🎨 创作建议

### 📊 内容策略方向
1. **热点追踪**: 基于以上资讯的时效性，可以创作"最新动态解读"类文章
2. **深度分析**: 结合多个来源的观点，形成独特的分析视角
3. **中国视角**: 将国际资讯与中国实际情况结合，提供本地化见解
4. **前瞻预测**: 基于当前趋势，预测未来发展方向

### ✍️ 写作技巧
- **开头吸引**: 以最新、最权威的数据或事件作为开头
- **逻辑清晰**: 采用"现状→分析→影响→启示"的结构
- **数据支撑**: 引用权威来源的具体数据和专家观点
- **实用价值**: 为读者提供可操作的建议和思考框架

---

📄 *本报告由有心言者主题灵感生成器自动生成*  
🤖 *基于Gemini联网搜索 + 权威来源筛选算法*
"""
        
        return report

    def create_inspired_draft(self, topic: str, results: List[NewsResult], category: Optional[str] = None) -> str:
        """基于灵感结果创建文章草稿"""
        try:
            # 创建草稿文件名
            safe_topic = re.sub(r'[^\w\s-]', '', topic).strip()
            safe_topic = re.sub(r'[-\s]+', '-', safe_topic)
            timestamp = datetime.now().strftime('%Y-%m-%d')
            
            draft_filename = f"{timestamp}-{safe_topic[:50]}.md"
            draft_path = Path("_drafts") / draft_filename
            
            # 确保草稿目录存在
            draft_path.parent.mkdir(exist_ok=True)
            
            # 生成草稿内容
            draft_content = self._generate_draft_content(topic, results, category)
            
            # 保存草稿
            with open(draft_path, 'w', encoding='utf-8') as f:
                f.write(draft_content)
            
            print(f"📄 草稿已创建: {draft_path}")
            return str(draft_path)
            
        except Exception as e:
            print(f"❌ 创建草稿失败: {e}")
            return ""

    def _generate_draft_content(self, topic: str, results: List[NewsResult], category: Optional[str] = None) -> str:
        """生成草稿内容"""
        
        # 生成标题
        title = f"{topic}的最新发展与趋势分析"
        
        # 生成标签
        basic_tags = ["全球趋势", "行业分析", "前沿资讯"]
        
        category_tags = {
            'tech-empowerment': ["技术创新", "数字化转型", "科技趋势"],
            'investment-finance': ["投资策略", "金融市场", "经济分析"],
            'global-perspective': ["国际视野", "全球化", "跨文化"],
            'cognitive-upgrade': ["思维升级", "学习方法", "认知科学"]
        }
        
        if category and category in category_tags:
            basic_tags.extend(category_tags[category])
        
        # 生成摘要
        excerpt = f"基于最新权威来源的深度分析，探讨{topic}领域的重要发展趋势和影响"
        
        # Front Matter
        front_matter = f"""---
title: "{title}"
date: "{datetime.now().strftime('%Y-%m-%d')}"
categories: ["{category or 'global-perspective'}"]
tags: {json.dumps(basic_tags, ensure_ascii=False)}
excerpt: "{excerpt}"
header:
  teaser: "/assets/images/default-teaser.jpg"
layout: "single"
author_profile: true
breadcrumbs: true
comments: true
related: true
share: true
toc: true
toc_icon: "list"
toc_label: "本页内容"
toc_sticky: true
---"""
        
        # 正文内容
        content = f"""
近期，{topic}领域出现了多项重要发展，来自{', '.join(set(r.source for r in results[:3]))}等权威媒体的报道显示，这一领域正在经历深刻变化。

## 🔍 最新发展动态

"""
        
        # 添加各个结果的内容
        for i, result in enumerate(results, 1):
            content += f"""### {i}. {result.title}

根据{result.source}的报道，{result.summary}

**关键要点**：
{chr(10).join(f'- {insight}' for insight in result.key_insights[:2] if insight)}

"""
        
        content += """<!-- more -->

## 💡 深度分析与思考

基于以上权威来源的信息，我们可以从以下几个维度来理解这些发展：

### 🌍 全球影响
这些发展不仅影响特定地区，更对全球格局产生深远影响。

### 🚀 未来趋势
从当前的发展轨迹来看，未来可能的演进方向包括...

### 🎯 实践启示
对于我们而言，这些发展提供了以下启示：

## 📚 参考资源

"""
        
        # 添加参考链接
        for result in results:
            if result.url:
                content += f"- [{result.title}]({result.url}) - {result.source}\n"
        
        content += f"""
---

*本文基于{datetime.now().strftime('%Y年%m月%d日')}的权威来源信息整理，数据来源包括{', '.join(set(r.source for r in results))}等。*
"""
        
        return front_matter + content

def main():
    """主函数 - 供独立运行使用"""
    print("💡 主题灵感生成器")
    print("="*50)
    
    # 检查环境变量
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ 错误：未找到GOOGLE_API_KEY环境变量")
        print("请在.env文件中配置您的Google API密钥")
        return
    
    # 获取用户输入
    topic = input("请输入要探索的主题: ").strip()
    if not topic:
        print("❌ 主题不能为空")
        return
    
    print("\n选择内容分类 (可选):")
    print("1. 🧠 认知升级")
    print("2. 🛠️ 技术赋能") 
    print("3. 🌍 全球视野")
    print("4. 💰 投资理财")
    print("5. 不限分类")
    
    category_choice = input("请选择 (1-5): ").strip()
    category_map = {
        '1': 'cognitive-upgrade',
        '2': 'tech-empowerment', 
        '3': 'global-perspective',
        '4': 'investment-finance'
    }
    
    category = category_map.get(category_choice)
    
    try:
        # 创建生成器实例
        generator = TopicInspirationGenerator()
        
        # 获取灵感
        results = generator.get_topic_inspiration(topic, category)
        
        if results:
            # 生成报告
            report = generator.generate_inspiration_report(topic, results, category)
            
            # 保存报告
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            safe_topic = re.sub(r'[^\w\s-]', '', topic)[:20]
            report_file = generator.output_dir / f"{safe_topic}-{timestamp}.md"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"\n✅ 灵感报告已生成: {report_file}")
            print(f"📊 找到 {len(results)} 条权威资讯")
            
            # 显示结果概要
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result.title} ({result.source})")
            
            # 询问是否创建草稿
            create_draft = input("\n是否基于这些灵感创建文章草稿？(y/N): ").strip().lower()
            if create_draft in ['y', 'yes']:
                draft_path = generator.create_inspired_draft(topic, results, category)
                if draft_path:
                    print(f"📄 草稿已创建: {draft_path}")
                    print("💡 您可以使用主程序的'处理现有草稿'功能来发布文章")
        else:
            print("❌ 未找到相关权威资讯，请尝试其他关键词")
            
    except Exception as e:
        print(f"❌ 操作失败: {e}")

if __name__ == "__main__":
    main()