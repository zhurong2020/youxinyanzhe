#!/usr/bin/env python3
"""
测试YouTube链接替换功能
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utils.youtube_link_mapper import YouTubeLinkMapper
from scripts.utils.audio_link_replacer import AudioLinkReplacer


class TestYouTubeLinkMapper:
    """测试YouTube链接映射器"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时目录作为项目根目录
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # 模拟项目结构
        (self.temp_path / ".tmp").mkdir(exist_ok=True)
        
        # 创建映射器实例并指向临时目录
        self.mapper = YouTubeLinkMapper()
        self.mapper.project_root = self.temp_path
        self.mapper.mapping_file = self.temp_path / ".tmp" / "youtube_mappings.json"
        self.mapper.mapping_file.parent.mkdir(exist_ok=True)
        self.mapper._load_mappings()
    
    def test_add_mapping(self):
        """测试添加映射功能"""
        # 测试数据
        local_file = "assets/audio/test.mp3"
        video_id = "dQw4w9WgXcQ"
        title = "Test Video"
        
        # 添加映射
        result = self.mapper.add_mapping(local_file, video_id, title)
        
        # 验证结果
        assert result is True
        assert local_file in self.mapper.mappings
        assert self.mapper.mappings[local_file]["video_id"] == video_id
        assert self.mapper.mappings[local_file]["title"] == title
        assert self.mapper.mappings[local_file]["youtube_url"] == f"https://www.youtube.com/watch?v={video_id}"
        assert self.mapper.mappings[local_file]["embed_url"] == f"https://www.youtube.com/embed/{video_id}"
    
    def test_get_youtube_url(self):
        """测试获取YouTube链接"""
        # 先添加映射
        local_file = "assets/audio/test.mp3"
        video_id = "dQw4w9WgXcQ"
        self.mapper.add_mapping(local_file, video_id, "Test Video")
        
        # 测试获取链接
        url = self.mapper.get_youtube_url(local_file)
        expected_url = f"https://www.youtube.com/watch?v={video_id}"
        
        assert url == expected_url
    
    def test_get_embed_url(self):
        """测试获取YouTube嵌入链接"""
        # 先添加映射
        local_file = "assets/audio/test.mp3"
        video_id = "dQw4w9WgXcQ"
        self.mapper.add_mapping(local_file, video_id, "Test Video")
        
        # 测试获取嵌入链接
        embed_url = self.mapper.get_embed_url(local_file)
        expected_url = f"https://www.youtube.com/embed/{video_id}"
        
        assert embed_url == expected_url
    
    def test_remove_mapping(self):
        """测试删除映射"""
        # 先添加映射
        local_file = "assets/audio/test.mp3"
        video_id = "dQw4w9WgXcQ"
        self.mapper.add_mapping(local_file, video_id, "Test Video")
        
        # 验证映射存在
        assert local_file in self.mapper.mappings
        
        # 删除映射
        result = self.mapper.remove_mapping(local_file)
        
        # 验证删除结果
        assert result is True
        assert local_file not in self.mapper.mappings
    
    def test_mapping_persistence(self):
        """测试映射持久化"""
        # 添加映射
        local_file = "assets/audio/persistent_test.mp3"
        video_id = "test123"
        self.mapper.add_mapping(local_file, video_id, "Persistent Test")
        
        # 创建新的映射器实例（模拟重启）
        new_mapper = YouTubeLinkMapper()
        new_mapper.project_root = self.temp_path
        new_mapper.mapping_file = self.mapper.mapping_file
        new_mapper._load_mappings()
        
        # 验证映射被正确加载
        assert local_file in new_mapper.mappings
        assert new_mapper.mappings[local_file]["video_id"] == video_id


