#!/usr/bin/env python3
"""
简单的Podcastfy API测试
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

from gradio_client import Client

def main():
    print("🔄 创建客户端...")
    client = Client("thatupiso/Podcastfy.ai_demo")
    
    print("🔄 测试最简单的调用...")
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # Me at the zoo (YouTube第一个视频)
    
    try:
        # 最简单的调用
        result = client.predict(
            "",  # text_input
            test_url,  # urls_input
            [],  # pdf_files  
            [],  # image_files
            os.getenv('GEMINI_API_KEY'),  # gemini_key
            "",  # openai_key
            "",  # elevenlabs_key
            200,  # word_count - 很小的数量
            "casual,informative",  # conversation_style
            "Host1",  # roles_person1
            "Host2",  # roles_person2
            "Intro,Summary,End",  # dialogue_structure
            "Test",  # podcast_name
            "Test",  # podcast_tagline
            "edge",  # tts_model
            0.5,  # creativity_level
            "Generate a short test podcast in Chinese.",  # user_instructions
            api_name="/process_inputs"
        )
        
        print(f"✅ 成功! 结果: {result}")
        print(f"结果类型: {type(result)}")
        
    except Exception as e:
        print(f"❌ 失败: {e}")
        # 打印详细的错误信息
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()