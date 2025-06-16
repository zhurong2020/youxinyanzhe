---
author_profile: true
breadcrumbs: true
categories:
- 技术实践
- 项目与创新
comments: true
date: 2024-03-24 19:55:00 +0000
excerpt: 通过选择并自托管 Github 上的开源项目，每个人都可以轻松构建属于自己的数字王国。
header:
  overlay_filter: 0.5
  overlay_image: https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/839f39f3-8c2f-4a1d-534b-722ab5e4fc00/public
  teaser: https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/839f39f3-8c2f-4a1d-534b-722ab5e4fc00/public
last_modified_at: '2025-03-05 11:39:46'
layout: single
related: true
share: true
tags:
- GitHub
- 开源
- 自托管
- Cloudreve
- Trilium
title: 轻松上手：用开源自托管项目打造你的数字王国
toc: true
toc_icon: list
toc_label: 本页内容
toc_sticky: true
---

## 引言

在信息化时代，掌控个人数据和服务，构建完全由自己控制的数字领域，已经不再是技术专家的特权。借助 GitHub 上丰富的开源和自托管项目，每个人都能轻松打造属于自己的数字王国，享受真正的隐私保护和无限的个性化体验。

### GitHub：程序员的社交网络

GitHub 是全球领先的代码托管平台和软件开发者社区。截至 2023 年 11 月，它拥有超过 9700 万注册用户，其中活跃用户超过 8300 万。凭借其专业特性，GitHub 的用户群体主要由全球程序员构成。它提供了一个便捷的环境，让程序员能够上传、分享、审查代码，并进行项目管理、社区互动和团队协作。

简单来说，GitHub 就像一个代码仓库，用户可以上传自己的代码，供他人查看、下载和使用，这就是开源。GitHub 不仅是开源项目的聚集地，也是技术交流和合作的重要平台。在这里，开源不仅仅是一个项目，更是一种精神，推动着全球范围内的技术共享和创新。

<img src="https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/733c7e19-9e9a-4fa2-54de-29bd7d5c7100/public" alt="github logo" alt="github logo" width="657" height="369" />

### 开源项目：技术共享的圣地

GitHub 上汇集了各种开源项目，从简单的脚本到复杂的操作系统，应有尽有。它还提供了先进的项目管理工具，满足从个人爱好者到专业团队的各种需求。在 GitHub 上，任何人都可以参与开源项目，形成一个全球性的技术合作生态。即使是非程序员，也能在这里找到无数免费且强大的工具和系统，为个人或企业带来实际的技术价值。

### 自托管：掌控数据的自由

**自托管（Self-Hosting）**源于对互联网服务控制权的追求。在技术领域，它指的是个人或组织使用自己的硬件和网络资源来运行软件或服务，而非依赖外部供应商。这种方式使用户能够完全掌控自己的数据和服务，提高自主性和可定制性，同时减少对第三方服务的依赖和成本。

自托管不仅是一种技术选择，更是一种数字生活方式的体现。它强调个人数据主权、隐私保护，以及对技术的深入理解和掌控能力。例如，Nextcloud 允许用户搭建私有云存储服务，而 Gitea 则提供了一个轻量级的代码托管解决方案。这些工具都能帮助你更好地控制自己的数据和服务。

## 自托管开源项目的优势

选择自托管开源项目，意味着你将拥有数据和服务的完全控制权，并能根据自身需求进行个性化配置。你每年只需支付 VPS 和域名的费用，就能享受随时随地的便利和高度个性化的数字体验。

具体操作如下：首先，购买网络托管服务公司的 VPS（虚拟专用服务器）；然后，购买域名注册服务公司提供的域名，例如 ABC.xyz；最后，在 VPS 上部署开源项目并进行配置，通过域名访问。如此一来，每年只需支付 VPS 和域名的费用，便可获得随时随地的便利和高度个性化的数字体验。

<img src="https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/2fad7531-5ee4-40fb-ad09-3e4332772f00/public" alt="opensource adv" alt="opensource adv" width="660" height="auto" />

