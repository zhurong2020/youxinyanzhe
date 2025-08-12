# 有心工坊项目文档
**YouXin Workshop Documentation**

这是有心工坊 - 为有心人打造的数字创作平台，基于Jekyll的自动化博客发布系统，专注于多平台内容分发、图片管理和会员服务。

## 📖 文档导航

### 核心文档
- **[开发约定](../CLAUDE.md)** - 核心开发规范和当前工作重点
- **[技术架构](TECHNICAL_ARCHITECTURE.md)** - 详细技术架构和关键决策
- **[更新历史](CHANGELOG_DETAILED.md)** - 完整的功能实现历史

### 专门指南
- **[会员系统指南](member-system-guide.md)** - 多级会员验证系统使用说明
- **[音频平台集成计划](audio-platform-integration-plan.md)** - 喜马拉雅等平台集成规划
- **[ElevenLabs Pro指南](elevenlabs_pro_guide.md)** - 高级TTS功能使用指南

### 设置指南
- **[setup/](setup/)** - 各种功能的详细设置指南
  - YouTube OAuth设置
  - Gemini API配置
  - TTS综合设置指南
- **[guides/](guides/)** - YouTube相关完整指南

### 规划文档
- **[音频平台集成计划](audio-platform-integration-plan.md)** - 多音频平台集成规划
- **[喜马拉雅开发要求](ximalaya-developer-requirements.md)** - 平台集成准备

---

## 项目特性概览

### 🎥 YouTube播客生成器
- 英转中播客: 将英文YouTube视频转换为中文学习播客
- 多语言支持: 中英日韩四种语言TTS
- OAuth认证: YouTube API的OAuth和API Key双重认证
- 配额管理: ElevenLabs API配额实时监控和预警

### 💰 多级会员系统
- 四级体系: 体验、月度、季度、年度服务
- 访问码验证: 动态会员级别内容过滤
- 自动邮件: 会员资料和访问码自动化处理
- 内容分层: 争议性内容仅向付费用户开放

### 📤 多平台发布
- Jekyll + GitHub Pages: 全自动化静态站点生成和部署
- WeChat公众号: 完整的内容处理和发布指导工作流
- 发布状态管理: YAML文件跟踪多平台发布状态

### 🎧 智能音频平台
- 地理位置检测: 基于用户位置智能推荐音频平台
- 响应式设计: 16:9宽高比视频容器，移动端优化
- 隐私保护: YouTube视频自动unlisted模式，会员专享

### 📈 数据分析
- Google Analytics 4: 会员级别行为跟踪
- 平台切换监控和内容交互分析
- 隐私友好的IP匿名化配置

### 📝 内容管理
- 四大分类体系: 认知升级、技术赋能、全球视野、投资理财
- Gemini AI内容优化和自动分类
- 投资文章自动添加风险声明

---

## 快速开始

1. **环境设置**: 参考 [setup/](setup/) 目录中的相关指南
2. **开发约定**: 阅读 [../CLAUDE.md](../CLAUDE.md) 了解核心约定
3. **技术架构**: 查看 [TECHNICAL_ARCHITECTURE.md](TECHNICAL_ARCHITECTURE.md) 理解系统设计

## 获取帮助

- 🐛 **问题反馈**: [GitHub Issues](https://github.com/wuxia/youxinyanzhe/issues)
- 📚 **功能文档**: 查看对应的专门指南
- 🔧 **技术问题**: 参考技术架构文档

---

**最后更新**: 2025-08-06  
**维护者**: 有心言者团队