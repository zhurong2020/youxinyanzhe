#!/usr/bin/env python
"""
测试微信草稿保存功能
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from scripts.content_pipeline import ContentPipeline

def test_wechat_draft():
    """测试微信草稿保存功能"""
    
    # 初始化内容管道
    pipeline = ContentPipeline("config/pipeline_config.yml", verbose=True)
    
    # 选择已发布的文章进行重新发布测试
    post_path = Path("_posts/2025-07-14-self-talk-unconscious-magic.md")
    
    if not post_path.exists():
        print(f"❌ 测试文件不存在: {post_path}")
        return False
    
    print(f"📄 测试文章: {post_path}")
    
    # 复制到草稿目录
    draft_path = pipeline.copy_post_to_draft(post_path)
    if not draft_path:
        print("❌ 复制文章到草稿失败")
        return False
    
    print(f"📝 草稿文件: {draft_path}")
    
    # 读取文章内容
    with open(draft_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔄 开始测试微信草稿保存...")
    
    # 直接测试微信发布功能
    success = pipeline._publish_to_wechat(content)
    
    if success:
        print("✅ 微信草稿保存测试成功！")
        print("📱 请登录微信公众号后台查看草稿箱")
    else:
        print("❌ 微信草稿保存测试失败")
    
    return success

if __name__ == "__main__":
    test_wechat_draft()