#!/usr/bin/env python3
"""
完成YouTube OAuth2认证
使用用户提供的授权码
"""

import sys
import json
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def complete_oauth_with_code(auth_code):
    """使用授权码完成OAuth认证"""
    print("🔐 完成YouTube OAuth2认证")
    print("=" * 50)
    
    try:
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
        
        # 设置redirect_uri为localhost:8080（匹配Google Cloud Console配置）
        flow.redirect_uri = 'http://localhost:8080/'
        
        print(f"✅ 使用授权码: {auth_code[:20]}...")
        
        # 使用授权码获取token
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        # 保存token
        token_file.parent.mkdir(exist_ok=True)
        with open(token_file, 'w') as f:
            f.write(credentials.to_json())
        
        print(f"✅ OAuth token已保存: {token_file}")
        
        # 测试API连接
        youtube = build('youtube', 'v3', credentials=credentials)
        
        # 获取频道信息
        request = youtube.channels().list(part="snippet", mine=True)
        response = request.execute()
        
        if response.get('items'):
            channel_name = response['items'][0]['snippet']['title']
            channel_id = response['items'][0]['id']
            print(f"✅ YouTube API连接成功!")
            print(f"📺 频道名称: {channel_name}")
            print(f"🆔 频道ID: {channel_id}")
        else:
            print("✅ YouTube API连接成功! (认证有效)")
            
        return True
        
    except Exception as e:
        print(f"❌ 完成认证失败: {e}")
        return False

def main():
    """主函数"""
    # 从你提供的URL中提取的授权码
    auth_code = "4/0AVMBsJhgpXAtymPlU7DVGjzHmQDuJ32yUkfyj5WYv46OdN9uxNqNJn7vc2hWgbgP9XDW4Q"
    
    success = complete_oauth_with_code(auth_code)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 OAuth认证完成!")
        print("现在可以运行: python youtube_upload.py")
        print("选择选项2测试单个文件上传")
    else:
        print("❌ OAuth认证失败")

if __name__ == "__main__":
    main()