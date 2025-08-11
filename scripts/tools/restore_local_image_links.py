#!/usr/bin/env python3
"""
OneDrive图片链接恢复到本地链接脚本
根据索引记录将文章中的OneDrive链接恢复为本地Jekyll路径
"""

import json
import re
from pathlib import Path
from typing import Dict, List
import argparse


def load_image_index(index_path: str = "_data/onedrive_image_index.json") -> Dict:
    """加载OneDrive图片索引"""
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载图片索引失败: {e}")
        return {}


def extract_article_records(index_data: Dict, article_file: str) -> List[Dict]:
    """提取指定文章的图片记录"""
    article_records = []
    for record_id, record in index_data.items():
        if record.get('article_file') == article_file:
            article_records.append(record)
    
    # 按图片索引排序
    article_records.sort(key=lambda x: x.get('image_index', 0))
    return article_records


def restore_article_links(article_path: str, dry_run: bool = True) -> Dict:
    """恢复文章中的OneDrive链接为本地链接"""
    try:
        article_file = Path(article_path)
        if not article_file.exists():
            return {'success': False, 'error': 'Article file not found'}
        
        # 加载索引数据
        index_data = load_image_index()
        if not index_data:
            return {'success': False, 'error': 'Failed to load image index'}
        
        # 读取文章内容
        with open(article_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 获取文章的图片记录
        article_records = extract_article_records(index_data, str(article_file))
        if not article_records:
            return {'success': True, 'message': 'No image records found for this article', 'changes': 0}
        
        print(f"📝 处理文章: {article_path}")
        print(f"🔍 找到 {len(article_records)} 个图片记录")
        
        # 执行替换
        replacements = []
        updated_content = content
        
        for record in article_records:
            onedrive_url = record.get('embed_url') or record.get('onedrive_url')
            local_path = record.get('local_path')
            
            if not onedrive_url or not local_path:
                continue
            
            # 转换本地路径为Jekyll格式
            jekyll_path = convert_to_jekyll_path(local_path)
            
            # 查找文章中的OneDrive链接
            # 匹配格式: ![alt_text](onedrive_url)
            pattern = rf'!\[([^\]]*)\]\({re.escape(onedrive_url)}\)'
            matches = list(re.finditer(pattern, updated_content))
            
            if matches:
                for match in matches:
                    old_link = match.group(0)
                    alt_text = match.group(1)
                    new_link = f"![{alt_text}]({jekyll_path})"
                    
                    updated_content = updated_content.replace(old_link, new_link)
                    replacements.append({
                        'old': old_link,
                        'new': new_link,
                        'local_path': local_path,
                        'jekyll_path': jekyll_path
                    })
                    
                    print(f"✅ 替换: {alt_text}")
                    print(f"   从: {onedrive_url}")
                    print(f"   到: {jekyll_path}")
        
        # 如果不是演练模式，写回文件
        if not dry_run and replacements:
            with open(article_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"💾 已更新文件: {article_path}")
        elif dry_run:
            print(f"🔍 演练模式: 将替换 {len(replacements)} 个链接")
        
        return {
            'success': True,
            'changes': len(replacements),
            'replacements': replacements
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}


def convert_to_jekyll_path(local_path: str) -> str:
    """将本地路径转换为Jekyll路径格式"""
    # 清理路径
    clean_path = local_path.replace('_drafts/../', '').replace('../', '')
    
    # 确保以assets开头
    if not clean_path.startswith('assets/'):
        if clean_path.startswith('/'):
            clean_path = clean_path[1:]
        clean_path = f"assets/{clean_path}"
    
    # 添加Jekyll baseurl前缀
    return f"{{{{ site.baseurl }}}}/{clean_path}"


def main():
    parser = argparse.ArgumentParser(description="恢复OneDrive图片链接为本地链接")
    parser.add_argument("article_path", help="文章文件路径")
    parser.add_argument("--dry-run", action="store_true", help="演练模式，不实际修改文件")
    parser.add_argument("--index-path", default="_data/onedrive_image_index.json", help="图片索引文件路径")
    
    args = parser.parse_args()
    
    # 执行恢复
    result = restore_article_links(args.article_path, dry_run=args.dry_run)
    
    if result['success']:
        if result.get('changes', 0) > 0:
            print(f"\n🎉 成功处理 {result['changes']} 个图片链接")
        else:
            print(f"\n📄 {result.get('message', '处理完成，无需更改')}")
    else:
        print(f"\n❌ 处理失败: {result['error']}")


if __name__ == "__main__":
    main()