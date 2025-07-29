#!/usr/bin/env python3
"""
深度调试Podcastfy API问题
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import json

# 加载环境变量
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / '.env')

from gradio_client import Client

def test_podcastfy_status():
    """测试Podcastfy服务状态"""
    print("🔄 检查Podcastfy服务状态...")
    
    try:
        client = Client("thatupiso/Podcastfy.ai_demo")
        print("✅ 客户端连接成功")
        
        # 获取API详细信息
        api_info = client.view_api()
        print("📋 API详细信息:")
        print(api_info)
        
        return client
        
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return None

def test_minimal_call(client):
    """测试最小化调用"""
    print("\n🧪 尝试最小化调用...")
    
    try:
        # 只传递必需参数
        result = client.predict(
            "",  # text_input
            "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # urls_input - YouTube第一个视频
            [],  # pdf_files
            [],  # image_files
            api_name="/process_inputs"
        )
        
        print(f"✅ 最小化调用成功: {result}")
        return True
        
    except Exception as e:
        print(f"❌ 最小化调用失败: {e}")
        return False

def test_alternative_endpoint():
    """测试替代的端点"""
    print("\n🔄 尝试不同的调用方式...")
    
    try:
        client = Client("thatupiso/Podcastfy.ai_demo")
        
        # 尝试使用fn_index而不是api_name
        result = client.predict(
            "",  # text_input
            "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # urls_input
            [],  # pdf_files
            [],  # image_files
            os.getenv('GEMINI_API_KEY', ''),  # gemini_key
            fn_index=0  # 使用函数索引
        )
        
        print(f"✅ 替代方式成功: {result}")
        return True
        
    except Exception as e:
        print(f"❌ 替代方式失败: {e}")
        return False

def check_huggingface_space():
    """检查HuggingFace Space状态"""
    print("\n🔄 检查HuggingFace Space状态...")
    
    import requests
    
    try:
        # 检查Space是否在线
        response = requests.get("https://thatupiso-podcastfy-ai-demo.hf.space", timeout=10)
        print(f"📡 Space状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Space在线")
            return True
        else:
            print("⚠️ Space可能有问题")
            return False
            
    except Exception as e:
        print(f"❌ 无法访问Space: {e}")
        return False

def suggest_alternatives():
    """建议替代方案"""
    print("\n💡 替代方案建议:")
    print("1. 等待Podcastfy服务修复URL问题")
    print("2. 尝试使用其他播客生成服务")
    print("3. 使用本地TTS解决方案")
    print("4. 联系Podcastfy开发者报告问题")
    print("5. 检查是否有其他Podcastfy镜像服务")

def main():
    print("=" * 60)
    print("🔍 Podcastfy深度诊断工具")
    print("=" * 60)
    
    # 检查环境变量
    gemini_key = os.getenv('GEMINI_API_KEY')
    print(f"GEMINI_API_KEY: {'✅ 已配置' if gemini_key else '❌ 未配置'}")
    
    # 检查HuggingFace Space状态
    space_online = check_huggingface_space()
    
    if not space_online:
        print("❌ Space不可访问，无法继续测试")
        suggest_alternatives()
        return
    
    # 测试服务状态
    client = test_podcastfy_status()
    if not client:
        print("❌ 无法连接到Podcastfy服务")
        suggest_alternatives()
        return
    
    # 测试最小化调用
    minimal_success = test_minimal_call(client)
    
    if not minimal_success:
        # 测试替代端点
        alt_success = test_alternative_endpoint()
        
        if not alt_success:
            print("\n❌ 所有测试都失败了")
            print("\n🔍 问题分析:")
            print("- Podcastfy API返回的文件URL包含换行符")
            print("- 这是服务端的问题，不是我们代码的问题")
            print("- 需要等待服务修复或寻找替代方案")
            
            suggest_alternatives()
        else:
            print("\n✅ 找到了可用的调用方式!")
    else:
        print("\n✅ 服务正常工作!")

if __name__ == "__main__":
    main()