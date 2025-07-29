#!/usr/bin/env python3
"""
重新生成YouTube学习文章
使用修复后的Gemini Flash模型
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from scripts.core.youtube_podcast_generator import YouTubePodcastGenerator

# 加载环境变量
load_dotenv()

def main():
    print("🔄 重新生成YouTube学习文章...")
    
    # 配置
    config = {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'YOUTUBE_API_KEY': os.getenv('YOUTUBE_API_KEY')
    }
    
    if not config['GEMINI_API_KEY']:
        print("❌ 需要配置GEMINI_API_KEY")
        return
    
    # 创建生成器
    generator = YouTubePodcastGenerator(config)
    
    # 生成YouTube学习文章
    youtube_url = "https://www.youtube.com/watch?v=YqDehngsBHw"
    
    print(f"📺 处理视频: {youtube_url}")
    print("⏳ 正在生成内容（使用Gemini Flash模型）...")
    
    result = generator.generate_from_youtube(
        youtube_url=youtube_url,
        tts_model="edge",
        target_language="zh-CN",
        conversation_style="casual,informative"
    )
    
    if result['status'] == 'success':
        print("\n✅ 文章生成成功！")
        print(f"📄 文章路径: {result['article_path']}")
        print(f"🎵 音频路径: {result.get('audio_path', 'N/A')}")
        print(f"🖼️ 缩略图路径: {result.get('thumbnail_path', 'N/A')}")
        print(f"📰 文章标题: {result['article_title']}")
        
        # 检查生成的文件
        if os.path.exists(result['article_path']):
            with open(result['article_path'], 'r', encoding='utf-8') as f:
                content = f.read()
                # 检查是否还是模板内容
                if "关键词汇1" in content or "常用表达1" in content:
                    print("⚠️ 警告：文章仍包含模板内容")
                else:
                    print("✅ 文章内容已正确生成")
    else:
        print(f"❌ 生成失败: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()