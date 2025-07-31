# ElevenLabs声音测试和双人对话配置指南

## 概述

这个指南将帮助你测试ElevenLabs账户中的可用声音，并配置双人对话播客功能。

## 前置要求

### 1. 安装依赖
```bash
pip install elevenlabs pydub
```

### 2. 配置API密钥
在 `.env` 文件中添加：
```env
ELEVENLABS_API_KEY=your_api_key_here
```

## 使用步骤

### 1. 运行声音测试脚本

```bash
cd /home/wuxia/projects/youxinyanzhe
python scripts/tools/elevenlabs_voice_tester.py
```

### 2. 测试流程说明

#### 选项1: 列出所有可用声音
- 显示你的ElevenLabs账户中所有可用声音
- 包括声音ID、名称、类别等信息
- 结果保存到 `tests/elevenlabs_voice_tests/available_voices.json`

#### 选项2: 批量测试声音质量
- 自动测试多个声音的生成效果
- 生成测试音频文件供你试听
- 返回成功测试的声音ID列表

#### 选项3: 创建双人对话播客测试
- 使用两个不同声音生成对话播客
- 自动合并音频片段
- 演示双人播客效果

#### 选项4: 检查对话API支持
- 检查ElevenLabs是否支持原生对话API
- 目前大多数情况下需要使用分段合成

#### 选项5: 生成声音配置文件
- 基于测试结果生成配置文件
- 保存到 `config/elevenlabs_voices.yml`

#### 选项6: 完整测试流程
- 自动执行上述所有步骤
- 一键完成全部测试和配置

## 测试结果解读

### 声音质量测试
- ✅ 表示该声音可正常使用
- ❌ 表示该声音不可用或有问题
- 测试音频保存在 `tests/elevenlabs_voice_tests/` 目录

### 声音分类
- **premade**: ElevenLabs官方预设声音
- **cloned**: 用户克隆的声音
- **generated**: AI生成的声音

## 配置文件说明

### 基本结构
```yaml
elevenlabs_voices:
  voice_combinations:
    chinese_podcast:  # 组合名称
      speaker_a:      # 说话者A
        voice_id: "21m00Tcm4TlvDq8ikWAM"
        name: "Rachel"
        role: "主持人"
        settings:
          stability: 0.4
          similarity_boost: 0.8
          style: 0.6
      speaker_b:      # 说话者B
        voice_id: "TxGEqnHWrfWFTfGW9XjX"  
        name: "Josh"
        role: "嘉宾"
        settings:
          stability: 0.35
          similarity_boost: 0.85
          style: 0.5
```

### 参数调优建议

#### stability (稳定性)
- **0.0-0.3**: 声音变化较大，更有表现力但可能不稳定
- **0.4-0.6**: 平衡的选择，适合大多数情况
- **0.7-1.0**: 非常稳定，但可能听起来较机械

#### similarity_boost (相似度增强)
- **0.0-0.5**: 声音变化较大，可能偏离原始声音
- **0.6-0.8**: 推荐范围，保持声音特征
- **0.9-1.0**: 最接近原始声音，但可能缺乏变化

#### style (风格强度)
- **0.0-0.3**: 较平淡，适合正式内容
- **0.4-0.6**: 中等表现力，适合播客
- **0.7-1.0**: 高表现力，适合戏剧性内容

## 双人对话实现方案

### 方案A: 分段生成 + 音频拼接 (推荐)
```python
# 1. 解析对话脚本，分离不同说话者
dialogue_segments = parse_script(script)

# 2. 为每个片段生成音频
for speaker, text in dialogue_segments:
    audio = generate_audio(voice_id, text)
    
# 3. 拼接所有音频片段
final_audio = merge_segments(audio_segments)
```

### 方案B: 实时切换 (如果API支持)
```python
# 某些ElevenLabs版本可能支持
conversation_audio = generate_conversation(
    speakers=[voice_a, voice_b],
    dialogue=parsed_script
)
```

## 常见问题

### Q: 为什么某些声音测试失败？
A: 可能的原因：
- 声音ID不存在或已被删除
- API权限不足
- 网络连接问题
- API配额已用完

### Q: 如何选择最佳的声音组合？
A: 建议考虑：
- **性别差异**: 一男一女区分度最高
- **音调差异**: 选择音调明显不同的声音
- **语言适配**: 确保声音支持目标语言
- **角色匹配**: 根据播客角色选择合适的声音特征

### Q: 双人对话音频如何优化？
A: 优化技巧：
- 在对话间添加适当停顿 (0.5-1秒)
- 为不同角色设置不同的语音参数
- 使用音频后处理添加背景音乐
- 调整音量平衡

### Q: API调用频率限制？
A: 注意事项：
- 每次API调用间隔0.5-1秒
- 监控API配额使用情况
- 批量测试时分批进行
- 保存测试结果避免重复调用

## 集成到现有系统

### 1. 更新YouTube播客生成器
将测试通过的声音配置集成到 `youtube_podcast_generator.py`

### 2. 修改音频生成逻辑
支持双声音模式和单声音模式切换

### 3. 配置文件加载
从 `config/elevenlabs_voices.yml` 读取声音配置

## 下一步

1. 运行测试脚本，获取你的可用声音
2. 试听测试音频，选择最佳组合
3. 更新配置文件
4. 集成到播客生成流程
5. 测试完整的双人对话播客生成

---

**提示**: 声音效果很主观，建议多试听几种组合，选择最适合你的播客风格的声音配置。