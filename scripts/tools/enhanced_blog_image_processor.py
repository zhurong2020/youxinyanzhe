#!/usr/bin/env python3
"""
增强博客图片处理器 - 集成自动Header功能
Enhanced Blog Image Processor with Auto Header Feature

功能：
1. 自动使用正文第一张图片设置header
2. 处理所有图片上传到OneDrive
3. 替换所有图片链接（包括header中的）
4. 完整的工作流程自动化

使用方法：
python scripts/tools/enhanced_blog_image_processor.py "_posts/article.md" [--dry-run] [--skip-header]
"""

import sys
import os
import logging
from pathlib import Path
from typing import Dict

# 添加工具目录到路径
sys.path.append(str(Path(__file__).parent))

try:
    from auto_header_image_processor import AutoHeaderImageProcessor
    from onedrive_blog_images import BlogImageManager
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all required modules are available")
    sys.exit(1)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnhancedBlogImageProcessor:
    """增强博客图片处理器"""
    
    def __init__(self, config_path: str = "config/onedrive_config.json"):
        self.config_path = config_path
        self.header_processor = AutoHeaderImageProcessor(config_path)
        self.onedrive_processor = None
        
        # 延迟初始化OneDrive处理器（可能需要认证）
        try:
            self.onedrive_processor = BlogImageManager(config_path)
        except Exception as e:
            logger.warning(f"OneDrive processor initialization deferred: {e}")
    
    def process_article_complete(self, article_path: str, 
                               skip_header: bool = False, 
                               dry_run: bool = False) -> Dict:
        """
        完整处理文章：自动header + 图片上传
        
        Args:
            article_path: 文章路径
            skip_header: 是否跳过header自动设置
            dry_run: 是否为演练模式
            
        Returns:
            处理结果字典
        """
        print("🚀 增强博客图片处理器")
        print("=" * 60)
        
        results = {
            'success': True,
            'article_path': article_path,
            'stages_completed': [],
            'header_processing': {},
            'image_upload': {},
            'errors': []
        }
        
        try:
            # 阶段1: 自动Header设置
            if not skip_header:
                print("\\n📋 阶段1: 自动Header设置...")
                header_result = self.header_processor.process_article_header(
                    article_path, dry_run=dry_run
                )
                
                results['header_processing'] = header_result
                
                if header_result['success']:
                    results['stages_completed'].append('auto_header')
                    if 'first_image' in header_result:
                        print(f"✅ Header已设置为: {header_result['first_image']}")
                    else:
                        print("✅ Header无需更新")
                else:
                    print(f"⚠️  Header处理警告: {header_result.get('error')}")
                    results['errors'].append(f"Header: {header_result.get('error')}")
            else:
                print("⏭️  跳过Header自动设置")
            
            # 阶段2: 图片上传和链接替换
            print("\\n☁️  阶段2: 图片上传到OneDrive...")
            
            if dry_run:
                print("🔍 演练模式 - 跳过实际上传")
                results['image_upload'] = {
                    'success': True,
                    'message': 'Dry run - upload skipped'
                }
            else:
                # 初始化OneDrive处理器（如果还未初始化）
                if not self.onedrive_processor:
                    try:
                        self.onedrive_processor = BlogImageManager(self.config_path)
                    except Exception as e:
                        error_msg = f"Failed to initialize OneDrive processor: {e}"
                        results['errors'].append(error_msg)
                        results['success'] = False
                        return results
                
                # 处理图片上传
                upload_result = self.onedrive_processor.process_draft(article_path)
                results['image_upload'] = upload_result
                
                if upload_result['success']:
                    results['stages_completed'].append('image_upload')
                    processed_count = upload_result.get('images_processed', 0)
                    print(f"✅ 成功处理 {processed_count} 张图片")
                    
                    # 显示处理详情
                    if 'processed_images' in upload_result:
                        for img_info in upload_result['processed_images']:
                            print(f"   📸 {img_info.get('local_path')} → OneDrive")
                else:
                    error_msg = f"图片上传失败: {upload_result.get('error')}"
                    results['errors'].append(error_msg)
                    print(f"❌ {error_msg}")
            
            # 阶段3: 完成总结
            print("\\n📊 处理总结:")
            print(f"   文章: {Path(article_path).name}")
            print(f"   完成阶段: {', '.join(results['stages_completed'])}")
            
            if results['errors']:
                print(f"   警告/错误: {len(results['errors'])}")
                for error in results['errors']:
                    print(f"     - {error}")
                # 如果有错误，但至少完成了一个阶段，仍认为部分成功
                results['success'] = len(results['stages_completed']) > 0
            else:
                print("   状态: 全部成功 ✅")
            
            return results
            
        except Exception as e:
            logger.error(f"Enhanced processing failed: {e}")
            results['success'] = False
            results['errors'].append(f"系统错误: {str(e)}")
            return results
    
    def get_processing_summary(self, results: Dict) -> str:
        """生成处理摘要文本"""
        lines = []
        lines.append("=" * 50)
        lines.append("📊 博客图片处理摘要")
        lines.append("=" * 50)
        
        lines.append(f"文章: {Path(results['article_path']).name}")
        lines.append(f"状态: {'成功' if results['success'] else '失败'}")
        
        if results['stages_completed']:
            lines.append(f"完成阶段: {', '.join(results['stages_completed'])}")
        
        # Header处理摘要
        if 'header_processing' in results and results['header_processing']:
            hp = results['header_processing']
            if hp.get('success') and 'first_image' in hp:
                lines.append(f"Header图片: {hp['first_image']}")
        
        # 图片上传摘要
        if 'image_upload' in results and results['image_upload']:
            iu = results['image_upload']
            if iu.get('success') and 'images_processed' in iu:
                lines.append(f"处理图片: {iu['images_processed']} 张")
        
        # 错误摘要
        if results['errors']:
            lines.append("⚠️  警告/错误:")
            for error in results['errors']:
                lines.append(f"  - {error}")
        
        return "\\n".join(lines)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='增强博客图片处理器')
    parser.add_argument('article_path', help='文章路径')
    parser.add_argument('--dry-run', action='store_true', help='演练模式，不实际修改文件')
    parser.add_argument('--skip-header', action='store_true', help='跳过自动header设置')
    parser.add_argument('--config', default='config/onedrive_config.json', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 检查文章文件是否存在
    if not Path(args.article_path).exists():
        print(f"❌ 文章文件不存在: {args.article_path}")
        return 1
    
    # 创建处理器并执行
    processor = EnhancedBlogImageProcessor(args.config)
    results = processor.process_article_complete(
        args.article_path, 
        skip_header=args.skip_header,
        dry_run=args.dry_run
    )
    
    # 显示最终摘要
    print("\\n" + processor.get_processing_summary(results))
    
    # 返回适当的退出码
    return 0 if results['success'] else 1


if __name__ == '__main__':
    exit(main())