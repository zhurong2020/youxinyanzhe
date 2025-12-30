#!/usr/bin/env python3
"""
Gridea HTML to WordPress Migration Script

Migrates Gridea static HTML posts to WordPress via REST API.
Extracts content from compiled HTML and converts back to structured posts.

Usage:
    python gridea_html_to_wp.py --source /path/to/zhurong2020.github.io/post/ --dry-run
    python gridea_html_to_wp.py --source /path/to/zhurong2020.github.io/post/ --limit 10
"""

import os
import sys
import re
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup, Tag
import html2text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gridea_migration.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class MigrationConfig:
    """Configuration for migration"""
    wp_url: str = ""
    wp_user: str = ""
    wp_app_password: str = ""
    dry_run: bool = False
    source_dir: str = ""
    limit: Optional[int] = None
    default_category: str = "待分类"

    # Category mapping cache
    category_map: Dict[str, int] = field(default_factory=dict)
    tag_cache: Dict[str, int] = field(default_factory=dict)


@dataclass
class GrideaPost:
    """Represents a parsed Gridea post from HTML"""
    folder_name: str
    title: str
    date: Optional[datetime]
    content_html: str
    content_markdown: str
    excerpt: str = ""
    tags: List[str] = field(default_factory=list)
    feature_image: str = ""


