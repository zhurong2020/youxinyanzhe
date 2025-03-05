---
---
layout: single
title: "您的文章标题"
date: 2025-02-18 16:45:00 +0000
excerpt: "文章的简短描述"
header:
  overlay_image: https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/your-image-id/public
  overlay_filter: 0.5
---
# layout: post
title: "轻松上手：用开源自托管项目打造你的数字王国"
date: 2024-03-24 19:55:48 +0000
categories: [技术实践, AI&开源, 开源项目]
tags: [github, selfhosting, opensource, vps, llm]
pin: false
image:
  # 1200px*630px，860px*780px
  path: "/assets/img/202404/selfhosting1200.png"
  lqip: "/assets/img/202404/selfhosting860.png"
  alt: "亲手打造自己的数字王国"
# 以下文章中涉及的所有的图片均需要增加alt描述

# 下面是WordPress插件Git it Write的字段
post_status: publish
# post_status: draft
post_excerpt: 亲手打造自己的数字王国
featured_image: /assets/img/2024004/selfhosting1200.png
taxonomy:
  category:
    - 技术实践
    - AI&开源
    - 开源项目
  post_tag:
    - github
    - selfhosting
    - opensource
    - vps
    - llm
# custom_fields:
# field1: value 1
# field2: value 2
comment_status: open
stick_post: no
---

## 引言

在这个信息化飞速发展的时代，掌握自己的数据和服务，拥有一方完全由自己控制的数字领域，已不再是技术高手的专利。通过开源和自托管项目，每个人都可以轻松构建属于自己的数字王国，享受真正的隐私保护和无限的个性化。

### Github：程序员的社交网络

GitHub 是全球最大的代码托管平台和软件开发者社区，截止 2023 年 11 月，有超过 9700 万注册用户，其中超过 8300 万活跃用户。因为平台的专业特性，平台用户主要是全世界的程序员。Github 提供了一个便捷的环境，使得程序员们能够上传、分享、审查代码，并进行项目管理、社区互动和各类团队协作。
简单地说，GitHub 就像是一个代码仓库，任何注册用户都可以上传自己的代码，并给别人查看、下载和使用，这就是开源。 Github 不仅是开源项目的聚集地，也是技术交流和合作的重要平台，而在这里，开源不仅是一个项目，更是一个精神，促进了全球范围内技术共享和创新。

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169774&authkey=%21AB2RCnS80sV4wYA&width=657&height=369" alt="github logo" width="657" height="369" />

### 开源项目：技术共享的圣地

在 GitHub 上，无论是简单脚本还是复杂操作系统，开源项目应有尽有。同时 Github 还提供了先进的项目管理工具，支持从个人爱好者到专业团队的每一种需求。在 GitHub 上，每个人都可以参与到开源项目中，形成了一个全球性的技术合作生态。即使非程序员，也能在这里找到无数免费且强大的工具和系统，为个人或企业带来实质的技术价值。

### 自托管：掌控数据的自由

**自托管（Self-Hosting）**的概念来源于对互联网服务控制权的追求。在技术领域，自托管指的是个人或组织使用自己的硬件和网络资源来运行软件或服务，而不是依赖外部供应商。这种做法使得用户可以完全控制他们的数据和服务，增加了自主性和可定制性，同时可能减少了对第三方服务的依赖和成本。
自托管不仅仅是一个技术选择，更是一种数字生活方式的体现。它强调的是个人数据的主权和隐私保护，以及对技术的深入了解和掌控能力。例如，Nextcloud 允许用户建立私人云存储服务，而 Gitea 则提供了一个轻量级的代码托管解决方案，这些工具都能让你更好地控制自己的数据和服务。

## 自托管开源项目的优势

选择自托管开源项目，意味着你将拥有数据和服务的完全控制权，同时可以根据自己的需求来个性化配置。年复一年，你所需支付的仅仅是 VPS 和域名的费用，而获得的则是随时随地的便利和高度个性化的数字体验。

