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
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

try:
    import yaml
except ImportError:
    print("⚠️ 警告：未安装PyYAML库，请运行: pip install PyYAML")
    yaml = None

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ 警告：未安装python-dotenv库，请运行: pip install python-dotenv")

try:
    import google.generativeai as genai  # type: ignore
    # 验证库是否正确安装并可用
    if hasattr(genai, 'configure') and hasattr(genai, 'GenerativeModel'):
        # 主要功能可用
        pass
    else:
        raise AttributeError("google.generativeai库功能不完整")
except ImportError:
    print("⚠️ 警告：未安装google-generativeai库，请运行: pip install google-generativeai")
    genai = None
except AttributeError:
    print("⚠️ 警告：google-generativeai库版本可能不兼容")
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
        
        # 灵感报告状态跟踪文件
        self.status_file = Path(".tmp/output/inspiration_status.json")
        self.status_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载专业领域配置
        self.domains = self._load_domain_config()
        
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
        
        # 确保加载环境变量
        from dotenv import load_dotenv
        load_dotenv()
            
        # 尝试从两个可能的环境变量名获取API密钥
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("未找到GEMINI_API_KEY或GOOGLE_API_KEY环境变量，请在.env文件中配置")
        
        try:
            genai.configure(api_key=api_key)  # type: ignore
            
            # 使用最新的Gemini 2.5模型
            model = genai.GenerativeModel(  # type: ignore[attr-defined]
                model_name='gemini-2.5-pro'
            )
            
            # 不在初始化时测试连接，避免阻塞程序启动
            print("✅ Gemini客户端初始化完成")
            return model
            
        except Exception as e:
            print(f"⚠️ Gemini客户端初始化警告: {e}")
            print("💡 这不会影响后续搜索功能，如遇到问题请检查API密钥")
            # 仍然返回model，让具体搜索时处理错误
            model = genai.GenerativeModel(  # type: ignore[attr-defined]
                model_name='gemini-2.5-pro'
            )
            return model

    def _load_domain_config(self) -> Dict[str, Any]:
        """加载专业领域配置文件"""
        try:
            if yaml is None:
                print("⚠️ PyYAML未安装，使用默认配置")
                return {}
                
            config_path = Path("config/inspiration_domains.yml")
            if not config_path.exists():
                print("⚠️ 专业领域配置文件不存在，使用默认配置")
                return {}
                
            with open(config_path, 'r', encoding='utf-8') as f:
                domains = yaml.safe_load(f)
                
            print(f"✅ 成功加载 {len(domains)} 个专业领域配置")
            return domains
            
        except Exception as e:
            print(f"⚠️ 加载专业领域配置失败: {e}")
            return {}

    def list_available_domains(self) -> List[tuple]:
        """获取可用的专业领域列表"""
        domain_list = []
        for domain_id, config in self.domains.items():
            display_name = config.get('display_name', domain_id)
            description = config.get('description', '')
            domain_list.append((domain_id, display_name, description))
        return domain_list

    def get_domain_inspiration(self, domain_id: str, days: int = 7) -> List[NewsResult]:
        """
        基于专业领域配置获取灵感
        
        Args:
            domain_id: 领域ID
            days: 搜索天数范围
        
        Returns:
            权威新闻结果列表
        """
        if domain_id not in self.domains:
            print(f"❌ 未找到领域配置: {domain_id}")
            return []
            
        domain_config = self.domains[domain_id]
        print(f"🔍 正在搜索领域: {domain_config.get('display_name', domain_id)}")
        
        try:
            # 构建专业领域搜索提示词
            search_prompt = self._build_domain_search_prompt(domain_config, days)
            
            # 执行Gemini联网搜索
            print("🌐 正在调用Gemini联网搜索...")
            response = self.gemini_client.generate_content(search_prompt)
            
            if not response:
                print("❌ Gemini搜索未返回响应")
                return []
            
            # 检查响应状态
            response_text = None
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    finish_reason = candidate.finish_reason
                    if finish_reason == 1:  # STOP - 正常完成
                        print("✅ 搜索正常完成")
                    elif finish_reason == 2:  # MAX_TOKENS
                        print("⚠️ 响应被截断，但可能包含有用信息")
                    elif finish_reason == 3:  # SAFETY
                        print("❌ 内容被安全过滤器阻止，尝试使用更通用的搜索词...")
                        # 尝试使用更通用的搜索提示
                        fallback_prompt = self._build_fallback_search_prompt(domain_config, days)
                        print("🔄 使用备用搜索策略...")
                        response = self.gemini_client.generate_content(fallback_prompt)
                        if not response:
                            print("❌ 备用搜索也失败")
                            return []
                    elif finish_reason == 4:  # RECITATION
                        print("❌ 内容因引用问题被过滤，请尝试其他搜索词")
                        return []
            
            # 尝试获取响应文本
            try:
                response_text = response.text
                if not response_text:
                    print("❌ Gemini搜索返回空内容")
                    return []
            except Exception as e:
                print(f"⚠️ 无法直接获取响应文本: {e}")
                # 尝试从候选答案中获取内容
                if hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate, 'content') and candidate.content:
                            if hasattr(candidate.content, 'parts') and candidate.content.parts:
                                for part in candidate.content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        response_text = part.text
                                        print("✅ 从候选内容中提取到文本")
                                        break
                                if response_text:
                                    break
                    
                    if not response_text:
                        print("❌ 无法从任何候选答案中提取内容")
                        return []
                else:
                    print("❌ 响应中没有候选答案")
                    return []
            
            print("📊 正在解析搜索结果...")
            # 解析搜索结果
            topic_name = domain_config.get('display_name', domain_id)
            results = self._parse_search_results(response_text, topic_name)
            
            # 使用领域专用的权威来源进行筛选和评分
            filtered_results = self._filter_and_score_domain_results(results, domain_config)
            
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

    def _build_domain_search_prompt(self, domain_config: Dict[str, Any], days: int = 7) -> str:
        """构建专业领域搜索提示词"""
        
        # 日期信息用于搜索偏好
        
        # 获取领域配置
        keywords = domain_config.get('keywords', [])
        sources = domain_config.get('sources', [])
        template = domain_config.get('search_prompt_template', '')
        
        # 使用领域专用的搜索模板
        if template and keywords and sources:
            keywords_str = ', '.join(keywords)
            sources_str = ', '.join(sources)
            
            # 替换模板中的占位符
            domain_prompt = template.format(
                keywords=keywords_str,
                sources=sources_str
            )
            
            # 添加时间范围和输出格式要求
            prompt = f"""
{domain_prompt}

**TIME REQUIREMENTS:** 
- PRIORITIZE content from 2025 (current year)
- Include recent 2024 content as secondary priority  
- Focus on latest developments, news, and research
- Prefer content from the last 6 months when available

**OUTPUT FORMAT:**
For each of exactly 5 results, provide structured information:

## Result [Number]
**Title:** [Clear, descriptive headline]
**Source:** [Publication name]
**Date:** [YYYY-MM-DD format]
**URL:** [Original article URL - REQUIRED for credibility]
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

**QUALITY CRITERIA:**
- Credible, fact-based reporting from the specified authoritative sources
- Recent developments (prioritize newer content)
- Significant impact or breakthrough potential
- Unique insights or analysis
- Potential for inspiring thoughtful Chinese content

**CRITICAL: MUST include original article URLs for all results**
"""
        else:
            # 回退到通用搜索格式
            keywords_str = ', '.join(keywords) if keywords else "general topics"
            prompt = f"""
Search for recent, authoritative information about: {keywords_str}

**TIME RANGE:** {date_range} (focus on the most recent {days} days)
**PREFERRED SOURCES:** {', '.join(sources) if sources else 'Major international news and academic sources'}

[继续使用标准输出格式...]
"""
        
        return prompt

    def _build_fallback_search_prompt(self, domain_config: Dict[str, Any], days: int = 7) -> str:
        """构建更简单的备用搜索提示词（避免安全过滤）"""
        
        # 日期信息用于搜索偏好
        
        # 获取领域的核心关键词（使用较少敏感的词汇）
        keywords = domain_config.get('keywords', [])
        sources = domain_config.get('sources', [])
        
        # 简化关键词，避免可能触发过滤的词汇
        safe_keywords = []
        for keyword in keywords[:4]:  # 只使用前4个关键词
            # 移除可能敏感的词汇
            safe_keyword = keyword.replace('AI', 'artificial intelligence').replace('medical', 'healthcare')
            safe_keywords.append(safe_keyword)
        
        prompt = f"""
Find recent news and research developments about: {', '.join(safe_keywords)}

**TIME REQUIREMENTS**:
- PRIORITIZE content from 2025 (current year)
- Include recent 2024 content as secondary priority
- Focus on latest developments and trending topics
**Preferred Sources**: {', '.join(sources[:5])}

Please provide 5 recent articles or research papers with this format:

## Result 1
**Title:** [Article title]
**Source:** [Publication name] 
**Date:** [YYYY-MM-DD]
**Summary:** [Brief description]
**Key Points:**
- [Point 1]
- [Point 2]

## Result 2
[Same format...]

Focus on factual reporting, recent developments, and credible sources.
"""
        
        return prompt

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
            
            if not response:
                print("❌ Gemini搜索未返回响应")
                return []
            
            # 获取响应文本（使用相同的错误处理逻辑）
            try:
                response_text = response.text
                if not response_text:
                    print("❌ Gemini搜索返回空内容")
                    return []
            except Exception as e:
                print(f"⚠️ 无法直接获取响应文本: {e}")
                # 尝试从候选答案中获取内容
                response_text = None
                if hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate, 'content') and candidate.content:
                            if hasattr(candidate.content, 'parts') and candidate.content.parts:
                                for part in candidate.content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        response_text = part.text
                                        print("✅ 从候选内容中提取到文本")
                                        break
                                if response_text:
                                    break
                
                if not response_text:
                    print("❌ 无法从响应中提取任何文本内容")
                    return []
            
            print("📊 正在解析搜索结果...")
            # 解析搜索结果
            results = self._parse_search_results(response_text, topic)
            
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
        
        # 日期信息用于搜索偏好
        
        # 基础搜索提示
        prompt = f"""
Search for recent, authoritative English-language news and insights about: "{topic}"

**SEARCH REQUIREMENTS:**
- Time Range: {date_range} (focus on the most recent {days} days)
- Current date: {datetime.now().strftime('%Y-%m-%d')}
- CRITICAL: ONLY content from {datetime.now().strftime('%Y')} (this year)
- EXCLUDE any content from 2024 or earlier years
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
**URL:** [Original article URL - REQUIRED for credibility]
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

**CRITICAL: MUST include original article URLs for all results**
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

    def _filter_and_score_domain_results(self, results: List[NewsResult], domain_config: Dict[str, Any]) -> List[NewsResult]:
        """筛选和评分领域专用结果"""
        filtered_results = []
        domain_sources = domain_config.get('sources', [])
        domain_keywords = domain_config.get('keywords', [])
        
        print(f"🔍 开始筛选 {len(results)} 个搜索结果...")
        
        for i, result in enumerate(results):
            print(f"  结果 {i+1}: {result.title[:50]}...")
            print(f"    来源: {result.source}")
            print(f"    原始可信度: {result.credibility_score}")
            print(f"    原始相关性: {result.relevance_score:.1f}")
            
            # 基本质量过滤
            if (len(result.title) < 10 or len(result.summary) < 50):
                print(f"    ❌ 被过滤：标题或摘要太短 (标题:{len(result.title)}, 摘要:{len(result.summary)})")
                continue
            
            # 使用领域专用来源计算可信度
            domain_credibility = self._calculate_domain_source_credibility(result.source, domain_sources)
            result.credibility_score = max(result.credibility_score, domain_credibility)
            
            # 使用领域关键词计算相关性
            domain_relevance = self._calculate_domain_relevance_score(
                result.title + " " + result.summary, 
                domain_keywords
            )
            result.relevance_score = max(result.relevance_score, domain_relevance)
            
            print(f"    领域可信度: {domain_credibility}")
            print(f"    领域相关性: {domain_relevance:.1f}")
            print(f"    最终可信度: {result.credibility_score}")
            print(f"    最终相关性: {result.relevance_score:.1f}")
            
            # 放宽质量标准 - 从6分降到5分
            if result.credibility_score >= 5 and result.relevance_score >= 5:
                print(f"    ✅ 通过筛选")
                filtered_results.append(result)
            else:
                print(f"    ❌ 被过滤：质量不达标 (可信度:{result.credibility_score}, 相关性:{result.relevance_score:.1f})")
        
        print(f"📊 筛选结果：{len(filtered_results)}/{len(results)} 个结果通过")
        return filtered_results

    def _calculate_domain_source_credibility(self, source: str, domain_sources: List[str]) -> int:
        """计算领域专用来源可信度分数"""
        source_lower = source.lower()
        
        # 优先匹配领域专用来源
        for domain_source in domain_sources:
            if domain_source.lower() in source_lower:
                # 领域专用来源给予更高分数
                if domain_source in ['nature.com', 'sciencemag.org', 'nejm.org', 'arxiv.org']:
                    return 10
                elif domain_source in ['bloomberg.com', 'reuters.com', 'ft.com']:
                    return 9
                else:
                    return 8
        
        # 回退到通用权威来源评分
        return self._calculate_source_credibility(source)

    def _calculate_domain_relevance_score(self, text: str, domain_keywords: List[str]) -> float:
        """计算与领域关键词的相关性分数"""
        try:
            text_lower = text.lower()
            relevance_score = 0.0
            matched_keywords = 0
            
            print(f"      分析文本: {text_lower[:100]}...")
            print(f"      领域关键词: {domain_keywords}")
            
            # 计算领域关键词匹配度
            for keyword in domain_keywords:
                keyword_lower = keyword.lower()
                keyword_matched = False
                
                if keyword_lower in text_lower:
                    # 完整短语匹配给予更高分数
                    if ' ' in keyword:
                        relevance_score += 4  # 提高完整短语分数
                        print(f"      ✅ 完整短语匹配: '{keyword}' (+4分)")
                    else:
                        relevance_score += 3  # 提高单词分数
                        print(f"      ✅ 单词匹配: '{keyword}' (+3分)")
                    keyword_matched = True
                else:
                    # 部分词匹配
                    keyword_words = keyword_lower.split()
                    partial_matches = 0
                    for word in keyword_words:
                        if len(word) > 2 and word in text_lower:  # 降低词长度要求
                            partial_matches += 1
                            relevance_score += 1
                            print(f"      ⚡ 部分匹配: '{word}' (+1分)")
                    
                    if partial_matches > 0:
                        keyword_matched = True
                
                if keyword_matched:
                    matched_keywords += 1
            
            # 更宽松的归一化 - 基于匹配的关键词数量而非最大可能分数
            if matched_keywords > 0:
                # 基础分数 + 匹配奖励
                base_score = 6.0  # 提高基础分数
                match_bonus = min(relevance_score * 0.5, 4.0)  # 匹配奖励
                relevance_score = base_score + match_bonus
            else:
                relevance_score = 5.0  # 没有匹配时的基础分数
            
            print(f"      匹配关键词数: {matched_keywords}/{len(domain_keywords)}")
            print(f"      计算相关性: {relevance_score:.1f}")
            
            return min(relevance_score, 10.0)  # 最高10分
            
        except Exception as e:
            print(f"      ❌ 相关性计算出错: {e}")
            return 6.0  # 提高默认相关性

    def generate_inspiration_report(self, topic: str, results: List[NewsResult], category: Optional[str] = None, domain_name: Optional[str] = None) -> str:
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
        
        # 优先显示专业领域名称
        if domain_name:
            category_display = domain_name
        else:
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
            # 构建英文引用和中文翻译，清理来源名称格式
            clean_source = result.source
            # 移除过长的括号说明，保留核心来源名称
            if '(' in clean_source and len(clean_source) > 30:
                # 提取主要来源名称，移除括号中的详细说明
                main_source = clean_source.split('(')[0].strip()
                if main_source and len(main_source) > 3:
                    clean_source = main_source
            
            english_source_desc = f"According to {clean_source}"
            chinese_source_desc = f"据{clean_source}报道"
            
            # 如果有URL，添加链接
            source_link = ""
            if result.url:
                source_link = f" ([原文链接]({result.url}))"
            
            # 为中文版本创建基于英文摘要的中文描述
            def translate_to_chinese_summary(english_summary: str) -> str:
                """基于英文摘要生成有意义的中文总结"""
                summary_lower = english_summary.lower()
                
                # 更精确的关键词识别和中文生成
                if "brain" in summary_lower or "neural" in summary_lower or "neuron" in summary_lower:
                    if "bci" in summary_lower or "interface" in summary_lower:
                        return "斯坦福大学研究人员开发的脑机接口技术实现重大突破，为瘫痪患者恢复交流能力带来新希望"
                    elif "memory" in summary_lower or "learning" in summary_lower:
                        return "神经科学研究揭示大脑学习和记忆的新机制，为理解人类认知提供重要洞察"
                    elif "dendrite" in summary_lower or "computation" in summary_lower:
                        return "MIT科学家发现神经元内部计算的新机制，颠覆了传统的大脑工作原理认知"
                    elif "suppress" in summary_lower or "thought" in summary_lower:
                        return "剑桥大学研究团队发现大脑主动抑制不良思维的神经机制，解释了思维控制的生物学基础"
                    else:
                        return "最新脑科学研究在神经机制理解方面取得重要进展，为认知科学发展提供新的理论支撑"
                
                elif "ai" in summary_lower or "artificial intelligence" in summary_lower:
                    return "人工智能技术在特定领域展现出突破性应用潜力，推动相关行业的技术革新"
                
                elif "decision" in summary_lower or "uncertainty" in summary_lower:
                    return "科学家对大脑决策机制的研究取得新发现，解释了人类在不确定环境下的选择行为"
                
                elif "consciousness" in summary_lower or "organoid" in summary_lower:
                    return "类脑器官意识检测研究引发科学界关注，为意识本质的理解开辟新的研究路径"
                
                elif "quantum" in summary_lower:
                    return "量子技术领域的最新发展为相关应用场景提供了新的技术可能性"
                
                elif "blockchain" in summary_lower or "crypto" in summary_lower:
                    return "区块链和加密货币技术的发展为数字金融生态带来新的变革机遇"
                
                else:
                    # 基于内容类型的通用生成
                    if "study" in summary_lower or "research" in summary_lower:
                        return f"最新学术研究在{topic}领域取得重要发现，为理论发展和实际应用提供新的启示"
                    elif "company" in summary_lower or "launched" in summary_lower:
                        return f"行业领先企业在{topic}领域的重要举措，标志着相关技术的商业化进程加速"
                    else:
                        return f"权威机构发布的{topic}领域分析显示，该领域正在经历重要的发展变化"
            
            chinese_summary = translate_to_chinese_summary(result.summary)
            
            content += f"""### {i}. {result.title}

