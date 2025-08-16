# 草稿文档管理规范

> **文档版本**: v1.0  
> **创建时间**: 2025年8月16日  
> **适用范围**: 有心工坊内容创作和文档管理

---

## 🎯 草稿管理原则

### 核心理念
1. **价值最大化**: 确保每个有价值的素材都得到充分利用
2. **结构化管理**: 按内容价值和使用状态分类管理
3. **版权安全**: 妥善处理第三方资料，避免法律风险
4. **可持续维护**: 建立长期可维护的管理体系

### 生命周期管理
```
创建 → 开发 → 整合 → 发布 → 归档/清理
```

---

## 📁 目录结构规范

### 主要目录
```
_drafts/
├── [active-drafts]              # 活跃草稿（根目录）
├── vip4-preparation/            # VIP4内容准备
├── archived/                    # 归档内容
│   ├── project-management/      # 项目管理文档
│   ├── completed-series/        # 已完成系列
│   └── reference/              # 参考资料
└── templates/                   # 文档模板

assets/
└── research-reports/            # 研究报告资源库
    ├── tesla/                   # Tesla相关报告
    ├── market-analysis/         # 市场分析报告
    └── [other-topics]/          # 其他主题报告
```

### 目录说明
- **根目录**: 当前正在开发的活跃草稿
- **vip4-preparation**: 为VIP4服务准备的高价值内容
- **archived**: 已完成项目的归档，按价值分类保存
- **research-reports**: 第三方研究报告，不纳入版本控制

---

## 📋 文件命名规范

### 草稿文档命名
```
格式: [主题]-[类型]-[描述].md
示例: 
- tesla-vip2-sa-analysis.md
- musk-interview-2025-analysis.md
- crypto-market-weekly-report.md
```

### 研究报告命名
```
格式: YYYY-MM-DD_[机构]_[主题]_[评级-目标价].pdf
示例:
- 2025-08-14_argus-research_tesla-analysis_HOLD-273.pdf
- 2025-08-15_cfra-research_tesla-analysis_HOLD-300.pdf
- 2025-08-15_morningstar_tesla-analysis_2STAR-250.pdf

命名要素说明:
- 日期: 报告发布日期 (YYYY-MM-DD)
- 机构: 研究机构名称 (小写,连字符)
- 主题: 分析标的/主题
- 评级: 投资评级和目标价
```

### 项目管理文档命名
```
格式: [项目]-[类型]-[状态].md
示例:
- tesla-content-strategy-completed.md
- tesla-completion-checklist-archived.md
- vip4-planning-draft.md
```

---

## 🔄 内容生命周期管理

### 阶段一：创建阶段
**位置**: `_drafts/` (根目录)
**状态**: 正在开发
**管理**: 
- 使用标准命名规范
- 包含完整的Front Matter
- 定期备份重要内容

### 阶段二：开发阶段  
**位置**: `_drafts/` (根目录)
**状态**: 内容完善中
**管理**:
- 定期质量检查
- 版本控制提交
- 内容价值评估

### 阶段三：整合阶段
**位置**: `_drafts/vip4-preparation/` 或继续在根目录
**状态**: 准备发布或整合到其他内容
**管理**:
- 确定发布计划
- 准备配套资源
- 最终质量审核

### 阶段四：发布阶段
**位置**: `_posts/`
**状态**: 正式发布
**管理**:
- 原草稿移至归档或删除
- 建立发布记录
- 持续监控反馈

### 阶段五：归档阶段
**位置**: `_drafts/archived/` (按分类)
**状态**: 项目完成，保留参考价值
**管理**:
- 按价值分类存储
- 定期清理评估
- 维护索引记录

---

## 📊 分类管理策略

### 按内容价值分类

#### 高价值内容 → `vip4-preparation/`
**标准**:
- 未来6个月内确定使用
- 具备VIP4服务价值
- 原创性分析内容
- 稀缺性研究资料

**示例**:
- Musk关键访谈深度分析
- 开源生态投资框架
- 机构级研究方法论

#### 项目管理价值 → `archived/project-management/`
**标准**:
- 项目复盘参考价值
- 流程优化经验
- 最佳实践记录
- 策略规划文档

**示例**:
- 内容策略完整方案
- 项目完成检查清单
- 系列规划文档

#### 参考资料价值 → `archived/reference/`
**标准**:
- 背景信息价值
- 历史记录意义
- 研究素材库
- 灵感来源池

**示例**:
- 行业报告收集
- 竞争对手分析
- 市场趋势资料

### 按使用状态分类

#### 已充分利用 → 删除
**标准**:
- 内容已完全发布
- 无残余价值
- 不具备参考意义
- 占用存储空间

#### 部分利用 → 评估保留
**标准**:
- 部分内容已使用
- 残余内容有价值
- 可能重新利用
- 需要进一步评估

---

## 🔒 版权和安全管理

### PDF文档管理
**原则**: 版权保护优先，避免法律风险

**技术实现**:
```bash
# .gitignore配置
assets/research-reports/    # 排除整个研究报告目录
*.pdf                      # 排除所有PDF文件  
!docs/*.pdf               # 但保留文档目录中的PDF
```

**访问控制**:
- 仅VIP4用户可下载完整报告
- 在VIP文档中提供专业引用
- 建立版权声明和使用条款

### 敏感信息处理
**原则**: 
- 移除个人隐私信息
- 保护商业机密数据
- 遵守数据保护法规

