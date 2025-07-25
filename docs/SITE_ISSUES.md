# 网站维护日志与待办事项

此文件用于记录网站需要修复的问题和待办的改进任务。

## 优先级最高

- [ ] **首页链接404错误 (2025-07-24)**
  - **问题**: 首页“量化交易系列”的“了解更多”按钮指向 `/categories/量化交易/`，导致404错误。
  - **原因**: 对应的页面 `_pages/category-quant.md` 的永久链接是 `/categories/量化投资/`。“交易”与“投资”不匹配。
  - **解决方案**: 修改 `index.md` 文件，将链接更正为 `/categories/量化投资/`。

## 失效链接修复清单 (2025-07-24)

在 `lychee` 工具扫描后发现以下外部链接已失效，需要修复或替换。

- [ ] **文件**: `_posts/2024-03-23-Selfhosted.md`
  - [ ] `https://znhskzj.github.io/posts/qiao-qiao-hua/` (404 Not Found)
  - [ ] `https://app.nextchat.dev/` (402 Payment Required)
  - [ ] `https://nextchat.dev/` (Timeout)

- [ ] **文件**: `_posts/2024-04-27-PuttyWinscp.md`
  - [ ] `https://www.putty.org/%EF%BC%8C%E7%82%B9%E5%87%BB` (404 Not Found, 检查Markdown格式)
  - [ ] `https://winscp.net/%EF%BC%8C%E7%82%B9%E5%87%BB` (404 Not Found, 检查Markdown格式)
