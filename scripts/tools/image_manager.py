#!/usr/bin/env python3
"""
智能图片管理工具
根据文件大小和用途自动选择存储策略
"""

import os
import shutil
from pathlib import Path
from PIL import Image
import requests
import json
from typing import Dict, Optional, Union
import argparse

class ImageManager:
    def __init__(self, config_path: str = "config/image_config.json"):
        """初始化图片管理器"""
        self.config = self._load_config(config_path)
        self.size_thresholds = {
            'tiny': 50 * 1024,      # 50KB
            'small': 200 * 1024,    # 200KB
            'medium': 1024 * 1024,  # 1MB
        }
        
    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        default_config = {
            "local_path": "assets/images/posts/",
            "cdn_config": {
                "provider": "imgbb",  # 或 "cloudinary"
                "api_key": "",
                "base_url": ""
            },
            "compression": {
                "jpeg_quality": 85,
                "webp_quality": 80,
                "png_optimize": True
            },
            "max_width": 1200,
            "thumbnail_width": 400
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def analyze_image(self, image_path: str) -> Dict:
        """分析图片信息"""
        path = Path(image_path)
        size = path.stat().st_size
        
        with Image.open(image_path) as img:
            width, height = img.size
            format_type = img.format.lower() if img.format else 'unknown'
        
        # 确定存储策略
        if size < self.size_thresholds['tiny']:
            storage = 'local'
            reason = f'超小图片 ({size//1024}KB < 50KB)'
        elif size < self.size_thresholds['small']:
            storage = 'local_compressed'
            reason = f'小图片 ({size//1024}KB < 200KB), 建议压缩'
        elif size < self.size_thresholds['medium']:
            storage = 'cdn'
            reason = f'中图片 ({size//1024}KB < 1MB), CDN存储'
        else:
            storage = 'cdn_with_thumbnail'
            reason = f'大图片 ({size//1024}KB > 1MB), CDN+缩略图'
        
        return {
            'path': image_path,
            'size': size,
            'dimensions': (width, height),
            'format': format_type,
            'storage_strategy': storage,
            'reason': reason
        }
    
    def optimize_image(self, input_path: str, output_path: str, 
                      max_width: Optional[int] = None) -> bool:
        """优化图片"""
        try:
            with Image.open(input_path) as img:
                # 转换为RGB如果是RGBA（针对JPEG）
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 创建白色背景
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
                    img = background
                
                # 调整尺寸
                if max_width and img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                # 保存优化后的图片
                save_kwargs = {}
                if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
                    save_kwargs['quality'] = self.config['compression']['jpeg_quality']
                    save_kwargs['optimize'] = True
                elif output_path.lower().endswith('.webp'):
                    save_kwargs['quality'] = self.config['compression']['webp_quality']
                    save_kwargs['method'] = 6  # 最佳压缩
                elif output_path.lower().endswith('.png'):
                    save_kwargs['optimize'] = self.config['compression']['png_optimize']
                
                img.save(output_path, **save_kwargs)
                return True
                
        except Exception as e:
            print(f"优化图片失败: {e}")
            return False
    
    def upload_to_cdn(self, image_path: str) -> Optional[str]:
        """上传图片到CDN"""
        provider = self.config['cdn_config']['provider']
        
        if provider == 'imgbb':
            return self._upload_to_imgbb(image_path)
        elif provider == 'cloudinary':
            return self._upload_to_cloudinary(image_path)
        else:
            print(f"不支持的CDN提供商: {provider}")
            return None
    
    def _upload_to_imgbb(self, image_path: str) -> Optional[str]:
        """上传到ImgBB"""
        api_key = self.config['cdn_config']['api_key']
        if not api_key:
            print("错误: 未配置ImgBB API密钥")
            return None
        
        try:
            with open(image_path, 'rb') as file:
                payload = {'key': api_key}
                files = {'image': file}
                
                response = requests.post(
                    'https://api.imgbb.com/1/upload',
                    data=payload,
                    files=files
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data['data']['url']
                else:
                    print(f"上传失败: {response.text}")
                    return None
        except Exception as e:
            print(f"上传到ImgBB失败: {e}")
            return None
    
    def _upload_to_cloudinary(self, image_path: str) -> Optional[str]:
        """上传到Cloudinary（需要安装cloudinary库）"""
        try:
            # 可选导入 - 仅在使用Cloudinary时需要
            import cloudinary  # type: ignore
            import cloudinary.uploader  # type: ignore
            
            # 这里需要配置Cloudinary凭据
            result = cloudinary.uploader.upload(image_path)
            return result['secure_url']
        except ImportError:
            print("错误: 未安装cloudinary库，运行: pip install cloudinary")
            return None
        except Exception as e:
            print(f"上传到Cloudinary失败: {e}")
            return None
    
    def process_image(self, image_path: str, article_date: str) -> Dict:
        """处理单个图片"""
        analysis = self.analyze_image(image_path)
        result = {'analysis': analysis, 'processed': False, 'markdown_link': ''}
        
        file_name = Path(image_path).stem
        strategy = analysis['storage_strategy']
        
        if strategy == 'local':
            # 直接复制到本地
            local_dir = Path(self.config['local_path']) / article_date
            local_dir.mkdir(parents=True, exist_ok=True)
            dest_path = local_dir / Path(image_path).name
            shutil.copy2(image_path, dest_path)
            
            result['markdown_link'] = f'![{file_name}]({{% site.baseurl %}}/assets/images/posts/{article_date}/{Path(image_path).name})'
            result['processed'] = True
            
        elif strategy == 'local_compressed':
            # 压缩后存储到本地
            local_dir = Path(self.config['local_path']) / article_date
            local_dir.mkdir(parents=True, exist_ok=True)
            dest_path = local_dir / f"{file_name}_compressed.webp"
            
            if self.optimize_image(image_path, str(dest_path), self.config['max_width']):
                result['markdown_link'] = f'![{file_name}]({{% site.baseurl %}}/assets/images/posts/{article_date}/{dest_path.name})'
                result['processed'] = True
            
        elif strategy in ['cdn', 'cdn_with_thumbnail']:
            # 上传到CDN
            cdn_url = self.upload_to_cdn(image_path)
            if cdn_url:
                result['markdown_link'] = f'![{file_name}]({cdn_url})'
                result['processed'] = True
                
                # 如果需要缩略图，也生成一个本地版本
                if strategy == 'cdn_with_thumbnail':
                    local_dir = Path(self.config['local_path']) / article_date
                    local_dir.mkdir(parents=True, exist_ok=True)
                    thumb_path = local_dir / f"{file_name}_thumb.webp"
                    
                    if self.optimize_image(image_path, str(thumb_path), 
                                         self.config['thumbnail_width']):
                        result['thumbnail_link'] = f'![{file_name} thumbnail]({{% site.baseurl %}}/assets/images/posts/{article_date}/{thumb_path.name})'
        
        return result
    
    def batch_process(self, image_dir: Union[str, Path], article_date: str) -> Dict:
        """批量处理图片"""
        results = {}
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
        
        image_dir_path = Path(image_dir)
        if not image_dir_path.exists():
            return {'error': f'目录不存在: {image_dir}'}
        
        image_files = [f for f in image_dir_path.glob('*') 
                      if f.suffix.lower() in image_extensions]
        
        if not image_files:
            return {'warning': '未找到图片文件'}
        
        total_size_before = 0
        total_size_after = 0
        
        for image_file in image_files:
            original_size = image_file.stat().st_size
            total_size_before += original_size
            
            result = self.process_image(str(image_file), article_date)
            results[image_file.name] = result
            
            # 计算处理后的大小（近似）
            if result['processed']:
                if 'compressed' in result['analysis']['storage_strategy']:
                    # 估算压缩后大小为原始大小的60%
                    total_size_after += original_size * 0.6
                elif 'local' in result['analysis']['storage_strategy']:
                    total_size_after += original_size
        
        results['summary'] = {
            'total_images': len(image_files),
            'processed': sum(1 for r in results.values() if isinstance(r, dict) and r.get('processed', False)),
            'original_size_mb': round(total_size_before / (1024*1024), 2),
            'estimated_size_mb': round(total_size_after / (1024*1024), 2),
            'space_saved_mb': round((total_size_before - total_size_after) / (1024*1024), 2)
        }
        
        return results

def main():
    parser = argparse.ArgumentParser(description='智能图片管理工具')
    parser.add_argument('--image-dir', required=True, help='图片目录路径')
    parser.add_argument('--article-date', required=True, help='文章日期 (YYYY/MM)')
    parser.add_argument('--config', default='config/image_config.json', help='配置文件路径')
    parser.add_argument('--analyze-only', action='store_true', help='仅分析不处理')
    
    args = parser.parse_args()
    
    manager = ImageManager(args.config)
    
    if args.analyze_only:
        # 仅分析模式
        results = {}
        image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}
        
        for image_file in Path(args.image_dir).glob('*'):
            if image_file.suffix.lower() in image_extensions:
                analysis = manager.analyze_image(str(image_file))
                results[image_file.name] = analysis
        
        print("\n=== 图片分析结果 ===")
        for filename, analysis in results.items():
            print(f"\n📁 {filename}")
            print(f"   大小: {analysis['size']//1024}KB")
            print(f"   尺寸: {analysis['dimensions'][0]}×{analysis['dimensions'][1]}")
            print(f"   策略: {analysis['storage_strategy']}")
            print(f"   原因: {analysis['reason']}")
    else:
        # 处理模式
        results = manager.batch_process(args.image_dir, args.article_date)
        
        print("\n=== 处理结果 ===")
        if 'summary' in results:
            summary = results['summary']
            print(f"总图片数: {summary['total_images']}")
            print(f"已处理: {summary['processed']}")
            print(f"原始大小: {summary['original_size_mb']}MB")
            print(f"处理后大小: {summary['estimated_size_mb']}MB")
            print(f"节省空间: {summary['space_saved_mb']}MB")
        
        print("\n=== Markdown链接 ===")
        for filename, result in results.items():
            if isinstance(result, dict) and result.get('processed'):
                print(f"# {filename}")
                print(result['markdown_link'])
                if 'thumbnail_link' in result:
                    print(f"# 缩略图: {result['thumbnail_link']}")
                print()

if __name__ == '__main__':
    main()