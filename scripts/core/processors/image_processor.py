"""
图片处理模块
负责图片路径检查、下载、转换和管理
"""
import re
import shutil
import tempfile
import hashlib
import urllib.parse
import requests
import frontmatter
import logging
from pathlib import Path
from typing import Dict, List, Optional


class ImageProcessor:
    """图片处理器 - 负责图片相关的所有操作"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化图片处理器
        
        Args:
            logger: 日志记录器
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def log(self, message: str, level: str = "info") -> None:
        """
        记录日志
        
        Args:
            message: 日志消息
            level: 日志级别
        """
        if self.logger:
            getattr(self.logger, level)(message)
    
    def check_image_paths(self, content: str) -> List[str]:
        """
        检查内容中的图片路径问题
        
        Args:
            content: 文章内容
            
        Returns:
            问题图片路径列表
        """
        # 查找所有图片引用
        image_patterns = [
            r'!\[.*?\]\((.*?)\)',  # Markdown 图片
            r'<img[^>]+src=["\']([^"\']+)["\']',  # HTML img 标签
        ]
        
        problematic_images = []
        
        for pattern in image_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                image_path = match.strip()
                
                # 检查是否是本地assets路径（需要OneDrive处理）
                if ('assets/images/' in image_path and 
                    not image_path.startswith('http') and 
                    not '{{ site.baseurl }}' in image_path):
                    problematic_images.append(image_path)
                
                # 检查是否是绝对路径（Jekyll不兼容）
                elif image_path.startswith('/assets/'):
                    problematic_images.append(image_path)
        
        return problematic_images
    
    def process_post_images(self, post_path: Path) -> Dict[str, str]:
        """
        处理文章中的图片
        
        Args:
            post_path: 文章文件路径
            
        Returns:
            图片处理结果字典 {图片名称: 本地路径}
        """
        # 获取文章中的本地图片
        local_images = {}
        temp_dir = None
        
        try:
            # 创建临时目录用于存储下载的图片
            temp_dir = Path(tempfile.mkdtemp())
            self.log(f"创建临时目录用于存储下载的图片: {temp_dir}", level="debug")
            
            with open(post_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 尝试解析 front matter
                try:
                    post = frontmatter.loads(content)
                except Exception as e:
                    self.log(f"⚠️ 解析 front matter 失败: {str(e)}", level="warning")
                    # 尝试修复 front matter
                    content = self._fix_frontmatter_quotes(content)
                    try:
                        post = frontmatter.loads(content)
                    except Exception as e:
                        self.log(f"❌ 修复后仍无法解析 front matter: {str(e)}", level="error")
                        return {}
                
                # 处理header中的图片
                local_images.update(self._process_header_images(post, temp_dir))
                
                # 处理markdown内容中的图片
                local_images.update(self._process_content_images(content, temp_dir))
            
            if not local_images:
                self.log("没有找到任何有效的图片", level="warning")
                return {}
            
            # 图片处理功能已移除（不再使用Cloudflare Images）
            self.log(f"发现 {len(local_images)} 张图片，但图片上传功能已移除", level="info")
            return {}
        
        except Exception as e:
            self.log(f"处理文章图片时出错: {str(e)}", level="error")
            return {}
        
        finally:
            # 清理临时目录
            self._cleanup_temp_directory(temp_dir)
    
    def _process_header_images(self, post: frontmatter.Post, temp_dir: Path) -> Dict[str, Path]:
        """
        处理front matter header中的图片
        
        Args:
            post: frontmatter解析后的文章对象
            temp_dir: 临时目录
            
        Returns:
            图片字典 {图片名称: 本地路径}
        """
        local_images = {}
        
        if 'header' not in post:
            return local_images
        
        header = post.get('header', {})
        if not isinstance(header, dict):
            return local_images
        
        # 处理各种header图片字段
        img_fields = ['image', 'og_image', 'overlay_image', 'teaser']
        
        for img_field in img_fields:
            if img_field not in header:
                continue
                
            img_path = header[img_field]
            if not img_path:
                continue
                
            # 处理OneDrive链接
            if self._is_onedrive_url(img_path):
                try:
                    self.log(f"发现OneDrive头图: {img_field} = {img_path}", level="info")
                    img_name = self._download_onedrive_image(img_path, temp_dir)
                    if img_name:
                        local_images[img_name] = temp_dir / img_name
                        self.log(f"成功下载OneDrive头图: {img_name}", level="info")
                except Exception as e:
                    self.log(f"下载OneDrive头图失败: {str(e)}", level="error")
                    
            # 处理本地图片
            elif img_path.startswith('/assets/images/'):
                name = Path(img_path).name
                full_path = Path.cwd() / img_path.lstrip('/')
                if full_path.exists():
                    local_images[name] = full_path
                    self.log(f"找到头图: {name}", level="debug")
                else:
                    self.log(f"头图不存在: {img_path}", level="warning")
        
        return local_images
    
    def _process_content_images(self, content: str, temp_dir: Path) -> Dict[str, Path]:
        """
        处理markdown内容中的图片
        
        Args:
            content: 文章内容
            temp_dir: 临时目录
            
        Returns:
            图片字典 {图片名称: 本地路径}
        """
        local_images = {}
        
        # 查找markdown图片语法
        for match in re.finditer(r'!\[.*?\]\((.*?)\)', content):
            img_path = match.group(1)
            
            # 跳过已经是本地路径的图片
            if img_path.startswith('/assets/images/'):
                self.log(f"跳过已有的本地图片路径: {img_path}", level="debug")
                continue
            
            # 处理OneDrive链接
            if self._is_onedrive_url(img_path):
                try:
                    self.log(f"发现OneDrive正文图片: {img_path}", level="info")
                    img_name = self._download_onedrive_image(img_path, temp_dir)
                    if img_name:
                        local_images[img_name] = temp_dir / img_name
                        self.log(f"成功下载OneDrive正文图片: {img_name}", level="info")
                except Exception as e:
                    self.log(f"下载OneDrive正文图片失败: {str(e)}", level="error")
                    
            # 处理本地图片
            elif img_path.startswith('/assets/images/'):
                name = Path(img_path).name
                full_path = Path.cwd() / img_path.lstrip('/')
                
                if full_path.exists():
                    local_images[name] = full_path
                    self.log(f"找到正文图片: {name}", level="debug")
                else:
                    self.log(f"正文图片不存在: {img_path}", level="warning")
        
        return local_images
    
    def _download_onedrive_image(self, url: str, temp_dir: Path) -> Optional[str]:
        """
        下载OneDrive图片
        
        Args:
            url: OneDrive图片URL
            temp_dir: 临时目录
            
        Returns:
            成功返回图片文件名，失败返回None
        """
        try:
            self.log(f"下载OneDrive图片: {url}", level="info")
            
            # 提取OneDrive URL中的唯一标识符
            unique_id = self._extract_onedrive_id(url)
            
            # 下载图片
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # 尝试从响应头中获取文件扩展名
            content_type = response.headers.get('content-type', '')
            extension = self._get_extension_from_content_type(content_type)
            
            # 生成文件名
            filename = f"onedrive_{unique_id}{extension}"
            file_path = temp_dir / filename
            
            # 保存文件
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.log(f"成功下载OneDrive图片: {filename}", level="info")
            return filename
            
        except Exception as e:
            self.log(f"下载OneDrive图片失败: {str(e)}", level="error")
            return None
    
    def _extract_onedrive_id(self, url: str) -> str:
        """
        从OneDrive URL中提取唯一标识符
        
        Args:
            url: OneDrive URL
            
        Returns:
            唯一标识符字符串
        """
        unique_id = None
        
        if 'onedrive.live.com' in url and 'resid=' in url:
            # 例如：https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169891&authkey=%21AFppTKcu8cfS2Eo&width=660
            resid_match = re.search(r'resid=([^&]+)', url)
            if resid_match:
                resid = resid_match.group(1)
                # 解码URL编码的字符
                resid = urllib.parse.unquote(resid)
                self.log(f"从URL中提取的resid: {resid}", level="debug")
                
                # 提取resid中的数字部分作为唯一标识符
                id_match = re.search(r'([0-9]+)$', resid)
                if id_match:
                    unique_id = id_match.group(1)
                    self.log(f"从resid中提取的唯一标识符: {unique_id}", level="debug")
        
        # 如果无法从URL中提取唯一标识符，则使用URL的哈希值
        if not unique_id:
            unique_id = hashlib.md5(url.encode()).hexdigest()[:5]
            self.log(f"使用URL哈希值作为唯一标识符: {unique_id}", level="debug")
        
        return unique_id
    
    def _get_extension_from_content_type(self, content_type: str) -> str:
        """
        根据content-type获取文件扩展名
        
        Args:
            content_type: HTTP响应的content-type
            
        Returns:
            文件扩展名（包含点号）
        """
        extension_map = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/bmp': '.bmp',
            'image/svg+xml': '.svg'
        }
        
        return extension_map.get(content_type.lower(), '.jpg')  # 默认为jpg
    
    def _is_onedrive_url(self, url: str) -> bool:
        """
        检查URL是否为OneDrive链接
        
        Args:
            url: 要检查的URL
            
        Returns:
            是否为OneDrive URL
        """
        return '1drv.ms' in url or 'onedrive.live.com' in url
    
    def _fix_frontmatter_quotes(self, content: str) -> str:
        """
        修复front matter中的引号问题
        
        Args:
            content: 文章内容
            
        Returns:
            修复后的内容
        """
        # 这里可以添加具体的修复逻辑
        # 目前只是返回原内容
        return content
    
    def _cleanup_temp_directory(self, temp_dir: Optional[Path]) -> None:
        """
        清理临时目录
        
        Args:
            temp_dir: 要清理的临时目录
        """
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
                self.log(f"清理临时目录: {temp_dir}", level="debug")
            except Exception as e:
                self.log(f"清理临时目录失败: {str(e)}", level="warning")
    
    def replace_images_in_content(self, content: str, images: Dict[str, str], _temp_dir_path: Optional[Path] = None) -> str:
        """
        替换内容中的图片路径
        
        Args:
            content: 文章内容
            images: 图片映射字典 {原路径: 新路径}
            temp_dir_path: 临时目录路径
            
        Returns:
            替换后的内容
        """
        # 替换markdown图片语法中的路径
        def replace_markdown_image(match):
            alt_text = match.group(1)
            img_path = match.group(2)
            
            # 如果有对应的替换路径，则替换
            if img_path in images:
                new_path = images[img_path]
                return f'![{alt_text}]({new_path})'
            return match.group(0)
        
        # 应用替换
        content = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_markdown_image, content)
        
        return content
    
    def update_header_images(self, post: dict, images: Dict[str, str]) -> dict:
        """
        更新header中的图片路径
        
        Args:
            post: 文章字典
            images: 图片映射字典
            
        Returns:
            更新后的文章字典
        """
        if 'header' not in post:
            return post
        
        header = post.get('header', {})
        if not isinstance(header, dict):
            return post
        
        # 更新各种header图片字段
        img_fields = ['image', 'og_image', 'overlay_image', 'teaser']
        
        for img_field in img_fields:
            if img_field in header and header[img_field] in images:
                header[img_field] = images[header[img_field]]
        
        return post
    
    def is_same_onedrive_image(self, onedrive_url: str, image_name: str) -> bool:
        """
        检查OneDrive URL是否对应指定的图片名称
        
        Args:
            onedrive_url: OneDrive URL
            image_name: 图片名称
            
        Returns:
            是否匹配
        """
        if not self._is_onedrive_url(onedrive_url):
            return False
        
        # 提取URL中的唯一标识符
        url_id = self._extract_onedrive_id(onedrive_url)
        
        # 检查图片名称是否包含这个标识符
        return url_id in image_name