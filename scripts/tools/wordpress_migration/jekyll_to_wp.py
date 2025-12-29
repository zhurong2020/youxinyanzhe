#!/usr/bin/env python3
"""
Jekyll to WordPress Migration Script

Migrates Jekyll markdown posts to WordPress via REST API.
Handles front matter parsing, category/tag mapping, and featured images.

Usage:
    python jekyll_to_wp.py --source _posts/ --dry-run
    python jekyll_to_wp.py --source _posts/ --batch-size 10
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

import requests
import frontmatter
import markdown

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('migration.log', encoding='utf-8')
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
    batch_size: int = 10
    source_dir: str = "_posts/"
    limit: Optional[int] = None

    # Category mapping: Jekyll category name -> WordPress category ID
    category_map: Dict[str, int] = field(default_factory=dict)

    # Tag cache
    tag_cache: Dict[str, int] = field(default_factory=dict)


@dataclass
class JekyllPost:
    """Represents a parsed Jekyll post"""
    file_path: Path
    title: str
    date: datetime
    content: str
    excerpt: str = ""
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    header_image: str = ""
    teaser_image: str = ""
    member_tier: str = ""
    layout: str = "single"
    last_modified: Optional[datetime] = None
    estimated_reading_time: str = ""
    raw_front_matter: Dict[str, Any] = field(default_factory=dict)


class JekyllToWordPress:
    """Main migration class"""

    def __init__(self, config: MigrationConfig):
        self.config = config
        self.session = requests.Session()

        if config.wp_user and config.wp_app_password:
            self.session.auth = (config.wp_user, config.wp_app_password)

        self.api_base = f"{config.wp_url}/wp-json/wp/v2"
        self.acf_api = f"{config.wp_url}/wp-json/acf/v3"

        # Statistics
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

        # Migration results
        self.results: List[Dict[str, Any]] = []

    def parse_jekyll_post(self, file_path: Path) -> Optional[JekyllPost]:
        """Parse a Jekyll markdown file and extract all metadata"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)

            # Extract basic fields
            title = post.get('title', file_path.stem)

            # Handle date - can be string or datetime
            date_raw = post.get('date', datetime.now())
            if isinstance(date_raw, str):
                # Try parsing common formats
                for fmt in ['%Y-%m-%d %H:%M:%S %z', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d']:
                    try:
                        date = datetime.strptime(date_raw.split('+')[0].strip(), fmt.split(' %z')[0])
                        break
                    except ValueError:
                        continue
                else:
                    date = datetime.now()
            else:
                date = date_raw

            # Handle categories (can be string or list)
            categories_raw = post.get('categories', [])
            if isinstance(categories_raw, str):
                categories = [categories_raw]
            else:
                categories = list(categories_raw) if categories_raw else []

            # Handle tags
            tags_raw = post.get('tags', [])
            if isinstance(tags_raw, str):
                tags = [tags_raw]
            else:
                tags = list(tags_raw) if tags_raw else []

            # Handle header images
            header = post.get('header', {})
            header_image = ""
            teaser_image = ""
            if isinstance(header, dict):
                header_image = header.get('overlay_image', '')
                teaser_image = header.get('teaser', '')

            # Handle last_modified_at
            last_modified = None
            last_mod_raw = post.get('last_modified_at', '')
            if last_mod_raw:
                if isinstance(last_mod_raw, str):
                    try:
                        last_modified = datetime.strptime(
                            last_mod_raw.split('+')[0].strip().replace("'", ""),
                            '%Y-%m-%d %H:%M:%S'
                        )
                    except ValueError:
                        pass
                elif isinstance(last_mod_raw, datetime):
                    last_modified = last_mod_raw

            return JekyllPost(
                file_path=file_path,
                title=title,
                date=date,
                content=post.content,
                excerpt=post.get('excerpt', ''),
                categories=categories,
                tags=tags,
                header_image=header_image,
                teaser_image=teaser_image,
                member_tier=post.get('member_tier', ''),
                layout=post.get('layout', 'single'),
                last_modified=last_modified,
                estimated_reading_time=post.get('estimated_reading_time', ''),
                raw_front_matter=dict(post.metadata)
            )

        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return None

    def get_or_create_category(self, category_name: str) -> Optional[int]:
        """Get category ID or create if not exists"""
        # Check cache first
        if category_name in self.config.category_map:
            return self.config.category_map[category_name]

        # Map Chinese category names to slugs
        category_slugs = {
            '认知升级': 'cognitive-upgrade',
            '技术赋能': 'tech-empowerment',
            '全球视野': 'global-perspective',
            '投资理财': 'investment-finance',
        }

        slug = category_slugs.get(category_name, category_name.lower().replace(' ', '-'))

        if self.config.dry_run:
            logger.info(f"  [DRY RUN] Would look up/create category: {category_name} (slug: {slug})")
            return None

        try:
            # Search for existing category
            response = self.session.get(
                f"{self.api_base}/categories",
                params={'slug': slug, 'per_page': 1}
            )

            if response.status_code == 200 and response.json():
                cat_id = response.json()[0]['id']
                self.config.category_map[category_name] = cat_id
                return cat_id

            # Create new category
            response = self.session.post(
                f"{self.api_base}/categories",
                json={'name': category_name, 'slug': slug}
            )

            if response.status_code == 201:
                cat_id = response.json()['id']
                self.config.category_map[category_name] = cat_id
                logger.info(f"  Created category: {category_name} (ID: {cat_id})")
                return cat_id

        except Exception as e:
            logger.error(f"  Failed to get/create category {category_name}: {e}")

        return None

    def get_or_create_tag(self, tag_name: str) -> Optional[int]:
        """Get tag ID or create if not exists"""
        if tag_name in self.config.tag_cache:
            return self.config.tag_cache[tag_name]

        if self.config.dry_run:
            logger.info(f"  [DRY RUN] Would look up/create tag: {tag_name}")
            return None

        try:
            # Search for existing tag
            response = self.session.get(
                f"{self.api_base}/tags",
                params={'search': tag_name, 'per_page': 1}
            )

            if response.status_code == 200 and response.json():
                # Check for exact match
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
                logger.info(f"  Created tag: {tag_name} (ID: {tag_id})")
                return tag_id

        except Exception as e:
            logger.error(f"  Failed to get/create tag {tag_name}: {e}")

        return None

    def upload_media(self, image_url: str, title: str = "") -> Optional[int]:
        """Upload image to WordPress media library or return existing media ID"""
        if not image_url:
            return None

        if self.config.dry_run:
            logger.info(f"  [DRY RUN] Would upload/reference image: {image_url[:50]}...")
            return None

        # If it's an OneDrive URL, we can try to keep it as-is
        # WordPress will embed external images
        if 'onedrive' in image_url.lower() or '1drv.ms' in image_url.lower():
            logger.info(f"  OneDrive image detected, will embed directly: {image_url[:50]}...")
            return None  # Use URL directly in content

        try:
            # Download image
            response = requests.get(image_url, timeout=30)
            if response.status_code != 200:
                logger.warning(f"  Failed to download image: {image_url}")
                return None

            # Determine filename and content type
            filename = image_url.split('/')[-1].split('?')[0]
            if not filename or '.' not in filename:
                filename = f"image_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"

            content_type = response.headers.get('content-type', 'image/jpeg')

            # Upload to WordPress
            upload_response = self.session.post(
                f"{self.api_base}/media",
                files={'file': (filename, response.content, content_type)},
                data={'title': title or filename}
            )

            if upload_response.status_code == 201:
                media_id = upload_response.json()['id']
                logger.info(f"  Uploaded image: {filename} (ID: {media_id})")
                return media_id
            else:
                logger.warning(f"  Failed to upload image: {upload_response.status_code}")

        except Exception as e:
            logger.error(f"  Failed to upload image {image_url}: {e}")

        return None

    def convert_markdown_to_html(self, content: str) -> str:
        """Convert Markdown content to HTML for WordPress"""
        # Configure markdown with extensions
        md = markdown.Markdown(extensions=[
            'tables',
            'fenced_code',
            'codehilite',
            'toc',
            'nl2br'
        ])

        html = md.convert(content)

        # Clean up some common issues
        # Remove <!-- more --> marker (WordPress uses its own)
        html = html.replace('<!-- more -->', '<!--more-->')

        return html

    def create_wp_post(self, post: JekyllPost) -> Optional[Dict[str, Any]]:
        """Create a WordPress post from a Jekyll post"""
        logger.info(f"Processing: {post.title}")

        # Get category IDs
        category_ids = []
        for cat in post.categories:
            cat_id = self.get_or_create_category(cat)
            if cat_id:
                category_ids.append(cat_id)

        # Get tag IDs
        tag_ids = []
        for tag in post.tags:
            tag_id = self.get_or_create_tag(tag)
            if tag_id:
                tag_ids.append(tag_id)

        # Handle featured image
        featured_media_id = None
        if post.header_image:
            featured_media_id = self.upload_media(post.header_image, post.title)

        # Convert content to HTML
        html_content = self.convert_markdown_to_html(post.content)

        # Prepare post data
        post_data = {
            'title': post.title,
            'content': html_content,
            'excerpt': post.excerpt,
            'status': 'publish',
            'date': post.date.isoformat() if post.date else None,
            'categories': category_ids if category_ids else [],
            'tags': tag_ids if tag_ids else [],
        }

        if featured_media_id:
            post_data['featured_media'] = featured_media_id

        # Handle modified date
        if post.last_modified:
            post_data['modified'] = post.last_modified.isoformat()

        if self.config.dry_run:
            logger.info(f"  [DRY RUN] Would create post:")
            logger.info(f"    Title: {post.title}")
            logger.info(f"    Date: {post.date}")
            logger.info(f"    Categories: {post.categories}")
            logger.info(f"    Tags: {post.tags}")
            logger.info(f"    Member Tier: {post.member_tier or 'None'}")
            logger.info(f"    Content length: {len(post.content)} chars")
            return {'dry_run': True, 'title': post.title}

        try:
            response = self.session.post(
                f"{self.api_base}/posts",
                json=post_data
            )

            if response.status_code == 201:
                result = response.json()
                wp_post_id = result['id']
                wp_url = result.get('link', '')

                logger.info(f"  Created post ID: {wp_post_id}")
                logger.info(f"  URL: {wp_url}")

                # Update ACF fields if member_tier exists
                if post.member_tier:
                    self.update_acf_fields(wp_post_id, post)

                return {
                    'success': True,
                    'wp_id': wp_post_id,
                    'wp_url': wp_url,
                    'jekyll_file': str(post.file_path),
                    'title': post.title
                }
            else:
                logger.error(f"  Failed to create post: {response.status_code}")
                logger.error(f"  Response: {response.text[:500]}")
                return {'success': False, 'error': response.text}

        except Exception as e:
            logger.error(f"  Exception creating post: {e}")
            return {'success': False, 'error': str(e)}

    def update_acf_fields(self, post_id: int, post: JekyllPost):
        """Update ACF custom fields for a post"""
        if self.config.dry_run:
            logger.info(f"  [DRY RUN] Would update ACF fields for post {post_id}")
            return

        acf_data = {}

        if post.member_tier:
            acf_data['member_tier'] = post.member_tier

        if post.estimated_reading_time:
            acf_data['estimated_reading_time'] = post.estimated_reading_time

        if not acf_data:
            return

        try:
            # Try ACF REST API first
            response = self.session.post(
                f"{self.acf_api}/posts/{post_id}",
                json={'acf': acf_data}
            )

            if response.status_code in [200, 201]:
                logger.info(f"  Updated ACF fields: {list(acf_data.keys())}")
            else:
                # Fallback to standard meta update
                for key, value in acf_data.items():
                    self.session.post(
                        f"{self.api_base}/posts/{post_id}",
                        json={'meta': {key: value}}
                    )
                logger.info(f"  Updated meta fields: {list(acf_data.keys())}")

        except Exception as e:
            logger.warning(f"  Failed to update ACF fields: {e}")

    def find_posts(self, source_dir: str) -> List[Path]:
        """Find all Jekyll markdown posts in the source directory"""
        source_path = Path(source_dir)

        if not source_path.exists():
            logger.error(f"Source directory not found: {source_dir}")
            return []

        # Find all .md files
        posts = list(source_path.glob('*.md'))

        # Sort by date (filename starts with YYYY-MM-DD)
        posts.sort(key=lambda p: p.name)

        return posts

    def migrate_all(self, source_dir: str):
        """Migrate all posts from source directory"""
        posts = self.find_posts(source_dir)

        if not posts:
            logger.warning("No posts found to migrate")
            return

        # Apply limit if specified
        if self.config.limit:
            posts = posts[:self.config.limit]

        self.stats['total'] = len(posts)
        logger.info(f"Found {len(posts)} posts to migrate")

        for i, post_path in enumerate(posts, 1):
            logger.info(f"\n[{i}/{len(posts)}] Processing: {post_path.name}")

            # Parse Jekyll post
            post = self.parse_jekyll_post(post_path)
            if not post:
                self.stats['failed'] += 1
                continue

            # Create WordPress post
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
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total posts: {self.stats['total']}")
        logger.info(f"Successful:  {self.stats['success']}")
        logger.info(f"Failed:      {self.stats['failed']}")
        logger.info(f"Skipped:     {self.stats['skipped']}")

        if self.config.dry_run:
            logger.info("\n[DRY RUN MODE] No actual changes were made")

        # Save results to JSON
        results_file = Path('migration_results.json')
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"\nResults saved to: {results_file}")


