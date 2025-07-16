#!/usr/bin/env python3
"""
测试永久素材管理接口
使用永久素材接口代替草稿接口
"""

import json
import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_access_token():
    """获取access_token"""
    appid = os.getenv('WECHAT_APPID')
    secret = os.getenv('WECHAT_APPSECRET')
    
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

def test_permanent_material(access_token):
    """测试永久素材管理接口"""
    
    # 简单的图文素材
    content = """
<h2>测试标题</h2>
<p>这是一个测试内容，用于验证永久素材管理接口。</p>
<p>如果您看到这个内容，说明接口调用成功。</p>
""".strip()
    
    material_data = {
        "articles": [{
            "title": "测试图文素材",
            "author": "测试作者",
            "digest": "这是一个测试内容，用于验证永久素材管理接口。",
            "content": content,
            "content_source_url": "",
            "show_cover_pic": 0
        }]
    }
    
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_news?access_token={access_token}"
    
    try:
        print("🔄 测试永久素材管理接口...")
        print(f"请求URL: {url}")
        print(f"请求数据: {json.dumps(material_data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(url, json=material_data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        print(f"📋 响应结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if "media_id" in result:
            print("✅ 永久素材创建成功！")
            print(f"📝 Media ID: {result['media_id']}")
            return result['media_id']
        elif result.get("errcode") == 0:
            print("✅ 接口调用成功！")
            return True
        else:
            print(f"❌ 失败: {result.get('errmsg', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def get_material_list(access_token):
    """获取永久素材列表"""
    
    list_data = {
        "type": "news",
        "offset": 0,
        "count": 10
    }
    
    url = f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={access_token}"
    
    try:
        print("\n🔄 获取永久素材列表...")
        response = requests.post(url, json=list_data, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        print(f"📋 素材列表: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if "item" in result:
            print(f"✅ 找到 {len(result['item'])} 个素材")
            return result['item']
        else:
            print("📭 没有找到素材")
            return []
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return []

def main():
    print("🔧 微信永久素材管理接口测试")
    print("=" * 50)
    
    # 获取access_token
    access_token = get_access_token()
    if not access_token:
        return
    
    # 测试创建永久素材
    print("\n" + "=" * 50)
    print("📝 测试创建永久素材")
    media_id = test_permanent_material(access_token)
    
    # 获取素材列表
    print("\n" + "=" * 50)
    print("📋 获取素材列表")
    materials = get_material_list(access_token)
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"创建素材: {'✅ 成功' if media_id else '❌ 失败'}")
    print(f"获取列表: {'✅ 成功' if materials else '❌ 失败'}")
    
    if media_id:
        print("\n💡 建议:")
        print("1. 永久素材管理接口工作正常")
        print("2. 可以使用此接口代替草稿功能")
        print("3. 素材创建后可以在微信公众平台后台的素材管理中查看")
        print("4. 可以手动在后台将素材发布为文章")

if __name__ == "__main__":
    main()