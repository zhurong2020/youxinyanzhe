# 有心言者博客内容处理工具

一个用于处理博客内容的自动化工具集,支持图片处理、内容生成和多平台发布。

## 功能特性

- 🖼️ 图片处理
  - 自动上传到 Cloudflare Images
  - 生成优化的图片变体
  - 自动维护图片 ID 映射关系
  - 支持图片变体和 CDN 分发

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
│   ├── content_pipeline.py # 内容处理流水线
│   └── image_mapper.py     # Cloudflare 图片处理和映射管理
├── tests/                  # 测试代码
│   ├── __init__.py
│   ├── conftest.py        # 测试配置和fixtures
│   ├── test_cloudflare.py
│   ├── test_content_pipeline.py
│   └── test_gemini.py
├── config/                 # 配置文件
│   ├── pipeline_config.yml    # 主配置
│   ├── cloudflare_config.yml  # Cloudflare Images 配置（API、变体、映射）
│   ├── gemini_config.yml      # AI模型配置
│   └── test_config.yml        # 测试配置
├── _data/                  # 数据文件
│   └── image_mappings.yml  # Cloudflare 图片 ID 映射关系
├── _drafts/               # 文章草稿
├── _posts/                # 已发布文章
├── .env.example          # 环境变量示例
└── _config.yml            # Jekyll配置
```

## 配置说明

- `_config.yml`: Jekyll 站点配置
- `config/pipeline_config.yml`: 内容处理流程配置
- `config/cloudflare_config.yml`: Cloudflare Images 配置（API、变体、映射）
- `config/gemini_config.yml`: AI 内容生成配置
- `.env`: 环境变量(API密钥等敏感信息)
- `_data/image_mappings.yml`: 自动生成的图片 ID 映射文件

## 图片处理流程

1. 图片上传
   - 检测文章中的图片引用
   - 自动上传到 Cloudflare Images
   - 生成并保存图片 ID 映射

2. 映射管理
   - 自动维护 `image_mappings.yml`
   - 按年/月/文章组织映射关系
   - 避免重复上传相同图片

3. 图片引用
   - 自动替换文章中的图片链接
   - 支持不同的图片变体
   - 使用 Cloudflare CDN 加速

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
- [Cloudflare Images](https://www.cloudflare.com/products/cloudflare-images/)
- [Google Gemini](https://deepmind.google/technologies/gemini/) 