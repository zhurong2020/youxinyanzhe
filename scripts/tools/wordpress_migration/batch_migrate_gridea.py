#!/usr/bin/env python3
"""
Batch Migrate Gridea to WordPress - Enhanced Version

Includes:
- English slug generation
- Image center alignment
- Buy Me A Coffee image fix
- Gutenberg format conversion
- Correct category mapping

Usage:
    python batch_migrate_gridea.py --dry-run
    python batch_migrate_gridea.py --limit 5
    python batch_migrate_gridea.py
"""

import os
import sys
import re
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, Tag

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.tools.wordpress_migration.gutenberg_converter import GutenbergConverter, ConversionOptions

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Category mapping based on content analysis
CATEGORY_MAPPING = {
    # 投资理财
    'investment-finance': [
        'ba-lun-zhou-kan',  # 巴伦周刊
        'min-zhu-dang-vs-gong-he-dang',  # 民主党vs共和党
        'qdii-ji-jin',  # QDII基金
        'liang-hua', 'jiao-yi', 'tou-zi', 'gu-piao',
        'tqqq', 'moomoo', 'wang-ge',
    ],
    # 云技术入门
    'cloud-tech-basics': [
        'ji-chu-pian',  # 基础篇系列
        'vps', 'namesilo', 'putty', 'winscp',
        'github-pages', 'cloudflare', 'github-ru-men',
        'qing-song-shang-shou-yong-kai-yuan',  # 开源自托管
        'yun-duan-qi-hang',  # 云端启航
        'ling-cheng-ben-da-zao-yun-duan',  # 零成本打造云端
        'nas', 'dsm', 'racknerd',
    ],
    # 开源应用
    'opensource-apps': [
        'ti-yan-pian',  # 体验篇系列
        'lm-studio', 'nextchat', 'lobe-chat',
        'z-library', 'pandora',
    ],
    # 认知升级
    'cognitive-upgrade': [
        'prompt', 'kimi', 'si-wei-dao-tu',
        'du-shu', 'xue-xi', 'aboboo',
        'photoshop', 'ps-xue-xi',
        'shi-jian-guan-li', 'bi-ji',
    ],
    # 全球视野
    'global-perspective': [
        'shi-jie-chong-qi',  # 世界重启
        'charlie-kirk', 'prove-me-wrong',
        'shi-jie-geng-jing-cai', 'xin-wen-guan-dian',
    ],
}

# Slug mapping for Chinese titles
SLUG_MAPPING = {
    'ji-chu-pian-2-qing-song-yong-you-zi-ji-de-vps': 'vps-getting-started',
    'ji-chu-pian-3-shen-ru-liao-jie-racknerd-vps': 'racknerd-vps-guide',
    'ji-chu-pian-4-zhang-wo-putty-yu-winscp': 'putty-winscp-guide',
    'ji-chu-pian-5-namesilo-yu-ming-zhu-ce': 'namesilo-domain-registration',
    'ji-chu-pian-6-shi-yong-namesilo-jin-xing-yu-ming-jie-xi': 'namesilo-dns-setup',
    'ti-yan-pian-2-yong-kai-yuan-zi-tuo-guan-xiang-mu': 'self-hosted-digital-kingdom',
    'ti-yan-pian-5-nextchat-ge-xing-hua': 'nextchat-customization',
    'ti-yan-pian-7-lm-studio': 'lm-studio-local-ai',
    'ling-cheng-ben-da-zao-yun-duan-sheng-huo': 'free-domain-cloudflare-guide',
    'github-pages-jiao-cheng': 'github-pages-tutorial',
    'github-ru-men-kai-yuan-shi-jie': 'github-beginner-guide',
    'min-zhu-dang-vs-gong-he-dang-shui-shi-gu-shi-ying-jia': 'democrat-republican-stock-market',
    'xin-shou-ru-men-jia-mi-bi-zhi-nan': 'crypto-meme-coin-guide',
    'qdii-ji-jin-tou-zi-hai-wai': 'qdii-overseas-investment',
    'liang-hua-jiao-yi-ji-qi-ren-de-can-shu': 'quant-trading-parameters',
    'you-hua-liang-hua-jiao-yi-ce-lue': 'optimize-quant-strategy',
    'ai-zhu-li-liang-hua-jiao-yi': 'ai-quant-trading',
    'da-zao-ni-de-di-yi-ge-liang-hua-jiao-yi': 'first-quant-trading-bot',
    'shi-yong-wang-ge-jiao-yi-gong-ju': 'grid-trading-tool',
    'shi-yong-kimi-sheng-cheng-si-wei-dao-tu': 'kimi-mind-map',
    'jie-suo-shu-zi-tu-shu-guan-z-library': 'z-library-guide',
    'ba-lun-zhou-kan-gong-bu-liao-2024': 'barrons-top-10-stocks-2024',
    'photoshop-zi-xue-xi-lie': 'photoshop-tutorial',
}


