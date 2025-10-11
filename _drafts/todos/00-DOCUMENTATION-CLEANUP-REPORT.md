# 📋 规划文档清理报告

**生成日期**: 2025-10-11
**目的**: 识别重复、过期文档，优化内容规划体系

---

## ✅ 已完成的更新

### 1. 修正重复规划
- **问题**: 10/29规划发布《为何普通人应该现在就开始投资美股？》
- **实际**: 该文章已于2025-06-16发布（`2025-06-16-putongrentouzimeigu.md`）
- **解决**:
  - ✅ 更新 `00-CONTENT-PUBLISHING-ROADMAP.md` - 删除10/29重复规划
  - ✅ 更新 `00-PUBLISHED-ARTICLES-REGISTRY.md` - 补充完整30篇已发布文章清单
  - ✅ 更新 `00-CONTENT-INTEGRATION-ANALYSIS.md` - 修正整合分析

### 2. 补充已发布文章清单
新增完整的30篇已发布文章信息：
- 💰 投资理财：9篇（含认知启蒙）
- 🌍 全球视野：8篇（Tesla系列 + Joe Rogan访谈）
- 🛠️ 技术赋能：3篇（VPS系列）
- 🧠 认知升级：5篇（信息素养 + 政治观察）
- 📺 英语学习：4篇
- 其他：1篇

---

## 📂 规划文档现状分析

### 核心规划文档（活跃使用）

| 文档名称 | 大小 | 用途 | 状态 |
|---------|------|------|------|
| `00-CONTENT-PUBLISHING-ROADMAP.md` | 21K | **Q4+2026发布计划** | ✅ 已更新 |
| `00-PUBLISHED-ARTICLES-REGISTRY.md` | 12K | **已发布文章登记** | ✅ 已更新 |
| `00-CONTENT-INTEGRATION-ANALYSIS.md` | 15K | **TO_CONTENT整合分析** | ✅ 已更新 |
| `00-CONTENT-PROMISES-TRACKER.md` | 3.6K | **预告追踪表** | 🟢 活跃 |
| `00-CONTENT-HOOKS-SOP.md` | 4.4K | **钩子管理流程** | 🟢 活跃 |
| `DEDUPLICATED-ARTICLES-REGISTRY.md` | 16K | **去重分析报告** | 🟢 参考 |

### 辅助规划文档（可考虑合并或归档）

| 文档名称 | 大小 | 用途 | 建议 |
|---------|------|------|------|
| `00-CONTENT-CREATION-ROADMAP-V2.1.md` | 12K | Gridea迁移计划 | ⚠️ 与PUBLISHING-ROADMAP重复 |
| `BLOG_PUBLISHING_MASTER_PLAN.md` | 11K | Q1-Q2总计划（创建于9/19） | ⚠️ 过期，已被新规划替代 |
| `00-CONTENT-STRATEGY-FRAMEWORK.md` | 7.6K | 内容战略框架 | 🟢 保留，战略指导 |
| `published_articles_auto_generated.md` | 5.0K | 自动生成的已发布清单 | ⚠️ 与REGISTRY重复 |

### 运营支撑文档（保留）

| 文档名称 | 大小 | 用途 | 状态 |
|---------|------|------|------|
| `meta-business-model.md` | 8.7K | 商业模式 | 🟢 保留 |
| `meta-content-system.md` | 9.4K | 内容体系 | 🟢 保留 |
| `meta-marketing-strategy.md` | 7.3K | 营销策略 | 🟢 保留 |
| `meta-media-matrix.md` | 6.4K | 媒体矩阵 | 🟢 保留 |
| `meta-publishing-timeline.md` | 5.6K | 发布时间线 | 🟢 保留 |
| `meta-wechat-group.md` | 2.8K | 微信群设置 | 🟢 保留 |
| `meta-wechat-moments.md` | 3.0K | 朋友圈文案 | 🟢 保留 |

### TO_CONTENT_PROJECT文档（参考素材，保留）

```
TO_CONTENT_PROJECT/
├── blog/（4个文件）- 量化投资进阶路径、策略矩阵、5策略体系
├── business/（4个文件）- 商业模式、营销策略、高级功能、融资需求
├── community/（14个文件）- 微信群管理、客服FAQ、支付系统、服务协议
├── compliance/（2个文件）- 合规运营、免责声明
├── marketing/（1个文件）- 媒体矩阵整合
└── promotion/（2个文件）- 发布检查清单、推广总结
```

**建议**: 保留所有TO_CONTENT文档作为参考素材库

---

## 🔄 建议的清理操作

### 立即归档（移至 `_drafts/archived/`）

#### 1. `BLOG_PUBLISHING_MASTER_PLAN.md`
- **原因**: 创建于2025-09-19，规划Q1-Q2内容，已被新规划替代
- **内容价值**: 包含40篇博文计划，但时间线过期
- **归档路径**: `_drafts/archived/planning/BLOG_PUBLISHING_MASTER_PLAN_2025-09-19.md`

