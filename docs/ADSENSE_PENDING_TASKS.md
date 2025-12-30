# Google AdSense 待办任务

> 创建时间: 2025-12-29
> 状态: 等待Google审核通过

## 当前状态

| 网站 | ads.txt | 验证代码 | 审核状态 |
|------|---------|----------|----------|
| arong.eu.org | ✅ 已授权 | ✅ 已部署 | 🟡 正在准备 |
| zhurong2020.github.io | ✅ 已部署 | ✅ 已部署 | ⏳ 待添加到AdSense |

---

## arong.eu.org (WordPress) 审核通过后任务

### 1. 创建广告单元

登录 [Google AdSense](https://www.google.com/adsense/) 后台:

1. **广告** → **按广告单元** → **新建广告单元**
2. 创建以下广告单元:

| 广告单元名称 | 类型 | 建议尺寸 | 用途 |
|-------------|------|----------|------|
| `arong-in-article` | 文章内嵌广告 | 自适应 | 文章段落间 |
| `arong-sidebar` | 展示广告 | 300x250 | 侧边栏 |
| `arong-footer` | 展示广告 | 728x90 | 页脚 |

### 2. 配置Ad Inserter插件

WordPress后台 → **设置** → **Ad Inserter**

#### Block 1: 文章内嵌广告
```
位置: After paragraph 2
适用: Posts
代码: [粘贴arong-in-article广告代码]
```

#### Block 2: 侧边栏广告
```
位置: Before sidebar
适用: Posts, Pages
代码: [粘贴arong-sidebar广告代码]
```

#### Block 3: 页脚广告
```
位置: Before footer
适用: All
代码: [粘贴arong-footer广告代码]
```

### 3. 验证广告显示

- [ ] 检查文章页广告是否正常显示
- [ ] 检查侧边栏广告是否正常显示
- [ ] 检查移动端广告是否自适应
- [ ] 确保广告不影响用户体验

---

## zhurong2020.github.io (GitHub Pages) 任务

### 1. 在AdSense后台添加站点

1. 登录 [Google AdSense](https://www.google.com/adsense/)
2. **站点** → **添加站点**
3. 输入: `zhurong2020.github.io`
4. 等待审核 (ads.txt和验证代码已部署)

### 2. 审核通过后添加广告代码

由于是静态站点，需要手动编辑HTML文件添加广告代码:

#### 方法A: 修改Gridea模板 (推荐)
在Gridea应用中修改主题模板，添加广告代码位置

#### 方法B: 直接修改HTML文件
```bash
cd /home/wuxia/projects/zhurong2020.github.io

# 使用sed批量添加广告代码到所有文章页
# 例如在文章内容后添加:
find ./post -name "index.html" -exec sed -i 's|</article>|<div class="ad-container">[广告代码]</div></article>|' {} \;

# 提交并推送
git add .
git commit -m "feat: 添加AdSense广告位"
git push
```

### 3. 建议的广告位置

| 位置 | 说明 | 实现方式 |
|------|------|----------|
| 文章顶部 | 标题下方 | 修改post模板 |
| 文章底部 | 内容结束后 | 修改post模板 |
| 侧边栏 | 如果有侧边栏 | 修改layout模板 |

---

## 注意事项

1. **避免过度广告**: 每页不超过3个广告单元
2. **遵守政策**: 不要将广告放在误导性位置
3. **移动端优化**: 确保广告在移动设备上正常显示
4. **加载速度**: 使用异步加载减少对页面速度的影响

---

## 相关文件

- WordPress mu-plugins: `/var/www/arong.eu.org/public_html/wp-content/mu-plugins/`
- Gridea项目: `/home/wuxia/projects/zhurong2020.github.io/`
- 迁移工具文档: `scripts/tools/wordpress_migration/README.md`
