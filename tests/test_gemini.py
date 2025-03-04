import pytest
import os
import logging
import sys
from pathlib import Path
import frontmatter

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions

# 现在导入本地模块
from scripts.content_pipeline import ContentPipeline
from scripts import setup_logger

# 设置测试日志
logger = setup_logger("TestGemini")

@pytest.fixture(scope="module")
def gemini_model():
    """创建 Gemini 模型实例的 fixture"""
    # 加载环境变量
    load_dotenv(override=True)
    
    # 获取并验证 API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        pytest.skip("❌ API key not found in .env file")
    if not api_key.startswith("AIza"):
        pytest.skip("❌ API key format appears to be invalid")
        
    logging.info(f"✓ API key loaded (starts with): {api_key[:10]}...")
    
    # 获取可用模型列表
    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()
        model_names = [model.name for model in models]
        logging.info(f"Available models: {model_names}")
        
        # 优先选择 Gemini 2.0 模型
        preferred_models = [
            "models/gemini-2.0-flash",
            "models/gemini-2.0-pro",
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro"
        ]
        
        # 查找最佳匹配模型
        model_name = None
        for preferred in preferred_models:
            matching_models = [name for name in model_names if preferred in name]
            if matching_models:
                # 优先选择没有 "exp" 的稳定版本
                stable_models = [name for name in matching_models if "exp" not in name.lower()]
                if stable_models:
                    model_name = stable_models[0]
                else:
                    model_name = matching_models[0]
                    logging.info(f"Found experimental model: {model_name}")
                break
        
        # 如果没有找到匹配的模型，使用任何可用的 Gemini 模型
        if not model_name:
            gemini_models = [name for name in model_names if 'gemini' in name.lower()]
            if gemini_models:
                model_name = gemini_models[0]
            else:
                model_name = "models/gemini-2.0-flash"  # 默认值
        
        logging.info(f"Using model: {model_name}")
        
        # 创建模型实例
        model = genai.GenerativeModel(model_name)
        
        # 测试连接
        response = model.generate_content("Hello, how are you?")
        if response:
            return model
        else:
            pytest.skip("❌ Failed to generate content with Gemini model")
    except exceptions.ResourceExhausted as e:
        pytest.skip(f"❌ API 配额已耗尽: {str(e)}")
    except Exception as e:
        pytest.skip(f"❌ Failed to initialize Gemini model: {str(e)}")

def test_gemini_basic_generation(gemini_model):
    """测试基本的文本生成功能"""
    prompt = "How to say hello in Chinese?"
    response = gemini_model.generate_content(prompt)
    
    assert response is not None
    assert response.text is not None
    assert len(response.text) > 0
    
    logging.info(f"生成的内容: {response.text}")

def test_gemini_connection():
    """测试通过 ContentPipeline 连接 Gemini"""
    try:
        load_dotenv()
        # 创建一个简化版的 ContentPipeline，避免完整初始化
        pipeline = ContentPipeline("config/pipeline_config.yml")
        
        # 检查 API 是否可用
        if not pipeline.api_available:
            pytest.skip("API 配额已耗尽，跳过测试")
        
        # 测试生成内容
        prompt = "Hello, this is a test."
        response = pipeline.model.generate_content(prompt)
        
        assert response is not None
        assert response.text is not None
        assert len(response.text) > 0
        
        logger.info(f"生成的内容: {response.text}")
    except exceptions.ResourceExhausted as e:
        logger.warning(f"API 配额已耗尽: {str(e)}")
        pytest.skip("API 配额已耗尽，跳过测试")
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        raise

def test_content_polish(test_draft):
    """测试内容润色功能"""
    try:
        pipeline = ContentPipeline("config/pipeline_config.yml")
        
        # 检查 API 是否可用
        if not pipeline.api_available:
            pytest.skip("API 配额已耗尽，跳过测试")
        
        with open(test_draft, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        content = post.content
        polished = pipeline._polish_content(content)
        
        assert polished is not None
        assert len(polished) > 0
        assert polished != content
        
        logger.info(f"原始内容长度: {len(content)}")
        logger.info(f"润色后内容长度: {len(polished)}")
    except exceptions.ResourceExhausted as e:
        logger.warning(f"API 配额已耗尽: {str(e)}")
        pytest.skip("API 配额已耗尽，跳过测试")
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
        raise

def test_error_handling(gemini_model):
    """测试错误处理"""
    try:
        # 测试空内容
        with pytest.raises(Exception) as excinfo:
            gemini_model.generate_content("")
        
        assert "contents must not be empty" in str(excinfo.value)
        logging.info(f"预期的错误处理: {str(excinfo.value)}")
    except Exception as e:
        logging.error(f"测试失败: {str(e)}")
        raise

if __name__ == "__main__":
    pytest.main(["-v", __file__]) 