#!/usr/bin/env python3
"""
OneDrive图片按日期下载工具
支持按日期范围从OneDrive云端下载备份图片，用于错误处理后的快速恢复
"""

import json
import requests
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
from datetime import datetime, timedelta
import re
from urllib.parse import urlparse, parse_qs

# 添加路径以导入本地模块
sys.path.append(str(Path(__file__).parent.parent))

try:
    from onedrive_blog_images import BlogImageManager
    from onedrive_image_index import OneDriveImageIndex
except ImportError as e:
    print(f"⚠️  导入模块失败: {e}")
    print("请确保在项目根目录运行此脚本")
    BlogImageManager = None
    OneDriveImageIndex = None

class OneDriveDateDownloader:
    """按日期下载OneDrive图片的工具类"""
    
    def __init__(self, config_path: str = "config/onedrive_config.json"):
        self.config_path = config_path
        
        # 检查模块是否正确导入
        if OneDriveImageIndex is None:
            raise ImportError("无法导入OneDriveImageIndex，请检查模块路径")
        
        self.index = OneDriveImageIndex()
        
        # 初始化OneDrive管理器（用于API访问）
        try:
            if BlogImageManager is not None:
                self.manager = BlogImageManager(config_path)
                self.uploader = self.manager.uploader
            else:
                self.manager = None
                self.uploader = None
        except Exception as e:
            print(f"❌ OneDrive连接初始化失败: {e}")
            self.manager = None
            self.uploader = None
    
    def parse_date_input(self, date_str: str) -> Optional[datetime]:
        """解析日期输入，支持多种格式"""
        if not date_str:
            return None
            
        try:
            # 相对时间格式: 7d, 24h, 30d
            if date_str.endswith('d'):
                days = int(date_str[:-1])
                return datetime.now() - timedelta(days=days)
            elif date_str.endswith('h'):
                hours = int(date_str[:-1])
                return datetime.now() - timedelta(hours=hours)
            
            # 绝对日期格式: 2025-08-12, 2025-08-12T10:30:00
            for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            raise ValueError(f"无法解析日期格式: {date_str}")
            
        except Exception as e:
            print(f"❌ 日期解析错误: {e}")
            return None
    
    def filter_by_date_range(self, start_date: Optional[datetime], end_date: Optional[datetime]) -> List[Dict]:
        """根据日期范围筛选图片记录"""
        filtered_records = []
        
        for record_id, record in self.index.records.items():
            try:
                # 解析上传日期
                upload_date = datetime.fromisoformat(record.upload_date.replace('Z', '+00:00'))
                upload_date = upload_date.replace(tzinfo=None)  # 移除时区信息以简化比较
                
                # 检查是否在日期范围内
                if start_date and upload_date < start_date:
                    continue
                if end_date and upload_date > end_date:
                    continue
                
                # 添加记录ID到记录中
                record_dict = record.__dict__.copy()
                record_dict['record_id'] = record_id
                filtered_records.append(record_dict)
                
            except (ValueError, AttributeError) as e:
                print(f"⚠️  跳过无效记录 {record_id}: {e}")
                continue
        
        # 按上传日期排序
        filtered_records.sort(key=lambda x: x['upload_date'], reverse=True)
        return filtered_records
    
    def download_image_from_file_id(self, file_id: str, local_path: str) -> bool:
        """通过文件ID从OneDrive API下载图片"""
        if not self.uploader:
            print("❌ OneDrive API未初始化")
            return False
            
        try:
            # 创建目标目录
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 使用Graph API下载文件
            endpoint = f"/me/drive/items/{file_id}/content"
            response = self.uploader._make_request('GET', endpoint)
            response.raise_for_status()
            
            # 保存文件
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            return True
            
        except Exception as e:
            print(f"❌ API下载失败 {file_id}: {e}")
            return False

    def download_image_from_url(self, onedrive_url: str, local_path: str) -> bool:
        """从OneDrive URL下载图片到本地路径（备用方法）"""
        try:
            # 创建目标目录
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            
            # 处理不同类型的OneDrive链接
            download_url = self.get_direct_download_url(onedrive_url)
            
            # 下载文件
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(download_url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
            
        except Exception as e:
            print(f"❌ 下载失败 {onedrive_url}: {e}")
            return False
    
    def get_direct_download_url(self, onedrive_url: str) -> str:
        """将OneDrive分享链接转换为直接下载链接"""
        try:
            # 如果已经是直接下载链接，直接返回
            if 'download.aspx' in onedrive_url:
                return onedrive_url
            
            # 处理分享链接格式 https://7fp1fj-my.sharepoint.com/:i:/g/personal/...
            if ':i:/g/personal/' in onedrive_url:
                # SharePoint分享链接，添加download=1参数
                return onedrive_url + '?download=1'
            
            # 其他格式的链接，尝试直接使用
            return onedrive_url
            
        except Exception as e:
            print(f"⚠️  链接转换失败，使用原链接: {e}")
            return onedrive_url
    
    def download_by_date_range(self, 
                              start_date: Optional[str] = None, 
                              end_date: Optional[str] = None,
                              download_dir: str = "temp/date_downloads",
                              dry_run: bool = False,
                              limit: Optional[int] = None) -> Dict:
        """按日期范围下载图片"""
        
        # 解析日期
        start_dt = self.parse_date_input(start_date) if start_date else None
        end_dt = self.parse_date_input(end_date) if end_date else None
        
        print(f"📅 日期范围: {start_dt or '最早'} 到 {end_dt or '最新'}")
        
        # 筛选记录
        filtered_records = self.filter_by_date_range(start_dt, end_dt)
        
        if not filtered_records:
            print("📝 没有找到符合条件的图片记录")
            return {'success': True, 'downloaded': 0, 'failed': 0}
        
        # 应用数量限制
        if limit and len(filtered_records) > limit:
            filtered_records = filtered_records[:limit]
            print(f"🔍 找到 {len(self.filter_by_date_range(start_dt, end_dt))} 张图片，限制下载 {limit} 张")
        else:
            print(f"🔍 找到 {len(filtered_records)} 张图片")
        
        if dry_run:
            print("🔍 预览模式，不实际下载:")
            for record in filtered_records:
                print(f"  📸 {record['filename']} - {record['upload_date']} - {record['article_title']}")
            return {'success': True, 'downloaded': 0, 'failed': 0, 'preview_count': len(filtered_records)}
        
        # 创建下载目录
        download_path = Path(download_dir)
        download_path.mkdir(parents=True, exist_ok=True)
        
        # 执行下载
        downloaded = 0
        failed = 0
        
        for record in filtered_records:
            try:
                # 生成本地文件路径
                # 格式: download_dir/YYYY-MM-DD_原文件名
                date_str = record['upload_date'][:10]  # YYYY-MM-DD
                local_filename = f"{date_str}_{record['filename']}"
                local_path = download_path / local_filename
                
                # 跳过已存在的文件
                if local_path.exists():
                    print(f"⏭️  跳过已存在: {local_filename}")
                    continue
                
                print(f"📥 下载: {record['filename']} -> {local_filename}")
                
                # 优先使用API下载，如果有文件ID的话
                success = False
                if 'onedrive_file_id' in record and record['onedrive_file_id']:
                    print(f"🔑 使用API下载 ID: {record['onedrive_file_id']}")
                    success = self.download_image_from_file_id(record['onedrive_file_id'], str(local_path))
                
                # 如果API下载失败，尝试URL下载
                if not success:
                    print(f"🔗 尝试URL下载: {record['onedrive_url'][:100]}...")
                    success = self.download_image_from_url(record['onedrive_url'], str(local_path))
                
                if success:
                    downloaded += 1
                    print(f"✅ 成功: {local_filename}")
                else:
                    failed += 1
                    
            except Exception as e:
                print(f"❌ 处理失败 {record['filename']}: {e}")
                failed += 1
        
        return {
            'success': True,
            'downloaded': downloaded,
            'failed': failed,
            'download_dir': str(download_path)
        }
    
    def list_available_dates(self) -> Dict[str, int]:
        """列出可用的上传日期统计"""
        date_counts = {}
        
        for record in self.index.records.values():
            try:
                # 提取日期部分 (YYYY-MM-DD)
                date_str = record.upload_date[:10]
                date_counts[date_str] = date_counts.get(date_str, 0) + 1
            except Exception:
                continue
        
        return dict(sorted(date_counts.items(), reverse=True))

def main():
    parser = argparse.ArgumentParser(description='按日期下载OneDrive图片')
    parser.add_argument('--start-date', help='开始日期 (支持 2025-08-12 或 7d 格式)')
    parser.add_argument('--end-date', help='结束日期 (支持 2025-08-12 或 1d 格式)')
    parser.add_argument('--download-dir', default='temp/date_downloads', help='下载目录')
    parser.add_argument('--dry-run', action='store_true', help='预览模式，不实际下载')
    parser.add_argument('--list-dates', action='store_true', help='列出可用的上传日期')
    parser.add_argument('--limit', type=int, help='限制下载数量')
    parser.add_argument('--config', default='config/onedrive_config.json', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 初始化下载器
    downloader = OneDriveDateDownloader(args.config)
    
    if args.list_dates:
        print("📅 可用的上传日期:")
        dates = downloader.list_available_dates()
        if dates:
            for date, count in dates.items():
                print(f"  {date}: {count} 张图片")
        else:
            print("  没有找到图片记录")
        return
    
    # 执行下载
    result = downloader.download_by_date_range(
        start_date=args.start_date,
        end_date=args.end_date,
        download_dir=args.download_dir,
        dry_run=args.dry_run,
        limit=args.limit
    )
    
    if result['success']:
        if args.dry_run:
            print(f"🔍 预览完成，共 {result.get('preview_count', 0)} 张图片")
        else:
            print(f"📊 下载完成: {result['downloaded']} 成功, {result['failed']} 失败")
            if result['downloaded'] > 0:
                print(f"📁 下载目录: {result['download_dir']}")
    else:
        print("❌ 下载过程中出现错误")

if __name__ == '__main__':
    main()