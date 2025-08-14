# 音频资源管理

## 目录结构

```
assets/audio/
├── README.md                 # 本说明文件
├── archive/                  # 音频文件归档目录
│   └── *.mp3                # 已发布文章的音频文件
└── temp/                    # 临时处理目录（可选）
```

## 音频文件归档流程

### 1. YouTube音频下载
当有新的YouTube播客需要提供离线版本时：

```bash
# 安装/更新 yt-dlp
pip install -U yt-dlp

# 下载音频为MP3格式
yt-dlp -x --audio-format mp3 --audio-quality 0 -o "assets/audio/temp/%(title)s.%(ext)s" "YOUTUBE_URL"

# 重命名为规范格式
mv "assets/audio/temp/原文件名.mp3" "assets/audio/archive/文章标识-podcast.mp3"
```

### 2. 文件命名规范
- **格式**: `{文章日期或关键词}-podcast.mp3`
- **示例**: 
  - `information-verification-methodology-podcast.mp3`
  - `2025-08-08-wuhan-university-analysis-podcast.mp3`

### 3. 归档记录
每个音频文件需要记录：
- 原YouTube链接
- 下载日期
- 文件大小
- 音频时长
- 关联文章路径
- 百度网盘分享链接

## 音频文件清单

### 2025-08-08 信息核实方法论
- **文件**: `information-verification-methodology-podcast.mp3`
- **YouTube**: https://www.youtube.com/watch?v=n9y3mQDOKpc
- **下载日期**: 2025-08-14
- **文件大小**: 7.2MB
- **时长**: 7分25秒
- **文章**: `_posts/2025-08-08-information-verification-methodology.md`
- **百度网盘**: https://pan.baidu.com/s/1vRCLI-sVCXxrWJEyCOuu5g?pwd=grrv
- **会员等级**: 年度会员专享

---

## 使用说明

1. **新音频发布流程**：
   - 上传YouTube → 下载音频 → 重命名归档 → 上传百度网盘 → 更新文章链接 → 更新此清单

2. **存储策略**：
   - 本地归档：保留高质量原始文件
   - 百度网盘：提供会员下载服务
   - YouTube：在线播放（需科学上网）

3. **会员权限**：
   - 普通读者：可访问YouTube在线版
   - 年度会员：可下载百度网盘离线版

4. **维护建议**：
   - 定期检查链接有效性
   - 备份重要音频文件
   - 保持命名规范一致性