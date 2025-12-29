#!/usr/bin/env python3
"""
Generate 301 Redirect Rules for Jekyll/Gridea to WordPress Migration

Generates redirect rules for:
1. Yoast SEO plugin (CSV format)
2. Redirection plugin (CSV format)
3. Jekyll redirect-from plugin (YAML)
4. Nginx/Apache config

Usage:
    python generate_redirects.py --jekyll-posts _posts/ --output redirects/
    python generate_redirects.py --gridea-posts ../zhurong2020.github.io/post/ --output redirects/
"""

import os
import re
import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

import frontmatter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class RedirectRule:
    """Represents a redirect rule"""
    source_url: str
    target_url: str
    source_type: str  # 'jekyll' or 'gridea'
    title: str = ""


class RedirectGenerator:
    """Generate redirect rules for various formats"""

    def __init__(self, wp_base_url: str = "https://arong.eu.org"):
        self.wp_base_url = wp_base_url.rstrip('/')
        self.rules: List[RedirectRule] = []

        # Mapping from migration results (if available)
        self.migration_mapping: Dict[str, str] = {}

    def load_migration_results(self, results_file: Path):
        """Load mapping from migration results JSON"""
        if results_file.exists():
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
                for item in results:
                    if item.get('success'):
                        source = item.get('jekyll_file') or item.get('gridea_folder')
                        target = item.get('wp_url')
                        if source and target:
                            self.migration_mapping[source] = target
            logger.info(f"Loaded {len(self.migration_mapping)} mappings from {results_file}")

    def parse_jekyll_posts(self, posts_dir: str) -> List[RedirectRule]:
        """Parse Jekyll posts and generate redirect rules"""
        rules = []
        posts_path = Path(posts_dir)

        if not posts_path.exists():
            logger.error(f"Posts directory not found: {posts_dir}")
            return rules

        for md_file in posts_path.glob('*.md'):
            try:
                # Parse filename: YYYY-MM-DD-slug.md
                filename = md_file.stem
                match = re.match(r'^(\d{4})-(\d{2})-(\d{2})-(.+)$', filename)

                if not match:
                    logger.warning(f"Skipping non-standard filename: {filename}")
                    continue

                year, month, day, slug = match.groups()

                # Read front matter for title
                with open(md_file, 'r', encoding='utf-8') as f:
                    post = frontmatter.load(f)
                    title = post.get('title', slug)

                # Jekyll URL format (based on _config.yml permalink setting)
                # Current: /posts/:year/:month/:title/
                jekyll_url = f"/posts/{year}/{month}/{slug}/"

                # Alternative formats that might exist
                alt_urls = [
                    f"/workshop/posts/{year}/{month}/{slug}/",
                    f"/{year}/{month}/{day}/{slug}/",
                    f"/workshop/{year}/{month}/{day}/{slug}/"
                ]

                # WordPress target URL
                # Check if we have a mapping from migration
                wp_url = self.migration_mapping.get(str(md_file))
                if not wp_url:
                    # Default WordPress URL format
                    wp_url = f"{self.wp_base_url}/{year}/{month}/{day}/{slug}/"

                # Primary redirect
                rules.append(RedirectRule(
                    source_url=jekyll_url,
                    target_url=wp_url,
                    source_type='jekyll',
                    title=title
                ))

                # Alternative redirects
                for alt_url in alt_urls:
                    rules.append(RedirectRule(
                        source_url=alt_url,
                        target_url=wp_url,
                        source_type='jekyll',
                        title=title
                    ))

            except Exception as e:
                logger.error(f"Error processing {md_file}: {e}")

        logger.info(f"Generated {len(rules)} redirect rules from Jekyll posts")
        return rules

    def parse_gridea_posts(self, posts_dir: str) -> List[RedirectRule]:
        """Parse Gridea post folders and generate redirect rules"""
        rules = []
        posts_path = Path(posts_dir)

        if not posts_path.exists():
            logger.error(f"Posts directory not found: {posts_dir}")
            return rules

        for folder in posts_path.iterdir():
            if not folder.is_dir():
                continue

            folder_name = folder.name

            # Skip special folders
            if folder_name in ['about', 'images', 'styles']:
                continue

            # Gridea URL format
            gridea_url = f"/post/{folder_name}/"
            alt_url = f"/{folder_name}/"

            # WordPress target URL
            wp_url = self.migration_mapping.get(folder_name)
            if not wp_url:
                # Default: same slug
                wp_url = f"{self.wp_base_url}/post/{folder_name}/"

            rules.append(RedirectRule(
                source_url=gridea_url,
                target_url=wp_url,
                source_type='gridea',
                title=folder_name
            ))

        logger.info(f"Generated {len(rules)} redirect rules from Gridea posts")
        return rules

    def export_yoast_csv(self, output_file: Path):
        """Export redirects in Yoast SEO CSV format"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Origin,Target,Type\n")
            for rule in self.rules:
                f.write(f'"{rule.source_url}","{rule.target_url}",301\n')

        logger.info(f"Exported {len(self.rules)} rules to {output_file}")

    def export_redirection_csv(self, output_file: Path):
        """Export redirects for Redirection plugin (CSV format)"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("source,target,type,title\n")
            for rule in self.rules:
                f.write(f'"{rule.source_url}","{rule.target_url}",url,"{rule.title}"\n')

        logger.info(f"Exported {len(self.rules)} rules to {output_file}")

    def export_redirection_json(self, output_file: Path):
        """Export redirects for Redirection plugin (JSON format)"""
        data = {
            'redirects': [
                {
                    'source': rule.source_url,
                    'target': rule.target_url,
                    'type': 'url',
                    'code': 301,
                    'title': rule.title
                }
                for rule in self.rules
            ]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Exported {len(self.rules)} rules to {output_file}")

    def export_nginx_config(self, output_file: Path):
        """Export redirects as Nginx rewrite rules"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Nginx 301 Redirect Rules\n")
            f.write("# Add to your server block\n\n")

            for rule in self.rules:
                # Escape special regex characters
                source = rule.source_url.replace('.', r'\.')
                f.write(f"rewrite ^{source}$ {rule.target_url} permanent;\n")

        logger.info(f"Exported {len(self.rules)} rules to {output_file}")

    def export_apache_htaccess(self, output_file: Path):
        """Export redirects as Apache .htaccess rules"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Apache 301 Redirect Rules\n")
            f.write("# Add to your .htaccess file\n\n")
            f.write("RewriteEngine On\n\n")

            for rule in self.rules:
                source = rule.source_url.lstrip('/')
                f.write(f"Redirect 301 /{source} {rule.target_url}\n")

        logger.info(f"Exported {len(self.rules)} rules to {output_file}")

    def export_jekyll_redirects(self, output_dir: Path, jekyll_posts_dir: Path):
        """Generate Jekyll redirect-from front matter for each post"""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Group rules by source file
        redirects_by_file: Dict[str, List[str]] = {}

        for rule in self.rules:
            if rule.source_type == 'jekyll':
                # Find corresponding markdown file
                for md_file in jekyll_posts_dir.glob('*.md'):
                    if rule.title and rule.title in md_file.name:
                        if str(md_file) not in redirects_by_file:
                            redirects_by_file[str(md_file)] = []
                        redirects_by_file[str(md_file)].append(rule.target_url)
                        break

        # Generate YAML files with redirect instructions
        instructions_file = output_dir / 'jekyll_redirect_instructions.md'
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write("# Jekyll Redirect Configuration\n\n")
            f.write("Add the following to each post's front matter:\n\n")
            f.write("```yaml\n")
            f.write("redirect_to: https://arong.eu.org/path/to/post/\n")
            f.write("```\n\n")
            f.write("Or for multiple redirects:\n\n")
            f.write("```yaml\n")
            f.write("redirect_from:\n")
            f.write("  - /old-url-1/\n")
            f.write("  - /old-url-2/\n")
            f.write("```\n\n")
            f.write("## Per-file instructions:\n\n")

            for md_file, urls in redirects_by_file.items():
                f.write(f"### {Path(md_file).name}\n")
                f.write("```yaml\n")
                f.write(f"redirect_to: {urls[0] if urls else 'TBD'}\n")
                f.write("```\n\n")

        logger.info(f"Exported Jekyll redirect instructions to {instructions_file}")

    def export_all(self, output_dir: str, jekyll_posts_dir: Optional[str] = None):
        """Export all redirect formats"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self.export_yoast_csv(output_path / 'yoast_redirects.csv')
        self.export_redirection_csv(output_path / 'redirection_plugin.csv')
        self.export_redirection_json(output_path / 'redirection_plugin.json')
        self.export_nginx_config(output_path / 'nginx_redirects.conf')
        self.export_apache_htaccess(output_path / 'htaccess_redirects.txt')

        if jekyll_posts_dir:
            self.export_jekyll_redirects(output_path, Path(jekyll_posts_dir))

        # Export summary
        summary_file = output_path / 'redirect_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump({
                'total_rules': len(self.rules),
                'jekyll_rules': len([r for r in self.rules if r.source_type == 'jekyll']),
                'gridea_rules': len([r for r in self.rules if r.source_type == 'gridea']),
                'generated_at': datetime.now().isoformat(),
                'wp_base_url': self.wp_base_url
            }, f, indent=2)

        logger.info(f"\nAll formats exported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate 301 redirect rules for migration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate from Jekyll posts
    python generate_redirects.py --jekyll-posts _posts/ --output redirects/

    # Generate from Gridea posts
    python generate_redirects.py --gridea-posts ../zhurong2020.github.io/post/ --output redirects/

    # Generate from both
    python generate_redirects.py \\
        --jekyll-posts _posts/ \\
        --gridea-posts ../zhurong2020.github.io/post/ \\
        --output redirects/

    # Use migration results for accurate mappings
    python generate_redirects.py \\
        --jekyll-posts _posts/ \\
        --migration-results migration_results.json \\
        --output redirects/
        """
    )

    parser.add_argument(
        '--jekyll-posts',
        help='Path to Jekyll _posts/ directory'
    )

    parser.add_argument(
        '--gridea-posts',
        help='Path to Gridea post/ directory'
    )

    parser.add_argument(
        '--output', '-o',
        default='redirects/',
        help='Output directory for redirect files (default: redirects/)'
    )

    parser.add_argument(
        '--wp-url',
        default='https://arong.eu.org',
        help='WordPress site URL (default: https://arong.eu.org)'
    )

    parser.add_argument(
        '--migration-results',
        help='Path to migration_results.json for accurate URL mappings'
    )

    args = parser.parse_args()

    if not args.jekyll_posts and not args.gridea_posts:
        parser.error("At least one of --jekyll-posts or --gridea-posts is required")

    generator = RedirectGenerator(args.wp_url)

    # Load migration results if available
    if args.migration_results:
        generator.load_migration_results(Path(args.migration_results))

    # Parse posts and generate rules
    if args.jekyll_posts:
        generator.rules.extend(generator.parse_jekyll_posts(args.jekyll_posts))

    if args.gridea_posts:
        generator.rules.extend(generator.parse_gridea_posts(args.gridea_posts))

    # Export all formats
    generator.export_all(args.output, args.jekyll_posts)


if __name__ == '__main__':
    main()
