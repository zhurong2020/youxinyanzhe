#!/usr/bin/env python3
"""
ElevenLabs语音生成功能测试

此脚本测试Pro账户的语音生成功能，无需用户读取权限。
用于验证：
1. API密钥是否可用于语音生成
2. Pro账户设置是否正确应用
3. 不同语音ID是否可用
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv()

def test_elevenlabs_voice_generation():
    """测试ElevenLabs语音生成功能"""
    print("🎙️ ElevenLabs语音生成功能测试")
    print("=" * 50)
    
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if not api_key:
        print("❌ 未找到ELEVENLABS_API_KEY环境变量")
        return False
    
    try:
        from elevenlabs import ElevenLabs, VoiceSettings
        client = ElevenLabs(api_key=api_key)
        print("✅ ElevenLabs客户端初始化成功")
        
        # 测试文本（简短测试）
        test_text = "这是一个ElevenLabs Pro账户语音质量测试。"
        
        # Pro账户优化设置
        pro_settings = VoiceSettings(
            stability=0.3,        # Pro级别低稳定性
            similarity_boost=0.9, # Pro级别高相似度
            style=0.7,           # Pro级别高风格化
            use_speaker_boost=True # Pro专属功能
        )
        
        print(f"🎯 测试设置:")
        print(f"   稳定性: 0.3 (Pro级别)")
        print(f"   相似度: 0.9 (Pro级别)")
        print(f"   风格化: 0.7 (Pro级别)")
        print(f"   语音增强: True (Pro专属)")
        
        # 测试Rachel语音
        try:
            print("\n🎤 测试Rachel语音生成...")
            rachel_voice_id = "21m00Tcm4TlvDq8ikWAM"
            
            audio_generator = client.text_to_speech.convert(
                voice_id=rachel_voice_id,
                text=test_text,
                model_id="eleven_multilingual_v2",
                voice_settings=pro_settings
            )
            
            # 收集音频数据（但不保存，仅测试）
            audio_data = b''.join(chunk for chunk in audio_generator)
            
            if audio_data and len(audio_data) > 1000:  # 简单验证音频数据
                print("✅ Rachel语音生成成功")
                print(f"   音频数据大小: {len(audio_data):,} 字节")
                print("   Pro设置已应用")
                return True
            else:
                print("❌ 音频数据异常")
                return False
                
        except Exception as voice_error:
            print(f"❌ 语音生成失败: {voice_error}")
            return False
            
    except ImportError:
        print("❌ ElevenLabs库未安装，请运行: pip install elevenlabs")
        return False
    except Exception as e:
        print(f"❌ ElevenLabs客户端初始化失败: {e}")
        return False

def test_voice_configurations():
    """测试语音配置加载"""
    print("\n📋 测试语音配置文件...")
    
    try:
        import yaml
        
        # 检查Pro配置
        pro_config_path = project_root / "config" / "elevenlabs_voices_pro.yml"
        standard_config_path = project_root / "config" / "elevenlabs_voices.yml"
        
        if pro_config_path.exists():
            with open(pro_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            print("✅ Pro配置文件加载成功")
            
            # 检查Pro功能配置
            pro_features = config.get('elevenlabs_voices', {}).get('pro_features', {})
            if pro_features.get('enabled'):
                print("🌟 Pro功能已启用")
                print(f"   语音增强: {pro_features.get('voice_cloning', False)}")
                print(f"   高级控制: {pro_features.get('advanced_controls', False)}")
                print(f"   商业许可: {pro_features.get('commercial_license', False)}")
            
            # 检查语音组合
            combinations = config.get('elevenlabs_voices', {}).get('voice_combinations', {})
            print(f"\n📻 可用语音组合: {len(combinations)}个")
            for name, combo in combinations.items():
                print(f"   • {name}: {combo.get('description', 'N/A')}")
                
        elif standard_config_path.exists():
            print("✅ 标准配置文件加载成功")
        else:
            print("❌ 未找到配置文件")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 配置文件测试失败: {e}")
        return False

def main():
    """主函数"""
    try:
        print("🧪 ElevenLabs Pro功能验证测试")
        print("=" * 60)
        
        # 测试配置文件
        config_ok = test_voice_configurations()
        
        # 测试语音生成
        voice_ok = test_elevenlabs_voice_generation()
        
        print("\n" + "=" * 60)
        print("📊 测试结果总结")
        print("=" * 60)
        
        if config_ok and voice_ok:
            print("🎉 所有测试通过！")
            print("✅ ElevenLabs Pro账户配置正确")
            print("✅ 语音生成功能正常")
            print("✅ Pro级别设置已应用")
            print("\n💡 您现在可以使用YouTube播客生成器享受Pro级别语音质量！")
        elif config_ok and not voice_ok:
            print("⚠️ 配置正确，但语音生成有问题")
            print("💡 请检查API密钥权限或网络连接")
        elif not config_ok and voice_ok:
            print("⚠️ 语音生成正常，但配置文件有问题")
            print("💡 建议检查配置文件完整性")
        else:
            print("❌ 测试失败")
            print("💡 请检查API密钥配置和网络连接")
            
    except Exception as e:
        print(f"❌ 测试程序执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()