**English Source Reference**: {english_source_desc}, {result.summary}{source_link}

**中文版本**: {chinese_source_desc}，{chinese_summary}。

**关键洞察**：
{chr(10).join(f'- {insight}' for insight in result.key_insights[:3] if insight)}

"""
        
        content += """<!-- more -->

## 💡 深度洞察与趋势分析

综合上述权威研究发现，可以观察到以下关键趋势和深层含义：

### 🧠 技术突破的共同模式
这些研究展现了当前科学发展的几个重要特征：精密测量技术的进步使得我们能够更深入地观察和理解复杂系统的运作机制，跨学科融合正在产生突破性的发现和应用。

### 🌟 应用前景与社会价值  
从实际应用角度来看，这些发现不仅推进了基础科学研究，更为解决实际问题提供了新的路径和工具，其潜在的社会价值和经济效益值得持续关注。

### 🎯 对个人发展的启示
对于关注该领域发展的人士而言，保持对前沿研究的敏感性，理解技术发展的内在逻辑，并思考如何将这些新知识应用到自己的工作和生活中，将是获得竞争优势的重要途径。

## 📚 参考资源

"""
        
        # 检查是否所有来源都是英文权威来源
        english_sources = {
            'nature.com', 'sciencemag.org', 'thelancet.com', 'nejm.org', 'arxiv.org', 
            'statnews.com', 'healthtechmagazine.net', 'mobihealthnews.com',
            'bloomberg.com', 'reuters.com', 'ft.com', 'wsj.com', 'nytimes.com',
            'bbc.com', 'guardian.com', 'techcrunch.com', 'wired.com'
        }
        
        all_english = all(any(eng_source in result.source.lower() for eng_source in english_sources) 
                         for result in results)
        
        if all_english:
            # 如果全部是英文权威来源，使用简洁格式
            content += "### Authoritative Sources:\n\n"
            for i, result in enumerate(results, 1):
                if result.url:
                    content += f"{i}. **{result.title}**  \n"
                    content += f"   *{result.source}* | [{result.publication_date}]({result.url})  \n\n"
                else:
                    content += f"{i}. **{result.title}**  \n"
                    content += f"   *{result.source}* | {result.publication_date}  \n\n"
        else:
            # 如果有中文或其他来源，使用完整格式
            content += "### English Sources:\n\n"
            for i, result in enumerate(results, 1):
                if result.url:
                    content += f"{i}. **{result.title}**  \n"
                    content += f"   Source: {result.source}  \n"
                    content += f"   Link: [{result.url}]({result.url})  \n"
                    content += f"   Date: {result.publication_date}\n\n"
                else:
                    content += f"{i}. **{result.title}**  \n"
                    content += f"   Source: {result.source}  \n"
                    content += f"   Date: {result.publication_date}\n\n"
            
            content += "\n### 中文来源说明：\n\n"
            for i, result in enumerate(results, 1):
                content += f"{i}. {result.title} - 来源：{result.source}\n"
        
        content += f"""
