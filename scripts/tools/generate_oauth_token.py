#!/usr/bin/env python3
"""
YouTube OAuth Token Generator
使用真实的credentials文件生成有效的OAuth令牌
"""

import json
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import webbrowser
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import threading
import time

# YouTube API 权限范围
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def create_oauth_token():
    """创建有效的OAuth令牌"""
    
    # 读取真实的credentials文件
    credentials_path = project_root / 'config' / 'youtube_oauth_credentials.json'
    token_path = project_root / 'config' / 'youtube_oauth_token.json'
    
    if not credentials_path.exists():
        print(f"❌ 找不到credentials文件: {credentials_path}")
        return False
    
    print(f"✅ 找到真实credentials文件: {credentials_path}")
    
    # 检查现有令牌
    creds = None
    if token_path.exists():
        try:
            with open(token_path, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
            
            # 检查是否为模板数据
            if token_data.get('token') == 'your_access_token_here':
                print("⚠️ 检测到模板数据，需要重新生成令牌")
                creds = None
            else:
                creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
                print("📋 找到现有令牌文件")
        except Exception as e:
            print(f"⚠️ 读取现有令牌失败: {e}")
            creds = None
    
    # 验证或刷新现有令牌
    if creds and creds.valid:
        print("✅ 现有令牌有效")
        return True
    elif creds and creds.expired and creds.refresh_token:
        print("🔄 尝试刷新过期令牌...")
        try:
            creds.refresh(Request())
            print("✅ 令牌刷新成功")
        except Exception as e:
            print(f"❌ 令牌刷新失败: {e}")
            creds = None
    
    # 如果没有有效令牌，创建新的
    if not creds:
        print("🔐 开始OAuth认证流程...")
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES)
            
            # 使用本地服务器模式
            print("🌐 启动本地服务器接收认证回调...")
            creds = flow.run_local_server(port=8080, open_browser=False)
            
            print("📝 请在浏览器中访问以下URL完成认证:")
            auth_url = flow.authorization_url()[0]
            print(f"🔗 {auth_url}")
            
        except Exception as e:
            print(f"❌ OAuth流程失败: {e}")
            return False
    
    # 保存令牌
    try:
        with open(token_path, 'w', encoding='utf-8') as f:
            f.write(creds.to_json())
        print(f"✅ 令牌已保存到: {token_path}")
        
        # 验证保存的令牌
        with open(token_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        if saved_data.get('token', '').startswith('ya29.'):
            print("✅ 令牌格式验证通过")
            return True
        else:
            print("⚠️ 令牌格式可能有问题")
            return False
            
    except Exception as e:
        print(f"❌ 保存令牌失败: {e}")
        return False

def verify_token():
    """验证令牌有效性"""
    token_path = project_root / 'config' / 'youtube_oauth_token.json'
    
    if not token_path.exists():
        print("❌ 令牌文件不存在")
        return False
    
    try:
        with open(token_path, 'r', encoding='utf-8') as f:
            token_data = json.load(f)
        
        # 检查关键字段
        required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret']
        for field in required_fields:
            if field not in token_data:
                print(f"❌ 令牌文件缺少字段: {field}")
                return False
            # 检查各种模板数据格式
            template_patterns = [
                'your_access_token_here', 'your_refresh_token_here', 
                'your_client_id_here', 'your_client_secret_here',
                'your-oauth-access-token-here', 'your-oauth-refresh-token-here',
                'your-client-id.apps.googleusercontent.com', 'your-client-secret'
            ]
            if token_data[field] in template_patterns:
                print(f"❌ 字段 {field} 仍为模板数据: {token_data[field]}")
                return False
        
        # 创建Credentials对象验证
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
        if creds.valid:
            print("✅ 令牌验证通过，可以使用")
            return True
        elif creds.expired:
            print("⚠️ 令牌已过期，但可以刷新")
            return True
        else:
            print("❌ 令牌无效")
            return False
            
    except Exception as e:
        print(f"❌ 验证令牌时出错: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("YouTube OAuth 令牌生成器")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'verify':
        print("🔍 验证现有令牌...")
        if verify_token():
            sys.exit(0)
        else:
            sys.exit(1)
    
    print("🚀 开始生成OAuth令牌...")
    success = create_oauth_token()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ OAuth令牌生成成功!")
        print("现在可以使用YouTube上传功能了")
        print("=" * 50)
        sys.exit(0)
    else:
        print("\n" + "=" * 50)
        print("❌ OAuth令牌生成失败")
        print("请检查网络连接和credentials文件")
        print("=" * 50)
        sys.exit(1)