#!/usr/bin/env python3
"""
从完整URL中提取授权码并完成OAuth认证
"""

import sys
import json
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def complete_oauth_from_url(callback_url):
    """从回调URL完成OAuth认证"""
    print("🔐 处理YouTube OAuth2回调")
    print("=" * 50)

    try:
        # 解析URL
        parsed = urlparse(callback_url)
        params = parse_qs(parsed.query)

        if 'code' not in params:
            print("❌ URL中没有找到授权码")
            return False

        auth_code = params['code'][0]
        print(f"✅ 提取授权码: {auth_code[:30]}...")

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

        # 设置redirect_uri
        flow.redirect_uri = 'http://localhost:8080/'

        print("🔄 正在交换token...")

        # 使用授权码获取token
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials

        # 保存token
        token_file.parent.mkdir(exist_ok=True)
        with open(token_file, 'w') as f:
            f.write(credentials.to_json())

        print(f"✅ OAuth token已保存: {token_file}")

        # 测试API连接
        print("🔄 测试YouTube API连接...")
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
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 从命令行参数获取URL
        callback_url = sys.argv[1]
    else:
        # 直接使用提供的URL
        callback_url = "http://localhost:8080/?state=N7Z06dNAkIhmwrBMu3ofJtYn6cGxuF&code=4/0AVGzR1BCGuh4U8EUunXR95BogXPd-VggeQ6moNZbu8CU-M-PjyuLhIVcGJn6SkVaZxRSaQ&scope=https://www.googleapis.com/auth/youtube.upload%20https://www.googleapis.com/auth/youtube.readonly"

    print(f"📎 处理URL: {callback_url[:80]}...")

    if complete_oauth_from_url(callback_url):
        print("\n" + "=" * 50)
        print("✅ OAuth认证成功!")
        print("现在可以使用YouTube API了")
    else:
        print("\n" + "=" * 50)
        print("❌ OAuth认证失败")
        print("请检查授权码是否有效或重新进行授权")

if __name__ == "__main__":
    main()