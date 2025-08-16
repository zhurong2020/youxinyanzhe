# VIP文章创作检查清单

**创建日期**: 2025-08-16  
**目的**: 确保VIP文章创作时不遗漏关键字段，访问控制正常工作

## 🔐 VIP文章必需字段检查

### 1. Front Matter 必需字段 ✅
```yaml
---
layout: member-post          # ⚠️ 必需！启用会员访问控制
title: "VIP2专享：文章标题"    # ⚠️ 建议包含VIP等级标识
date: 2025-08-16
categories: [分类, VIP专享]
tags: [标签1, 标签2, VIP2]    # ⚠️ 建议包含VIP等级标签
header:
  teaser: "{{ site.baseurl }}/assets/images/teaser.jpg"
excerpt: "50-60字符的摘要内容"  # ⚠️ 必需，用于SEO和首页预览
member_tier: monthly         # ⚠️ 必需！决定访问等级
estimated_reading_time: 15分钟
last_updated: 2025-08-16
---
```

### 2. 会员等级映射 ✅
| 用户显示 | 技术字段 | 价格 | 权限层级 |
|---------|---------|------|---------|
| VIP1体验会员 | `experience` | 免费 | 1级 |
| VIP2月度会员 | `monthly` | ¥99/月 | 2级 |
| VIP3季度会员 | `quarterly` | ¥288/季 | 3级 |
| VIP4年度会员 | `yearly` | ¥1999/年 | 4级 |

## 🔧 自动化检查机制

### 1. ContentPipeline 验证 ✅
当前系统在草稿质量检查时会自动验证：
- ✅ `layout: member-post` 字段存在性
- ✅ `member_tier` 值的合法性
- ✅ 标题是否包含VIP等级标识
- ✅ 访问控制完整性

### 2. VIP内容创建器修复 ✅
`scripts/tools/content/vip_content_creator.py` 已修复：
- ✅ 自动添加 `layout: member-post`
- ✅ 正确设置 `member_tier` 字段
- ✅ 生成符合规范的Front Matter

## 📋 创作工作流程检查清单

### 创作阶段 📝
- [ ] 使用正确的VIP内容创作工具 (菜单: 3 → 5 → VIP多层内容创作)
- [ ] 确认目标会员等级 (VIP2/VIP3/VIP4)
- [ ] 标题包含VIP等级标识
- [ ] 设置合适的内容长度目标

### 草稿完成 🔍  
- [ ] 运行草稿质量检查 (菜单: 2 → 内容规范化处理)
- [ ] 确认无VIP相关警告信息
- [ ] 验证Front Matter所有必需字段

### 发布前检查 🚀
- [ ] 确认 `layout: member-post` 存在
- [ ] 确认 `member_tier` 设置正确
- [ ] 测试访问控制 (使用测试访问码)
- [ ] 验证会员验证界面正常显示

### 发布后验证 ✅
- [ ] 访问文章页面确认显示会员验证界面
- [ ] 使用对应等级测试码验证解锁功能
- [ ] 确认内容在验证后正常显示

## 🧪 测试访问码

### 当前可用测试码:
- **VIP2测试**: `VIP2_20250915_TBOMUC` (有效至2025-09-15)
- **VIP3测试**: `VIP3_20251114_TF41A4` (有效至2025-11-14)  
- **VIP4测试**: `VIP4_20260816_TB48UO` (有效至2026-08-16)
- **管理员**: `ADMIN_20350814_MGRH803` (有效至2035-08-14)

### 生成新测试码:
```bash
# 生成所有等级测试码
python scripts/tools/generate_test_codes.py

# 生成特定等级测试码
python scripts/tools/generate_test_codes.py single VIP3 90
```

## ⚠️ 常见问题和解决方案

### 1. 文章可以直接访问 (最常见)
**原因**: 缺少 `layout: member-post`
**解决**: 在Front Matter中添加该字段

### 2. 验证码无效
**原因**: 使用了过期或错误格式的验证码
**解决**: 生成新的测试访问码

### 3. 权限等级不匹配
**原因**: `member_tier` 设置错误
**解决**: 确认使用技术字段值 (monthly/quarterly/yearly)

### 4. 标题不规范
**原因**: 标题缺少VIP等级标识
**建议**: 包含 "VIP2专享"、"VIP3专享" 等明确标识

## 🔄 持续改进建议

1. **模板标准化**: 为每个VIP等级创建标准模板
2. **自动化验证**: 在发布流程中增加强制VIP字段检查
3. **测试自动化**: 定期验证测试访问码的有效性
4. **文档同步**: 确保新功能及时更新到检查清单

---

**最后更新**: 2025-08-16  
**负责人**: 系统管理员  
**相关文档**: 
- `docs/MEMBER_CONTENT_MANAGEMENT_SYSTEM.md`
- `docs/MEMBER_CONTENT_RULES_AND_STANDARDS.md`