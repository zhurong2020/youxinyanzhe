# 有心言者博客内容处理工具

一个用于处理博客内容的自动化工具集,支持图片处理、内容生成和多平台发布。

## 功能特性

- 📝 智能内容处理
  - 使用 Google Gemini AI 进行内容生成和优化
  - 自动润色和格式化
  - 支持多种内容模板和条件显示
  - 投资理财文章自动添加风险声明

- 🚀 多平台发布系统
  - **GitHub Pages**: 完整的Jekyll网站发布
  - **WordPress**: 自动发布到WordPress站点
  - **微信公众号**: 智能内容转换和发布指导
    - Markdown到微信HTML自动转换
    - OneDrive图片自动上传到微信服务器
    - AI驱动的移动端排版优化
    - 生成发布指导文件，支持手动发布
    - **注意**: 由于API权限限制，需要手动在微信后台创建文章

- 📊 发布状态管理
  - 跟踪文章在各平台的发布状态
  - 支持已发布文章的重新发布到其他平台
  - 防止重复发布到同一平台
  - 微信发布指导文件保存(`_output/wechat_guides/`)

## 项目结构

```
youxinyanzhe/
├── assets/                 # 静态资源
│   ├── css/               # 样式文件
│   ├── js/                # JavaScript文件  
│   └── images/            # 图片资源
│       ├── favicon/       # 网站图标
│       └── posts/         # 文章图片
├── scripts/                # 核心功能模块
│   ├── __init__.py
│   ├── content_pipeline.py # 内容处理流水线(主流程)
│   ├── update_post.py     # 文章更新工具
│   └── wechat_publisher.py # 微信发布器(草稿保存)
├── tests/                  # 测试代码
│   ├── __init__.py
│   ├── conftest.py        # 测试配置和fixtures
│   ├── run_tests.py       # 测试运行器
│   ├── test_*.py          # 各功能测试文件
│   └── test_wechat_draft.py # 微信功能测试
├── config/                 # 配置文件
│   ├── pipeline_config.yml    # 主配置
│   ├── gemini_config.yml      # AI模型配置
│   ├── platforms.yml         # 平台发布配置
│   ├── post_templates.yml    # 文章模板(支持条件显示)
│   └── test_config.yml        # 测试配置
├── _drafts/               # 文章草稿
│   ├── .publishing/       # 发布状态管理(*.yml)
│   └── archived/          # 已处理草稿归档
├── _posts/                # 已发布文章
├── _pages/                # 静态页面
├── _includes/             # Jekyll包含文件
├── _output/               # 输出文件(自动生成)
│   ├── wechat_guides/     # 微信发布指导文件
│   └── wechat_image_cache/ # 微信图片缓存
├── .env                   # 环境变量(包含API密钥)
├── .env.example          # 环境变量示例
├── CLAUDE.md             # Claude Code协作约定
├── run.py                # 主启动脚本
└── _config.yml            # Jekyll配置
```

## 配置说明

### 核心配置文件
- `_config.yml`: Jekyll 站点配置
- `config/pipeline_config.yml`: 内容处理流程配置
- `config/gemini_config.yml`: AI 内容生成配置
- `config/post_templates.yml`: 文章模板配置(支持投资文章风险声明)
- `.env`: 环境变量(API密钥等敏感信息)

### 环境变量配置 (.env)
```bash
# AI配置
GEMINI_API_KEY=your_gemini_api_key

# 微信公众号配置
WECHAT_APPID=your_wechat_appid
WECHAT_APPSECRET=your_wechat_appsecret

# WordPress配置
WP_API_URL=your_wordpress_site/wp-json/wp/v2
WP_USERNAME=your_wp_username
WP_PASSWORD=your_wp_password

# GitHub配置
GITHUB_TOKEN=your_github_token
GITHUB_USERNAME=your_username
GITHUB_REPO=your_repo_name
```

### 微信公众号配置要求
1. 在微信公众号后台设置IP白名单
2. 获取AppID和AppSecret
3. **注意**: 由于API权限限制，系统生成发布指导文件供手动使用

## 内容处理流程

### 1. 文章创建和处理
- **新建草稿**: 在`_drafts/`目录创建文章
- **AI 润色**: 使用Gemini AI优化内容质量
- **内容转换**: 根据目标平台自动调整格式
- **条件显示**: 投资理财文章自动添加风险声明

### 2. 多平台发布
- **GitHub Pages**: 完整Jekyll格式，包含所有元数据和页脚
- **微信公众号**: 
  - 移除所有超链接，添加"阅读原文"引导
  - 图片自动上传到微信服务器
  - AI优化移动端排版
  - 生成发布指导文件，需要手动在微信后台创建文章
- **WordPress**: API自动发布

