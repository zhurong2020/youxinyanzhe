import re
import yaml
import pytest
import frontmatter
from pathlib import Path
from typing import Dict, Any, cast

def test_image_url_replacement():
    """测试图片URL替换功能"""
    # 测试内容
    content = """---
layout: single
title: "测试文章"
header:
  image: "/assets/images/posts/2025/02/test.jpg"
---

这是一个测试图片：
![测试图片](/assets/images/posts/2025/02/test.jpg)

另一个图片：
![图片2](/assets/images/posts/2025/02/image2.png)
"""

    # 图片映射
    image_mappings = {
        'test.jpg': 'https://imagedelivery.net/xxx/test',
        'image2.png': 'https://imagedelivery.net/xxx/image2'
    }

    # 解析 frontmatter
    post = frontmatter.loads(content)
    content_text = post.content

    # 替换图片URL
    for local_name, cloudflare_url in image_mappings.items():
        # 处理正文中的图片
        pattern = f'!\\[([^\\]]*)\\]\\([^)]*{re.escape(local_name)}\\)'
        replacement = f'![\\1]({cloudflare_url})'
        content_text = re.sub(pattern, replacement, content_text)

        # 处理 front matter 中的图片
        metadata = cast(Dict[str, Any], post.metadata)
        if hasattr(post, 'metadata') and 'header' in metadata and 'image' in metadata['header']:
            if local_name in str(metadata['header']['image']):
                metadata['header']['image'] = cloudflare_url

    # 更新内容
    post.content = content_text
    result = frontmatter.dumps(post)

    # 验证结果
    assert 'https://imagedelivery.net/xxx/test' in result
    assert 'https://imagedelivery.net/xxx/image2' in result
    assert '/assets/images/posts/2025/02/test.jpg' not in result
    assert '/assets/images/posts/2025/02/image2.png' not in result

def test_yaml_parsing():
    """测试YAML解析功能"""
    content = """---
layout: single
title: "测试文章"
date: 2025-02-20 12:00:00 +0000
categories: 
  - 测试
tags:
  - YAML
  - 解析
excerpt: "这是一个测试摘要，包含'单引号'和\"双引号\"。"
---

## 测试内容

这是测试内容。
"""
    
    # 解析front matter
    post = frontmatter.loads(content)
    
    # 验证解析结果
    metadata = cast(Dict[str, Any], post.metadata)
    assert metadata['layout'] == 'single'
    assert metadata['title'] == '测试文章'
    assert '测试' in metadata['categories']
    assert 'YAML' in metadata['tags']
    assert 'excerpt' in metadata
    
    # 测试重新序列化
    from collections import OrderedDict
    ordered_post = OrderedDict()
    ordered_post['layout'] = post['layout']
    
    # 添加其他字段
    for key, value in post.metadata.items():
        if key != 'layout':
            ordered_post[key] = value
    
    # 创建新的post对象并设置内容
    new_post = frontmatter.Post(post.content, **ordered_post)
    result = frontmatter.dumps(new_post)
    
    # 验证layout是第一个字段
    lines = result.split('\n')
    assert lines[1].strip().startswith('layout:')

def test_complex_image_url_replacement():
    """测试复杂的图片URL替换场景"""
    content = """---
layout: single
title: "测试文章"
header:
  image: "/assets/images/posts/2025/02/test.jpg"
---

图片1：
![测试图片](/assets/images/posts/2025/02/test.jpg)

图片2：
![图片2](/assets/images/posts/2025/02/image2.png)

相对路径图片：
![图片3](test.jpg)
"""

    # 图片映射
    image_mappings = {
        'test.jpg': 'https://imagedelivery.net/xxx/test',
        'image2.png': 'https://imagedelivery.net/xxx/image2'
    }

    # 解析 frontmatter
    post = frontmatter.loads(content)
    content_text = post.content

    # 替换图片URL
    for local_name, cloudflare_url in image_mappings.items():
        patterns = [
            f'!\\[([^\\]]*)\\]\\(/assets/images/posts/.*?/{re.escape(local_name)}\\)',
            f'!\\[([^\\]]*)\\]\\({re.escape(local_name)}\\)'
        ]
        
        for pattern in patterns:
            replacement = f'![\\1]({cloudflare_url})'
            content_text = re.sub(pattern, replacement, content_text)

    # 验证结果
    assert 'https://imagedelivery.net/xxx/test' in content_text
    assert 'https://imagedelivery.net/xxx/image2' in content_text
    assert '/assets/images/posts/2025/02/test.jpg' not in content_text
    assert '/assets/images/posts/2025/02/image2.png' not in content_text

def test_real_world_image_url_replacement():
    """测试真实场景的图片URL替换"""
    content = """---
layout: single
title: "测试文章"
header:
  image: "/assets/images/posts/2025/01/trump-crypto-meme.jpg"
  overlay_filter: 0.5
excerpt: |
  这是一个包含"中文引号"的摘要，
  测试YAML解析
---

第一张图片：
![特朗普加密货币](/assets/images/posts/2025/01/trump-crypto-meme.jpg)

第二张图片：
![市场走势](/assets/images/posts/2025/01/market-trend.png)
"""

    # 图片映射 - 使用实际的 Cloudflare 图片 ID 格式
    image_mappings = {
        'trump-crypto-meme.jpg': 'https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/abc123-def4-56gh-89ij-klmno0pqrst0/public',
        'market-trend.png': 'https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/uvw789-xyz0-12ab-34cd-efghijklmn00/public'
    }

    # 解析 frontmatter
    # 直接解析，因为内容已经是正确的格式
    post = frontmatter.loads(content)
    content_text = post.content

    # 替换图片URL
    for local_name, cloudflare_url in image_mappings.items():
        patterns = [
            f'!\\[([^\\]]*)\\]\\(/assets/images/posts/.*?/{re.escape(local_name)}\\)',  # 完整路径
            f'!\\[([^\\]]*)\\]\\({re.escape(local_name)}\\)'  # 仅文件名
        ]
        
        replaced = False
        for pattern in patterns:
            if re.search(pattern, content_text):
                content_text = re.sub(pattern, f'![\\1]({cloudflare_url})', content_text)
                replaced = True

        # 处理 front matter 中的图片
        metadata = cast(Dict[str, Any], post.metadata)
        if hasattr(post, 'metadata') and 'header' in metadata and 'image' in metadata['header']:
            header_image = metadata['header']['image']
            if local_name in str(header_image):
                metadata['header']['image'] = cloudflare_url

    # 更新内容
    post.content = content_text
    result = frontmatter.dumps(post)

    # 验证结果
    assert 'imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/' in result
    assert '/public' in result
    assert '/assets/images/posts/2025/01/trump-crypto-meme.jpg' not in result
    assert '/assets/images/posts/2025/01/market-trend.png' not in result

if __name__ == '__main__':
    pytest.main(['-v', __file__]) 