具体操作：先购买网络托管服务公司的 VPS （虚拟专用服务器），再购买域名注册服务公司提供的域名，比如 ABC.xyz，最后在 VPS 上部署开源项目并进行配置，实现通过域名访问的方式。这样，每年只要支付 VPS 和域名的费用，你获得的是随时随地的便利和高度个性化的数字体验。

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169777&authkey=%21AD-W4G8YS9I82x0&width=660" alt="opensource adv" width="660" height="auto" />

下面会简单介绍 Cloudreve 私有云存储、Trilium 个人笔记系统、Jellyfin 家庭影音服务器、NextChat 共享 LLM 等应用的功能，具体开源项目的链接请参考文末。如果你也对这些可自托管的开源项目感兴趣，希望能提供更加详细的安装步骤的，请继续关注我们后续的文章。

### 通过 Cloudreve 实现私有云存储

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169778&authkey=%21AENDRKObZ8mnQzQ&width=660" alt="Cloudreve" width="660" height="auto" />

使用开源程序 Cloudreve，完全可以替代某度云盘的功能，不仅能享受完全带宽的下载，也不需要支付每月的订阅费用。

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

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169779&authkey=%21ANP3lIPqmwHGUHM&width=660" alt="Trilium" width="660" height="auto" />

部署 Trilium 个人笔记应用后，基本可以替代某象笔记，再也不用受到无处不在的广告的骚扰，也不用因为促销，就将账户使用期限延长到了 2030 年。

- **Trilium**：个人笔记应用方案特点
  Trilium Notes 是一个层次化的笔记应用程序，专注于建立大型个人知识库。
  笔记可以排列成任意深的树，单个笔记可以放在树中的多个位置
  丰富的所见即所得笔记编辑功能，包括带有 Markdown 自动格式化功能的表格，图像和数学
  支持编辑使用源代码的笔记，包括语法高亮显示
  笔记之间快速导航，全文搜索和笔记聚焦
  笔记属性可用于笔记组织，查询和高级脚本编写
  公开地分享（发布）笔记到互联网
  具有按笔记粒度的强大的笔记加密
  使用自带的 Excalidraw 来绘制图表（笔记类型“画布”）
  关系图和链接图，用于可视化笔记及其关系
  在拥有超过 10 万条笔记时仍能保持良好的可用性和性能
  针对智能手机和平板电脑进行优化的用于移动设备的前端
  Evernote 和 Markdown 导入导出功能
  使用网页剪藏轻松保存互联网上的内容

