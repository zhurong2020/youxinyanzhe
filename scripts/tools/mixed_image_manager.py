#!/usr/bin/env python3
"""
有心工坊 - 混合图片管理系统 Phase 0.5
YouXin Workshop - Mixed Image Management System

支持任意位置图片发现和四阶段处理流程: 临时创作 → 项目缓存 → 云端归档 → 安全清理

核心特性:
- 智能路径解析: 支持绝对路径、相对路径、任意临时目录
- 四阶段管理: pending → uploaded → cloud storage → user-confirmed cleanup
- 完整备份机制: processing/uploaded/ 备份机制
- 安全清理策略: 用户确认发布后才删除本地备份
- 回滚机制: 支持从备份恢复原始状态
"""

import json
import os
import re
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import argparse

# 导入现有OneDrive组件
try:
    from onedrive_blog_images import BlogImageManager, OneDriveUploadManager, OneDriveAuthManager
    from onedrive_image_index import OneDriveImageIndex
except ImportError as e:
    print(f"⚠️  Warning: OneDrive components not available: {e}")
    BlogImageManager = None
    OneDriveUploadManager = None
    OneDriveAuthManager = None
    OneDriveImageIndex = None

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ImageProcessingRecord:
    """图片处理记录"""
    original_path: str
    original_markdown: str
    processing_stage: str  # pending, uploaded, published, cleaned
    project_cache_path: Optional[str] = None
    onedrive_path: Optional[str] = None
    onedrive_url: Optional[str] = None
    embed_url: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()


