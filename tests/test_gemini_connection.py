#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的 Gemini API 连接测试脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions

def test_gemini_connection():
    """测试 Gemini API 连接"""
    print("开始测试 Gemini API 连接...")
    
    # 加载环境变量
    load_dotenv(override=True)
    
    # 获取 API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ API key 未找到，请检查 .env 文件")
        return False
    
    if not api_key.startswith("AIza"):
        print("❌ API key 格式似乎无效")
        return False
    
    print(f"✓ API key 已加载 (开头为): {api_key[:10]}...")
    
    try:
        # 配置 API
        genai.configure(api_key=api_key)
        
        # 获取可用模型列表
        print("正在获取可用模型列表...")
        models = genai.list_models()
        model_names = [model.name for model in models]
        print(f"可用模型: {model_names}")
        
        # 优先选择 Gemini 2.0 Flash 模型
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
                    print(f"找到稳定版本模型: {model_name}")
                else:
                    model_name = matching_models[0]
                    print(f"找到实验版本模型: {model_name}")
                break
        
        # 如果没有找到匹配的模型，使用任何可用的 Gemini 模型
        if not model_name:
            gemini_models = [name for name in model_names if 'gemini' in name.lower()]
            if gemini_models:
                # 过滤掉已知的弃用模型
                valid_models = [name for name in gemini_models if 'gemini-1.0' not in name]
                if valid_models:
                    model_name = valid_models[0]
                else:
                    model_name = gemini_models[0]
                    print("警告：可能使用了已弃用的模型")
            else:
                model_name = "models/gemini-2.0-flash"  # 默认值
                print(f"未找到 Gemini 模型，尝试使用默认模型: {model_name}")
        
        print(f"选择使用模型: {model_name}")
        
        # 创建模型实例
        model = genai.GenerativeModel(model_name)
        
        # 测试生成内容
        try:
            print("测试生成内容...")
            response = model.generate_content("This is a test. Please respond with a brief hello.")
            
            if response and response.text:
                print(f"✅ 成功生成内容: {response.text}\n")
                return True
            else:
                print("❌ 生成内容失败：响应为空")
                return False
        except exceptions.ResourceExhausted as e:
            print(f"❌ API 配额已耗尽，请稍后再试: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_gemini_connection()
    print(f"\n测试结果: {'成功' if success else '失败'}")
    sys.exit(0 if success else 1) 