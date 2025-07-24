# 微信内容变现系统

## 📖 系统概述

微信内容变现系统是一套完整的自动化解决方案，专为解决GitHub Pages在国内访问限制问题而设计，通过微信公众号打赏机制实现优质内容的合理变现。

### 🎯 核心功能

- **自动内容打包**: 将博客文章自动生成高质量PDF和资料包
- **GitHub Release存储**: 利用GitHub Release作为免费、永久的文件存储
- **智能邮件发送**: 自动向用户发送精美的HTML邮件和下载链接
- **WeChat页脚集成**: 现有发布流程自动添加获取完整内容的说明
- **Token安全管理**: 自动监控GitHub Token过期时间，提供及时提醒

## 🚀 快速开始

### 1. 环境配置

在 `.env` 文件中配置必要的API密钥：

```bash
# GitHub配置
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_username
GITHUB_REPO=your_repo_name

# Gmail SMTP配置
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# 微信公众号配置
WECHAT_APPID=your_wechat_appid
WECHAT_APPSECRET=your_wechat_appsecret
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 系统测试

```bash
# 运行系统测试
python scripts/test_reward_system.py

# 检查GitHub Token状态
python scripts/check_github_token.py
```

## 📋 主要命令

### 基础操作

```bash
# 为文章创建资料包并上传到GitHub Release
python scripts/reward_system_manager.py create _posts/article-name.md

# 向用户发送奖励内容包
python scripts/reward_system_manager.py send user@example.com "文章标题"

# 查看系统统计信息
python scripts/reward_system_manager.py stats
```

### 批量处理

```bash
# 添加待处理请求
python scripts/reward_system_manager.py add user@example.com "文章标题" --name "用户名"

# 批量处理待处理请求
python scripts/reward_system_manager.py process --batch-size 10
```

## 🏗️ 系统架构

```
文章发布 → 自动生成PDF包 → 上传GitHub Release → 微信文章添加页脚
                                                    ↓
用户打赏 → 截图+邮箱私信 → 手动处理 → 自动发送邮件包含下载链接
```

### 核心组件

1. **GitHub Release管理器** (`github_release_manager.py`)
   - 自动创建Release
   - 上传ZIP格式的内容包
   - 管理下载链接和统计

2. **内容打包系统** (`package_creator.py`)
   - 生成高质量PDF
   - 收集文章图片
   - 整理相关链接
   - 创建资料清单

3. **邮件发送系统** (`email_sender.py`)
   - Gmail SMTP集成
   - 精美HTML邮件模板
   - 发送记录管理

4. **WeChat发布集成** (`wechat_publisher.py`)
   - 自动添加奖励页脚
   - 集成现有发布流程

5. **系统管理器** (`reward_system_manager.py`)
   - 统一命令行界面
   - 批量处理功能
   - 系统统计和监控

## 📊 监控和维护

### GitHub Token管理

系统会自动监控GitHub Token状态：
- 30天前：✅ 状态良好
- 14天前：📅 建议更新  
- 7天前：⚠️ 需要更新
- 已过期：❌ 立即更新

### 系统统计

```bash
python scripts/reward_system_manager.py stats
```

输出示例：
```
📊 系统统计信息:
✅ GitHub Token: 89 天后过期
GitHub Releases: 0 个
总下载次数: 0 次
邮件发送: 0 成功, 0 失败
成功率: 0.0%
待处理请求: 0 个
已处理请求: 0 个
```

## 🔧 工作流程

### 内容创作者流程

1. **发布文章** - 使用现有的内容发布脚本
2. **自动处理** - 系统自动生成资料包并上传到GitHub Release
3. **微信发布** - 文章末尾自动添加获取完整内容的说明

### 用户交互流程

1. **用户打赏** - 在微信公众号文章下打赏任意金额
2. **提交信息** - 截图发送到公众号并提供邮箱地址
3. **手动处理** - 内容创作者使用系统工具发送资料包
4. **自动发送** - 系统自动发送包含下载链接的精美邮件

## 📁 目录结构

```
scripts/
├── reward_system_manager.py    # 主管理脚本
├── github_release_manager.py   # GitHub Release管理
├── email_sender.py             # 邮件发送系统
├── package_creator.py          # 内容打包系统
├── check_github_token.py       # Token状态检查
└── test_reward_system.py       # 系统测试脚本

config/templates/
└── wechat_reward_footer.html   # WeChat页脚模板

_data/                          # 数据存储目录（git忽略）
├── github_releases.json       # Release记录
├── email_records.json         # 邮件发送记录
├── github_token_status.json   # Token状态缓存
├── pending_reward_requests.json   # 待处理请求
└── processed_reward_requests.json # 已处理请求

_output/                        # 输出目录（git忽略）
├── packages/                   # 生成的内容包
└── wechat_guides/             # WeChat发布指导
```

## 🔐 安全考虑

- **环境变量隔离**: 所有敏感信息通过 `.env` 文件管理
- **数据文件保护**: 所有数据文件已添加到 `.gitignore`
- **Token监控**: 自动监控GitHub Token过期时间
- **权限最小化**: GitHub Token仅需要 `repo-Contents` 权限

## 📚 扩展功能

### 计划中的功能

- **微信消息自动识别**: 自动识别打赏截图和邮箱信息
- **统计分析面板**: 详细的收益和用户行为分析
- **会员制度**: 支持月度会员和批量内容访问

### 自定义配置

系统支持多种自定义选项：
- 邮件模板定制
- 页脚文案调整
- 打包内容配置
- 过期提醒设置

## 🛠️ 故障排除

### 常见问题

1. **GitHub Token无效**
   ```bash
   python scripts/check_github_token.py
   ```

2. **邮件发送失败**
   ```bash
   python scripts/email_sender.py test
   ```

3. **依赖包问题**
   ```bash
   pip install -r requirements.txt
   ```

### 获取支持

- 查看项目 `PROJECT_ROADMAP.md` 了解最新进展
- 运行测试脚本诊断问题
- 检查日志文件了解详细错误信息

---

*该系统设计注重安全性、自动化和用户体验，为优质内容创作提供可持续的变现解决方案。*