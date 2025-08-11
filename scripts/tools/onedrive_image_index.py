#!/usr/bin/env python3
"""
OneDrive博客图片索引管理系统
提供图片上传记录、查询、管理和统计功能
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

@dataclass
class ImageRecord:
    """图片记录数据结构"""
    # 基本信息
    local_path: str                 # 本地原始路径
    onedrive_path: str             # OneDrive存储路径
    onedrive_url: str              # OneDrive分享链接
    embed_url: str                 # 嵌入式链接
    
    # 文章信息
    article_file: str              # 文章文件路径
    article_title: str             # 文章标题
    article_date: str              # 文章日期
    
    # 图片属性
    filename: str                  # 文件名
    file_size: int                 # 文件大小(字节)
    file_hash: str                 # MD5哈希值(去重)
    image_index: int               # 在文章中的图片序号
    
    # 上传信息
    upload_date: str               # 上传时间
    onedrive_file_id: str          # OneDrive文件ID
    processing_notes: Optional[str] = None  # 处理备注


class OneDriveImageIndex:
    """OneDrive图片索引管理器"""
    
    def __init__(self, index_file: str = "_data/onedrive_image_index.json"):
        self.index_file = Path(index_file)
        self.index_file.parent.mkdir(exist_ok=True, parents=True)
        self.records: Dict[str, ImageRecord] = {}
        self._load_index()
    
    def _load_index(self):
        """加载索引文件"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.records = {
                        key: ImageRecord(**record) 
                        for key, record in data.items()
                    }
                print(f"📖 加载了 {len(self.records)} 条图片记录")
            else:
                print("📝 创建新的图片索引文件")
        except Exception as e:
            print(f"⚠️ 索引文件加载失败: {e}")
            self.records = {}
    
    def _save_index(self):
        """保存索引文件"""
        try:
            data = {key: asdict(record) for key, record in self.records.items()}
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 已保存 {len(self.records)} 条图片记录")
        except Exception as e:
            print(f"❌ 索引文件保存失败: {e}")
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件MD5哈希值"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            print(f"⚠️ 文件哈希计算失败 {file_path}: {e}")
            return ""
    
    def add_record(self, 
                   local_path: str,
                   onedrive_path: str,
                   onedrive_url: str,
                   embed_url: str,
                   article_file: str,
                   article_title: str,
                   onedrive_file_id: str,
                   image_index: int = 1,
                   processing_notes: Optional[str] = None) -> str:
        """添加图片记录"""
        
        # 生成记录键值
        file_hash = self._calculate_file_hash(local_path)
        record_key = f"{Path(article_file).stem}_{image_index:02d}_{file_hash[:8]}"
        
        # 检查重复文件
        if self.is_duplicate_file(file_hash):
            existing = self.find_by_hash(file_hash)
            print(f"⚠️ 检测到重复文件: {existing.local_path}")
            return existing.embed_url
        
        # 获取文件信息
        local_file = Path(local_path)
        file_size = local_file.stat().st_size if local_file.exists() else 0
        
        # 提取文章日期
        article_date = self._extract_article_date(article_file)
        
        # 创建记录
        record = ImageRecord(
            local_path=local_path,
            onedrive_path=onedrive_path,
            onedrive_url=onedrive_url,
            embed_url=embed_url,
            article_file=article_file,
            article_title=article_title,
            article_date=article_date,
            filename=local_file.name,
            file_size=file_size,
            file_hash=file_hash,
            image_index=image_index,
            upload_date=datetime.now().isoformat(),
            onedrive_file_id=onedrive_file_id,
            processing_notes=processing_notes
        )
        
        # 保存记录
        self.records[record_key] = record
        self._save_index()
        
        print(f"✅ 已添加图片记录: {record_key}")
        return embed_url
    
    def _extract_article_date(self, article_file: str) -> str:
        """从文章文件名提取日期"""
        try:
            filename = Path(article_file).name
            # 匹配 YYYY-MM-DD 格式
            import re
            match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
            return match.group(1) if match else datetime.now().strftime('%Y-%m-%d')
        except:
            return datetime.now().strftime('%Y-%m-%d')
    
    def is_duplicate_file(self, file_hash: str) -> bool:
        """检查是否为重复文件"""
        return any(record.file_hash == file_hash for record in self.records.values())
    
    def find_by_hash(self, file_hash: str) -> Optional[ImageRecord]:
        """根据哈希值查找记录"""
        for record in self.records.values():
            if record.file_hash == file_hash:
                return record
        return None
    
    def find_by_article(self, article_file: str) -> List[ImageRecord]:
        """查找文章相关的所有图片"""
        article_stem = Path(article_file).stem
        return [record for record in self.records.values() 
                if Path(record.article_file).stem == article_stem]
    
    def find_by_date_range(self, start_date: str, end_date: str) -> List[ImageRecord]:
        """查找日期范围内的图片"""
        results = []
        for record in self.records.values():
            if start_date <= record.article_date <= end_date:
                results.append(record)
        return sorted(results, key=lambda x: x.article_date)
    
    def get_statistics(self) -> Dict:
        """获取图片统计信息"""
        if not self.records:
            return {"total_images": 0, "total_size": 0, "total_articles": 0}
        
        total_size = sum(record.file_size for record in self.records.values())
        articles = set(Path(record.article_file).stem for record in self.records.values())
        
        # 按月份统计
        monthly_stats = {}
        for record in self.records.values():
            month = record.article_date[:7]  # YYYY-MM
            if month not in monthly_stats:
                monthly_stats[month] = {"count": 0, "size": 0}
            monthly_stats[month]["count"] += 1
            monthly_stats[month]["size"] += record.file_size
        
        return {
            "total_images": len(self.records),
            "total_size": total_size,
            "total_size_mb": round(total_size / (1024*1024), 2),
            "total_articles": len(articles),
            "monthly_stats": monthly_stats,
            "average_size_per_image": round(total_size / len(self.records) / 1024, 2) if self.records else 0,
            "latest_upload": max(record.upload_date for record in self.records.values()) if self.records else None
        }
    
    def generate_report(self) -> str:
        """生成详细报告"""
        stats = self.get_statistics()
        
        report = [
            "📊 OneDrive博客图片索引报告",
            "=" * 50,
            "",
            "📈 总体统计:",
            f"  • 图片总数: {stats['total_images']} 张",
            f"  • 存储空间: {stats['total_size_mb']} MB",
            f"  • 涉及文章: {stats['total_articles']} 篇",
            f"  • 平均图片大小: {stats['average_size_per_image']} KB",
            f"  • 最近上传: {stats['latest_upload'][:19] if stats['latest_upload'] else 'N/A'}",
            "",
            "📅 按月份统计:",
        ]
        
        for month, data in sorted(stats['monthly_stats'].items(), reverse=True):
            size_mb = round(data['size'] / (1024*1024), 2)
            report.append(f"  • {month}: {data['count']} 张图片, {size_mb} MB")
        
        return "\n".join(report)
    
    def cleanup_missing_files(self) -> int:
        """清理本地文件已删除的记录"""
        to_remove = []
        for key, record in self.records.items():
            if not Path(record.local_path).exists():
                to_remove.append(key)
        
        for key in to_remove:
            del self.records[key]
        
        if to_remove:
            self._save_index()
            print(f"🧹 已清理 {len(to_remove)} 条无效记录")
        
        return len(to_remove)
    
    def export_urls_for_article(self, article_file: str) -> Dict[str, str]:
        """导出文章相关的所有图片URL映射"""
        records = self.find_by_article(article_file)
        return {
            record.local_path: record.embed_url 
            for record in sorted(records, key=lambda x: x.image_index)
        }


