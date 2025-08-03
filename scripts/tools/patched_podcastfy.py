#!/usr/bin/env python3
"""
修复版的Podcastfy调用器
通过猴子补丁修复URL中的换行符问题
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import re

# 加载环境变量
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / '.env')

# 导入并修复gradio_client，移除未使用的re导入以清理代码
from gradio_client import Client
import httpx

# 保存原始的httpx.stream方法
original_httpx_stream = httpx.stream

def patched_httpx_stream(method, url, **kwargs):
    """修复的httpx.stream方法，清理URL中的非打印字符"""
    if isinstance(url, str):
        # 清理URL中的换行符和其他非打印字符
        cleaned_url = re.sub(r'[\r\n\t]', '', url.strip())
        if cleaned_url != url:
            print(f"🔧 URL清理: 发现并清理了非打印字符")
        url = cleaned_url
    
    return original_httpx_stream(method, url, **kwargs)

# 应用补丁
httpx.stream = patched_httpx_stream

def test_patched_podcastfy():
    """测试修复后的Podcastfy"""
    print("🔄 使用修复版本测试Podcastfy...")
    
    try:
        client = Client("thatupiso/Podcastfy.ai_demo")
        print("✅ 客户端连接成功")
        
        # 测试简单调用
        result = client.predict(
            "",  # text_input
            "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # urls_input
            [],  # pdf_files
            [],  # image_files
            os.getenv('GEMINI_API_KEY', ''),  # gemini_key
            "",  # openai_key
            "",  # elevenlabs_key
            300,  # word_count - 很小的数量用于测试
            "casual,informative",  # conversation_style
            "主播",  # roles_person1
            "助手",  # roles_person2
            "开始,总结,结束",  # dialogue_structure
            "测试播客",  # podcast_name
            "测试",  # podcast_tagline
            "edge",  # tts_model
            0.5,  # creativity_level
            "请生成一个简短的中文测试播客",  # user_instructions
            api_name="/process_inputs"
        )
        
        print(f"✅ 测试成功!")
        print(f"📄 结果类型: {type(result)}")
        print(f"📄 结果: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("=" * 50)
    print("🔧 修复版Podcastfy测试")
    print("=" * 50)
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    print(f"GEMINI_API_KEY: {'✅ 已配置' if gemini_key else '❌ 未配置'}")
    
    if not gemini_key:
        print("❌ 需要配置GEMINI_API_KEY")
        return
    
    result = test_patched_podcastfy()
    
    if result:
        print("\n✅ 修复成功! 可以继续使用Podcastfy")
        print("💡 这个修复可以集成到主程序中")
    else:
        print("\n❌ 修复失败，需要寻找其他解决方案")

if __name__ == "__main__":
    main()