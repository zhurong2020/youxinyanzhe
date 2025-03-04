import os
import yaml
import requests
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv
from . import setup_logger

class CloudflareImageMapper:
    """Cloudflare 图片处理和映射管理"""
    
    def __init__(self, account_id: str, account_hash: str, api_token: str, config_path: str = "config/cloudflare_config.yml"):
        """
        初始化 Cloudflare Images 客户端
        
        Args:
            account_id: Cloudflare 账户 ID
            account_hash: Cloudflare 账户 Hash
            api_token: Cloudflare API 令牌
            config_path: 配置文件路径
        """
        # 设置logger
        self.logger = setup_logger("CloudflareImageMapper")
        self.logger.info("初始化 Cloudflare 图片处理器")
        
        # 记录配置信息
        self.logger.debug(f"账户ID: {account_id[:8]}...")
        self.logger.debug(f"配置文件: {config_path}")
        
        self.account_id = account_id
        self.account_hash = account_hash
        self.api_token = api_token
        self.headers = {"Authorization": f"Bearer {api_token}"}
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1"
        
        # 加载配置
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                self.config = config["image_processing"]["cloudflare"]
                
            # 初始化映射文件路径
            self.mapping_file = Path(self.config["mapping_file"])
            self.mappings = self._load_mappings()
            
            # 配置重试策略
            self.retry_config = self.config.get("retry", {
                "max_attempts": 3,
                "initial_delay": 1.0,
                "max_delay": 10.0
            })
            
        except Exception as e:
            logging.error(f"加载配置失败: {str(e)}")
            raise
        
    def _load_mappings(self) -> Dict:
        """加载现有的图片映射关系"""
        if self.mapping_file.exists():
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {"posts": {}}
        
    def _save_mapping(self, image_path: Path, image_id: str):
        """保存图片ID映射"""
        try:
            # 将 Windows 路径转换为 POSIX 路径
            image_path = Path(str(image_path).replace('\\', '/'))
            base_path = Path('assets/images/posts').resolve()
            
            # 获取相对路径
            try:
                rel_path = image_path.relative_to(base_path)
                # 将路径转换为字符串列表
                parts = list(rel_path.parts)
                
                # 构建嵌套字典
                current = self.mappings["posts"]
                for part in parts[:-1]:  # 年/月/文章名
                    current = current.setdefault(part, {})
                
                # 保存映射
                current[parts[-1]] = image_id  # 图片名: ID
                
                # 确保目录存在
                self.mapping_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 写入文件
                with open(self.mapping_file, 'w', encoding='utf-8') as f:
                    yaml.dump(self.mappings, f, allow_unicode=True, sort_keys=False)
                
                self.logger.info(f"✅ 已保存图片映射: {parts[-1]} -> {image_id}")
                
            except ValueError:
                self.logger.warning(f"图片不在基础路径下: {image_path}")
                return
            
        except Exception as e:
            self.logger.error(f"保存图片映射失败: {str(e)}")
            
    def get_cloudflare_url(self, image_id: str, variant: str = "public") -> str:
        """获取 Cloudflare 图片 URL"""
        return f"https://imagedelivery.net/{self.account_hash}/{image_id}/{variant}"
        
    def upload_image(self, image_path: Path) -> Optional[str]:
        """上传单个图片到 Cloudflare Images
        
        Returns:
            成功返回图片 URL，失败返回 None
        """
        try:
            self.logger.info(f"开始上传图片: {image_path.name}")
            self.logger.debug(f"完整路径: {image_path}")
            
            if not image_path.exists():
                self.logger.error(f"图片不存在: {image_path}")
                return None
                
            # 上传图片
            with open(image_path, 'rb') as f:
                files = {'file': (image_path.name, f, 'image/webp' if image_path.suffix == '.webp' else 'image/jpeg')}
                self.logger.debug(f"准备上传请求: {files}")
                response = requests.post(self.base_url, headers=self.headers, files=files)
            
            self.logger.debug(f"API响应: {response.status_code}")
            self.logger.debug(f"响应内容: {response.text[:200]}...")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    image_id = result['result']['id']
                    # 保存映射关系
                    self._save_mapping(image_path, image_id)
                    url = self.get_cloudflare_url(image_id)
                    self.logger.info(f"上传成功: {image_path.name} -> {url}")
                    return url
            
            self.logger.error(f"上传失败: {response.text}")
            return None
            
        except Exception as e:
            self.logger.error(f"上传出错: {str(e)}", exc_info=True)
            return None
            
    def map_images(self, local_images: Dict[str, Path]) -> Dict[str, str]:
        """批量处理图片
        
        Args:
            local_images: {图片名: 图片路径}
            
        Returns:
            {图片名: Cloudflare URL}
        """
        result = {}
        for name, path in local_images.items():
            if url := self.upload_image(path):
                result[name] = url
                
        return result 