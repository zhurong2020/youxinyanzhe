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
- **OneDrive图床自动化** - 完整的图片托管工作流，从本地创作到云端发布
- **微信公众号** - 智能内容适配，图片自动处理
- **WordPress** - API自动发布，扩展兼容性
- **音频平台准备** - 喜马拉雅等平台集成架构

### ✏️ 智能内容处理
- **OneDrive图片管理** - 自动上传、链接替换、本地清理的完整图片工作流
- **图片索引系统** - 智能去重、多维查询、完整元数据追踪
- **手工草稿格式化** - 智能分析手工内容，自动分类到四大体系
- **Jekyll规范化** - 自动生成front matter、标签、摘要
- **批量处理能力** - 支持单个文件和目录批量格式化
- **一站式工作流** - 从手工创作到正式发布的完整流程

### 💡 AI驱动的创作灵感
- **Gemini联网搜索** - 获取最新权威英文资讯和趋势分析
- **权威来源筛选** - 智能识别Reuters、Bloomberg、Nature等高可信媒体
- **结构化灵感报告** - 自动生成包含洞察和创作角度的详细报告
- **草稿自动生成** - 基于搜索结果一键创建文章框架

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
| | [技术架构文档](docs/TECHNICAL_ARCHITECTURE.md) | 详细的技术架构和设计决策 |
| | [项目结构](docs/PROJECT_STRUCTURE.md) | 详细的目录结构说明 |
| | [开发约定](CLAUDE.md) | 项目开发规范和约定 |
| **🔧 配置指南** | [OneDrive图片工作流程](docs/IMAGE_MANAGEMENT_WORKFLOW.md) | 完整的图片管理自动化流程 |
| | [环境配置](.env.example) | 环境变量配置模板 |
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
├── 📁 _posts/          # Jekyll发布文章
├── 📁 _drafts/         # 草稿文件
├── 📁 _data/           # Jekyll数据文件(图片索引等)
├── 📁 assets/          # 静态资源(图片、音频、CSS)
├── 📁 scripts/         # 核心业务脚本
│   ├── 📁 core/        # 核心业务逻辑
│   ├── 📁 utils/       # 工具和辅助函数
│   └── 📁 tools/       # 独立工具和测试脚本
│       ├── onedrive_blog_images.py    # OneDrive图床自动化
│       └── onedrive_image_index.py    # 图片索引管理
├── 📁 config/          # 配置文件
│   └── onedrive_config.json           # OneDrive图床配置
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