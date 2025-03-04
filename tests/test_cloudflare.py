import pytest
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from scripts.image_mapper import CloudflareImageMapper
from scripts import setup_logger
import yaml

# 设置测试日志
logger = setup_logger("TestCloudflare")

@pytest.fixture(scope="session")
def cloudflare_config():
    """加载 Cloudflare 配置"""
    with open("config/cloudflare_config.yml", 'r') as f:
        return yaml.safe_load(f)["image_processing"]["cloudflare"]

@pytest.fixture(scope="session")
def test_settings():
    """加载测试配置"""
    with open("config/test_config.yml", 'r') as f:
        return yaml.safe_load(f)["test_settings"]

@pytest.fixture(scope="module")
def cloudflare_mapper():
    """创建 CloudflareImageMapper 实例的 fixture"""
    # 加载环境变量
    load_dotenv(override=True)
    
    # 检查环境变量
    account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
    account_hash = os.getenv('CLOUDFLARE_ACCOUNT_HASH')
    api_token = os.getenv('CLOUDFLARE_API_TOKEN')
    
    logger.info(f"Account ID: {account_id[:10]}..." if account_id else "Not found")
    logger.info(f"API Token: {api_token[:10]}..." if api_token else "Not found")
    
    if not all([account_id, account_hash, api_token]):
        pytest.skip("❌ Cloudflare 环境变量未正确设置")
    
    # 返回 mapper 实例
    return CloudflareImageMapper(
        account_id=account_id,
        account_hash=account_hash,
        api_token=api_token
    )

def test_cloudflare_image_upload(cloudflare_mapper, test_image):
    """测试 Cloudflare 图片上传功能"""
    assert test_image.exists(), f"测试图片不存在: {test_image}"
    logger.info(f"开始上传测试图片: {test_image}")
    
    # 测试单个图片上传
    url = cloudflare_mapper.upload_image(test_image)
    
    assert url is not None, "❌ 图片上传失败"
    assert url.startswith('https://imagedelivery.net/'), "图片URL格式不正确"
    logger.info(f"✅ 图片上传成功: {url}")

def test_cloudflare_batch_upload(cloudflare_mapper, test_image):
    """测试批量图片上传功能"""
    test_images = {
        "test.webp": test_image
    }
    
    logger.info("开始批量上传测试")
    logger.debug(f"测试图片列表: {test_images}")
    
    # 测试批量上传
    result = cloudflare_mapper.map_images(test_images)
    
    assert result, "批量上传返回结果为空"
    assert "test.webp" in result, "上传结果中找不到测试图片"
    assert result["test.webp"].startswith('https://imagedelivery.net/'), "图片URL格式不正确"
    logger.info(f"✅ 批量上传成功: {result}")

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 