#!/usr/bin/env python3
"""
博客网站爬虫工具

功能：
1. 爬取zhurong2020.github.io/youxinyanzhe网站上的所有文章
2. 与本地_posts目录对比，识别缺失文章
3. 生成完整的文章清单

使用：
python scripts/tools/content/crawl_published_site.py
"""

import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
from datetime import datetime
import json


class BlogCrawler:
    def __init__(self):
        self.base_url = "https://zhurong2020.github.io"
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.posts_dir = self.project_root / "_posts"
        self.online_articles = []
        self.local_articles = []

    def fetch_page(self, url):
        """获取网页内容"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"❌ 获取页面失败 {url}: {e}")
            return None

    def parse_posts_page(self, html):
        """解析文章归档页面"""
        soup = BeautifulSoup(html, 'html.parser')
        articles = []

        # 查找所有文章条目
        # Jekyll Chirpy主题通常使用特定的HTML结构
        post_items = soup.find_all(['article', 'div'], class_=re.compile(r'post|card'))

        if not post_items:
            # 尝试其他可能的选择器
            post_items = soup.find_all('a', href=re.compile(r'/posts/\d{4}/\d{2}/'))

        for item in post_items:
            # 提取标题
            title_elem = item.find(['h1', 'h2', 'h3', 'h4'])
            if not title_elem:
                title_elem = item.find('a', href=re.compile(r'/posts/'))

            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)

            # 提取链接
            link_elem = item.find('a', href=re.compile(r'/posts/'))
            if not link_elem:
                continue

            link = link_elem.get('href', '')
            if not link.startswith('http'):
                link = self.base_url + link

            # 从链接中提取slug和日期
            match = re.search(r'/posts/(\d{4})/(\d{2})/([^/]+)/?$', link)
            if match:
                year, month, slug = match.groups()

                # 提取日期（尝试从页面或使用URL中的日期）
                date_elem = item.find(class_=re.compile(r'date|time'))
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    # 尝试解析日期
                    for fmt in ['%B %d, %Y', '%Y-%m-%d', '%d %B %Y']:
                        try:
                            date_obj = datetime.strptime(date_text, fmt)
                            date = date_obj.strftime('%Y-%m-%d')
                            break
                        except:
                            continue
                    else:
                        date = f"{year}-{month}-01"
                else:
                    date = f"{year}-{month}-01"

                articles.append({
                    'title': title,
                    'link': link,
                    'slug': slug,
                    'date': date,
                    'year': year,
                    'month': month
                })

        return articles

    def crawl_online_articles(self):
        """爬取线上所有文章"""
        print("🌐 开始爬取线上博客文章...")

        # 1. 爬取文章归档页面
        posts_url = f"{self.base_url}/posts/"
        html = self.fetch_page(posts_url)
        if html:
            articles = self.parse_posts_page(html)
            self.online_articles.extend(articles)
            print(f"✅ 从归档页面获取到 {len(articles)} 篇文章")

        # 2. 爬取首页
        home_url = self.base_url
        html = self.fetch_page(home_url)
        if html:
            articles = self.parse_posts_page(html)
            # 去重
            existing_slugs = {a['slug'] for a in self.online_articles}
            new_articles = [a for a in articles if a['slug'] not in existing_slugs]
            self.online_articles.extend(new_articles)
            print(f"✅ 从首页额外获取 {len(new_articles)} 篇文章")

        # 去重并排序
        unique_articles = {}
        for article in self.online_articles:
            unique_articles[article['slug']] = article

        self.online_articles = list(unique_articles.values())
        self.online_articles.sort(key=lambda x: x['date'], reverse=True)

        print(f"📊 线上文章总数: {len(self.online_articles)} 篇")

    def scan_local_articles(self):
        """扫描本地文章"""
        print("\n📁 扫描本地_posts目录...")

        for md_file in self.posts_dir.glob("*.md"):
            filename = md_file.stem
            match = re.match(r'^(\d{4}-\d{2}-\d{2})-(.+)$', filename)
            if match:
                date, slug = match.groups()
                self.local_articles.append({
                    'filename': md_file.name,
                    'slug': slug,
                    'date': date
                })

        print(f"✅ 本地文章总数: {len(self.local_articles)} 篇")

    def compare_articles(self):
        """对比线上和本地文章"""
        print("\n🔍 对比线上和本地文章...")

        local_slugs = {a['slug'] for a in self.local_articles}
        online_slugs = {a['slug'] for a in self.online_articles}

        # 线上有但本地没有的文章
        missing_local = []
        for article in self.online_articles:
            if article['slug'] not in local_slugs:
                missing_local.append(article)

        # 本地有但线上没有的文章（可能是草稿）
        not_published = []
        for article in self.local_articles:
            if article['slug'] not in online_slugs:
                not_published.append(article)

        return missing_local, not_published

    def generate_report(self):
        """生成对比报告"""
        missing_local, not_published = self.compare_articles()

        print("\n" + "="*60)
        print("📊 文章对比报告")
        print("="*60)

        print(f"\n线上文章总数: {len(self.online_articles)} 篇")
        print(f"本地文章总数: {len(self.local_articles)} 篇")

        if missing_local:
            print(f"\n⚠️ 线上有但本地缺失的文章: {len(missing_local)} 篇")
            for article in missing_local:
                print(f"  - {article['date']} | {article['title']}")
                print(f"    链接: {article['link']}")
        else:
            print("\n✅ 所有线上文章在本地都有对应文件")

        if not_published:
            print(f"\n📝 本地有但未发布的文章: {len(not_published)} 篇")
            for article in not_published:
                print(f"  - {article['date']} | {article['slug']}")

        print("\n" + "="*60)

        # 导出完整文章列表
        output = {
            'online_articles': self.online_articles,
            'local_articles': self.local_articles,
            'missing_local': missing_local,
            'not_published': not_published,
            'generated_at': datetime.now().isoformat()
        }

        output_file = self.project_root / "_drafts" / "todos" / "crawled_articles.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"💾 详细数据已保存到: {output_file}")

        return missing_local, not_published

    def generate_markdown_list(self):
        """生成Markdown格式的文章列表"""
        output = []
        output.append("## 🌐 线上发布的文章完整清单\n")
        output.append(f"**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"**文章总数**: {len(self.online_articles)} 篇\n")

        # 按年份分组
        articles_by_year = {}
        for article in self.online_articles:
            year = article['year']
            if year not in articles_by_year:
                articles_by_year[year] = []
            articles_by_year[year].append(article)

        for year in sorted(articles_by_year.keys(), reverse=True):
            articles = articles_by_year[year]
            output.append(f"### {year}年 ({len(articles)}篇)\n")
            output.append("| 发布日期 | 文章标题 | 链接 |")
            output.append("|---------|---------|------|")

            for article in sorted(articles, key=lambda x: x['date'], reverse=True):
                date = article['date']
                title = article['title']
                link = article['link']
                output.append(f"| {date} | {title} | [查看]({link}) |")

            output.append("")

        return "\n".join(output)

    def run(self):
        """执行爬取和对比"""
        self.crawl_online_articles()
        self.scan_local_articles()
        missing_local, not_published = self.generate_report()

        # 生成Markdown列表
        markdown_list = self.generate_markdown_list()

        output_file = self.project_root / "_drafts" / "todos" / "online_articles_list.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_list)

        print(f"\n📄 Markdown文章列表已保存到: {output_file}")


def main():
    crawler = BlogCrawler()
    crawler.run()


if __name__ == "__main__":
    main()