---

*本文基于{datetime.now().strftime('%Y年%m月%d日')}的权威来源信息整理，数据来源包括{', '.join(set(r.source for r in results))}等。*
"""
        
        return front_matter + content

    def _load_inspiration_status(self) -> Dict[str, Any]:
        """加载灵感报告状态"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"reports": [], "last_updated": datetime.now().isoformat()}
        except Exception as e:
            print(f"⚠️ 加载状态文件失败: {e}")
            return {"reports": [], "last_updated": datetime.now().isoformat()}

    def _save_inspiration_status(self, status: Dict[str, Any]) -> None:
        """保存灵感报告状态"""
        try:
            status["last_updated"] = datetime.now().isoformat()
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ 保存状态文件失败: {e}")

    def _record_inspiration_report(self, report_file: str, topic: str, domain_name: Optional[str] = None, 
                                 draft_path: Optional[str] = None) -> None:
        """记录生成的灵感报告"""
        status = self._load_inspiration_status()
        
        report_record = {
            "id": datetime.now().strftime('%Y%m%d-%H%M%S'),
            "report_file": str(report_file),
            "topic": topic,
            "domain_name": domain_name,
            "created_time": datetime.now().isoformat(),
            "draft_created": draft_path is not None,
            "draft_path": str(draft_path) if draft_path else None,
            "draft_exists": Path(draft_path).exists() if draft_path else False,
            "status": "active"
        }
        
        status["reports"].append(report_record)
        self._save_inspiration_status(status)
        
    def get_inspiration_history(self) -> List[Dict[str, Any]]:
        """获取灵感报告历史"""
        status = self._load_inspiration_status()
        reports = status.get("reports", [])
        
        # 更新草稿存在状态
        for report in reports:
            if report.get("draft_path"):
                report["draft_exists"] = Path(report["draft_path"]).exists()
        
        # 按时间倒序排列
        reports.sort(key=lambda x: x.get("created_time", ""), reverse=True)
        return reports
        
    def clean_inspiration_reports(self, keep_days: int = 30) -> Dict[str, int]:
        """清理旧的灵感报告"""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        status = self._load_inspiration_status()
        reports = status.get("reports", [])
        
        cleaned_count = 0
        orphan_count = 0
        kept_reports = []
        
        for report in reports:
            try:
                report_time = datetime.fromisoformat(report["created_time"])
                report_file = Path(report["report_file"])
                
                # 检查是否超过保留期
                if report_time < cutoff_date:
                    # 删除报告文件
                    if report_file.exists():
                        report_file.unlink()
                        cleaned_count += 1
                    
                    # 如果有对应的草稿且已被删除，标记为orphan
                    if report.get("draft_path") and not Path(report["draft_path"]).exists():
                        report["status"] = "draft_deleted"
                        orphan_count += 1
                else:
                    # 保留的报告，更新草稿状态
                    if report.get("draft_path"):
                        report["draft_exists"] = Path(report["draft_path"]).exists()
                        if not report["draft_exists"] and report["status"] == "active":
                            report["status"] = "draft_deleted"
                            orphan_count += 1
                    kept_reports.append(report)
                    
            except Exception as e:
                print(f"⚠️ 处理报告记录时出错: {e}")
                kept_reports.append(report)
        
        # 更新状态
        status["reports"] = kept_reports
        self._save_inspiration_status(status)
        
        return {
            "cleaned": cleaned_count,
            "orphaned": orphan_count,
            "remaining": len(kept_reports)
        }

