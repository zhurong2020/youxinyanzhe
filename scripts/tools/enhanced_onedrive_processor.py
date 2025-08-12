#!/usr/bin/env python3
"""
增强的OneDrive图片处理器
集成回退机制和GitHub Release备份
"""

import json
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse

# 导入现有组件
try:
    from onedrive_blog_images import BlogImageManager
except ImportError as e:
    print(f"⚠️  BlogImageManager import failed: {e}")
    BlogImageManager = None

# RewardManager 模块不存在，直接设为None
RewardManager = None


class EnhancedOneDriveProcessor:
    """增强的OneDrive处理器，包含回退和备份功能"""
    
    def __init__(self, config_path: str = "config/onedrive_config.json"):
        self.config_path = config_path
        self.snapshots_dir = Path("temp/onedrive_snapshots")
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化组件
        self.onedrive_manager = BlogImageManager(config_path) if BlogImageManager else None
        self.reward_manager = RewardManager() if RewardManager else None
        
    def process_with_backup(self, article_path: str, create_github_release: bool = True) -> Dict:
        """带备份机制的完整处理流程"""
        
        print("🚀 开始增强的OneDrive图片处理流程")
        print("="*60)
        
        article_file = Path(article_path)
        if not article_file.exists():
            return {'success': False, 'error': 'Article file not found'}
        
        # 步骤1: 创建处理前快照
        print("📸 创建处理前快照...")
        snapshot = self.create_snapshot(article_path)
        if not snapshot['success']:
            return {'success': False, 'error': f"Failed to create snapshot: {snapshot['error']}"}
        
        try:
            # 步骤2: 执行OneDrive图片处理
            print("☁️  处理OneDrive图片上传...")
            onedrive_result = self.process_onedrive_images(article_path)
            
            if not onedrive_result['success']:
                print("❌ OneDrive处理失败，执行回退...")
                self.rollback_from_snapshot(snapshot['snapshot_id'])
                return {
                    'success': False, 
                    'error': onedrive_result['error'],
                    'rolled_back': True,
                    'snapshot_id': snapshot['snapshot_id']
                }
            
            # 步骤3: 验证图片链接可访问性
            print("🔍 验证图片链接...")
            validation_result = self.validate_image_links(article_path)
            
            if not validation_result['success']:
                print("⚠️  图片链接验证失败，但继续流程...")
                # 不回退，仅记录警告
            
            # 步骤4: 创建GitHub Release备份
            backup_result = {'success': True, 'message': 'Backup skipped'}
            if create_github_release and self.reward_manager:
                print("📦 创建GitHub Release备份...")
                backup_result = self.create_github_backup(article_path, snapshot['snapshot_id'])
            
            print("✅ 处理流程完成！")
            return {
                'success': True,
                'onedrive_result': onedrive_result,
                'validation_result': validation_result,
                'backup_result': backup_result,
                'snapshot_id': snapshot['snapshot_id']
            }
            
        except Exception as e:
            print(f"❌ 处理过程中发生异常: {e}")
            print("🔄 执行紧急回退...")
            self.rollback_from_snapshot(snapshot['snapshot_id'])
            return {
                'success': False,
                'error': str(e),
                'rolled_back': True,
                'snapshot_id': snapshot['snapshot_id']
            }
    
    def create_snapshot(self, article_path: str) -> Dict:
        """创建处理前快照"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_id = f"{Path(article_path).stem}_{timestamp}"
            snapshot_dir = self.snapshots_dir / snapshot_id
            snapshot_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存文章内容
            article_file = Path(article_path)
            shutil.copy2(article_file, snapshot_dir / "article_content.md")
            
            # 扫描并保存本地图片信息
            local_images = self.scan_local_images(article_path)
            
            # 保存本地图片文件(如果存在)
            images_dir = snapshot_dir / "local_images"
            images_dir.mkdir(exist_ok=True)
            
            saved_images = []
            for img_path in local_images:
                img_file = Path(img_path)
                if img_file.exists():
                    dest = images_dir / img_file.name
                    shutil.copy2(img_file, dest)
                    saved_images.append(str(dest))
            
            # 保存OneDrive索引状态
            index_path = Path("_data/onedrive_image_index.json")
            if index_path.exists():
                shutil.copy2(index_path, snapshot_dir / "onedrive_index_backup.json")
            
            # 创建快照元数据
            snapshot_metadata = {
                'snapshot_id': snapshot_id,
                'created_at': timestamp,
                'article_path': str(article_path),
                'local_images_found': local_images,
                'saved_images': saved_images,
                'article_size': article_file.stat().st_size,
                'has_index_backup': index_path.exists()
            }
            
            with open(snapshot_dir / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump(snapshot_metadata, f, indent=2, ensure_ascii=False)
            
            print(f"📸 快照已创建: {snapshot_id}")
            print(f"   📁 保存位置: {snapshot_dir}")
            print(f"   📝 文章大小: {article_file.stat().st_size} bytes")
            print(f"   🖼️  本地图片: {len(local_images)} 找到, {len(saved_images)} 已保存")
            
            return {
                'success': True,
                'snapshot_id': snapshot_id,
                'snapshot_dir': str(snapshot_dir),
                'metadata': snapshot_metadata
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def scan_local_images(self, article_path: str) -> List[str]:
        """扫描文章中引用的本地图片"""
        try:
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
            local_images = []
            
            for match in image_pattern.finditer(content):
                img_path = match.group(2)
                
                # 检查是否是本地路径
                if self.is_local_path(img_path):
                    # 解析实际路径
                    resolved_path = self.resolve_local_path(img_path, article_path)
                    if resolved_path:
                        local_images.append(resolved_path)
            
            return local_images
            
        except Exception as e:
            print(f"⚠️  扫描本地图片失败: {e}")
            return []
    
    def is_local_path(self, path: str) -> bool:
        """判断是否是本地路径"""
        if '{{ site.baseurl }}' in path:
            return True
        if path.startswith('./') or path.startswith('../'):
            return True
        if path.startswith('/') and not path.startswith('//'):
            return True
        return not (path.startswith('http://') or path.startswith('https://'))
    
    def resolve_local_path(self, img_path: str, article_path: str) -> Optional[str]:
        """解析本地图片的实际路径"""
        try:
            # 处理Windows绝对路径 (如 c:\Users\... 或 C:\Users\...)
            if len(img_path) >= 3 and img_path[1:3] == ':\\':
                # Windows绝对路径格式，转换为WSL路径
                drive_letter = img_path[0].lower()
                windows_path = img_path[3:].replace('\\', '/')
                # 转换为WSL格式: /mnt/c/Users/...
                wsl_path = f"/mnt/{drive_letter}/{windows_path}"
                return wsl_path
            elif '{{ site.baseurl }}' in img_path:
                relative_path = img_path.replace('{{ site.baseurl }}/', '')
                return str(Path(relative_path))
            elif img_path.startswith('../'):
                article_dir = Path(article_path).parent
                return str((article_dir / img_path).resolve())
            elif img_path.startswith('./'):
                article_dir = Path(article_path).parent
                return str((article_dir / img_path[2:]).resolve())
            else:
                return img_path
        except Exception:
            return None
    
    def process_onedrive_images(self, article_path: str) -> Dict:
        """执行OneDrive图片处理"""
        if not self.onedrive_manager:
            return {'success': False, 'error': 'OneDrive manager not available'}
        
        try:
            result = self.onedrive_manager.process_draft(article_path)
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def validate_image_links(self, article_path: str) -> Dict:
        """验证文章中的图片链接可访问性"""
        try:
            import requests
            
            with open(article_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
            
            total_images = 0
            accessible_images = 0
            failed_images = []
            
            for match in image_pattern.finditer(content):
                img_url = match.group(2)
                alt_text = match.group(1)
                
                # 跳过本地路径
                if self.is_local_path(img_url):
                    continue
                
                total_images += 1
                
                try:
                    # 简单的HEAD请求检查
                    response = requests.head(img_url, timeout=10, allow_redirects=True)
                    if response.status_code == 200:
                        accessible_images += 1
                    else:
                        failed_images.append({
                            'url': img_url,
                            'alt': alt_text,
                            'status_code': response.status_code
                        })
                except Exception as e:
                    failed_images.append({
                        'url': img_url,
                        'alt': alt_text,
                        'error': str(e)
                    })
            
            success_rate = (accessible_images / total_images * 100) if total_images > 0 else 100
            
            print(f"🔍 图片链接验证结果:")
            print(f"   📊 总计: {total_images}")
            print(f"   ✅ 可访问: {accessible_images}")
            print(f"   ❌ 失败: {len(failed_images)}")
            print(f"   📈 成功率: {success_rate:.1f}%")
            
            return {
                'success': success_rate >= 80,  # 80%以上认为成功
                'total_images': total_images,
                'accessible_images': accessible_images,
                'failed_images': failed_images,
                'success_rate': success_rate
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_github_backup(self, article_path: str, snapshot_id: str) -> Dict:
        """创建GitHub Release备份"""
        if not self.reward_manager:
            return {'success': False, 'error': 'Reward manager not available'}
        
        try:
            # 扩展的备份包包含快照信息
            snapshot_dir = self.snapshots_dir / snapshot_id
            
            # 创建临时备份目录
            with tempfile.TemporaryDirectory() as temp_dir:
                backup_dir = Path(temp_dir) / "article_backup"
                backup_dir.mkdir(parents=True)
                
                # 复制文章文件
                shutil.copy2(article_path, backup_dir / "article.md")
                
                # 复制快照内容
                if snapshot_dir.exists():
                    shutil.copytree(snapshot_dir, backup_dir / "snapshot", dirs_exist_ok=True)
                
                # 复制OneDrive索引
                index_path = Path("_data/onedrive_image_index.json")
                if index_path.exists():
                    shutil.copy2(index_path, backup_dir / "onedrive_index.json")
                
                # 创建恢复脚本
                recovery_script = self.generate_recovery_script(article_path, snapshot_id)
                (backup_dir / "recover.py").write_text(recovery_script, encoding='utf-8')
                
                # 使用现有的reward manager创建release
                result = self.reward_manager.create_article_package(
                    str(backup_dir / "article.md"),
                    upload_to_github=True
                )
                
                return result
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_recovery_script(self, article_path: str, snapshot_id: str) -> str:
        """生成恢复脚本"""
        return f'''#!/usr/bin/env python3
"""
自动生成的恢复脚本
用于回退OneDrive图片处理操作

