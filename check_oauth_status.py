#!/usr/bin/env python3
"""
检查YouTube OAuth2配置状态
"""

import os
import json
from pathlib import Path

def check_oauth_status():
    """检查OAuth配置状态"""
    print("🔍 YouTube OAuth2配置状态检查")
    print("=" * 50)
    
    # 检查凭据文件
    credentials_file = Path("config/youtube_oauth_credentials.json")
    token_file = Path("config/youtube_oauth_token.json")
    
    print("📁 文件检查:")
    print(f"   OAuth凭据文件: {'✅ 存在' if credentials_file.exists() else '❌ 不存在'}")
    print(f"   OAuth Token文件: {'✅ 存在' if token_file.exists() else '❌ 不存在（首次使用正常）'}")
    
    if credentials_file.exists():
        try:
            with open(credentials_file, 'r') as f:
                creds = json.load(f)
            
            client_id = creds.get('installed', {}).get('client_id', '')
            client_secret = creds.get('installed', {}).get('client_secret', '')
            project_id = creds.get('installed', {}).get('project_id', '')
            
            print("\n🔑 凭据文件内容:")
            print(f"   Client ID: {client_id}")
            print(f"   Project ID: {project_id}")
            print(f"   Client Secret: {'设置' if client_secret != 'YOUR_CLIENT_SECRET' else '未设置（模板）'}")
            
            if client_id == "YOUR_CLIENT_ID.apps.googleusercontent.com":
                print("\n⚠️  检测到模板凭据文件！")
                print("📋 下一步操作:")
                print("   1. 按照 YOUTUBE_OAUTH_SETUP.md 指南创建Google Cloud OAuth凭据")
                print("   2. 下载真实的凭据JSON文件")
                print("   3. 替换 config/youtube_oauth_credentials.json")
                print("   4. 重新运行 python youtube_upload.py")
                return False
            else:
                print("✅ 凭据文件配置正确")
                return True
                
        except Exception as e:
            print(f"❌ 读取凭据文件失败: {e}")
            return False
    else:
        print("\n❌ OAuth凭据文件不存在")
        print("📋 请运行: python scripts/tools/youtube_oauth_setup.py")
        return False

def main():
    """主函数"""
    is_configured = check_oauth_status()
    
    print("\n" + "=" * 50)
    if is_configured:
        print("✅ OAuth配置完整，可以运行: python youtube_upload.py")
    else:
        print("⚠️  需要完成OAuth配置才能使用自动上传功能")
        print("📖 详细步骤请查看: YOUTUBE_OAUTH_SETUP.md")
        print("🚀 临时方案：使用 python youtube_video_gen.py 生成视频文件")

if __name__ == "__main__":
    main()