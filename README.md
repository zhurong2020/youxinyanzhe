# 有心言者博客发布系统

> 🚀 自动化多平台内容发布与管理系统

[![Jekyll](https://img.shields.io/badge/Jekyll-CC0000?style=flat&logo=Jekyll&logoColor=white)](https://jekyllrb.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-222222?style=flat&logo=GitHub%20Pages&logoColor=white)](https://pages.github.com/)

## ✨ 核心功能

- 📝 **智能内容处理** - AI驱动的内容生成与优化
- 🚀 **多平台发布** - GitHub Pages、微信公众号、WordPress
- 🎧 **音频生成** - 自动创建文章播客版本
- 🎬 **YouTube播客生成器** - 将英文YouTube视频转换为中文学习播客
- 📊 **发布状态管理** - 跟踪多平台发布状态
- 💰 **内容变现** - 集成打赏和内容付费系统

## 🚀 快速开始

```bash
# 克隆项目
git clone https://github.com/zhurong2020/youxinyanzhe.git
cd youxinyanzhe

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（复制并编辑.env文件）
cp .env.example .env

# 启动发布系统
python run.py
```

## 📚 完整文档

| 文档类型 | 文档 | 描述 |
|---------|------|------|
| **核心文档** | [详细说明](docs/README.md) | 完整的功能介绍和使用指南 |
| | [项目结构](docs/PROJECT_STRUCTURE.md) | 详细的目录结构说明 |
| | [开发指南](docs/DEVELOPMENT.md) | 开发环境和贡献指南 |
| **配置指南** | [Gemini配置](docs/setup/gemini_setup.md) | AI模型配置说明 |
| | [TTS设置](docs/setup/tts_setup.md) | 文本转语音配置 |
| **功能指南** | [ElevenLabs集成](docs/guides/elevenlabs_integration_guide.md) | 高质量语音合成 |
| | [YouTube TTS升级](docs/guides/youtube_tts_upgrade_guide.md) | YouTube播客功能 |
| **系统文档** | [集成指南](docs/INTEGRATION_GUIDE.md) | 系统集成和配置说明 |
| | [变现系统](docs/REWARD_SYSTEM.md) | 内容变现功能详解 |
| | [项目路线图](docs/ROADMAP.md) | 功能规划和发展方向 |

## 🏗️ 项目结构

```
youxinyanzhe/
├── 📁 _posts/          # Jekyll文章
├── 📁 assets/          # 静态资源(图片、音频、CSS)
├── 📁 scripts/         # 核心业务脚本
├── 📁 config/          # 配置文件
├── 📁 docs/            # 项目文档
├── 📁 tests/           # 测试文件
├── 📁 .build/          # 构建和运行时文件
└── 📁 .tmp/            # 临时文件和输出
```

## 🤝 贡献

欢迎提交Issue和Pull Request！请查看[开发指南](docs/DEVELOPMENT.md)了解详细信息。

## 📄 许可证

本项目采用MIT许可证 - 查看[LICENSE](LICENSE)文件了解详情。

---

**🌟 如果这个项目对您有帮助，请给个Star支持一下！**