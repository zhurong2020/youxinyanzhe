#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试OneDrive图片处理修复
"""

import os
import sys
import logging
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# 添加当前目录到sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from scripts.content_pipeline import ContentPipeline

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TestImageFix")

def test_onedrive_image_download():
    """测试OneDrive图片下载功能"""
    # 加载环境变量
    load_dotenv()
    
    # 初始化内容管道
    pipeline = ContentPipeline(verbose=True)
    
    # 测试OneDrive图片URL
    test_urls = [
        "https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169891&authkey=%21AFppTKcu8cfS2Eo&width=660",
        "https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169894&authkey=%21AAQe7bvCcv0ZAMg&width=660",
        "https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169893&authkey=%21AAhNnTuuzWjx57M&width=660"
    ]
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 下载图片
        downloaded_files = []
        for url in test_urls:
            logger.info(f"测试下载图片: {url}")
            img_name = pipeline._download_onedrive_image(url, temp_path)
            if img_name:
                downloaded_files.append(img_name)
                logger.info(f"✅ 下载成功: {img_name}")
            else:
                logger.error(f"❌ 下载失败: {url}")
        
        # 验证下载的图片是否都有唯一的文件名
        unique_files = set(downloaded_files)
        logger.info(f"下载的图片数量: {len(downloaded_files)}")
        logger.info(f"唯一的图片数量: {len(unique_files)}")
        
        if len(downloaded_files) == len(unique_files):
            logger.info("✅ 所有图片都有唯一的文件名")
        else:
            logger.error("❌ 存在重复的文件名")
            for name in downloaded_files:
                logger.info(f"  - {name}")

def test_image_replacement():
    """测试图片替换功能"""
    # 加载环境变量
    load_dotenv()
    
    # 初始化内容管道
    pipeline = ContentPipeline(verbose=True)
    
    # 测试Markdown内容
    test_content = """
# 测试文档

这是一个测试文档，包含多个OneDrive图片链接。

![图片1](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169891&authkey=%21AFppTKcu8cfS2Eo&width=660)

这是第二张图片：

![图片2](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169894&authkey=%21AAQe7bvCcv0ZAMg&width=660)

这是第三张图片：

![图片3](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169893&authkey=%21AAhNnTuuzWjx57M&width=660)
"""
    
    # 处理图片
    logger.info("开始处理测试内容中的图片")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        
        # 创建临时文件
        temp_file = temp_dir_path / "test_content.md"
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        # 手动下载图片并创建映射
        images = {}
        test_urls = [
            "https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169891&authkey=%21AFppTKcu8cfS2Eo&width=660",
            "https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169894&authkey=%21AAQe7bvCcv0ZAMg&width=660",
            "https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169893&authkey=%21AAhNnTuuzWjx57M&width=660"
        ]
        
        for url in test_urls:
            img_name = pipeline._download_onedrive_image(url, temp_dir_path)
            if img_name:
                # 模拟上传到Cloudflare并获取ID
                cloudflare_id = f"test-{img_name.replace('.', '-')}"
                cloudflare_url = f"https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/{cloudflare_id}/public"
                images[img_name] = cloudflare_url
                logger.info(f"模拟上传图片: {img_name} -> {cloudflare_url}")
        
        # 替换图片链接
        with open(temp_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        new_content = pipeline._replace_images(content, images)
        
        # 保存替换后的内容
        result_file = temp_dir_path / "result_content.md"
        with open(result_file, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        # 检查替换后的内容
        cloudflare_urls = []
        for line in new_content.split('\n'):
            if 'imagedelivery.net' in line:
                cloudflare_urls.append(line)
                logger.info(f"替换后的图片链接: {line}")
        
        # 验证替换后的图片链接是否都不同
        unique_urls = set(cloudflare_urls)
        logger.info(f"替换后的图片链接数量: {len(cloudflare_urls)}")
        logger.info(f"唯一的图片链接数量: {len(unique_urls)}")
        
        if len(cloudflare_urls) == len(unique_urls):
            logger.info("✅ 所有图片链接都是唯一的")
        else:
            logger.error("❌ 存在重复的图片链接")
            for url in cloudflare_urls:
                logger.info(f"  - {url}")

if __name__ == "__main__":
    logger.info("开始测试OneDrive图片处理修复")
    
    # 测试图片下载
    test_onedrive_image_download()
    
    # 测试图片替换
    test_image_replacement()
    
    logger.info("测试完成") 