# 有心言者博客发布系统

> 🚀 自动化多平台内容发布与管理系统

[![Jekyll](https://img.shields.io/badge/Jekyll-CC0000?style=flat&logo=Jekyll&logoColor=white)](https://jekyllrb.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-222222?style=flat&logo=GitHub%20Pages&logoColor=white)](https://pages.github.com/)

## ✨ 核心功能

- 📝 **智能内容处理** - AI驱动的内容生成与优化
- 🚀 **多平台发布** - GitHub Pages、微信公众号、WordPress
- 🎧 **高质量音频生成** - ElevenLabs双人对话播客，媲美NotebookLM
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

## 📋 系统依赖

### 必需依赖
- **Python 3.8+** - 核心运行环境
- **pip packages** - 详见 `requirements.txt`

### 可选依赖（推荐安装）
- **FFmpeg** - 高性能音视频处理
  - **Windows**: 下载 [FFmpeg官网](https://ffmpeg.org/download.html#build-windows)
  - **macOS**: `brew install ffmpeg`
  - **Linux**: `sudo apt install ffmpeg` 或 `sudo yum install ffmpeg`

> 💡 **智能降级策略**: 如果未安装FFmpeg，系统将自动使用MoviePy作为备用方案，确保所有功能正常运行。

## 📚 完整文档

| 文档类型 | 文档 | 描述 |
|---------|------|------|
| **核心文档** | [详细说明](docs/README.md) | 完整的功能介绍和使用指南 |
| | [项目结构](docs/PROJECT_STRUCTURE.md) | 详细的目录结构说明 |
| | [开发指南](docs/DEVELOPMENT.md) | 开发环境和贡献指南 |
| **配置指南** | [Gemini配置](docs/setup/gemini_setup.md) | AI模型配置说明 |
| | [TTS完整配置](docs/setup/tts_comprehensive_setup.md) | 语音系统完整配置指南 |
| | [YouTube播客设置](docs/setup/youtube_podcast_setup.md) | YouTube播客完整配置 |
| | [YouTube OAuth设置](docs/setup/YOUTUBE_OAUTH_SETUP.md) | YouTube上传OAuth2配置 |
| | [Google OAuth修复](docs/setup/GOOGLE_OAUTH_VERIFICATION_FIX.md) | OAuth验证问题解决方案 |
| **功能指南** | [YouTube上传完整指南](docs/guides/YOUTUBE_COMPLETE_GUIDE.md) | YouTube上传功能完整指南 |
| | [YouTube上传解决方案](docs/guides/YOUTUBE_SOLUTIONS.md) | 常见问题和解决方案 |
| **系统文档** |
| | [变现系统](docs/REWARD_SYSTEM.md) | 内容变现功能详解 |
| | [项目路线图](docs/ROADMAP.md) | 功能规划和发展方向 |
| | [更新日志](docs/CHANGELOG.md) | 版本更新和变更记录 |

## 🏗️ 项目结构

```
youxinyanzhe/
├── 📁 _posts/          # Jekyll文章
├── 📁 assets/          # 静态资源(图片、音频、CSS)
├── 📁 scripts/         # 核心业务脚本
│   ├── 📁 core/        # 核心业务逻辑
│   ├── 📁 utils/       # 工具和辅助函数
│   └── 📁 tools/       # 独立工具和测试脚本
├── 📁 config/          # 配置文件
├── 📁 docs/            # 项目文档
│   ├── 📁 setup/       # 安装配置指南
│   └── 📁 guides/      # 功能使用指南
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