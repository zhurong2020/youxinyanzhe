#!/usr/bin/env python3
"""
Google OAuth调试工具
用于诊断和解决OAuth授权问题
"""

import os
import sys
import socket
from pathlib import Path
from urllib.parse import urlparse

def check_port_availability(port):
    """检查端口是否可用"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result != 0  # 端口可用
    except:
        return False

def debug_oauth():
    """调试OAuth配置"""
    config_file = Path("config/youtube_oauth_credentials.json")
    
    if not config_file.exists():
        print("❌ OAuth配置文件不存在")
        return
    
    print("🔍 Google OAuth调试信息")
    print("=" * 50)
    
    # 检查常见端口
    common_ports = [8080, 8000, 8888, 3000, 5000]
    print("📡 端口可用性检查:")
    for port in common_ports:
        available = "✅" if check_port_availability(port) else "❌"
        print(f"   端口 {port}: {available}")
    
    # 检查配置文件
    import json
    try:
        with open(config_file) as f:
            config = json.load(f)
        
        print(f"\n📝 配置信息:")
        print(f"   项目ID: {config.get('installed', {}).get('project_id', '未知')}")
        print(f"   客户端ID: {config.get('installed', {}).get('client_id', '未知')}")
        print(f"   重定向URLs: {config.get('installed', {}).get('redirect_uris', [])}")
        
    except Exception as e:
        print(f"❌ 配置文件解析失败: {e}")
    
    # 网络连接测试
    print(f"\n🌐 网络测试:")
    try:
        import urllib.request
        response = urllib.request.urlopen('https://accounts.google.com', timeout=5)
        print(f"   ✅ Google认证服务器可访问 (状态码: {response.getcode()})")
    except Exception as e:
        print(f"   ❌ 无法连接Google认证服务器: {e}")

if __name__ == "__main__":
    debug_oauth()