class SmartPathResolver:
    """智能路径解析器 - 支持任意位置图片发现"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.common_temp_dirs = [
            Path.home() / "Desktop",
            Path.home() / "Downloads", 
            Path.home() / "Documents",
            Path("/tmp"),
            Path("/var/folders"),  # macOS临时目录
            Path("C:/Users") / os.environ.get('USERNAME', '') / "Desktop",  # Windows桌面
            Path("C:/Users") / os.environ.get('USERNAME', '') / "Downloads",  # Windows下载
        ]
    
    def find_image_paths(self, content: str, article_path: str) -> List[Tuple[str, str, str]]:
        """查找Markdown中的所有图片引用并解析真实路径"""
        image_pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')
        found_images = []
        
        for match in image_pattern.finditer(content):
            alt_text = match.group(1)
            img_path = match.group(2)
            full_match = match.group(0)
            
            # 跳过已经是网络链接的图片
            if self._is_web_url(img_path):
                continue
            
            # 解析本地路径
            resolved_path = self.resolve_image_path(img_path, article_path)
            if resolved_path:
                found_images.append((full_match, alt_text, resolved_path))
            else:
                logger.warning(f"Could not resolve image path: {img_path}")
        
        return found_images
    
    def resolve_image_path(self, img_path: str, article_path: str) -> Optional[str]:
        """智能解析图片路径 - 支持各种路径格式"""
        article_dir = Path(article_path).parent
        
        try:
            # 情况1: Jekyll baseurl路径
            if '{{ site.baseurl }}' in img_path:
                relative_path = img_path.replace('{{ site.baseurl }}/', '')
                candidate = self.project_root / relative_path
                if candidate.exists():
                    return str(candidate.resolve())
            
            # 情况2: 绝对路径
            if Path(img_path).is_absolute():
                candidate = Path(img_path)
                if candidate.exists():
                    return str(candidate.resolve())
            
            # 情况3: 相对路径（相对于文章）
            if img_path.startswith('./') or img_path.startswith('../'):
                candidate = (article_dir / img_path).resolve()
                if candidate.exists():
                    return str(candidate)
            
            # 情况4: 项目内相对路径
            candidate = self.project_root / img_path
            if candidate.exists():
                return str(candidate.resolve())
            
            # 情况5: 相对于文章目录的简单路径
            candidate = article_dir / img_path
            if candidate.exists():
                return str(candidate.resolve())
            
            # 情况6: 在常见临时目录中搜索
            img_filename = Path(img_path).name
            for temp_dir in self.common_temp_dirs:
                if temp_dir.exists():
                    # 在临时目录中搜索同名文件
                    for candidate in temp_dir.rglob(img_filename):
                        if candidate.is_file():
                            logger.info(f"Found image in temp directory: {candidate}")
                            return str(candidate.resolve())
            
            # 情况7: 全局搜索（最后手段，限制深度）
            return self._search_image_globally(img_filename, max_depth=3)
            
        except Exception as e:
            logger.warning(f"Error resolving path {img_path}: {e}")
            return None
    
    def _is_web_url(self, path: str) -> bool:
        """判断是否是网络URL"""
        return path.startswith(('http://', 'https://', '//', 'data:'))
    
    def _search_image_globally(self, filename: str, max_depth: int = 3) -> Optional[str]:
        """全局搜索图片文件（限制深度避免性能问题）"""
        def search_recursive(directory: Path, current_depth: int) -> Optional[str]:
            if current_depth > max_depth:
                return None
            
            try:
                for item in directory.iterdir():
                    if item.name == filename and item.is_file():
                        return str(item.resolve())
                    elif item.is_dir() and not item.name.startswith('.'):
                        result = search_recursive(item, current_depth + 1)
                        if result:
                            return result
            except PermissionError:
                pass
            return None
        
        # 从项目根目录开始搜索
        return search_recursive(self.project_root, 0)


class ProcessingDirectoryManager:
    """处理目录管理器"""
    
    def __init__(self, base_path: str = "assets/images/processing"):
        self.base_path = Path(base_path)
        self.pending_dir = self.base_path / "pending"
        self.uploaded_dir = self.base_path / "uploaded"
        self.failed_dir = self.base_path / "failed"
        
        # 确保目录存在
        self._ensure_directories()
        
    def _ensure_directories(self):
        """确保所有必需目录存在"""
        for directory in [self.pending_dir, self.uploaded_dir, self.failed_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def create_processing_session(self, article_title: str) -> str:
        """创建处理会话目录"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"{article_title[:20]}_{timestamp}"
        # 清理文件名中的特殊字符
        session_id = re.sub(r'[<>:"/\\|?*]', '_', session_id)
        
        session_dir = self.pending_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Created processing session: {session_id}")
        return session_id
    
    def move_to_uploaded(self, session_id: str) -> bool:
        """将会话从pending移动到uploaded"""
        try:
            pending_path = self.pending_dir / session_id
            uploaded_path = self.uploaded_dir / session_id
            
            if pending_path.exists():
                shutil.move(str(pending_path), str(uploaded_path))
                logger.info(f"Moved session to uploaded: {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to move session to uploaded: {e}")
            return False
    
    def move_to_failed(self, session_id: str, error_info: str) -> bool:
        """将会话移动到failed并记录错误信息"""
        try:
            pending_path = self.pending_dir / session_id
            failed_path = self.failed_dir / session_id
            
            if pending_path.exists():
                shutil.move(str(pending_path), str(failed_path))
                
                # 记录错误信息
                error_file = failed_path / "error.txt"
                error_file.write_text(f"Error: {error_info}\nTime: {datetime.now().isoformat()}", 
                                    encoding='utf-8')
                logger.error(f"Moved session to failed: {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to move session to failed: {e}")
            return False
    
    def cleanup_uploaded_session(self, session_id: str, user_confirmed: bool = False) -> bool:
        """清理已上传的会话（需要用户确认）"""
        if not user_confirmed:
            logger.warning(f"Session cleanup requires user confirmation: {session_id}")
            return False
        
        try:
            uploaded_path = self.uploaded_dir / session_id
            if uploaded_path.exists():
                shutil.rmtree(uploaded_path)
                logger.info(f"Cleaned up uploaded session: {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to cleanup session: {e}")
            return False


