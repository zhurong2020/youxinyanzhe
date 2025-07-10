import pytest
import os
import logging
from pathlib import Path
from PIL import Image, ImageDraw
from dotenv import load_dotenv, dotenv_values
import frontmatter
from datetime import datetime
import shutil
import yaml
from scripts import setup_logger

# 设置测试日志
logger = setup_logger("TestFixtures")

@pytest.fixture(scope="session", autouse=True)
def check_environment():
    """检查测试环境配置"""
    load_dotenv(override=True)
    
    # 检查必要的环境变量
    required_vars = {
        'CLOUDFLARE_ACCOUNT_ID': '用于 Cloudflare Images',
        'CLOUDFLARE_ACCOUNT_HASH': '用于 Cloudflare Images',
        'CLOUDFLARE_API_TOKEN': '用于 Cloudflare API 认证',
        'GEMINI_API_KEY': '用于 Google Gemini API'
    }
    
    missing_vars = []
    for var, desc in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({desc})")
    
    if missing_vars:
        pytest.skip(f"缺少必要的环境变量:\n" + "\n".join(missing_vars))
    
    logger.info("✅ 环境变量检查通过")

@pytest.fixture(scope="session")
def test_config():
    """加载测试配置"""
    with open("config/test_config.yml", encoding="utf-8") as f:
        return yaml.safe_load(f)

@pytest.fixture(scope="session")
def test_assets(test_config):
    """根据配置创建测试资源"""
    config = test_config["test_assets"]
    # 创建图片目录
    image_dir = Path("assets/images/posts/2025/02/test-post")
    image_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建测试图片
    test_images = {
        "header.webp": (800, 400, "Header Image"),
        "test.webp": (600, 300, "Test Image")
    }
    
    image_paths = {}
    for name, (width, height, text) in test_images.items():
        image_path = image_dir / name
        img = Image.new('RGB', (width, height), color='blue')
        draw = ImageDraw.Draw(img)
        draw.rectangle([50, 50, width-50, height-50], outline='white', width=5)
        draw.text((width//2, height//2), text, fill='white', anchor="mm")
        img.save(image_path)
        image_paths[name] = image_path
        logger.info(f"✅ 创建测试图片: {image_path}")
        
    yield image_paths
    
    # 清理测试图片 - 使用更安全的方法
    if image_dir.exists():
        try:
            # 先删除文件
            for file in image_dir.glob("*"):
                try:
                    file.unlink(missing_ok=True)
                except Exception as e:
                    logger.warning(f"无法删除文件 {file}: {str(e)}")
            
            # 尝试删除目录
            try:
                # 尝试删除所有子目录
                for subdir in sorted(image_dir.glob("**/*"), reverse=True):
                    if subdir.is_dir():
                        try:
                            subdir.rmdir()
                        except Exception:
                            pass
                
                # 最后尝试删除主目录
                image_dir.rmdir()
                logger.info(f"🧹 清理测试图片目录: {image_dir}")
            except Exception as e:
                logger.warning(f"无法删除图片目录 {image_dir}: {str(e)}")
                logger.warning("这不会影响测试结果，但可能需要手动清理")
        except Exception as e:
            logger.warning(f"清理测试图片时出错: {str(e)}")

@pytest.fixture(scope="session")
def test_draft(test_assets):
    """创建测试文章"""
    logger.info("📝 创建测试文章...")
    
    # 测试文章内容
    content = """
## 测试文章

这是一篇测试文章，用于测试图片上传和内容处理功能。

![测试图片](/assets/images/posts/2025/02/test-post/header.webp)

另一张图片：![图片2](/assets/images/posts/2025/02/test-post/image2.png)
"""
    
    # 使用OrderedDict确保layout字段在最前面
    from collections import OrderedDict
    post = OrderedDict()
    post["layout"] = "single"
    post["title"] = "测试文章：图片上传和内容处理"
    post["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S +0000")
    post["categories"] = ["测试"]
    post["tags"] = ["图片处理", "Cloudflare"]
    post["header"] = {
        "image": "/assets/images/posts/2025/02/test-post/header.webp",
        "overlay_filter": 0.5
    }
    
    # 创建文章
    draft_dir = Path("tests/test_data/drafts")
    draft_dir.mkdir(parents=True, exist_ok=True)
    draft_path = draft_dir / "test-article.md"
    
    # 写入文件
    post_text = frontmatter.dumps(frontmatter.Post(content, **post))
    draft_path.write_text(post_text, encoding='utf-8')
    logger.info(f"✅ 创建测试文章: {draft_path}")
    
    yield draft_path
    
    # 清理测试文章
    if draft_dir.exists():
        try:
            # 先删除文件，再删除目录
            for file in draft_dir.glob("*"):
                try:
                    file.unlink()
                except Exception as e:
                    logger.warning(f"无法删除文件 {file}: {str(e)}")
            
            # 尝试删除目录
            try:
                draft_dir.rmdir()
                logger.info(f"🧹 清理测试文章目录: {draft_dir}")
            except Exception as e:
                logger.warning(f"无法删除目录 {draft_dir}: {str(e)}")
                logger.warning("这不会影响测试结果，但可能需要手动清理")
        except Exception as e:
            logger.warning(f"清理测试文章时出错: {str(e)}")
    
    # 清理发布的文章和归档
    published_path = Path("_posts") / draft_path.name
    if published_path.exists():
        published_path.unlink()
        logger.info(f"🧹 清理已发布文章: {published_path}")
    
    archived_path = Path("_drafts/archived") / draft_path.name
    if archived_path.exists():
        archived_path.unlink()
        logger.info(f"🧹 清理已归档文章: {archived_path}") 