#!/usr/bin/env python3
"""
自动Header图片处理器
Auto Header Image Processor

功能：
1. 自动使用正文第一张图片作为header的overlay_image和teaser
2. 支持临时目录图片的智能处理
3. 与OneDrive图片管理系统集成

使用方法：
python scripts/tools/auto_header_image_processor.py "_posts/article.md"
"""

import re
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AutoHeaderImageProcessor:
    """自动Header图片处理器"""
    
    def __init__(self, config_path: str = "config/onedrive_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
            return {}
    
    def process_article_header(self, article_path: str, dry_run: bool = False) -> Dict:
        """
        处理文章的header图片设置
        
        Args:
            article_path: 文章路径
            dry_run: 是否为演练模式
            
        Returns:
            处理结果字典
        """
        article_file = Path(article_path)
        if not article_file.exists():
            return {'success': False, 'error': 'Article file not found'}
        
        logger.info(f"Processing header images for: {article_path}")
        print("🖼️  自动Header图片处理器")
        print("=" * 50)
        
        try:
            # 读取文章内容
            with open(article_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析Front Matter和正文
            front_matter, body_content = self._parse_front_matter(content)
            if not front_matter:
                return {'success': False, 'error': 'No front matter found'}
            
            # 查找正文中的第一张图片
            first_image = self._find_first_body_image(body_content)
            if not first_image:
                return {'success': False, 'error': 'No images found in article body'}
            
            print(f"📍 发现第一张图片: {first_image['path']}")
            
            # 检查是否需要更新header
            needs_update = self._check_header_update_needed(front_matter, first_image)
            
            if not needs_update:
                print("✅ Header图片已是最新，无需更新")
                return {'success': True, 'message': 'Header already up to date'}
            
            # 准备更新header
            updated_front_matter = self._update_header_images(front_matter, first_image)
            
            if dry_run:
                print("🔍 演练模式 - 将要进行的更改:")
                self._show_planned_changes(front_matter, updated_front_matter)
                return {'success': True, 'message': 'Dry run completed'}
            
            # 写入更新的文章
            updated_content = self._rebuild_article(updated_front_matter, body_content)
            
            # 备份原文件
            backup_path = article_file.with_suffix('.md.backup')
            article_file.rename(backup_path)
            print(f"📦 备份原文件: {backup_path}")
            
            # 写入新文件
            with open(article_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("✅ Header图片设置完成")
            
            return {
                'success': True,
                'first_image': first_image['path'],
                'backup_created': str(backup_path),
                'changes': self._get_changes_summary(front_matter, updated_front_matter)
            }
            
        except Exception as e:
            logger.error(f"Failed to process header images: {e}")
            return {'success': False, 'error': str(e)}
    
    def _parse_front_matter(self, content: str) -> Tuple[Optional[Dict], str]:
        """解析Front Matter和正文内容"""
        front_matter_pattern = re.compile(r'^---\s*\n(.*?)\n---\s*\n(.*)', re.DOTALL)
        match = front_matter_pattern.match(content)
        
        if not match:
            return None, content
        
        try:
            yaml_content = match.group(1)
            body_content = match.group(2)
            
            # 解析YAML
            front_matter = yaml.safe_load(yaml_content)
            return front_matter, body_content
            
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML front matter: {e}")
            return None, content
    
    def _find_first_body_image(self, body_content: str) -> Optional[Dict]:
        """查找正文中的第一张图片"""
        # 跳过front matter后的第一张图片
        image_pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')
        
        for match in image_pattern.finditer(body_content):
            alt_text = match.group(1)
            img_path = match.group(2).strip()
            
            # 跳过网络链接
            if img_path.startswith(('http://', 'https://')):
                continue
            
            # 跳过已经处理过的OneDrive链接
            if 'sharepoint.com' in img_path or 'onedrive' in img_path:
                continue
                
            return {
                'alt_text': alt_text,
                'path': img_path,
                'markdown': match.group(0)
            }
        
        return None
    
    def _check_header_update_needed(self, front_matter: Dict, first_image: Dict) -> bool:
        """检查是否需要更新header"""
        header = front_matter.get('header', {})
        
        # 检查overlay_image
        current_overlay = header.get('overlay_image', '')
        # 检查teaser
        current_teaser = header.get('teaser', '')
        
        first_image_path = first_image['path']
        
        # 如果header为空，需要更新
        if not current_overlay and not current_teaser:
            return True
        
        # 如果header指向的不是第一张图片，需要更新
        # 简化路径比较（去除可能的baseurl变量）
        def normalize_path(path: str) -> str:
            # 移除Jekyll变量
            path = re.sub(r'\{\{\s*site\.baseurl\s*\}\}/?', '', path)
            # 移除引号
            path = path.strip('\'"')
            return path.strip()
        
        current_overlay_norm = normalize_path(current_overlay)
        current_teaser_norm = normalize_path(current_teaser)
        first_image_norm = normalize_path(first_image_path)
        
        # 检查路径是否匹配（允许部分匹配，因为可能有baseurl差异）
        overlay_matches = (current_overlay_norm.endswith(first_image_norm) or 
                          first_image_norm.endswith(current_overlay_norm))
        teaser_matches = (current_teaser_norm.endswith(first_image_norm) or 
                         first_image_norm.endswith(current_teaser_norm))
        
        return not (overlay_matches and teaser_matches)
    
    def _update_header_images(self, front_matter: Dict, first_image: Dict) -> Dict:
        """更新header中的图片设置"""
        updated_fm = front_matter.copy()
        
        # 确保header字典存在
        if 'header' not in updated_fm:
            updated_fm['header'] = {}
        
        # 构造图片路径
        # 如果是临时目录的图片，保持原路径，等待后续OneDrive处理
        img_path = first_image['path']
        
        # 如果不是临时目录，使用Jekyll baseurl格式
        if not img_path.startswith('temp/drafting/'):
            if not img_path.startswith('{{ site.baseurl }}'):
                img_path = f"{{{{ site.baseurl }}}}/{img_path.lstrip('/')}"
        
        # 更新header设置
        updated_fm['header']['overlay_image'] = img_path
        updated_fm['header']['teaser'] = img_path
        
        # 确保overlay_filter存在
        if 'overlay_filter' not in updated_fm['header']:
            updated_fm['header']['overlay_filter'] = 0.5
        
        return updated_fm
    
    def _show_planned_changes(self, old_fm: Dict, new_fm: Dict):
        """显示计划的更改"""
        old_header = old_fm.get('header', {})
        new_header = new_fm.get('header', {})
        
        print("📋 计划更改:")
        print(f"   overlay_image: {old_header.get('overlay_image', '(未设置)')} → {new_header.get('overlay_image')}")
        print(f"   teaser: {old_header.get('teaser', '(未设置)')} → {new_header.get('teaser')}")
        print(f"   overlay_filter: {old_header.get('overlay_filter', '(未设置)')} → {new_header.get('overlay_filter')}")
    
    def _get_changes_summary(self, old_fm: Dict, new_fm: Dict) -> Dict:
        """获取更改摘要"""
        old_header = old_fm.get('header', {})
        new_header = new_fm.get('header', {})
        
        return {
            'overlay_image': {
                'old': old_header.get('overlay_image'),
                'new': new_header.get('overlay_image')
            },
            'teaser': {
                'old': old_header.get('teaser'),
                'new': new_header.get('teaser')
            }
        }
    
    def _rebuild_article(self, front_matter: Dict, body_content: str) -> str:
        """重建文章内容"""
        # 转换front matter为YAML
        yaml_content = yaml.dump(front_matter, default_flow_style=False, 
                                allow_unicode=True, sort_keys=False)
        
        # 重建完整文章
        return f"---\n{yaml_content}---\n{body_content}"


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='自动Header图片处理器')
    parser.add_argument('article_path', help='文章路径')
    parser.add_argument('--dry-run', action='store_true', help='演练模式，不实际修改文件')
    parser.add_argument('--config', default='config/onedrive_config.json', help='配置文件路径')
    
    args = parser.parse_args()
    
    processor = AutoHeaderImageProcessor(args.config)
    result = processor.process_article_header(args.article_path, args.dry_run)
    
    if result['success']:
        print(f"\n✅ 处理完成: {result.get('message', '')}")
        if 'first_image' in result:
            print(f"🖼️  使用图片: {result['first_image']}")
    else:
        print(f"\n❌ 处理失败: {result.get('error')}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())