class GrideaHtmlToWordPress:
    """Migration class for Gridea HTML to WordPress"""

    def __init__(self, config: MigrationConfig):
        self.config = config
        self.session = requests.Session()

        if config.wp_user and config.wp_app_password:
            self.session.auth = (config.wp_user, config.wp_app_password)

        self.api_base = f"{config.wp_url}/wp-json/wp/v2"

        # HTML to Markdown converter
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.body_width = 0  # Don't wrap lines
        self.h2t.unicode_snob = True

        # Statistics
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

        self.results: List[Dict[str, Any]] = []

    def extract_post_from_html(self, html_path: Path) -> Optional[GrideaPost]:
        """Extract post content and metadata from Gridea HTML file"""
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract title
            title_elem = soup.find('title')
            title = ""
            if title_elem:
                title = title_elem.text.strip()
                # Remove site name suffix (e.g., "文章标题 | 有心言者")
                if '|' in title:
                    title = title.split('|')[0].strip()

            # Extract date from meta or content
            date = self.extract_date(soup, html_path.parent.name)

            # Extract main content
            content_html = ""
            content_div = soup.find('div', class_='post-content')
            if not content_div:
                content_div = soup.find('article')
            if not content_div:
                content_div = soup.find('div', class_='content')

            if content_div:
                content_html = str(content_div)

            # Convert HTML to Markdown
            content_markdown = self.h2t.handle(content_html) if content_html else ""

            # Clean up Markdown
            content_markdown = self.clean_markdown(content_markdown)

            # Extract excerpt from meta description
            excerpt = ""
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and isinstance(meta_desc, Tag):
                content = meta_desc.get('content')
                if content and isinstance(content, str):
                    excerpt = content[:300]

            # Extract tags
            tags = self.extract_tags(soup)

            # Extract feature image
            feature_image = ""
            og_image = soup.find('meta', attrs={'property': 'og:image'})
            if og_image and isinstance(og_image, Tag):
                img_content = og_image.get('content')
                if img_content and isinstance(img_content, str):
                    feature_image = img_content

            return GrideaPost(
                folder_name=html_path.parent.name,
                title=title,
                date=date,
                content_html=content_html,
                content_markdown=content_markdown,
                excerpt=excerpt,
                tags=tags,
                feature_image=feature_image
            )

        except Exception as e:
            logger.error(f"Failed to extract post from {html_path}: {e}")
            return None

    def extract_date(self, soup: BeautifulSoup, folder_name: str) -> Optional[datetime]:
        """Extract publication date from HTML or folder name"""
        # Try to find date in meta tags
        date_meta = soup.find('meta', attrs={'property': 'article:published_time'})
        if date_meta and isinstance(date_meta, Tag):
            date_content = date_meta.get('content')
            if date_content and isinstance(date_content, str):
                try:
                    return datetime.fromisoformat(date_content.replace('Z', '+00:00'))
                except ValueError:
                    pass

        # Try to extract from folder name (some Gridea posts have date prefix)
        # Pattern: 2025-nian-..., 2024-..., etc.
        year_match = re.match(r'^(\d{4})-', folder_name)
        if year_match:
            year = int(year_match.group(1))
            return datetime(year, 1, 1)

        year_match = re.match(r'^(\d{4})nian', folder_name)
        if year_match:
            year = int(year_match.group(1))
            return datetime(year, 1, 1)

        # Try to find date in page content
        date_elem = soup.find(class_=re.compile(r'date|time|published'))
        if date_elem:
            date_text = date_elem.get_text()
            # Try common date formats
            for pattern in [r'(\d{4})-(\d{2})-(\d{2})', r'(\d{4})年(\d{1,2})月(\d{1,2})日']:
                match = re.search(pattern, date_text)
                if match:
                    try:
                        return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
                    except ValueError:
                        pass

        # Default to current date
        return datetime.now()

    def extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract tags from HTML"""
        tags = []

        # Try meta keywords
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        if keywords and isinstance(keywords, Tag):
            kw_content = keywords.get('content')
            if kw_content and isinstance(kw_content, str):
                tags.extend([t.strip() for t in kw_content.split(',') if t.strip()])

        # Try tag links
        tag_links = soup.find_all('a', href=re.compile(r'/tag/'))
        for link in tag_links:
            tag_text = link.get_text().strip()
            if tag_text and tag_text not in tags:
                tags.append(tag_text)

        return tags

    def clean_markdown(self, markdown: str) -> str:
        """Clean up converted Markdown"""
        # Remove excessive blank lines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)

        # Fix image URLs (convert relative to absolute)
        markdown = re.sub(
            r'!\[([^\]]*)\]\(/post-images/',
            r'![\1](https://zhurong2020.github.io/post-images/',
            markdown
        )

        # Remove navigation elements that might have been included
        lines = markdown.split('\n')
        clean_lines = []
        skip_patterns = ['首页', '归档', '标签', '关于', '←', '→', 'Previous', 'Next']

        for line in lines:
            if not any(pattern in line for pattern in skip_patterns):
                clean_lines.append(line)

        return '\n'.join(clean_lines).strip()

    def get_or_create_category(self, category_name: str) -> Optional[int]:
        """Get category ID or create if not exists"""
        if category_name in self.config.category_map:
            return self.config.category_map[category_name]

        if self.config.dry_run:
            logger.info(f"  [DRY RUN] Would look up/create category: {category_name}")
            return None

        try:
            # Search for existing category
            response = self.session.get(
                f"{self.api_base}/categories",
                params={'search': category_name, 'per_page': 10}
            )

            if response.status_code == 200:
                for cat in response.json():
                    if cat['name'] == category_name:
                        self.config.category_map[category_name] = cat['id']
                        return cat['id']

            # Create new category
            response = self.session.post(
                f"{self.api_base}/categories",
                json={'name': category_name}
            )

            if response.status_code == 201:
                cat_id = response.json()['id']
                self.config.category_map[category_name] = cat_id
                logger.info(f"  Created category: {category_name} (ID: {cat_id})")
                return cat_id

        except Exception as e:
            logger.error(f"  Failed to get/create category: {e}")

        return None

    def get_or_create_tag(self, tag_name: str) -> Optional[int]:
        """Get tag ID or create if not exists"""
        if tag_name in self.config.tag_cache:
            return self.config.tag_cache[tag_name]

        if self.config.dry_run:
            return None

        try:
            response = self.session.get(
                f"{self.api_base}/tags",
                params={'search': tag_name, 'per_page': 5}
            )

            if response.status_code == 200:
                for tag in response.json():
                    if tag['name'].lower() == tag_name.lower():
                        self.config.tag_cache[tag_name] = tag['id']
                        return tag['id']

            # Create new tag
            response = self.session.post(
                f"{self.api_base}/tags",
                json={'name': tag_name}
            )

            if response.status_code == 201:
                tag_id = response.json()['id']
                self.config.tag_cache[tag_name] = tag_id
                return tag_id

        except Exception as e:
            logger.error(f"  Failed to get/create tag: {e}")

        return None

    def create_wp_post(self, post: GrideaPost) -> Optional[Dict[str, Any]]:
        """Create a WordPress post from a Gridea post"""
        logger.info(f"Processing: {post.title}")

        # Get default category
        category_ids = []
        cat_id = self.get_or_create_category(self.config.default_category)
        if cat_id:
            category_ids.append(cat_id)

        # Get tag IDs
        tag_ids = []
        for tag in post.tags:
            tag_id = self.get_or_create_tag(tag)
            if tag_id:
                tag_ids.append(tag_id)

        # Use HTML content directly (WordPress handles it well)
        # Or use Markdown with a Gutenberg block
        content = post.content_html

        post_data = {
            'title': post.title,
            'content': content,
            'excerpt': post.excerpt,
            'status': 'publish',
            'date': post.date.isoformat() if post.date else None,
            'categories': category_ids,
            'tags': tag_ids,
        }

        if self.config.dry_run:
            logger.info(f"  [DRY RUN] Would create post:")
            logger.info(f"    Title: {post.title}")
            logger.info(f"    Date: {post.date}")
            logger.info(f"    Tags: {post.tags}")
            logger.info(f"    Content length: {len(post.content_markdown)} chars")
            logger.info(f"    Feature image: {post.feature_image[:50] if post.feature_image else 'None'}...")
            return {'dry_run': True, 'title': post.title}

        try:
            response = self.session.post(
                f"{self.api_base}/posts",
                json=post_data
            )

            if response.status_code == 201:
                result = response.json()
                logger.info(f"  Created post ID: {result['id']}")
                return {
                    'success': True,
                    'wp_id': result['id'],
                    'wp_url': result.get('link', ''),
                    'gridea_folder': post.folder_name,
                    'title': post.title
                }
            else:
                logger.error(f"  Failed to create post: {response.status_code}")
                return {'success': False, 'error': response.text}

        except Exception as e:
            logger.error(f"  Exception creating post: {e}")
            return {'success': False, 'error': str(e)}

    def find_posts(self, source_dir: str) -> List[Path]:
        """Find all Gridea post directories"""
        source_path = Path(source_dir)

        if not source_path.exists():
            logger.error(f"Source directory not found: {source_dir}")
            return []

        posts = []
        for item in source_path.iterdir():
            if item.is_dir():
                index_file = item / 'index.html'
                if index_file.exists():
                    posts.append(index_file)

        posts.sort(key=lambda p: p.parent.name)
        return posts

    def migrate_all(self, source_dir: str):
        """Migrate all posts from source directory"""
        posts = self.find_posts(source_dir)

        if not posts:
            logger.warning("No posts found to migrate")
            return

        if self.config.limit:
            posts = posts[:self.config.limit]

        self.stats['total'] = len(posts)
        logger.info(f"Found {len(posts)} posts to migrate")

        for i, post_path in enumerate(posts, 1):
            logger.info(f"\n[{i}/{len(posts)}] Processing: {post_path.parent.name}")

            post = self.extract_post_from_html(post_path)
            if not post:
                self.stats['failed'] += 1
                continue

            # Skip 'about' page
            if post.folder_name == 'about':
                logger.info("  Skipping 'about' page")
                self.stats['skipped'] += 1
                continue

            result = self.create_wp_post(post)

            if result:
                if result.get('success') or result.get('dry_run'):
                    self.stats['success'] += 1
                else:
                    self.stats['failed'] += 1
                self.results.append(result)
            else:
                self.stats['failed'] += 1

        self.print_summary()

    def print_summary(self):
        """Print migration summary"""
        logger.info("\n" + "=" * 50)
        logger.info("GRIDEA MIGRATION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total posts: {self.stats['total']}")
        logger.info(f"Successful:  {self.stats['success']}")
        logger.info(f"Failed:      {self.stats['failed']}")
        logger.info(f"Skipped:     {self.stats['skipped']}")

        if self.config.dry_run:
            logger.info("\n[DRY RUN MODE] No actual changes were made")

        results_file = Path('gridea_migration_results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"\nResults saved to: {results_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Migrate Gridea HTML posts to WordPress',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Dry run to preview migration
    python gridea_html_to_wp.py --source ../zhurong2020.github.io/post/ --dry-run

    # Migrate first 10 posts
    python gridea_html_to_wp.py --source ../zhurong2020.github.io/post/ --limit 10

Environment Variables:
    WP_URL          WordPress site URL
    WP_USER         WordPress username
    WP_APP_PASSWORD WordPress application password
        """
    )

    parser.add_argument(
        '--source', '-s',
        required=True,
        help='Source directory containing Gridea post folders'
    )

    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Preview migration without making changes'
    )

    parser.add_argument(
        '--limit', '-l',
        type=int,
        help='Limit number of posts to migrate'
    )

    parser.add_argument(
        '--default-category',
        default='待分类',
        help='Default category for migrated posts (default: 待分类)'
    )

    parser.add_argument('--wp-url', help='WordPress site URL')
    parser.add_argument('--wp-user', help='WordPress username')
    parser.add_argument('--wp-password', help='WordPress app password')

    args = parser.parse_args()

    config = MigrationConfig(
        wp_url=args.wp_url or os.getenv('WP_URL', ''),
        wp_user=args.wp_user or os.getenv('WP_USER', ''),
        wp_app_password=args.wp_password or os.getenv('WP_APP_PASSWORD', ''),
        dry_run=args.dry_run,
        source_dir=args.source,
        limit=args.limit,
        default_category=args.default_category
    )

    if not args.dry_run and not config.wp_url:
        logger.error("WP_URL is required for actual migration")
        sys.exit(1)

    # Backup confirmation for actual migration
    if not args.dry_run:
        print("\n" + "=" * 60)
        print("IMPORTANT: WordPress Backup Reminder")
        print("=" * 60)
        print(f"Target: {config.wp_url}")
        print("\nBefore proceeding, ensure you have:")
        print("  1. Created a full WordPress backup (files + database)")
        print("  2. Tested backup restore procedure")
        print("\nBackup command (run on VPS):")
        print("  bash scripts/tools/wordpress_migration/wp_backup.sh")
        print("\nOr use UpdraftPlus plugin in WordPress admin.")
        print("=" * 60)

        confirm = input("\nHave you backed up WordPress? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("\nMigration cancelled. Please backup WordPress first.")
            sys.exit(0)

        print("\nProceeding with migration...\n")

    migrator = GrideaHtmlToWordPress(config)
    migrator.migrate_all(args.source)


if __name__ == '__main__':
    main()
