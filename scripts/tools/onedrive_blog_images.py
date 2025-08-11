#!/usr/bin/env python3
"""
OneDrive博客图床自动化系统
基于Microsoft Graph API实现博客图片自动上传和链接替换
"""

import re
import json
import os
import time
import logging
import argparse
import webbrowser
import subprocess
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs, urlencode
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from dotenv import load_dotenv

# 导入索引管理器
try:
    from onedrive_image_index import OneDriveImageIndex
except ImportError:
    OneDriveImageIndex = None

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def smart_open_browser(url: str) -> bool:
    """智能打开浏览器，适配不同环境"""
    try:
        # 检查是否在WSL环境中
        if platform.system() == "Linux":
            # 尝试检测WSL环境
            try:
                with open('/proc/version', 'r') as f:
                    proc_version = f.read()
                if 'microsoft' in proc_version.lower() or 'wsl' in proc_version.lower():
                    # WSL环境，使用powershell.exe启动浏览器
                    # 避免cmd.exe的参数解析问题
                    powershell_cmd = f'Start-Process "{url}"'
                    subprocess.run(['powershell.exe', '-Command', powershell_cmd], 
                                 check=True, capture_output=True, text=True)
                    return True
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
            
            # 非WSL Linux环境，尝试常见的浏览器命令
            browsers = ['xdg-open', 'google-chrome', 'firefox', 'chromium-browser']
            for browser in browsers:
                try:
                    subprocess.run([browser, url], check=True, 
                                 capture_output=True, text=True)
                    return True
                except (FileNotFoundError, subprocess.CalledProcessError):
                    continue
        
        # 回退到默认webbrowser模块
        webbrowser.open(url)
        return True
        
    except Exception as e:
        logger.warning(f"Failed to open browser automatically: {e}")
        return False


