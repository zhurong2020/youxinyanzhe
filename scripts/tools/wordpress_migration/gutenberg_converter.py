#!/usr/bin/env python3
"""
Gutenberg Block Converter

Converts pure HTML content to WordPress Gutenberg block format.

Usage:
    from gutenberg_converter import convert_html_to_gutenberg

    html = "<h2>Title</h2><p>Content</p>"
    gutenberg = convert_html_to_gutenberg(html)

Author: YouXin Workshop
Date: 2025-12-30
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString

logger = logging.getLogger(__name__)


@dataclass
class ConversionStats:
    """Statistics for conversion process"""
    paragraphs: int = 0
    headings: int = 0
    code_blocks: int = 0
    images: int = 0
    lists: int = 0
    tables: int = 0
    quotes: int = 0
    separators: int = 0
    html_blocks: int = 0
    preserved_inline: int = 0

    def __str__(self) -> str:
        return (
            f"Conversion Stats: "
            f"paragraphs={self.paragraphs}, headings={self.headings}, "
            f"code_blocks={self.code_blocks}, images={self.images}, "
            f"lists={self.lists}, tables={self.tables}, "
            f"quotes={self.quotes}, separators={self.separators}, "
            f"html_blocks={self.html_blocks}"
        )


@dataclass
class ConversionOptions:
    """Configuration options for conversion"""
    preserve_inline_styles: bool = True
    add_wp_classes: bool = True
    wrap_images_in_figure: bool = True
    preserve_code_language: bool = True
    convert_codehilite: bool = True
    handle_mathjax: bool = True
    preserve_more_tag: bool = True


class GutenbergConverter:
    """
    Converts HTML content to WordPress Gutenberg block format.

    Uses a sequential parsing strategy to handle top-level elements
    while preserving nested inline content.
    """

    # Block-level elements that become Gutenberg blocks
    BLOCK_ELEMENTS = {
        'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'pre', 'ul', 'ol', 'table', 'blockquote', 'hr', 'figure',
        'div', 'script', 'style'
    }

    # Inline elements preserved within blocks
    INLINE_ELEMENTS = {
        'a', 'strong', 'b', 'em', 'i', 'code', 'span',
        'sup', 'sub', 'mark', 'del', 's', 'u', 'br'
    }

    def __init__(self, options: Optional[ConversionOptions] = None):
        self.options = options or ConversionOptions()
        self.stats = ConversionStats()

    def convert(self, html: str) -> Tuple[str, ConversionStats]:
        """
        Convert HTML to Gutenberg block format.

        Args:
            html: Raw HTML content

        Returns:
            Tuple of (converted content, statistics)
        """
        self.stats = ConversionStats()

        if not html or not html.strip():
            return '', self.stats

        # Pre-process: Protect special content
        html, protected = self._protect_special_content(html)

        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')

        # Process top-level elements
        blocks = []
        for element in soup.children:
            if isinstance(element, NavigableString):
                text = str(element).strip()
                if text and text != '<!--more-->':
                    # Wrap orphan text in paragraph
                    block = self._create_paragraph_block(text)
                    if block:
                        blocks.append(block)
                elif text == '<!--more-->':
                    # Preserve WordPress more tag
                    blocks.append('<!--more-->')
            elif isinstance(element, Tag):
                block = self._convert_element(element)
                if block:
                    blocks.append(block)

        # Join blocks with double newlines
        result = '\n\n'.join(filter(None, blocks))

        # Restore protected content
        result = self._restore_special_content(result, protected)

        return result, self.stats

    def _protect_special_content(self, html: str) -> Tuple[str, Dict[str, str]]:
        """Protect content that shouldn't be parsed (MathJax, LaTeX, etc.)"""
        protected: Dict[str, str] = {}
        counter = 0

        # Protect MathJax scripts
        if self.options.handle_mathjax:
            def save_mathjax(match: re.Match) -> str:
                nonlocal counter
                key = f'%%PROTECTED_MATHJAX_{counter}%%'
                protected[key] = match.group(0)
                counter += 1
                return key

            # Script tags with MathJax content
            html = re.sub(
                r'<script[^>]*>.*?MathJax.*?</script>',
                save_mathjax, html, flags=re.DOTALL | re.IGNORECASE
            )

        # Protect <!--more--> tag
        if self.options.preserve_more_tag:
            html = html.replace('<!--more-->', '%%MORE_TAG%%')
            protected['%%MORE_TAG%%'] = '<!--more-->'

        return html, protected

    def _restore_special_content(self, html: str, protected: Dict[str, str]) -> str:
        """Restore protected content"""
        for key, value in protected.items():
            if 'MATHJAX' in key:
                # Wrap MathJax in HTML block
                wrapped = f'<!-- wp:html -->\n{value}\n<!-- /wp:html -->'
                self.stats.html_blocks += 1
                html = html.replace(key, wrapped)
            elif 'MORE_TAG' in key:
                # Keep more tag as-is
                html = html.replace(key, value)
            else:
                html = html.replace(key, value)
        return html

    def _convert_element(self, element: Tag) -> Optional[str]:
        """Convert a single HTML element to Gutenberg block"""
        tag_name = element.name.lower()

        # Headings
        if tag_name in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            return self._convert_heading(element)

        # Paragraphs
        if tag_name == 'p':
            return self._convert_paragraph(element)

        # Code blocks (pre or div.codehilite)
        if tag_name == 'pre':
            return self._convert_code_block(element)
        if tag_name == 'div':
            classes = element.get('class') or []
            if isinstance(classes, str):
                classes = [classes]
            if classes and 'codehilite' in classes:
                return self._convert_codehilite(element)
            return self._convert_generic_div(element)

        # Lists
        if tag_name == 'ul':
            return self._convert_list(element, ordered=False)
        if tag_name == 'ol':
            return self._convert_list(element, ordered=True)

        # Tables
        if tag_name == 'table':
            return self._convert_table(element)

        # Images
        if tag_name == 'img':
            return self._convert_image(element)
        if tag_name == 'figure':
            return self._convert_figure(element)

        # Blockquotes
        if tag_name == 'blockquote':
            return self._convert_blockquote(element)

        # Horizontal rules
        if tag_name == 'hr':
            return self._convert_separator()

        # Scripts (non-MathJax, already protected)
        if tag_name == 'script':
            return self._convert_html_block(element)

        # Fallback: wrap in HTML block
        return self._convert_html_block(element)

    def _convert_heading(self, element: Tag) -> str:
        """Convert heading to wp:heading block"""
        level = int(element.name[1])
        inner_html = self._get_inner_html(element)

        # Preserve id attribute if present
        attrs: Dict[str, Any] = {"level": level}
        if element.get('id'):
            # WordPress doesn't use id in heading blocks by default
            pass

        self.stats.headings += 1

        attrs_json = json.dumps(attrs)
        return f'<!-- wp:heading {attrs_json} -->\n<{element.name}>{inner_html}</{element.name}>\n<!-- /wp:heading -->'

    def _convert_paragraph(self, element: Tag) -> Optional[str]:
        """Convert paragraph to wp:paragraph block"""
        inner_html = self._get_inner_html(element)

        # Skip empty paragraphs
        if not inner_html.strip():
            return None

        # Check for <!--more--> inside paragraph
        if '%%MORE_TAG%%' in inner_html or '<!--more-->' in inner_html:
            # Split around more tag
            parts = re.split(r'%%MORE_TAG%%|<!--more-->', inner_html)
            blocks = []
            for i, part in enumerate(parts):
                part = part.strip()
                if part:
                    blocks.append(self._create_paragraph_block(part))
                if i < len(parts) - 1:
                    blocks.append('<!--more-->')
            return '\n\n'.join(filter(None, blocks))

        return self._create_paragraph_block(inner_html)

    def _create_paragraph_block(self, content: str) -> Optional[str]:
        """Create a paragraph block from content string"""
        content = content.strip()
        if not content:
            return None

        self.stats.paragraphs += 1
        return f'<!-- wp:paragraph -->\n<p>{content}</p>\n<!-- /wp:paragraph -->'

    def _convert_code_block(self, element: Tag) -> str:
        """Convert pre/code to wp:code block"""
        code_element = element.find('code')
        language = None

        if code_element:
            # Get raw text, preserving whitespace
            code_content = code_element.get_text()
            # Detect language from class (supports both 'language-xxx' and 'xxx')
            classes = code_element.get('class') or []
            if isinstance(classes, str):
                classes = [classes]
            for cls in (classes if classes else []):
                if cls.startswith('language-'):
                    language = cls.replace('language-', '')
                    break
                elif cls in ('python', 'javascript', 'js', 'bash', 'shell', 'json',
                           'html', 'css', 'sql', 'yaml', 'xml', 'markdown', 'md',
                           'java', 'c', 'cpp', 'csharp', 'go', 'rust', 'ruby', 'php'):
                    language = cls
                    break
        else:
            code_content = element.get_text()

        # Also check pre element for language class
        if not language:
            pre_classes = element.get('class') or []
            if isinstance(pre_classes, str):
                pre_classes = [pre_classes]
            for cls in (pre_classes if pre_classes else []):
                if cls.startswith('language-'):
                    language = cls.replace('language-', '')
                    break

        # Escape HTML entities in code
        code_content = self._escape_code_content(code_content)

        self.stats.code_blocks += 1

        # Build block attributes
        attrs: Dict[str, Any] = {}
        if language and self.options.preserve_code_language:
            attrs['language'] = language

        attrs_str = f' {json.dumps(attrs)}' if attrs else ''

        return f'''<!-- wp:code{attrs_str} -->
<pre class="wp-block-code"><code>{code_content}</code></pre>
<!-- /wp:code -->'''

    def _convert_codehilite(self, element: Tag) -> str:
        """Convert Python Markdown codehilite div to wp:code block"""
        pre_element = element.find('pre')
        if pre_element:
            # Extract plain text from highlighted code
            code_content = pre_element.get_text()
            code_content = self._escape_code_content(code_content)

            self.stats.code_blocks += 1

            return f'''<!-- wp:code -->
<pre class="wp-block-code"><code>{code_content}</code></pre>
<!-- /wp:code -->'''

        # Fallback: wrap entire div as HTML block
        return self._convert_html_block(element)

    def _convert_list(self, element: Tag, ordered: bool) -> str:
        """Convert ul/ol to wp:list block"""
        # Preserve inner HTML (including nested lists)
        inner_html = self._get_inner_html(element)
        tag = 'ol' if ordered else 'ul'

        self.stats.lists += 1

        if ordered:
            return f'''<!-- wp:list {{"ordered":true}} -->
<ol>{inner_html}</ol>
<!-- /wp:list -->'''
        else:
            return f'''<!-- wp:list -->
<ul>{inner_html}</ul>
<!-- /wp:list -->'''

    def _convert_table(self, element: Tag) -> str:
        """Convert table to wp:table block"""
        # Remove inline styles from table elements to avoid Gutenberg conflicts
        # WordPress Gutenberg has its own table styling
        for tag in element.find_all(['table', 'th', 'td', 'tr', 'thead', 'tbody']):
            if isinstance(tag, Tag) and tag.has_attr('style'):
                del tag['style']

        table_html = str(element)

        self.stats.tables += 1

        return f'''<!-- wp:table -->
<figure class="wp-block-table">{table_html}</figure>
<!-- /wp:table -->'''

    def _convert_image(self, element: Tag) -> str:
        """Convert img to wp:image block"""
        # Build img tag preserving all attributes
        attrs_list = []
        for key, value in element.attrs.items():
            if isinstance(value, list):
                value = ' '.join(value)
            # Escape quotes in attribute values
            value = str(value).replace('"', '&quot;')
            attrs_list.append(f'{key}="{value}"')

        img_tag = f'<img {" ".join(attrs_list)} />'

        self.stats.images += 1

        if self.options.wrap_images_in_figure:
            return f'''<!-- wp:image -->
<figure class="wp-block-image">{img_tag}</figure>
<!-- /wp:image -->'''
        else:
            return f'''<!-- wp:image -->
{img_tag}
<!-- /wp:image -->'''

    def _convert_figure(self, element: Tag) -> str:
        """Convert figure (may contain image) to wp:image block"""
        img = element.find('img')
        if img:
            self.stats.images += 1
            return f'''<!-- wp:image -->
{str(element)}
<!-- /wp:image -->'''

        # Fallback to HTML block for other figures
        return self._convert_html_block(element)

    def _convert_blockquote(self, element: Tag) -> str:
        """Convert blockquote to wp:quote block"""
        inner_html = self._get_inner_html(element)

        self.stats.quotes += 1

        return f'''<!-- wp:quote -->
<blockquote class="wp-block-quote">{inner_html}</blockquote>
<!-- /wp:quote -->'''

    def _convert_separator(self) -> str:
        """Convert hr to wp:separator block"""
        self.stats.separators += 1

        return '''<!-- wp:separator -->
<hr class="wp-block-separator has-alpha-channel-opacity"/>
<!-- /wp:separator -->'''

    def _convert_html_block(self, element: Tag) -> str:
        """Wrap element in wp:html block (fallback for unsupported elements)"""
        self.stats.html_blocks += 1

        return f'''<!-- wp:html -->
{str(element)}
<!-- /wp:html -->'''

    def _convert_generic_div(self, element: Tag) -> Optional[str]:
        """Handle generic div elements"""
        classes = element.get('class') or []
        if isinstance(classes, str):
            classes = [classes]

        # Video containers
        if classes and 'video-container' in classes:
            return self._convert_html_block(element)

        # ASCII art or monospace content
        style = element.get('style') or ''
        if style and ('monospace' in style or 'pre' in style):
            return self._convert_html_block(element)

        # Default: process children as separate blocks
        blocks = []
        for child in element.children:
            if isinstance(child, Tag):
                block = self._convert_element(child)
                if block:
                    blocks.append(block)
            elif isinstance(child, NavigableString):
                text = str(child).strip()
                if text:
                    block = self._create_paragraph_block(text)
                    if block:
                        blocks.append(block)

        if blocks:
            return '\n\n'.join(blocks)

        return None

    def _get_inner_html(self, element: Tag) -> str:
        """Get inner HTML of element, preserving inline elements"""
        return ''.join(str(child) for child in element.children)

    def _escape_code_content(self, text: str) -> str:
        """Escape HTML special characters in code content"""
        return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;'))


