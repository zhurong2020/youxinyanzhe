#!/usr/bin/env python3
"""
Fix Existing WordPress Posts to Gutenberg Format

Updates already-migrated posts from pure HTML to Gutenberg block format.

Usage:
    # Preview changes (dry run)
    python fix_existing_posts.py --dry-run --post-id 343

    # Fix specific posts
    python fix_existing_posts.py --post-id 343 --post-id 336

    # Fix all posts needing conversion
    python fix_existing_posts.py --all --dry-run
    python fix_existing_posts.py --all

Environment variables:
    WP_URL          - WordPress site URL (default: https://www.arong.eu.org)
    WP_USER         - WordPress username
    WP_APP_PASSWORD - WordPress application password

Author: YouXin Workshop
Date: 2025-12-30
"""

import os
import sys
import json
import argparse
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gutenberg_converter import (
    convert_html_to_gutenberg_with_stats,
    ConversionOptions,
    ConversionStats
)

# Configure logging
log_filename = f'gutenberg_fix_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_filename, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class FixConfig:
    """Configuration for fixing posts"""
    wp_url: str
    wp_user: str
    wp_app_password: str
    dry_run: bool = False
    post_ids: Optional[List[int]] = None
    fix_all: bool = False
    show_preview: bool = True
    preview_length: int = 500


