# YouTube播客生成器TTS升级指南

## 🎯 升级内容

### 新增高质量TTS支持
- **Google TTS (gTTS)** - 最佳音质，自然流畅的中文语音 ⭐⭐⭐⭐⭐
- **智能降级策略** - 自动尝试不同TTS引擎直到成功
- **音频格式支持** - 支持WAV/MP3格式转换

## 📦 安装新依赖

```bash
# 安装高质量TTS依赖
pip install gtts>=2.3.0 pydub>=0.25.0 pygame>=2.1.0

# 或使用requirements.txt
pip install -r requirements.txt
```

## 🔧 TTS引擎对比

| TTS引擎 | 音质 | 速度 | 中文支持 | 网络要求 | 推荐度 |
|---------|------|------|----------|----------|--------|
| **Google TTS** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 需要 | 🏆 最佳 |
| eSpeak | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | 不需要 | 备用 |
| pyttsx3 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 不需要 | 系统默认 |

## 🚀 使用方法

### 自动选择（推荐）
系统会自动按优先级尝试：
1. **Google TTS** (最佳音质)
2. **eSpeak** (快速生成)  
3. **pyttsx3** (系统默认)

### 手动指定TTS引擎
在菜单中选择"TTS模型"时：
- **选择1 (Edge TTS)** → 自动使用Google TTS
- **选择2-4** → 按原有设置

## 🎧 音质对比测试

### 测试命令
```bash
# 测试Google TTS
python -c "from gtts import gTTS; tts = gTTS('这是Google TTS测试', lang='zh-CN'); tts.save('test_gtts.mp3')"

# 测试eSpeak
espeak -v zh -s 150 "这是eSpeak测试" -w test_espeak.wav

# 播放对比
# 您会明显感受到Google TTS的音质提升
```

## 📝 配置优化

### 模型统一
- 统一使用 `gemini-2.5-flash` 模型
- 保持与主系统配置一致
- 提升生成内容质量

### 日志优化
- 减少重复日志输出
- 增加TTS引擎选择日志
- 更清晰的音频生成过程追踪

## ⚠️ 注意事项

### 网络要求
- Google TTS需要互联网连接
- 首次使用会自动下载语音数据
- 网络异常时自动降级到本地TTS

### 依赖冲突
如果遇到依赖问题：
```bash
# 清理并重新安装
pip uninstall gtts pydub pygame pyttsx3
pip install gtts>=2.3.0 pydub>=0.25.0 pygame>=2.1.0 pyttsx3>=2.90
```

## 🎉 预期效果

### 音质提升
- **语音自然度**：从机器音变为接近人声
- **中文发音**：标准普通话，语调流畅
- **听觉体验**：显著提升播客收听体验

### 智能选择
- 自动选择最佳可用TTS引擎
- 网络异常时自动降级
- 多重保障确保音频生成成功

## 📈 使用建议

1. **首次使用**：运行一次测试确保依赖安装正确
2. **网络环境**：确保能访问Google服务获得最佳音质
3. **备用方案**：eSpeak仍然可用作快速生成选项
4. **质量对比**：建议试听不同TTS引擎的效果后选择偏好