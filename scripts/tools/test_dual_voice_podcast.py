#!/usr/bin/env python3
"""
双人对话播客测试脚本
用于测试YouTube播客生成器的双人对话功能
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

# 加载环境变量
load_dotenv()

from scripts.core.youtube_podcast_generator import YouTubePodcastGenerator


def test_dual_voice_dialogue():
    """测试双人对话音频生成"""
    print("🎭 测试双人对话播客生成")
    print("=" * 50)
    
    # 配置
    config = {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'ELEVENLABS_API_KEY': os.getenv('ELEVENLABS_API_KEY'),
        'YOUTUBE_API_KEY': os.getenv('YOUTUBE_API_KEY')
    }
    
    if not config['ELEVENLABS_API_KEY']:
        print("❌ 请在.env文件中设置ELEVENLABS_API_KEY")
        return False
    
    # 创建生成器实例
    try:
        generator = YouTubePodcastGenerator(config)
        print("✅ YouTube播客生成器初始化成功")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False
    
    # 测试对话脚本
    test_script = """
[主播助手]: 大家好，欢迎收听今天的播客。我们今天要讨论的是特斯拉的最新技术发展。

[学习导师]: 是的，特斯拉在人工智能和自动驾驶方面确实取得了很大的进展。他们的FSD技术已经达到了一个新的里程碑。

[主播助手]: 这个技术对普通消费者意味着什么呢？我们是否很快就能体验到完全自动驾驶？

[学习导师]: 从技术角度来看，特斯拉的神经网络已经能够处理大部分驾驶场景。但是监管和安全考虑仍然是主要挑战。

[主播助手]: 那么投资者应该如何看待这些技术进展呢？

[学习导师]: 这些技术突破确实为特斯拉带来了长期竞争优势，但投资决策还需要考虑更多因素，比如市场竞争和监管环境。
"""
    
    # 输出文件路径
    output_path = "tests/dual_voice_test.wav"
    os.makedirs("tests", exist_ok=True)
    
    print("\n🎤 开始生成双人对话音频...")
    print(f"📝 测试脚本长度: {len(test_script)} 字符")
    
    # 生成音频
    try:
        success = generator.generate_local_audio(
            script=test_script,
            output_path=output_path,
            tts_engine="elevenlabs",
            dual_speaker=True
        )
        
        if success:
            print(f"✅ 双人对话音频生成成功!")
            print(f"🎧 音频文件: {output_path}")
            
            # 检查文件大小
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"📊 文件大小: {file_size / 1024:.1f} KB")
                
                if file_size > 1000:  # 至少1KB
                    print("✅ 音频文件大小正常")
                    return True
                else:
                    print("⚠️ 音频文件太小，可能生成失败")
                    return False
            else:
                print("❌ 音频文件未生成")
                return False
        else:
            print("❌ 双人对话音频生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False


def test_single_voice_fallback():
    """测试单人模式回退功能"""
    print("\n🎙️ 测试单人模式回退")
    print("-" * 30)
    
    config = {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'ELEVENLABS_API_KEY': os.getenv('ELEVENLABS_API_KEY'),
        'YOUTUBE_API_KEY': os.getenv('YOUTUBE_API_KEY')
    }
    
    generator = YouTubePodcastGenerator(config)
    
    # 没有对话格式的脚本
    single_script = """
    今天我们要讨论特斯拉的技术发展。特斯拉在人工智能领域取得了重大突破，
    他们的FSD技术已经能够处理复杂的驾驶场景。这对整个汽车行业都有重要影响。
    投资者需要关注这些技术进展对公司长期价值的影响。
    """
    
    output_path = "tests/single_voice_test.wav"
    
    try:
        success = generator.generate_local_audio(
            script=single_script,
            output_path=output_path,
            tts_engine="elevenlabs",
            dual_speaker=True  # 即使设置为True，也应该回退到单人模式
        )
        
        if success:
            print("✅ 单人模式回退成功")
            return True
        else:
            print("❌ 单人模式回退失败")
            return False
            
    except Exception as e:
        print(f"❌ 单人模式测试出错: {e}")
        return False


def main():
    """主函数"""
    print("🎙️ ElevenLabs双人对话播客测试")
    print("=" * 50)
    
    # 检查必要的依赖
    try:
        from elevenlabs import ElevenLabs
        print("✅ ElevenLabs库可用")
    except ImportError:
        print("❌ 请安装ElevenLabs: pip install elevenlabs")
        return
    
    try:
        from pydub import AudioSegment
        print("✅ Pydub库可用")
    except ImportError:
        print("❌ 请安装pydub: pip install pydub")
        return
    
    # 运行测试
    results = []
    
    print("\n" + "="*50)
    results.append(test_dual_voice_dialogue())
    
    print("\n" + "="*50)  
    results.append(test_single_voice_fallback())
    
    # 测试结果统计
    print("\n" + "="*50)
    print("📊 测试结果统计:")
    print(f"✅ 成功: {sum(results)} / {len(results)}")
    print(f"❌ 失败: {len(results) - sum(results)} / {len(results)}")
    
    if all(results):
        print("\n🎉 所有测试通过！双人对话功能工作正常")
    else:
        print(f"\n⚠️ 部分测试失败，请检查配置和依赖")


if __name__ == "__main__":
    main()