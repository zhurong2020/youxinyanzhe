#!/usr/bin/env python3
"""
查看微信发布指南文件
"""
import os
import sys
from pathlib import Path
from datetime import datetime

def view_wechat_guides():
    """查看所有微信发布指南"""

    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent

    # 微信指南目录
    guide_dir = project_root / "tmp/output/wechat/guides"

    if not guide_dir.exists():
        print("❌ 微信指南目录不存在")
        print(f"   期望位置: {guide_dir}")
        return

    # 获取所有指南文件
    guide_files = list(guide_dir.glob("*.md"))

    if not guide_files:
        print("📄 暂无微信发布指南文件")
        return

    # 按修改时间排序
    guide_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    print("📱 微信发布指南列表")
    print("=" * 60)
    print(f"📂 目录: {guide_dir}")
    print(f"📊 共找到 {len(guide_files)} 个指南文件")
    print("-" * 60)

    for i, file in enumerate(guide_files, 1):
        # 获取文件信息
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        size = file.stat().st_size

        # 提取文章标题（从文件名）
        title = file.stem.replace("_guide", "")
        if "_2025" in title:
            parts = title.rsplit("_2025", 1)
            title = parts[0]

        print(f"\n{i}. {title}")
        print(f"   📄 文件: {file.name}")
        print(f"   📅 生成时间: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   📊 文件大小: {size:,} 字节")

    # 提供查看选项
    print("\n" + "=" * 60)
    print("💡 提示:")
    print("   - 查看文件: cat [文件路径]")
    print("   - 最新文件: " + str(guide_files[0]) if guide_files else "无")

    # 询问是否查看最新文件
    if guide_files:
        print("\n是否查看最新的指南文件？(y/N): ", end="")
        choice = input().strip().lower()

        if choice in ['y', 'yes']:
            print("\n" + "=" * 60)
            print("📄 最新指南内容（前50行）:")
            print("=" * 60)

            with open(guide_files[0], 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[:50]:
                    print(line, end='')

            if len(lines) > 50:
                print(f"\n... 还有 {len(lines) - 50} 行未显示")
                print(f"完整查看: cat {guide_files[0]}")

if __name__ == "__main__":
    view_wechat_guides()