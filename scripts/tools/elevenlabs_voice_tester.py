#!/usr/bin/env python3
"""
ElevenLabs声音测试工具
用于测试账户中可用的声音，并生成双人对话播客
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

try:
    from elevenlabs import ElevenLabs, VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    print("❌ 请先安装 elevenlabs: pip install elevenlabs")
    exit(1)

try:
    from pydub import AudioSegment
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    print("⚠️ 未安装 pydub，无法进行音频处理: pip install pydub")
    AUDIO_PROCESSING_AVAILABLE = False


class ElevenLabsVoiceTester:
    """ElevenLabs声音测试器"""
    
    def __init__(self):
        """初始化测试器"""
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        if not self.api_key:
            raise ValueError("请在.env文件中设置ELEVENLABS_API_KEY")
        
        self.client = ElevenLabs(api_key=self.api_key)
        self.test_dir = Path("tests/elevenlabs_voice_tests")
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        # 测试文本
        self.test_texts = {
            'chinese': "你好，我是AI语音助手。今天天气很好，适合学习新知识。",
            'english': "Hello, I'm an AI voice assistant. The weather is great today for learning.",
            'conversation_a': "大家好，欢迎收听今天的播客。我们来讨论一个有趣的话题。",
            'conversation_b': "是的，这确实是个值得深入探讨的问题。让我们从不同角度来分析。"
        }
    
    def list_all_voices(self) -> Dict[str, Dict]:
        """获取账户中所有可用声音"""
        print("\n🔍 正在获取账户中的所有声音...")
        
        try:
            voices = self.client.voices.get_all()
            voice_dict = {}
            
            print(f"✅ 找到 {len(voices.voices)} 个可用声音\n")
            print("=" * 80)
            print(f"{'ID':<25} {'名称':<15} {'类别':<12} {'描述'}")
            print("=" * 80)
            
            for voice in voices.voices:
                voice_info = {
                    'name': voice.name,
                    'voice_id': voice.voice_id,
                    'category': getattr(voice, 'category', 'Unknown'),
                    'description': getattr(voice, 'description', ''),
                    'preview_url': getattr(voice, 'preview_url', ''),
                    'labels': getattr(voice, 'labels', {}),
                    'settings': getattr(voice, 'settings', None),
                    'available_models': getattr(voice, 'available_models', [])
                }
                
                voice_dict[voice.voice_id] = voice_info
                
                # 打印声音信息
                print(f"{voice.voice_id:<25} {voice.name:<15} {voice_info['category']:<12} {voice_info['description'][:30]}")
            
            print("=" * 80)
            
            # 保存声音列表到文件
            output_file = self.test_dir / "available_voices.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(voice_dict, f, indent=2, ensure_ascii=False)
            
            print(f"💾 声音列表已保存到: {output_file}")
            return voice_dict
            
        except Exception as e:
            error_str = str(e)
            print(f"❌ 获取声音列表失败: {e}")
            
            # 检查是否是权限问题
            if "missing_permissions" in error_str and "voices_read" in error_str:
                print("📝 权限问题解决方案:")
                print("   1. 检查你的ElevenLabs账户类型 - 可能需要付费账户")
                print("   2. 在ElevenLabs官网重新生成API密钥")
                print("   3. 确认API密钥有完整权限")
                print("   4. 或者直接使用预设的公开声音ID进行测试")
                
                # 返回预设的声音信息
                print("\n💡 使用预设的公开声音进行测试...")
                return self._get_fallback_voices()
            
            return {}
    
    def _get_fallback_voices(self) -> Dict[str, Dict]:
        """获取回退的预设声音列表"""
        fallback_voices = {
            "21m00Tcm4TlvDq8ikWAM": {
                "name": "Rachel",
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "category": "premade",
                "description": "清晰、专业的女性声音，适合主持",
                "preview_url": "",
                "labels": {"gender": "female", "language": "multilingual"},
                "settings": None,
                "available_models": ["eleven_multilingual_v2"]
            },
            "TxGEqnHWrfWFTfGW9XjX": {
                "name": "Josh",
                "voice_id": "TxGEqnHWrfWFTfGW9XjX", 
                "category": "premade",
                "description": "温和、友好的男性声音，适合对话",
                "preview_url": "",
                "labels": {"gender": "male", "language": "multilingual"},
                "settings": None,
                "available_models": ["eleven_multilingual_v2"]
            },
            "EXAVITQu4vr4xnSDxMaL": {
                "name": "Bella",
                "voice_id": "EXAVITQu4vr4xnSDxMaL",
                "category": "premade", 
                "description": "专业、权威的女性声音",
                "preview_url": "",
                "labels": {"gender": "female", "language": "multilingual"},
                "settings": None,
                "available_models": ["eleven_multilingual_v2"]
            },
            "MF3mGyEYCl7XYWbV9V6O": {
                "name": "Elli",
                "voice_id": "MF3mGyEYCl7XYWbV9V6O",
                "category": "premade",
                "description": "知性、优雅的女性声音", 
                "preview_url": "",
                "labels": {"gender": "female", "language": "multilingual"},
                "settings": None,
                "available_models": ["eleven_multilingual_v2"]
            },
            "AZnzlk1XvdvUeBnXmlld": {
                "name": "Domi",
                "voice_id": "AZnzlk1XvdvUeBnXmlld",
                "category": "premade",
                "description": "亲切、活泼的女性声音",
                "preview_url": "",
                "labels": {"gender": "female", "language": "multilingual"},
                "settings": None,
                "available_models": ["eleven_multilingual_v2"]
            }
        }
        
        print(f"✅ 使用预设声音列表 ({len(fallback_voices)} 个声音)")
        print("=" * 80)
        print(f"{'ID':<25} {'名称':<15} {'类别':<12} {'描述'}")
        print("=" * 80)
        
        for voice_id, voice_info in fallback_voices.items():
            print(f"{voice_id:<25} {voice_info['name']:<15} {voice_info['category']:<12} {voice_info['description'][:30]}")
        
        print("=" * 80)
        
        # 保存预设声音列表
        output_file = self.test_dir / "fallback_voices.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(fallback_voices, f, indent=2, ensure_ascii=False)
        
        print(f"💾 预设声音列表已保存到: {output_file}")
        return fallback_voices
    
    def get_available_models(self) -> Dict[str, Any]:
        """获取可用的TTS模型列表"""
        print("\n🔍 正在获取可用的TTS模型...")
        
        try:
            # 尝试获取模型信息
            models_info = {}
            
            # 检查客户端是否有models相关方法
            if hasattr(self.client, 'models'):
                try:
                    models = self.client.models.get_all()
                    print(f"✅ 找到 {len(models)} 个可用模型")
                    for model in models:
                        model_info = {
                            'model_id': getattr(model, 'model_id', 'Unknown'),
                            'name': getattr(model, 'name', 'Unknown'),
                            'description': getattr(model, 'description', ''),
                            'languages': getattr(model, 'languages', []),
                            'can_be_finetuned': getattr(model, 'can_be_finetuned', False),
                            'can_do_text_to_speech': getattr(model, 'can_do_text_to_speech', True),
                            'can_do_voice_conversion': getattr(model, 'can_do_voice_conversion', False),
                            'token_cost_factor': getattr(model, 'token_cost_factor', 1.0)
                        }
                        models_info[model.model_id] = model_info
                        print(f"  📋 {model.model_id}: {model.name}")
                except Exception as model_error:
                    print(f"   ⚠️ 无法获取详细模型信息: {model_error}")
            else:
                print("   ⚠️ 客户端不支持models API")
            
            # 如果没有获取到模型，使用已知的模型列表
            if not models_info:
                print("   📝 使用已知模型列表:")
                known_models = {
                    "eleven_multilingual_v2": {
                        "name": "Multilingual v2",
                        "description": "最新的多语言模型，支持28种语言",
                        "languages": ["zh", "en", "ja", "ko", "es", "fr", "de", "it", "pt", "ru"],
                        "recommended": True
                    },
                    "eleven_multilingual_v1": {
                        "name": "Multilingual v1",
                        "description": "第一代多语言模型",
                        "languages": ["zh", "en", "es", "fr", "de", "it", "pt"],
                        "recommended": False
                    },
                    "eleven_monolingual_v1": {
                        "name": "English v1",
                        "description": "英语专用模型，英语效果最佳",
                        "languages": ["en"],
                        "recommended": False
                    },
                    "eleven_turbo_v2": {
                        "name": "Turbo v2",
                        "description": "高速生成模型，速度更快",
                        "languages": ["en"],
                        "recommended": False
                    }
                }
                models_info = known_models
                for model_id, info in known_models.items():
                    status = "✨ 推荐" if info.get("recommended") else ""
                    print(f"  📋 {model_id}: {info['name']} {status}")
            
            # 保存模型信息
            output_file = self.test_dir / "available_models.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(models_info, f, indent=2, ensure_ascii=False)
            
            print(f"💾 模型信息已保存到: {output_file}")
            return models_info
            
        except Exception as e:
            print(f"❌ 获取模型列表失败: {e}")
            return {}
    
    def test_voice_quality(self, voice_id: str, voice_name: str, test_text: str = None) -> bool:
        """测试特定声音的质量"""
        if not test_text:
            test_text = self.test_texts['chinese']
        
        print(f"🎙️ 测试声音: {voice_name} ({voice_id})")
        
        try:
            # 生成测试音频
            audio_generator = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=test_text,
                model_id="eleven_multilingual_v2",
                voice_settings=VoiceSettings(
                    stability=0.4,
                    similarity_boost=0.8,
                    style=0.6,
                    use_speaker_boost=True
                )
            )
            
            # 保存音频文件
            output_file = self.test_dir / f"test_{voice_name}_{voice_id[:8]}.mp3"
            with open(output_file, 'wb') as f:
                for chunk in audio_generator:
                    f.write(chunk)
            
            print(f"   ✅ 测试成功，音频已保存: {output_file}")
            return True
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            return False
    
    def batch_test_voices(self, voice_dict: Dict[str, Dict], max_tests: int = 5) -> List[str]:
        """批量测试声音质量"""
        print(f"\n🧪 开始批量测试声音 (最多测试 {max_tests} 个)...")
        
        successful_voices = []
        test_count = 0
        
        for voice_id, voice_info in voice_dict.items():
            if test_count >= max_tests:
                break
            
            if self.test_voice_quality(voice_id, voice_info['name']):
                successful_voices.append(voice_id)
            
            test_count += 1
            time.sleep(1)  # 避免API限流
        
        print(f"\n✅ 成功测试了 {len(successful_voices)} 个声音")
        return successful_voices
    
    def create_dual_voice_podcast(self, voice_a_id: str, voice_b_id: str, 
                                voice_a_name: str = "A", voice_b_name: str = "B") -> bool:
        """创建双人对话播客"""
        print(f"\n🎭 创建双人对话播客: {voice_a_name} & {voice_b_name}")
        
        # 对话脚本
        dialogue_script = [
            (voice_a_id, self.test_texts['conversation_a']),
            (voice_b_id, self.test_texts['conversation_b']),
            (voice_a_id, "这个观点很有意思。你觉得我们还应该考虑哪些因素？"),
            (voice_b_id, "我认为数据分析和用户反馈都很重要。让我们详细讨论一下。"),
            (voice_a_id, "好的，那我们先从数据分析开始说起。"),
            (voice_b_id, "数据能告诉我们很多故事，关键是如何正确解读。")
        ]
        
        try:
            audio_segments = []
            
            for i, (voice_id, text) in enumerate(dialogue_script):
                print(f"   🎤 生成片段 {i+1}/{len(dialogue_script)}: {text[:20]}...")
                
                # 为不同角色设置不同的语音参数
                if voice_id == voice_a_id:
                    voice_settings = VoiceSettings(
                        stability=0.4,
                        similarity_boost=0.8,
                        style=0.6,
                        use_speaker_boost=True
                    )
                else:
                    voice_settings = VoiceSettings(
                        stability=0.35,
                        similarity_boost=0.85,
                        style=0.5,
                        use_speaker_boost=True
                    )
                
                audio_generator = self.client.text_to_speech.convert(
                    voice_id=voice_id,
                    text=text,
                    model_id="eleven_multilingual_v2",
                    voice_settings=voice_settings
                )
                
                # 收集音频数据
                audio_data = b''.join(chunk for chunk in audio_generator)
                audio_segments.append(audio_data)
                
                time.sleep(0.5)  # 避免API限流
            
            # 合并音频片段
            if AUDIO_PROCESSING_AVAILABLE:
                combined_audio = self._merge_audio_segments(audio_segments)
                output_file = self.test_dir / f"dual_voice_podcast_{voice_a_name}_{voice_b_name}.wav"
                combined_audio.export(str(output_file), format="wav")
                print(f"   ✅ 双人播客生成成功: {output_file}")
                return True
            else:
                print("   ⚠️ 无法合并音频，pydub未安装")
                # 保存单独的音频片段
                for i, audio_data in enumerate(audio_segments):
                    output_file = self.test_dir / f"segment_{i+1}_{voice_a_name if i%2==0 else voice_b_name}.mp3"
                    with open(output_file, 'wb') as f:
                        f.write(audio_data)
                print(f"   💾 已保存 {len(audio_segments)} 个音频片段")
                return True
                
        except Exception as e:
            print(f"   ❌ 双人播客生成失败: {e}")
            return False
    
    def _merge_audio_segments(self, audio_segments: List[bytes]) -> AudioSegment:
        """合并音频片段"""
        import io
        
        combined_audio = AudioSegment.empty()
        
        for audio_data in audio_segments:
            # 将bytes数据转换为AudioSegment
            audio_io = io.BytesIO(audio_data)
            segment = AudioSegment.from_file(audio_io, format="mp3")
            
            # 添加短暂停顿 (0.8秒)
            pause = AudioSegment.silent(duration=800)
            combined_audio += segment + pause
        
        return combined_audio
    
    def check_conversation_api(self) -> bool:
        """检查是否支持对话API"""
        print("\n🔍 检查ElevenLabs对话API支持...")
        
        try:
            # 尝试访问对话相关的API
            # 注意：这个API可能不存在或需要特殊权限
            # 这里只是示例代码
            
            # 检查客户端是否有conversation相关方法
            client_methods = [method for method in dir(self.client) if 'conversation' in method.lower()]
            
            if client_methods:
                print(f"   ✅ 发现对话相关方法: {client_methods}")
                return True
            else:
                print("   ⚠️ 未发现内置对话API，建议使用分段合成方法")
                return False
                
        except Exception as e:
            print(f"   ❌ 检查对话API失败: {e}")
            return False
    
    def generate_voice_config(self, successful_voices: List[str], voice_dict: Dict[str, Dict]) -> None:
        """生成声音配置文件"""
        print("\n📝 生成声音配置文件...")
        
        # 推荐的声音组合
        config = {
            "elevenlabs_voices": {
                "api_settings": {
                    "model_id": "eleven_multilingual_v2",
                    "default_settings": {
                        "stability": 0.4,
                        "similarity_boost": 0.8,
                        "style": 0.6,
                        "use_speaker_boost": True
                    }
                },
                "voice_combinations": {
                    "chinese_podcast": {
                        "description": "中文播客推荐组合",
                        "speaker_a": {
                            "voice_id": successful_voices[0] if successful_voices else "21m00Tcm4TlvDq8ikWAM",
                            "name": voice_dict.get(successful_voices[0], {}).get('name', 'Unknown') if successful_voices else 'Rachel',
                            "role": "主持人",
                            "settings": {
                                "stability": 0.4,
                                "similarity_boost": 0.8,
                                "style": 0.6
                            }
                        },
                        "speaker_b": {
                            "voice_id": successful_voices[1] if len(successful_voices) > 1 else "TxGEqnHWrfWFTfGW9XjX",
                            "name": voice_dict.get(successful_voices[1], {}).get('name', 'Unknown') if len(successful_voices) > 1 else 'Josh',
                            "role": "嘉宾",
                            "settings": {
                                "stability": 0.35,
                                "similarity_boost": 0.85,
                                "style": 0.5
                            }
                        }
                    }
                },
                "available_voices": {
                    voice_id: {
                        "name": info['name'],
                        "category": info['category'],
                        "tested": voice_id in successful_voices
                    } for voice_id, info in voice_dict.items()
                }
            }
        }
        
        # 保存配置文件
        config_file = Path("config/elevenlabs_voices.yml")
        config_file.parent.mkdir(exist_ok=True)
        
        # 转换为YAML格式并保存
        import yaml
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True, indent=2)
            print(f"✅ 配置文件已生成: {config_file}")
        except ImportError:
            # 如果没有安装yaml，保存为JSON
            config_file = config_file.with_suffix('.json')
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"✅ 配置文件已生成: {config_file}")


def main():
    """主函数"""
    print("🎙️ ElevenLabs声音测试工具")
    print("=" * 50)
    
    try:
        tester = ElevenLabsVoiceTester()
        
        while True:
            print("\n请选择操作：")
            print("1. 列出所有可用声音")
            print("2. 获取可用TTS模型")
            print("3. 批量测试声音质量")
            print("4. 创建双人对话播客测试")
            print("5. 检查对话API支持")
            print("6. 生成声音配置文件")
            print("7. 完整测试流程")
            print("0. 退出")
            
            choice = input("\n请输入选项 (0-7): ").strip()
            
            if choice == "0":
                print("👋 再见！")
                break
            elif choice == "1":
                voice_dict = tester.list_all_voices()
            elif choice == "2":
                models_dict = tester.get_available_models()
            elif choice == "3":
                voice_dict = tester.list_all_voices()
                if voice_dict:
                    max_tests = int(input("最多测试几个声音？(默认5): ") or "5")
                    successful_voices = tester.batch_test_voices(voice_dict, max_tests)
            elif choice == "4":
                voice_dict = tester.list_all_voices()
                if len(voice_dict) >= 2:
                    voice_ids = list(voice_dict.keys())
                    print(f"使用前两个声音: {voice_dict[voice_ids[0]]['name']} & {voice_dict[voice_ids[1]]['name']}")
                    tester.create_dual_voice_podcast(
                        voice_ids[0], voice_ids[1],
                        voice_dict[voice_ids[0]]['name'], voice_dict[voice_ids[1]]['name']
                    )
                else:
                    print("❌ 需要至少2个可用声音")
            elif choice == "5":
                tester.check_conversation_api()
            elif choice == "6":
                voice_dict = tester.list_all_voices()
                successful_voices = list(voice_dict.keys())[:5]  # 假设前5个都可用
                tester.generate_voice_config(successful_voices, voice_dict)
            elif choice == "7":
                print("🚀 开始完整测试流程...")
                voice_dict = tester.list_all_voices()
                models_dict = tester.get_available_models()
                if voice_dict:
                    successful_voices = tester.batch_test_voices(voice_dict, 3)
                    if len(successful_voices) >= 2:
                        tester.create_dual_voice_podcast(
                            successful_voices[0], successful_voices[1],
                            voice_dict[successful_voices[0]]['name'],
                            voice_dict[successful_voices[1]]['name']
                        )
                    tester.check_conversation_api()
                    tester.generate_voice_config(successful_voices, voice_dict)
                    print("✅ 完整测试流程完成！")
            else:
                print("❌ 无效选项，请重新选择")
    
    except KeyboardInterrupt:
        print("\n👋 用户中断，再见！")
    except Exception as e:
        print(f"❌ 程序错误: {e}")


if __name__ == "__main__":
    main()