**检查清单**:
- [ ] 是否包含个人邮箱/电话
- [ ] 是否包含内部价格信息  
- [ ] 是否包含未公开的战略信息
- [ ] 是否符合引用和转载规范

---

## 📅 定期维护规范

### 每月检查 (月末执行)
**目标**: 保持目录清洁，及时处理积压

**检查项目**:
- [ ] 根目录是否有超过30天未更新的草稿
- [ ] 是否有已发布但未清理的原稿
- [ ] vip4-preparation目录内容评估
- [ ] 新增研究报告的价值评估

### 每季度清理 (季度末执行)  
**目标**: 深度整理，优化结构

**清理项目**:
- [ ] 归档超过90天未使用的内容
- [ ] 清理无价值的临时文件
- [ ] 更新文档索引和分类
- [ ] 评估归档内容的保留价值

### 年度复盘 (年末执行)
**目标**: 总结经验，优化流程

**复盘内容**:
- [ ] 草稿管理效率评估
- [ ] 内容利用率统计分析  
- [ ] 管理流程优化建议
- [ ] 下年度改进计划制定

---

## 🛠️ 技术工具支持

### 自动化脚本
```bash
# 草稿状态检查
python scripts/tools/draft_status_checker.py

# 过期内容清理  
python scripts/tools/draft_cleaner.py --days 90

# 文件重命名工具
python scripts/tools/file_renamer.py --type research-report
```

### 查询和检索
```bash
# 按主题查找
find _drafts/ -name "*tesla*" -type f

# 按日期查找
find assets/research-reports/ -name "2025-08*" -type f

# 按类型查找
find _drafts/ -name "*vip4*" -type f
```

### 备份和恢复
```bash
# 重要草稿备份
tar -czf drafts_backup_$(date +%Y%m%d).tar.gz _drafts/vip4-preparation/

# 研究报告备份
tar -czf reports_backup_$(date +%Y%m%d).tar.gz assets/research-reports/
```

---

## 📊 质量控制标准

### 内容质量要求
**VIP准备内容**:
- 原创分析占比 ≥ 70%
- 专业数据支撑完整
- 逻辑结构清晰合理
- 实用价值明确

**项目管理文档**:
- 经验总结完整
- 流程描述清晰  
- 可复制性强
- 持续改进价值

### 技术质量要求
**文档格式**:
- Front Matter完整规范
- Markdown语法正确
- 图片链接有效
- 文件编码UTF-8

**命名规范**:
- 符合命名约定
- 描述性强
- 检索友好
- 版本区分清晰

---

## 🔍 最佳实践示例

### 成功案例：Tesla投资系列
**原始状态**:
```
_drafts/
├── tesla-vip2-sa-data-analysis.md
├── tesla-vip3-ark-strategy-analysis.md  
├── tesla-teslamate-investment-guide.md
├── argus-tesla20250814.pdf
├── cfra-tesla.pdf
└── morning star-tesla.pdf
```

**处理过程**:
1. 发布VIP2和VIP3文档到 `_posts/`
2. 移动未用内容到 `vip4-preparation/`
3. 重命名PDF为标准格式移至 `assets/research-reports/tesla/`
4. 删除已充分利用的草稿
5. 更新.gitignore排除PDF

**最终状态**:
```
_posts/
├── 2025-08-16-tesla-vip2-sa-professional-analysis.md
└── 2025-08-16-tesla-vip3-ark-strategy-complete.md

_drafts/vip4-preparation/
├── musk-2025-key-interviews-analysis.md
├── tesla-open-source-ecosystem-investment-framework.md
└── tesla-vip2-complete-analysis-package.md

assets/research-reports/tesla/
├── 2025-08-14_argus-research_tesla-analysis_HOLD-273.pdf
├── 2025-08-15_cfra-research_tesla-analysis_HOLD-300.pdf
└── 2025-08-15_morningstar_tesla-analysis_2STAR-250.pdf
```

**成功要素**:
- 价值最大化：每个素材都得到充分利用
- 结构化管理：按价值和状态分类存储
- 版权保护：PDF文档排除在版本控制外
- 命名规范：便于后期查询和管理

### 失败案例警示
**常见问题**:
- 草稿积压过多，难以管理
- 文件命名混乱，查找困难
- 版权风险，PDF文档误提交
- 价值内容丢失，重复工作

**预防措施**:
- 定期清理维护
- 严格执行命名规范
- 配置.gitignore保护
- 建立备份机制

---

## 📈 持续改进计划

### 短期目标 (1-3个月)
- [ ] 完善自动化清理脚本
- [ ] 建立内容价值评估标准
- [ ] 优化文件检索效率
- [ ] 制定版权使用指南

### 中期目标 (3-6个月)  
- [ ] 开发草稿管理Dashboard
- [ ] 集成内容质量检查工具
- [ ] 建立用户反馈收集机制
- [ ] 完善备份和恢复流程

### 长期目标 (6-12个月)
- [ ] 实现智能内容推荐
- [ ] 建立知识图谱系统
- [ ] 开发内容价值预测模型
- [ ] 构建完整的内容生态系统

---

**📝 文档维护**: 本规范每季度更新一次，根据实际使用情况持续优化  
**📞 问题反馈**: 如发现规范不当或需要改进的地方，请及时反馈

---

*本文档遵循有心工坊内容创作规范，版权所有 © 2025*