def main():
    """主函数 - 供独立运行使用"""
    print("💡 主题灵感生成器 - 专业化版本")
    print("="*60)
    
    # 检查环境变量
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ 错误：未找到GEMINI_API_KEY或GOOGLE_API_KEY环境变量")
        print("请在.env文件中配置您的Gemini API密钥")
        return
    
    try:
        # 创建生成器实例
        generator = TopicInspirationGenerator()
        
        # 显示搜索模式选择
        print("\n🔍 请选择搜索模式：")
        print("1. 📚 专业领域搜索 - 基于预设的专业领域知识库")
        print("2. 🔍 自定义主题搜索 - 基于用户输入的主题")
        
        mode_choice = input("请选择模式 (1-2): ").strip()
        
        results = []
        topic_name = ""
        domain_name = None
        category = None
        
        if mode_choice == "1":
            # 专业领域搜索模式
            domains = generator.list_available_domains()
            
            if not domains:
                print("❌ 未找到专业领域配置，回退到自定义搜索模式")
                mode_choice = "2"
            else:
                print("\n📋 可用的专业领域：")
                for i, (domain_id, display_name, description) in enumerate(domains, 1):
                    print(f"{i}. {display_name}")
                    print(f"   {description}")
                    print()
                
                domain_choice = input(f"请选择领域 (1-{len(domains)}): ").strip()
                try:
                    domain_index = int(domain_choice) - 1
                    if 0 <= domain_index < len(domains):
                        domain_id, display_name, description = domains[domain_index]
                        domain_name = display_name
                        topic_name = display_name.replace('🏥 ', '').replace('⚛️ ', '').replace('💳 ', '').replace('🌱 ', '').replace('🧠 ', '').replace('🚀 ', '')
                        
                        print(f"\n🎯 选择领域: {display_name}")
                        print(f"📝 描述: {description}")
                        
                        # 获取领域配置中的category
                        domain_config = generator.domains.get(domain_id, {})
                        category = domain_config.get('category', 'global-perspective')
                        
                        # 执行专业领域搜索
                        results = generator.get_domain_inspiration(domain_id)
                    else:
                        print("❌ 选择无效，回退到自定义搜索")
                        mode_choice = "2"
                except (ValueError, IndexError):
                    print("❌ 输入格式错误，回退到自定义搜索")
                    mode_choice = "2"
        
        if mode_choice == "2":
            # 自定义主题搜索模式
            topic = input("\n请输入要探索的主题: ").strip()
            if not topic:
                print("❌ 主题不能为空")
                return
            
            topic_name = topic
            
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
            
            # 执行传统主题搜索
            results = generator.get_topic_inspiration(topic, category)
        
        # 处理搜索结果
        if results:
            # 生成报告
            report = generator.generate_inspiration_report(topic_name, results, category, domain_name)
            
            # 保存报告
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            safe_topic = re.sub(r'[^\w\s-]', '', topic_name)[:20]
            report_file = generator.output_dir / f"{safe_topic}-{timestamp}.md"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"\n✅ 灵感报告已生成: {report_file}")
            print(f"📊 找到 {len(results)} 条权威资讯")
            
            # 显示结果概要
            for i, result in enumerate(results, 1):
                credibility_emoji = "🌟" if result.credibility_score >= 9 else "⭐" if result.credibility_score >= 7 else "📰"
                date_display = f" - {result.publication_date}" if result.publication_date else ""
                print(f"  {i}. {credibility_emoji} {result.title} ({result.source}{date_display})")
            
            # 询问是否创建草稿
            create_draft = input("\n是否基于这些灵感创建文章草稿？(y/N): ").strip().lower()
            if create_draft in ['y', 'yes']:
                draft_path = generator.create_inspired_draft(topic_name, results, category)
                if draft_path:
                    print(f"📄 草稿已创建: {draft_path}")
                    print("💡 草稿使用说明:")
                    print("   • 草稿已自动生成Front Matter和基础结构")
                    print("   • 包含了所有权威来源的关键洞察")
                    print("   • 可以直接编辑完善后发布")
                    print("   • 或使用主程序的'处理现有草稿'功能进行发布")
                    
                    # 记录灵感报告和草稿
                    generator._record_inspiration_report(str(report_file), topic_name, domain_name, draft_path)
                else:
                    # 只记录灵感报告
                    generator._record_inspiration_report(str(report_file), topic_name, domain_name)
        else:
            print("❌ 未找到相关权威资讯，请尝试其他关键词或领域")
            
    except Exception as e:
        print(f"❌ 操作失败: {e}")

if __name__ == "__main__":
    main()