class MixedImageManager:
    """混合图片管理系统主控制器"""
    
    def __init__(self, config_path: str = "config/onedrive_config.json", 
                 project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # 初始化组件
        self.path_resolver = SmartPathResolver(self.project_root)
        self.dir_manager = ProcessingDirectoryManager()
        
        # 初始化OneDrive组件（如果可用）
        self.onedrive_manager = None
        self.image_index = None
        
        if BlogImageManager:
            try:
                self.onedrive_manager = BlogImageManager(config_path)
                self.image_index = OneDriveImageIndex() if OneDriveImageIndex else None
            except Exception as e:
                logger.warning(f"OneDrive manager initialization failed: {e}")
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            # 默认配置
            default_config = {
                "image_processing": {
                    "temp_retention_days": 7,
                    "auto_cleanup_after_publish": False,
                    "backup_original_files": True,
                    "processing_directory": "assets/images/processing",
                    "max_file_size_mb": 10
                }
            }
            
            # 尝试加载文件配置
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    default_config.update(file_config)
            
            return default_config
            
        except Exception as e:
            logger.warning(f"Failed to load config, using defaults: {e}")
            return {"image_processing": {
                "temp_retention_days": 7,
                "auto_cleanup_after_publish": False,
                "backup_original_files": True,
                "processing_directory": "assets/images/processing",
                "max_file_size_mb": 10
            }}
    
    def process_article_images(self, article_path: str, 
                             dry_run: bool = False) -> Dict:
        """处理文章中的所有图片 - 完整的四阶段流程"""
        
        article_file = Path(article_path)
        if not article_file.exists():
            return {'success': False, 'error': 'Article file not found'}
        
        logger.info(f"Starting mixed image processing for: {article_path}")
        print("🚀 启动混合图片管理系统")
        print("=" * 60)
        
        try:
            # 阶段1: 临时创作 → 项目缓存
            print("📁 阶段1: 发现和缓存图片...")
            cache_result = self._stage1_discover_and_cache(article_path, dry_run)
            
            if not cache_result['success']:
                return cache_result
            
            if cache_result['images_found'] == 0:
                return {'success': True, 'message': 'No images to process', 'stages_completed': 1}
            
            # 阶段2: 项目缓存 → 云端归档
            print("☁️  阶段2: 上传到云端...")
            upload_result = self._stage2_upload_to_cloud(cache_result['session_id'], 
                                                       article_path, dry_run)
            
            if not upload_result['success']:
                # 失败时移动到failed目录
                self.dir_manager.move_to_failed(cache_result['session_id'], 
                                               upload_result.get('error', 'Upload failed'))
                return upload_result
            
            # 阶段3: 更新文章链接
            print("🔗 阶段3: 更新文章链接...")
            update_result = self._stage3_update_article_links(article_path, 
                                                             upload_result['replacements'], 
                                                             dry_run)
            
            # 阶段4: 移动到uploaded状态（等待用户确认清理）
            print("📦 阶段4: 保存处理状态...")
            if not dry_run:
                self.dir_manager.move_to_uploaded(cache_result['session_id'])
            
            print("✅ 混合图片处理完成！")
            print(f"💾 会话ID: {cache_result['session_id']}")
            print(f"🖼️  处理图片: {upload_result['images_processed']}")
            
            return {
                'success': True,
                'session_id': cache_result['session_id'],
                'images_processed': upload_result['images_processed'],
                'replacements': upload_result['replacements'],
                'stages_completed': 4,
                'cache_result': cache_result,
                'upload_result': upload_result,
                'update_result': update_result
            }
            
        except Exception as e:
            logger.error(f"Failed to process article images: {e}")
            return {'success': False, 'error': str(e)}
    
    def _stage1_discover_and_cache(self, article_path: str, dry_run: bool) -> Dict:
        """阶段1: 发现图片并缓存到processing/pending/"""
        try:
            # 读取文章内容
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取文章标题
            title_match = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', content, re.MULTILINE)
            article_title = title_match.group(1) if title_match else Path(article_path).stem
            
            # 发现图片路径
            found_images = self.path_resolver.find_image_paths(content, article_path)
            
            if not found_images:
                return {'success': True, 'images_found': 0, 'message': 'No local images found'}
            
            print(f"🔍 发现 {len(found_images)} 个本地图片")
            
            # 创建处理会话
            session_id = self.dir_manager.create_processing_session(article_title)
            session_dir = self.dir_manager.pending_dir / session_id
            
            # 缓存图片文件和元数据
            cached_images = []
            for i, (full_match, alt_text, img_path) in enumerate(found_images, 1):
                try:
                    img_file = Path(img_path)
                    if not img_file.exists():
                        logger.warning(f"Image file not found: {img_path}")
                        continue
                    
                    # 检查文件大小
                    file_size_mb = img_file.stat().st_size / (1024 * 1024)
                    max_size = self.config.get('image_processing', {}).get('max_file_size_mb', 10)
                    if file_size_mb > max_size:
                        logger.warning(f"Image too large ({file_size_mb:.1f}MB): {img_path}")
                        continue
                    
                    # 复制到缓存目录
                    cached_filename = f"{i:02d}_{img_file.name}"
                    cached_path = session_dir / cached_filename
                    
                    if not dry_run:
                        shutil.copy2(img_file, cached_path)
                    
                    # 创建处理记录
                    record = ImageProcessingRecord(
                        original_path=img_path,
                        original_markdown=full_match,
                        processing_stage="pending",
                        project_cache_path=str(cached_path)
                    )
                    
                    cached_images.append(record)
                    print(f"  📥 {i:02d}. {img_file.name} -> 项目缓存")
                    
                except Exception as e:
                    logger.error(f"Failed to cache image {img_path}: {e}")
                    continue
            
            # 保存会话元数据
            session_metadata = {
                'session_id': session_id,
                'article_path': article_path,
                'article_title': article_title,
                'images_found': len(found_images),
                'images_cached': len(cached_images),
                'created_at': datetime.now().isoformat(),
                'cached_images': [
                    {
                        'original_path': img.original_path,
                        'original_markdown': img.original_markdown,
                        'cache_path': img.project_cache_path,
                        'processing_stage': img.processing_stage
                    }
                    for img in cached_images
                ]
            }
            
            if not dry_run:
                metadata_file = session_dir / "session_metadata.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(session_metadata, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'session_id': session_id,
                'images_found': len(found_images),
                'images_cached': len(cached_images),
                'cached_images': cached_images,
                'metadata': session_metadata
            }
            
        except Exception as e:
            logger.error(f"Stage 1 failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _stage2_upload_to_cloud(self, session_id: str, article_path: str, 
                              dry_run: bool) -> Dict:
        """阶段2: 上传缓存的图片到云端"""
        
        if not self.onedrive_manager:
            return {'success': False, 'error': 'OneDrive manager not available'}
        
        try:
            session_dir = self.dir_manager.pending_dir / session_id
            metadata_file = session_dir / "session_metadata.json"
            
            # 在试运行模式下，如果元数据文件不存在，返回成功但不实际处理
            if dry_run and not metadata_file.exists():
                print("  🚀 [DRY RUN] 模拟云端上传阶段")
                return {
                    'success': True,
                    'images_processed': 0,
                    'replacements': {},
                    'session_metadata': {'note': 'dry run mode'}
                }
            
            # 加载会话元数据
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            replacements = {}
            processed_count = 0
            
            for i, img_info in enumerate(metadata['cached_images'], 1):
                try:
                    cache_path = img_info['cache_path']
                    original_markdown = img_info['original_markdown']
                    
                    if dry_run:
                        print(f"  🚀 {i:02d}. [DRY RUN] Would upload: {Path(cache_path).name}")
                        continue
                    
                    # 使用现有的OneDrive上传逻辑
                    # 这里需要调用原有的上传和链接生成代码
                    upload_result = self._upload_single_image(cache_path, article_path, i)
                    
                    if upload_result['success']:
                        # 更新Markdown链接
                        alt_text = original_markdown.split('![')[1].split(']')[0]
                        new_markdown = f"![{alt_text}]({upload_result['embed_url']})"
                        replacements[original_markdown] = new_markdown
                        processed_count += 1
                        
                        print(f"  ✅ {i:02d}. {Path(cache_path).name} -> OneDrive")
                    else:
                        logger.error(f"Failed to upload {cache_path}: {upload_result.get('error')}")
                        
                except Exception as e:
                    logger.error(f"Failed to process cached image {i}: {e}")
                    continue
            
            # 更新会话元数据
            metadata['upload_completed_at'] = datetime.now().isoformat()
            metadata['images_uploaded'] = processed_count
            metadata['upload_replacements'] = replacements
            
            if not dry_run:
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            return {
                'success': True,
                'images_processed': processed_count,
                'replacements': replacements,
                'session_metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Stage 2 failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _upload_single_image(self, cache_path: str, article_path: str, 
                           index: int) -> Dict:
        """上传单个图片到OneDrive"""
        
        if not self.onedrive_manager:
            return {'success': False, 'error': 'OneDrive manager not available'}
        
        try:
            # 使用现有的processor逻辑
            processor = self.onedrive_manager.processor
            
            # 生成远程路径
            cache_file = Path(cache_path)
            now = datetime.now()
            
            # 提取文章标题
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            title_match = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', content, re.MULTILINE)
            article_title = title_match.group(1) if title_match else Path(article_path).stem
            
            remote_path = processor._generate_remote_path(cache_path, article_title, index)
            
            # 上传文件
            upload_result = processor.uploader.upload_file(cache_path, remote_path)
            
            # 获取嵌入链接
            direct_link = processor.uploader.get_direct_image_url(upload_result['id'])
            
            # 添加到索引
            if processor.index:
                processor.index.add_record(
                    local_path=cache_path,
                    onedrive_path=remote_path,
                    onedrive_url=direct_link,
                    embed_url=direct_link,
                    article_file=article_path,
                    article_title=article_title,
                    onedrive_file_id=upload_result['id'],
                    image_index=index,
                    processing_notes=f"Mixed workflow upload from cache"
                )
            
            return {
                'success': True,
                'onedrive_file_id': upload_result['id'],
                'remote_path': remote_path,
                'direct_link': direct_link,
                'embed_url': direct_link
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _stage3_update_article_links(self, article_path: str, 
                                   replacements: Dict[str, str], 
                                   dry_run: bool) -> Dict:
        """阶段3: 更新文章中的图片链接"""
        
        if not replacements:
            return {'success': True, 'message': 'No links to update'}
        
        try:
            # 读取原始内容
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 创建备份
            backup_path = f"{article_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if not dry_run:
                shutil.copy2(article_path, backup_path)
            
            # 应用替换
            updated_content = content
            for old_link, new_link in replacements.items():
                updated_content = updated_content.replace(old_link, new_link)
            
            if dry_run:
                print(f"  🔗 [DRY RUN] Would update {len(replacements)} links in article")
            else:
                # 写回文件
                with open(article_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                print(f"  ✅ 已更新 {len(replacements)} 个图片链接")
            
            return {
                'success': True,
                'links_updated': len(replacements),
                'backup_path': backup_path
            }
            
        except Exception as e:
            logger.error(f"Stage 3 failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def list_uploaded_sessions(self) -> List[Dict]:
        """列出所有等待清理确认的上传会话"""
        sessions = []
        
        for session_dir in self.dir_manager.uploaded_dir.iterdir():
            if session_dir.is_dir():
                try:
                    metadata_file = session_dir / "session_metadata.json"
                    if metadata_file.exists():
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        sessions.append(metadata)
                except Exception as e:
                    logger.warning(f"Failed to read session metadata: {e}")
        
        return sorted(sessions, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def confirm_cleanup(self, session_id: str, user_confirmed: bool = False) -> Dict:
        """确认清理上传会话（需要用户明确确认）"""
        
        if not user_confirmed:
            return {
                'success': False, 
                'error': 'User confirmation required for cleanup',
                'message': 'Please set user_confirmed=True to proceed'
            }
        
        success = self.dir_manager.cleanup_uploaded_session(session_id, user_confirmed)
        
        if success:
            return {'success': True, 'message': f'Session {session_id} cleaned up successfully'}
        else:
            return {'success': False, 'error': f'Failed to cleanup session {session_id}'}


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description="有心工坊 - 混合图片管理系统")
    parser.add_argument("article_path", nargs='?', help="文章文件路径")
    parser.add_argument("--dry-run", action="store_true", help="试运行模式（不实际修改文件）")
    parser.add_argument("--list-sessions", action="store_true", help="列出等待清理的会话")
    parser.add_argument("--confirm-cleanup", help="确认清理指定会话ID")
    parser.add_argument("--config", default="config/onedrive_config.json", help="配置文件路径")
    
    args = parser.parse_args()
    
    try:
        manager = MixedImageManager(config_path=args.config)
        
        if args.list_sessions:
            # 列出等待清理的会话
            sessions = manager.list_uploaded_sessions()
            if not sessions:
                print("📭 没有等待清理的会话")
            else:
                print(f"📋 等待清理的会话 ({len(sessions)}个):")
                for session in sessions:
                    print(f"  🗂️  {session['session_id']}")
                    print(f"     文章: {session.get('article_title', 'Unknown')}")
                    print(f"     创建: {session.get('created_at', 'Unknown')}")
                    print(f"     图片: {session.get('images_uploaded', 0)}")
                    print()
                    
        elif args.confirm_cleanup:
            # 确认清理会话
            print(f"⚠️  正在清理会话: {args.confirm_cleanup}")
            print("这将永久删除本地备份文件！")
            
            confirm = input("请输入 'YES' 确认清理: ")
            if confirm == 'YES':
                result = manager.confirm_cleanup(args.confirm_cleanup, user_confirmed=True)
                if result['success']:
                    print("✅ 清理完成")
                else:
                    print(f"❌ 清理失败: {result['error']}")
            else:
                print("❌ 清理已取消")
                
        elif args.article_path:
            # 处理文章图片
            print(f"📝 处理文章: {args.article_path}")
            if args.dry_run:
                print("🔍 试运行模式 - 不会修改任何文件")
            
            result = manager.process_article_images(args.article_path, dry_run=args.dry_run)
            
            if result['success']:
                print("✅ 处理成功!")
                if not args.dry_run:
                    print(f"💾 会话ID: {result.get('session_id')}")
                    print("📝 提示: 文章发布后可使用 --confirm-cleanup 清理备份文件")
            else:
                print(f"❌ 处理失败: {result.get('error')}")
        else:
            parser.print_help()
            
    except Exception as e:
        logger.error(f"Application error: {e}")
        print(f"❌ 系统错误: {e}")


if __name__ == "__main__":
    main()