[Trilium 官网](https://trilium.cc)

### 使用 NextChat 共享 LLM

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169781&authkey=%21AASfS7lEgLXGmbw&width=660" alt="NextChat" width="660" height="auto" />

对于想要使用 ChatGPT 和 Gemini 的中国国内用户，当你部署开源应用 NextChat，再配置好相关环境变量，你就可以在中国国内直接使用 ChatGPT 或者 Gemini，并且还可以和朋友分享。

- **NextChat**：开源的 LLM 共享应用平台特点
- 在 1 分钟内使用 Vercel 免费一键部署
  提供体积极小（~5MB）的跨平台客户端（Linux/Windows/MacOS）, 下载地址
  完整的 Markdown 支持：LaTex 公式、Mermaid 流程图、代码高亮等等
  精心设计的 UI，响应式设计，支持深色模式，支持 PWA
  极快的首屏加载速度（~100kb），支持流式响应
  隐私安全，所有数据保存在用户浏览器本地
  预制角色功能（面具），方便地创建、分享和调试你的个性化对话
  海量的内置 prompt 列表，来自中文和英文
  自动压缩上下文聊天记录，在节省 Token 的同时支持超长对话
  多国语言支持：English, 简体中文, 繁体中文, 日本語, Español, Italiano, Türkçe, Deutsch, Tiếng Việt, Русский, Čeština, 한국어, Indonesia
  拥有自己的域名？好上加好，绑定后即可在任何地方无障碍快速访问

[NextChat 官网](https://nextchat.dev/)

### 安装 Jellyfin，实现家庭的影音服务器

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169782&authkey=%21AGWvBam0MlMYIok&width=660" alt="Jellyfin" width="660" height="auto" />

- **Jellyfin**：家庭媒体服务器方案特点
  Jellyfin 完全免费和开源，你可以自由使用、修改和分发
  Jellyfin 不含任何广告和跟踪程序，您将完全控制自己的媒体数据
  Jellyfin 的服务端应用程序安装在运行 Microsoft Windows、MacOS、Linux 等系统的服务器上或 Docker 上
  Jellyfin 的客户端应用程序可以安装在智能手机、平板电脑、智能电视、网络机顶盒、电子游戏机或网页浏览器上
  支持 DLNA 以及插有 Chromecast 的设备也能接收 Jellyfin 服务端发来的文件
  直播电视和 DVR，字幕管理，多用户多设备支持，插件和扩展程序
  硬件解码、4K 播放与转码、AV1/H.265/HEVC 解码、电影海报刮削、音乐管理与播放、网络收音机、片头自动跳过、杜比多音轨、少儿控制
  Jellyfin 活跃的社区支持

  [Jellyfin 官网](https://jellyfin.org/)

在本系列的文章中，我们目前计划将演示的项目有（按拼音顺序）：

- bitwarden 密码管理工具--开源密码管理解决方案后端，适用于个人和组织的密码管理需求。
- calibre 书籍管理系统--电子书管理 Web 应用程序，适用于拥有大量电子书收藏的用户。
- cloudreve 家庭云盘--帮助用户高效地管理和访问文件，提高文件安全性的个人云盘系统。
- jellyfin 家庭媒体服务器--管理和流式播放个人媒体收藏并注重用户隐私的媒体服务器软件。
- netdata 实时网络监控--提供实时的系统性能数据、丰富的可视化界面和告警系统，帮助用户高效地监控服务器、网络和应用程序的性能。
- photoprism 家庭照片服务器--开源照片管理应用程序，适用于重视照片隐私和控制权的用户。
- pi-hole 网络广告拦截--有效拦截网络广告、保护用户隐私，改善浏览体验的 DNS sinkhole 工具。
- rclone 挂接三方云盘--命令行工具，可实现高效地在本地和云存储之间同步和管理文件的方案。
- stable-diffusion-webui--一個可以用于生成图像和修改現有图像的基于 Stable Diffusion 模型的网页界面。
- trilium 个人笔记--个人知识管理应用程序，适合注重灵活性和隐私的用户。
- webmin 服务器监控--可以帮助用户高效管理各种 Linux/Unix 系统，非常适合初学者和服务器管理人员。
- wordpress 个人网站--适合个人、企业和组织快速搭建和管理网站的免费网站搭建平台。
- xray 及 3x-ui 代理服务器--帮助用户突破网络限制、保护网络隐私，网络代理核心框架。

[点击此处可以查看部分应用截图和介绍](https://zhurong2020.github.io/post/yun-duan-sheng-huo-chu-ti-yan-da-zao-zhuan-shu-de-duo-gong-neng-jia-ting-fu-wu-qi/)

另外目前正在尝试以下和 LLM 有关的项目，届时会选一二个功能比较完整的进行演示：

- chatgpt-on-wechat--使用 OpenAI，Google 等主流 LLM，实现个人微信、企业微信、微信公众号、飞书和钉钉等平台不同场景的对话机器人搭建需求
- chat-next-web--提供跨平台图形用户界面 (GUI) 以与大型语言模型（ChatGPT 和 Gemini）交互的项目
- gtp-academic--基于大语言模型为科研人员和学生提供文献检索、论文写作、代码生成、图表制作、问答系统等功能的辅助平台
- lobe-chat--支持多种 AI 提供商（OpenAI/Claude 3/Gemini/Perplexity/Bedrock/Azure/Mistral/Ollama）的聊天框架
- open-interpreter--一个有潜力的自然语言界面，可以利用 AI，使用普通语言来输入命令

这些项目不仅能让你享受 DIY 的乐趣，还能让你在技术旅途上不断成长。

## 实施和运维的步骤

要成功部署和管理自托管项目，你需要遵循以下步骤：

1. **个人云服务器的配置**：选择合适的服务商，建议跟着我们的系列文章购买 Racknerd 的 VPS 和 Namesilo 的域名，最低年付 12 美元起。
2. **应用的安装与运行**：根据我们的文章和操作步骤说明，一步步安装所需的开源应用，并完成配置或参数修改，高级用户再设置反代。
3. **常规的更新与维护**：不断学习新技术，积极参与用户群中的讨论，定期检查 VPS 并更新应用，确保自己搭建系统的安全与稳定。

## 实际应用案例

后续文章中，我们将提供详细的案例分析，展示如何在实际环境中部署以上提到的开源项目。配备清晰的截图和步骤说明，有些项目将提供视频安装步骤，帮助你更好地理解这些项目的部署方式和应用场景。

## 参考链接和演示网址（已付费用户可发邮件索要密码）

为了让你能更直观地体验这些自托管服务，我们提供了以下演示网址，你可以通过演示网址查看：

- [Jellyfin Demo](https://demo.jellyfin.org/stable/web/index.html#!/login.html?serverid=713dc3fe952b438fa70ed35e4ef0525a)
- [NextChat Demo](https://app.nextchat.dev/)，付费用户请来信索要生产网址和密码。

现在就开始你的自托管旅程吧！选择一个开源项目，跟随我们的指南，一步一步构建你的数字王国。每个人都值得拥有一个完全自主控制的数字空间。

---

加入我们的社区，与其他数字自主爱好者一起探讨、学习和分享。不论你是技术新手还是老手，这里都有你的一席之地。
记得查看系列中的其他文章，以全面构建你的云端生活：

- [云端生活入门：从小白到网络达人](https://zhurong2020.github.io/post/yun-duan-sheng-huo-ru-men-cong-xiao-bai-dao-wang-luo-da-ren/)
- [云端生活入门：用 ChatGPT-4 开启个性化在线学习之旅](https://zhurong2020.github.io/post/yun-duan-sheng-huo-ru-men-yong-chatgpt-4-kai-qi-ge-xing-hua-zai-xian-xue-xi-zhi-lu/)
- [云端生活初体验-打造专属的多功能家庭服务器](https://zhurong2020.github.io/post/yun-duan-sheng-huo-chu-ti-yan-da-zao-zhuan-shu-de-duo-gong-neng-jia-ting-fu-wu-qi/)
- [云端生活体验-让人呼吸顺畅的 ChatGPT（可惜项目已经停止，为感谢作者留文纪念）](https://zhurong2020.github.io/post/yun-duan-sheng-huo-ti-yan-rang-ren-hu-xi-shun-chang-de-chatgpt/)
- [云端生活体验-NextChat 一个跨平台的 AI 聊天项目](https://zhurong2020.github.io/post/nextchatge-xing-hua-nin-de-chatgpt-ti-yan-kai-yuan-kuai-su-bu-shu-yu-duo-yuan-ying-yong/)
- [云端启航：轻松拥有自己的 VPS 开启你的云端之旅](https://zhurong2020.github.io/post/yun-duan-qi-hang-qing-song-yong-you-zi-ji-de-vpskai-qi-ni-de-yun-duan-zhi-lu/)
- [聊天机器人秘诀-悄悄话让 AI 更懂你](https://znhskzj.github.io/posts/qiao-qiao-hua/)

好了，今天就到这里。如果您对今天讨论的自托管还有疑问，欢迎您加入我们的“云端生活交流群”，和其它小伙伴一起学习交流。另外您希望我下一篇写什么内容，也欢迎在评论区留言。

如果你觉得我的文章对你有帮助，可以[请我喝咖啡](https://www.buymeacoffee.com/zhurong052Q)。

<img src="https://sat02pap005files.storage.live.com/y4m1bQmI2HjlYf8y0-p5ILDLqV4klxYZjjhDZYzn60HpwCTOEot0HfRqsp5RrXVXKechgLZmehuN6udGTqYc3Qudqo73s1tqUAIJul__ZG1-YBMQGkzr8FC9gRj_ywS7n9a_Vpp87CQm1enxUNgrZSKE5wIDvhjixZA3QdOTcwjGnYZRk62QXEWOOAg83tq7Mu1?width=256&height=200&cropmode=none" alt="buymeacoffee" width="256" height="200" />
