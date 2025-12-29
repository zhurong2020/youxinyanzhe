# 项目结构文档

这个文档描述了有心言者博客发布系统的详细目录结构和文件组织。

## 总体架构

```
workshop/
├── 📝 内容文件
│   ├── _posts/              # Jekyll发布的文章
│   ├── _drafts/             # 草稿文件
│   └── assets/              # 静态资源（图片、音频、CSS等）
├── 🔧 核心系统
│   ├── scripts/             # Python业务逻辑
│   ├── config/              # 配置文件
│   └── run.py              # 主程序入口
├── 📚 文档和测试
│   ├── docs/               # 项目文档
│   ├── tests/              # 测试文件
│   └── README.md           # 项目说明
└── 🔨 构建和部署
    ├── .build/             # 构建临时文件
    ├── .tmp/               # 运行时临时文件
    └── venv/               # Python虚拟环境
```

## 详细目录结构

### 重构后的核心业务逻辑 (`scripts/`) - 2025-08-13

```
scripts/
├── core/                      # 核心业务逻辑层 (重构)
│   ├── processors/            # 处理器模块
│   │   ├── __init__.py
│   │   ├── ai_processor.py        # AI内容处理器
│   │   ├── image_processor.py     # 图片处理器
│   │   └── platform_processor.py # 平台发布处理器
│   ├── validators/            # 验证器模块
│   │   ├── __init__.py
│   │   ├── content_validator.py   # 内容验证器基类
│   │   ├── frontmatter_validator.py  # Front Matter验证
│   │   ├── image_validator.py     # 图片验证器
│   │   ├── quality_validator.py   # 质量验证器
│   │   └── structure_validator.py # 结构验证器
│   ├── workflows/             # 工作流引擎
│   │   ├── __init__.py
│   │   ├── content_workflow.py    # 内容处理工作流
│   │   └── integrated_workflow.py # 集成工作流
│   ├── managers/              # 管理器模块
│   │   ├── __init__.py
│   │   └── publish_manager.py     # 发布状态管理器
│   ├── __init__.py
│   ├── content_pipeline.py       # 内容处理主流程 (重构)
│   ├── wechat_publisher.py        # WeChat发布器
│   ├── youtube_podcast_generator.py  # YouTube播客生成器
│   └── fallback_podcast_generator.py # 备用播客生成器
├── cli/                       # 命令行界面层 (新增)
│   ├── __init__.py
│   └── menu_handler.py           # 菜单处理器
├── utils/                     # 通用工具层
│   ├── __init__.py
│   ├── audio_link_replacer.py     # 音频链接替换工具
│   ├── email_sender.py           # 邮件发送工具
│   ├── github_release_manager.py # GitHub Release管理
│   ├── package_creator.py        # 包创建工具
│   ├── reward_system_manager.py  # 奖励系统管理器
│   └── youtube_link_mapper.py    # YouTube链接映射
└── tools/                     # 独立工具层 (重组)
    ├── content/                   # 内容处理工具
    │   ├── format_draft.py           # 草稿格式化工具
    │   └── topic_inspiration_generator.py  # 主题灵感生成器
    ├── youtube/                   # YouTube相关工具
    │   ├── upload_single.py          # 单个视频上传
    │   ├── youtube_upload.py         # YouTube上传主工具
    │   ├── youtube_upload_tester.py  # 上传功能测试
    │   ├── youtube_video_gen.py      # 视频生成器
    │   ├── youtube_video_generator.py
    │   ├── youtube_single_upload.py
    │   └── youtube_oauth_*.py        # OAuth相关工具
    ├── oauth/                     # OAuth认证工具
    │   ├── check_oauth_status.py     # OAuth状态检查
    │   ├── check_google_oauth_fix.py
    │   ├── fix_oauth_hanging.py
    │   ├── generate_oauth_token.py   # Token生成
    │   ├── oauth_debug.py
    │   └── restore_youtube_oauth.py  # OAuth恢复
    ├── elevenlabs/                # ElevenLabs语音工具
    │   ├── elevenlabs_voice_manager.py    # 语音管理
    │   ├── elevenlabs_voice_tester.py     # 语音测试
    │   ├── elevenlabs_voice_test.py
    │   ├── elevenlabs_pro_setup.py       # Pro功能设置
    │   ├── elevenlabs_permission_check.py
    │   └── test_dual_voice_podcast.py
    ├── checks/                    # 系统检查工具
    │   └── check_github_token.py     # GitHub Token检查
    ├── testing/                   # 测试工具
    │   ├── test_reward_system.py      # 奖励系统测试
    │   ├── test_content_generation.py # 内容生成测试
    │   └── test_podcastfy_api.py      # API测试
    ├── mixed_image_manager.py         # 混合图片管理系统 (重构)
    ├── enhanced_onedrive_processor.py # 增强OneDrive处理器 (新增)
    ├── onedrive_blog_images.py        # OneDrive图床自动化系统
    ├── onedrive_image_index.py        # OneDrive图片索引管理
    ├── recover_onedrive_images.py     # OneDrive图片恢复工具 (新增)
    ├── manage_uploaded_images.py      # 已上传图片管理工具 (新增)
    ├── cleanup_onedrive_*.py          # OneDrive清理工具
    ├── onedrive_date_downloader.py    # OneDrive日期下载器
    ├── restore_local_image_links.py   # 本地图片链接恢复
    ├── create_valid_token.py          # Token创建工具
    ├── generate_test_codes.py         # 测试代码生成器
    ├── patched_podcastfy.py           # 修补版Podcastfy
    ├── regenerate_youtube_article.py  # YouTube文章重新生成
    ├── simple_test.py                # 简单测试工具
    ├── verify_gemini_model.py         # Gemini模型验证
    ├── wechat_api_debug.py            # WeChat API调试
    ├── wechat_system_verify.py        # WeChat系统验证
    └── debug_podcastfy.py             # Podcastfy调试工具
```

