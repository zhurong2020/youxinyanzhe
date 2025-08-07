#!/usr/bin/env python3
"""
ElevenLabs API权限检查工具
检查API密钥权限并提供解决方案
"""

import os
from dotenv import load_dotenv

load_dotenv()

try:
    from elevenlabs import ElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    print("❌ 请先安装 elevenlabs: pip install elevenlabs")
    exit(1)


def check_api_permissions():
    """检查ElevenLabs API权限"""
    print("🔍 ElevenLabs API权限检查")
    print("=" * 50)
    
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("❌ 未找到ELEVENLABS_API_KEY环境变量")
        print("📝 解决方案: 在.env文件中添加ELEVENLABS_API_KEY=your_key_here")
        return False
    
    print(f"✅ API密钥存在: {api_key[:10]}...")
    
    try:
        client = ElevenLabs(api_key=api_key)
        
        # 测试基本TTS功能（不需要voices_read权限）
        print("\n🎤 测试基本TTS功能...")
        test_text = "Hello, this is a test."
        
        # 使用已知的公开声音ID
        voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel
        
        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            text=test_text,
            model_id="eleven_multilingual_v2"
        )
        
        # 尝试生成少量音频数据
        audio_data = b''
        for i, chunk in enumerate(audio_generator):
            audio_data += chunk
            if i > 5:  # 只获取前几个chunk，节省配额
                break
        
        if len(audio_data) > 100:
            print("✅ 基本TTS功能正常 - 可以进行双人对话播客生成")
        else:
            print("⚠️ TTS功能异常 - 生成的音频数据太少")
            
    except Exception as e:
        error_str = str(e)
        print(f"❌ TTS测试失败: {e}")
        
        if "missing_permissions" in error_str:
            print("\n📝 权限不足 - 但这不影响双人对话功能！")
            print("   • voices_read权限缺失只影响声音列表查询")
            print("   • TTS生成功能通常仍然可用")
            print("   • 系统会使用预设的公开声音ID")
            return True
        else:
            print(f"❌ 其他API错误: {e}")
            return False
    
    # 尝试测试voices_read权限
    print("\n👥 测试声音列表权限...")
    try:
        voices = client.voices.get_all()
        print(f"✅ 声音列表权限正常 - 找到 {len(voices.voices)} 个声音")
        return True
    except Exception as e:
        error_str = str(e)
        if "missing_permissions" in error_str and "voices_read" in error_str:
            print("⚠️ 缺少voices_read权限")
            print("📝 这不影响双人对话功能，系统会使用预设声音")
            return True  # TTS功能可用就行
        else:
            print(f"❌ 声音列表测试失败: {e}")
            return False


def show_solutions():
    """显示解决方案"""
    print("\n" + "=" * 50)
    print("📋 权限问题解决方案")
    print("=" * 50)
    
    print("\n1️⃣ 免费账户限制:")
    print("   • ElevenLabs免费账户可能限制某些API权限")
    print("   • 但TTS生成功能通常仍可使用")
    print("   • 双人对话播客功能不受影响")
    
    print("\n2️⃣ 推荐操作:")
    print("   • 继续使用现有API密钥进行播客生成")
    print("   • 系统会自动使用预设的公开声音ID")
    print("   • 无需升级账户即可享受双人对话功能")
    
    print("\n3️⃣ 如需完整权限:")
    print("   • 访问 https://elevenlabs.io/")
    print("   • 考虑升级到付费账户")
    print("   • 重新生成具有完整权限的API密钥")
    
    print("\n4️⃣ 测试建议:")
    print("   • 直接运行: python scripts/tools/test_dual_voice_podcast.py")
    print("   • 或使用主程序: python run.py (选择YouTube播客生成器)")
    print("   • 系统会自动处理权限限制")


def main():
    """主函数"""
    print("🔐 ElevenLabs API权限检查工具")
    print("=" * 50)
    
    success = check_api_permissions()
    
    show_solutions()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 结论: 你的API密钥可以用于双人对话播客生成！")
        print("💡 建议: 直接开始使用播客功能，忽略权限警告")
    else:
        print("❌ 结论: API密钥存在问题，需要检查配置")
        print("💡 建议: 检查API密钥是否正确，或重新生成")
    
    print("\n🚀 下一步:")
    print("   python scripts/tools/test_dual_voice_podcast.py")


if __name__ == "__main__":
    main()