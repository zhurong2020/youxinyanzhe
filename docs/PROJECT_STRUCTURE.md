# 项目目录结构

本项目采用标准的软件工程最佳实践，目录结构清晰分离关注点。

## 📁 根目录文件

```
youxinyanzhe/
├── README.md                 # 项目主要说明文档
├── CLAUDE.md                 # Claude Code 项目约定和指导文档
├── requirements.txt          # Python依赖清单
├── pytest.ini              # 测试配置
├── run.py                   # 主程序入口
├── _config.yml              # Jekyll站点配置
├── Gemfile                  # Ruby依赖（Jekyll）
├── Gemfile.lock            # Ruby依赖锁定版本
└── index.md                # 站点首页内容
```

## 📁 核心目录结构

### 🛠️ 开发和构建
```
├── scripts/                 # 核心业务逻辑
│   ├── core/               # 核心功能模块
│   │   ├── content_pipeline.py        # 内容处理管道
│   │   ├── wechat_publisher.py        # 微信发布器
│   │   └── youtube_podcast_generator.py # YouTube播客生成器
│   ├── utils/              # 工具和辅助函数
│   └── tools/              # 独立工具和调试脚本
├── tests/                   # 测试套件
├── config/                  # 配置文件
├── docs/                    # 项目文档
└── .build/                  # 构建输出（.gitignore）
```

### 📝 内容管理
```
├── _posts/                  # 发布的文章
├── _drafts/                 # 草稿和内容管理
│   ├── archived/           # 已归档文章
│   └── musk-empire/        # 系列文章规划
├── _pages/                  # 静态页面
├── _includes/              # Jekyll组件
└── _data/                  # 数据文件
```

### 🎨 资源文件
```
└── assets/                  # 静态资源
    ├── css/                # 样式文件
    ├── js/                 # JavaScript文件
    ├── images/             # 图片资源
    │   ├── posts/          # 文章配图（按年月分组）
    │   ├── homepage/       # 主页图片
    │   └── favicon/        # 网站图标
    ├── audio/              # 音频文件
    └── videos/             # 视频文件（如需要）
```

### 📚 文档系统
```
└── docs/                    # 完整项目文档
    ├── README.md           # 文档总览
    ├── PROJECT_STRUCTURE.md # 本文件
    ├── DEVELOPMENT.md      # 开发指南
    ├── setup/              # 安装配置指南
    │   ├── gemini_setup.md
    │   └── tts_setup.md
    ├── guides/             # 使用指南
    │   ├── elevenlabs_integration_guide.md
    │   └── youtube_tts_upgrade_guide.md
    └── changelog/          # 变更日志
        ├── gemini_model_update_summary.md
        ├── youtube_issues_fixes_summary.md
        ├── youtube_fixes_summary.md
        ├── text_length_limit_removal.md
        └── youtube_comprehensive_fixes_2025-07-29.md
```

### 🔧 运行时目录
```
├── .build/                  # 构建和运行时文件（Git忽略）
│   ├── logs/               # 应用日志
│   └── htmlcov/            # 测试覆盖率报告
├── .tmp/                    # 临时文件（Git忽略）
│   ├── output/             # 生成的输出文件
│   │   ├── wechat_guides/  # 微信发布指导文件
│   │   ├── wechat_image_cache/ # 微信图片缓存
│   │   └── packages/       # 生成的内容包
├── logs/                    # 主日志目录（Git忽略）
└── venv/                    # Python虚拟环境（Git忽略）
```

## 🎯 设计原则

### 1. 分离关注点
- **核心业务逻辑**：`scripts/core/`
- **工具和辅助**：`scripts/utils/` 和 `scripts/tools/`
- **配置管理**：`config/`
- **测试代码**：`tests/`

### 2. 清晰的文档层次
- **用户文档**：根目录的 README.md
- **开发文档**：`docs/` 目录按类型组织
- **API文档**：代码内docstring

### 3. 资源组织
- **按时间组织**：文章图片按年月分组
- **按功能组织**：CSS、JS、音频分别管理
- **版本控制友好**：大文件和临时文件排除在外

### 4. 运行时安全
- **敏感信息**：`.env` 文件被Git忽略
- **临时文件**：`.build/` 和 `.tmp/` 目录隔离
- **日志分离**：统一的日志目录管理

## 🔄 迁移说明

此结构整理完成了以下改进：

1. **文档整理**：根目录的临时文档移动到 `docs/` 相应子目录
2. **依赖清理**：合并重复的requirements文件
3. **忽略规则**：修正 `.gitignore` 确保敏感文件安全
4. **标准化**：符合现代Python项目和Jekyll站点的最佳实践

## 🚀 后续扩展

目录结构为后续功能扩展预留了空间：
- 新的内容处理器可添加到 `scripts/core/`
- 新的工具脚本放在 `scripts/tools/`
- 新的配置文件放在 `config/`
- 文档更新维护在 `docs/` 相应分类中

---

*最后更新：2025-07-30*