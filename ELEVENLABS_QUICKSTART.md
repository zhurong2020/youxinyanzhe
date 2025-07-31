# ElevenLabs双人对话功能快速开始指南

## ✅ 导入问题已修复

我已经修复了所有的类型注解导入问题：
- 添加了缺失的 `Any` 类型导入
- 添加了缺失的 `List, Tuple` 类型导入  
- 优化了YAML库的导入处理

## 🚀 立即开始使用

### 1. 确保环境正确
```bash
# 激活虚拟环境（如果你使用了虚拟环境）
source venv/bin/activate

# 确保所有依赖已安装
pip install -r requirements.txt
```

### 2. 配置API密钥
在 `.env` 文件中添加：
```env
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. 测试ElevenLabs功能
```bash
# 测试声音和API
python scripts/tools/elevenlabs_voice_tester.py

# 建议选择的测试流程:
# 1. 选择选项 1: 列出所有可用声音
# 2. 选择选项 2: 获取可用TTS模型  
# 4. 选择选项 4: 创建双人对话播客测试
# 或者选择选项 7: 完整测试流程（一键测试所有功能）
```

### 4. 测试双人对话功能
```bash
# 运行双人对话测试
python scripts/tools/test_dual_voice_podcast.py
```

### 5. 使用YouTube播客生成器
```bash
# 运行主程序
python run.py

# 选择选项 10: YouTube播客生成器
# 输入YouTube视频URL
# 系统会自动检测对话格式并启用双人模式
```

## 🎯 预期效果

### 双人模式自动启用条件
当满足以下条件时，系统会自动启用双人对话模式：
1. ✅ 脚本包含对话格式（`[角色]:`、`A:`等）
2. ✅ 使用ElevenLabs TTS引擎
3. ✅ ElevenLabs API正常工作
4. ✅ pydub库可用于音频合并

### 日志输出示例
```
🎭 检测到对话格式，启用双人对话模式
🎤 生成对话片段 1/6: 大家好，欢迎收听今天的播客...
🎤 生成对话片段 2/6: 是的，今天我们要讨论一个很有趣的话题...
✅ 双人对话音频生成成功: assets/audio/podcast.wav
```

## 🔧 如果遇到问题

### 问题1: "No module named 'elevenlabs'"
```bash
pip install elevenlabs
```

### 问题2: "No module named 'pydub'"
```bash
pip install pydub
```

### 问题3: ElevenLabs API失败
- 检查API密钥是否正确设置
- 运行声音测试器确认API工作正常
- 系统会自动回退到其他TTS引擎

### 问题4: 没有启用双人模式
检查脚本是否包含对话标记：
- `[主播助手]: 内容`
- `【专家】: 内容`  
- `A: 内容`
- `B: 内容`

## 📞 技术支持

如果仍有问题，请检查：
1. 虚拟环境是否激活
2. 所有依赖是否正确安装
3. API密钥是否有效
4. 网络连接是否正常

现在你可以开始使用升级后的双人对话播客功能了！🎉