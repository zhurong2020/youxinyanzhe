# 会员系统使用指南

## 系统概述

本会员系统为您的Jekyll博客提供了完整的付费会员功能，包括：
- 多级会员验证系统
- 用户信息收集和管理
- 自动化访问码生成和邮件发送
- 会员数据统计和导出

## 快速开始

### 1. 环境配置

1. **复制配置文件**：
   ```bash
   cp .env.example .env
   ```

2. **配置邮件服务**：
   编辑 `.env` 文件，设置您的邮件配置：
   ```
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   FROM_EMAIL=your-email@gmail.com
   ```

3. **安装Python依赖**：
   ```bash
   # 如果没有安装python-dotenv
   pip install python-dotenv
   ```

### 2. 页面部署

系统已创建了以下页面：
- `/members/` - 会员专区主页面
- `/member-signup/` - 会员信息收集表单

这些页面会自动被Jekyll构建，无需额外配置。

### 3. 会员管理工作流

#### 3.1 用户注册流程
1. 用户在微信公众号完成打赏
2. 用户访问 `/member-signup/` 填写信息
3. 管理员处理注册并发送访问码
4. 用户使用访问码访问会员内容

#### 3.2 管理员处理流程

**查看待处理注册**：
```bash
python scripts/member_management.py stats
```

**批量处理注册（生成访问码并发送邮件）**：
```bash
python scripts/member_management.py process
```

**只生成访问码不发送邮件**：
```bash
python scripts/member_management.py process --no-email
```

**手动生成单个访问码**：
```bash
python scripts/member_management.py generate --level monthly --email user@example.com
```

**验证访问码**：
```bash
python scripts/member_management.py validate --code VIP2_20250831_A7K9
```

**导出会员数据**：
```bash
python scripts/member_management.py export
```

## 会员等级配置

| 等级 | 代码 | 价格 | 有效期 | 美元等值 | 每月成本 | 权限 |
|------|------|------|--------|----------|----------|------|
| 体验会员 | VIP1 | ¥35 | 7天 | ~$5 | - | SA随机报告体验 |
| 月度会员 | VIP2 | ¥108 | 30天 | ~$15 | ¥108 | SA精选报告+量化评级 |
| 季度会员 | VIP3 | ¥288 | 90天 | ~$40 | ¥96 | 专家分析+组合诊断 |
| 年度会员 | VIP4 | ¥720 | 365天 | ~$100 | ¥60 | 网格软件+策略代码 |

## 访问码格式

访问码格式：`LEVEL_EXPIRY_RANDOM`
- `LEVEL`：会员等级代码（VIP1-VIP4）
- `EXPIRY`：过期日期（YYYYMMDD）
- `RANDOM`：4位随机字符串

示例：`VIP3_20250831_B2M5`（季度会员，2025年8月31日过期）

## 内容创作指南

### 在会员页面添加新内容

编辑 `members.md` 文件，在 `<div id="member-content">` 区域内添加新的内容板块：

```markdown
### 🆕 新增专题内容
- **投资组合优化**：最新的资产配置策略
- **AI工具测评**：深度评测和使用指南
```

### 内容分级显示

系统会根据会员等级自动过滤内容：
- 包含"专享VIP"或"个人投资组合"的内容只对季度/年度会员显示
- 可通过修改JavaScript代码调整过滤规则

### 在现有文章添加会员内容

在文章中添加会员专享区块：
```markdown
<!-- 公开内容 -->
这里是免费可见的内容...

<!-- 会员专享内容 -->
<div class="member-only" data-level="monthly">
这里是月度会员及以上可见的内容...
</div>
```

## 数据管理

### 数据存储位置
- 注册信息：`.tmp/member_data/registrations.json`
- 访问码记录：`.tmp/member_data/access_codes.json`
- 邮件日志：`.tmp/member_data/email_log.json`

### 数据备份
定期备份 `.tmp/member_data/` 目录：
```bash
tar -czf member_data_backup_$(date +%Y%m%d).tar.gz .tmp/member_data/
```

### 数据清理
清理过期的访问码和注册记录：
```python
# 可在member_management.py中添加清理功能
def cleanup_expired_data():
    # 清理逻辑
    pass
```

## 安全注意事项

1. **环境变量保护**：
   - 确保 `.env` 文件不被提交到Git
   - 使用强密码和应用专用密码

2. **访问码安全**：
   - 定期更换访问码格式
   - 监控异常访问模式

3. **数据隐私**：
   - 只收集必要的用户信息
   - 遵守数据保护法规

## 自定义和扩展

### 添加新的会员等级
在 `member_management.py` 中修改 `member_levels` 配置：
```python
self.member_levels = {
    'premium': {'code': 'VIP5', 'days': 30, 'price': 199, 'name': '高级会员'},
    # 注意：实际使用的价格配置已更新为：
    # 'experience': 35, 'monthly': 108, 'quarterly': 288, 'yearly': 720
    # ... 其他等级
}
```

### 自定义邮件模板
修改 `send_access_code_email` 方法中的邮件正文模板。

### 集成支付API
可扩展系统集成微信支付、支付宝等API，实现自动化支付验证。

## 故障排除

### 常见问题

**Q: 邮件发送失败**
A: 检查邮件配置，确保：
- SMTP设置正确
- 应用专用密码有效
- 网络连接正常

**Q: 访问码验证失败**
A: 检查：
- 访问码格式是否正确
- 是否已过期
- JavaScript控制台是否有错误

**Q: 页面样式异常**
A: 确保：
- Jekyll主题支持自定义CSS
- 浏览器缓存已清理

### 调试模式
在开发环境中启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 更新和维护

### 定期任务
1. 检查过期会员并发送续费提醒
2. 分析会员数据优化定价策略
3. 更新内容提升会员价值
4. 备份重要数据

### 版本升级
更新系统时注意：
- 备份现有数据
- 测试新功能
- 逐步发布更新

---

如有问题，请查看系统日志或联系技术支持。