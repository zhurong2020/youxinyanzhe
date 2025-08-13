#!/usr/bin/env python3
"""
恢复YouTube OAuth认证功能
基于现有的client credentials生成真实的OAuth tokens
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
import urllib.parse

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

def generate_oauth_url():
    """生成OAuth认证URL"""
    
    credentials_path = project_root / 'config' / 'youtube_oauth_credentials.json'
    
    if not credentials_path.exists():
        print("❌ 找不到credentials文件")
        return None
    
    try:
        with open(credentials_path, 'r', encoding='utf-8') as f:
            credentials = json.load(f)
        
        client_info = credentials['installed']
        client_id = client_info['client_id']
        
        # 构建OAuth URL
        base_url = "https://accounts.google.com/o/oauth2/auth"
        params = {
            'client_id': client_id,
            'redirect_uri': 'http://localhost:8080',
            'scope': 'https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        oauth_url = base_url + '?' + urllib.parse.urlencode(params)
        
        print("=" * 80)
        print("🔐 YouTube OAuth认证恢复")
        print("=" * 80)
        print()
        print("📋 请按以下步骤操作：")
        print()
        print("1️⃣ 复制下面的URL到浏览器中打开：")
        print("🔗", oauth_url)
        print()
        print("2️⃣ 在浏览器中：")
        print("   - 选择你的Google账户")
        print("   - 授权应用访问YouTube")
        print("   - 复制重定向后URL中的'code='参数值")
        print()
        print("3️⃣ 回来运行：")
        print("   python scripts/tools/restore_youtube_oauth.py exchange YOUR_CODE_HERE")
        print()
        print("=" * 80)
        
        return oauth_url
        
    except Exception as e:
        print(f"❌ 生成OAuth URL失败: {e}")
        return None

def exchange_code_for_tokens(auth_code):
    """交换授权码获取tokens"""
    
    credentials_path = project_root / 'config' / 'youtube_oauth_credentials.json'
    token_path = project_root / 'config' / 'youtube_oauth_token.json'
    
    try:
        with open(credentials_path, 'r', encoding='utf-8') as f:
            credentials = json.load(f)
        
        client_info = credentials['installed']
        client_id = client_info['client_id']
        client_secret = client_info['client_secret']
        
        # 使用requests交换code
        import requests
        
        token_url = "https://oauth2.googleapis.com/token"
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': auth_code,
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://localhost:8080'
        }
        
        print("🔄 正在交换授权码获取访问令牌...")
        response = requests.post(token_url, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            
            # 构建完整的token文件
            full_token = {
                "token": token_data.get("access_token"),
                "refresh_token": token_data.get("refresh_token"),
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": client_id,
                "client_secret": client_secret,
                "scopes": [
                    "https://www.googleapis.com/auth/youtube.readonly",
                    "https://www.googleapis.com/auth/youtube.upload"
                ],
                "universe_domain": "googleapis.com",
                "account": "",
                "expiry": None  # 会由Google库自动计算
            }
            
            # 如果有expires_in，计算过期时间
            if 'expires_in' in token_data:
                expiry = datetime.now(timezone.utc) + timedelta(seconds=token_data['expires_in'])
                full_token['expiry'] = expiry.isoformat() + "Z"
            
            # 保存token文件
            with open(token_path, 'w', encoding='utf-8') as f:
                json.dump(full_token, f, indent=2, ensure_ascii=False)
            
            print("=" * 60)
            print("✅ OAuth认证成功！")
            print(f"📁 Token已保存到: {token_path}")
            print("🎯 现在可以使用YouTube上传功能了")
            print("=" * 60)
            
            # 验证token
            verify_token()
            return True
            
        else:
            print(f"❌ 交换token失败: {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 交换token时出错: {e}")
        return False

def verify_token():
    """验证token有效性"""
    
    token_path = project_root / 'config' / 'youtube_oauth_token.json'
    
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        
        # 读取token
        with open(token_path, 'r', encoding='utf-8') as f:
            token_data = json.load(f)
        
        # 创建credentials
        creds = Credentials.from_authorized_user_info(token_data)
        
        print(f"\n🔍 Token验证:")
        print(f"   有效: {creds.valid}")
        print(f"   可刷新: {bool(creds.refresh_token)}")
        
        # 如果token过期但有refresh_token，尝试刷新
        if not creds.valid and creds.refresh_token:
            print("🔄 刷新过期token...")
            creds.refresh(Request())
            
            # 保存刷新后的token
            with open(token_path, 'w', encoding='utf-8') as f:
                f.write(creds.to_json())
            print("✅ Token刷新成功")
        
        if creds.valid:
            # 测试YouTube API
            print("🧪 测试YouTube API连接...")
            youtube = build('youtube', 'v3', credentials=creds)
            
            # 简单的API调用测试
            test_request = youtube.videos().list(
                part="snippet",
                id="dQw4w9WgXcQ",  # Rick Roll视频，肯定存在
                maxResults=1
            )
            test_response = test_request.execute()
            
            if test_response.get('items'):
                print("✅ YouTube API测试成功，OAuth认证完全可用！")
                print("🚀 现在可以使用上传功能了")
                return True
            else:
                print("⚠️ API调用成功但未返回预期结果")
        
    except Exception as e:
        print(f"❌ Token验证失败: {e}")
        return False

def main():
    if len(sys.argv) == 1:
        # 第一步：生成OAuth URL
        generate_oauth_url()
    elif len(sys.argv) == 3 and sys.argv[1] == 'exchange':
        # 第二步：交换授权码
        auth_code = sys.argv[2]
        if exchange_code_for_tokens(auth_code):
            print("\n🎉 OAuth认证恢复完成！")
            print("现在可以运行YouTube播客生成器进行上传了")
        else:
            print("❌ OAuth认证恢复失败")
            sys.exit(1)
    else:
        print("用法:")
        print("  python scripts/tools/restore_youtube_oauth.py")
        print("  python scripts/tools/restore_youtube_oauth.py exchange <authorization_code>")

if __name__ == "__main__":
    main()