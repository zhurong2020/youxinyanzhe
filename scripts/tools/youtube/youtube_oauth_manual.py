#!/usr/bin/env python3
"""
手动YouTube OAuth2认证工具
解决浏览器自动跳转问题
"""

import os
import sys
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def manual_oauth_flow():
    """手动OAuth认证流程"""
    print("🔐 YouTube OAuth2 手动认证")
    print("=" * 50)
    
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        
        # 权限范围
        SCOPES = [
            'https://www.googleapis.com/auth/youtube.readonly',
            'https://www.googleapis.com/auth/youtube.upload'
        ]
        
        credentials_file = project_root / "config" / "youtube_oauth_credentials.json"
        token_file = project_root / "config" / "youtube_oauth_token.json"
        
        if not credentials_file.exists():
            print(f"❌ 凭据文件不存在: {credentials_file}")
            return False
        
        # 创建OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_file), SCOPES
        )
        
        # 设置redirect_uri（必须匹配Google Cloud Console中的配置）
        flow.redirect_uri = 'http://localhost:8080/'
        
        # 生成授权URL
        auth_url, _ = flow.authorization_url(
            prompt='consent', 
            access_type='offline'
        )
        
        print("\n📋 手动认证步骤:")
        print("1. 复制以下链接到浏览器:")
        print(f"\n{auth_url}\n")
        print("2. 完成Google授权")
        print("3. 授权后，浏览器会跳转到localhost:8080页面（可能显示无法访问）")
        print("4. 复制地址栏中的完整URL并粘贴到下方")
        print("5. URL应该类似: http://localhost:8080/?code=4/0Adeu5B...")
        
        # 获取用户输入的回调URL
        while True:
            callback_url = input("\n请粘贴完整的回调URL: ").strip()
            
            if not callback_url:
                print("❌ URL不能为空")
                continue
                
            if "code=" not in callback_url:
                print("❌ URL中没有找到授权码，请确保复制完整的URL")
                continue
                
            try:
                # 解析URL获取授权码
                parsed_url = urlparse(callback_url)
                query_params = parse_qs(parsed_url.query)
                
                if 'code' not in query_params:
                    print("❌ URL中没有找到code参数")
                    continue
                    
                auth_code = query_params['code'][0]
                print(f"✅ 成功提取授权码: {auth_code[:20]}...")
                break
                
            except Exception as e:
                print(f"❌ 解析URL失败: {e}")
                continue
        
        # 使用授权码获取token
        try:
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
            
            # 保存token
            token_file.parent.mkdir(exist_ok=True)
            with open(token_file, 'w') as f:
                f.write(credentials.to_json())
            
            print(f"✅ OAuth token已保存: {token_file}")
            
            # 测试API连接
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # 简单的API测试
            request = youtube.channels().list(part="snippet", mine=True)
            response = request.execute()
            
            if response.get('items'):
                channel_name = response['items'][0]['snippet']['title']
                print(f"✅ YouTube API连接成功!")
                print(f"📺 频道名称: {channel_name}")
            else:
                print("✅ YouTube API连接成功! (未找到频道信息，但认证有效)")
                
            return True
            
        except Exception as e:
            print(f"❌ 获取token失败: {e}")
            return False
            
    except ImportError:
        print("❌ 缺少依赖: pip install google-auth-oauthlib google-auth-httplib2")
        return False
    except Exception as e:
        print(f"❌ OAuth流程失败: {e}")
        return False

def main():
    """主函数"""
    success = manual_oauth_flow()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 OAuth认证完成!")
        print("现在可以运行: python youtube_upload.py")
    else:
        print("❌ OAuth认证失败")
        print("请检查Google Cloud配置或稍后重试")

if __name__ == "__main__":
    main()