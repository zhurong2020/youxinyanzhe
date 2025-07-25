#!/usr/bin/env python3
"""
微信API调试脚本
用于验证微信草稿API的正确调用方式
"""

import json
import os
import requests
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
def setup_logging():
    """设置日志配置"""
    log_dir = Path(".build/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 只使用文件日志，避免与stdout/stderr混淆
    file_handler = logging.FileHandler(log_dir / "pipeline.log", encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - [微信API调试] %(message)s'))
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    return logging.getLogger(__name__)

logger = setup_logging()

def get_access_token():
    """获取access_token"""
    appid = os.getenv('WECHAT_APPID')
    secret = os.getenv('WECHAT_APPSECRET')
    
    if not appid or not secret:
        error_msg = "❌ 请确保在.env文件中设置了WECHAT_APPID和WECHAT_APPSECRET"
        print(error_msg)
        logger.error("缺少微信API配置")
        return None
    
    url = "https://api.weixin.qq.com/cgi-bin/stable_token"
    data = {
        "grant_type": "client_credential",
        "appid": appid,
        "secret": secret,
        "force_refresh": False
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if "access_token" in result:
            print(f"✅ 成功获取access_token: {result['access_token'][:20]}...")
            return result['access_token']
        else:
            print(f"❌ 获取access_token失败: {result}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_simple_draft(access_token):
    """测试保存简单草稿"""
    
    # 极简的HTML内容
    simple_content = """
<h2>测试标题</h2>
<p>这是一个简单的测试内容。</p>
<p>不包含任何图片或复杂元素。</p>
""".strip()
    
    draft_data = {
        "articles": [{
            "title": "简单测试文章",
            "author": "测试作者",
            "digest": "这是一个简单的测试内容。",
            "content": simple_content,
            "content_source_url": "",
            "show_cover_pic": 0,
            "need_open_comment": 0,
            "only_fans_can_comment": 0
        }]
    }
    
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
    
    try:
        print("🔄 发送草稿保存请求...")
        print(f"请求URL: {url}")
        print(f"请求数据: {json.dumps(draft_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=draft_data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        print(f"📋 响应结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get("errcode") == 0:
            print("✅ 草稿保存成功！")
            return True
        else:
            print(f"❌ 草稿保存失败: {result.get('errmsg')}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_with_image_draft(access_token):
    """测试包含图片的草稿"""
    
    # 包含微信图片URL的HTML内容
    content_with_image = """
<h2>测试标题</h2>
<p>这是一个包含图片的测试内容。</p>
<p><img src="http://mmbiz.qpic.cn/mmbiz_jpg/zpzHgtJfs7URY7JX1BO1F153EB4Se8deJ7qibRiaKIichmMboPVicjLamPl55d0SODB0KiajVwbZS5WPedUXibPzic9wA/0?from=appmsg" alt="测试图片" /></p>
<p>图片测试结束。</p>
""".strip()
    
    draft_data = {
        "articles": [{
            "title": "图片测试文章",
            "author": "测试作者", 
            "digest": "这是一个包含图片的测试内容。",
            "content": content_with_image,
            "content_source_url": "",
            "show_cover_pic": 0,
            "need_open_comment": 0,
            "only_fans_can_comment": 0
        }]
    }
    
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
    
    try:
        print("🔄 发送带图片的草稿保存请求...")
        print(f"请求URL: {url}")
        print(f"请求数据: {json.dumps(draft_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=draft_data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        print(f"📋 响应结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get("errcode") == 0:
            print("✅ 带图片的草稿保存成功！")
            return True
        else:
            print(f"❌ 带图片的草稿保存失败: {result.get('errmsg')}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    print("🔧 微信草稿API调试工具")
    print("=" * 50)
    logger.info("开始微信API调试")
    
    # 1. 获取access_token
    access_token = get_access_token()
    if not access_token:
        logger.error("获取access_token失败，调试终止")
        return
    
    # 2. 测试简单草稿
    print("\n" + "=" * 50)
    print("🧪 测试1: 简单草稿（无图片）")
    success1 = test_simple_draft(access_token)
    
    # 3. 测试包含图片的草稿
    print("\n" + "=" * 50)
    print("🧪 测试2: 包含图片的草稿")
    success2 = test_with_image_draft(access_token)
    
    # 4. 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"简单草稿: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"图片草稿: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("\n🎉 所有测试通过！微信API工作正常。")
        print("💡 建议检查实际代码中的HTML内容格式。")
    elif success1:
        print("\n⚠️ 简单草稿成功，但图片草稿失败。")
        print("💡 问题可能在于图片URL格式或HTML结构。")
    else:
        print("\n❌ 基础测试失败。")
        print("💡 请检查access_token或网络连接。")

if __name__ == "__main__":
    main()