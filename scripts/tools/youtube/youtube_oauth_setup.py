#!/usr/bin/env python3
"""
YouTube OAuth2认证设置工具
"""

import os
import json
from pathlib import Path
from typing import Optional

def create_oauth_credentials_template():
    """创建OAuth认证凭据模板"""
    
    template = {
        "installed": {
            "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
            "project_id": "your-project-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "YOUR_CLIENT_SECRET",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
        }
    }
    
    credentials_file = Path("config/youtube_oauth_credentials.json")
    credentials_file.parent.mkdir(exist_ok=True)
    
    with open(credentials_file, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2)
    
    print(f"✅ OAuth凭据模板已创建: {credentials_file}")
    return credentials_file

def setup_oauth_instructions():
    """显示OAuth设置说明"""
    
    instructions = """
🔧 YouTube OAuth2 设置指南
============================

YouTube上传API需要OAuth2认证。请按以下步骤设置：

1️⃣ 创建Google Cloud项目
   • 访问: https://console.cloud.google.com/
   • 创建新项目或选择现有项目
   • 启用YouTube Data API v3

2️⃣ 创建OAuth2凭据
   • 转到"APIs & Services" > "Credentials"
   • 点击"Create Credentials" > "OAuth client ID"
   • 选择"Desktop application"
   • 下载JSON文件

3️⃣ 配置凭据文件
   • 将下载的JSON文件重命名为: youtube_oauth_credentials.json
   • 放置在项目的 config/ 目录下
   • 或者编辑模板文件并填入你的凭据

4️⃣ 首次认证
   • 运行工具时会自动打开浏览器进行授权
   • 完成授权后会保存token用于后续使用

⚠️ 注意事项:
   • OAuth凭据文件包含敏感信息，不要提交到Git
   • 首次使用需要在浏览器中完成授权
   • 授权token会自动保存和刷新
"""
    
    print(instructions)

def main():
    """主函数"""
    print("🎬 YouTube OAuth2 设置工具")
    print("=" * 50)
    
    setup_oauth_instructions()
    
    print("\n📝 可用操作:")
    print("1. 创建OAuth凭据模板文件")
    print("2. 显示详细设置说明")
    print("0. 退出")
    
    while True:
        choice = input("\n请选择操作 (0-2): ").strip()
        
        if choice == "0":
            break
        elif choice == "1":
            create_oauth_credentials_template()
            print("\n💡 请编辑生成的模板文件，填入你的OAuth凭据")
        elif choice == "2":
            setup_oauth_instructions()
        else:
            print("❌ 无效选择")

if __name__ == "__main__":
    main()