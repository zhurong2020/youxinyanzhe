# 开发指南

本文档为开发者提供项目开发、测试和贡献的详细指南。

## 🛠️ 开发环境设置

### 环境要求
- Python 3.8+
- Node.js 14+ (用于Jekyll依赖)
- Git
- FFmpeg (用于音频/视频处理)

### 本地开发设置

```bash
# 1. 克隆项目
git clone https://github.com/zhurong2020/youxinyanzhe.git
cd youxinyanzhe

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装Python依赖
pip install -r requirements.txt

# 4. 安装Jekyll依赖
bundle install

# 5. 配置环境变量
cp .env.example .env
# 编辑.env文件，填入必要的API密钥

# 6. 运行测试确保环境正常
python -m pytest tests/
```

## 📁 项目架构

### 核心模块结构
```
scripts/
├── core/                    # 核心业务逻辑
│   ├── content_pipeline.py  # 内容处理管道
│   └── wechat_publisher.py  # 微信发布器
├── utils/                   # 工具函数
│   ├── email_sender.py      # 邮件发送
│   └── github_release_manager.py
└── tools/                   # 独立工具
    └── check_github_token.py
```

### 配置系统
```
config/
├── environments/            # 环境配置
├── platforms.yml           # 平台配置
├── templates/              # 模板文件
└── gemini_config.yml       # AI配置
```

## 🧪 测试指南

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试文件
python tests/run_tests.py

# 生成测试覆盖率报告
python -m pytest --cov=scripts tests/
```

### 测试约定

- 所有测试文件放在`tests/`目录
- 测试文件以`test_`开头
- 使用`conftest.py`管理共享fixtures
- 重要功能必须有对应测试

## 🔧 代码规范

### Python代码规范

```python
# 1. 使用类型注解
def process_content(content: str) -> Dict[str, Any]:
    pass

# 2. 错误处理
try:
    result = api_call()
except SpecificException as e:
    logger.error(f"API调用失败: {e}")
    raise

# 3. 导入规范
from pathlib import Path
from typing import Dict, List, Optional
```

### Jekyll/Markdown规范

```markdown
# 文章Front Matter标准
---
title: "文章标题"
date: YYYY-MM-DD
categories:
- 分类名
tags:
- 标签1
- 标签2
header:
  overlay_image: {{ site.baseurl }}/assets/images/posts/YYYY/MM/image.jpg
---
```

## 🚀 部署流程

### GitHub Pages部署
项目自动通过GitHub Actions部署到GitHub Pages，无需手动操作。

### 本地Jekyll预览
```bash
# 启动本地Jekyll服务器
bundle exec jekyll serve

# 访问 http://localhost:4000/youxinyanzhe
```

## 🤝 贡献流程

### 1. Fork和Clone
```bash
# Fork项目到个人GitHub
# 然后克隆个人Fork
git clone https://github.com/YOUR_USERNAME/youxinyanzhe.git
```

### 2. 创建功能分支
```bash
git checkout -b feature/new-feature-name
```

### 3. 开发和测试
- 编写代码
- 添加或更新测试
- 确保所有测试通过
- 遵循代码规范

### 4. 提交PR
```bash
git add .
git commit -m "feat: 添加新功能描述"
git push origin feature/new-feature-name
```

然后在GitHub上创建Pull Request。

## 📝 提交信息规范

使用[约定式提交](https://www.conventionalcommits.org/zh-hans/)格式：

```
<类型>: <描述>

[可选的正文]

[可选的脚注]
```

类型包括：
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具相关

## 🐛 调试指南

### 日志系统
- 运行时日志: `.build/logs/pipeline.log`
- 错误排查: 检查日志文件中的ERROR和WARNING信息

### 常见问题
1. **API调用失败**: 检查`.env`中的API密钥配置
2. **图片显示问题**: 确认使用`{{ site.baseurl }}`变量
3. **微信发布失败**: 检查IP白名单和API权限

## 📊 性能监控

### 代码覆盖率
- 目标覆盖率: >80%
- 查看报告: `.build/htmlcov/index.html`

### 性能指标
- API响应时间
- 文件处理时间
- 内存使用量

---

## 💡 开发建议

1. **开发前**先阅读相关文档和现有代码
2. **小步快跑**，保持提交粒度适中
3. **测试驱动**，重要功能先写测试
4. **文档同步**，代码变更时更新相关文档
5. **性能意识**，注意代码性能和资源使用

如有疑问，欢迎通过Issue讨论！