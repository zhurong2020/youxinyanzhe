# 安装eSpeak TTS引擎指南

YouTube播客生成器需要eSpeak TTS引擎来生成本地音频文件。

## Ubuntu/Debian系统安装

```bash
sudo apt-get update
sudo apt-get install -y espeak espeak-data
```

## 验证安装

```bash
espeak "Hello World" -v zh -s 150
```

如果听到语音输出，说明安装成功。

## 如果无法安装

如果无法安装eSpeak，系统会：
1. 生成播客文本脚本（保存在 `assets/audio/` 目录）
2. 在文章中显示音频生成失败的提示
3. 提供其他学习建议

## 其他TTS选项

可以考虑使用：
- OpenAI TTS（需要API密钥）
- ElevenLabs TTS（需要API密钥）
- Google Text-to-Speech（通过Podcastfy在线服务）