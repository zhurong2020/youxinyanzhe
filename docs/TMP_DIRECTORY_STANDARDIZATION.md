# 临时目录规范化方案

## 当前状况分析

### 存在的两个tmp目录：
1. **根目录 `.tmp/`** - 项目级临时文件
2. **脚本目录 `scripts/.tmp/`** - 脚本专用临时文件

### 当前使用情况：

#### `.tmp/` (根目录)
```
.tmp/
├── claude_exchange/      # Claude交互数据
├── member_data/          # 会员数据
└── output/
    └── inspiration_reports/  # 灵感报告
```

#### `scripts/.tmp/`
```
scripts/.tmp/
└── output/
    ├── wechat_guides/       # 微信发布指南
    └── wechat_image_cache/  # 微信图片缓存
```

## 🎯 推荐的最佳实践

### 统一使用根目录 `.tmp/`

**理由：**
1. **单一真相源** - 所有临时文件在一个地方
2. **更容易管理** - 统一的清理和备份策略
3. **避免混淆** - 开发者不需要记住多个位置
4. **Git友好** - 只需要一个.gitignore规则

### 建议的目录结构：

```
.tmp/                           # 所有临时文件的根目录
├── cache/                      # 缓存文件
│   ├── wechat_images/         # 微信图片缓存
│   ├── api_responses/         # API响应缓存
│   └── processed_content/     # 处理过的内容缓存
├── output/                     # 输出文件
│   ├── wechat_guides/         # 微信发布指南
│   ├── youtube_videos/        # YouTube视频
│   ├── inspiration_reports/   # 灵感报告
│   └── member_packages/       # 会员内容包
├── session/                    # 会话数据
│   ├── claude_exchange/       # Claude交互
│   └── image_processing/      # 图片处理会话
└── data/                       # 临时数据
    ├── member_data/           # 会员数据
    └── drafts_backup/         # 草稿备份
```

## 📋 迁移计划

### 第一步：创建统一结构
```python
# 在 ContentPipeline.__init__ 中
self.tmp_root = Path(".tmp")
self.cache_dir = self.tmp_root / "cache"
self.output_dir = self.tmp_root / "output"
self.session_dir = self.tmp_root / "session"
self.data_dir = self.tmp_root / "data"

# 确保目录存在
for dir in [self.cache_dir, self.output_dir, self.session_dir, self.data_dir]:
    dir.mkdir(parents=True, exist_ok=True)
```

### 第二步：更新路径引用
1. **微信发布器**：
   - 旧：`project_root / ".tmp/output/wechat_image_cache"`
   - 新：`project_root / ".tmp/cache/wechat_images"`

   - 旧：`project_root / ".tmp/output/wechat_guides"`
   - 新：`project_root / ".tmp/output/wechat_guides"`

2. **其他模块**：
   - 统一使用 `.tmp/` 根目录下的相应子目录

### 第三步：数据迁移
```bash
# 迁移脚本
mv scripts/.tmp/output/wechat_guides/* .tmp/output/wechat_guides/
mv scripts/.tmp/output/wechat_image_cache/* .tmp/cache/wechat_images/
```

### 第四步：清理旧目录
```bash
# 确认迁移成功后
rm -rf scripts/.tmp
```

## 🔧 实施建议

### 立即行动：
1. **保持现状** - 暂时不迁移，避免破坏现有功能
2. **记录决策** - 在CLAUDE.md中添加临时目录使用规范
3. **渐进迁移** - 新功能使用`.tmp/`，旧功能逐步迁移

### 长期计划：
1. **创建配置文件** - `config/paths.yml` 集中管理所有路径
2. **路径工具类** - 创建 `PathManager` 类统一管理
3. **自动清理** - 添加定期清理临时文件的脚本

## 📝 配置示例

`config/paths.yml`:
```yaml
tmp:
  root: ".tmp"
  cache:
    wechat_images: ".tmp/cache/wechat_images"
    api_responses: ".tmp/cache/api_responses"
  output:
    wechat_guides: ".tmp/output/wechat_guides"
    youtube_videos: ".tmp/output/youtube_videos"
  session:
    claude: ".tmp/session/claude_exchange"
  data:
    members: ".tmp/data/member_data"
```

## ⚠️ 注意事项

1. **Git忽略规则** - 确保`.gitignore`包含：
   ```
   .tmp/
   scripts/.tmp/  # 迁移期间
   ```

2. **权限管理** - 敏感数据目录需要适当的权限设置

3. **备份策略** - 重要的临时数据需要定期备份

4. **文档更新** - 更新所有相关文档中的路径引用

## 总结

**推荐方案**：统一使用根目录 `.tmp/` 作为所有临时文件的存储位置，这是业界最佳实践，符合大多数项目的约定。