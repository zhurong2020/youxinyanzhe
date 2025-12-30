# API密钥注册表

本文档记录项目中使用的各类API密钥信息，便于管理和追踪。

⚠️ **安全提示**: 本文档仅记录密钥的元数据（项目信息、创建时间等），实际密钥值存储在 `.env` 文件中（已加入 `.gitignore`）

## Google Gemini API 密钥

### 当前激活密钥

#### 密钥 #1 (vscode项目)
- **密钥后缀**: `...hXDE1k`
- **完整密钥**: [已移除 - 存储在 .env 文件中]
- **项目名称**: vscode
- **Google Cloud项目**: `projects/783808103449`
- **项目编号**: 783808103449
- **创建时间**: 2025-10-11
- **创建位置**: [Google AI Studio](https://aistudio.google.com/)
- **配额类型**: Free Tier (50次/天)
- **状态**: ✅ 激活中
- **用途**: VSCode Claude Code开发环境使用

#### 密钥 #2 (历史密钥)
- **密钥后缀**: `...ox4J7yc`
- **完整密钥**: [已移除 - 存储在 .env 文件中]
- **项目名称**: workshop (推测)
- **创建时间**: 未知 (早期创建)
- **配额类型**: Free Tier (50次/天)
- **状态**: ✅ 有效（备用）
- **说明**: 原项目密钥，仍然有效，可作为备用

### 配额管理策略

#### Free Tier限制
- **每日请求数**: 50次/天
- **重置时间**: 太平洋时间午夜 (北京时间下午4点)
- **每分钟请求**: 5 RPM (gemini-2.5-pro)
- **每分钟token**: 125,000 TPM

#### 智能配额管理
项目已实现 **Claude+Gemini智能协同系统**，详见 `docs/TECHNICAL_ARCHITECTURE.md`：
- 自动检测配额状态
- 配额耗尽时自动切换到Claude
- 多密钥轮换机制（未来实现）

#### 升级到付费层级

如需更高配额，可通过以下步骤升级：

1. **访问 Google AI Studio**: https://aistudio.google.com/
2. **启用Cloud Billing**: 绑定信用卡（有$300免费额度）
3. **自动升级到Tier 1**:
   - 150 RPM
   - 2,000,000 TPM
   - 移除每日50次限制

参考文档: https://ai.google.dev/gemini-api/docs/rate-limits

### Google One AI Pro订阅说明

⚠️ **重要**: Google One AI Pro订阅 **不等于** Gemini API付费层级

- **Google One AI Pro**: 消费者产品订阅（2TB存储 + AI功能增强）
- **Gemini API Tier 1+**: 需要单独的Cloud Billing账户

即使订阅了Google One AI Pro，API仍然使用Free Tier配额，除非单独启用Cloud Billing。

## 其他API密钥

### Azure TTS (语音合成)
- **配置位置**: `.env` 文件中的 `AZURE_TTS_KEY`
- **服务区域**: 存储在 `AZURE_TTS_REGION`
- **用途**: 播客和YouTube视频的语音生成

### YouTube Data API
- **配置位置**: OAuth 2.0认证
- **凭据文件**: `client_secrets.json` (已加入 `.gitignore`)
- **用途**: YouTube视频上传和管理

### OneDrive API (Workshop 图床)
- **配置位置**: OAuth 2.0认证
- **凭据文件**: `onedrive_credentials.json` (已加入 `.gitignore`)
- **用途**: 图床文件管理

### OneDrive API (VPS 服务器)
- **Azure 应用名称**: onedrive-msft
- **Client ID**: `dede9e56-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (完整信息见 vpsserver 仓库)
- **Client Secret 名称**: `rclone20251230`
- **Client Secret 创建日期**: 2025-12-30
- **Client Secret 到期日期**: ⚠️ **2027-12-30** (请在到期前续期)
- **配置位置**: VPS 服务器 (详见 vpsserver 仓库文档)
- **用途**: VPS 备份 (Trilium)、论文周报存储
- **相关服务**:
  - Trilium 每日备份 (03:00)
  - 论文周报存储 (每周一 08:00)
- **续期提醒**: 建议在 2027-11-30 前更新 Client Secret
- **详细配置**: 见 `vpsserver/docs/ONEDRIVE_CONFIG.md` (private 仓库)

## 密钥安全管理

### 当前实践
1. ✅ 所有密钥存储在 `.env` 文件
2. ✅ `.env` 已加入 `.gitignore`
3. ✅ OAuth凭据文件已排除版本控制
4. ✅ 代码中不包含硬编码密钥

### 未来计划
- **Azure Key Vault集成**: 统一密钥管理 (参见 `docs/AZURE_INTEGRATION_ROADMAP.md`)
- **环境隔离**: 开发/生产环境分离
- **密钥轮换**: 定期更新密钥

## 更新历史

- **2025-12-30**: 添加 VPS OneDrive API (Azure) 密钥信息，记录到期日期 (2027-12-30)
- **2025-10-11**: 创建文档，记录两个Gemini API密钥
- **2025-10-11**: 添加Google One AI Pro订阅说明
- **2025-10-11**: 添加配额管理和升级指南

---

**相关文档**:
- `docs/TECHNICAL_ARCHITECTURE.md` - Claude+Gemini智能协同系统
- `docs/AZURE_INTEGRATION_ROADMAP.md` - Azure Key Vault集成计划
- `.env.example` - 环境变量配置示例
