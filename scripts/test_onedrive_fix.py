#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging
import tempfile
from pathlib import Path

# 添加当前目录到sys.path，以便能够导入scripts模块
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from scripts.content_pipeline import ContentPipeline

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

def test_download_onedrive_image():
    """测试下载OneDrive图片"""
    pipeline = ContentPipeline()
    
    # 测试OneDrive URL
    onedrive_urls = [
        "https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169891&authkey=%21AFppTKcu8cfS2Eo&width=660",
        "https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169892&authkey=%21AP4tETGqIc2pBDc&width=621&height=486"
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        success_count = 0
        for url in onedrive_urls:
            try:
                img_name = pipeline._download_onedrive_image(url, temp_dir_path)
                if img_name:
                    logger.info(f"成功下载图片: {url} -> {img_name}")
                    
                    # 验证图片名称格式
                    assert img_name.startswith("onedrive_"), f"图片名称应该以onedrive_开头: {img_name}"
                    
                    # 验证图片文件是否存在
                    img_path = temp_dir_path / img_name
                    assert img_path.exists(), f"图片文件不存在: {img_path}"
                    success_count += 1
                else:
                    logger.warning(f"下载图片失败: {url}")
            except Exception as e:
                logger.warning(f"下载图片时出错: {url}, 错误: {str(e)}")
        
        # 确保至少有一个图片下载成功
        assert success_count > 0, "没有图片下载成功"

def test_is_same_onedrive_image():
    """测试判断OneDrive URL是否对应指定的图片名称"""
    pipeline = ContentPipeline()
    
    # 测试用例
    test_cases = [
        # URL, 图片名称, 期望结果
        ("https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169891&authkey=%21AFppTKcu8cfS2Eo&width=660", "onedrive_69891.jpg", True),
        ("https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169892&authkey=%21AP4tETGqIc2pBDc&width=621&height=486", "onedrive_69892.jpg", True),
        ("https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169891&authkey=%21AFppTKcu8cfS2Eo&width=660", "onedrive_69892.jpg", False),
        ("https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169891&authkey=%21AFppTKcu8cfS2Eo&width=660", "onedrive_abcde.jpg", False)
    ]
    
    for url, img_name, expected in test_cases:
        result = pipeline._is_same_onedrive_image(url, img_name)
        logger.info(f"URL: {url}, 图片名称: {img_name}, 结果: {result}, 期望: {expected}")
        assert result == expected, f"测试失败: URL={url}, 图片名称={img_name}, 结果={result}, 期望={expected}"

def test_replace_images():
    """测试替换内容中的图片URL"""
    pipeline = ContentPipeline()
    
    # 测试内容
    content = """
# 测试文章

这是一篇测试文章，包含多个OneDrive图片链接。

![图片1](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169891&authkey=%21AFppTKcu8cfS2Eo&width=660)

![图片2](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169892&authkey=%21AP4tETGqIc2pBDc&width=621&height=486)

![图片3](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169893&authkey=%21AJXupxPWiQDXyQs&width=660)
"""
    
    # 测试图片映射
    images = {
        "onedrive_69891.jpg": "cloudflare_id_1",
        "onedrive_69892.jpg": "cloudflare_id_2",
        "onedrive_69893.jpg": "cloudflare_id_3"
    }
    
    # 替换图片URL
    result = pipeline._replace_images(content, images)
    
    # 验证结果
    logger.info(f"替换后的内容:\n{result}")
    
    # 检查是否包含Cloudflare URL
    assert "https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/cloudflare_id_1/public" in result, "结果中应该包含第一个Cloudflare URL"
    assert "https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/cloudflare_id_2/public" in result, "结果中应该包含第二个Cloudflare URL"
    assert "https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/cloudflare_id_3/public" in result, "结果中应该包含第三个Cloudflare URL"
    
    # 检查是否不再包含OneDrive URL
    assert "https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169891" not in result, "结果中不应该包含第一个OneDrive URL"
    assert "https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169892" not in result, "结果中不应该包含第二个OneDrive URL"
    assert "https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169893" not in result, "结果中不应该包含第三个OneDrive URL"

def main():
    """运行所有测试"""
    logger.info("开始测试OneDrive图片处理...")
    
    try:
        logger.info("测试下载OneDrive图片...")
        test_download_onedrive_image()
        logger.info("✅ 测试下载OneDrive图片成功")
        
        logger.info("测试判断OneDrive URL是否对应指定的图片名称...")
        test_is_same_onedrive_image()
        logger.info("✅ 测试判断OneDrive URL是否对应指定的图片名称成功")
        
        logger.info("测试替换内容中的图片URL...")
        test_replace_images()
        logger.info("✅ 测试替换内容中的图片URL成功")
        
        logger.info("✅ 所有测试通过")
    except AssertionError as e:
        logger.error(f"❌ 测试失败: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 测试出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 