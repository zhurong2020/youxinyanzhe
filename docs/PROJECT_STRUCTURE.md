# 项目结构文档

这个文档描述了有心言者博客发布系统的详细目录结构和文件组织。

## 总体架构

```
youxinyanzhe/
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

### 核心业务逻辑 (`scripts/`)

```
scripts/
├── core/                   # 核心业务逻辑
│   ├── content_pipeline.py    # 内容处理主流程
│   ├── youtube_podcast_generator.py  # YouTube播客生成器
│   ├── member_system.py       # 会员系统管理
│   └── reward_manager.py      # 内容变现管理
├── utils/                  # 工具和辅助函数  
│   ├── github_utils.py        # GitHub API工具
│   ├── wechat_utils.py        # 微信发布工具
│   ├── reward_system_manager.py  # 奖励系统管理器
│   └── security_utils.py      # 安全工具
└── tools/                  # 独立工具（已重新组织）
    ├── content/               # 内容处理工具
    │   └── format_draft.py       # 手工草稿格式化工具
    ├── youtube/               # YouTube相关工具
    │   ├── upload_single.py      # 单个视频上传
    │   ├── youtube_upload.py     # YouTube上传主工具
    │   ├── youtube_upload_tester.py  # 上传功能测试
    │   └── youtube_video_generator.py  # 视频生成器
    ├── oauth/                 # OAuth认证工具
    │   ├── check_oauth_status.py  # OAuth状态检查
    │   ├── generate_oauth_token.py  # Token生成
    │   └── restore_youtube_oauth.py  # OAuth恢复
    ├── elevenlabs/            # ElevenLabs语音工具
    │   ├── elevenlabs_voice_manager.py  # 语音管理
    │   ├── elevenlabs_voice_tester.py   # 语音测试
    │   └── elevenlabs_pro_setup.py     # Pro功能设置
    ├── checks/                # 系统检查工具
    │   └── check_github_token.py  # GitHub Token检查
    └── testing/               # 测试工具
        ├── test_reward_system.py   # 奖励系统测试
        ├── test_content_generation.py  # 内容生成测试
        └── test_podcastfy_api.py    # API测试
```

### 配置管理 (`config/`)

```
config/
├── pipeline_config.yml     # 主流程配置
├── elevenlabs_voices.yml   # ElevenLabs语音配置
├── elevenlabs_voices_pro.yml  # Pro版语音配置
├── youtube_categories.yml  # YouTube分类映射
└── member_tiers.yml        # 会员等级配置
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
├── DEVELOPMENT.md             # 开发指南
└── ROADMAP.md                 # 路线图
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
| `run.py` | 系统主入口，提供交互式菜单界面 | ⭐⭐⭐⭐⭐ |
| `scripts/core/content_pipeline.py` | 内容处理核心流程 | ⭐⭐⭐⭐⭐ |
| `scripts/core/youtube_podcast_generator.py` | YouTube播客生成核心 | ⭐⭐⭐⭐⭐ |
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

## 扩展指南

在添加新功能时：

1. **核心逻辑** → `scripts/core/`
2. **工具脚本** → `scripts/tools/[category]/`
3. **配置文件** → `config/`
4. **文档** → `docs/guides/` 或 `docs/setup/`
5. **测试** → `scripts/tools/testing/` 或 `tests/`

这种组织结构确保了代码的可维护性、可扩展性和团队协作效率。