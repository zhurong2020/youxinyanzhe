# 🎙️ TTS语音系统完整配置指南

本指南包含项目中所有TTS相关功能的完整配置方法。

## 📋 目录

- [ElevenLabs API配置](#elevenlabs-api配置)
- [双人对话播客功能](#双人对话播客功能)
- [本地eSpeak引擎](#本地espeak引擎)
- [语音测试和调试](#语音测试和调试)
- [故障排查](#故障排查)

---

## 🎯 ElevenLabs API配置

### 1. 获取API密钥

1. 访问 [ElevenLabs官网](https://elevenlabs.io)
2. 注册账号并获取API密钥
3. 在项目根目录的`.env`文件中添加：

```bash
ELEVENLABS_API_KEY=your_api_key_here
```

### 2. 配置语音参数

编辑 `config/elevenlabs_voices.yml`：

```yaml
default_voices:
  primary: "21m00Tcm4TlvDq8ikWAM"    # Rachel (英文)
  secondary: "AZnzlk1XvdvUeBnXmlld"  # Domi (英文)
  
chinese_voices:
  primary: "your_chinese_voice_id"
  secondary: "another_chinese_voice_id"

settings:
  stability: 0.5
  similarity_boost: 0.75
  style: 0.0
  use_speaker_boost: true
```

### 3. 测试API连接

运行语音测试工具：

```bash
python scripts/tools/elevenlabs_voice_tester.py
```

---

## 🎭 双人对话播客功能

### 功能概述

系统可以自动识别对话格式文本，生成双人对话播客音频，模拟真实的双人讨论效果。

### 支持的对话格式

- `[角色]: 内容` - 标准格式
- `【角色】: 内容` - 中文格式  
- `A: 内容` - 简化格式
- `主持人: 内容` - 角色名格式

### 配置双人对话

1. **声音配置**：在 `elevenlabs_voices.yml` 中设置不同角色的声音：

```yaml
dialogue_roles:
  主持人:
    voice_id: "21m00Tcm4TlvDq8ikWAM"  # Rachel
    settings:
      stability: 0.6
      similarity_boost: 0.8
  
  嘉宾:
    voice_id: "AZnzlk1XvdvUeBnXmlld"  # Domi
    settings:
      stability: 0.4
      similarity_boost: 0.7
```

2. **自动检测**：系统会自动识别对话格式并启用双人模式

3. **测试对话**：

```bash
python scripts/tools/elevenlabs_voice_tester.py
# 选择 "6. 双人对话测试"
```

### 使用示例

创建包含对话的文本：

```markdown
[主持人]: 欢迎来到今天的节目，我们将讨论人工智能的发展趋势。

[嘉宾]: 感谢邀请！我认为AI在教育领域的应用前景非常广阔。

[主持人]: 能具体说说有哪些应用场景吗？
```

系统会自动：
- 识别对话格式
- 为不同角色分配不同声音
- 生成连贯的双人对话音频

---

## 🔧 本地eSpeak引擎

### Ubuntu/Debian安装

```bash
sudo apt-get update
sudo apt-get install -y espeak espeak-data
```

### macOS安装

```bash
brew install espeak
```

### Windows安装

1. 下载 [eSpeak官方安装包](http://espeak.sourceforge.net/download.html)
2. 运行安装程序
3. 将安装目录添加到PATH环境变量

### 验证安装

```bash
# 英文测试
espeak "Hello World" -v en -s 150

# 中文测试
espeak "你好世界" -v zh -s 150
```

### 配置中文语音

```bash
# 下载中文语音包
sudo apt-get install espeak-data-zh

# 测试中文语音
espeak "这是中文测试" -v zh -s 120 -a 100
```

---

## 🧪 语音测试和调试

### 使用语音测试工具

```bash
python scripts/tools/elevenlabs_voice_tester.py
```

### 可用测试选项

1. **测试文本转语音** - 基础TTS功能测试
2. **列出所有可用声音** - 查看账号可用的声音
3. **获取可用TTS模型** - 检查支持的模型
4. **测试中文语音** - 专门测试中文TTS
5. **语音质量对比** - 比较不同参数设置
6. **双人对话测试** - 测试对话模式
7. **检查API配额** - 查看剩余字符数

### 调试技巧

1. **API限制检查**：
```bash
curl -X GET "https://api.elevenlabs.io/v1/user" \
  -H "Accept: application/json" \
  -H "xi-api-key: YOUR_API_KEY"
```

2. **声音ID验证**：
```bash
curl -X GET "https://api.elevenlabs.io/v1/voices" \
  -H "Accept: application/json" \
  -H "xi-api-key: YOUR_API_KEY"
```

3. **日志查看**：
```bash
tail -f .build/logs/pipeline.log | grep -i "elevenlabs"
```

---

## 🚨 故障排查

### 常见问题

#### 1. API密钥错误
```
错误: 401 Unauthorized
解决: 检查.env文件中的ELEVENLABS_API_KEY是否正确
```

#### 2. 声音ID无效
```
错误: Voice not found
解决: 运行语音测试工具获取有效的voice_id列表
```

#### 3. 配额不足
```
错误: Quota exceeded
解决: 检查API使用量，升级账号或等待配额重置
```

#### 4. 网络连接问题
```
错误: Connection timeout
解决: 检查网络连接，考虑使用代理
```

#### 5. 双人对话不生效
```
问题: 所有内容都用同一个声音
解决: 检查文本格式，确保包含角色标识符（如[主持人]:）
```

### 调试命令

```bash
# 检查Python环境
python -c "import elevenlabs; print('ElevenLabs库已安装')"

# 测试网络连接
curl -I https://api.elevenlabs.io/v1/voices

# 检查配置文件
python -c "
import yaml
with open('config/elevenlabs_voices.yml') as f:
    config = yaml.safe_load(f)
    print('配置文件加载成功')
"
```

### 获取帮助

如果问题仍然存在：

1. 查看详细日志：`.build/logs/pipeline.log`
2. 运行系统检查：`python run.py` → 选项5 → 选项3
3. 提交Issue时包含：
   - 错误信息截图
   - 相关日志内容
   - 系统环境信息

---

## 📚 参考资源

- [ElevenLabs官方文档](https://docs.elevenlabs.io/)
- [eSpeak用户指南](http://espeak.sourceforge.net/commands.html)
- [项目语音配置文件示例](../config/elevenlabs_voices_template.yml)

**最后更新**: 2025-08-03