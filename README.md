# 有心言者博客内容处理工具

一个用于处理博客内容的自动化工具集,支持图片处理、内容生成和多平台发布。

## 功能特性

- 📝 内容处理
  - 使用 Google Gemini 生成内容
  - 自动润色和格式化
  - 支持多种内容模板

- 🚀 多平台发布
  - GitHub Pages
  - WordPress
  - 微信公众号

## 项目结构

```
youxinyanzhe/
├── assets/                 # 静态资源
│   └── images/
│       ├── favicon/       # 网站图标
│       └── posts/         # 文章图片
├── scripts/                # 主要功能脚本
│   ├── __init__.py
│   └── content_pipeline.py # 内容处理流水线
├── tests/                  # 测试代码
│   ├── __init__.py
│   ├── conftest.py        # 测试配置和fixtures
│   ├── test_content_pipeline.py
│   └── test_gemini.py
├── config/                 # 配置文件
│   ├── pipeline_config.yml    # 主配置
│   ├── gemini_config.yml      # AI模型配置
│   └── test_config.yml        # 测试配置
├── _drafts/               # 文章草稿
├── _posts/                # 已发布文章
├── .env.example          # 环境变量示例
└── _config.yml            # Jekyll配置
```

## 配置说明

- `_config.yml`: Jekyll 站点配置
- `config/pipeline_config.yml`: 内容处理流程配置
- `config/gemini_config.yml`: AI 内容生成配置
- `.env`: 环境变量(API密钥等敏感信息)

## 内容处理流程

1. 草稿处理
   - 读取草稿文件
   - 使用 AI 润色内容
   - 生成多平台内容变体

2. Frontmatter 处理
   - 自动处理 YAML frontmatter
   - 支持多种布局模板
   - 注意：虽然 `layout: single` 不必严格位于 frontmatter 第一行，但为保持一致性，代码会尝试将其放在首位
   - 自动添加和更新元数据（如最后修改时间）

3. 发布流程
   - 自动发布到 GitHub Pages
   - 支持 WordPress 和微信公众号发布
   - 发布后自动归档草稿



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

1. 创建新文章:
```bash
python run.py
```

2. 处理现有草稿:
```bash
python scripts/content_pipeline.py process
```

3. 运行测试:
```bash
pytest
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

- 2025-06-19: 增加了推荐图片尺寸规范，优化了"最新文章"区块的图片显示效果
- 2025-03-04: 改进了 frontmatter 处理逻辑，使用 OrderedDict 确保字段顺序一致性
- 2025-03-04: 修复了图片处理和上传流程中的问题
- 2025-03-04: 优化了内容生成和发布流程
