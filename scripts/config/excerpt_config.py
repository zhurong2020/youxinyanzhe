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
            'min': 80,
            'max': 120,
            'optimal': 100,
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
            'min': 60,
            'max': 80,
            'optimal': 70,
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
   - 长度：80-120字符（最佳100字符）
   - 内容：包含核心关键词，说明文章价值
   - 格式：纯文本，完整句子，无Markdown
   - 特点：清晰传达文章主题和解决的问题

2. <!-- more -->前内容（主页显示用）：
   - 长度：60-80字符（最佳70字符）
   - 内容：引人入胜的开头，制造悬念
   - 位置：第一段结束后
   - 特点：2-3行文字，可以是问题或故事开头

3. 两者关系：
   - 功能不同：SEO摘要更正式，主页摘要更吸引人
   - 长度不同：SEO摘要较长（传达完整信息），主页摘要较短（节省空间）
   - Front Matter excerpt偏重SEO关键词
   - <!-- more -->前内容偏重吸引点击

示例：
---
excerpt: "期权解套完全指南：用Wheel策略和智能参数调整，把23.9%的浮亏变成稳定收入，6-10个月实现解套"  # SEO用，100字符
---

当股票被深套23.9%时，有一种方法能在6-10个月内解套并赚取稳定收入，你相信吗？  # 主页显示，70字符

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