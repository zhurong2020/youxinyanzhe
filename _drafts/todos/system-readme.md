# 📚 项目文档结构

本目录包含Moomoo自定义交易策略的完整文档集合，涵盖策略开发、社群运营、商业模式等。

## 📋 文档目录说明

### 🚀 策略相关

#### DCA智能定投策略 (v2.10.3)
- **版本历史**: [`releases/DCA_VERSION_HISTORY.md`](releases/DCA_VERSION_HISTORY.md)
- **回测方案**: [`backtest_plans/`](backtest_plans/) - 回测配置和执行方案
- **回测结果**: [`backtest_results/`](backtest_results/) - 数据分析报告

#### Wheel期权策略 (v1.4.8)
- **营销内容**: [`marketing/Blog_Content_Plan_Wheel.md`](marketing/Blog_Content_Plan_Wheel.md)

### 👥 社群运营
- [`community/`](community/) - 社群管理核心文档
  - `FAQ.md` - 常见问题解答（用户自助）
  - `GROUP_RULES.md` - 社群管理规则
  - `FREE_GROUP_MANAGEMENT_STRATEGY.md` - 免费群低维护策略
  - `WELCOME_GUIDE.md` - 新人欢迎指南
  - [`wechat/`](community/wechat/) - 企业微信专属文档
    - `DCA_FREE_STRATEGY_INTRO.md` - DCA免费版完整介绍
    - `PAYMENT_MANAGEMENT_SYSTEM.md` - 付费管理体系（3+1定价）
    - `SERVICE_LEVEL_AGREEMENT.md` - 服务等级说明

### 💼 商业运营
- [`business/`](business/) - 商业模式和功能规划
- [`compliance/`](compliance/) - 合规运营指南和免责模板
- [`marketing/`](marketing/) - 营销策略和内容计划
- [`promotion/`](promotion/) - 推广执行和发布清单

### 🛠️ 技术开发
- [`developer/`](developer/) - 开发文档
  - `Moomoo量化功能中常用的API函数及其用法.txt` - API完整参考
  - `MOOMOO_API_LIMITATIONS_AND_SOLUTIONS.md` - API限制解决方案
  - `VERSION_MANAGEMENT_FINAL.md` - 版本管理方案

### 📝 内容创作
- [`blog_insights/`](blog_insights/) - 博客数据洞察
  - `DCA_BLOG_INSIGHTS_REPORT.md` - DCA策略分析报告
  - `2025-tqqq-investment-guide.md` - TQQQ投资指南
- [`content_strategy/`](content_strategy/) - 内容策略体系

### 📖 使用教程
- [`tutorials/`](tutorials/) - 教程指南
  - `AI_DEVELOPMENT_GUIDE.md` - AI辅助开发指南
  - `MOOMOO_ACCOUNT_SETUP_GUIDE.md` - Moomoo账户设置

### 🗄️ 归档文件
- [`archive/`](archive/) - 历史版本和过期文档（16个文件）

## 🎯 快速导航

### 新用户开始
1. 📋 阅读项目配置: [`../CLAUDE.md`](../CLAUDE.md)
2. 🚀 选择策略: DCA定投策略 (推荐) 或 Wheel策略
3. 📊 配置回测: 参考相应的回测配置方案
4. 🔧 API参考: 查阅API函数使用指南

### 开发者指南
1. 🔍 API限制: 查看API限制与解决方案文档
2. 📈 回测执行: 参考回测执行指南
3. 🔒 高级功能: 管理员数据收集模式使用指南
4. 📋 版本历史: 了解策略演进过程

### 管理员功能
1. 🔒 数据收集: 启用纯净数据收集模式
2. 🚀 性能优化: v2.10.3性能提升60-75%
3. 📊 长期回测: 支持10年+历史数据验证

## 📊 当前版本状态

| 策略 | 版本 | 状态 | 特性 |
|------|------|------|------|
| DCA Strategy | v2.10.3 | ✅ 生产就绪 | 性能优化，管理员数据收集，每日定投100%执行 |
| Wheel Strategy | v1.4.8 | ✅ 生产就绪 | 完全参数化，独立平仓策略，VIP分级系统 |
| Option Scanner | v1.0.8 | ✅ 生产就绪 | 合约扫描，持仓检测，Delta精准匹配 |

## 🔄 文档更新

- **最近更新**: 2025-01-08
- **更新内容**: 版本信息同步更新，Wheel策略v1.4.8文档整合
- **下次更新**: 根据回测结果和用户反馈

---

*Moomoo自定义策略文档 - 持续更新，追求卓越*