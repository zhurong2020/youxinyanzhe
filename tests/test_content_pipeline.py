import pytest
import logging
from pathlib import Path
from scripts.content_pipeline import ContentPipeline
import os
from dotenv import load_dotenv
from scripts import setup_logger

# 设置测试日志
logger = setup_logger("TestContentPipeline")

@pytest.fixture(scope="module")
def pipeline():
    """创建 ContentPipeline 实例"""
    load_dotenv(override=True)
    return ContentPipeline("config/pipeline_config.yml")

def test_process_images(pipeline, test_draft):
    """测试图片处理功能"""
    result = pipeline.process_post_images(test_draft)
    assert result, "图片处理返回结果为空"
    assert len(result) > 0, "没有处理任何图片"
    
    # 验证图片URL格式
    for url in result.values():
        assert url.startswith('https://imagedelivery.net/'), f"无效的图片URL: {url}"
    logging.info(f"处理的图片: {result}")

def test_generate_content(pipeline):
    """测试内容生成功能"""
    draft = pipeline.generate_test_content()
    assert draft is not None, "生成的草稿为空"
    assert draft.exists(), "草稿文件不存在"
    logging.info(f"生成的测试文章: {draft}")

def test_full_pipeline(pipeline, test_draft):
    """测试完整的内容处理流程"""
    try:
        # 选择发布平台
        platforms = ["github_pages"]
        
        # 处理并发布
        pipeline.process_draft(test_draft, platforms)
        
        # 验证发布结果
        published_path = Path("_posts") / test_draft.name
        assert published_path.exists(), "发布的文章不存在"
        
        # 验证归档
        archived_path = Path("_drafts/archived") / test_draft.name
        assert archived_path.exists(), "草稿未被归档"
        
        logging.info("✅ 完整流程测试通过")
        
    except Exception as e:
        logging.error(f"❌ 处理过程出错: {str(e)}")
        logging.debug("错误详情:", exc_info=True)
        pytest.fail(f"流程测试失败: {str(e)}")

class TestContentPipeline:
    def test_config_loading(self):
        """测试配置加载"""
        pipeline = ContentPipeline("config/test_config.yml")
        assert pipeline.config is not None
        
    def test_cloudflare_upload(self):
        """测试 Cloudflare 上传"""
        # 保留这个集成测试

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 