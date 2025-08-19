# 有心工坊 开发约定

这是有心工坊 (YouXin Workshop) - 为有心人打造的数字创作平台，基于Jekyll的自动化博客发布系统，重点关注多平台内容分发、图片管理和会员服务。

## 项目概述
- **平台定位**: 有心工坊 - 为终身学习者和内容创作者提供的一站式数字创作平台
- **主要功能**: Jekyll博客系统、YouTube播客生成器、会员管理系统、混合图片管理、多平台发布
- **核心理念**: 学习 · 分享 · 进步
- **技术架构**: 详见 `docs/TECHNICAL_ARCHITECTURE.md`
- **图片管理**: 详见 `docs/IMAGE_MANAGEMENT_WORKFLOW.md`
- **Azure集成规划**: 详见 `docs/AZURE_INTEGRATION_ROADMAP.md`
- **更新历史**: 详见 `docs/CHANGELOG_DETAILED.md`

## 当前状态
- **系统状态**: 所有核心模块已完成重构，VIP会员系统运行稳定
- **主要功能**: 统一内容处理流程、OneDrive图片管理、模块化菜单系统
- **下个阶段**: Azure AI服务集成、喜马拉雅平台集成

**详细进展**: 查看 `docs/CHANGELOG_DETAILED.md` 获取完整的开发历史和重构成果

## ⚠️ 重要提示：代码重构说明
**原因**: 原`run.py`代码3394行，采用单体式架构，维护困难  
**重构方式**: 拆分为模块化架构，新入口为`run.py`，原文件归档为`docs/archived/run_old.py`

**功能问题排查**:
1. 如发现功能异常，首先检查新模块化实现 (`scripts/core/`, `scripts/cli/`)
2. 若新实现有缺失，可参考 `docs/archived/run_old.py` 对应功能
3. **⚠️ 重要**: 原文件3394行，**超过LLM单次读取限制**，需具体定位功能后分段阅读
4. 参考归档文件的详细说明: `docs/archived/README.md`

**重构对照**: 原单体文件 → 新模块化架构  
- 菜单系统: `scripts/cli/` (MenuHandler → MenuRouter → 专门处理器)
- 内容处理: `scripts/core/content_pipeline.py` 
- 工具脚本: `scripts/tools/` (按功能分类)

## 核心开发约定

### 代码规范
- **编码风格**: 遵循PEP 8，使用类型注解，确保IDE无Error级别问题
- **虚拟环境**: 始终在`venv/`环境中运行脚本和安装依赖
- **测试**: 核心功能修改需要对应的pytest测试用例

### 内容创作约定
#### 四大分类体系
- **🧠 认知升级** (`cognitive-upgrade`): 思维模型、学习方法、认知心理学
- **🛠️ 技术赋能** (`tech-empowerment`): 实用工具、技术教程、自动化方案
- **🌍 全球视野** (`global-perspective`): 国际趋势、文化差异、跨文化思维
- **💰 投资理财** (`investment-finance`): 投资策略、理财方法、量化分析

#### 内容标准
- **Front Matter**: 必需字段 `title`(25-35字符), `date`, `header`
- **摘要**: 50-60字符，用于首页预览
- **结构**: 开头钩子 + `<!-- more -->` + 主要内容 + 🎧播客 + 🌍英文资源
- **风格**: 客观事实导向，科普语调，数据驱动，鼓励思考

### VIP会员系统
#### 技术字段映射
- **VIP2** → `member_tier: monthly` (¥108/月)
- **VIP3** → `member_tier: quarterly` (¥288/季)  
- **VIP4** → `member_tier: yearly` (¥720/年)

**重要**: Front Matter中使用技术字段值，用户界面显示VIP2/VIP3/VIP4

**详细规范**: 查看 `docs/MEMBER_CONTENT_RULES_AND_STANDARDS.md` 获取完整的会员内容管理规则

### 关键技术要求
- **Jekyll资源路径**: 必须使用 `{{ site.baseurl }}/assets/...`，禁用绝对路径
- **安全管理**: 敏感数据使用`.env`文件，API密钥不提交到仓库

---

**相关文档**:
- `docs/TECHNICAL_ARCHITECTURE.md` - 详细技术架构说明
- `docs/CHANGELOG_DETAILED.md` - 完整更新历史
- `docs/project-completion-summary.md` - 项目完成状态总结
- `docs/MEMBER_CONTENT_RULES_AND_STANDARDS.md` - 会员内容管理规范
- `docs/MEMBER_CONTENT_MANAGEMENT_SYSTEM.md` - 会员内容技术实现
- `docs/CONTENT_SERIES_INTEGRATION_STRATEGY.md` - 内容系列集成策略
- `docs/IMAGE_MANAGEMENT_WORKFLOW.md` - 图片管理完整工作流程
- `docs/SYSTEM_MENU_ARCHITECTURE.md` - 系统菜单架构设计
- `docs/AUDIO_RESOURCE_MANAGEMENT.md` - 音频资源管理系统