def main():
    """命令行工具"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OneDrive图片索引管理')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    parser.add_argument('--report', action='store_true', help='生成详细报告')
    parser.add_argument('--cleanup', action='store_true', help='清理无效记录')
    parser.add_argument('--article', help='查看指定文章的图片')
    parser.add_argument('--date-range', nargs=2, help='查看日期范围内的图片 (开始日期 结束日期)')
    
    args = parser.parse_args()
    
    # 创建索引管理器
    index = OneDriveImageIndex()
    
    if args.stats:
        stats = index.get_statistics()
        print(f"📊 总图片数: {stats['total_images']}")
        print(f"📦 总大小: {stats.get('total_size_mb', 0)} MB")
        print(f"📝 涉及文章: {stats['total_articles']} 篇")
    
    elif args.report:
        print(index.generate_report())
    
    elif args.cleanup:
        cleaned = index.cleanup_missing_files()
        print(f"✅ 清理完成，删除了 {cleaned} 条记录")
    
    elif args.article:
        records = index.find_by_article(args.article)
        if records:
            print(f"📖 文章 {args.article} 的图片:")
            for record in sorted(records, key=lambda x: x.image_index):
                print(f"  {record.image_index:02d}. {record.filename} -> {record.embed_url}")
        else:
            print(f"❌ 未找到文章 {args.article} 的图片记录")
    
    elif args.date_range:
        start_date, end_date = args.date_range
        records = index.find_by_date_range(start_date, end_date)
        print(f"📅 {start_date} 至 {end_date} 期间的图片:")
        for record in records:
            print(f"  {record.article_date} - {record.article_title} - {record.filename}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()