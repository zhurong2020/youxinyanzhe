#!/usr/bin/env python3
"""
Re-migrate Post from Jekyll Markdown to WordPress

Re-migrates a specific post from original Markdown source to WordPress,
updating the existing post with proper Gutenberg block format.

Usage:
    # Dry run (preview only)
    python remigrate_post.py --post-id 343 --source _posts/2025-12-27-protect-your-python-code-with-pyobfus.md --dry-run

    # Actual update
    python remigrate_post.py --post-id 343 --source _posts/2025-12-27-protect-your-python-code-with-pyobfus.md

Environment variables:
    WP_URL          - WordPress site URL
    WP_USER         - WordPress username
    WP_APP_PASSWORD - WordPress application password

Author: YouXin Workshop
Date: 2025-12-30
"""

import os
import sys
import re
import argparse
import logging
from pathlib import Path
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth
import frontmatter
import markdown

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gutenberg_converter import convert_html_to_gutenberg_with_stats, ConversionOptions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def convert_markdown_to_gutenberg(content: str) -> tuple:
    """
    Convert Markdown content directly to Gutenberg format.

    Returns:
        Tuple of (gutenberg_content, stats)
    """
    # === Pre-processing: Clean Jekyll/Liquid specific syntax ===

    # Remove Liquid template blocks
    content = re.sub(
        r'\{%\s*assign\s+investment_tags.*?\{%\s*endif\s*%\}',
        '', content, flags=re.DOTALL
    )
    content = re.sub(r'\{%\s*assign\s+[^%]*%\}', '', content)
    content = re.sub(r'\{%\s*for\s+[^%]*%\}.*?\{%\s*endfor\s*%\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\{%\s*if\s+[^%]*%\}.*?\{%\s*endif\s*%\}', '', content, flags=re.DOTALL)
    content = re.sub(r'\{%[^%]*%\}', '', content)
    content = re.sub(r'\{\{[^}]*\}\}', '', content)

    # Convert Kramdown link attributes
    kramdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)\{:target=["\']_blank["\']\}', content)
    content = re.sub(r'\{:target=["\']_blank["\']\}', '', content)

    # Protect LaTeX math formulas
    math_blocks = []
    def save_math(match):
        math_blocks.append(match.group(0))
        return f'%%MATH_BLOCK_{len(math_blocks)-1}%%'

    content = re.sub(r'\$\$[^$]+\$\$', save_math, content, flags=re.DOTALL)
    content = re.sub(r'\$[^$\n]+\$', save_math, content)

    # Protect ASCII art blocks
    ascii_art_blocks = []
    def save_ascii_art(match):
        ascii_art_blocks.append(match.group(0))
        return f'\n%%ASCII_ART_{len(ascii_art_blocks)-1}%%\n'

    content = re.sub(
        r'```[^\n]*\n((?:[^\n]*[├─│└┘┐┌┬┴┼╔╗╚╝║═]+[^\n]*\n)+)```',
        save_ascii_art, content
    )
    content = re.sub(
        r'((?:^[^\n]*[├─│└┘┐┌┬┴┼╔╗╚╝║═]+[^\n]*$\n?){3,})',
        save_ascii_art, content, flags=re.MULTILINE
    )

    # === Convert Markdown to HTML ===
    # Use fenced_code (NOT codehilite) to preserve language info
    md = markdown.Markdown(extensions=[
        'tables',
        'fenced_code',  # Preserves language info as class="language-xxx"
        'toc',
    ])

    html = md.convert(content)

    # === Post-processing ===

    # Restore LaTeX math blocks
    for i, math in enumerate(math_blocks):
        html = html.replace(f'%%MATH_BLOCK_{i}%%', math)

    # Restore ASCII art blocks with proper styling for CJK alignment
    for i, art in enumerate(ascii_art_blocks):
        # Use a font stack that supports equal-width CJK characters
        # Also set letter-spacing and line-height for better alignment
        pre_block = f'''<div class="ascii-art-container" style="overflow-x: auto; background: #f8f9fa; padding: 1.5em; border-radius: 8px; margin: 1em 0; border: 1px solid #e9ecef;">
<pre style="font-family: 'Sarasa Mono SC', 'Noto Sans Mono CJK SC', 'Source Han Mono SC', 'Microsoft YaHei Mono', 'Courier New', monospace; font-size: 14px; line-height: 1.5; white-space: pre; margin: 0; letter-spacing: 0;">{art}</pre>
</div>'''
        html = html.replace(f'<p>%%ASCII_ART_{i}%%</p>', pre_block)
        html = html.replace(f'%%ASCII_ART_{i}%%', pre_block)

    # Fix more tag
    html = html.replace('<!-- more -->', '<!--more-->')

    # Add target="_blank" to external links
    for link_text, link_url in kramdown_links:
        old_link = f'<a href="{link_url}">{link_text}</a>'
        new_link = f'<a href="{link_url}" target="_blank" rel="noopener noreferrer">{link_text}</a>'
        html = html.replace(old_link, new_link)

    # Make images responsive
    html = re.sub(
        r'<img\s+([^>]*?)(/?)>',
        r'<img \1 style="max-width: 100%; height: auto;" \2>',
        html
    )

    # Note: Do NOT add inline styles to tables - WordPress Gutenberg handles table styling
    # Adding custom styles causes "unexpected content" errors in the block editor

    # Clean up empty paragraphs
    html = re.sub(r'<p>\s*</p>', '', html)

    # Track if we have math content
    has_math = len(math_blocks) > 0

    # === Convert to Gutenberg format ===
    options = ConversionOptions(
        preserve_inline_styles=True,
        add_wp_classes=True,
        wrap_images_in_figure=True,
        preserve_code_language=True,
        convert_codehilite=True,
        handle_mathjax=False,  # We'll handle MathJax manually
        preserve_more_tag=True
    )

    gutenberg_content, stats = convert_html_to_gutenberg_with_stats(html, options)

    # Note: MathJax is now handled by mu-plugin (mathjax-support.php)
    # No need to embed script in each post

    return gutenberg_content, stats


def update_wordpress_post(post_id: int, content: str, config: dict, dry_run: bool = False) -> bool:
    """Update an existing WordPress post with new content."""

    if dry_run:
        logger.info(f"[DRY RUN] Would update post {post_id}")
        logger.info(f"Content preview (first 1000 chars):\n{content[:1000]}...")
        return True

    session = requests.Session()
    session.auth = HTTPBasicAuth(config['wp_user'], config['wp_app_password'])

    api_url = f"{config['wp_url']}/wp-json/wp/v2/posts/{post_id}"

    try:
        response = session.post(api_url, json={'content': content})

        if response.status_code == 200:
            logger.info(f"Successfully updated post {post_id}")
            return True
        else:
            logger.error(f"Failed to update post {post_id}: HTTP {response.status_code}")
            logger.error(f"Response: {response.text[:500]}")
            return False

    except Exception as e:
        logger.error(f"Error updating post {post_id}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Re-migrate a Jekyll post to WordPress with Gutenberg format'
    )

    parser.add_argument('--post-id', type=int, required=True,
                       help='WordPress post ID to update')
    parser.add_argument('--source', type=str, required=True,
                       help='Path to Jekyll Markdown source file')
    parser.add_argument('--dry-run', '-n', action='store_true',
                       help='Preview changes without updating')
    parser.add_argument('--wp-url', default=os.getenv('WP_URL', 'https://www.arong.eu.org'))
    parser.add_argument('--wp-user', default=os.getenv('WP_USER'))
    parser.add_argument('--wp-password', default=os.getenv('WP_APP_PASSWORD'))

    args = parser.parse_args()

    if not args.wp_user or not args.wp_password:
        parser.error("WordPress credentials required (WP_USER, WP_APP_PASSWORD)")

    source_path = Path(args.source)
    if not source_path.exists():
        logger.error(f"Source file not found: {source_path}")
        sys.exit(1)

    # Read Markdown source
    logger.info(f"Reading source file: {source_path}")
    with open(source_path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)

    logger.info(f"Title: {post.get('title', 'Unknown')}")
    logger.info(f"Original Markdown length: {len(post.content)} chars")

    # Convert to Gutenberg
    logger.info("Converting to Gutenberg format...")
    gutenberg_content, stats = convert_markdown_to_gutenberg(post.content)

    logger.info(f"Conversion stats: {stats}")
    logger.info(f"Gutenberg content length: {len(gutenberg_content)} chars")

    # Check for code language attributes
    lang_matches = re.findall(r'<!-- wp:code \{"language":\s*"([^"]+)"\}', gutenberg_content)
    if lang_matches:
        logger.info(f"Code languages detected: {set(lang_matches)}")

    # Update WordPress
    config = {
        'wp_url': args.wp_url,
        'wp_user': args.wp_user,
        'wp_app_password': args.wp_password
    }

    success = update_wordpress_post(
        args.post_id,
        gutenberg_content,
        config,
        dry_run=args.dry_run
    )

    if success:
        logger.info("Migration completed successfully!")
        if args.dry_run:
            logger.info("Run without --dry-run to apply changes")
    else:
        logger.error("Migration failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
