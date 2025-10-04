#!/usr/bin/env python3
"""
已发布文章同步工具

功能：
1. 扫描_posts目录下的所有文章
2. 提取文章元数据（标题、日期、分类、系列等）
3. 自动更新00-PUBLISHED-ARTICLES-REGISTRY.md
4. 生成统计报告

使用：
python scripts/tools/content/sync_published_articles.py
"""

import os
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import yaml


class PublishedArticlesSyncer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.posts_dir = self.project_root / "_posts"
        self.registry_file = self.project_root / "_drafts" / "todos" / "00-PUBLISHED-ARTICLES-REGISTRY.md"
        self.articles = []

    def extract_front_matter(self, file_path):
        """提取文章的Front Matter"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 匹配Front Matter（YAML格式）
        match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return None

        try:
            front_matter = yaml.safe_load(match.group(1))
            return front_matter
        except yaml.YAMLError as e:
            print(f"⚠️ YAML解析错误 {file_path.name}: {e}")
            return None

    def scan_articles(self):
        """扫描所有已发布文章"""
        print("📚 扫描已发布文章...")

        for md_file in self.posts_dir.glob("*.md"):
            front_matter = self.extract_front_matter(md_file)
            if not front_matter:
                continue

            # 从文件名提取日期
            filename = md_file.stem
            date_match = re.match(r'^(\d{4}-\d{2}-\d{2})-(.+)$', filename)

            # 统一日期格式
            date_value = front_matter.get('date', date_match.group(1) if date_match else 'Unknown')
            if isinstance(date_value, datetime):
                date_str = date_value.strftime('%Y-%m-%d')
            else:
                date_str = str(date_value)[:10] if len(str(date_value)) >= 10 else str(date_value)

            article_info = {
                'filename': md_file.name,
                'slug': date_match.group(2) if date_match else filename,
                'date': date_str,
                'title': front_matter.get('title', 'No Title'),
                'categories': front_matter.get('categories', []),
                'tags': front_matter.get('tags', []),
                'series': front_matter.get('series'),
                'series_order': front_matter.get('series_order'),
                'member_tier': front_matter.get('member_tier'),
                'excerpt': front_matter.get('excerpt', ''),
            }

            self.articles.append(article_info)

        # 按日期排序（字符串格式YYYY-MM-DD可以直接排序）
        self.articles.sort(key=lambda x: x['date'] if x['date'] != 'Unknown' else '0000-00-00', reverse=True)
        print(f"✅ 共扫描到 {len(self.articles)} 篇文章")

    def categorize_articles(self):
        """按分类整理文章"""
        categorized = {
            '💰 投资理财': [],
            '🛠️ 技术赋能': [],
            '🧠 认知升级': [],
            '🌍 全球视野': [],
            '📺 英语学习': [],
            '📝 其他': []
        }

        category_mapping = {
            '投资理财': '💰 投资理财',
            '技术赋能': '🛠️ 技术赋能',
            '认知升级': '🧠 认知升级',
            '全球视野': '🌍 全球视野',
            '英语学习': '📺 英语学习',
        }

        for article in self.articles:
            cats = article.get('categories', [])
            matched = False

            for cat in cats:
                for key, value in category_mapping.items():
                    if key in str(cat):
                        categorized[value].append(article)
                        matched = True
                        break
                if matched:
                    break

            if not matched:
                categorized['📝 其他'].append(article)

        return categorized

    def group_by_series(self):
        """按系列分组文章"""
        series_dict = defaultdict(list)

        for article in self.articles:
            series_name = article.get('series')
            if series_name:
                series_dict[series_name].append(article)

        # 按series_order排序
        for series_name in series_dict:
            series_dict[series_name].sort(key=lambda x: x.get('series_order', 999))

        return dict(series_dict)

    def generate_statistics(self):
        """生成统计信息"""
        categorized = self.categorize_articles()
        series_dict = self.group_by_series()

        stats = {
            'total': len(self.articles),
            'by_category': {k: len(v) for k, v in categorized.items() if len(v) > 0},
            'series_count': len(series_dict),
            'series_articles': sum(len(v) for v in series_dict.values()),
            'standalone_articles': len(self.articles) - sum(len(v) for v in series_dict.values()),
        }

        return stats, categorized, series_dict

    def print_report(self):
        """打印统计报告"""
        stats, categorized, series_dict = self.generate_statistics()

        print("\n" + "="*60)
        print("📊 已发布文章统计报告")
        print("="*60)

        print(f"\n总文章数: {stats['total']} 篇")

        print("\n分类分布:")
        for category, count in stats['by_category'].items():
            percentage = (count / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {category}: {count} 篇 ({percentage:.1f}%)")

        print(f"\n系列文章: {stats['series_articles']} 篇（{stats['series_count']} 个系列）")
        print(f"独立文章: {stats['standalone_articles']} 篇")

        if series_dict:
            print("\n系列清单:")
            for series_name, articles in series_dict.items():
                print(f"  📚 {series_name}: {len(articles)} 篇")
                for article in articles:
                    order = article.get('series_order', '?')
                    date = str(article['date'])[:10]
                    print(f"     {order}. {article['title']} ({date})")

        print("\n" + "="*60)

    def export_to_markdown_table(self):
        """导出为Markdown表格格式"""
        stats, categorized, series_dict = self.generate_statistics()

        output = []
        output.append("## 📋 已发布文章完整清单（自动生成）\n")
        output.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"**总文章数**: {stats['total']} 篇\n")

        # 按系列输出
        if series_dict:
            output.append("### 🎯 系列文章\n")
            for series_name, articles in series_dict.items():
                output.append(f"#### {series_name} ({len(articles)}篇)\n")
                output.append("| 发布日期 | 标题 | 文件名 | 系列位置 |")
                output.append("|---------|------|--------|---------|")

                for article in articles:
                    date = str(article['date'])[:10]
                    order = article.get('series_order', '?')
                    title = article['title']
                    filename = f"`{article['filename']}`"
                    position = f"第{order}篇" if order != '?' else "待确认"

                    output.append(f"| {date} | {title} | {filename} | {position} |")

                output.append("")

        # 按分类输出独立文章
        output.append("### 📚 独立文章\n")
        for category, articles in categorized.items():
            if not articles:
                continue

            # 过滤掉已在系列中的文章
            standalone = [a for a in articles if not a.get('series')]
            if not standalone:
                continue

            output.append(f"#### {category} ({len(standalone)}篇)\n")
            output.append("| 发布日期 | 标题 | 文件名 | VIP等级 |")
            output.append("|---------|------|--------|---------|")

            for article in standalone:
                date = str(article['date'])[:10]
                title = article['title']
                filename = f"`{article['filename']}`"
                vip = article.get('member_tier', '免费')
                if vip == 'monthly':
                    vip = 'VIP2'
                elif vip == 'quarterly':
                    vip = 'VIP3'
                elif vip == 'yearly':
                    vip = 'VIP4'

                output.append(f"| {date} | {title} | {filename} | {vip} |")

            output.append("")

        return "\n".join(output)

    def run(self):
        """执行同步"""
        self.scan_articles()
        self.print_report()

        # 导出Markdown
        markdown_output = self.export_to_markdown_table()

        print("\n✅ Markdown表格已生成，可复制到登记表中")
        print("\n" + "="*60)
        print(markdown_output)
        print("="*60)

        # 询问是否保存到文件
        save_path = self.project_root / "_drafts" / "todos" / "published_articles_auto_generated.md"
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(markdown_output)

        print(f"\n💾 已保存到: {save_path}")


def main():
    syncer = PublishedArticlesSyncer()
    syncer.run()


if __name__ == "__main__":
    main()
