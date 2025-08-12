#!/usr/bin/env python3
"""
OneDrive图片恢复工具
从OneDrive索引恢复图片到原始本地目录，保持原有文件名
"""

import json
import requests
import os
from pathlib import Path
from typing import Dict, List, Optional
import argparse
from urllib.parse import urlparse, parse_qs
import re

class OneDriveImageRecovery:
    def __init__(self, index_file: str = "_data/onedrive_image_index.json"):
        self.index_file = Path(index_file)
        self.index_data = self.load_index()
    
    def load_index(self) -> Dict:
        """加载OneDrive索引文件"""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 索引文件未找到: {self.index_file}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ 索引文件格式错误: {e}")
            return {}
    
    def extract_original_info(self, record: Dict) -> Optional[Dict]:
        """从索引记录中提取原始文件信息"""
        try:
            # 从Windows路径推断原始文件信息
            local_path = record.get('local_path', '')
            filename = record.get('filename', '')
            
            # 如果local_path包含Windows路径，解析出原始目录
            if '\\' in local_path:
                # Windows路径格式
                original_dir = Path(local_path).parent
                original_filename = Path(local_path).name
            else:
                # 项目内路径，使用文件名和推断的目录
                # 对于桌面图片，恢复到项目临时目录
                original_dir = Path("temp/recovered_images") 
                original_filename = filename
            
            return {
                'original_dir': str(original_dir),
                'original_filename': original_filename,
                'download_url': record.get('onedrive_url', ''),
                'article_title': record.get('article_title', ''),
                'upload_date': record.get('upload_date', '')
            }
        except Exception as e:
            print(f"⚠️ 无法解析记录: {e}")
            return None
    
    def convert_to_direct_download_url(self, share_url: str) -> str:
        """将OneDrive分享链接转换为直接下载链接"""
        try:
            # 对于SharePoint链接格式
            if 'sharepoint.com' in share_url and ':i:' in share_url:
                # 提取基础URL和文件ID
                base_match = re.search(r'(https://[^/]+)', share_url)
                if base_match:
                    base_url = base_match.group(1)
                    # 转换为直接下载格式
                    if '/personal/' in share_url:
                        personal_part = share_url.split('/personal/')[1].split('/')[0]
                        # 构建下载链接 - 这里可能需要根据实际链接格式调整
                        return f"{base_url}/personal/{personal_part}/_layouts/15/download.aspx"
            
            # 如果已经是下载链接，直接返回
            if 'download.aspx' in share_url:
                return share_url
                
            # 对于其他格式，尝试添加下载参数
            return share_url + "&download=1" if '?' in share_url else share_url + "?download=1"
            
        except Exception as e:
            print(f"⚠️ URL转换失败: {e}")
            return share_url
    
    def download_image(self, url: str, target_path: Path) -> bool:
        """下载图片到指定路径"""
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 转换为直接下载链接
            download_url = self.convert_to_direct_download_url(url)
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            print(f"📥 下载: {target_path.name}")
            response = requests.get(download_url, headers=headers, stream=True, timeout=30)
            
            if response.status_code == 200:
                with open(target_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"✅ 下载成功: {target_path}")
                return True
            else:
                print(f"❌ 下载失败 ({response.status_code}): {target_path.name}")
                return False
                
        except Exception as e:
            print(f"❌ 下载异常: {e}")
            return False
    
    def recover_images_for_article(self, article_title: str) -> Dict:
        """恢复指定文章的所有图片"""
        recovered = []
        failed = []
        
        print(f"\n🔄 开始恢复文章图片: {article_title}")
        
        for key, record in self.index_data.items():
            if record.get('article_title') == article_title:
                info = self.extract_original_info(record)
                if not info:
                    failed.append(f"无法解析记录: {key}")
                    continue
                
                # 构建目标路径
                if info['original_dir'].startswith('c:') or info['original_dir'].startswith('C:'):
                    # Windows路径，转换为WSL格式并恢复到项目临时目录
                    target_dir = Path("temp/recovered_images/desktop")
                else:
                    # 项目内路径，恢复到原位置
                    target_dir = Path(info['original_dir'])
                
                target_path = target_dir / info['original_filename']
                
                # 如果文件已存在，询问是否覆盖
                if target_path.exists():
                    response = input(f"文件已存在: {target_path}\n是否覆盖? (y/N): ").strip().lower()
                    if response != 'y':
                        print(f"⏭️ 跳过: {target_path.name}")
                        continue
                
                # 下载图片
                if self.download_image(info['download_url'], target_path):
                    recovered.append(str(target_path))
                else:
                    failed.append(f"{info['original_filename']}: 下载失败")
        
        return {
            'recovered': recovered,
            'failed': failed,
            'total': len(recovered) + len(failed)
        }
    
    def recover_all_images(self) -> Dict:
        """恢复所有图片"""
        print("🔄 开始恢复所有图片...")
        
        all_recovered = []
        all_failed = []
        
        # 按文章分组处理
        articles = set(record.get('article_title', '') for record in self.index_data.values())
        
        for article in articles:
            if article:
                result = self.recover_images_for_article(article)
                all_recovered.extend(result['recovered'])
                all_failed.extend(result['failed'])
        
        return {
            'recovered': all_recovered,
            'failed': all_failed,
            'total': len(all_recovered) + len(all_failed)
        }
    
    def list_recoverable_images(self) -> None:
        """列出可恢复的图片"""
        print("\n📋 可恢复的图片列表:")
        print("=" * 60)
        
        articles = {}
        for key, record in self.index_data.items():
            article = record.get('article_title', '未知文章')
            if article not in articles:
                articles[article] = []
            
            info = self.extract_original_info(record)
            if info:
                articles[article].append({
                    'filename': info['original_filename'],
                    'original_dir': info['original_dir'],
                    'upload_date': info['upload_date']
                })
        
        for article, images in articles.items():
            print(f"\n📄 {article}")
            print(f"   图片数量: {len(images)}")
            for img in images:
                print(f"   📸 {img['filename']}")
                print(f"      原始目录: {img['original_dir']}")
                print(f"      上传时间: {img['upload_date']}")

def main():
    parser = argparse.ArgumentParser(description="OneDrive图片恢复工具")
    parser.add_argument('--article', '-a', help="恢复指定文章的图片")
    parser.add_argument('--all', action='store_true', help="恢复所有图片")
    parser.add_argument('--list', '-l', action='store_true', help="列出可恢复的图片")
    parser.add_argument('--index', '-i', default="_data/onedrive_image_index.json", 
                       help="索引文件路径")
    
    args = parser.parse_args()
    
    recovery = OneDriveImageRecovery(args.index)
    
    if not recovery.index_data:
        print("❌ 无可用的索引数据")
        return
    
    if args.list:
        recovery.list_recoverable_images()
    elif args.article:
        result = recovery.recover_images_for_article(args.article)
        print(f"\n📊 恢复结果:")
        print(f"✅ 成功: {len(result['recovered'])} 个文件")
        print(f"❌ 失败: {len(result['failed'])} 个文件")
        if result['failed']:
            print("失败详情:")
            for failure in result['failed']:
                print(f"  - {failure}")
    elif args.all:
        result = recovery.recover_all_images()
        print(f"\n📊 恢复结果:")
        print(f"✅ 成功: {len(result['recovered'])} 个文件")
        print(f"❌ 失败: {len(result['failed'])} 个文件")
        if result['failed']:
            print("失败详情:")
            for failure in result['failed']:
                print(f"  - {failure}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()