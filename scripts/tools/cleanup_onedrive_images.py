#!/usr/bin/env python3
"""
OneDrive图片清理工具
安全地清理OneDrive图片文件和本地索引记录
包含备份功能和多重确认
"""

import json
import shutil
import requests
from pathlib import Path
from typing import Dict, Optional
import argparse
from datetime import datetime

# 导入OneDrive组件
try:
    from onedrive_blog_images import OneDriveAuthManager, OneDriveUploadManager
except ImportError:
    OneDriveAuthManager = None
    OneDriveUploadManager = None


class OneDriveCleanupManager:
    """OneDrive图片清理管理器"""
    
    def __init__(self, config_path: str = "config/onedrive_config.json"):
        self.config_path = Path(config_path)
        self.index_path = Path("_data/onedrive_image_index.json")
        self.backup_dir = Path("backup/onedrive_images")
        
        # 加载配置和索引
        self.config = self._load_config()
        self.index_data = self._load_index()
        
        # 初始化OneDrive组件
        if OneDriveAuthManager is not None and OneDriveUploadManager is not None and self.config:
            try:
                self.auth = OneDriveAuthManager(self.config)
                self.uploader = OneDriveUploadManager(self.auth, self.config)
            except Exception as e:
                print(f"⚠️  OneDrive认证失败: {e}")
                self.auth = None
                self.uploader = None
        else:
            self.auth = None
            self.uploader = None
    
    def _load_config(self) -> Optional[Dict]:
        """加载OneDrive配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  无法加载OneDrive配置: {e}")
            return None
    
    def _load_index(self) -> Dict:
        """加载图片索引"""
        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  无法加载图片索引: {e}")
            return {}
    
    def analyze_cleanup_scope(self, article_file: Optional[str] = None) -> Dict:
        """分析清理范围"""
        if not self.index_data:
            return {'success': False, 'error': 'No index data available'}
        
        # 过滤要清理的记录
        if article_file:
            records = {record_id: v for record_id, v in self.index_data.items() 
                      if v.get('article_file') == article_file}
            scope = f"文章 '{article_file}'"
        else:
            records = self.index_data
            scope = "所有记录"
        
        # 统计信息
        total_records = len(records)
        total_size = sum(record.get('file_size', 0) for record in records.values())
        
        # 检查本地文件状态
        local_missing = 0
        local_exists = 0
        
        for record in records.values():
            local_path = record.get('local_path', '')
            if local_path:
                # 尝试多种可能的本地路径
                possible_paths = [
                    Path(local_path),
                    Path(local_path.replace('_drafts/../', '')),
                    Path(local_path.replace('../', ''))
                ]
                
                if any(p.exists() for p in possible_paths):
                    local_exists += 1
                else:
                    local_missing += 1
        
        return {
            'success': True,
            'scope': scope,
            'total_records': total_records,
            'total_size_mb': total_size / (1024 * 1024),
            'local_exists': local_exists,
            'local_missing': local_missing,
            'records': records
        }
    
    def backup_images_from_onedrive(self, records: Dict, backup_dir: Optional[Path] = None) -> Dict:
        """从OneDrive下载图片备份"""
        if not self.uploader:
            return {'success': False, 'error': 'OneDrive uploader not available'}
        
        backup_path = backup_dir or self.backup_dir
        backup_path.mkdir(parents=True, exist_ok=True)
        
        print(f"📥 开始从OneDrive下载备份到: {backup_path}")
        
        downloaded = 0
        failed = 0
        
        for record_id, record in records.items():
            try:
                onedrive_url = record.get('onedrive_url', '')
                filename = record.get('filename', f"{record_id}.unknown")
                local_backup_path = backup_path / filename
                
                # 如果备份已存在，跳过
                if local_backup_path.exists():
                    print(f"⏭️  跳过已存在: {filename}")
                    continue
                
                print(f"📥 下载: {filename}")
                
                # 从OneDrive下载文件
                response = requests.get(onedrive_url, stream=True)
                response.raise_for_status()
                
                with open(local_backup_path, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
                
                downloaded += 1
                print(f"✅ 完成: {filename}")
                
            except Exception as e:
                failed += 1
                print(f"❌ 下载失败 {filename}: {e}")
        
        return {
            'success': True,
            'downloaded': downloaded,
            'failed': failed,
            'backup_path': str(backup_path)
        }
    
    def delete_from_onedrive(self, records: Dict, dry_run: bool = True) -> Dict:
        """从OneDrive删除文件"""
        if not self.uploader:
            return {'success': False, 'error': 'OneDrive uploader not available'}
        
        print(f"🗑️  {'演练模式' if dry_run else '实际执行'}: 删除OneDrive文件")
        
        deleted = 0
        failed = 0
        
        for record_id, record in records.items():
            try:
                file_id = record.get('onedrive_file_id', '')
                filename = record.get('filename', record_id)
                
                if not file_id:
                    print(f"⏭️  跳过(无文件ID): {filename}")
                    continue
                
                print(f"🗑️  {'[演练]' if dry_run else ''}删除: {filename}")
                
                if not dry_run:
                    # 执行删除
                    response = self.uploader._make_request('DELETE', f"/me/drive/items/{file_id}")
                    if response.status_code in [204, 404]:  # 204=删除成功, 404=已不存在
                        deleted += 1
                        print(f"✅ 删除成功: {filename}")
                    else:
                        failed += 1
                        print(f"❌ 删除失败 {filename}: {response.text}")
                else:
                    deleted += 1
                
            except Exception as e:
                failed += 1
                print(f"❌ 删除出错 {filename}: {e}")
        
        return {
            'success': True,
            'deleted': deleted,
            'failed': failed
        }
    
    def cleanup_index_records(self, records: Dict, dry_run: bool = True) -> Dict:
        """清理本地索引记录"""
        if dry_run:
            print(f"🗑️  [演练] 将清理 {len(records)} 条索引记录")
            return {'success': True, 'cleaned': len(records)}
        
        print(f"🗑️  清理 {len(records)} 条索引记录")
        
        # 创建备份
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.index_path.parent / f"onedrive_image_index_backup_{timestamp}.json"
        
        shutil.copy2(self.index_path, backup_file)
        print(f"💾 索引备份已保存: {backup_file}")
        
        # 移除指定记录
        for record_id in records.keys():
            if record_id in self.index_data:
                del self.index_data[record_id]
        
        # 写回索引文件
        with open(self.index_path, 'w', encoding='utf-8') as f:
            json.dump(self.index_data, f, indent=2, ensure_ascii=False)
        
        return {'success': True, 'cleaned': len(records), 'backup_file': str(backup_file)}
    
    def interactive_cleanup(self, article_file: Optional[str] = None):
        """交互式清理流程"""
        print("🧹 OneDrive图片清理工具")
        print("="*50)
        
        # 分析清理范围
        analysis = self.analyze_cleanup_scope(article_file)
        if not analysis['success']:
            print(f"❌ 分析失败: {analysis['error']}")
            return
        
        print(f"📊 清理范围: {analysis['scope']}")
        print(f"📝 记录数量: {analysis['total_records']}")
        print(f"💾 总大小: {analysis['total_size_mb']:.1f}MB")
        print(f"📁 本地存在: {analysis['local_exists']}")
        print(f"❌ 本地缺失: {analysis['local_missing']}")
        
        if analysis['total_records'] == 0:
            print("ℹ️  没有需要清理的记录")
            return
        
        # 确认是否继续
        if not self._confirm("是否继续清理流程？"):
            print("❌ 用户取消")
            return
        
        records = analysis['records']
        
        # 步骤1：备份下载
        if analysis['local_missing'] > 0:
            print(f"\n⚠️  检测到 {analysis['local_missing']} 个图片本地文件缺失")
            if self._confirm("是否先从OneDrive下载备份？"):
                backup_result = self.backup_images_from_onedrive(records)
                if backup_result['success']:
                    print(f"✅ 备份完成: {backup_result['downloaded']} 成功, {backup_result['failed']} 失败")
                else:
                    print(f"❌ 备份失败: {backup_result['error']}")
                    if not self._confirm("备份失败，是否继续清理？"):
                        return
        
        # 步骤2：清理选择
        print(f"\n🗑️  清理选项:")
        print("1. 仅清理本地索引记录")
        print("2. 清理OneDrive文件 + 本地索引记录")
        print("0. 取消清理")
        
        choice = input("请选择清理方式 (0-2): ").strip()
        
        if choice == "0":
            print("❌ 用户取消")
            return
        elif choice == "1":
            cleanup_onedrive = False
        elif choice == "2":
            cleanup_onedrive = True
        else:
            print("❌ 无效选择")
            return
        
        # 最终确认
        print(f"\n⚠️  最终确认:")
        print(f"   范围: {analysis['scope']}")
        print(f"   OneDrive文件: {'删除' if cleanup_onedrive else '保留'}")
        print(f"   本地索引: 清理")
        
        if not self._confirm("确认执行清理？"):
            print("❌ 用户取消")
            return
        
        # 执行清理
        if cleanup_onedrive:
            print(f"\n🗑️  清理OneDrive文件...")
            delete_result = self.delete_from_onedrive(records, dry_run=False)
            if delete_result['success']:
                print(f"✅ OneDrive清理完成: {delete_result['deleted']} 成功, {delete_result['failed']} 失败")
            else:
                print(f"❌ OneDrive清理失败: {delete_result['error']}")
        
        print(f"\n🗑️  清理本地索引记录...")
        index_result = self.cleanup_index_records(records, dry_run=False)
        if index_result['success']:
            print(f"✅ 索引清理完成: {index_result['cleaned']} 条记录")
            print(f"💾 备份文件: {index_result.get('backup_file', 'N/A')}")
        
        print(f"\n🎉 清理流程完成！")
    
    def _confirm(self, message: str) -> bool:
        """确认对话"""
        response = input(f"{message} (y/N): ").strip().lower()
        return response in ['y', 'yes', '是', '确定']


def main():
    parser = argparse.ArgumentParser(description="OneDrive图片清理工具")
    parser.add_argument("--article", help="仅清理指定文章的图片")
    parser.add_argument("--config", default="config/onedrive_config.json", help="OneDrive配置文件路径")
    
    args = parser.parse_args()
    
    # 创建清理管理器
    cleanup_manager = OneDriveCleanupManager(args.config)
    
    # 启动交互式清理
    cleanup_manager.interactive_cleanup(args.article)


if __name__ == "__main__":
    main()