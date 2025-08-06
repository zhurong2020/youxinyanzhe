# 🧪 会员系统测试验证码快速指南

## 📋 当前可用的测试验证码

### 🔑 长期测试码 (适合功能开发)

```bash
# 管理员验证码 (10年有效)
ADMIN_20350804_MGR8KYD

# 体验会员 (7天有效)
VIP1_20250813_T1EJXM

# 月度会员 (30天有效)
VIP2_20250905_TIM0FU

# 季度会员 (90天有效)
VIP3_20251104_T1DKX3

# 年度会员 (365天有效)
VIP4_20260806_TB9VQX
```

### ⚡ 短期测试码 (适合快速测试)

```bash
# 7天有效的VIP2测试码
VIP2_20250813_TPV5UD

# 30天有效的管理员码
ADMIN_20250905_ADMW4JU
```

## 🛠️ 生成新验证码

### 生成完整套装
```bash
python scripts/tools/generate_test_codes.py
```

### 生成单个验证码
```bash
# 生成30天有效的VIP2验证码
python scripts/tools/generate_test_codes.py single VIP2 30

# 生成90天有效的VIP3验证码
python scripts/tools/generate_test_codes.py single VIP3 90

# 生成管理员验证码
python scripts/tools/generate_test_codes.py single ADMIN
```

## 🧭 测试场景建议

### 1. 基础功能测试
- 使用 `VIP1_20250813_T1EJXM` 测试体验会员内容显示
- 使用 `VIP2_20250905_TIM0FU` 测试月度会员功能

### 2. 权限级别测试
- 测试不同会员等级看到的内容差异
- 验证高等级会员可以访问低等级内容

### 3. 过期处理测试
- 使用短期测试码验证过期后的行为
- 测试过期提醒和续费提示

### 4. 管理功能测试
- 使用管理员码测试后台管理功能
- 验证管理员权限和普通会员权限的区别

## 📱 快速测试流程

1. **打开会员页面**: `/members/`
2. **输入验证码**: 从上面复制任意适合的验证码
3. **验证访问**: 确认对应等级内容正常显示
4. **测试Analytics**: 检查Google Analytics中的member_access事件

## ⚠️ 重要提醒

- 🚫 **不要在生产环境使用这些测试码**
- 🔒 **不要将.env文件提交到Git**
- 🗑️ **部署前删除所有测试验证码**
- 🔄 **定期更新测试验证码保持新鲜**

## 📞 故障排除

### 验证码无效？
1. 检查验证码格式是否正确
2. 确认是否已过期
3. 清除浏览器缓存重试

### 内容不显示？
1. 检查浏览器控制台是否有JavaScript错误
2. 确认网页完全加载后再输入验证码
3. 验证Analytics事件是否正常发送

---

**工具位置**: `scripts/tools/generate_test_codes.py`  
**最后更新**: 2025-08-06  
**维护者**: 管理员