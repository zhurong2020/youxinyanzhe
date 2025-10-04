#!/usr/bin/env python3
"""
综合文章分析工具

功能：
1. 读取Gridea本地文章（81篇）
2. 读取Jekyll _posts文章（30篇）
3. 对比去重，识别迁移状态
4. 生成完整的文章登记表

使用：
python scripts/tools/content/analyze_all_articles.py
"""

import re
import yaml
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class ArticleAnalyzer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.gridea_dir = Path("/mnt/c/onedrive/wuxiami/OneDrive/Documents/Gridea/posts")
        self.jekyll_posts_dir = self.project_root / "_posts"

        self.gridea_articles = []
        self.jekyll_articles = []
        self.title_map = {}  # 标题映射，用于去重

    def extract_gridea_front_matter(self, file_path):
        """提取Gridea文章的Front Matter"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Gridea使用 ---...--- 格式
            match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not match:
                return None, content

            try:
                front_matter = yaml.safe_load(match.group(1))
                body = content[match.end():].strip()
                return front_matter, body
            except:
                return None, content
        except Exception as e:
            print(f"⚠️ 读取失败 {file_path.name}: {e}")
            return None, ""

    def scan_gridea_articles(self):
        """扫描Gridea文章"""
        print("📚 扫描Gridea文章目录...")

        if not self.gridea_dir.exists():
            print(f"❌ Gridea目录不存在: {self.gridea_dir}")
            return

        for md_file in self.gridea_dir.glob("*.md"):
            if md_file.name == "about.md":
                continue

            front_matter, body = self.extract_gridea_front_matter(md_file)
            if not front_matter:
                continue

            title = front_matter.get('title', 'No Title')
            date = front_matter.get('date', front_matter.get('published', 'Unknown'))
            tags = front_matter.get('tags', [])

            # 统一日期格式
            if isinstance(date, datetime):
                date_str = date.strftime('%Y-%m-%d')
            else:
                date_str = str(date)[:10] if len(str(date)) >= 10 else str(date)

            article_info = {
                'source': 'gridea',
                'filename': md_file.name,
                'title': title,
                'date': date_str,
                'tags': tags if isinstance(tags, list) else [],
                'word_count': len(body),
                'file_path': str(md_file)
            }

            self.gridea_articles.append(article_info)
            self.title_map[title.strip().lower()] = article_info

        print(f"✅ Gridea文章: {len(self.gridea_articles)} 篇")

    def scan_jekyll_articles(self):
        """扫描Jekyll文章"""
        print("\n📚 扫描Jekyll _posts目录...")

        for md_file in self.jekyll_posts_dir.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
                if not match:
                    continue

                front_matter = yaml.safe_load(match.group(1))
                body = content[match.end():].strip()

                filename = md_file.stem
                date_match = re.match(r'^(\d{4}-\d{2}-\d{2})-(.+)$', filename)

                title = front_matter.get('title', 'No Title')
                date = front_matter.get('date', date_match.group(1) if date_match else 'Unknown')
                categories = front_matter.get('categories', [])

                # 统一日期格式
                if isinstance(date, datetime):
                    date_str = date.strftime('%Y-%m-%d')
                else:
                    date_str = str(date)[:10] if len(str(date)) >= 10 else str(date)

                article_info = {
                    'source': 'jekyll',
                    'filename': md_file.name,
                    'slug': date_match.group(2) if date_match else filename,
                    'title': title,
                    'date': date_str,
                    'categories': categories if isinstance(categories, list) else [],
                    'word_count': len(body),
                    'file_path': str(md_file)
                }

                self.jekyll_articles.append(article_info)

            except Exception as e:
                print(f"⚠️ 读取失败 {md_file.name}: {e}")

        print(f"✅ Jekyll文章: {len(self.jekyll_articles)} 篇")

    def compare_articles(self):
        """对比文章，识别迁移状态"""
        print("\n🔍 对比Gridea和Jekyll文章...")

        # 基于标题匹配
        migrated = []
        not_migrated = []

        jekyll_titles = {a['title'].strip().lower() for a in self.jekyll_articles}

        for gridea_article in self.gridea_articles:
            title_lower = gridea_article['title'].strip().lower()
            if title_lower in jekyll_titles:
                gridea_article['migration_status'] = '✅ 已迁移'
                migrated.append(gridea_article)
            else:
                gridea_article['migration_status'] = '❌ 未迁移'
                not_migrated.append(gridea_article)

        return migrated, not_migrated

    def categorize_articles(self, articles):
        """按主题分类文章"""
        categories = defaultdict(list)

        for article in articles:
            title = article['title']

            # 基于标题关键词分类
            if any(k in title for k in ['投资', '美股', '定投', 'TQQQ', 'DCA', '期权', '量化', 'ETF', 'Moomoo', '网格', 'QDII', '股票', '基金']):
                categories['💰 投资理财'].append(article)
            elif any(k in title for k in ['特斯拉', 'Tesla', '马斯克', 'Optimus', 'Robotaxi', 'FSD']):
                categories['🌍 特斯拉研究'].append(article)
            elif any(k in title for k in ['VPS', 'GitHub', 'Cloudflare', '自托管', 'Gridea', 'Jekyll', 'ChatGPT', 'AI', 'Lobe Chat', 'NextChat', 'Pandora', 'LM Studio', 'Kimi']):
                categories['🛠️ 技术赋能'].append(article)
            elif any(k in title for k in ['信息', '学习', '读书', '思维', '意志力', '自我对话', '笔记', '效率']):
                categories['🧠 认知升级'].append(article)
            elif any(k in title for k in ['英语', '巴伦', '民主党', '共和党', 'Prove Me Wrong']):
                categories['📺 英语学习与观察'].append(article)
            else:
                categories['📝 其他'].append(article)

        return dict(categories)

    def generate_report(self):
        """生成综合报告"""
        migrated, not_migrated = self.compare_articles()

        print("\n" + "="*70)
        print("📊 综合文章分析报告")
        print("="*70)

        print(f"\nGridea文章总数: {len(self.gridea_articles)} 篇")
        print(f"Jekyll文章总数: {len(self.jekyll_articles)} 篇")
        print(f"\n已迁移到Jekyll: {len(migrated)} 篇 ({len(migrated)/len(self.gridea_articles)*100:.1f}%)")
        print(f"尚未迁移: {len(not_migrated)} 篇 ({len(not_migrated)/len(self.gridea_articles)*100:.1f}%)")

        # 未迁移文章分类
        if not_migrated:
            print("\n⚠️ 未迁移文章按主题分类：")
            categorized = self.categorize_articles(not_migrated)

            for category, articles in sorted(categorized.items()):
                print(f"\n{category} ({len(articles)}篇):")
                for article in sorted(articles, key=lambda x: x.get('date', ''), reverse=True)[:5]:
                    print(f"  - {article['date']} | {article['title']}")
                if len(articles) > 5:
                    print(f"  ... 还有 {len(articles) - 5} 篇")

        print("\n" + "="*70)

        return migrated, not_migrated

    def generate_markdown_registry(self):
        """生成完整的Markdown登记表"""
        migrated, not_migrated = self.compare_articles()

        output = []
        output.append("# 📚 完整文章登记表（Gridea + Jekyll）\n")
        output.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"**Gridea文章**: {len(self.gridea_articles)} 篇")
        output.append(f"**Jekyll文章**: {len(self.jekyll_articles)} 篇")
        output.append(f"**已迁移**: {len(migrated)} 篇")
        output.append(f"**未迁移**: {len(not_migrated)} 篇\n")

        output.append("---\n")

        # 已迁移文章
        output.append("## ✅ 已迁移到Jekyll的文章 ({} 篇)\n".format(len(migrated)))
        categorized_migrated = self.categorize_articles(migrated)

        for category, articles in sorted(categorized_migrated.items()):
            output.append(f"### {category} ({len(articles)}篇)\n")
            output.append("| 发布日期 | 文章标题 | Gridea文件 | 字数 |")
            output.append("|---------|---------|-----------|------|")

            for article in sorted(articles, key=lambda x: x.get('date', ''), reverse=True):
                date = article.get('date', 'Unknown')
                title = article['title']
                filename = f"`{article['filename']}`"
                word_count = f"{article['word_count']:,}"

                output.append(f"| {date} | {title} | {filename} | {word_count} |")

            output.append("")

        # 未迁移文章
        if not_migrated:
            output.append("---\n")
            output.append("## ❌ 尚未迁移的Gridea文章 ({} 篇)\n".format(len(not_migrated)))
            categorized_not_migrated = self.categorize_articles(not_migrated)

            for category, articles in sorted(categorized_not_migrated.items()):
                output.append(f"### {category} ({len(articles)}篇)\n")
                output.append("| 发布日期 | 文章标题 | 文件名 | 字数 | 建议 |")
                output.append("|---------|---------|--------|------|------|")

                for article in sorted(articles, key=lambda x: x.get('date', ''), reverse=True):
                    date = article.get('date', 'Unknown')
                    title = article['title']
                    filename = f"`{article['filename']}`"
                    word_count = f"{article['word_count']:,}"

                    # 基于字数和日期给出建议
                    if article['word_count'] > 3000 and date.startswith('2024') or date.startswith('2025'):
                        suggestion = "🔥 推荐迁移"
                    elif article['word_count'] > 1000:
                        suggestion = "📝 可考虑"
                    else:
                        suggestion = "📦 可归档"

                    output.append(f"| {date} | {title} | {filename} | {word_count} | {suggestion} |")

                output.append("")

        return "\n".join(output)

    def run(self):
        """执行完整分析"""
        self.scan_gridea_articles()
        self.scan_jekyll_articles()
        self.generate_report()

        # 生成Markdown登记表
        markdown = self.generate_markdown_registry()

        output_file = self.project_root / "_drafts" / "todos" / "COMPLETE-ARTICLES-REGISTRY.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"\n📄 完整登记表已保存到: {output_file}\n")


def main():
    analyzer = ArticleAnalyzer()
    analyzer.run()


if __name__ == "__main__":
    main()