### 配置管理 (`config/`)

```
config/
├── pipeline_config.yml     # 主流程配置
├── elevenlabs_voices.yml   # ElevenLabs语音配置
├── elevenlabs_voices_pro.yml  # Pro版语音配置
├── youtube_categories.yml  # YouTube分类映射
├── member_tiers.yml        # 会员等级配置
├── onedrive_config.json    # OneDrive图床配置
├── onedrive_tokens.json    # OneDrive访问令牌 (运行时生成)
├── image_config.json       # 图片处理配置
└── azure_app_info.md       # Azure应用注册信息
```

### 文档系统 (`docs/`)

```
docs/
├── setup/                  # 安装配置指南
│   ├── youtube_podcast_setup.md
│   ├── tts_comprehensive_setup.md
│   └── YOUTUBE_OAUTH_SETUP.md
├── guides/                 # 使用指南
│   ├── YOUTUBE_COMPLETE_GUIDE.md
│   └── member-system-guide.md
├── TECHNICAL_ARCHITECTURE.md  # 技术架构
├── CHANGELOG_DETAILED.md      # 详细更新历史
├── ONEDRIVE_BLOG_IMAGE_SYSTEM.md  # OneDrive图床系统文档
├── IMAGE_MANAGEMENT_WORKFLOW.md   # 图片管理工作流程
├── ONEDRIVE_SETUP_GUIDE.md        # OneDrive设置指南
└── PROJECT_STRUCTURE.md       # 项目结构文档
```

### 内容和资源

```
_posts/                     # 已发布的Jekyll文章
_drafts/                    # 草稿文件
  ├── archived/               # 已归档的草稿
  └── [date]-[title].md       # 待发布草稿

assets/                     # 静态资源
├── images/                   # 图片资源
│   ├── posts/[year]/[month]/   # 按日期组织的文章图片
│   └── default-teaser.jpg      # 默认预览图
├── audio/                    # 音频文件
│   └── podcasts/              # 播客音频
├── css/                      # 样式文件
├── js/                       # JavaScript文件
└── videos/                   # 视频文件（临时）
```

### 临时和构建文件

```
.build/                     # 构建相关文件
├── logs/                     # 构建日志
└── cache/                    # 构建缓存

.tmp/                       # 运行时临时文件
├── output/                   # 处理结果输出
│   ├── videos/                 # 生成的视频文件
│   └── wechat_guides/          # 微信发布指导
├── member_data/              # 会员数据临时文件
└── admin_data/               # 管理数据临时文件
```