@dataclass
class MigrationResult:
    folder: str
    title: str
    success: bool
    wp_id: Optional[int] = None
    wp_url: Optional[str] = None
    error: Optional[str] = None


class EnhancedGrideaMigrator:
    """Enhanced Gridea to WordPress migrator with all improvements"""

    def __init__(self, wp_url: str, wp_user: str, wp_password: str, dry_run: bool = False):
        self.wp_url = wp_url
        self.session = requests.Session()
        self.session.auth = (wp_user, wp_password)
        self.api_base = f"{wp_url}/wp-json/wp/v2"
        self.dry_run = dry_run

        # Gutenberg converter
        self.converter = GutenbergConverter(ConversionOptions(
            preserve_inline_styles=True,
            handle_mathjax=True,
            preserve_more_tag=True
        ))

        # Cache
        self.category_cache: Dict[str, int] = {}
        self.existing_slugs: set = set()

        # Stats
        self.results: List[MigrationResult] = []

    def load_existing_posts(self):
        """Load existing posts to avoid duplicates"""
        logger.info("Loading existing posts...")
        response = self.session.get(
            f"{self.api_base}/posts",
            params={'per_page': 100, 'status': 'publish'}
        )
        if response.status_code == 200:
            for post in response.json():
                self.existing_slugs.add(post['slug'])
        logger.info(f"Found {len(self.existing_slugs)} existing posts")

    def get_category_id(self, slug: str) -> Optional[int]:
        """Get category ID by slug"""
        if slug in self.category_cache:
            return self.category_cache[slug]

        response = self.session.get(
            f"{self.api_base}/categories",
            params={'slug': slug}
        )
        if response.status_code == 200 and response.json():
            cat_id = response.json()[0]['id']
            self.category_cache[slug] = cat_id
            return cat_id
        return None

    def determine_category(self, folder_name: str, tags: List[str]) -> str:
        """Determine category based on folder name and tags"""
        folder_lower = folder_name.lower()
        tags_lower = [t.lower() for t in tags]

        for category, keywords in CATEGORY_MAPPING.items():
            for keyword in keywords:
                if keyword in folder_lower:
                    return category
                if any(keyword in tag for tag in tags_lower):
                    return category

        # Default based on tags
        if any(t in ['投资', '股票', 'AI'] for t in tags):
            return 'investment-finance'
        if any(t in ['云生活', 'VPS'] for t in tags):
            return 'cloud-tech-basics'
        if any(t in ['开源', '免费'] for t in tags):
            return 'opensource-apps'
        if any(t in ['AI', '学习'] for t in tags):
            return 'cognitive-upgrade'

        return 'cloud-tech-basics'  # Default

    def generate_slug(self, folder_name: str, title: str) -> str:
        """Generate English slug from folder name or title"""
        # Check mapping first
        for key, slug in SLUG_MAPPING.items():
            if key in folder_name:
                return slug

        # Generate from folder name
        slug = folder_name.replace('-', '-')

        # If slug is too long or contains Chinese encoding, simplify
        if len(slug) > 50:
            # Extract key parts
            parts = slug.split('-')[:5]
            slug = '-'.join(parts)

        return slug

    def extract_post(self, html_path: Path) -> Optional[dict]:
        """Extract post from Gridea HTML"""
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html = f.read()

            soup = BeautifulSoup(html, 'html.parser')

            # Title
            title_elem = soup.find('title')
            title = title_elem.text.split('|')[0].strip() if title_elem else ""

            # Date
            date = None
            date_elem = soup.find(class_=re.compile(r'date|time'))
            if date_elem:
                date_match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_elem.get_text())
                if date_match:
                    date = datetime(int(date_match.group(1)), int(date_match.group(2)), int(date_match.group(3)))
            if not date:
                date = datetime.now()

            # Content
            content_div = soup.find('div', class_='post-content')
            content_html = str(content_div) if content_div else ""

            # Tags
            tags = []
            keywords = soup.find('meta', attrs={'name': 'keywords'})
            if keywords and isinstance(keywords, Tag):
                kw = keywords.get('content')
                if kw:
                    tags = [t.strip() for t in str(kw).split(',') if t.strip()]

            # Excerpt
            excerpt = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and isinstance(meta_desc, Tag):
                exc = meta_desc.get('content')
                if exc:
                    excerpt = str(exc)[:300]

            return {
                'folder': html_path.parent.name,
                'title': title,
                'date': date,
                'content_html': content_html,
                'tags': tags,
                'excerpt': excerpt
            }

        except Exception as e:
            logger.error(f"Failed to extract {html_path}: {e}")
            return None

    def process_content(self, content_html: str) -> str:
        """Process content: convert to Gutenberg and apply fixes"""
        # Convert to Gutenberg
        gutenberg, _ = self.converter.convert(content_html)

        # Fix image alignment - center all images
        gutenberg = re.sub(
            r'<!-- wp:image -->',
            '<!-- wp:image {"align":"center"} -->',
            gutenberg
        )
        gutenberg = re.sub(
            r'<figure class="wp-block-image">',
            '<figure class="wp-block-image aligncenter">',
            gutenberg
        )

        # Fix Buy Me A Coffee image
        coffee_pattern = r'<!-- wp:image[^>]*-->\s*<figure[^>]*><img[^>]*alt="请我喝咖啡"[^>]*></figure>\s*<!-- /wp:image -->'
        coffee_replacement = '''<!-- wp:paragraph -->
<p><a href="https://www.buymeacoffee.com/zhurong052Q" target="_blank"><img style="width: 200px;" src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee"></a></p>
<!-- /wp:paragraph -->'''
        gutenberg = re.sub(coffee_pattern, coffee_replacement, gutenberg, flags=re.DOTALL)

        return gutenberg

    def migrate_post(self, post_data: dict) -> MigrationResult:
        """Migrate a single post to WordPress"""
        folder = post_data['folder']
        title = post_data['title']

        # Generate slug
        slug = self.generate_slug(folder, title)

        # Check if already exists
        if slug in self.existing_slugs:
            logger.info(f"  Skipping (already exists): {slug}")
            return MigrationResult(folder, title, False, error="Already exists")

        # Determine category
        category_slug = self.determine_category(folder, post_data['tags'])
        category_id = self.get_category_id(category_slug)

        # Process content
        content = self.process_content(post_data['content_html'])

        if self.dry_run:
            logger.info(f"  [DRY RUN] Would create:")
            logger.info(f"    Title: {title}")
            logger.info(f"    Slug: {slug}")
            logger.info(f"    Category: {category_slug}")
            logger.info(f"    Tags: {post_data['tags']}")
            return MigrationResult(folder, title, True)

        # Create post
        post_payload = {
            'title': title,
            'slug': slug,
            'content': content,
            'excerpt': post_data['excerpt'],
            'status': 'publish',
            'date': post_data['date'].isoformat() if post_data['date'] else None,
            'categories': [category_id] if category_id else [],
        }

        try:
            response = self.session.post(f"{self.api_base}/posts", json=post_payload)

            if response.status_code == 201:
                result = response.json()
                logger.info(f"  Created: ID={result['id']}, URL={result['link']}")
                return MigrationResult(
                    folder, title, True,
                    wp_id=result['id'],
                    wp_url=result['link']
                )
            else:
                logger.error(f"  Failed: {response.status_code} - {response.text[:200]}")
                return MigrationResult(folder, title, False, error=response.text[:200])

        except Exception as e:
            logger.error(f"  Exception: {e}")
            return MigrationResult(folder, title, False, error=str(e))

    def migrate_all(self, source_dir: str, limit: Optional[int] = None, exclude: Optional[List[str]] = None):
        """Migrate all posts from source directory"""
        source_path = Path(source_dir)
        exclude = exclude or []

        # Find all posts
        posts = []
        for item in source_path.iterdir():
            if item.is_dir() and item.name not in exclude and item.name != 'about':
                index_file = item / 'index.html'
                if index_file.exists():
                    posts.append(index_file)

        posts.sort(key=lambda p: p.parent.name)

        if limit:
            posts = posts[:limit]

        logger.info(f"Found {len(posts)} posts to migrate")

        # Load existing posts
        self.load_existing_posts()

        # Migrate each post
        for i, post_path in enumerate(posts, 1):
            logger.info(f"\n[{i}/{len(posts)}] Processing: {post_path.parent.name}")

            post_data = self.extract_post(post_path)
            if not post_data:
                self.results.append(MigrationResult(post_path.parent.name, "", False, error="Extract failed"))
                continue

            result = self.migrate_post(post_data)
            self.results.append(result)

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print migration summary"""
        success = sum(1 for r in self.results if r.success)
        failed = sum(1 for r in self.results if not r.success)

        logger.info("\n" + "=" * 50)
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total: {len(self.results)}")
        logger.info(f"Success: {success}")
        logger.info(f"Failed: {failed}")

        if failed > 0:
            logger.info("\nFailed posts:")
            for r in self.results:
                if not r.success:
                    logger.info(f"  - {r.folder}: {r.error}")

        # Save results
        with open('batch_migration_results.json', 'w', encoding='utf-8') as f:
            json.dump([{
                'folder': r.folder,
                'title': r.title,
                'success': r.success,
                'wp_id': r.wp_id,
                'wp_url': r.wp_url,
                'error': r.error
            } for r in self.results], f, indent=2, ensure_ascii=False, default=str)
        logger.info("\nResults saved to: batch_migration_results.json")


def main():
    parser = argparse.ArgumentParser(description='Batch migrate Gridea to WordPress')
    parser.add_argument('--source', default='/home/wuxia/projects/zhurong2020.github.io/post')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()

    migrator = EnhancedGrideaMigrator(
        wp_url=os.getenv('WP_URL', 'https://www.arong.eu.org'),
        wp_user=os.getenv('WP_USER', 'arong'),
        wp_password=os.getenv('WP_APP_PASSWORD', ''),
        dry_run=args.dry_run
    )

    # Exclude already migrated posts (from DEDUPLICATED-ARTICLES-REGISTRY.md)
    already_migrated = [
        'prove-me-wrong',
        '2025-nian-de-shi-jie-geng-jing-cai',
        'tqqq-ding-tou-hui-ce',
        'kai-yuan-ding-tou-ce-lue-gai-zao',
        'mei-gu-bei-dong-shou-ru-zhi-nan',
        'qi-quan-jie-tao-wan-quan-zhi-nan',
        'te-si-la-gai-nian-gu-tou-zi',
        'wei-shi-me-pu-tong-ren-ying-gai',
        'zhi-neng-tou-zi-zhi-nan',
        'liao-tian-ji-qi-ren-xiao-mi-jue',
        'wei-shi-me-yi-zhi-li-zong-shi',
        'xin-xi-mi-wu-zhong-de-qiu-zhen',
        'dang-ji-qi-ren-yong-you-ling-hun',
        'ma-si-ke-di-guo-jie-mi',
        'te-si-la-22-tian-kuo-zhang',
        'te-si-la-de-sheng-chan-li-he-bao',
        # Also exclude ones already in WordPress
        'github-ru-men-kai-yuan-shi-jie-de-di-yi-bu',  # Just migrated
    ]

    migrator.migrate_all(args.source, limit=args.limit, exclude=already_migrated)


if __name__ == '__main__':
    main()