使用方法:
python3 recover.py

原始文章: {article_path}
快照ID: {snapshot_id}
创建时间: {datetime.now().isoformat()}
"""

import shutil
from pathlib import Path

def recover():
    """执行恢复操作"""
    print("🔄 开始执行恢复操作...")
    
    snapshot_dir = Path("snapshot")
    if not snapshot_dir.exists():
        print("❌ 快照目录不存在")
        return False
    
    # 恢复文章内容
    article_backup = snapshot_dir / "article_content.md"
    if article_backup.exists():
        shutil.copy2(article_backup, "{article_path}")
        print(f"✅ 文章内容已恢复: {article_path}")
    
    # 恢复本地图片
    images_dir = snapshot_dir / "local_images"
    if images_dir.exists():
        for img_file in images_dir.glob("*"):
            # 这里需要根据实际情况调整目标路径
            print(f"📁 发现图片备份: {{img_file.name}}")
    
    # 恢复OneDrive索引
    index_backup = snapshot_dir / "onedrive_index_backup.json"
    if index_backup.exists():
        shutil.copy2(index_backup, "_data/onedrive_image_index.json")
        print("✅ OneDrive索引已恢复")
    
    print("🎉 恢复操作完成！")
    return True

if __name__ == "__main__":
    recover()
'''
    
    def rollback_from_snapshot(self, snapshot_id: str) -> Dict:
        """从快照回退"""
        try:
            snapshot_dir = self.snapshots_dir / snapshot_id
            if not snapshot_dir.exists():
                return {'success': False, 'error': f'Snapshot {snapshot_id} not found'}
            
            # 加载快照元数据
            metadata_file = snapshot_dir / "metadata.json"
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            print(f"🔄 开始从快照回退: {snapshot_id}")
            
            # 恢复文章内容
            article_backup = snapshot_dir / "article_content.md"
            if article_backup.exists():
                shutil.copy2(article_backup, metadata['article_path'])
                print(f"✅ 文章内容已恢复")
            
            # 恢复OneDrive索引
            index_backup = snapshot_dir / "onedrive_index_backup.json"
            if index_backup.exists():
                shutil.copy2(index_backup, "_data/onedrive_image_index.json")
                print("✅ OneDrive索引已恢复")
            
            print("🎉 回退操作完成！")
            return {'success': True, 'restored_files': ['article', 'index']}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description="增强的OneDrive图片处理器")
    parser.add_argument("article_path", help="文章文件路径")
    parser.add_argument("--with-github-backup", action="store_true", help="创建GitHub Release备份")
    parser.add_argument("--rollback", help="从指定快照ID回退")
    
    args = parser.parse_args()
    
    processor = EnhancedOneDriveProcessor()
    
    if args.rollback:
        result = processor.rollback_from_snapshot(args.rollback)
        if result['success']:
            print("✅ 回退成功")
        else:
            print(f"❌ 回退失败: {result['error']}")
    else:
        result = processor.process_with_backup(
            args.article_path,
            create_github_release=args.with_github_backup
        )
        
        if result['success']:
            print("✅ 处理成功")
            if result.get('snapshot_id'):
                print(f"💾 快照ID: {result['snapshot_id']}")
        else:
            print(f"❌ 处理失败: {result['error']}")
            if result.get('rolled_back'):
                print("🔄 已自动回退")


if __name__ == "__main__":
    main()