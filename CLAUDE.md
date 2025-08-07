# Claude Code 开发约定

这是一个基于Jekyll的自动化博客发布系统，重点关注多平台内容分发和会员管理。

## 项目概述
- **主要功能**: Jekyll博客系统、YouTube播客生成器、会员管理系统、多平台发布
- **技术架构**: 详见 `docs/TECHNICAL_ARCHITECTURE.md`
- **更新历史**: 详见 `docs/CHANGELOG_DETAILED.md`

## 当前工作重点
- **Phase 1 (当前)**: 内容创作与数据观察 - 保持每周1-2篇高质量内容，完善会员服务
- **Phase 2 (2-3月后)**: 喜马拉雅平台集成 - OAuth认证、音频上传、智能平台选择
- **Phase 3 (3-6月后)**: 社区功能与高级服务 - Discord社区、深度投资服务

## 核心开发约定

### 代码规范
- **编码风格**: 遵循PEP 8，使用类型注解和显式类型转换
- **类型检查**: 修改代码后必须检查IDE中的类型错误提示，确保无Error级别问题
  - 使用 `Optional[str]` 而非 `str = None` 
  - 函数参数类型必须明确，避免 `None` 类型冲突
  - 未使用参数可用 `_` 占位符代替具体参数名
- **测试**: 核心业务逻辑修改需要对应的pytest测试用例
- **虚拟环境**: 始终在`venv/`环境中运行脚本和安装依赖

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

### 关键技术要求
#### Jekyll资源路径 (关键)
- **必须使用**: `{{ site.baseurl }}/assets/...` (因为使用baseurl="/youxinyanzhe"部署)
- **禁止使用**: 绝对路径如 `/assets/images/...`
- **测试**: 在本地Jekyll服务器和GitHub Pages上都要测试

#### 安全约定
- **敏感数据**: 使用`.env`文件，排除于版本控制
- **API密钥**: 从不提交密钥到仓库
- **访问控制**: 限制API权限到最小所需范围

---

**相关文档**:
- `docs/TECHNICAL_ARCHITECTURE.md` - 详细技术架构说明
- `docs/CHANGELOG_DETAILED.md` - 完整更新历史
- `docs/project-completion-summary.md` - 项目完成状态总结