class GutenbergFixer:
    """Updates existing WordPress posts to Gutenberg format"""

    def __init__(self, config: FixConfig):
        self.config = config
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(config.wp_user, config.wp_app_password)
        self.api_base = f"{config.wp_url.rstrip('/')}/wp-json/wp/v2"

        self.stats = {
            'total': 0,
            'updated': 0,
            'skipped': 0,
            'already_gutenberg': 0,
            'failed': 0
        }

        self.conversion_options = ConversionOptions(
            preserve_inline_styles=True,
            add_wp_classes=True,
            wrap_images_in_figure=True,
            preserve_code_language=True,
            convert_codehilite=True,
            handle_mathjax=True,
            preserve_more_tag=True
        )

    def get_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Fetch a single post by ID with raw content"""
        try:
            response = self.session.get(
                f"{self.api_base}/posts/{post_id}",
                params={'context': 'edit'}
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Failed to fetch post {post_id}: HTTP {response.status_code}")
            logger.error(f"Response: {response.text[:500]}")
        except Exception as e:
            logger.error(f"Error fetching post {post_id}: {e}")
        return None

    def get_all_posts(self) -> List[Dict[str, Any]]:
        """Fetch all posts that need Gutenberg conversion"""
        posts = []
        page = 1
        per_page = 100

        logger.info("Scanning all posts...")

        while True:
            try:
                response = self.session.get(
                    f"{self.api_base}/posts",
                    params={
                        'per_page': per_page,
                        'page': page,
                        'context': 'edit',
                        'status': 'publish,draft,pending,private'
                    }
                )

                if response.status_code != 200:
                    if response.status_code == 400:
                        # No more pages
                        break
                    logger.error(f"API error: {response.status_code}")
                    break

                batch = response.json()
                if not batch:
                    break

                # Filter: only posts without Gutenberg blocks
                for post in batch:
                    content = post.get('content', {}).get('raw', '')
                    if self._needs_conversion(content):
                        posts.append(post)
                    else:
                        logger.debug(f"Skipping post {post['id']}: already has Gutenberg blocks")

                page += 1

            except Exception as e:
                logger.error(f"Error fetching posts page {page}: {e}")
                break

        return posts

    def _needs_conversion(self, content: str) -> bool:
        """Check if content needs Gutenberg conversion"""
        if not content:
            return False

        # Already has Gutenberg blocks
        if content.strip().startswith('<!-- wp:'):
            return False

        # Has HTML content that needs conversion
        if '<p>' in content or '<h' in content or '<div' in content:
            return True

        return False

    def _is_already_gutenberg(self, content: str) -> bool:
        """Check if content is already in Gutenberg format"""
        return content.strip().startswith('<!-- wp:')

    def update_post(self, post_id: int, new_content: str) -> bool:
        """Update post content via REST API"""
        if self.config.dry_run:
            logger.info(f"  [DRY RUN] Would update post {post_id}")
            if self.config.show_preview:
                preview = new_content[:self.config.preview_length]
                logger.info(f"  Preview:\n{preview}...")
            return True

        try:
            response = self.session.post(
                f"{self.api_base}/posts/{post_id}",
                json={'content': new_content}
            )

            if response.status_code == 200:
                logger.info(f"  Successfully updated post {post_id}")
                return True
            else:
                logger.error(f"  Failed to update post {post_id}: HTTP {response.status_code}")
                logger.error(f"  Response: {response.text[:500]}")

        except Exception as e:
            logger.error(f"  Error updating post {post_id}: {e}")

        return False

    def fix_post(self, post: Dict[str, Any]) -> bool:
        """Convert a single post to Gutenberg format"""
        post_id = post['id']
        title = post.get('title', {}).get('rendered', f'Post {post_id}')
        content = post.get('content', {}).get('raw', '')

        logger.info(f"\nProcessing: {title} (ID: {post_id})")
        logger.info(f"  Original content length: {len(content)} chars")

        # Check if already converted
        if self._is_already_gutenberg(content):
            logger.info(f"  Skipping: already has Gutenberg blocks")
            self.stats['already_gutenberg'] += 1
            return True

        # Check if needs conversion
        if not self._needs_conversion(content):
            logger.info(f"  Skipping: no HTML content to convert")
            self.stats['skipped'] += 1
            return True

        # Convert to Gutenberg
        try:
            gutenberg_content, conv_stats = convert_html_to_gutenberg_with_stats(
                content,
                self.conversion_options
            )

            logger.info(f"  Conversion stats: {conv_stats}")
            logger.info(f"  New content length: {len(gutenberg_content)} chars")

            if self.update_post(post_id, gutenberg_content):
                self.stats['updated'] += 1
                return True
            else:
                self.stats['failed'] += 1
                return False

        except Exception as e:
            logger.error(f"  Conversion error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.stats['failed'] += 1
            return False

    def run(self):
        """Execute the fixing process"""
        logger.info("=" * 60)
        logger.info("WordPress Gutenberg Format Fixer")
        logger.info("=" * 60)
        logger.info(f"Target: {self.config.wp_url}")
        logger.info(f"Mode: {'DRY RUN' if self.config.dry_run else 'LIVE UPDATE'}")
        logger.info("=" * 60)

        if self.config.post_ids:
            # Fix specific posts
            logger.info(f"Processing {len(self.config.post_ids)} specified post(s)")
            for post_id in self.config.post_ids:
                post = self.get_post(post_id)
                if post:
                    self.stats['total'] += 1
                    self.fix_post(post)
                else:
                    logger.error(f"Could not fetch post {post_id}")
                    self.stats['failed'] += 1

        elif self.config.fix_all:
            # Fix all posts needing conversion
            posts = self.get_all_posts()
            self.stats['total'] = len(posts)
            logger.info(f"\nFound {len(posts)} post(s) needing conversion")

            for i, post in enumerate(posts, 1):
                logger.info(f"\n[{i}/{len(posts)}]")
                self.fix_post(post)

        self.print_summary()

    def print_summary(self):
        """Print final statistics"""
        logger.info("\n" + "=" * 60)
        logger.info("GUTENBERG FIX SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total processed:    {self.stats['total']}")
        logger.info(f"Updated:            {self.stats['updated']}")
        logger.info(f"Already Gutenberg:  {self.stats['already_gutenberg']}")
        logger.info(f"Skipped:            {self.stats['skipped']}")
        logger.info(f"Failed:             {self.stats['failed']}")

        if self.config.dry_run:
            logger.info("\n[DRY RUN MODE] No actual changes were made")
            logger.info("Run without --dry-run to apply changes")

        logger.info(f"\nLog saved to: {log_filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Fix existing WordPress posts to Gutenberg format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Preview changes for specific posts
    python fix_existing_posts.py --dry-run --post-id 343 --post-id 336

    # Apply changes to specific posts
    python fix_existing_posts.py --post-id 343 --post-id 336

    # Preview all posts needing conversion
    python fix_existing_posts.py --all --dry-run

    # Fix all posts
    python fix_existing_posts.py --all

Environment variables:
    WP_URL, WP_USER, WP_APP_PASSWORD
        """
    )

    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Preview changes without updating'
    )
    parser.add_argument(
        '--post-id',
        type=int,
        action='append',
        dest='post_ids',
        help='Specific post ID(s) to fix (can be repeated)'
    )
    parser.add_argument(
        '--all',
        dest='fix_all',
        action='store_true',
        help='Fix all posts needing conversion'
    )
    parser.add_argument(
        '--no-preview',
        action='store_true',
        help='Do not show content preview in dry-run mode'
    )
    parser.add_argument(
        '--preview-length',
        type=int,
        default=500,
        help='Length of content preview (default: 500)'
    )
    parser.add_argument(
        '--wp-url',
        default=os.getenv('WP_URL', 'https://www.arong.eu.org'),
        help='WordPress site URL'
    )
    parser.add_argument(
        '--wp-user',
        default=os.getenv('WP_USER'),
        help='WordPress username'
    )
    parser.add_argument(
        '--wp-password',
        default=os.getenv('WP_APP_PASSWORD'),
        help='WordPress application password'
    )

    args = parser.parse_args()

    # Validation
    if not args.post_ids and not args.fix_all:
        parser.error("Specify --post-id or --all")

    if not args.wp_user or not args.wp_password:
        parser.error("WordPress credentials required (WP_USER, WP_APP_PASSWORD)")

    config = FixConfig(
        wp_url=args.wp_url,
        wp_user=args.wp_user,
        wp_app_password=args.wp_password,
        dry_run=args.dry_run,
        post_ids=args.post_ids,
        fix_all=args.fix_all,
        show_preview=not args.no_preview,
        preview_length=args.preview_length
    )

    fixer = GutenbergFixer(config)
    fixer.run()


if __name__ == '__main__':
    main()
