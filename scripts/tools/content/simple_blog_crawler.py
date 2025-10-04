#!/usr/bin/env python3
"""
简单的博客爬虫 - 不依赖BeautifulSoup
使用正则表达式直接从HTML中提取文章信息
"""

import re
import requests
from pathlib import Path
import json
from datetime import datetime


def fetch_page(url):
    """获取网页内容"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        return None


def extract_articles_from_html(html):
    """从HTML中提取文章信息"""
    articles = []

    # Gridea 的实际HTML结构：
    # <article class="post">
    #   <a href="...">
    #     <h2 class="post-title">标题</h2>
    #   </a>
    # </article>

    # 提取所有文章块
    article_pattern = r'<article[^>]*class="post"[^>]*>(.*?)</article>'
    article_blocks = re.findall(article_pattern, html, re.DOTALL)

    for block in article_blocks:
        # 提取链接（在a标签中）
        link_match = re.search(r'<a\s+href="([^"]+)"', block)
        if not link_match:
            continue

        link = link_match.group(1)

        # 提取标题（在h2中）
        title_match = re.search(r'<h2[^>]*class="post-title"[^>]*>(.*?)</h2>', block, re.DOTALL)
        if not title_match:
            continue

        title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
        title = re.sub(r'\s+', ' ', title)  # 清理多余空格

        # 提取日期
        date_match = re.search(r'<time[^>]*>(.*?)</time>', block)
        date = date_match.group(1).strip() if date_match else 'Unknown'

        # 从链接中提取slug
        slug_match = re.search(r'/post/([^/]+)/?$', link)
        slug = slug_match.group(1) if slug_match else link.split('/')[-1]

        articles.append({
            'title': title,
            'link': link if link.startswith('http') else f"https://zhurong2020.github.io{link}",
            'slug': slug,
            'date': date
        })

    return articles


def crawl_archives():
    """爬取归档页面"""
    print("🌐 开始爬取归档页面...")

    url = "https://zhurong2020.github.io/archives/"
    html = fetch_page(url)

    if not html:
        return []

    articles = extract_articles_from_html(html)
    print(f"✅ 从归档页面提取到 {len(articles)} 篇文章")

    return articles


def crawl_homepage_pagination():
    """爬取首页的分页内容"""
    print("\n🌐 开始爬取首页分页...")
    all_articles = []

    # 尝试抓取前5页
    for page in range(1, 6):
        if page == 1:
            url = "https://zhurong2020.github.io/"
        else:
            url = f"https://zhurong2020.github.io/page/{page}/"

        print(f"  正在抓取第{page}页...")
        html = fetch_page(url)

        if not html:
            break

        articles = extract_articles_from_html(html)
        if not articles:
            print(f"  第{page}页没有找到文章，停止")
            break

        all_articles.extend(articles)
        print(f"  ✅ 第{page}页: {len(articles)} 篇文章")

    return all_articles


def scan_local_posts():
    """扫描本地_posts目录"""
    project_root = Path(__file__).parent.parent.parent.parent
    posts_dir = project_root / "_posts"

    local_articles = []
    for md_file in posts_dir.glob("*.md"):
        filename = md_file.stem
        match = re.match(r'^(\d{4}-\d{2}-\d{2})-(.+)$', filename)
        if match:
            date, slug = match.groups()
            local_articles.append({
                'filename': md_file.name,
                'slug': slug,
                'date': date
            })

    return local_articles


def deduplicate_articles(articles):
    """去重文章（基于slug）"""
    unique = {}
    for article in articles:
        slug = article['slug']
        if slug not in unique:
            unique[slug] = article

    return list(unique.values())


def compare_and_report():
    """对比线上和本地文章"""
    # 1. 爬取线上文章
    online_articles = []

    # 从归档页面爬取
    archives_articles = crawl_archives()
    online_articles.extend(archives_articles)

    # 从首页分页爬取
    homepage_articles = crawl_homepage_pagination()
    online_articles.extend(homepage_articles)

    # 去重
    online_articles = deduplicate_articles(online_articles)
    online_articles.sort(key=lambda x: x.get('date', ''), reverse=True)

    print(f"\n📊 线上文章总数（去重后）: {len(online_articles)} 篇")

    # 2. 扫描本地文章
    print("\n📁 扫描本地_posts目录...")
    local_articles = scan_local_posts()
    print(f"✅ 本地文章总数: {len(local_articles)} 篇")

    # 3. 对比
    print("\n🔍 对比线上和本地文章...")

    local_slugs = {a['slug'] for a in local_articles}
    online_slugs = {a['slug'] for a in online_articles}

    missing_local = [a for a in online_articles if a['slug'] not in local_slugs]
    not_online = [a for a in local_articles if a['slug'] not in online_slugs]

    # 4. 生成报告
    print("\n" + "="*70)
    print("📊 文章对比报告")
    print("="*70)

    print(f"\n线上文章: {len(online_articles)} 篇")
    print(f"本地文章: {len(local_articles)} 篇")
    print(f"两者都有: {len(online_slugs & local_slugs)} 篇")

    if missing_local:
        print(f"\n⚠️ 线上有但本地缺失: {len(missing_local)} 篇")
        for article in missing_local[:10]:  # 只显示前10个
            print(f"  - {article.get('date', 'No date')} | {article['title']}")
            print(f"    链接: {article['link']}")
            print(f"    Slug: {article['slug']}")
        if len(missing_local) > 10:
            print(f"  ... 还有 {len(missing_local) - 10} 篇")
    else:
        print("\n✅ 所有线上文章在本地都有对应")

    if not_online:
        print(f"\n📝 本地有但未发布: {len(not_online)} 篇")
        for article in not_online[:5]:
            print(f"  - {article['date']} | {article['slug']}")

    print("\n" + "="*70)

    # 5. 保存详细数据
    project_root = Path(__file__).parent.parent.parent.parent
    output_file = project_root / "_drafts" / "todos" / "crawled_blog_data.json"

    data = {
        'online_articles': online_articles,
        'local_articles': local_articles,
        'missing_local': missing_local,
        'not_online': not_online,
        'generated_at': datetime.now().isoformat(),
        'stats': {
            'online_total': len(online_articles),
            'local_total': len(local_articles),
            'both': len(online_slugs & local_slugs),
            'missing_local': len(missing_local),
            'not_online': len(not_online)
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"💾 详细数据已保存到: {output_file}")

    # 6. 生成Markdown列表
    md_output = []
    md_output.append("## 🌐 线上博客文章完整清单")
    md_output.append(f"\n**爬取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    md_output.append(f"**文章总数**: {len(online_articles)} 篇\n")

    md_output.append("| 序号 | 发布日期 | 文章标题 | Slug | 本地状态 |")
    md_output.append("|------|---------|---------|------|---------|")

    for idx, article in enumerate(online_articles, 1):
        date = article.get('date', 'Unknown')
        title = article['title']
        slug = article['slug']
        local_status = "✅ 已有" if slug in local_slugs else "❌ 缺失"

        md_output.append(f"| {idx} | {date} | {title} | `{slug}` | {local_status} |")

    md_file = project_root / "_drafts" / "todos" / "online_blog_articles.md"
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_output))

    print(f"📄 Markdown列表已保存到: {md_file}\n")

    return data


if __name__ == "__main__":
    compare_and_report()