class TestAudioLinkReplacer:
    """测试音频链接替换器"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        
        # 创建替换器实例
        self.replacer = AudioLinkReplacer()
        
        # 模拟映射器
        self.mock_mapper = Mock()
        self.replacer.mapper = self.mock_mapper
    
    def test_extract_audio_path(self):
        """测试音频路径提取"""
        # 测试标准Jekyll路径
        src_attr = "{{ site.baseurl }}/assets/audio/test.mp3"
        result = self.replacer.extract_audio_path(src_attr)
        assert result == "assets/audio/test.mp3"
        
        # 测试不同格式的路径
        src_attr2 = "{{site.baseurl}}/assets/audio/another-test.mp3"
        result2 = self.replacer.extract_audio_path(src_attr2)
        assert result2 == "assets/audio/another-test.mp3"
        
        # 测试无效路径
        invalid_src = "/some/other/path.mp3"
        result3 = self.replacer.extract_audio_path(invalid_src)
        assert result3 is None
    
    def test_create_youtube_embed(self):
        """测试YouTube嵌入代码生成"""
        video_id = "dQw4w9WgXcQ"
        title = "Test Video"
        
        embed_code = self.replacer.create_youtube_embed(video_id, title)
        
        # 验证嵌入代码包含必要元素
        assert f"https://www.youtube.com/embed/{video_id}" in embed_code
        assert 'title="Test Video"' in embed_code
        assert "youtube-audio-embed" in embed_code
        assert "🎧 中文播客导读" in embed_code
    
    def test_replace_audio_links(self):
        """测试音频链接替换"""
        # 准备测试内容
        content = '''---
title: "测试文章"
---

## 🎧 中文播客导读

<audio controls>
  <source src="{{ site.baseurl }}/assets/audio/test.mp3" type="audio/mpeg">
  您的浏览器不支持音频播放。
</audio>

这是文章内容。
'''
        
        # 模拟映射器返回
        mapping_info = {
            "video_id": "dQw4w9WgXcQ",
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "title": "Test Audio"
        }
        self.mock_mapper.get_mapping_info.return_value = mapping_info
        
        # 执行替换
        new_content, replaced_count = self.replacer.replace_audio_links(content, "test-article")
        
        # 验证替换结果
        assert replaced_count == 1
        assert "youtube.com/embed/dQw4w9WgXcQ" in new_content
        assert "youtube-audio-embed" in new_content
        assert "<audio controls>" not in new_content
    
    def test_no_replacement_when_no_mapping(self):
        """测试没有映射时不进行替换"""
        content = '''<audio controls>
  <source src="{{ site.baseurl }}/assets/audio/no-mapping.mp3" type="audio/mpeg">
  您的浏览器不支持音频播放。
</audio>'''
        
        # 模拟映射器返回None
        self.mock_mapper.get_mapping_info.return_value = None
        
        # 执行替换
        new_content, replaced_count = self.replacer.replace_audio_links(content, "test")
        
        # 验证没有替换
        assert replaced_count == 0
        assert new_content == content
        assert "<audio controls>" in new_content
    
    def test_preview_replacements(self):
        """测试替换预览功能"""
        content = '''<audio controls>
  <source src="{{ site.baseurl }}/assets/audio/test1.mp3" type="audio/mpeg">
</audio>

<audio controls>
  <source src="{{ site.baseurl }}/assets/audio/test2.mp3" type="audio/mpeg">
</audio>'''
        
        # 模拟映射器返回
        def mock_get_mapping_info(path):
            if "test1.mp3" in path:
                return {"video_id": "video1", "title": "Test 1"}
            elif "test2.mp3" in path:
                return None
            return None
        
        self.mock_mapper.get_mapping_info.side_effect = mock_get_mapping_info
        
        # 测试预览功能（不抛出异常即为成功）
        try:
            self.replacer.preview_replacements(content)
            preview_success = True
        except Exception:
            preview_success = False
        
        assert preview_success is True


@pytest.fixture
def sample_article_content():
    """示例文章内容"""
    return '''---
title: "YouTube链接替换测试文章"
date: 2025-08-03
categories: [tech-empowerment]
---

这是一个测试文章，包含音频播放器。

## 🎧 中文播客导读

<audio controls>
  <source src="{{ site.baseurl }}/assets/audio/youtube-test-video.mp3" type="audio/mpeg">
  您的浏览器不支持音频播放。
</audio>

## 文章正文

这里是文章的正文内容。
'''


def test_integration_youtube_link_replacement(sample_article_content):
    """集成测试：YouTube链接替换完整流程"""
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(sample_article_content)
        temp_file = Path(f.name)
    
    try:
        # 创建映射器并添加测试映射
        mapper = YouTubeLinkMapper()
        
        # 模拟项目根目录
        test_root = tempfile.mkdtemp()
        mapper.project_root = Path(test_root)
        mapper.mapping_file = Path(test_root) / ".tmp" / "youtube_mappings.json"
        mapper.mapping_file.parent.mkdir(parents=True, exist_ok=True)
        mapper._load_mappings()
        
        # 添加测试映射
        mapper.add_mapping("assets/audio/youtube-test-video.mp3", "testVideoId123", "Test Video")
        
        # 创建替换器并使用模拟的映射器
        replacer = AudioLinkReplacer()
        replacer.mapper = mapper
        
        # 读取文件内容
        original_content = temp_file.read_text()
        
        # 执行替换
        new_content, replaced_count = replacer.replace_audio_links(original_content, "test-article")
        
        # 验证替换结果
        assert replaced_count == 1
        assert "youtube.com/embed/testVideoId123" in new_content
        assert "<audio controls>" not in new_content
        assert "youtube-audio-embed" in new_content
        
    finally:
        # 清理临时文件
        temp_file.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])