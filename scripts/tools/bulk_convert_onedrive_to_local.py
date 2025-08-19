#!/usr/bin/env python3
"""
批量将OneDrive链接转换回本地路径工具
Bulk convert OneDrive links back to local paths

将文章中的OneDrive链接替换回对应的本地图片路径，以便重新处理
"""

import re
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple


def load_onedrive_index() -> Dict:
    """加载OneDrive图片索引"""
    index_path = Path("_data/onedrive_image_index.json")
    if index_path.exists():
        with open(index_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def find_onedrive_links(content: str) -> List[str]:
    """查找文章中的OneDrive链接"""
    patterns = [
        r'https://[^"\s]+sharepoint\.com[^"\s]*/_layouts/15/download\.aspx\?UniqueId=[A-Z0-9]+',
        r'https://[^"\s]+sharepoint\.com[^"\s]*/_layouts/15/download\.aspx\?share=[A-Za-z0-9_-]+',
        r'https://[^"\s]+sharepoint\.com[^"\s]*/:i:/g/personal/[^"\s]+',
    ]
    
    all_links = []
    for pattern in patterns:
        all_links.extend(re.findall(pattern, content))
    
    return list(set(all_links))  # 去重


def find_local_path_for_onedrive_link(onedrive_link: str, onedrive_index: Dict, article_file: str) -> str:
    """根据OneDrive链接查找对应的本地路径"""
    article_name = Path(article_file).stem
    
    # 方法1: 在索引中查找完全匹配的链接
    for record_id, record in onedrive_index.items():
        if 'embed_url' in record and record['embed_url'] == onedrive_link:
            if 'local_path' in record:
                return record['local_path']
        if 'onedrive_url' in record and record['onedrive_url'] == onedrive_link:
            if 'local_path' in record:
                return record['local_path']
    
    # 方法2: 基于文章名称和图片序号的模式匹配
    # 提取OneDrive文件名中的信息
    if 'BlogImages' in onedrive_link:
        # 尝试从OneDrive路径推断本地路径
        # 例如：BlogImages/2025/08/20250818_投资马斯克帝国_01.png
        for record_id, record in onedrive_index.items():
            if 'article_file' in record and article_name in record['article_file']:
                if 'local_path' in record:
                    # 根据图片在文章中的出现顺序推断
                    local_path = record['local_path']
                    # 检查本地文件是否存在
                    if Path(local_path).exists():
                        return local_path
    
    # 方法3: 基于常见的图片命名模式推断
    common_patterns = [
        "temp/drafting/images/fiveinvestmentpathways.png",
        "temp/drafting/images/tesila-shengtaiquanjing.png", 
        "temp/drafting/images/portfolioallocation02.png",
        "temp/drafting/images/tesila-shengtaiquanjing2.png",
        "temp/drafting/images/2600goal02.png",
        "temp/drafting/images/converging.png",
        "temp/drafting/images/etfinstruments02.png",
        "temp/drafting/images/qiquantesla20250818.png",
        "temp/drafting/images/californiagoldrush02.png",
        "temp/drafting/images/tesilashangxiayou.png",
        "temp/drafting/images/vip2-03.png",
        "temp/drafting/images/TESILAETF.png",
        "temp/drafting/images/tesilachangqijiazhizuhe.png",
        "temp/drafting/images/muskscosmicventures.png",
        "temp/drafting/images/marscolonizationscene.png",
        "temp/drafting/images/financialplanningdiagram.png",
        "temp/drafting/images/journeytofinancialfreedom02.png",
        "temp/drafting/images/digitalchecklist02.png"
    ]
    
    # 基于文章中OneDrive链接的出现顺序返回对应的本地路径
    # 这是一个简单的映射，基于我们知道的图片顺序
    return None


def convert_article_links(file_path: str, dry_run: bool = False) -> bool:
    """转换文章中的OneDrive链接回本地路径"""
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
    
    # 查找OneDrive链接
    onedrive_links = find_onedrive_links(content)
    print(f"🔍 发现 {len(onedrive_links)} 个OneDrive链接")
    
    if not onedrive_links:
        print("✅ 未发现需要转换的链接")
        return True
    
    # 使用预定义的映射进行批量替换
    # 这是基于我们知道的特斯拉文章图片顺序
    predefined_mappings = {
        # 这些是我们知道的图片本地路径，按在文章中出现的顺序
        0: "temp/drafting/images/fiveinvestmentpathways.png",  # 已处理
        1: "temp/drafting/images/tesila-shengtaiquanjing.png",
        2: "temp/drafting/images/portfolioallocation02.png", 
        3: "temp/drafting/images/tesila-shengtaiquanjing2.png",
        4: "temp/drafting/images/2600goal02.png",
        5: "temp/drafting/images/converging.png",
        6: "temp/drafting/images/2600goal02.png",  # 重复使用
        7: "temp/drafting/images/etfinstruments02.png",
        8: "temp/drafting/images/qiquantesla20250818.png",
        9: "temp/drafting/images/californiagoldrush02.png",
        10: "temp/drafting/images/tesilashangxiayou.png",
        11: "temp/drafting/images/vip2-03.png",
        12: "temp/drafting/images/TESILAETF.png",
        13: "temp/drafting/images/tesilachangqijiazhizuhe.png",
        14: "temp/drafting/images/muskscosmicventures.png",
        15: "temp/drafting/images/marscolonizationscene.png",
        16: "temp/drafting/images/financialplanningdiagram.png",
        17: "temp/drafting/images/journeytofinancialfreedom02.png",
        18: "temp/drafting/images/digitalchecklist02.png"
    }
    
    # 替换链接
    updated_content = content
    conversion_count = 0
    
    # 找到所有OneDrive链接的位置，按顺序替换
    unique_links = []
    for link in onedrive_links:
        if link not in unique_links:
            unique_links.append(link)
    
    for i, onedrive_link in enumerate(unique_links):
        if i in predefined_mappings:
            local_path = predefined_mappings[i]
            print(f"\n🔄 替换链接 {i+1}: {onedrive_link[:80]}...")
            print(f"   → {local_path}")
            
            # 检查本地文件是否存在
            if Path(local_path).exists():
                updated_content = updated_content.replace(onedrive_link, local_path)
                conversion_count += 1
                print(f"✅ 替换成功")
            else:
                print(f"⚠️  本地文件不存在: {local_path}")
        else:
            print(f"\n⚠️  无映射: {onedrive_link[:80]}...")
    
    # 显示转换结果
    print(f"\n📊 转换结果:")
    print(f"   处理链接: {len(unique_links)} 个")
    print(f"   成功转换: {conversion_count} 个")
    print(f"   保持原样: {len(unique_links) - conversion_count} 个")
    
    if dry_run:
        print("🔍 演练模式 - 未实际修改文件")
        return True
    
    if conversion_count > 0:
        # 备份原文件
        backup_path = f"{file_path}.backup.{Path().cwd().name}"
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
    
    parser = argparse.ArgumentParser(description='批量将OneDrive链接转换回本地路径')
    parser.add_argument('file_path', help='要处理的文章文件路径')
    parser.add_argument('--dry-run', action='store_true', help='演练模式，不实际修改文件')
    
    args = parser.parse_args()
    
    print("🔄 OneDrive链接批量转换工具")
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