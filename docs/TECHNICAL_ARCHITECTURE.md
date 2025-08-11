# 技术架构说明

本文档详细说明项目的技术架构、关键决策和具体实现方案。

## 技术栈概览

### 核心技术
- **Jekyll**: 静态站点生成器，GitHub Pages自动部署
- **Python 3.8+**: 后端脚本和自动化工具
- **Google Gemini**: AI内容生成和优化
- **ElevenLabs**: 高质量TTS语音合成
- **YouTube API**: 视频管理和播客生成

### 关键集成
- **WeChat API**: 公众号内容发布指导
- **Google Analytics 4**: 深度用户行为分析
- **Microsoft Graph API**: OneDrive图床自动化和图片索引管理
- **Azure AI服务 (规划中)**: Azure OpenAI Service + Azure AI Speech
- **SMTP**: 自动化邮件发送

## 核心架构决策

### 1. WeChat发布策略
**决策**: 采用指导模式而非直接API发布
- **原因**: WeChat API发布权限需要企业认证，个人账号受限
- **实现**: 完整内容处理(Markdown→HTML，图片上传，AI优化) + 手动发布指导
- **文件位置**: `.tmp/output/wechat_guides/`
- **优势**: 保持技术处理自动化，提供清晰的手动发布步骤

### 2. 图片托管方案 (已完成)
**决策**: OneDrive图床自动化系统，完整的创作到发布工作流
- **完整工作流**: 本地创作 → OneDrive上传 → 链接替换 → 本地清理 → 索引记录
- **Microsoft Graph集成**: OAuth2认证，WSL环境优化，支持文件批量管理
- **智能索引系统**: 文件哈希去重，完整元数据记录，多维度查询支持
- **自动化处理**: 上传成功后自动删除本地assets文件，保持仓库精简
- **路径兼容**: 支持Jekyll baseurl变量，确保GitHub Pages完全兼容

### 3. 发布状态管理
**决策**: 使用YAML文件跟踪发布状态
- **位置**: `_drafts/.publishing/*.yml`
- **功能**: 跟踪已发布平台、时间戳和发布计数
- **优势**: 支持跨平台重新发布和去重，便于团队协作

### 4. 会员验证系统
**决策**: 基于访问码的多级会员验证
- **实现**: JavaScript前端验证 + Python后端管理
- **等级**: VIP1-VIP4四级递进服务体系
- **内容分层**: 争议性/教育性内容仅向付费用户开放

## 项目结构详解

### 目录组织
```
├── scripts/
│   ├── core/              # 核心业务逻辑
│   │   ├── content_pipeline.py
│   │   ├── wechat_publisher.py
│   │   └── youtube_podcast_generator.py
│   ├── utils/             # 可重用工具
│   └── tools/             # 独立调试工具
│       ├── image_manager.py           # 智能图片管理系统
│       ├── onedrive_blog_images.py    # OneDrive图床自动化
│       └── onedrive_image_index.py    # OneDrive图片索引管理
├── tests/                 # 所有测试文件
├── config/                # 配置文件
│   ├── platforms.yml
│   ├── gemini_config.yml
│   ├── onedrive_config.json        # OneDrive图床配置
│   └── templates/
├── docs/                  # 项目文档
├── _data/                 # Jekyll数据文件
│   └── onedrive_image_index.json   # OneDrive图片索引记录
├── _drafts/
│   ├── .publishing/       # 发布状态跟踪
│   └── archived/          # 已完成文章归档
├── .build/                # 构建和运行时文件 (Git忽略)
└── .tmp/                  # 临时文件和输出 (Git忽略)
```

### 关键文件说明
- **run.py**: 主入口脚本，统一的操作界面，含OneDrive图片索引管理菜单
- **content_pipeline.py**: 内容处理管道，支持多平台适配
- **youtube_podcast_generator.py**: YouTube视频转播客系统
- **wechat_publisher.py**: WeChat发布指导生成器
- **member_management.py**: 会员系统管理工具
- **image_manager.py**: 根据文件大小自动选择存储策略的智能图片管理
- **onedrive_blog_images.py**: OneDrive OAuth认证和图床自动化系统，支持批量处理
- **onedrive_image_index.py**: OneDrive图片索引管理，支持查询统计和数据维护

## 安全与部署

### 敏感数据管理
- **环境变量**: 使用`.env`文件存储敏感数据，排除于版本控制
- **API密钥**: 从不提交密钥到仓库
- **IP白名单**: WeChat API需要在官方后台配置IP白名单

### 部署安全
- **VPS部署**: 生产WeChat发布使用静态IP地址
- **访问控制**: 限制API权限到最小所需范围
- **依赖项**: 保持requirements.txt更新和最小化

## 性能优化

### 资源处理
- **图片优化**: 自动压缩和格式转换
- **音频处理**: 智能TTS配额管理和缓存
- **内容缓存**: 生成内容的本地缓存机制

### API管理
- **配额监控**: ElevenLabs TTS配额实时监控和预警
- **错误恢复**: 自动重试和降级策略
- **日志系统**: 统一日志系统，支持级别过滤和轮转

## 扩展性设计

### 平台扩展
- **模块化设计**: 新平台可以通过插件方式添加
- **配置驱动**: 平台特定设置通过YAML配置
- **统一接口**: 标准化的内容适配接口

### 功能扩展
- **插件架构**: 支持第三方功能模块
- **钩子系统**: 关键流程节点支持自定义处理
- **API接口**: 为外部工具提供标准化API

## 技术路线图

### 混合TTS架构优化 (Phase 1.5-A) 
**目标**: 大幅降低TTS成本，解决中文AI口音问题，提升语音质量

**优先级1 - TTS服务重构** (立即实施):
- **中文语音**: 豆包Web版 (免费，行业领先质量，几乎无AI口音)
- **英文语音**: Microsoft Edge TTS (免费，OpenAI兼容，企业级质量)
- **备选方案**: ElevenLabs (故障切换保障)
- **预期节省**: $242/年 (ElevenLabs订阅成本)

**混合架构特性**:
- 智能语言检测和服务路由
- 音频处理和格式统一
- 异步并发处理
- 故障自动切换

### Azure生态系统集成 (Phase 1.5-B)
**目标**: 技术储备，等待最佳时机迁移

**延后评估 - AI服务替换** (2025年底前):
- **Azure OpenAI Service**: Gemini Pro免费期结束前重新评估
- **Gemini Pro**: 继续使用免费版至2025年底

**优先级2 - 基础设施增强**:
- **Azure Key Vault**: 统一密钥管理，提升安全性
- **Azure CDN**: OneDrive图片全球加速

**详细规划**: 参见 `docs/AZURE_INTEGRATION_ROADMAP.md`

---

**文档版本**: v1.4  
**最后更新**: 2025-08-11  
**维护**: 技术架构变更时同步更新

## 最近更新 (v1.4)
- 制定混合TTS架构策略，优先解决中文AI口音和成本问题
- 确定豆包Web版(中文) + Edge TTS(英文)免费方案组合
- 调整Azure集成时间线，延后至Gemini Pro免费期结束前
- 设计智能语言路由和故障切换机制
- 预期年节省$242 TTS订阅成本

## 历史更新 (v1.3)
- 完成OneDrive图床自动化系统集成
- 新增图片索引管理系统和完整工作流程
- 优化WSL环境下的OAuth认证流程
- 实现本地文件自动清理和去重功能
- 新增Azure生态系统集成技术路线图