#!/usr/bin/env python3
"""
OneDrive云端图片清理工具
支持按日期范围删除OneDrive中的图片文件，用于清理误传或测试文件
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import argparse
import re
from urllib.parse import urlparse
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

try:
    from onedrive_blog_images import OneDriveUploadManager, OneDriveAuthManager
except ImportError:
    print("❌ 无法导入OneDrive管理器，请确保onedrive_blog_images.py存在")
    sys.exit(1)

class OneDriveCloudCleaner:
    def __init__(self, config_file: str = "config/onedrive_config.json"):
        self.config_file = Path(config_file)
        self.config = self.load_config()
        self.upload_manager = None
        self.index_file = Path("_data/onedrive_image_index.json")
        
        # 初始化OneDrive连接
        try:
            # 初始化认证管理器
            self.auth_manager = OneDriveAuthManager(self.config)
            # 初始化上传管理器
            self.upload_manager = OneDriveUploadManager(self.auth_manager, self.config)
            print("✅ OneDrive连接已建立")
        except Exception as e:
            print(f"❌ OneDrive连接失败: {e}")
            print("请确保配置文件正确且已完成OAuth认证")
    
    def load_config(self) -> Dict:
        """加载OneDrive配置，优先使用环境变量"""
        try:
            # 首先加载基础配置文件
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 使用环境变量覆盖认证配置
            if 'ONEDRIVE_TENANT_ID' in os.environ:
                if 'auth' not in config:
                    config['auth'] = {}
                config['auth']['tenant_id'] = os.environ['ONEDRIVE_TENANT_ID']
            
            if 'ONEDRIVE_CLIENT_ID' in os.environ:
                if 'auth' not in config:
                    config['auth'] = {}
                config['auth']['client_id'] = os.environ['ONEDRIVE_CLIENT_ID']
            
            if 'ONEDRIVE_CLIENT_SECRET' in os.environ:
                if 'auth' not in config:
                    config['auth'] = {}
                config['auth']['client_secret'] = os.environ['ONEDRIVE_CLIENT_SECRET']
            
            if 'ONEDRIVE_REDIRECT_URI' in os.environ:
                if 'auth' not in config:
                    config['auth'] = {}
                config['auth']['redirect_uri'] = os.environ['ONEDRIVE_REDIRECT_URI']
            
            return config
            
        except FileNotFoundError:
            print(f"❌ 配置文件未找到: {self.config_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件格式错误: {e}")
            return {}
    
    def list_cloud_files(self, folder_path: str = None) -> List[Dict]:
        """列出OneDrive中的文件"""
        if not self.upload_manager:
            return []
        
        try:
            # 构建查询路径
            if folder_path:
                query_path = f"/me/drive/root:/{folder_path}:/children"
            else:
                base_folder = self.config.get('onedrive', {}).get('base_folder', '/BlogImages')
                query_path = f"/me/drive/root:{base_folder}:/children"
            
            response = self.upload_manager._make_request('GET', query_path)
            
            if response.status_code == 200:
                data = response.json()
                files = []
                
                for item in data.get('value', []):
                    if item.get('file'):  # 只处理文件，不处理文件夹
                        file_info = {
                            'id': item.get('id'),
                            'name': item.get('name'),
                            'size': item.get('size', 0),
                            'created_time': item.get('createdDateTime'),
                            'modified_time': item.get('lastModifiedDateTime'),
                            'web_url': item.get('webUrl'),
                            'download_url': item.get('@microsoft.graph.downloadUrl'),
                            'path': item.get('parentReference', {}).get('path', ''),
                            'mime_type': item.get('file', {}).get('mimeType', '')
                        }
                        files.append(file_info)
                
                return files
            else:
                print(f"❌ 获取文件列表失败: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ 列出文件时出错: {e}")
            return []
    
    def list_all_files_recursive(self, base_path: str = None) -> List[Dict]:
        """递归列出所有文件（包括子文件夹）"""
        all_files = []
        
        def _list_folder(folder_path: str = None):
            try:
                if folder_path:
                    query_path = f"/me/drive/root:/{folder_path}:/children"
                else:
                    base_folder = self.config.get('onedrive', {}).get('base_folder', '/BlogImages')
                    query_path = f"/me/drive/root:{base_folder}:/children"
                
                response = self.upload_manager._make_request('GET', query_path)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data.get('value', []):
                        if item.get('file'):  # 文件
                            file_info = {
                                'id': item.get('id'),
                                'name': item.get('name'),
                                'size': item.get('size', 0),
                                'created_time': item.get('createdDateTime'),
                                'modified_time': item.get('lastModifiedDateTime'),
                                'web_url': item.get('webUrl'),
                                'download_url': item.get('@microsoft.graph.downloadUrl'),
                                'path': item.get('parentReference', {}).get('path', ''),
                                'mime_type': item.get('file', {}).get('mimeType', ''),
                                'folder_path': folder_path or base_folder
                            }
                            all_files.append(file_info)
                        elif item.get('folder'):  # 文件夹，递归处理
                            folder_name = item.get('name')
                            if folder_path:
                                subfolder_path = f"{folder_path}/{folder_name}"
                            else:
                                base_folder = self.config.get('onedrive', {}).get('base_folder', '/BlogImages')
                                subfolder_path = f"{base_folder.strip('/')}/{folder_name}"
                            
                            _list_folder(subfolder_path)
                            
            except Exception as e:
                print(f"⚠️ 处理文件夹时出错 {folder_path}: {e}")
        
        _list_folder(base_path)
        return all_files
    
    def parse_date_range(self, date_str: str) -> Tuple[datetime, datetime]:
        """解析日期范围字符串"""
        try:
            if '-' in date_str and date_str.count('-') >= 2:
                # 具体日期格式: 2025-08-12 或 2025-08-12:2025-08-13
                if ':' in date_str:
                    start_str, end_str = date_str.split(':', 1)
                    start_date = datetime.strptime(start_str.strip(), '%Y-%m-%d')
                    end_date = datetime.strptime(end_str.strip(), '%Y-%m-%d')
                else:
                    # 单个日期，当天
                    start_date = datetime.strptime(date_str, '%Y-%m-%d')
                    end_date = start_date + timedelta(days=1)
            elif date_str.endswith('d'):
                # 最近N天: 7d, 30d
                days = int(date_str[:-1])
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)
            elif date_str.endswith('h'):
                # 最近N小时: 24h, 48h
                hours = int(date_str[:-1])
                end_date = datetime.now()
                start_date = end_date - timedelta(hours=hours)
            else:
                raise ValueError(f"无法解析日期格式: {date_str}")
            
            return start_date, end_date
            
        except Exception as e:
            raise ValueError(f"日期格式错误 '{date_str}': {e}")
    
    def filter_files_by_date(self, files: List[Dict], date_range: str) -> List[Dict]:
        """按日期范围过滤文件"""
        start_date, end_date = self.parse_date_range(date_range)
        
        filtered_files = []
        for file_info in files:
            # 使用修改时间进行过滤
            file_time_str = file_info.get('modified_time') or file_info.get('created_time')
            if not file_time_str:
                continue
            
            try:
                # 解析ISO格式时间
                file_time = datetime.fromisoformat(file_time_str.replace('Z', '+00:00'))
                # 转换为本地时间进行比较
                file_time = file_time.replace(tzinfo=None)
                
                if start_date <= file_time <= end_date:
                    filtered_files.append(file_info)
                    
            except Exception as e:
                print(f"⚠️ 解析文件时间失败 {file_info.get('name')}: {e}")
                continue
        
        return filtered_files
    
    def delete_cloud_file(self, file_id: str) -> bool:
        """删除OneDrive中的单个文件"""
        if not self.upload_manager:
            return False
        
        try:
            response = self.upload_manager._make_request('DELETE', f"/me/drive/items/{file_id}")
            
            if response.status_code in [204, 200]:  # 删除成功
                return True
            else:
                print(f"❌ 删除失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 删除文件时出错: {e}")
            return False
    
    def update_local_index(self, deleted_files: List[Dict]) -> None:
        """更新本地索引，移除已删除的文件记录"""
        if not self.index_file.exists():
            return
        
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            # 获取已删除文件的OneDrive ID
            deleted_ids = {f.get('id') for f in deleted_files}
            deleted_names = {f.get('name') for f in deleted_files}
            
            # 从索引中移除对应记录
            original_count = len(index_data)
            updated_index = {}
            
            for key, record in index_data.items():
                file_id = record.get('onedrive_file_id')
                filename = record.get('filename')
                
                # 如果文件ID或文件名匹配已删除的文件，则不保留
                if file_id not in deleted_ids and filename not in deleted_names:
                    updated_index[key] = record
            
            removed_count = original_count - len(updated_index)
            
            if removed_count > 0:
                with open(self.index_file, 'w', encoding='utf-8') as f:
                    json.dump(updated_index, f, indent=2, ensure_ascii=False)
                
                print(f"📝 已从本地索引中移除 {removed_count} 条记录")
            else:
                print("📝 本地索引无需更新")
                
        except Exception as e:
            print(f"⚠️ 更新本地索引时出错: {e}")
    
    def preview_deletion(self, files: List[Dict]) -> None:
        """预览将要删除的文件"""
        if not files:
            print("📂 没有找到符合条件的文件")
            return
        
        print(f"\n📋 将要删除的文件 ({len(files)} 个):")
        print("=" * 80)
        
        total_size = 0
        for i, file_info in enumerate(files, 1):
            size_mb = file_info.get('size', 0) / (1024 * 1024)
            total_size += file_info.get('size', 0)
            
            print(f"{i:3d}. {file_info.get('name')}")
            print(f"     📅 修改时间: {file_info.get('modified_time', '未知')}")
            print(f"     📂 路径: {file_info.get('folder_path', '未知')}")
            print(f"     📏 大小: {size_mb:.2f} MB")
            print(f"     🔗 类型: {file_info.get('mime_type', '未知')}")
            print()
        
        print(f"📊 总计: {len(files)} 个文件, {total_size / (1024 * 1024):.2f} MB")
    
    def clean_files_by_date(self, date_range: str, dry_run: bool = True, 
                           confirm: bool = False) -> Dict:
        """按日期范围清理文件"""
        print(f"🔍 查找日期范围内的文件: {date_range}")
        
        # 获取所有文件
        print("📡 正在获取OneDrive文件列表...")
        all_files = self.list_all_files_recursive()
        
        if not all_files:
            return {'success': False, 'error': '无法获取文件列表或文件夹为空'}
        
        print(f"📁 共找到 {len(all_files)} 个文件")
        
        # 按日期过滤
        try:
            filtered_files = self.filter_files_by_date(all_files, date_range)
        except ValueError as e:
            return {'success': False, 'error': str(e)}
        
        if not filtered_files:
            return {'success': True, 'deleted_count': 0, 'message': '没有找到符合日期条件的文件'}
        
        # 预览删除文件
        self.preview_deletion(filtered_files)
        
        if dry_run:
            return {
                'success': True, 
                'deleted_count': 0, 
                'preview_count': len(filtered_files),
                'message': f'预览模式：找到 {len(filtered_files)} 个文件'
            }
        
        # 确认删除
        if not confirm:
            response = input(f"\n⚠️ 确认删除这 {len(filtered_files)} 个文件吗？此操作不可恢复！\n输入 'DELETE' 确认: ")
            if response != 'DELETE':
                return {'success': False, 'error': '操作已取消'}
        
        # 执行删除
        print(f"\n🗑️ 开始删除 {len(filtered_files)} 个文件...")
        deleted_files = []
        failed_files = []
        
        for i, file_info in enumerate(filtered_files, 1):
            filename = file_info.get('name')
            file_id = file_info.get('id')
            
            print(f"🗑️ [{i}/{len(filtered_files)}] 删除: {filename}")
            
            if self.delete_cloud_file(file_id):
                deleted_files.append(file_info)
                print(f"✅ 删除成功: {filename}")
            else:
                failed_files.append(file_info)
                print(f"❌ 删除失败: {filename}")
        
        # 更新本地索引
        if deleted_files:
            self.update_local_index(deleted_files)
        
        return {
            'success': True,
            'deleted_count': len(deleted_files),
            'failed_count': len(failed_files),
            'deleted_files': [f.get('name') for f in deleted_files],
            'failed_files': [f.get('name') for f in failed_files]
        }

def main():
    parser = argparse.ArgumentParser(
        description="OneDrive云端图片清理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
日期格式示例:
  7d              - 最近7天
  24h             - 最近24小时
  2025-08-12      - 指定日期（当天）
  2025-08-12:2025-08-15 - 日期范围

使用示例:
  python cleanup_onedrive_cloud.py --list                    # 列出所有文件
  python cleanup_onedrive_cloud.py --preview 7d              # 预览最近7天的文件
  python cleanup_onedrive_cloud.py --delete 2025-08-12       # 删除指定日期的文件
  python cleanup_onedrive_cloud.py --delete 24h --yes        # 删除最近24小时文件（跳过确认）
        """
    )
    
    parser.add_argument('--list', '-l', action='store_true', 
                       help="列出OneDrive中的所有文件")
    parser.add_argument('--preview', '-p', metavar='DATE_RANGE',
                       help="预览指定日期范围内的文件（不执行删除）")
    parser.add_argument('--delete', '-d', metavar='DATE_RANGE',
                       help="删除指定日期范围内的文件")
    parser.add_argument('--yes', '-y', action='store_true',
                       help="跳过删除确认（危险！）")
    parser.add_argument('--config', '-c', default="config/onedrive_config.json",
                       help="OneDrive配置文件路径")
    
    args = parser.parse_args()
    
    # 检查参数
    if not any([args.list, args.preview, args.delete]):
        parser.print_help()
        return
    
    cleaner = OneDriveCloudCleaner(args.config)
    
    if not cleaner.upload_manager:
        print("❌ OneDrive连接失败，无法继续")
        return
    
    if args.list:
        print("📡 正在获取OneDrive文件列表...")
        files = cleaner.list_all_files_recursive()
        
        if files:
            cleaner.preview_deletion(files)
        else:
            print("📂 OneDrive中没有找到文件")
    
    elif args.preview:
        result = cleaner.clean_files_by_date(args.preview, dry_run=True)
        
        if result['success']:
            print(f"\n📊 预览结果: {result.get('message', '')}")
        else:
            print(f"❌ 预览失败: {result.get('error', '')}")
    
    elif args.delete:
        result = cleaner.clean_files_by_date(args.delete, dry_run=False, confirm=args.yes)
        
        if result['success']:
            deleted_count = result.get('deleted_count', 0)
            failed_count = result.get('failed_count', 0)
            
            print(f"\n📊 清理完成:")
            print(f"✅ 成功删除: {deleted_count} 个文件")
            if failed_count > 0:
                print(f"❌ 删除失败: {failed_count} 个文件")
                
                failed_files = result.get('failed_files', [])
                if failed_files:
                    print("失败的文件:")
                    for filename in failed_files:
                        print(f"  - {filename}")
        else:
            print(f"❌ 清理失败: {result.get('error', '')}")

if __name__ == "__main__":
    main()