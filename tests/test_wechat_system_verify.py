#!/usr/bin/env python3
"""
验证微信发布系统是否正常工作
"""

import os
from pathlib import Path
import json
from datetime import datetime

def check_system_status():
    """检查系统状态"""
    print("🔍 检查微信发布系统状态...")
    
    # 检查输出目录
    output_dir = Path("_output")
    guides_dir = output_dir / "wechat_guides"
    previews_dir = output_dir / "wechat_previews"
    
    print(f"📁 输出目录: {output_dir.exists()}")
    print(f"📋 指导文件目录: {guides_dir.exists()}")
    print(f"📱 预览文件目录: {previews_dir.exists()}")
    
    # 列出最新的文件
    if guides_dir.exists():
        guide_files = list(guides_dir.glob("*.md"))
        html_files = list(guides_dir.glob("*.html"))
        
        print(f"\n📋 指导文件 ({len(guide_files)} 个):")
        for f in sorted(guide_files)[-5:]:  # 显示最新5个
            print(f"  - {f.name}")
        
        print(f"\n📄 HTML文件 ({len(html_files)} 个):")
        for f in sorted(html_files)[-5:]:  # 显示最新5个
            print(f"  - {f.name}")
    
    # 检查图片缓存
    cache_file = output_dir / "wechat_image_cache" / "image_cache.json"
    if cache_file.exists():
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            print(f"\n📸 图片缓存: {len(cache_data)} 个已上传的图片")
        except:
            print("\n📸 图片缓存: 无法读取缓存文件")
    else:
        print("\n📸 图片缓存: 尚未创建")

def show_latest_guide():
    """显示最新的发布指导"""
    guides_dir = Path("_output/wechat_guides")
    
    if not guides_dir.exists():
        print("❌ 指导文件目录不存在")
        return
    
    guide_files = list(guides_dir.glob("*_guide.md"))
    if not guide_files:
        print("❌ 没有找到指导文件")
        return
    
    # 获取最新的指导文件
    latest_guide = sorted(guide_files)[-1]
    
    print(f"\n📋 最新的发布指导文件: {latest_guide.name}")
    print("=" * 50)
    
    try:
        with open(latest_guide, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 只显示前面的部分，避免输出过长
        lines = content.split('\n')
        for i, line in enumerate(lines[:30]):  # 显示前30行
            print(line)
        
        if len(lines) > 30:
            print("... (更多内容请查看完整文件)")
            
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")

def show_usage_instructions():
    """显示使用说明"""
    print("\n" + "=" * 50)
    print("📖 微信发布系统使用说明")
    print("=" * 50)
    
    instructions = [
        "1. 系统当前工作模式：生成本地指导文件",
        "2. 微信后台不会自动出现草稿（API权限限制）",
        "3. 需要手动在微信公众平台创建文章",
        "",
        "📋 使用步骤：",
        "  a) 运行发布脚本: python run.py",
        "  b) 选择草稿和微信平台",
        "  c) 查看生成的指导文件: _output/wechat_guides/",
        "  d) 按照指导文件手动在微信后台创建文章",
        "",
        "🔗 微信公众平台地址：",
        "  - 登录：https://mp.weixin.qq.com/",
        "  - 素材管理：素材管理 → 新建图文素材",
        "",
        "💡 优势：",
        "  - 图片已自动上传到微信服务器",
        "  - HTML内容已针对手机优化",
        "  - 所有外部链接已移除",
        "  - 提供详细的操作指导"
    ]
    
    for instruction in instructions:
        print(instruction)

def main():
    print("🔧 微信发布系统验证工具")
    print("=" * 50)
    
    # 检查系统状态
    check_system_status()
    
    # 显示最新的指导文件
    show_latest_guide()
    
    # 显示使用说明
    show_usage_instructions()

if __name__ == "__main__":
    main()