#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
去重分析工具 - 精确匹配Gridea和Jekyll(_posts)文章
"""

import os
import re
import yaml
from datetime import datetime
from pathlib import Path

class ArticleDeduplicator:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.gridea_dir = Path("/mnt/c/onedrive/wuxiami/OneDrive/Documents/Gridea/posts")
        self.jekyll_dir = self.project_root / "_posts"

        self.gridea_articles = []
        self.jekyll_articles = []

    def extract_front_matter(self, file_path, source='jekyll'):
        """提取front matter"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 匹配YAML front matter
            match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not match:
                return None

            front_matter = yaml.safe_load(match.group(1))

            # 提取关键信息
            article = {
                'title': front_matter.get('title', '无标题'),
                'file_path': str(file_path),
                'source': source
            }

            # 处理日期
            date_value = front_matter.get('date', front_matter.get('published', ''))
            if isinstance(date_value, datetime):
                article['date'] = date_value.strftime('%Y-%m-%d')
            else:
                article['date'] = str(date_value)[:10] if date_value else ''

            # 统计字数
            body = content[match.end():].strip()
            article['word_count'] = len(re.sub(r'\s+', '', body))

            # 提取标签和分类
            article['tags'] = front_matter.get('tags', [])
            article['category'] = front_matter.get('category', '')

            return article

        except Exception as e:
            print(f"⚠️ 读取文件失败 {file_path}: {e}")
            return None

    def scan_gridea_articles(self):
        """扫描Gridea文章"""
        print(f"📂 扫描Gridea目录: {self.gridea_dir}")

        for file_path in self.gridea_dir.glob("*.md"):
            if file_path.name == 'about.md':
                continue

            article = self.extract_front_matter(file_path, source='Gridea')
            if article:
                self.gridea_articles.append(article)

        print(f"✅ Gridea文章: {len(self.gridea_articles)} 篇")

    def scan_jekyll_articles(self):
        """扫描Jekyll(_posts)文章"""
        print(f"📂 扫描Jekyll目录: {self.jekyll_dir}")

        for file_path in self.jekyll_dir.glob("*.md"):
            article = self.extract_front_matter(file_path, source='Jekyll')
            if article:
                self.jekyll_articles.append(article)

        print(f"✅ Jekyll文章: {len(self.jekyll_articles)} 篇")

    def normalize_title(self, title):
        """标准化标题用于匹配"""
        # 去除空格、标点、emoji等，转小写
        normalized = re.sub(r'[^\w\u4e00-\u9fff]+', '', title.lower())
        return normalized

    def extract_title_core(self, title):
        """提取标题核心内容用于模糊匹配"""
        # 去除常见前缀和序号
        title = re.sub(r'^(投资马斯克帝国：|马斯克帝国解密[①②③④⑤➀➁➂➃➄]?：?)', '', title)
        # 去除副标题（冒号或问号之后的内容）
        title = re.sub(r'[：？].+$', '', title)
        # 统一用词
        title = re.sub(r'为什么', '为何', title)
        title = re.sub(r'量化工具', 'moomoo量化工具', title, flags=re.IGNORECASE)
        # 标准化
        core = re.sub(r'[^\w\u4e00-\u9fff]+', '', title.lower())
        return core

    def similarity_score(self, title1, title2):
        """计算两个标题的相似度（0-1）"""
        # 方法1: 精确匹配
        norm1 = self.normalize_title(title1)
        norm2 = self.normalize_title(title2)
        if norm1 == norm2:
            return 1.0

        # 方法2: 核心内容匹配
        core1 = self.extract_title_core(title1)
        core2 = self.extract_title_core(title2)

        if core1 == core2:
            return 0.95

        # 方法3: 包含关系
        if core1 and core2:
            if core1 in core2 or core2 in core1:
                shorter = min(len(core1), len(core2))
                longer = max(len(core1), len(core2))
                ratio = shorter / longer
                if ratio >= 0.85:  # 85%以上重叠视为同一篇
                    return 0.9 * ratio

        # 方法4: 字符重叠率
        set1 = set(norm1)
        set2 = set(norm2)
        if set1 and set2:
            intersection = len(set1 & set2)
            union = len(set1 | set2)
            overlap = intersection / union
            if overlap >= 0.7:
                return overlap

        return 0.0

    def find_duplicates(self):
        """查找重复文章（使用模糊匹配）"""
        print(f"\n🔍 开始去重匹配（智能模糊算法）...")

        duplicates = []
        unique_gridea = []
        matched_jekyll = set()

        for gridea_article in self.gridea_articles:
            best_match = None
            best_score = 0.0

            for jekyll_article in self.jekyll_articles:
                if jekyll_article['title'] in matched_jekyll:
                    continue

                score = self.similarity_score(
                    gridea_article['title'],
                    jekyll_article['title']
                )

                if score > best_score:
                    best_score = score
                    best_match = jekyll_article

            # 阈值设为0.85（85%相似度视为重复）
            if best_score >= 0.85:
                duplicates.append({
                    'gridea': gridea_article,
                    'jekyll': best_match,
                    'similarity': best_score
                })
                matched_jekyll.add(best_match['title'])
            else:
                unique_gridea.append(gridea_article)

        return duplicates, unique_gridea

    def categorize_article(self, article):
        """根据标题和标签分类文章"""
        title = article['title'].lower()
        tags = [t.lower() for t in article.get('tags', [])]
        category = article.get('category', '').lower()

        # 投资理财
        if any(k in title or k in ' '.join(tags) or k in category
               for k in ['投资', '美股', '定投', 'tqqq', 'qqq', '期权', '股票', '基金', 'qdii', '理财', 'dca']):
            return '💰 投资理财'

        # 特斯拉专题
        if any(k in title or k in ' '.join(tags)
               for k in ['特斯拉', 'tesla', 'fsd', 'robotaxi', 'optimus']):
            return '🚗 特斯拉研究'

        # 技术赋能
        if any(k in title or k in ' '.join(tags) or k in category
               for k in ['技术', 'vps', 'docker', '部署', '服务器', 'linux', 'python', '代码', '开发', 'selfhosted']):
            return '🛠️ 技术赋能'

        # 认知升级
        if any(k in title or k in ' '.join(tags) or k in category
               for k in ['认知', '思维', '心理', '学习', '成长', '自我对话', '潜意识']):
            return '🧠 认知升级'

        # 全球视野
        if any(k in title or k in ' '.join(tags) or k in category
               for k in ['国际', '全球', '世界', '美国', '政治', '经济', 'youtube', '新闻']):
            return '🌍 全球视野'

        return '📝 其他'

    def generate_report(self, duplicates, unique_gridea):
        """生成去重报告"""
        output_file = self.project_root / "_drafts/todos/DEDUPLICATED-ARTICLES-REGISTRY.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 📊 文章去重分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # 统计数据
            f.write(f"## 📈 统计概览\n\n")
            f.write(f"- **Gridea总数**: {len(self.gridea_articles)} 篇\n")
            f.write(f"- **Jekyll总数**: {len(self.jekyll_articles)} 篇\n")
            f.write(f"- **重复文章**: {len(duplicates)} 篇\n")
            f.write(f"- **Gridea独有**: {len(unique_gridea)} 篇\n")
            f.write(f"- **去重率**: {len(duplicates)/len(self.gridea_articles)*100:.1f}%\n\n")

            # 重复文章列表
            f.write(f"## ✅ 已在Jekyll发布的文章 ({len(duplicates)} 篇)\n\n")

            # 按分类整理
            categorized_dups = {}
            for dup in duplicates:
                cat = self.categorize_article(dup['gridea'])
                if cat not in categorized_dups:
                    categorized_dups[cat] = []
                categorized_dups[cat].append(dup)

            for cat in sorted(categorized_dups.keys()):
                items = categorized_dups[cat]
                f.write(f"### {cat} ({len(items)}篇)\n\n")
                for dup in items:
                    gridea = dup['gridea']
                    jekyll = dup['jekyll']
                    similarity = dup.get('similarity', 1.0)
                    f.write(f"- **Gridea标题**: {gridea['title']}\n")
                    f.write(f"  **Jekyll标题**: {jekyll['title']}\n")
                    f.write(f"  **相似度**: {similarity*100:.1f}%\n")
                    f.write(f"  - Gridea: {gridea['date']} ({gridea['word_count']:,}字)\n")
                    f.write(f"  - Jekyll: `{Path(jekyll['file_path']).name}` ({jekyll['date']})\n\n")

            # Gridea独有文章
            f.write(f"\n## ❌ 尚未迁移的Gridea文章 ({len(unique_gridea)} 篇)\n\n")

            # 按分类整理
            categorized_unique = {}
            for article in unique_gridea:
                cat = self.categorize_article(article)
                if cat not in categorized_unique:
                    categorized_unique[cat] = []
                categorized_unique[cat].append(article)

            for cat in sorted(categorized_unique.keys()):
                items = sorted(categorized_unique[cat], key=lambda x: x['word_count'], reverse=True)

                # 计算推荐迁移数量
                recommend_count = sum(1 for a in items if a['word_count'] >= 3000 and a['date'] >= '2024-01-01')

                f.write(f"### {cat} ({len(items)}篇)")
                if recommend_count > 0:
                    f.write(f" - 🔥 {recommend_count}篇推荐迁移")
                f.write(f"\n\n")

                for article in items:
                    # 判断迁移优先级
                    if article['word_count'] >= 3000 and article['date'] >= '2024-01-01':
                        priority = '🔥'
                    elif article['word_count'] >= 2000 and article['date'] >= '2023-01-01':
                        priority = '📝'
                    else:
                        priority = '📦'

                    f.write(f"{priority} **{article['title']}** ({article['word_count']:,}字, {article['date']})\n")
                    if article['tags']:
                        f.write(f"   - 标签: {', '.join(article['tags'][:5])}\n")
                    f.write(f"\n")

            # 迁移建议
            f.write(f"\n## 💡 迁移建议\n\n")
            f.write(f"### 优先级说明\n\n")
            f.write(f"- 🔥 **推荐迁移**: 3,000字以上，2024年后创作，内容价值高\n")
            f.write(f"- 📝 **可考虑**: 2,000字以上，2023年后创作\n")
            f.write(f"- 📦 **可归档**: 字数较少或时效性较弱\n\n")

            # 统计推荐迁移数量
            high_priority = [a for a in unique_gridea if a['word_count'] >= 3000 and a['date'] >= '2024-01-01']
            f.write(f"### 推荐立即迁移 ({len(high_priority)} 篇)\n\n")
            for article in sorted(high_priority, key=lambda x: x['word_count'], reverse=True):
                cat = self.categorize_article(article)
                f.write(f"- {cat} **{article['title']}** ({article['word_count']:,}字)\n")

        print(f"\n✅ 报告已生成: {output_file}")
        return output_file

    def run(self):
        """执行去重分析"""
        print("=" * 60)
        print("🔄 文章去重分析工具")
        print("=" * 60)

        self.scan_gridea_articles()
        self.scan_jekyll_articles()

        duplicates, unique_gridea = self.find_duplicates()

        print(f"\n📊 去重结果:")
        print(f"  - 重复文章: {len(duplicates)} 篇")
        print(f"  - Gridea独有: {len(unique_gridea)} 篇")

        report_file = self.generate_report(duplicates, unique_gridea)

        return report_file

if __name__ == "__main__":
    deduplicator = ArticleDeduplicator()
    deduplicator.run()
