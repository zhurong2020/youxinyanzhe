#!/usr/bin/env python3
"""
ElevenLabs语音管理工具 - Pro账户语音优化

此工具用于：
1. 获取ElevenLabs Pro账户中所有可用的语音
2. 分析语音特性和质量
3. 为不同用途推荐最佳语音组合
4. 更新配置文件以使用高质量语音
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
load_dotenv()

class ElevenLabsVoiceManager:
    def __init__(self):
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.client = None
        self.config_path = project_root / "config" / "elevenlabs_voices.yml"
        
        if not self.api_key:
            raise ValueError("未找到ELEVENLABS_API_KEY环境变量")
            
        self._setup_client()
    
    def _setup_client(self):
        """设置ElevenLabs客户端"""
        try:
            from elevenlabs import ElevenLabs
            self.client = ElevenLabs(api_key=self.api_key)
            print("✅ ElevenLabs客户端初始化成功")
        except ImportError:
            raise ImportError("请安装ElevenLabs库: pip install elevenlabs")
        except Exception as e:
            raise Exception(f"ElevenLabs客户端初始化失败: {e}")
    
    def get_available_voices(self) -> List[Dict[str, Any]]:
        """获取所有可用的语音"""
        try:
            voices_response = self.client.voices.get_all()
            voices = []
            
            for voice in voices_response.voices:
                voice_info = {
                    'voice_id': voice.voice_id,
                    'name': voice.name,
                    'category': voice.category,
                    'description': getattr(voice, 'description', ''),
                    'labels': getattr(voice, 'labels', {}),
                    'preview_url': getattr(voice, 'preview_url', ''),
                    'available_for_tiers': getattr(voice, 'available_for_tiers', []),
                    'settings': getattr(voice, 'settings', {}),
                    'sharing': getattr(voice, 'sharing', {})
                }
                voices.append(voice_info)
            
            print(f"📊 获取到 {len(voices)} 个可用语音")
            return voices
            
        except Exception as e:
            print(f"❌ 获取语音列表失败: {e}")
            return []
    
    def analyze_voice_quality(self, voices: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """分析语音质量和分类"""
        categories = {
            'premium_professional': [],  # 专业级高质量语音
            'premium_conversational': [],  # 对话式高质量语音
            'standard': [],  # 标准语音
            'multilingual': [],  # 多语言语音
            'chinese_optimized': []  # 中文优化语音
        }
        
        for voice in voices:
            # 基于语音名称和标签进行分类
            name = voice.get('name', '').lower()
            labels = voice.get('labels', {})
            category = voice.get('category', '').lower()
            
            # 检查是否为高质量专业语音
            if any(keyword in name for keyword in ['professional', 'narrator', 'news', 'documentary']):
                categories['premium_professional'].append(voice)
            # 检查对话式语音
            elif any(keyword in name for keyword in ['conversational', 'podcast', 'chat', 'interview']):
                categories['premium_conversational'].append(voice)
            # 检查多语言支持
            elif 'multilingual' in labels.get('description', '').lower() or 'chinese' in labels.get('description', '').lower():
                categories['multilingual'].append(voice)
            # 检查中文优化
            elif any(keyword in name for keyword in ['chinese', 'mandarin', 'cn']):
                categories['chinese_optimized'].append(voice)
            else:
                categories['standard'].append(voice)
        
        return categories
    
    def recommend_voice_combinations(self, categorized_voices: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """为不同用途推荐最佳语音组合"""
        recommendations = {}
        
        # 中文播客推荐组合
        chinese_voices = (categorized_voices['premium_conversational'] + 
                         categorized_voices['multilingual'] + 
                         categorized_voices['chinese_optimized'])
        
        if len(chinese_voices) >= 2:
            recommendations['chinese_podcast_pro'] = {
                'description': 'Pro账户中文播客高质量组合',
                'speaker_a': {
                    'voice_id': chinese_voices[0]['voice_id'],
                    'name': chinese_voices[0]['name'],
                    'role': '主持人',
                    'category': chinese_voices[0]['category'],
                    'settings': {
                        'stability': 0.35,  # Pro账户可以使用更低稳定性获得更自然效果
                        'similarity_boost': 0.9,  # Pro账户支持更高相似度
                        'style': 0.7,  # 更高的风格化程度
                        'use_speaker_boost': True  # Pro账户专属功能
                    }
                },
                'speaker_b': {
                    'voice_id': chinese_voices[1]['voice_id'],
                    'name': chinese_voices[1]['name'],
                    'role': '嘉宾',
                    'category': chinese_voices[1]['category'],
                    'settings': {
                        'stability': 0.4,
                        'similarity_boost': 0.85,
                        'style': 0.6,
                        'use_speaker_boost': True
                    }
                }
            }
        
        # 英文播客推荐组合
        english_voices = (categorized_voices['premium_professional'] + 
                         categorized_voices['premium_conversational'])
        
        if len(english_voices) >= 2:
            recommendations['english_podcast_pro'] = {
                'description': 'Pro账户英文播客专业组合',
                'speaker_a': {
                    'voice_id': english_voices[0]['voice_id'],
                    'name': english_voices[0]['name'],
                    'role': 'Host',
                    'category': english_voices[0]['category'],
                    'settings': {
                        'stability': 0.3,
                        'similarity_boost': 0.9,
                        'style': 0.8,
                        'use_speaker_boost': True
                    }
                },
                'speaker_b': {
                    'voice_id': english_voices[1]['voice_id'],
                    'name': english_voices[1]['name'],
                    'role': 'Guest',
                    'category': english_voices[1]['category'],
                    'settings': {
                        'stability': 0.35,
                        'similarity_boost': 0.85,
                        'style': 0.7,
                        'use_speaker_boost': True
                    }
                }
            }
        
        return recommendations
    
    def update_voice_config(self, voices: List[Dict[str, Any]], recommendations: Dict[str, Dict]):
        """更新语音配置文件"""
        try:
            # 读取现有配置
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
            else:
                config = {'elevenlabs_voices': {}}
            
            # 更新API设置为Pro账户优化配置
            config['elevenlabs_voices']['api_settings'] = {
                'default_settings': {
                    'similarity_boost': 0.9,  # Pro账户可用更高值
                    'stability': 0.35,  # 更低稳定性获得更自然效果
                    'style': 0.7,  # 更高风格化
                    'use_speaker_boost': True  # Pro账户专属
                },
                'model_id': 'eleven_multilingual_v2',  # 使用多语言模型
                'turbo_mode': False,  # Pro账户可选择高质量模式
                'output_format': 'mp3_44100_128'  # 高质量输出格式
            }
            
            # 更新可用语音列表
            config['elevenlabs_voices']['available_voices'] = {}
            for voice in voices:
                config['elevenlabs_voices']['available_voices'][voice['voice_id']] = {
                    'name': voice['name'],
                    'category': voice['category'],
                    'description': voice.get('description', ''),
                    'labels': voice.get('labels', {}),
                    'preview_url': voice.get('preview_url', '')
                }
            
            # 更新推荐组合
            config['elevenlabs_voices']['voice_combinations'].update(recommendations)
            
            # 保存配置文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False, indent=2)
            
            print(f"✅ 配置文件已更新: {self.config_path}")
            return True
            
        except Exception as e:
            print(f"❌ 更新配置文件失败: {e}")
            return False
    
    def display_voice_summary(self, categorized_voices: Dict[str, List[Dict]], 
                            recommendations: Dict[str, Dict]):
        """显示语音分析总结"""
        print("\n" + "="*60)
        print("🎙️ ElevenLabs Pro账户语音分析总结")
        print("="*60)
        
        # 显示各类别语音数量
        for category, voices in categorized_voices.items():
            if voices:
                category_names = {
                    'premium_professional': '专业级语音',
                    'premium_conversational': '对话式语音', 
                    'standard': '标准语音',
                    'multilingual': '多语言语音',
                    'chinese_optimized': '中文优化语音'
                }
                print(f"📊 {category_names.get(category, category)}: {len(voices)}个")
                for voice in voices[:3]:  # 显示前3个
                    print(f"   • {voice['name']} ({voice['voice_id'][:8]}...)")
                if len(voices) > 3:
                    print(f"   • ... 还有{len(voices)-3}个语音")
                print()
        
        # 显示推荐组合
        print("\n🎯 推荐语音组合:")
        for combo_name, combo_config in recommendations.items():
            print(f"\n📻 {combo_config['description']}:")
            print(f"   主讲者: {combo_config['speaker_a']['name']} ({combo_config['speaker_a']['role']})")
            print(f"   对话者: {combo_config['speaker_b']['name']} ({combo_config['speaker_b']['role']})")
        
        print(f"\n💡 配置已保存到: {self.config_path}")
        print("💡 现在可以在YouTube播客生成器中使用这些高质量语音组合!")

def main():
    """主函数"""
    try:
        print("🎙️ ElevenLabs Pro账户语音管理工具")
        print("=" * 50)
        
        # 初始化管理器
        voice_manager = ElevenLabsVoiceManager()
        
        # 获取所有可用语音
        print("\n📡 正在获取可用语音列表...")
        voices = voice_manager.get_available_voices()
        
        if not voices:
            print("❌ 未能获取到语音列表，请检查API密钥和网络连接")
            return
        
        # 分析语音质量
        print("\n🔍 正在分析语音质量和特性...")
        categorized_voices = voice_manager.analyze_voice_quality(voices)
        
        # 生成推荐组合
        print("\n🎯 正在生成推荐语音组合...")
        recommendations = voice_manager.recommend_voice_combinations(categorized_voices)
        
        # 更新配置文件
        print("\n💾 正在更新配置文件...")
        if voice_manager.update_voice_config(voices, recommendations):
            voice_manager.display_voice_summary(categorized_voices, recommendations)
        else:
            print("❌ 配置文件更新失败")
            
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()