#!/usr/bin/env python3
"""
YouTube链接映射管理器
用于记录和管理本地音频文件与YouTube链接的映射关系
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class YouTubeLinkMapper:
    """YouTube链接映射管理器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent  # 从 scripts/utils/ 往上3层到项目根目录
        self.mapping_file = self.project_root / ".tmp" / "youtube_mappings.json"
        self.mapping_file.parent.mkdir(exist_ok=True)
        self._load_mappings()
    
    def _load_mappings(self) -> None:
        """加载映射文件"""
        try:
            if self.mapping_file.exists():
                with open(self.mapping_file, 'r', encoding='utf-8') as f:
                    self.mappings = json.load(f)
            else:
                self.mappings = {}
        except Exception as e:
            print(f"⚠️ 加载映射文件失败: {e}")
            self.mappings = {}
    
    def _save_mappings(self) -> None:
        """保存映射文件"""
        try:
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.mappings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ 保存映射文件失败: {e}")
    
    def add_mapping(self, local_file_path: str, video_id: str, title: str = "") -> bool:
        """
        添加映射关系
        
        Args:
            local_file_path: 本地文件路径（相对于项目根目录）
            video_id: YouTube视频ID
            title: 视频标题（可选）
        
        Returns:
            bool: 是否成功添加
        """
        try:
            # 规范化路径（相对于项目根目录）
            if local_file_path.startswith('/'):
                # 绝对路径，转换为相对路径
                local_path = Path(local_file_path)
                if local_path.is_absolute():
                    try:
                        relative_path = str(local_path.relative_to(self.project_root))
                    except ValueError:
                        # 路径不在项目目录内，使用原路径
                        relative_path = local_file_path
                else:
                    relative_path = local_file_path
            else:
                relative_path = local_file_path
            
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            
            mapping_info = {
                "video_id": video_id,
                "youtube_url": youtube_url,
                "embed_url": embed_url,
                "title": title,
                "upload_time": datetime.now().isoformat(),
                "local_file": relative_path
            }
            
            self.mappings[relative_path] = mapping_info
            self._save_mappings()
            
            print(f"✅ 已添加映射: {relative_path} -> {youtube_url}")
            return True
            
        except Exception as e:
            print(f"❌ 添加映射失败: {e}")
            return False
    
    def get_youtube_url(self, local_file_path: str) -> Optional[str]:
        """
        获取YouTube链接
        
        Args:
            local_file_path: 本地文件路径
        
        Returns:
            Optional[str]: YouTube链接，如果没有找到返回None
        """
        # 规范化路径
        if local_file_path.startswith('/'):
            local_path = Path(local_file_path)
            if local_path.is_absolute():
                try:
                    relative_path = str(local_path.relative_to(self.project_root))
                except ValueError:
                    relative_path = local_file_path
            else:
                relative_path = local_file_path
        else:
            relative_path = local_file_path
        
        mapping = self.mappings.get(relative_path)
        return mapping["youtube_url"] if mapping else None
    
    def get_embed_url(self, local_file_path: str) -> Optional[str]:
        """
        获取YouTube嵌入链接
        
        Args:
            local_file_path: 本地文件路径
        
        Returns:
            Optional[str]: YouTube嵌入链接，如果没有找到返回None
        """
        # 规范化路径
        if local_file_path.startswith('/'):
            local_path = Path(local_file_path)
            if local_path.is_absolute():
                try:
                    relative_path = str(local_path.relative_to(self.project_root))
                except ValueError:
                    relative_path = local_file_path
            else:
                relative_path = local_file_path
        else:
            relative_path = local_file_path
        
        mapping = self.mappings.get(relative_path)
        return mapping["embed_url"] if mapping else None
    
    def get_mapping_info(self, local_file_path: str) -> Optional[Dict[str, Any]]:
        """
        获取完整映射信息
        
        Args:
            local_file_path: 本地文件路径
        
        Returns:
            Optional[Dict]: 映射信息，如果没有找到返回None
        """
        # 规范化路径
        if local_file_path.startswith('/'):
            local_path = Path(local_file_path)
            if local_path.is_absolute():
                try:
                    relative_path = str(local_path.relative_to(self.project_root))
                except ValueError:
                    relative_path = local_file_path
            else:
                relative_path = local_file_path
        else:
            relative_path = local_file_path
        
        return self.mappings.get(relative_path)
    
    def list_all_mappings(self) -> Dict[str, Dict[str, Any]]:
        """列出所有映射"""
        return self.mappings.copy()
    
    def remove_mapping(self, local_file_path: str) -> bool:
        """
        删除映射
        
        Args:
            local_file_path: 本地文件路径
        
        Returns:
            bool: 是否成功删除
        """
        try:
            # 规范化路径
            if local_file_path.startswith('/'):
                local_path = Path(local_file_path)
                if local_path.is_absolute():
                    try:
                        relative_path = str(local_path.relative_to(self.project_root))
                    except ValueError:
                        relative_path = local_file_path
                else:
                    relative_path = local_file_path
            else:
                relative_path = local_file_path
            
            if relative_path in self.mappings:
                del self.mappings[relative_path]
                self._save_mappings()
                print(f"✅ 已删除映射: {relative_path}")
                return True
            else:
                print(f"⚠️ 未找到映射: {relative_path}")
                return False
                
        except Exception as e:
            print(f"❌ 删除映射失败: {e}")
            return False


def main():
    """测试和管理映射的命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="YouTube链接映射管理器")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 添加映射
    add_parser = subparsers.add_parser('add', help='添加映射')
    add_parser.add_argument('local_file', help='本地文件路径')
    add_parser.add_argument('video_id', help='YouTube视频ID')
    add_parser.add_argument('--title', help='视频标题')
    
    # 查询映射
    get_parser = subparsers.add_parser('get', help='查询映射')
    get_parser.add_argument('local_file', help='本地文件路径')
    
    # 列出所有映射
    subparsers.add_parser('list', help='列出所有映射')
    
    # 删除映射
    remove_parser = subparsers.add_parser('remove', help='删除映射')
    remove_parser.add_argument('local_file', help='本地文件路径')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    mapper = YouTubeLinkMapper()
    
    if args.command == 'add':
        success = mapper.add_mapping(args.local_file, args.video_id, args.title or "")
        if success:
            print("✅ 映射添加成功")
        else:
            print("❌ 映射添加失败")
    
    elif args.command == 'get':
        info = mapper.get_mapping_info(args.local_file)
        if info:
            print(f"📁 本地文件: {args.local_file}")
            print(f"🎬 YouTube链接: {info['youtube_url']}")
            print(f"📺 嵌入链接: {info['embed_url']}")
            print(f"📝 标题: {info['title']}")
            print(f"📅 上传时间: {info['upload_time']}")
        else:
            print(f"❌ 未找到映射: {args.local_file}")
    
    elif args.command == 'list':
        mappings = mapper.list_all_mappings()
        if mappings:
            print(f"📋 共找到 {len(mappings)} 个映射:")
            for local_file, info in mappings.items():
                print(f"  📁 {local_file} -> 🎬 {info['youtube_url']}")
        else:
            print("📋 暂无映射记录")
    
    elif args.command == 'remove':
        success = mapper.remove_mapping(args.local_file)
        if success:
            print("✅ 映射删除成功")
        else:
            print("❌ 映射删除失败")


if __name__ == "__main__":
    main()