## 文件命名约定

### 文章文件
- **格式**: `YYYY-MM-DD-title-slug.md`
- **示例**: `2025-08-07-deep-learning-investment-applications.md`

### 配置文件
- **格式**: `[功能]_config.yml` 或 `[组件]_[类型].yml`
- **示例**: `pipeline_config.yml`, `elevenlabs_voices.yml`

### 工具脚本
- **格式**: `[功能]_[动作].py`
- **示例**: `youtube_upload.py`, `format_draft.py`

### 文档文件
- **指南**: `[主题]_GUIDE.md` (全大写)
- **配置**: `[功能]_setup.md` (小写)
- **架构**: `[类型]_ARCHITECTURE.md` (全大写)

## 重要文件说明

| 文件 | 作用 | 重要性 |
|------|------|--------|
| `run.py` | 系统主入口，重构后的9项精简菜单界面 | ⭐⭐⭐⭐⭐ |
| `scripts/core/content_pipeline.py` | 重构后的内容处理核心流程 | ⭐⭐⭐⭐⭐ |
| `scripts/core/workflows/content_workflow.py` | 工作流引擎核心 | ⭐⭐⭐⭐⭐ |
| `scripts/core/processors/ai_processor.py` | AI内容处理器 | ⭐⭐⭐⭐ |
| `scripts/core/validators/content_validator.py` | 内容验证器基类 | ⭐⭐⭐⭐ |
| `scripts/cli/menu_handler.py` | 菜单处理器 | ⭐⭐⭐⭐ |
| `scripts/core/youtube_podcast_generator.py` | YouTube播客生成核心 | ⭐⭐⭐⭐ |
| `config/pipeline_config.yml` | 主要系统配置 | ⭐⭐⭐⭐ |
| `CLAUDE.md` | 项目开发约定和规范 | ⭐⭐⭐⭐ |
| `.env` | 环境变量和敏感配置 | ⭐⭐⭐⭐ |

## 安全文件管理

以下文件包含敏感信息，已正确排除在版本控制外：

```
# 敏感配置文件（已在.gitignore中排除）
.env                        # 环境变量
config/*_credentials.json   # OAuth凭据
config/*_token.json         # API tokens
.build/logs/*.log          # 可能包含敏感信息的日志
.tmp/                      # 临时文件可能包含处理数据
```

## 维护建议

1. **定期清理**: 定期清理 `.tmp/` 和 `.build/` 目录中的旧文件
2. **日志轮转**: 实施日志轮转机制，避免日志文件过大
3. **依赖更新**: 定期更新 `requirements.txt` 中的依赖版本
4. **文档同步**: 重要功能变更时及时更新相关文档

## 重构特性 (2025-08-13)

### 架构优化
- **分层架构**: 明确的core/cli/utils/tools分层
- **模块化设计**: processors、validators、workflows、managers模块
- **工作流引擎**: 抽象的工作流处理框架
- **测试覆盖**: 175个测试用例，核心模块100%覆盖

### 新增功能模块
- **验证器系统**: 模块化内容验证和质量保证
- **工作流引擎**: 支持步骤化处理和错误恢复
- **处理器架构**: 统一的内容处理接口
- **增强图片管理**: 完整的OneDrive图片管理和恢复系统

## 扩展指南

在添加新功能时：

1. **核心业务逻辑** → `scripts/core/processors/` 或 `scripts/core/workflows/`
2. **验证规则** → `scripts/core/validators/`
3. **工作流步骤** → `scripts/core/workflows/`
4. **平台发布** → `scripts/core/processors/platform_processor.py`
5. **独立工具** → `scripts/tools/[category]/`
6. **配置文件** → `config/`
7. **文档** → `docs/`
8. **测试** → `tests/test_*.py`

### 重构后的开发原则
- **单一职责**: 每个模块负责特定功能
- **依赖注入**: 通过参数传递依赖，便于测试
- **错误处理**: 统一的错误处理和恢复机制
- **可扩展性**: 通过抽象基类支持功能扩展

这种重构后的组织结构大幅提升了代码的可维护性、可扩展性和测试覆盖率。