def load_config_from_env() -> MigrationConfig:
    """Load configuration from environment variables"""
    return MigrationConfig(
        wp_url=os.getenv('WP_URL', ''),
        wp_user=os.getenv('WP_USER', ''),
        wp_app_password=os.getenv('WP_APP_PASSWORD', ''),
    )


def main():
    parser = argparse.ArgumentParser(
        description='Migrate Jekyll posts to WordPress',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Dry run to preview migration
    python jekyll_to_wp.py --source _posts/ --dry-run

    # Migrate first 5 posts for testing
    python jekyll_to_wp.py --source _posts/ --limit 5

    # Full migration with batch processing
    python jekyll_to_wp.py --source _posts/ --batch-size 10

Environment Variables:
    WP_URL          WordPress site URL (e.g., https://arong.eu.org)
    WP_USER         WordPress username
    WP_APP_PASSWORD WordPress application password
        """
    )

    parser.add_argument(
        '--source', '-s',
        default='_posts/',
        help='Source directory containing Jekyll posts (default: _posts/)'
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
        '--batch-size', '-b',
        type=int,
        default=10,
        help='Number of posts to process in each batch (default: 10)'
    )

    parser.add_argument(
        '--wp-url',
        help='WordPress site URL (overrides WP_URL env var)'
    )

    parser.add_argument(
        '--wp-user',
        help='WordPress username (overrides WP_USER env var)'
    )

    parser.add_argument(
        '--wp-password',
        help='WordPress app password (overrides WP_APP_PASSWORD env var)'
    )

    args = parser.parse_args()

    # Load config
    config = load_config_from_env()

    # Override with command line args
    if args.wp_url:
        config.wp_url = args.wp_url
    if args.wp_user:
        config.wp_user = args.wp_user
    if args.wp_password:
        config.wp_app_password = args.wp_password

    config.dry_run = args.dry_run
    config.batch_size = args.batch_size
    config.source_dir = args.source
    config.limit = args.limit

    # Validate config (skip for dry run)
    if not args.dry_run:
        if not config.wp_url:
            logger.error("WP_URL is required. Set via --wp-url or WP_URL env var")
            sys.exit(1)
        if not config.wp_user or not config.wp_app_password:
            logger.warning("WordPress credentials not set. Some operations may fail.")

        # Backup confirmation
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
            print("Run: ssh arong-vps 'bash -s' < scripts/tools/wordpress_migration/wp_backup.sh")
            sys.exit(0)

        print("\nProceeding with migration...\n")

    # Run migration
    migrator = JekyllToWordPress(config)
    migrator.migrate_all(args.source)


if __name__ == '__main__':
    main()
