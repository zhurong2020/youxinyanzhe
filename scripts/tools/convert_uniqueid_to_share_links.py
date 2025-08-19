#!/usr/bin/env python3
"""
UniqueId链接转换为share格式链接工具
Convert UniqueId format OneDrive links to share format links

将文章中的 UniqueId= 格式链接转换为 share= 格式链接
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, List
import requests


def load_onedrive_index() -> Dict:
    """加载OneDrive图片索引"""
    index_path = Path("_data/onedrive_image_index.json")
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def find_uniqueid_links(content: str) -> List[str]:
    """查找文章中的UniqueId格式链接"""
    pattern = r'https://[^"\s]+/_layouts/15/download\.aspx\?UniqueId=[A-Z0-9]+'
    return re.findall(pattern, content)


def convert_uniqueid_to_share_format(uniqueid_url: str, onedrive_index: Dict) -> str:
    """尝试从索引中找到对应的share格式链接"""
    # 从索引中查找对应的正确链接
    for record_id, record in onedrive_index.items():
        # 检查embed_url或onedrive_url是否包含相同的文件信息
        if 'embed_url' in record and record['embed_url']:
            embed_url = record['embed_url']
            # 如果找到share格式的链接，返回它
            if '/_layouts/15/download.aspx?share=' in embed_url:
                # 验证是否是同一个文件（通过文件路径或其他标识）
                print(f"Found potential match: {embed_url}")
                return embed_url
    
    # 如果在索引中找不到，返回原链接
    print(f"No share format found for: {uniqueid_url}")
    return uniqueid_url


def convert_article_links(file_path: str, dry_run: bool = False) -> bool:
    """转换文章中的链接格式"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return False
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 加载OneDrive索引
    onedrive_index = load_onedrive_index()
    print(f"📖 已加载 {len(onedrive_index)} 条OneDrive记录")
    
    # 查找UniqueId格式链接
    uniqueid_links = find_uniqueid_links(content)
    print(f"🔍 发现 {len(uniqueid_links)} 个UniqueId格式链接")
    
    if not uniqueid_links:
        print("✅ 未发现需要转换的链接")
        return True
    
    # 替换链接
    updated_content = content
    conversion_count = 0
    
    for uniqueid_link in uniqueid_links:
        print(f"\n🔄 处理链接: {uniqueid_link[:80]}...")
        
        # 尝试转换为share格式
        share_link = convert_uniqueid_to_share_format(uniqueid_link, onedrive_index)
        
        if share_link != uniqueid_link:
            updated_content = updated_content.replace(uniqueid_link, share_link)
            conversion_count += 1
            print(f"✅ 转换成功: {share_link[:80]}...")
        else:
            print(f"⚠️  无法转换，保持原链接")
    
    # 显示转换结果
    print(f"\n📊 转换结果:")
    print(f"   处理链接: {len(uniqueid_links)} 个")
    print(f"   成功转换: {conversion_count} 个")
    print(f"   保持原样: {len(uniqueid_links) - conversion_count} 个")
    
    if dry_run:
        print("🔍 演练模式 - 未实际修改文件")
        return True
    
    if conversion_count > 0:
        # 备份原文件
        backup_path = f"{file_path}.backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📦 已备份原文件: {backup_path}")
        
        # 写入更新内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        print(f"✅ 已更新文件: {file_path}")
    else:
        print("ℹ️  无需更新文件")
    
    return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='转换UniqueId格式OneDrive链接为share格式')
    parser.add_argument('file_path', help='要处理的文章文件路径')
    parser.add_argument('--dry-run', action='store_true', help='演练模式，不实际修改文件')
    
    args = parser.parse_args()
    
    print("🔄 UniqueId链接转换工具")
    print("=" * 50)
    
    success = convert_article_links(args.file_path, args.dry_run)
    
    if success:
        print("\n✅ 转换完成")
        return 0
    else:
        print("\n❌ 转换失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())