class AuthCallbackHandler(BaseHTTPRequestHandler):
    """OAuth回调处理器"""
    
    def do_GET(self):
        """处理OAuth回调"""
        try:
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)
            
            if 'code' in params:
                self.server.auth_code = params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                <html><body>
                <h1>Authorization Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
                <script>setTimeout(() => window.close(), 3000);</script>
                </body></html>
                """)
            elif 'error' in params:
                self.server.auth_error = params['error'][0]
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"<html><body><h1>Authorization Failed</h1><p>Error: {params['error'][0]}</p></body></html>".encode())
            else:
                self.send_response(400)
                self.end_headers()
                
        except Exception as e:
            logger.error(f"Callback handler error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def log_message(self, format, *args):
        """禁用HTTP服务器日志"""
        pass


class OneDriveAuthManager:
    """Microsoft Graph API OAuth认证管理器"""
    
    def __init__(self, config: Dict):
        self.config = config['auth']
        self.token_file = Path("config/onedrive_tokens.json")
        self.tokens = self._load_tokens()
        
    def _load_tokens(self) -> Dict:
        """加载已保存的令牌"""
        try:
            if self.token_file.exists():
                with open(self.token_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load tokens: {e}")
        return {}
    
    def _save_tokens(self, tokens: Dict):
        """保存令牌到文件"""
        try:
            self.token_file.parent.mkdir(exist_ok=True)
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(tokens, f, indent=2)
            self.tokens = tokens
            logger.info("Tokens saved successfully")
        except Exception as e:
            logger.error(f"Failed to save tokens: {e}")
    
    def get_authorization_url(self) -> str:
        """获取OAuth授权URL"""
        auth_params = {
            'client_id': self.config['client_id'],
            'response_type': 'code',
            'redirect_uri': self.config['redirect_uri'],
            'scope': ' '.join(self.config['scopes']),
            'response_mode': 'query'
        }
        
        base_url = f"https://login.microsoftonline.com/{self.config['tenant_id']}/oauth2/v2.0/authorize"
        return f"{base_url}?{urlencode(auth_params)}"
    
    def exchange_code_for_tokens(self, auth_code: str) -> Dict:
        """用授权码交换访问令牌"""
        token_url = f"https://login.microsoftonline.com/{self.config['tenant_id']}/oauth2/v2.0/token"
        
        token_data = {
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'code': auth_code,
            'redirect_uri': self.config['redirect_uri'],
            'grant_type': 'authorization_code',
            'scope': ' '.join(self.config['scopes'])
        }
        
        response = requests.post(token_url, data=token_data)
        
        if response.status_code == 200:
            tokens = response.json()
            tokens['expires_at'] = time.time() + tokens['expires_in']
            self._save_tokens(tokens)
            return tokens
        else:
            raise Exception(f"Token exchange failed: {response.text}")
    
    def refresh_access_token(self) -> str:
        """刷新访问令牌"""
        if 'refresh_token' not in self.tokens:
            raise Exception("No refresh token available")
        
        token_url = f"https://login.microsoftonline.com/{self.config['tenant_id']}/oauth2/v2.0/token"
        
        refresh_data = {
            'client_id': self.config['client_id'],
            'client_secret': self.config['client_secret'],
            'refresh_token': self.tokens['refresh_token'],
            'grant_type': 'refresh_token',
            'scope': ' '.join(self.config['scopes'])
        }
        
        response = requests.post(token_url, data=refresh_data)
        
        if response.status_code == 200:
            tokens = response.json()
            tokens['expires_at'] = time.time() + tokens['expires_in']
            # 保留旧的refresh_token如果新响应中没有
            if 'refresh_token' not in tokens and 'refresh_token' in self.tokens:
                tokens['refresh_token'] = self.tokens['refresh_token']
            self._save_tokens(tokens)
            return tokens['access_token']
        else:
            raise Exception(f"Token refresh failed: {response.text}")
    
    def get_valid_access_token(self) -> str:
        """获取有效的访问令牌"""
        if not self.tokens:
            raise Exception("No tokens available. Please run authentication first.")
        
        # 检查令牌是否即将过期（提前5分钟刷新）
        if time.time() > (self.tokens.get('expires_at', 0) - 300):
            logger.info("Token expired or expiring soon, refreshing...")
            return self.refresh_access_token()
        
        return self.tokens['access_token']
    
    def authenticate_interactive(self):
        """交互式OAuth认证流程"""
        # 检查必需配置
        if not self.config.get('client_id') or not self.config.get('client_secret'):
            raise Exception("Client ID and Secret are required. Please update config/onedrive_config.json")
        
        print("🔐 Starting OneDrive authentication...")
        
        # 启动本地HTTP服务器接收回调
        server = HTTPServer(('localhost', 8080), AuthCallbackHandler)
        server.auth_code = None
        server.auth_error = None
        
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        # 打开浏览器进行认证
        auth_url = self.get_authorization_url()
        print(f"🌐 Opening browser for authentication...")
        print(f"If browser doesn't open automatically, visit: {auth_url}")
        
        # 使用智能浏览器打开函数
        if not smart_open_browser(auth_url):
            print("⚠️  Could not open browser automatically. Please manually copy and paste the URL above.")
        
        # 等待认证回调
        print("⏳ Waiting for authentication callback...")
        timeout = 300  # 5分钟超时
        start_time = time.time()
        
        while server.auth_code is None and server.auth_error is None:
            if time.time() - start_time > timeout:
                server.shutdown()
                raise Exception("Authentication timeout")
            time.sleep(1)
        
        server.shutdown()
        
        if server.auth_error:
            raise Exception(f"Authentication failed: {server.auth_error}")
        
        if server.auth_code:
            print("✅ Authorization code received, exchanging for tokens...")
            tokens = self.exchange_code_for_tokens(server.auth_code)
            print("🎉 Authentication successful!")
            return tokens
        
        raise Exception("Authentication failed: No code received")


class OneDriveUploadManager:
    """OneDrive文件上传管理器"""
    
    def __init__(self, auth_manager: OneDriveAuthManager, config: Dict):
        self.auth = auth_manager
        self.config = config
        self.api_base = "https://graph.microsoft.com/v1.0"
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """发起Graph API请求"""
        headers = {
            'Authorization': f'Bearer {self.auth.get_valid_access_token()}',
            'Content-Type': 'application/json'
        }
        
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']
        
        url = f"{self.api_base}{endpoint}"
        response = requests.request(method, url, headers=headers, **kwargs)
        
        if response.status_code == 401:
            # 令牌可能过期，尝试刷新后重试
            logger.info("Received 401, refreshing token and retrying...")
            headers['Authorization'] = f'Bearer {self.auth.refresh_access_token()}'
            response = requests.request(method, url, headers=headers, **kwargs)
        
        return response
    
    def create_folder(self, folder_path: str) -> Dict:
        """创建文件夹（如果不存在）"""
        try:
            # 先尝试获取文件夹
            response = self._make_request('GET', f"/me/drive/root:/{folder_path}")
            if response.status_code == 200:
                return response.json()
        except:
            pass
        
        # 文件夹不存在，创建它
        folder_parts = folder_path.strip('/').split('/')
        current_path = ""
        
        for part in folder_parts:
            current_path += f"/{part}"
            try:
                response = self._make_request('GET', f"/me/drive/root:{current_path}")
                if response.status_code == 200:
                    continue
            except:
                pass
            
            # 创建文件夹
            parent_path = "/".join(current_path.strip('/').split('/')[:-1])
            parent_endpoint = f"/me/drive/root:/{parent_path}:/children" if parent_path else "/me/drive/root/children"
            
            create_data = {
                "name": part,
                "folder": {},
                "@microsoft.graph.conflictBehavior": "skip"
            }
            
            response = self._make_request('POST', parent_endpoint, json=create_data)
            if response.status_code not in [200, 201, 409]:  # 409是已存在
                logger.warning(f"Failed to create folder {current_path}: {response.text}")
        
        # 返回最终文件夹信息
        response = self._make_request('GET', f"/me/drive/root:/{folder_path}")
        return response.json() if response.status_code == 200 else {}
    
    def upload_file(self, local_path: str, remote_path: str) -> Dict:
        """上传文件到OneDrive"""
        local_file = Path(local_path)
        if not local_file.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")
        
        file_size = local_file.stat().st_size
        max_size = self.config['processing']['max_file_size_mb'] * 1024 * 1024
        
        if file_size > max_size:
            raise ValueError(f"File too large: {file_size / (1024*1024):.1f}MB > {max_size / (1024*1024)}MB")
        
        # 确保目标文件夹存在
        folder_path = '/'.join(remote_path.strip('/').split('/')[:-1])
        if folder_path:
            self.create_folder(folder_path)
        
        # 上传文件
        with open(local_file, 'rb') as file_data:
            headers = {'Content-Type': 'application/octet-stream'}
            response = self._make_request(
                'PUT',
                f"/me/drive/root:/{remote_path}:/content",
                data=file_data,
                headers=headers
            )
        
        if response.status_code in [200, 201]:
            logger.info(f"Successfully uploaded: {local_path} -> {remote_path}")
            return response.json()
        else:
            raise Exception(f"Upload failed: {response.text}")
    
    def get_sharing_link(self, item_id: str, link_type: str = 'view') -> str:
        """获取文件的分享链接"""
        share_data = {
            "type": link_type,
            "scope": "anonymous"
        }
        
        response = self._make_request('POST', f"/me/drive/items/{item_id}/createLink", json=share_data)
        
        if response.status_code in [200, 201]:
            link_info = response.json()
            return link_info['link']['webUrl']
        else:
            raise Exception(f"Failed to create sharing link: {response.text}")
    
    def get_direct_image_url(self, item_id: str) -> str:
        """获取可直接嵌入Jekyll的图片链接"""
        try:
            # 方法1: 尝试获取直接下载链接
            response = self._make_request('GET', f"/me/drive/items/{item_id}")
            if response.status_code == 200:
                item_data = response.json()
                
                # 检查是否有直接下载链接
                download_url = item_data.get('@microsoft.graph.downloadUrl')
                if download_url:
                    logger.info("Using @microsoft.graph.downloadUrl")
                    return download_url
                
                # 方法2: 构建直接访问链接
                web_url = item_data.get('webUrl', '')
                if web_url:
                    # 将OneDrive web链接转换为直接下载链接
                    # 格式: https://domain.sharepoint.com/personal/user/_layouts/15/download.aspx?UniqueId=xxx
                    if 'sharepoint.com' in web_url:
                        unique_id = item_data.get('id', '')
                        base_url = web_url.split('/personal/')[0] + '/personal/' + web_url.split('/personal/')[1].split('/')[0]
                        direct_url = f"{base_url}/_layouts/15/download.aspx?UniqueId={unique_id}"
                        logger.info("Using SharePoint direct download URL")
                        return direct_url
            
            # 方法3: 回退到分享链接
            logger.warning("Falling back to sharing link")
            return self.get_sharing_link(item_id, 'view')
            
        except Exception as e:
            logger.error(f"Failed to get direct image URL: {e}")
            return self.get_sharing_link(item_id, 'view')
    
    def convert_to_embed_link(self, share_url: str, width: int = 800) -> str:
        """将OneDrive分享链接转换为嵌入链接"""
        try:
            # 提取资源ID和认证密钥
            if '1drv.ms' in share_url:
                # 短链接需要展开
                response = requests.head(share_url, allow_redirects=True)
                share_url = response.url
            
            # 解析OneDrive链接参数
            parsed = urlparse(share_url)
            params = parse_qs(parsed.query)
            
            # 处理标准OneDrive链接格式 (onedrive.live.com)
            if 'resid' in params and 'authkey' in params:
                resid = params['resid'][0]
                authkey = params['authkey'][0]
                
                embed_params = {
                    'resid': resid,
                    'authkey': authkey,
                    'width': width
                }
                
                return f"https://onedrive.live.com/embed?{urlencode(embed_params)}"
            
            # 处理SharePoint链接格式 (xxx.sharepoint.com)
            if 'sharepoint.com' in share_url and ':i:' in share_url:
                # SharePoint图片链接格式转换为嵌入链接
                # 原始链接格式: https://domain.sharepoint.com/:i:/g/personal/user/ID?e=hash
                # 嵌入链接格式: https://domain.sharepoint.com/:i:/g/personal/user/ID (移除查询参数)
                base_url = share_url.split('?')[0]  # 移除查询参数
                return base_url
            
            # 如果无法转换，返回原链接
            return share_url
            
        except Exception as e:
            logger.warning(f"Failed to convert link to embed format: {e}")
            return share_url


class MarkdownImageProcessor:
    """Markdown文档图片处理器"""
    
    def __init__(self, upload_manager: OneDriveUploadManager, config: Dict):
        self.uploader = upload_manager
        self.config = config
        # 匹配Markdown图片链接的正则表达式
        self.image_pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')
        # 初始化索引管理器
        self.index = OneDriveImageIndex() if OneDriveImageIndex else None
        
    def find_local_images(self, content: str) -> List[Tuple[str, str, str]]:
        """查找Markdown中的本地图片链接"""
        local_images = []
        
        for match in self.image_pattern.finditer(content):
            alt_text = match.group(1)
            img_path = match.group(2)
            full_match = match.group(0)
            
            # 检查是否是本地路径
            if self._is_local_path(img_path):
                local_images.append((full_match, alt_text, img_path))
        
        return local_images
    
    def _is_local_path(self, path: str) -> bool:
        """判断是否是本地路径"""
        # Jekyll baseurl路径
        if '{{ site.baseurl }}' in path:
            return True
        # 相对路径
        if path.startswith('./') or path.startswith('../'):
            return True
        # 绝对本地路径
        if path.startswith('/') and not path.startswith('//'):
            return True
        # 不是URL
        return not (path.startswith('http://') or path.startswith('https://'))
    
    def _resolve_local_path(self, img_path: str, article_path: str) -> Optional[str]:
        """解析本地图片的实际路径"""
        try:
            article_dir = Path(article_path).parent
            
            if '{{ site.baseurl }}' in img_path:
                # Jekyll baseurl路径
                relative_path = img_path.replace('{{ site.baseurl }}/', '')
                full_path = Path(relative_path)
            elif img_path.startswith('./'):
                # 相对于文章的路径
                full_path = article_dir / img_path[2:]
            elif img_path.startswith('../'):
                # 相对于文章的上级路径
                full_path = article_dir / img_path
            elif img_path.startswith('/'):
                # 绝对路径
                full_path = Path(img_path[1:])  # 去掉开头的斜杠
            else:
                # 相对路径 - 先尝试相对于项目根目录
                full_path = Path(img_path)
                if not full_path.exists():
                    # 如果不存在，再尝试相对于文章目录
                    full_path = article_dir / img_path
            
            return str(full_path) if full_path.exists() else None
            
        except Exception as e:
            logger.warning(f"Failed to resolve path {img_path}: {e}")
            return None
    
    def _generate_remote_path(self, local_path: str, article_title: str, index: int) -> str:
        """生成OneDrive远程路径"""
        local_file = Path(local_path)
        now = datetime.now()
        
        # 格式化文件夹结构
        folder_path = self.config['onedrive']['folder_structure'].format(
            year=now.year,
            month=now.month
        )
        
        # 格式化文件名
        filename = self.config['onedrive']['filename_format'].format(
            date=now.strftime('%Y%m%d'),
            article_title=article_title[:20],  # 限制标题长度
            index=index,
            ext=local_file.suffix[1:]  # 去掉点号
        )
        
        # 清理文件名中的特殊字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        return f"{self.config['onedrive']['base_folder']}/{folder_path}/{filename}"
    
    def process_article(self, article_path: str) -> Dict:
        """处理文章中的所有图片"""
        try:
            article_file = Path(article_path)
            if not article_file.exists():
                return {'success': False, 'error': 'Article file not found'}
            
            # 读取文章内容
            with open(article_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取文章标题
            title_match = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', content, re.MULTILINE)
            article_title = title_match.group(1) if title_match else article_file.stem
            
            # 查找本地图片
            local_images = self.find_local_images(content)
            
            if not local_images:
                return {'success': True, 'message': 'No local images found', 'images_processed': 0}
            
            logger.info(f"Found {len(local_images)} local images in {article_path}")
            
            # 处理每个图片
            replacements = {}
            processed_count = 0
            
            for i, (full_match, alt_text, img_path) in enumerate(local_images, 1):
                try:
                    # 解析本地路径
                    local_path = self._resolve_local_path(img_path, article_path)
                    if not local_path:
                        logger.warning(f"Could not resolve local path: {img_path}")
                        continue
                    
                    # 生成远程路径
                    remote_path = self._generate_remote_path(local_path, article_title, i)
                    
                    # 上传文件
                    logger.info(f"Uploading {local_path} to OneDrive...")
                    upload_result = self.uploader.upload_file(local_path, remote_path)
                    
                    # 获取直接图片链接(优先)或分享链接(备用)
                    try:
                        direct_link = self.uploader.get_direct_image_url(upload_result['id'])
                        embed_link = direct_link
                        logger.info(f"Using direct image URL: {direct_link[:100]}...")
                    except Exception as e:
                        logger.warning(f"Direct link failed, using share link: {e}")
                        share_link = self.uploader.get_sharing_link(upload_result['id'])
                        embed_link = self.uploader.convert_to_embed_link(
                            share_link, 
                            self.config['links']['width']
                        )
                    
                    # 添加到索引记录
                    if self.index:
                        try:
                            self.index.add_record(
                                local_path=local_path,
                                onedrive_path=remote_path,
                                onedrive_url=share_link,
                                embed_url=embed_link,
                                article_file=article_path,
                                article_title=article_title,
                                onedrive_file_id=upload_result['id'],
                                image_index=i,
                                processing_notes=f"Uploaded from {img_path}"
                            )
                        except Exception as e:
                            logger.warning(f"Failed to add image to index: {e}")
                    
                    # 记录替换
                    new_link = f"![{alt_text}]({embed_link})"
                    replacements[full_match] = new_link
                    processed_count += 1
                    
                    # 删除本地文件（如果配置允许）
                    if self.config['processing'].get('delete_local_after_upload', False):
                        try:
                            local_file = Path(local_path)
                            if local_file.exists():
                                local_file.unlink()
                                logger.info(f"🗑️ Deleted local file: {local_path}")
                                
                                # 检查是否需要删除空目录
                                parent_dir = local_file.parent
                                if parent_dir.exists() and not any(parent_dir.iterdir()):
                                    parent_dir.rmdir()
                                    logger.info(f"🗂️ Removed empty directory: {parent_dir}")
                                    
                        except Exception as e:
                            logger.warning(f"Failed to delete local file {local_path}: {e}")
                    
                    logger.info(f"✅ Processed image {i}/{len(local_images)}: {Path(local_path).name}")
                    
                except Exception as e:
                    logger.error(f"Failed to process image {img_path}: {e}")
                    continue
            
            # 应用替换
            if replacements:
                for old_link, new_link in replacements.items():
                    content = content.replace(old_link, new_link)
                
                # 写回文件
                with open(article_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"✅ Updated {article_path} with {len(replacements)} new links")
            
            return {
                'success': True,
                'images_processed': processed_count,
                'images_found': len(local_images),
                'replacements': replacements
            }
            
        except Exception as e:
            logger.error(f"Failed to process article {article_path}: {e}")
            return {'success': False, 'error': str(e)}


class BlogImageManager:
    """博客图床系统主控制器"""
    
    def __init__(self, config_path: str = "config/onedrive_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # 初始化组件
        self.auth = OneDriveAuthManager(self.config)
        self.uploader = OneDriveUploadManager(self.auth, self.config)
        self.processor = MarkdownImageProcessor(self.uploader, self.config)
        
        # 设置日志
        self._setup_logging()
    
    def _load_config(self) -> Dict:
        """加载配置文件并合并.env环境变量"""
        try:
            # 加载.env文件
            load_dotenv()
            
            # 加载JSON配置文件
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 从环境变量覆盖敏感配置
            if 'ONEDRIVE_TENANT_ID' in os.environ:
                config['auth']['tenant_id'] = os.environ['ONEDRIVE_TENANT_ID']
            if 'ONEDRIVE_CLIENT_ID' in os.environ:
                config['auth']['client_id'] = os.environ['ONEDRIVE_CLIENT_ID']
            if 'ONEDRIVE_CLIENT_SECRET' in os.environ:
                config['auth']['client_secret'] = os.environ['ONEDRIVE_CLIENT_SECRET']
            if 'ONEDRIVE_REDIRECT_URI' in os.environ:
                config['auth']['redirect_uri'] = os.environ['ONEDRIVE_REDIRECT_URI']
                
            return config
        except Exception as e:
            raise Exception(f"Failed to load config from {self.config_path}: {e}")
    
    def _setup_logging(self):
        """设置日志"""
        log_config = self.config.get('logging', {})
        log_file = log_config.get('file')
        
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(exist_ok=True, parents=True)
            
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(file_handler)
    
    def setup_authentication(self):
        """设置认证"""
        try:
            print("🚀 OneDrive Blog Image System Setup")
            print("="*50)
            
            # 检查配置
            auth_config = self.config['auth']
            if not auth_config.get('client_id') or not auth_config.get('client_secret'):
                print("❌ Missing authentication configuration!")
                print("\nTo set up authentication:")
                print("1. Go to https://portal.azure.com/")
                print("2. Register a new application")
                print("3. Set redirect URI to: http://localhost:8080/callback")
                print("4. Generate a client secret")
                print("5. Update config/onedrive_config.json with client_id and client_secret")
                return False
            
            # 执行认证
            self.auth.authenticate_interactive()
            
            # 测试连接
            print("🧪 Testing OneDrive connection...")
            response = self.uploader._make_request('GET', '/me/drive')
            if response.status_code == 200:
                drive_info = response.json()
                total_gb = drive_info['quota']['total'] / (1024**3)
                used_gb = drive_info['quota']['used'] / (1024**3)
                print(f"✅ Connected to OneDrive: {used_gb:.1f}GB / {total_gb:.1f}GB used")
            
            print("🎉 Setup completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            print(f"❌ Setup failed: {e}")
            return False
    
    def process_draft(self, draft_path: str) -> Dict:
        """处理单个草稿文件"""
        return self.processor.process_article(draft_path)
    
    def batch_process(self, drafts_dir: str = "_drafts") -> Dict:
        """批量处理草稿目录"""
        drafts_path = Path(drafts_dir)
        if not drafts_path.exists():
            return {'success': False, 'error': 'Drafts directory not found'}
        
        results = {}
        total_processed = 0
        
        for draft_file in drafts_path.glob("*.md"):
            result = self.process_draft(str(draft_file))
            results[draft_file.name] = result
            if result.get('success'):
                total_processed += result.get('images_processed', 0)
        
        return {
            'success': True,
            'total_images_processed': total_processed,
            'files_processed': len(results),
            'detailed_results': results
        }


def main():
    parser = argparse.ArgumentParser(description='OneDrive博客图床自动化系统')
    parser.add_argument('--setup', action='store_true', help='初始化认证设置')
    parser.add_argument('--draft', help='处理指定的草稿文件')
    parser.add_argument('--batch', help='批量处理草稿目录 (默认: _drafts)')
    parser.add_argument('--config', default='config/onedrive_config.json', help='配置文件路径')
    
    args = parser.parse_args()
    
    try:
        manager = BlogImageManager(args.config)
        
        if args.setup:
            # 初始化设置
            manager.setup_authentication()
            
        elif args.draft:
            # 处理单个草稿
            print(f"📝 Processing draft: {args.draft}")
            result = manager.process_draft(args.draft)
            
            if result['success']:
                print(f"✅ Successfully processed {result.get('images_processed', 0)} images")
            else:
                print(f"❌ Failed to process draft: {result.get('error')}")
                
        elif args.batch is not None:
            # 批量处理
            drafts_dir = args.batch if args.batch else "_drafts"
            print(f"📁 Batch processing directory: {drafts_dir}")
            result = manager.batch_process(drafts_dir)
            
            if result['success']:
                print(f"✅ Batch processing completed:")
                print(f"   - Files processed: {result['files_processed']}")
                print(f"   - Images processed: {result['total_images_processed']}")
            else:
                print(f"❌ Batch processing failed: {result.get('error')}")
        else:
            # 显示帮助
            parser.print_help()
            
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    main()