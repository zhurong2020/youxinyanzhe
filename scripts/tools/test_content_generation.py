#!/usr/bin/env python3
"""
测试内容生成功能
"""
import os
import sys
import json
import re
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import google.generativeai as genai

# 加载环境变量
load_dotenv()

def test_content_guide_generation():
    """测试内容导读生成"""
    print("🧪 测试内容导读生成...")
    
    # 设置API
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 模拟视频信息
    video_info = {
        'title': 'Elon Musk Interview | The Future, Engineered | X Takeover 2025',
        'description': 'Deep dive interview with Elon Musk covering AI, space exploration, and the future of technology.',
        'channel_title': 'Tesla Owners Silicon Valley',
        'duration': '1小时17分钟10秒'
    }
    
    prompt = f"""
请为以下英文YouTube视频生成一篇中文导读文章，用于英语学习：

视频标题: {video_info['title']}
视频描述: {video_info['description']}
频道: {video_info['channel_title']}
时长: {video_info['duration']}

请生成以下内容：
1. 25-35字符的中文标题（前缀：【英语学习】）
2. 50-60字的文章摘要
3. 4-5个要点的内容大纲
4. 英语学习建议（关键词汇、表达方式、文化背景）
5. 3-5个相关标签

要求：
- 强调全球视野和学习价值
- 内容要吸引中文读者
- 突出英语学习的实用性
- 保持客观和专业的语调

请以JSON格式返回，包含以下字段：
- title: 文章标题
- excerpt: 文章摘要  
- outline: 内容大纲（数组）
- learning_tips: 学习建议对象，包含vocabulary、expressions、cultural_context
- tags: 标签数组
- difficulty_level: 难度级别（初级/中级/高级）
"""
    
    try:
        response = model.generate_content(prompt)
        content_text = response.text
        print(f"✅ API调用成功，响应长度: {len(content_text)}")
        print(f"📄 原始响应:\n{content_text[:500]}...\n")
        
        # 提取JSON内容
        json_match = re.search(r'\{.*\}', content_text, re.DOTALL)
        if json_match:
            content_data = json.loads(json_match.group())
            print("✅ JSON解析成功")
            print("📋 生成的内容:")
            print(f"标题: {content_data.get('title', 'N/A')}")
            print(f"摘要: {content_data.get('excerpt', 'N/A')}")
            print(f"大纲数量: {len(content_data.get('outline', []))}")
            print(f"标签: {content_data.get('tags', [])}")
            print(f"难度: {content_data.get('difficulty_level', 'N/A')}")
            return True
        else:
            print("❌ 无法从响应中提取JSON内容")
            return False
            
    except Exception as e:
        print(f"❌ 内容生成失败: {e}")
        return False

def test_podcast_script_generation():
    """测试播客脚本生成"""
    print("\n🎧 测试播客脚本生成...")
    
    # 设置API
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 模拟视频信息
    video_info = {
        'title': 'Elon Musk Interview | The Future, Engineered | X Takeover 2025',
        'description': 'Deep dive interview with Elon Musk covering AI, space exploration, and the future of technology.',
        'channel_title': 'Tesla Owners Silicon Valley',
        'duration': '1小时17分钟10秒'
    }
    
    prompt = f"""
请为以下YouTube视频生成一个中文播客脚本，包含两个主播的对话：

视频标题: {video_info['title']}
视频描述: {video_info['description']}
频道: {video_info['channel_title']}
时长: {video_info['duration']}

要求：
1. 生成一个约5-8分钟的播客对话脚本
2. 两个角色：主播助手（负责介绍和总结）和学习导师（负责提问和解释）
3. 对话风格：casual,informative
4. 目标语言：zh-CN
5. 内容要适合英语学习者收听
6. 包含以下结构：
   - 开场白（30秒）
   - 内容总结（3-4分钟）
   - 学习要点（2-3分钟）
   - 结语（30秒）

请以以下格式输出：
[主播助手]: 对话内容
[学习导师]: 对话内容

确保对话自然流畅，信息丰富且具有教育价值。
"""
    
    try:
        response = model.generate_content(prompt)
        script = response.text
        print(f"✅ 脚本生成成功，长度: {len(script)} 字符")
        
        # 统计对话轮次
        dialogue_count = len(re.findall(r'\[.*?\]:', script))
        print(f"📊 对话轮次: {dialogue_count}")
        
        # 显示前几行
        lines = script.split('\n')[:10]
        print("📝 脚本预览:")
        for line in lines:
            if line.strip():
                print(f"  {line}")
        
        return len(script) > 500  # 判断是否生成了足够的内容
        
    except Exception as e:
        print(f"❌ 脚本生成失败: {e}")
        return False

def main():
    print("=" * 60)
    print("🧪 YouTube播客生成器内容测试")
    print("=" * 60)
    
    # 检查API密钥
    api_key = os.getenv('GEMINI_API_KEY')
    print(f"GEMINI_API_KEY: {'✅ 已配置' if api_key else '❌ 未配置'}")
    
    if not api_key:
        print("❌ 需要配置GEMINI_API_KEY")
        return
    
    # 测试内容生成
    guide_success = test_content_guide_generation()
    script_success = test_podcast_script_generation()
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"内容导读生成: {'✅ 成功' if guide_success else '❌ 失败'}")
    print(f"播客脚本生成: {'✅ 成功' if script_success else '❌ 失败'}")
    
    if guide_success and script_success:
        print("\n🎉 所有测试通过！内容生成功能正常")
        print("💡 现在可以重新运行YouTube播客生成器")
    else:
        print("\n⚠️ 部分测试失败，需要进一步调试")

if __name__ == "__main__":
    main()