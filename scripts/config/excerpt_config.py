"""
摘要处理统一配置
==============
本配置文件定义了有心工坊系统中两种摘要的处理规则和用途

作者：有心工坊技术团队
更新时间：2025-09-20
"""

# =============================
# 摘要类型定义和用途
# =============================

EXCERPT_TYPES = {
    'front_matter_excerpt': {
        '用途': 'SEO和社交媒体分享',
        '显示位置': ['meta标签', 'Open Graph', 'Twitter Card', 'RSS Feed'],
        '格式': '纯文本',
        '字数要求': {
            'min': 50,
            'max': 160,
            'optimal': 80,
            'unit': '字符'
        },
        '访问方式': 'page.excerpt 或 post.meta.excerpt',
        '必需': True,
        '自动生成': True
    },

    'content_excerpt': {
        '用途': '主页和归档页显示',
        '显示位置': ['主页文章列表', '分类页', '标签页', '归档页'],
        '格式': 'Markdown（渲染后显示）',
        '字数要求': {
            'min': 80,
            'max': 150,
            'optimal': 120,
            'unit': '字符（纯文本计算）'
        },
        '标记': '<!-- more -->',
        '访问方式': 'post.excerpt（Jekyll自动提取）',
        '必需': True,
        '自动生成': True
    }
}

# =============================
# 格式化规则
# =============================

FORMAT_RULES = {
    'more_tag_insertion': {
        '描述': '自动插入<!-- more -->标记的规则',
        '优先查找位置': [
            '第一段结束后（80-150字符）',
            '第二段结束后（如果第一段太短）',
            '150字符处强制截断'
        ],
        '避免位置': [
            '标题行',
            '引用块内',
            '代码块内',
            '列表项中间'
        ]
    },

    'front_matter_excerpt': {
        '描述': 'Front Matter excerpt字段生成规则',
        '生成方法': [
            '优先使用用户提供的excerpt',
            '从文章第一段提取',
            '使用AI生成（Gemini）'
        ],
        '处理流程': [
            '移除Markdown格式',
            '移除特殊字符',
            '截断到合适长度',
            '添加省略号（如需要）'
        ]
    }
}

# =============================
# 验证规则
# =============================

VALIDATION_RULES = {
    'front_matter_excerpt': {
        'required': True,
        'min_length': 50,
        'max_length': 160,
        'warning_if_missing': '缺少SEO摘要，将影响搜索引擎收录',
        'auto_fix': True
    },

    'content_excerpt': {
        'required': True,
        'min_length': 80,
        'max_length': 150,
        'warning_if_missing': '缺少主页摘要，将影响文章列表显示',
        'auto_fix': True
    },

    'more_tag': {
        'required': True,
        'warning_if_missing': '缺少<!-- more -->标记，将显示全文',
        'auto_fix': True
    }
}

# =============================
# 显示模板配置
# =============================

TEMPLATE_CONFIG = {
    'home_page': {
        '使用字段': 'post.excerpt（<!-- more -->前内容）',
        '最大显示长度': 160,
        '处理流程': [
            'markdownify（转换Markdown）',
            'strip_html（移除HTML标签）',
            'truncate: 160（截断）'
        ]
    },

    'seo_meta': {
        '使用字段': 'page.excerpt（Front Matter字段）',
        '最大长度': 160,
        '用途': [
            '<meta name="description" content="{{ page.excerpt }}">',
            '<meta property="og:description" content="{{ page.excerpt }}">',
            '<meta name="twitter:description" content="{{ page.excerpt }}">'
        ]
    }
}

# =============================
# 最佳实践建议
# =============================

BEST_PRACTICES = """
1. Front Matter excerpt（SEO用）：
   - 长度：80-120字符最佳
   - 内容：包含关键词，吸引点击
   - 格式：纯文本，无Markdown

2. <!-- more -->前内容（主页显示用）：
   - 长度：100-150字符的完整段落
   - 内容：引人入胜的开头，可包含粗体等简单格式
   - 位置：第一段结束后

3. 两者关系：
   - 可以相同（简单处理）
   - 可以不同（各自优化）
   - Front Matter excerpt更简洁（SEO）
   - <!-- more -->前内容更生动（吸引阅读）

示例：
---
excerpt: "深入解析期权解套策略，从套牢到盈利的完整指南"  # SEO用，简洁包含关键词
---

当你的股票被深套23.9%时，大多数人会选择死扛或割肉。但如果我告诉你，
有一种方法可以在6-10个月内解套，甚至还能赚取稳定收入，你会相信吗？  # 主页显示，更生动

<!-- more -->
"""

def get_excerpt_requirements(excerpt_type: str) -> dict:
    """获取指定类型摘要的要求"""
    return EXCERPT_TYPES.get(excerpt_type, {})

def validate_excerpt_length(text: str, excerpt_type: str) -> tuple:
    """验证摘要长度是否符合要求

    Returns:
        (is_valid, message)
    """
    if excerpt_type not in EXCERPT_TYPES:
        return False, f"未知的摘要类型: {excerpt_type}"

    req = EXCERPT_TYPES[excerpt_type]['字数要求']
    length = len(text.strip())

    if length < req['min']:
        return False, f"{excerpt_type}过短（{length}字符），建议{req['optimal']}字符"
    elif length > req['max']:
        return False, f"{excerpt_type}过长（{length}字符），建议{req['optimal']}字符"
    else:
        return True, f"{excerpt_type}长度合适（{length}字符）"