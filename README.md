# 有心言者博客发布系统

> 🚀 自动化多平台内容发布与管理系统

[![Jekyll](https://img.shields.io/badge/Jekyll-CC0000?style=flat&logo=Jekyll&logoColor=white)](https://jekyllrb.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://python.org/)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-222222?style=flat&logo=GitHub%20Pages&logoColor=white)](https://pages.github.com/)

## ✨ 核心功能

### 🎬 智能音视频系统
- **YouTube播客生成器** - 英文视频→中文播客→博客文章自动化流程
- **响应式iframe嵌入** - 移动端友好的视频播放体验
- **unlisted隐私保护** - 自动设置非公开，保护会员专享内容
- **多平台音频支持** - 智能地区检测，国内外用户优化体验

### 🚀 多平台发布系统
- **GitHub Pages** - Jekyll静态博客，完美SEO优化
- **微信公众号** - 智能内容适配，图片自动处理
- **WordPress** - API自动发布，扩展兼容性
- **音频平台准备** - 喜马拉雅等平台集成架构

### 💎 会员服务体系
- **四级递进权益** - 从入门探索到深度个性化服务
- **内容分层保护** - 争议话题、深度分析仅向付费用户开放
- **社区价值导向** - 志同道合用户的终身学习社群
- **视野拓展内容** - 优质英文资源，增进全球认知

### 📊 数据驱动运营
- **Google Analytics 4** - 会员级别行为跟踪分析
- **用户体验监控** - 平台切换、内容互动数据
- **隐私友好配置** - IP匿名化，符合隐私保护标准

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
| **🎯 项目总览** | [功能实施总结](docs/project-completion-summary.md) | 最新功能成果和后续规划 |
| | [项目结构](docs/PROJECT_STRUCTURE.md) | 详细的目录结构说明 |
| | [开发约定](CLAUDE.md) | 项目开发规范和约定 |
| **🔧 配置指南** | [环境配置](.env.example) | 环境变量配置模板 |
| | [YouTube播客设置](docs/setup/youtube_podcast_setup.md) | YouTube播客完整配置 |
| | [TTS完整配置](docs/setup/tts_comprehensive_setup.md) | 语音系统完整配置指南 |
| | [Google OAuth设置](docs/setup/YOUTUBE_OAUTH_SETUP.md) | YouTube上传OAuth2配置 |
| **🎬 音频视频系统** | [音频平台集成规划](docs/audio-platform-integration-plan.md) | 多平台音频系统架构 |
| | [使用示例文档](docs/audio-platform-usage-example.md) | 功能使用指南和最佳实践 |
| | [喜马拉雅开发者认证](docs/ximalaya-developer-requirements.md) | 第三方平台集成准备 |
| **🔒 安全与维护** | [安全配置指南](SECURITY.md) | 项目安全最佳实践 |
| | [会员系统完整指南](docs/member-system-guide.md) | 会员管理、配置和运营指南 |
| **📋 功能指南** | [YouTube完整指南](docs/guides/YOUTUBE_COMPLETE_GUIDE.md) | YouTube功能使用说明 |
| | [开发指南](docs/DEVELOPMENT.md) | 开发环境和贡献指南 |
| | [项目路线图](docs/ROADMAP.md) | 功能规划和发展方向 |

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