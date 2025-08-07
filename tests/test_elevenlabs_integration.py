#!/usr/bin/env python3
"""
测试ElevenLabs集成功能
"""

import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestElevenLabsIntegration:
    """测试ElevenLabs集成功能"""
    
    def test_elevenlabs_menu_function_exists(self):
        """测试ElevenLabs菜单函数是否存在"""
        from run import handle_elevenlabs_menu
        assert callable(handle_elevenlabs_menu)
    
    def test_required_files_exist(self):
        """测试必要文件是否存在"""
        required_files = [
            "scripts/tools/elevenlabs_voice_tester.py",
            "scripts/tools/elevenlabs_permission_check.py",
            "scripts/tools/test_dual_voice_podcast.py",
            "config/elevenlabs_voices.yml",
            "config/elevenlabs_voices_template.yml",
            "docs/guides/dual_voice_podcast_guide.md",
            "docs/guides/elevenlabs_voice_testing_guide.md"
        ]
        
        for file_path in required_files:
            assert Path(file_path).exists(), f"Required file missing: {file_path}"
    
    def test_config_file_structure(self):
        """测试配置文件结构"""
        config_file = Path("config/elevenlabs_voices.yml")
        assert config_file.exists()
        
        try:
            import yaml
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            assert 'elevenlabs_voices' in config
            assert 'voice_combinations' in config['elevenlabs_voices']
            assert 'chinese_podcast' in config['elevenlabs_voices']['voice_combinations']
            
            chinese_podcast = config['elevenlabs_voices']['voice_combinations']['chinese_podcast']
            assert 'speaker_a' in chinese_podcast
            assert 'speaker_b' in chinese_podcast
            
        except ImportError:
            # 如果没有PyYAML，跳过这个测试
            pytest.skip("PyYAML not installed")
    
    def test_menu_integration_in_run_py(self):
        """测试菜单集成是否正确"""
        with open("run.py", 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查菜单选项
        assert "10. ElevenLabs语音测试" in content
        assert "请输入选项 (1-10/0)" in content
        assert "'10': 'ElevenLabs语音测试'" in content
        assert "handle_elevenlabs_menu(pipeline)" in content
        assert "def handle_elevenlabs_menu(pipeline):" in content
    
    @patch('subprocess.run')
    def test_elevenlabs_menu_subprocess_calls(self, mock_subprocess):
        """测试ElevenLabs菜单的子进程调用"""
        from run import handle_elevenlabs_menu
        
        # 模拟pipeline对象
        mock_pipeline = Mock()
        mock_pipeline.log = Mock()
        
        # 模拟用户输入和subprocess返回
        mock_subprocess.return_value.returncode = 0
        
        with patch('builtins.input', side_effect=['1', '0']):  # 选择选项1然后退出
            handle_elevenlabs_menu(mock_pipeline)
        
        # 验证subprocess被调用
        mock_subprocess.assert_called()
        
        # 验证日志被记录
        mock_pipeline.log.assert_called()


class TestElevenLabsTools:
    """测试ElevenLabs工具脚本"""
    
    def test_voice_tester_imports(self):
        """测试声音测试器导入"""
        # 测试主要的导入不会失败
        import scripts.tools.elevenlabs.elevenlabs_voice_tester as voice_tester
        assert hasattr(voice_tester, 'ElevenLabsVoiceTester')
        assert hasattr(voice_tester, 'main')
    
    def test_permission_check_imports(self):
        """测试权限检查工具导入"""
        import scripts.tools.elevenlabs.elevenlabs_permission_check as permission_check
        assert hasattr(permission_check, 'check_api_permissions')
        assert hasattr(permission_check, 'main')
    
    def test_dual_voice_test_imports(self):
        """测试双人对话测试导入"""
        import scripts.tools.elevenlabs.test_dual_voice_podcast as dual_voice_test
        assert hasattr(dual_voice_test, 'test_dual_voice_dialogue')
        assert hasattr(dual_voice_test, 'main')


class TestYouTubePodcastGeneratorDualVoice:
    """测试YouTube播客生成器的双人对话功能"""
    
    def test_youtube_generator_imports(self):
        """测试YouTube播客生成器导入"""
        from scripts.core.youtube_podcast_generator import YouTubePodcastGenerator
        assert YouTubePodcastGenerator is not None
    
    def test_dual_voice_methods_exist(self):
        """测试双人对话相关方法是否存在"""
        from scripts.core.youtube_podcast_generator import YouTubePodcastGenerator
        
        # 检查新增的双人对话方法
        methods = [
            '_generate_dual_speaker_audio',
            '_generate_single_speaker_audio', 
            '_parse_dialogue',
            '_get_speaker_settings',
            '_get_speaker_voice_id',
            '_merge_dialogue_segments',
            '_load_voice_config',
            '_get_default_voice_config'
        ]
        
        for method_name in methods:
            assert hasattr(YouTubePodcastGenerator, method_name), f"Method {method_name} not found"
    
    def test_dialogue_parsing(self):
        """测试对话解析功能"""
        from scripts.core.youtube_podcast_generator import YouTubePodcastGenerator
        
        # 创建一个测试实例
        config = {'GEMINI_API_KEY': 'test', 'ELEVENLABS_API_KEY': 'test'}
        generator = YouTubePodcastGenerator(config)
        
        # 测试对话解析
        test_text = """
        [主播助手]: 大家好，欢迎收听播客。
        [学习导师]: 是的，今天我们讨论一个有趣的话题。
        [主播助手]: 这个话题确实很有意思。
        """
        
        dialogue_segments = generator._parse_dialogue(test_text)
        
        assert len(dialogue_segments) == 3
        assert dialogue_segments[0][0] == 'A'  # 主播助手映射到A
        assert dialogue_segments[1][0] == 'B'  # 学习导师映射到B
        assert dialogue_segments[2][0] == 'A'  # 主播助手映射到A
    
    def test_default_voice_config(self):
        """测试默认声音配置"""
        from scripts.core.youtube_podcast_generator import YouTubePodcastGenerator
        
        config = {'GEMINI_API_KEY': 'test', 'ELEVENLABS_API_KEY': 'test'}
        generator = YouTubePodcastGenerator(config)
        
        default_config = generator._get_default_voice_config()
        
        assert 'voice_combinations' in default_config
        assert 'chinese_podcast' in default_config['voice_combinations']
        
        chinese_config = default_config['voice_combinations']['chinese_podcast']
        assert 'speaker_a' in chinese_config
        assert 'speaker_b' in chinese_config
        
        # 检查默认声音ID
        assert chinese_config['speaker_a']['voice_id'] == "21m00Tcm4TlvDq8ikWAM"
        assert chinese_config['speaker_b']['voice_id'] == "TxGEqnHWrfWFTfGW9XjX"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])