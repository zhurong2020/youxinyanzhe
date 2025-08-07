#!/usr/bin/env python3
"""
Podcastfy API测试和诊断工具
用于诊断和修复API调用问题
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv(project_root / '.env')

try:
    from gradio_client import Client
    print("✅ gradio_client 导入成功")
except ImportError as e:
    print(f"❌ gradio_client 导入失败: {e}")
    print("请运行: pip install gradio-client")
    sys.exit(1)

def test_podcastfy_connection():
    """测试Podcastfy连接和API信息"""
    print("\n🔄 测试Podcastfy API连接...")
    
    try:
        client = Client("thatupiso/Podcastfy.ai_demo")
        print("✅ Podcastfy客户端连接成功")
        
        # 获取API信息
        try:
            api_info = client.view_api()
            print(f"\n📋 API信息:")
            if api_info is not None and hasattr(api_info, '__iter__') and not isinstance(api_info, (str, bytes)):
                for i, info in enumerate(api_info):
                    print(f"  {i}: {info}")
            else:
                print(f"  {api_info}")
        except Exception as e:
            print(f"⚠️ 无法获取API详细信息: {e}")
        
        return client
        
    except Exception as e:
        print(f"❌ Podcastfy连接失败: {e}")
        return None

def test_simple_api_call(client):
    """测试简单的API调用"""
    print("\n🧪 测试简单API调用...")
    
    # 测试URL - 确保没有换行符
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ".strip()
    
    try:
        # 使用正确的API调用格式
        print("📝 使用正确的API端点调用")
        print(f"🔗 测试URL: {test_url}")
        print(f"🔑 Gemini Key长度: {len(os.getenv('GEMINI_API_KEY', ''))}")
        
        result = client.predict(
            text_input="",
            urls_input=test_url,
            pdf_files=[],
            image_files=[],
            gemini_key=os.getenv('GEMINI_API_KEY', ''),
            openai_key="",
            elevenlabs_key="",
            word_count=500,  # 较小的字数用于测试
            conversation_style="casual,informative",
            roles_person1="主播助手",  # 新增参数
            roles_person2="学习导师",  # 新增参数
            dialogue_structure="引言,内容总结,结语",  # 新增参数
            podcast_name="Test Podcast",
            podcast_tagline="Testing",
            tts_model="edge",
            creativity_level=0.5,
            user_instructions="请生成一个简短的中文测试播客。",  # 新增参数
            api_name="/process_inputs"  # 正确的API端点
        )
        print(f"✅ API调用成功!")
        print(f"📄 结果类型: {type(result)}")
        if hasattr(result, '__len__'):
            print(f"📄 结果长度: {len(result)}")
        print(f"📄 结果内容: {result}")
        return result
        
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        print(f"🔍 错误详情: {str(e)}")
        return None

def main():
    """主函数"""
    print("=" * 50)
    print("🧪 Podcastfy API 诊断工具")
    print("=" * 50)
    
    # 检查环境变量
    gemini_key = os.getenv('GEMINI_API_KEY')
    print(f"GEMINI_API_KEY: {'✅ 已配置' if gemini_key else '❌ 未配置'}")
    
    if not gemini_key:
        print("⚠️ 警告: 未配置GEMINI_API_KEY，API调用可能失败")
        print("请在.env文件中配置GEMINI_API_KEY")
    
    # 测试连接
    client = test_podcastfy_connection()
    if not client:
        print("❌ 无法连接到Podcastfy，测试结束")
        return
    
    # 测试API调用
    result = test_simple_api_call(client)
    
    print("\n" + "=" * 50)
    if result:
        print("✅ API测试成功！可以使用Podcastfy生成播客")
        print(f"📄 测试结果类型: {type(result)}")
        print(f"📄 测试结果内容: {result}")
    else:
        print("❌ API测试失败，需要进一步调试")
        print("\n🔧 建议的解决方案:")
        print("1. 检查网络连接")
        print("2. 确认GEMINI_API_KEY配置正确")
        print("3. 稍后重试（服务可能暂时不可用）")
        print("4. 检查Podcastfy服务状态: https://huggingface.co/spaces/thatupiso/Podcastfy.ai_demo")
    print("=" * 50)

if __name__ == "__main__":
    main()