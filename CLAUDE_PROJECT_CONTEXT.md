# Claude Code 项目上下文 - 有心工坊

## 项目角色定位
**有心工坊 (YouXin Workshop)** - 媒体矩阵的技术核心和内容创作引擎

## 项目技术概况
- **技术栈**：Jekyll + Python + AI双引擎
- **代码质量**：175个测试用例，A级软件工程标准
- **核心功能**：VIP内容管理、多平台发布、OneDrive图床、播客生成
- **商业模式**：VIP会员分层体系（VIP2/VIP3/VIP4）

## 与家庭项目的关系
- 家庭项目提供**媒体矩阵战略和资源规划**
- 有心工坊负责**技术实现和内容执行**
- 两个项目形成完整的"规划-执行"闭环

## Claude Code 使用指南

### 当前项目适用场景
- Python代码开发和调试
- 内容处理流程优化
- AI集成和API调用
- VIP系统功能开发
- 多平台发布自动化
- 测试用例编写和执行
- 技术文档更新

### 切换到家庭项目的场景
- 媒体矩阵策略调整
- 跨平台内容规划
- 品牌定位优化
- 商业模式设计
- 效果分析和复盘

## 重要文件和命令速查

### 核心文件位置
- 🎛️ 主程序：`run.py`
- ⚙️ 核心业务：`scripts/core/content_pipeline.py`
- 🔧 工具集：`scripts/tools/`
- 📝 配置文件：`config/`
- 📚 项目文档：`docs/`
- 🧪 测试文件：`tests/`

### 常用命令
- 启动系统：`python run.py`
- 运行测试：`python -m pytest tests/ -v`
- 检查代码：`python -m flake8 scripts/`
- 安装依赖：`pip install -r requirements.txt`

### 开发约定
- 遵循`CLAUDE.md`中的开发规范
- 新功能必须有对应测试用例
- 配置修改需要更新相关文档
- 重要变更要更新`CHANGELOG_DETAILED.md`

## 快速项目识别
- 📁 当前路径：`/home/wuxia/projects/youxinyanzhe`
- 🔗 家庭项目路径：`/home/wuxia/projects/family_management_hub`
- 🚀 切换命令：`cd ../family_management_hub`