def convert_html_to_gutenberg(
    html: str,
    options: Optional[ConversionOptions] = None
) -> str:
    """
    Convenience function to convert HTML to Gutenberg format.

    Args:
        html: Raw HTML content
        options: Conversion options (optional)

    Returns:
        Gutenberg block formatted content
    """
    converter = GutenbergConverter(options)
    result, stats = converter.convert(html)
    logger.info(f"Conversion complete: {stats}")
    return result


def convert_html_to_gutenberg_with_stats(
    html: str,
    options: Optional[ConversionOptions] = None
) -> Tuple[str, ConversionStats]:
    """
    Convert HTML to Gutenberg format with statistics.

    Args:
        html: Raw HTML content
        options: Conversion options (optional)

    Returns:
        Tuple of (converted content, statistics)
    """
    converter = GutenbergConverter(options)
    return converter.convert(html)


# CLI for testing
if __name__ == '__main__':
    import sys

    # Simple test
    test_html = """
    <h2>Test Heading</h2>
    <p>This is a <strong>test</strong> paragraph with <a href="#">a link</a>.</p>
    <pre><code>def hello():
    print("Hello World")</code></pre>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
    <hr>
    <table>
        <tr><th>Header</th></tr>
        <tr><td>Cell</td></tr>
    </table>
    """

    print("=== Input HTML ===")
    print(test_html)
    print("\n=== Gutenberg Output ===")

    result, stats = convert_html_to_gutenberg_with_stats(test_html)
    print(result)
    print(f"\n=== Statistics ===\n{stats}")