#### 2. `published_articles_auto_generated.md`
- **原因**: 与 `00-PUBLISHED-ARTICLES-REGISTRY.md` 功能重复
- **内容价值**: 自动生成的简单清单，信息不如手工维护的REGISTRY完整
- **归档路径**: `_drafts/archived/planning/published_articles_auto_generated.md`

### 考虑合并

#### 3. `00-CONTENT-CREATION-ROADMAP-V2.1.md` ← 合并到主规划
- **问题**: 与 `00-CONTENT-PUBLISHING-ROADMAP.md` 内容重叠
- **价值**: 包含Gridea迁移的详细计划（21篇高价值文章清单）
- **建议**:
  - 将"高价值待迁移清单"部分保留在独立文档
  - 删除与PUBLISHING-ROADMAP重复的Q4规划部分
  - 重命名为 `GRIDEA-MIGRATION-PRIORITY-LIST.md`

---

## 📊 文档体系优化后的结构

### 层级1：核心规划（必读）
```
00-CONTENT-PUBLISHING-ROADMAP.md        # Q4+2026发布计划（主规划）
00-PUBLISHED-ARTICLES-REGISTRY.md       # 已发布30篇文章登记表
00-CONTENT-PROMISES-TRACKER.md          # 预告追踪（9个预告，3个已兑现）
00-CONTENT-HOOKS-SOP.md                 # 钩子管理SOP
```

### 层级2：战略指导（参考）
```
00-CONTENT-STRATEGY-FRAMEWORK.md        # 内容战略框架
00-CONTENT-INTEGRATION-ANALYSIS.md      # TO_CONTENT整合分析
DEDUPLICATED-ARTICLES-REGISTRY.md       # 去重分析（16篇已迁移，64篇待迁移）
GRIDEA-MIGRATION-PRIORITY-LIST.md       # Gridea迁移优先级清单（待创建）
```

### 层级3：运营支撑（执行）
```
meta-business-model.md                  # 商业模式
meta-content-system.md                  # 内容体系
meta-marketing-strategy.md              # 营销策略
meta-media-matrix.md                    # 媒体矩阵
meta-publishing-timeline.md             # 发布时间线
meta-wechat-group.md                    # 微信群设置
meta-wechat-moments.md                  # 朋友圈文案
system-*.md                             # 系统配置（3个文件）
```

### 层级4：素材库（备查）
```
TO_CONTENT_PROJECT/                     # 27个参考文档
investment-finance/                     # 17个投资理财类草稿
tech-empowerment/                       # 技术赋能类草稿
```

---

## ✅ 执行计划

### 第1步：归档过期文档（立即执行）
```bash
# 创建归档目录
mkdir -p _drafts/archived/planning

# 归档过期文档
mv _drafts/todos/BLOG_PUBLISHING_MASTER_PLAN.md \
   _drafts/archived/planning/BLOG_PUBLISHING_MASTER_PLAN_2025-09-19.md

mv _drafts/todos/published_articles_auto_generated.md \
   _drafts/archived/planning/published_articles_auto_generated.md
```

### 第2步：重构迁移规划文档（待执行）
1. 提取 `00-CONTENT-CREATION-ROADMAP-V2.1.md` 中的"高价值待迁移清单（21篇）"
2. 创建新文档 `GRIDEA-MIGRATION-PRIORITY-LIST.md`
3. 归档原 `00-CONTENT-CREATION-ROADMAP-V2.1.md`

### 第3步：更新README索引（待执行）
在 `_drafts/todos/system-readme.md` 中：
- 添加新的文档结构说明
- 标注各文档的用途和优先级
- 提供快速导航链接

---

## 📝 后续维护建议

### 文档命名规范
- `00-` 前缀：核心规划文档（最高优先级）
- `meta-` 前缀：运营支撑文档
- `system-` 前缀：系统配置文档
- 无前缀：素材和草稿

### 更新频率
- **核心规划**：每次发布新文章后立即更新
- **战略指导**：每月1日review
- **运营支撑**：按需更新
- **素材库**：持续补充

### 归档策略
- 超过3个月未更新的规划文档 → 考虑归档
- 已被新规划替代的文档 → 立即归档
- 归档时保留创建日期在文件名中

---

## 🎯 优化效果预期

### 减少混淆
- ✅ 消除重复规划（10/29认知启蒙文章）
- ✅ 明确唯一的发布计划来源（PUBLISHING-ROADMAP）
- ✅ 避免查找时在多个文档间切换

### 提高效率
- ✅ 核心文档数量减少：10个 → 4个
- ✅ 文档层级清晰：核心 → 战略 → 运营 → 素材
- ✅ 快速定位所需信息

### 保持一致性
- ✅ 单一事实来源（Single Source of Truth）
- ✅ 已发布文章唯一登记表
- ✅ 发布计划唯一规划文档

---

**维护责任**: 每次更新规划后更新本报告
**下次review**: 2025-11-01