下面将简要介绍 Cloudreve 私有云存储、Trilium 个人笔记系统、Jellyfin 家庭影音服务器、NextChat 共享 LLM 等应用的功能。具体的开源项目链接请参考文末。如果你对这些可自托管的开源项目感兴趣，希望获得更详细的安装步骤，请继续关注我们后续的文章。

### 通过 Cloudreve 实现私有云存储

<img src="https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/81e98647-5185-4bc1-1599-5a5c7d4f3d00/public" alt="Cloudreve" alt="Cloudreve" width="660" height="auto" />

使用开源程序 Cloudreve，你可以完全替代某度云盘的功能，不仅能享受完全带宽的下载速度，也无需支付每月订阅费用。

- **Cloudreve**：私人云存储解决方案特点：
  ☁️ 支持本机、从机、七牛、阿里云 OSS、腾讯云 COS、又拍云、OneDrive (包括世纪互联版) 、S3 兼容协议 作为存储端
  📤 上传/下载 支持客户端直传，支持下载限速
  💾 可对接 Aria2 离线下载，可使用多个从机节点分担下载任务
  📚 在线 压缩/解压缩、多文件打包下载
  💻 覆盖全部存储策略的 WebDAV 协议支持
  ⚡ 拖拽上传、目录上传、流式上传处理
  🗃️ 文件拖拽管理
  👩‍👧‍👦 多用户、用户组、多存储策略
  🔗 创建文件、目录的分享链接，可设定自动过期
  👁️‍🗨️ 视频、图像、音频、 ePub 在线预览，文本、Office 文档在线编辑
  🎨 自定义配色、黑暗模式、PWA 应用、全站单页应用、国际化支持
  🚀 All-In-One 打包，开箱即用

