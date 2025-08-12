#!/usr/bin/env python3
"""
上传图片管理工具
提供手动删除、查看、管理已上传图片的功能
"""

import json
import os
from pathlib import Path
import argparse
from typing import Dict, List

class UploadedImageManager:
    def __init__(self, backup_dir: str = "temp/image_processing"):
        self.backup_dir = Path(backup_dir)
        self.backup_index_file = self.backup_dir / "backup_index.json"
        self.backup_index = self.load_backup_index()
    
    def load_backup_index(self) -> Dict:
        """加载备份索引"""
        try:
            if self.backup_index_file.exists():
                with open(self.backup_index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"⚠️ 加载备份索引失败: {e}")
            return {}
    
    def save_backup_index(self) -> None:
        """保存备份索引"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            with open(self.backup_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.backup_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存备份索引失败: {e}")
    
    def list_uploaded_files(self) -> None:
        """列出所有已上传的文件"""
        print("\n📋 已上传文件列表:")
        print("=" * 80)
        
        if not self.backup_index:
            print("📂 暂无已上传的文件记录")
            return
        
        for backup_name, record in self.backup_index.items():
            original_path = record.get('original_path', '未知')
            backup_path = record.get('backup_path', '未知')
            remote_path = record.get('remote_path', '未知')
            backup_time = record.get('backup_time', '未知')
            
            backup_file = Path(backup_path)
            exists = "✅" if backup_file.exists() else "❌"
            size = f"{backup_file.stat().st_size / 1024:.1f}KB" if backup_file.exists() else "未知"
            
            print(f"\n📸 {backup_name}")
            print(f"   状态: {exists}")
            print(f"   原始路径: {original_path}")
            print(f"   项目备份: {backup_path}")
            print(f"   OneDrive: {remote_path}")
            print(f"   大小: {size}")
            print(f"   备份时间: {backup_time}")
    
    def clean_uploaded_files(self, confirm: bool = False) -> None:
        """清理已上传的文件"""
        if not self.backup_index:
            print("📂 暂无已上传的文件记录")
            return
        
        print(f"\n🧹 发现 {len(self.backup_index)} 个已上传的文件备份")
        
        if not confirm:
            response = input("是否要清理这些文件？此操作不可恢复！(y/N): ").strip().lower()
            if response != 'y':
                print("❌ 操作已取消")
                return
        
        deleted_count = 0
        failed_count = 0
        
        for backup_name, record in list(self.backup_index.items()):
            backup_path = Path(record.get('backup_path', ''))
            
            try:
                if backup_path.exists():
                    backup_path.unlink()
                    print(f"🗑️ 已删除: {backup_name}")
                    deleted_count += 1
                else:
                    print(f"⚠️ 文件不存在: {backup_name}")
                
                # 从索引中移除
                del self.backup_index[backup_name]
                
            except Exception as e:
                print(f"❌ 删除失败 {backup_name}: {e}")
                failed_count += 1
        
        # 保存更新后的索引
        self.save_backup_index()
        
        print(f"\n📊 清理结果:")
        print(f"✅ 成功删除: {deleted_count} 个文件")
        if failed_count > 0:
            print(f"❌ 删除失败: {failed_count} 个文件")
    
    def delete_specific_files(self, filenames: List[str]) -> None:
        """删除指定的文件"""
        deleted_count = 0
        failed_count = 0
        
        for filename in filenames:
            if filename in self.backup_index:
                record = self.backup_index[filename]
                backup_path = Path(record.get('backup_path', ''))
                
                try:
                    if backup_path.exists():
                        backup_path.unlink()
                        print(f"🗑️ 已删除: {filename}")
                        deleted_count += 1
                    else:
                        print(f"⚠️ 文件不存在: {filename}")
                    
                    # 从索引中移除
                    del self.backup_index[filename]
                    
                except Exception as e:
                    print(f"❌ 删除失败 {filename}: {e}")
                    failed_count += 1
            else:
                print(f"❌ 未找到文件: {filename}")
                failed_count += 1
        
        # 保存更新后的索引
        self.save_backup_index()
        
        print(f"\n📊 删除结果:")
        print(f"✅ 成功删除: {deleted_count} 个文件")
        if failed_count > 0:
            print(f"❌ 删除失败: {failed_count} 个文件")
    
    def get_storage_info(self) -> None:
        """获取存储信息"""
        total_size = 0
        total_files = 0
        existing_files = 0
        
        for backup_name, record in self.backup_index.items():
            backup_path = Path(record.get('backup_path', ''))
            total_files += 1
            
            if backup_path.exists():
                existing_files += 1
                total_size += backup_path.stat().st_size
        
        print(f"\n📊 存储信息:")
        print(f"总文件数: {total_files}")
        print(f"现存文件: {existing_files}")
        print(f"总大小: {total_size / 1024 / 1024:.2f} MB")
        print(f"备份目录: {self.backup_dir}")

def main():
    parser = argparse.ArgumentParser(description="上传图片管理工具")
    parser.add_argument('--list', '-l', action='store_true', help="列出已上传的文件")
    parser.add_argument('--clean', '-c', action='store_true', help="清理所有已上传的文件")
    parser.add_argument('--delete', '-d', nargs='+', help="删除指定的文件")
    parser.add_argument('--info', '-i', action='store_true', help="显示存储信息")
    parser.add_argument('--backup-dir', default="temp/image_processing", 
                       help="备份目录路径")
    parser.add_argument('--yes', '-y', action='store_true', help="跳过确认提示")
    
    args = parser.parse_args()
    
    manager = UploadedImageManager(args.backup_dir)
    
    if args.list:
        manager.list_uploaded_files()
    elif args.clean:
        manager.clean_uploaded_files(args.yes)
    elif args.delete:
        manager.delete_specific_files(args.delete)
    elif args.info:
        manager.get_storage_info()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()