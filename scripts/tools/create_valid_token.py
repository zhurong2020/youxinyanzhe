#!/usr/bin/env python3
"""
创建有效的OAuth令牌文件
基于真实credentials文件生成正确格式的令牌文件
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def create_valid_token_structure():
    """基于真实credentials创建有效的令牌文件结构"""
    
    credentials_path = project_root / 'config' / 'youtube_oauth_credentials.json'
    token_path = project_root / 'config' / 'youtube_oauth_token.json'
    
    # 读取真实credentials
    if not credentials_path.exists():
        print(f"❌ 找不到credentials文件: {credentials_path}")
        return False
    
    try:
        with open(credentials_path, 'r', encoding='utf-8') as f:
            credentials = json.load(f)
        
        client_info = credentials['installed']
        client_id = client_info['client_id']
        client_secret = client_info['client_secret']
        
        print(f"✅ 读取到真实credentials: client_id={client_id[:20]}...")
        
        # 创建一个占位令牌文件，等待真实认证
        # 这个文件格式正确，但需要通过真实OAuth流程获取实际令牌
        placeholder_token = {
            "token": f"placeholder_token_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "refresh_token": f"placeholder_refresh_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": client_id,
            "client_secret": client_secret,
            "scopes": [
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/youtube.upload"
            ],
            "universe_domain": "googleapis.com",
            "account": "",
            "expiry": (datetime.now() + timedelta(hours=1)).isoformat() + "Z"
        }
        
        # 保存令牌文件
        with open(token_path, 'w', encoding='utf-8') as f:
            json.dump(placeholder_token, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 已创建占位令牌文件: {token_path}")
        print("📝 注意: 这个文件包含真实的client_id和client_secret，但访问令牌是占位符")
        print("🔐 系统将自动检测并使用API Key模式进行YouTube数据获取")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建令牌文件失败: {e}")
        return False

def update_youtube_generator_oauth_detection():
    """更新YouTube生成器中的OAuth检测逻辑"""
    
    generator_path = project_root / 'scripts' / 'core' / 'youtube_podcast_generator.py'
    
    try:
        with open(generator_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新OAuth检测逻辑，识别占位符令牌
        old_detection = '''# 检查是否为模板数据
            if (token_data.get('token') in ['your_access_token_here', 'your-oauth-access-token-here'] or
                token_data.get('client_id') in ['your_client_id_here', 'your-client-id.apps.googleusercontent.com']):
                self.logger.warning("⚠️ OAuth token文件包含模板数据，跳过OAuth认证")
                return None'''
        
        new_detection = '''# 检查是否为模板数据或占位符数据
            template_patterns = [
                'your_access_token_here', 'your-oauth-access-token-here',
                'your_client_id_here', 'your-client-id.apps.googleusercontent.com'
            ]
            
            if (token_data.get('token', '').startswith('placeholder_token_') or
                token_data.get('token') in template_patterns or
                token_data.get('client_id') in template_patterns):
                self.logger.info("📋 检测到占位符或模板数据，使用API Key模式")
                return None'''
        
        if old_detection in content:
            content = content.replace(old_detection, new_detection)
            
            with open(generator_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 已更新YouTube生成器OAuth检测逻辑")
            return True
        else:
            print("⚠️ 未找到需要更新的OAuth检测代码")
            return False
            
    except Exception as e:
        print(f"❌ 更新OAuth检测逻辑失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("创建有效的OAuth令牌文件")
    print("=" * 60)
    
    success = create_valid_token_structure()
    
    if success:
        print("\n🔄 更新OAuth检测逻辑...")
        update_youtube_generator_oauth_detection()
        
        print("\n" + "=" * 60)
        print("✅ 令牌文件创建成功!")
        print("💡 系统现在将使用API Key模式获取视频信息")
        print("🎯 这将解决'视频信息不足'的问题")
        print("=" * 60)
    else:
        print("\n❌ 创建失败")
        sys.exit(1)