### 3. 发布状态管理
- **状态跟踪**: `_drafts/.publishing/*.yml`记录各平台发布状态
- **重新发布**: 支持已发布文章发布到其他平台
- **防重复**: 自动过滤已发布的平台选项
- **发布指导**: 微信版本保存到`_output/wechat_guides/`



## 推荐图片尺寸

为确保网站各处图片显示效果一致且美观，建议使用以下尺寸规范：

1. 上方频道图片（feature_row）
   - 尺寸：600px宽 × 400px高
   - 格式：JPEG或WebP（质量75%）
   - URL参数：`?format=auto&width=600&quality=75`
   - 用途：主页上方的三个主要频道展示

2. "最新文章"区块头图
   - 尺寸：600px宽 × 350px高
   - 格式：JPEG或WebP（质量75%）
   - URL参数：`?format=auto&width=600&quality=75`
   - 用途：主页"最新文章"区块的文章缩略图

3. 文章内容页头图
   - 尺寸：1200px宽 × 630px高
   - 格式：JPEG或WebP（质量85%）
   - URL参数：`?format=auto&width=1200&quality=85`
   - 用途：文章页面顶部的大图

4. 文章内容中的图片
   - 尺寸：600px宽，高度自适应
   - 格式：JPEG或WebP（质量75%）
   - URL参数：`?format=auto&width=600&quality=75`
   - 用途：文章正文中插入的图片

> 注：使用OneDrive作为图床时，建议在上传前按照上述尺寸裁剪图片，以确保显示效果一致。

## 环境准备

1. 安装依赖:
```bash
pip install -r requirements.txt
```

2. 配置环境变量:
```bash
cp .env.example .env
# 编辑 .env 文件,填入必要的 API 密钥
```

## 使用说明

### 基本使用流程

1. **启动内容处理流水线**:
```bash
python run.py
```

2. **选择操作模式**:
   - `1`: 处理现有草稿 (新文章发布)
   - `2`: 重新发布已发布文章 (跨平台发布)
   - `3`: 生成测试文章

3. **选择发布平台**:
   - 系统会自动显示可用的发布平台
   - 已发布的平台会被自动过滤

### 高级功能

1. **微信公众号发布**:
```bash
# 确保配置了微信API和IP白名单
python run.py
# 选择选项1 -> 选择文章 -> 选择微信平台
# 查看生成的发布指导文件
cat _output/wechat_guides/*_guide.md
# 按照指导文件手动在微信后台创建文章
```

2. **查看发布状态**:
```bash
# 查看文章发布状态
ls _drafts/.publishing/

# 查看微信发布指导文件
ls _output/wechat_guides/
```

3. **运行测试**:
```bash
# 完整测试套件
pytest

# 微信功能测试
python tests/test_wechat_draft.py

# 使用项目测试运行器
python tests/run_tests.py
```

## 开发指南

1. 代码风格
- 使用 Python 3.8+
- 遵循 PEP 8 规范
- 使用类型注解

2. 测试
- 使用 pytest 进行测试
- 运行测试前确保配置正确
- 测试覆盖率要求 > 80%

3. 配置管理
- 敏感信息存放在 `.env`
- 配置分模块存放在 `config/`
- 遵循配置即代码原则

## 贡献指南

1. Fork 本仓库
2. 创建特性分支
3. 提交变更
4. 创建 Pull Request

## 许可证

MIT License

## 作者

Rong Zhu

## 致谢

- [Minimal Mistakes Jekyll Theme](https://mmistakes.github.io/minimal-mistakes/)
- [Google Gemini](https://deepmind.google/technologies/gemini/)

## 最近更新

### 2025-07-16: 微信发布功能优化 🚀
- **微信发布指导系统**: 由于API权限限制，改为生成发布指导文件
- **内容自动化处理**: 实现完整的内容转换、图片上传、AI排版优化
- **多平台发布状态管理**: 新增发布状态跟踪系统，支持跨平台重新发布
- **发布指导文件**: 微信版本保存到`_output/wechat_guides/`供手动使用
- **条件内容显示**: 投资理财文章自动添加风险声明
- **UI改进**: 修复订阅表单对齐问题，使用flexbox布局

### 历史更新
- 2025-06-19: 增加了推荐图片尺寸规范，优化了"最新文章"区块的图片显示效果
- 2025-03-04: 改进了 frontmatter 处理逻辑，使用 OrderedDict 确保字段顺序一致性
- 2025-03-04: 修复了图片处理和上传流程中的问题
- 2025-03-04: 优化了内容生成和发布流程

## 路线图 🗺️

- [ ] 支持更多图床服务 (Cloudflare Images, AWS S3)
- [ ] 添加内容SEO优化建议
- [ ] 支持批量文章操作
- [ ] 集成更多社交媒体平台
- [ ] 添加文章数据分析功能
