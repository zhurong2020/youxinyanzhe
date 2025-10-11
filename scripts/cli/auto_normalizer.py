"""
自动规范化引擎
用于一键规范化和智能发布的统一规范化逻辑
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import re


class AutoNormalizer:
    """自动规范化引擎"""

    # 四大分类映射
    CATEGORIES_MAP = {
        'cognitive-upgrade': {
            'keywords': ['认知', '思维', '学习', '心理', '成长', '模型', '方法论', '效率', '提升'],
            'emoji': '🧠',
            'name_cn': '认知升级',
            'name_en': 'cognitive-upgrade'
        },
        'tech-empowerment': {
            'keywords': ['技术', '工具', '自动化', '编程', '代码', 'AI', '人工智能', '软件', '应用', '教程'],
            'emoji': '🛠️',
            'name_cn': '技术赋能',
            'name_en': 'tech-empowerment'
        },
        'global-perspective': {
            'keywords': ['全球', '国际', '文化', '趋势', '视野', '世界', '跨文化', '差异'],
            'emoji': '🌍',
            'name_cn': '全球视野',
            'name_en': 'global-perspective'
        },
        'investment-finance': {
            'keywords': ['投资', '理财', '金融', '股票', '基金', '量化', '财富', '资产', '收益', '策略', '美股', '定投'],
            'emoji': '💰',
            'name_cn': '投资理财',
            'name_en': 'investment-finance'
        }
    }

    def __init__(self, ai_client=None):
        """
        初始化自动规范化引擎

        Args:
            ai_client: AI客户端（用于生成摘要）
        """
        self.ai_client = ai_client

    def infer_category_from_content(self, title: str, tags: List[str], content: str = "") -> Optional[str]:
        """
        基于标题、标签和内容推断分类

        Args:
            title: 文章标题
            tags: 标签列表
            content: 文章内容（可选）

        Returns:
            推断的分类（英文key）或None
        """
        # 合并所有文本用于分析
        text_to_analyze = f"{title} {' '.join(tags)} {content[:500]}"
        text_lower = text_to_analyze.lower()

        # 计算每个分类的匹配分数
        scores = {}
        for category_key, category_info in self.CATEGORIES_MAP.items():
            score = 0
            for keyword in category_info['keywords']:
                # 标题匹配权重更高
                if keyword in title.lower():
                    score += 3
                # 标签匹配权重中等
                if any(keyword in tag.lower() for tag in tags):
                    score += 2
                # 内容匹配权重较低
                if keyword in text_lower:
                    score += 1
            scores[category_key] = score

        # 返回得分最高的分类
        if scores:
            best_category = max(scores.items(), key=lambda x: x[1])
            if best_category[1] > 0:  # 至少有一个关键词匹配
                return best_category[0]

        return None

    def optimize_excerpt_with_ai(self, content: str, target_length: int = 70) -> Optional[str]:
        """
        使用AI优化摘要

        Args:
            content: 文章内容
            target_length: 目标长度（字符）

        Returns:
            优化后的摘要或None
        """
        if not self.ai_client:
            return None

        try:
            # 提取文章开头部分用于AI分析
            # 移除Front Matter
            content_lines = content.split('\n')
            fm_count = 0
            content_start = 0
            for i, line in enumerate(content_lines):
                if line.strip() == '---':
                    fm_count += 1
                    if fm_count == 2:
                        content_start = i + 1
                        break

            main_content = '\n'.join(content_lines[content_start:content_start+50])  # 前50行

            prompt = f"""请为以下文章生成一个{target_length}字符左右的精炼摘要。

要求：
1. 准确概括文章核心内容
2. 长度严格控制在{target_length}字符左右（不超过{target_length + 10}字符）
3. 语言简洁有力，吸引读者
4. 不要使用"本文"、"这篇文章"等开头
5. 直接从内容核心开始

文章内容：
{main_content}

请直接输出摘要，不要其他说明："""

            # 调用AI生成摘要
            response = self.ai_client.generate_content(prompt)
            if response and hasattr(response, 'text'):
                summary = response.text.strip()
                # 确保长度合适
                if len(summary) > target_length + 15:
                    summary = summary[:target_length] + "..."
                return summary

        except Exception as e:
            print(f"   ⚠️ AI生成摘要失败: {e}")
            return None

        return None

    def truncate_excerpt(self, excerpt: str, max_length: int = 80) -> str:
        """
        截断摘要到指定长度

        Args:
            excerpt: 原始摘要
            max_length: 最大长度

        Returns:
            截断后的摘要
        """
        if len(excerpt) <= max_length:
            return excerpt

        # 在句子边界截断
        truncated = excerpt[:max_length]

        # 找到最后一个句子结束符
        last_period = max(
            truncated.rfind('。'),
            truncated.rfind('！'),
            truncated.rfind('？'),
            truncated.rfind('.'),
            truncated.rfind('!'),
            truncated.rfind('?')
        )

        if last_period > max_length * 0.7:  # 如果句子边界不太远
            return truncated[:last_period + 1]
        else:
            # 否则在最后一个逗号处截断
            last_comma = max(truncated.rfind('，'), truncated.rfind(','))
            if last_comma > max_length * 0.7:
                return truncated[:last_comma] + "..."
            else:
                return truncated + "..."

    def extract_front_matter(self, content: str) -> tuple[Dict[str, Any], str]:
        """
        提取Front Matter和正文内容

        Args:
            content: 文件内容

        Returns:
            (front_matter_dict, body_content)
        """
        import frontmatter

        try:
            post = frontmatter.loads(content)
            return dict(post.metadata), post.content
        except Exception as e:
            print(f"   ⚠️ 解析Front Matter失败: {e}")
            return {}, content

    def rebuild_content(self, front_matter: Dict[str, Any], body: str) -> str:
        """
        重建文件内容（Front Matter + 正文）

        Args:
            front_matter: Front Matter字典
            body: 正文内容

        Returns:
            完整文件内容
        """
        import yaml

        fm_str = yaml.dump(front_matter, allow_unicode=True, default_flow_style=False, sort_keys=False)
        return f"---\n{fm_str}---\n{body}"
