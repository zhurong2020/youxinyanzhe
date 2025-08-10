# OneDrive图床系统安全配置指南

## 🚨 安全警告

**重要**: OneDrive OAuth凭据包含敏感信息，必须妥善保护！

## 安全配置步骤

### 1. 重新生成Azure应用密钥

⚠️ **当前密钥已泄露，必须重新生成！**

1. 访问 [Azure Portal](https://portal.azure.com/)
2. 进入 **App registrations** → **YouXinYanZhe-BlogImageManager**
3. 点击 **Certificates & secrets**
4. **删除现有密钥**: `BlogImageManager-Secret-2025`
5. **生成新密钥**:
   - 点击 **+ New client secret**
   - 描述: `BlogImageManager-Secret-2025-New`
   - 过期时间: 24个月
   - 点击 **Add**
6. **立即复制密钥值**（只显示一次）

### 2. 本地安全配置

1. **复制示例配置文件**:
   ```bash
   cp config/onedrive_config.example.json config/onedrive_config.json
   ```

2. **填入真实凭据**:
   ```json
   {
     "auth": {
       "tenant_id": "438e2517-218a-479e-9d6a-26273849f10c",
       "client_id": "000539fa-2f28-4bd1-b539-137dafc38cc4",
       "client_secret": "YOUR_NEW_CLIENT_SECRET_HERE",
       "redirect_uri": "http://localhost:8080/callback",
       "scopes": ["Files.ReadWrite", "offline_access"]
     }
   }
   ```

3. **验证.gitignore**:
   ```bash
   # 确认这些行在.gitignore中
   config/onedrive_tokens.json
   config/onedrive_config.json
   ```

### 3. 重新运行OAuth认证

```bash
# 删除旧的令牌文件（如果存在）
rm -f config/onedrive_tokens.json

# 重新运行认证
python3 scripts/tools/onedrive_blog_images.py --setup
```

### 4. 安全检查清单

- [ ] ✅ 已重新生成Azure应用密钥
- [ ] ✅ 已删除旧的客户端密钥  
- [ ] ✅ 已创建新的config/onedrive_config.json
- [ ] ✅ 已验证.gitignore包含OneDrive配置文件
- [ ] ✅ 已重新运行OAuth认证
- [ ] ✅ 已测试图片上传功能正常

## 安全最佳实践

### ✅ 应该做的

- **永远不要**将包含密钥的配置文件提交到Git
- **定期轮换**API密钥（建议每6个月）
- **使用最小权限**原则配置OAuth scope
- **监控**Azure应用的使用情况

### ❌ 不应该做的

- 不要在任何文档中记录真实密钥
- 不要通过聊天工具分享配置文件
- 不要在公共环境中运行OAuth认证
- 不要忽略Azure的安全警告

## 紧急响应

如果发现密钥泄露：

1. **立即撤销**Azure中的客户端密钥
2. **生成新密钥**并更新本地配置
3. **检查日志**查看是否有异常访问
4. **更新文档**记录安全事件

## 监控和维护

### 定期检查
- Azure应用使用统计
- OneDrive存储使用量
- 系统日志中的错误信息

### 令牌管理
- `config/onedrive_tokens.json` 会自动刷新
- 如认证失败，删除该文件重新认证
- 保持系统时间准确（令牌有时效性）

---

**文档版本**: v1.0  
**最后更新**: 2025-08-10  
**维护者**: 系统管理员