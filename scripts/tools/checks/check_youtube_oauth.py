#!/usr/bin/env python3
"""
YouTube OAuth状态检查工具
用于验证和监控YouTube OAuth认证的状态
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# 添加项目路径 - 智能解析
def find_project_root():
    """智能查找项目根目录"""
    current = Path(__file__).resolve()
    
    # 向上查找包含run.py和scripts目录的目录
    for path in [current] + list(current.parents):
        if (path / 'run.py').exists() and (path / 'scripts').exists():
            return path
    
    # 后备：使用当前工作目录
    if (Path.cwd() / 'run.py').exists():
        return Path.cwd()
    
    # 最后后备：传统计算
    return Path(__file__).parent.parent.parent

project_root = find_project_root()
sys.path.append(str(project_root))

# 配置日志
def setup_logging():
    """设置日志配置"""
    log_dir = Path(".build/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 只使用文件日志，避免与stdout/stderr混淆
    file_handler = logging.FileHandler(log_dir / "pipeline.log", encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - [YouTube OAuth检查] %(message)s'))
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    return logging.getLogger(__name__)

logger = setup_logging()

def check_oauth_files():
    """检查OAuth相关文件"""
    credentials_file = Path("config/youtube_oauth_credentials.json")
    token_file = Path("config/youtube_oauth_token.json")
    
    results = {
        'credentials_exists': credentials_file.exists(),
        'token_exists': token_file.exists(),
        'credentials_valid': False,
        'token_valid': False,
        'client_id': None,
        'project_id': None,
        'token_expiry': None,
        'scopes': []
    }
    
    # 检查凭据文件
    if results['credentials_exists']:
        try:
            with open(credentials_file, 'r') as f:
                creds_data = json.load(f)
            
            if 'installed' in creds_data:
                client_id = creds_data['installed'].get('client_id', '')
                project_id = creds_data['installed'].get('project_id', '')
                
                # 检查是否是模板数据
                if client_id != "YOUR_CLIENT_ID.apps.googleusercontent.com":
                    results['credentials_valid'] = True
                    results['client_id'] = client_id
                    results['project_id'] = project_id
                    
        except Exception as e:
            logger.error(f"读取凭据文件失败: {e}")
    
    # 检查token文件
    if results['token_exists']:
        try:
            with open(token_file, 'r') as f:
                token_data = json.load(f)
            
            # 检查是否是占位符token
            token = token_data.get('token', '')
            if not token.startswith('placeholder_token_'):
                results['token_valid'] = True
                results['token_expiry'] = token_data.get('expiry')
                results['scopes'] = token_data.get('scopes', [])
                
        except Exception as e:
            logger.error(f"读取token文件失败: {e}")
    
    return results

def test_youtube_api_connection():
    """测试YouTube API连接"""
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request
        
        token_file = Path("config/youtube_oauth_token.json")
        if not token_file.exists():
            return {'success': False, 'error': 'Token文件不存在'}
        
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        creds = Credentials.from_authorized_user_info(token_data)
        
        # 检查并刷新token
        if not creds.valid:
            if creds.refresh_token:
                creds.refresh(Request())
            else:
                return {'success': False, 'error': 'Token无效且无法刷新'}
        
        # 创建YouTube客户端并测试
        youtube = build('youtube', 'v3', credentials=creds)
        
        # 测试API调用
        channels_response = youtube.channels().list(
            part='snippet',
            mine=True,
            maxResults=1
        ).execute()
        
        if channels_response.get('items'):
            channel = channels_response['items'][0]
            return {
                'success': True,
                'channel_name': channel['snippet']['title'],
                'channel_id': channel['id']
            }
        else:
            return {'success': False, 'error': '未找到YouTube频道'}
            
    except ImportError:
        return {'success': False, 'error': '缺少必要的Python包'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    """主检查函数"""
    print("🔍 YouTube OAuth状态检查")
    logger.info("开始YouTube OAuth状态检查")
    
    # 检查OAuth文件
    file_results = check_oauth_files()
    
    print("\n📁 文件检查:")
    print(f"   OAuth凭据文件: {'✅ 存在' if file_results['credentials_exists'] else '❌ 不存在'}")
    print(f"   OAuth Token文件: {'✅ 存在' if file_results['token_exists'] else '❌ 不存在'}")
    
    if file_results['credentials_valid']:
        print(f"   客户端ID: {file_results['client_id']}")
        print(f"   项目ID: {file_results['project_id']}")
        print("   ✅ 凭据文件配置正确")
    elif file_results['credentials_exists']:
        print("   ⚠️ 凭据文件存在但可能是模板数据")
    
    if file_results['token_valid']:
        print("   ✅ Token文件有效")
        if file_results['token_expiry']:
            try:
                # 解析过期时间
                if 'T' in file_results['token_expiry']:
                    expiry_dt = datetime.fromisoformat(file_results['token_expiry'].replace('Z', '+00:00'))
                    now_dt = datetime.now(expiry_dt.tzinfo)
                    if expiry_dt > now_dt:
                        delta = expiry_dt - now_dt
                        print(f"   ⏰ Token过期时间: {delta.days}天后")
                    else:
                        print("   ⚠️ Token已过期")
            except:
                print(f"   ⏰ Token过期时间: {file_results['token_expiry']}")
        
        if file_results['scopes']:
            print(f"   🔑 权限范围: {len(file_results['scopes'])}个")
            for scope in file_results['scopes']:
                scope_name = scope.split('/')[-1]
                print(f"      • {scope_name}")
    elif file_results['token_exists']:
        print("   ❌ Token文件无效（可能是占位符数据）")
    
    # 测试API连接
    if file_results['credentials_valid'] and file_results['token_valid']:
        print("\n🧪 API连接测试:")
        api_result = test_youtube_api_connection()
        
        if api_result['success']:
            print("   ✅ YouTube API连接成功")
            print(f"   📺 频道名称: {api_result['channel_name']}")
            print(f"   🆔 频道ID: {api_result['channel_id']}")
            logger.info(f"YouTube API连接成功 - 频道: {api_result['channel_name']}")
        else:
            print(f"   ❌ API连接失败: {api_result['error']}")
            logger.warning(f"YouTube API连接失败: {api_result['error']}")
    
    # 总结状态
    print("\n📊 OAuth状态总结:")
    oauth_ready = file_results['credentials_valid'] and file_results['token_valid']
    
    if oauth_ready:
        # 进一步验证API连接
        api_result = test_youtube_api_connection()
        if api_result['success']:
            print("   🎉 ✅ 完全配置，可以上传YouTube视频")
            logger.info("YouTube OAuth配置完整且功能正常")
        else:
            print("   ⚠️ 文件配置正确但API连接失败")
            print(f"   💡 建议: {api_result['error']}")
            logger.warning(f"YouTube OAuth配置不完整: {api_result['error']}")
    else:
        print("   ❌ 需要配置OAuth认证")
        missing_items = []
        if not file_results['credentials_valid']:
            missing_items.append("OAuth凭据文件")
        if not file_results['token_valid']:
            missing_items.append("有效的认证Token")
        
        print(f"   💡 缺少: {', '.join(missing_items)}")
        print("   📋 请运行 'python run.py' → '4. YouTube内容处理' → '3. YouTube平台上传' → '4. YouTube OAuth管理'")
        logger.warning(f"YouTube OAuth配置不完整，缺少: {', '.join(missing_items)}")

if __name__ == "__main__":
    main()