[Cloudreve 官网](https://cloudreve.org/)

### 通过 Trilium 实现个人笔记系统

<img src="https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/144693bc-43d2-458c-6081-eb7492104100/public" alt="Trilium" alt="Trilium" width="660" height="auto" />

部署 Trilium 个人笔记应用后，你基本可以替代某象笔记，再也不用受到无处不在的广告的骚扰，也不必因为促销，就将账户使用期限延长到 2030 年。

- Trilium Notes 是一个层次化的笔记应用程序，专注于构建大型个人知识库。
- 笔记可以排列成任意深的树状结构，单个笔记可以位于树中的多个位置。
- 提供丰富的所见即所得笔记编辑功能，包括带有 Markdown 自动格式化功能的表格、图像和数学公式
- 支持编辑使用源代码的笔记，并提供语法高亮显示
- 可在笔记之间快速导航，进行全文搜索和笔记聚焦
- 笔记属性可用于笔记组织、查询和高级脚本编写
- 可以公开地分享（发布）笔记到互联网
- 具有按笔记粒度的强大加密功能
- 使用自带的 Excalidraw 来绘制图表（笔记类型“画布”）
- 关系图和链接图，用于可视化笔记及其关系
- 即使拥有超过 10 万条笔记，仍能保持良好的可用性和性能
- 针对智能手机和平板电脑进行优化的移动设备前端
- 支持 Evernote 和 Markdown 导入导出功能
- 使用网页剪藏轻松保存互联网上的内容

[Trilium 官网](https://trilium.cc)

### 使用 NextChat 共享 LLM

<img src="https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/dc02f882-bab1-40e0-afb7-7d7696101b00/public" alt="NextChat" alt="NextChat" width="660" height="auto" />

对于想要使用 ChatGPT 和 Gemini 的中国国内用户，部署开源应用 NextChat 并配置好相关环境变量后，就可以直接在中国国内使用 ChatGPT 或 Gemini，并且还可以与朋友分享。

- 可以在 1 分钟内使用 Vercel 免费一键部署
- 提供体积极小（~5MB）的跨平台客户端（Linux/Windows/MacOS）, 下载地址
- 完整的 Markdown 支持：LaTex 公式、Mermaid 流程图、代码高亮等等
- 精心设计的 UI，响应式设计，支持深色模式，支持 PWA
- 极快的首屏加载速度（~100kb），支持流式响应
- 隐私安全，所有数据保存在用户浏览器本地
- 预制角色功能（面具），方便地创建、分享和调试你的个性化对话
- 海量的内置 prompt 列表，来自中文和英文
- 自动压缩上下文聊天记录，在节省 Token 的同时支持超长对话
- 多国语言支持：English, 简体中文, 繁体中文, 日本語, Español, Italiano, Türkçe, Deutsch, Tiếng Việt, Русский, Čeština, 한국어, Indonesia
- 拥有自己的域名？好上加好，绑定后即可在任何地方无障碍快速访问

[NextChat 官网](https://nextchat.dev/)

### 安装 Jellyfin，实现家庭的影音服务器

<img src="https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/89270019-08a4-47ff-73cd-cb3ed2dfee00/public" alt="Jellyfin" alt="Jellyfin" width="660" height="auto" />

- 完全免费和开源，你可以自由使用、修改和分发
- 不含任何广告和跟踪程序，您可以完全控制自己的媒体数据
- 服务端应用程序安装在运行 Microsoft Windows、MacOS、Linux 等系统的服务器上或 Docker 上
- 客户端应用程序可以安装在智能手机、平板电脑、智能电视、网络机顶盒、电子游戏机或网页浏览器上
- 支持 DLNA 以及插有 Chromecast 的设备也能接收 Jellyfin 服务端发来的文件
- 直播电视和 DVR，字幕管理，多用户多设备支持，插件和扩展程序
- 硬件解码、4K 播放与转码、AV1/H.265/HEVC 解码、电影海报刮削、音乐管理与播放、网络收音机、片头自动跳过、杜比多音轨、少儿控制
- 活跃的社区支持

  [Jellyfin 官网](https://jellyfin.org/)

在本系列的文章中，我们目前计划演示的项目包括（按拼音顺序）：

- bitwarden 密码管理工具：开源密码管理解决方案后端，适用于个人和组织的密码管理需求。
- calibre 书籍管理系统：电子书管理 Web 应用程序，适用于拥有大量电子书收藏的用户。
- cloudreve 家庭云盘：帮助用户高效地管理和访问文件，提高文件安全性的个人云盘系统。
- jellyfin 家庭媒体服务器：管理和流式播放个人媒体收藏并注重用户隐私的媒体服务器软件。
- netdata 实时网络监控：提供实时的系统性能数据、丰富的可视化界面和告警系统，帮助用户高效地监控服务器、网络和应用程序的性能。
- photoprism 家庭照片服务器：开源照片管理应用程序，适用于重视照片隐私和控制权的用户。
- pi-hole 网络广告拦截：有效拦截网络广告、保护用户隐私，改善浏览体验的 DNS sinkhole 工具。
- rclone 挂接三方云盘：命令行工具，可实现高效地在本地和云存储之间同步和管理文件的方案。
- stable-diffusion-webui：一个可以用于生成图像和修改现有图像的基于 Stable Diffusion 模型的网页界面。
- trilium 个人笔记：个人知识管理应用程序，适合注重灵活性和隐私的用户。
- webmin 服务器监控：可以帮助用户高效管理各种 Linux/Unix 系统，非常适合初学者和服务器管理人员。
- wordpress 个人网站：适合个人、企业和组织快速搭建和管理网站的免费网站搭建平台。
- xray 及 3x-ui 代理服务器：帮助用户突破网络限制、保护网络隐私的网络代理核心框架。

[点击此处可以查看部分应用截图和介绍](https://zhurong2020.github.io/post/yun-duan-sheng-huo-chu-ti-yan-da-zao-zhuan-shu-de-duo-gong-neng-jia-ting-fu-wu-qi/)

另外，我们目前正在尝试以下与 LLM 有关的项目，届时会选择一两个功能比较完整的进行演示：

- chatgpt-on-wechat：使用 OpenAI、Google 等主流 LLM，实现个人微信、企业微信、微信公众号、飞书和钉钉等平台不同场景的对话机器人搭建需求。
- chat-next-web：提供跨平台图形用户界面 (GUI) 以与大型语言模型（ChatGPT 和 Gemini）交互的项目
- gtp-academic：基于大语言模型为科研人员和学生提供文献检索、论文写作、代码生成、图表制作、问答系统等功能的辅助平台
- lobe-chat：支持多种 AI 提供商（OpenAI/Claude 3/Gemini/Perplexity/Bedrock/Azure/Mistral/Ollama）的聊天框架
- open-interpreter：一个有潜力的自然语言界面，可以利用 AI，使用普通语言来输入命令

这些项目不仅能让你享受 DIY 的乐趣，还能让你在技术旅途中不断成长。

## 实施和运维的步骤

要成功部署和管理自托管项目，你需要遵循以下步骤：

1. **个人云服务器的配置**：选择合适的服务商。建议参考我们的系列文章，购买 Racknerd 的 VPS 和 Namesilo 的域名，最低年付 12 美元起。
2. **应用的安装与运行**：根据我们的文章和操作步骤说明，逐步安装所需的开源应用，并完成配置或参数修改。高级用户可以设置反向代理。
3. **常规的更新与维护**：不断学习新技术，积极参与用户群中的讨论，定期检查 VPS 并更新应用，确保自己搭建系统的安全与稳定。

## 实际应用案例

在后续文章中，我们将提供详细的自托管项目案例分析，展示如何在实际环境中部署以上提到的开源项目。我们会配备清晰的截图和步骤说明，有些项目还会提供视频安装步骤，帮助你更好地理解这些项目的部署方式和应用场景。

## 参考链接和演示网址

为了让你能更直观地体验这些自托管服务，你可以使用以下演示网址：

- [Jellyfin Demo](https://demo.jellyfin.org/stable/web/#/home.html)
- [NextChat Demo](https://app.nextchat.dev/)

现在就开始你的自托管旅程吧！选择一个开源项目，跟随我们的指南，一步一步构建你的数字王国。每个人都值得拥有一个完全自主控制的数字空间。

---

加入我们的社区，与其他数字自主爱好者一起探讨、学习和分享。无论你是技术新手还是老手，这里都有你的一席之地。
记得查看系列中的其他文章，以全面构建你的云端生活：

- [云端生活入门：从小白到网络达人](https://zhurong2020.github.io/post/yun-duan-sheng-huo-ru-men-cong-xiao-bai-dao-wang-luo-da-ren/)
- [云端生活入门：用 ChatGPT-4 开启个性化在线学习之旅](https://zhurong2020.github.io/post/yun-duan-sheng-huo-ru-men-yong-chatgpt-4-kai-qi-ge-xing-hua-zai-xian-xue-xi-zhi-lu/)
- [云端生活初体验-打造专属的多功能家庭服务器](https://zhurong2020.github.io/post/yun-duan-sheng-huo-chu-ti-yan-da-zao-zhuan-shu-de-duo-gong-neng-jia-ting-fu-wu-qi/)
- [云端生活体验-让人呼吸顺畅的 ChatGPT（可惜项目已经停止，为感谢作者留文纪念）](https://zhurong2020.github.io/post/yun-duan-sheng-huo-ti-yan-rang-ren-hu-xi-shun-chang-de-chatgpt/)
- [云端生活体验-NextChat 一个跨平台的 AI 聊天项目](https://zhurong2020.github.io/post/nextchatge-xing-hua-nin-de-chatgpt-ti-yan-kai-yuan-kuai-su-bu-shu-yu-duo-yuan-ying-yong/)
- [云端启航：轻松拥有自己的 VPS 开启你的云端之旅](https://zhurong2020.github.io/post/yun-duan-qi-hang-qing-song-yong-you-zi-ji-de-vpskai-qi-ni-de-yun-duan-zhi-lu/)
- [聊天机器人秘诀-悄悄话让 AI 更懂你](https://znhskzj.github.io/posts/qiao-qiao-hua/)

好了，今天就到这里。如果您对今天讨论的自托管还有疑问，欢迎您加入我们的“云端生活交流群”，和其他小伙伴一起学习交流。另外，您希望我下一篇写什么内容，也欢迎在评论区留言。


如果你觉得我的文章对你有帮助，可以[请我喝咖啡](https://www.buymeacoffee.com/zhurong052Q)

<a href="https://www.buymeacoffee.com/zhurong052Q" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

> 💬 **发表评论**: 您需要有一个 GitHub 账号来发表评论。