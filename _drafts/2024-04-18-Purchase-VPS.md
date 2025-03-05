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
title: "云端启航：轻松拥有自己的VPS，开启你的云端之旅"
date: 2024-04-18 12:17:48 +0000
categories: [技术实践, 云技术, VPS]
tags: [host, vps, racknerd]
pin: false
image:
  # 1200px*630px，860px*780px
  path: "/assets/img/202404/buyvps1200-680.png"
  lqip: "/assets/img/202404/buyvps860-780.png"
  alt: "购买VPS开启云端生活"
# 以下文章中涉及的所有的图片均需要增加alt描述

# 下面是WordPress插件Git it Write的字段
post_status: publish
# post_status: draft
post_excerpt: 购买VPS开启云端生活
featured_image: /assets/img/202404/buyvps1200-680.png
taxonomy:
  category:
    - 技术实践
    - 云技术
    - VPS
  post_tag:
    - host
    - vps
    - racknerd
# custom_fields:
# field1: value 1
# field2: value 2
comment_status: open
stick_post: no
---

## 引言

在这个数字化和网络化日益深入的时代，掌握关键技术知识已成为现代人的一种必备能力。《云端生活入门：从小白到网络达人》系列文章将引导您逐步走入技术世界，从基本概念入手，带你了解云端生活的原理，并通过动手实践，完成个人网站搭建、安装开源应用、定制家庭云功能等。

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169762&authkey=%21ACQqWwcwo_DyaCs&width=660" alt="云生活" width="660" height="auto" />

本系列将涉及以下主题：

- **网站托管**：如何使用 VPS 托管个人或商业网站，并完成 WordPress 网站的搭建。
- **开发和测试环境**：重新安装 Linux 系统，配置 LNMP，使用 SSH 登录，并部署应用。
- **私人云存储**：借助 Cloudreve 和 Rclone，创建一个跨平台、多用户的文件存储系统。
- **游戏服务器**：如果你的 VPS 配置允许，可以尝试搭建 Minecraft 或其他游戏的私服。
- **其他用途**：介绍开源应用 Xray、Webmin、NextChat、Trilium 等软件的使用。

如果你只是想跟随操作步骤实现特定功能，可以直接跳转到操作部分，比如这篇文章主要介绍 VPS 以及如何购买 RackNerd VPS。

## What & Why-什么是主机、VPS，为什么要用 VPS

### 主机及主机服务商

我们的系列文章旨在通过现代技术帮助普通人实现“云端生活”，即在一个 24 小时在线的服务器上，安装并运行各种开源程序，通过网络随时随地访问这些服务。我们常说的主机服务商，如国外的谷歌、亚马逊、微软，国内的阿里、腾讯、华为等，就是提供这类主机服务的公司。

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169763&authkey=%21ABY9nJwQ4mFitvo&width=660" alt="主机" width="660" height="auto" />

### 主机服务及 VPS

主机服务商通常提供多种主机服务，如共享主机、虚拟私人服务器（VPS）、专用服务器和云托管等，每种服务适合不同的需求和客户。对于个人用户，VPS 因其独特的性价比，提供了类似专用服务器的体验，但成本更低，是理想的云端入门选择。

### 为何选择 VPS 入门

选择 VPS 的理由在于其平衡性：VPS 比共享主机提供更多控制权和性能，而成本又低于专用服务器和高端云托管服务。对于初学者，VPS 是理想的学习和实践平台，因为它结合了经济性、灵活性和足够的资源，让用户可以在学习过程中有充分的实践机会。

## 我推荐的主机服务商-RackNerd 及 VPS 入门配置

RackNerd 是一家成立于 2019 年的主机服务商，以其高性能、低成本的 VPS 方案著称，非常适合入门用户。以下是一些推荐的配置方案：

### 入门 VPS 配置推荐

年付 10.99 美元的 VPS，适合初学者和基础用户：

[年付 10.99 美元的 VPS 套餐](https://my.racknerd.com/aff.php?aff=7454&pid=838)。

年付 23.88 美元的 VPS，适合需要搭建个人网站或探索开源应用的用户：

[年付 23.88 美元的 VPS 套餐](https://my.racknerd.com/aff.php?aff=7454&pid=840)。

年付 37.38 美元的 VPS，适合有更高性能需求的用户，如搭建家庭云盘、影音系统或游戏私服：

[年付 37.38 美元的 VPS 套餐](https://my.racknerd.com/aff.php?aff=7454&pid=829)。

## 购买 VPS 过程（实际操作步骤）

1. 选择套餐：首先定位自己的需求，选择下面适合自己的套餐:

[10.99 美元套餐](https://my.racknerd.com/aff.php?aff=7454&pid=838)

[23.88 美元套餐](https://my.racknerd.com/aff.php?aff=7454&pid=840)

[37.38 美元套餐](https://my.racknerd.com/aff.php?aff=7454&pid=829)

请注意，如果您选择的是其它服务商提供的 VPS，本系列的所有文章内容仅供参考。

点击上述链接，会跳转到 Racknerd 的购物车页面，如果您想使用中文的，在 View Cart 的按钮旁边可以直接选择“中文”，当然你也可以使用浏览器的翻译功能，我们之后的介绍都以英文的为主，如果阅读英文有困难的小伙伴，请自行摸索是否有中文界面或使用浏览器翻译功能进行调整。

2. 确认配置：如果你想跟着本系列的文章，一步一步完成多个家庭应用的搭建，建议至少选择 23.88 美元的套餐（土豪请随意），点击链接后，应该是类似这样的画面：

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169752&authkey=%21AERnB9d1Fj51XRE&width=672&height=512" alt="rn 23.88套餐" width="672" height="512" />

这就是你选择的 VPS 的基本配置，2 核（CPU）2.5G（RAM）38G（SSD）6000G（月带宽）1G（连接速度）1 个 IPv4（唯一的公网 IP 地址），另外还有用于管理 VPS 的控制面板，允许选择全球多个数据中心，付费周期是年付 23.88 美元。

如果你想调整部分参数（含硬件配置），下面的画面提供了可选参数：

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169753&authkey=%21AHpUXvHhEiJri8o&width=660" alt="rn 23.88套餐可调参数" width="660" height="auto" />

如果您是中国国内的用户，我建议只调整这 2 个参数：Operating System（操作系统）和 Location（机房位置），其中 Operating System 选择 Ubuntu 22.04 64 Bit，Location 选择 San Jose CA。查看一下 Order Summary，合计金额应该还是 23.88 美元，点击 Continue，来到了确认页面：

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169754&authkey=%21AEiX0TN_1fWZO6Y&width=660" alt="rn 23.88套餐价格确认" width="660" height="auto" />

3. 填个人信息：点击绿色的 Checkout 按钮，填入个人信息，注意页面中已经有 China 相关选项，应该可以填写自己的真实地址：

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169755&authkey=%21AM-9-N_LC5iYB7Y&width=660" alt="rn 23.88套餐个人信息" width="660" height="auto" />

4. 付款：最后 Payment Details（付款）中，可以选择你喜欢的付款方式，也包括了支付宝和银联卡。

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169756&authkey=%21AMvAFGXQR9HsDsU&width=256" alt="rn 23.88套餐支付方式" width="256" height="auto" />

最后，点击“I have read and agree to the Terms of Service”和 Complete Order 就好了。

5. 查收邮件：之后你会收到多封 RackNerd 发来的欢迎邮件，告诉你如何登录自己的账户，如何获得支持，订单支付情况，发票，特别注意其中有一封邮件是有关 KVM VPS Login Information，请保存其中的 root password：

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169757&authkey=%21AGLUlL290GCeduY&width=602&height=550" alt="rn 套餐购买后查收邮件" width="602" height="550" />

好的，至此，购买 VPS 的步骤就完成了，你已经拥有了一台完全可控的可以 24 小时访问的服务器，后续我们将探讨如何管理这台 VPS，并利用免费的开源项目，完成私有云存储、家庭影院、代理服务器、共享 ChatGPT 等各种实用功能，这样就能构建一个 7\*24 小时可用的，家庭或者小范围的私有云端服务，让我们来看几个使用这台 VPS 搭建的应用画面：

使用开源项目 Cloudreve，免费搭建私有化云存储方案：
<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169759&authkey=%21AJT5Ob6Yn3mr32E&width=660" alt="vps上的私有化存储" width="660" height="auto" />

使用开源项目 Trilium，免费搭建个人笔记（知识库）系统：
<<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169760&authkey=%21ABbCG9Mx5P0ezD0&width=660" alt="vps上的个人笔记" width="660" height="auto" />>

使用开源项目 NextChat，免费搭建共享 ChatGPT 或 Gemini：
<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169761&authkey=%21AHEM9bf9PGrkDp4&width=660" alt="vps上的共享ChatGPT" width="660" height="auto" />

使用开源项目 Jellyfin，免费搭建家庭影音系统：
<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169758&authkey=%21AKeo9Fx-noX8k-g&width=660" alt="vps上的家庭影音" width="660" height="auto" />

今天我们完成了对主机、主机服务商，VPS 的初步认识，并且通过 RackNerd 网站完成了用户注册购买的流程。

## 结论

通过选择购买 RackNerd VPS，您已经迈出成为网络达人的第一步。接下来的文章将介绍如何管理和优化您的 VPS，确保您可以最大限度地利用这项技术。

## 附录

### FAQ

- 购买 VPS 套餐时，如果浏览器页面显示 out of stock，那么说明这款优惠套餐卖完了，你可能需要自行[在 RackNerd 中选购](https://my.racknerd.com/aff.php?aff=7454)

- 上面提到的 VPS 的具体配置中，Location 其实指的是机房位置，一般选择离中国国内比较近的美国西海岸的机房，速度可能会快一些。

- 在付款页面，RackNerd 目前支持多种付款方式：PayPal、信用卡、支付宝、加密货币等，一般选择支付宝即可，勾选【同意服务条款】，点击【Complete Order】完成订单，在跳转页面用支付宝扫码付款即可完成购买：

- 建议购买至少 1GB 内存配置的 VPS ，以获得更好的使用体验。如果考虑有个人建站及多种应用搭建需求的，至少应选择 2GB 双核以上的配置，经济条件较好的最好能选择 4GB 以上的配置。

- 国内用户，在购买成功之后，最好能通过客户端 ping 测试一下 VPS 的 IP 地址，如果分到了被墙的 IP，可以在购买后 72 小时内免费更换 (点击 Change IP 按钮自助更换)，之后更换一次 IP 需支付 3 美元。

- 如果你发现购买的 VPS 不能满足应用安装的需求，可以通过 ticket 的方式向 RackNerd 说明，如果沟通顺畅，那么可以贴补差价来更换配置更好的 VPS。我当时第一次选了内存不到 1G 的 VPS，后来发现 Ubuntu22 操作系统和部分开源项目都需要至少 1G 内存，通过沟通，在首次购买 10 天后成功支付差价更换了新的 VPS 套餐。

### 资源链接

其实主机服务商有很多，都各有特色，如果希望多了解一些，你也可以自己上网探索，以下是一些常用的主机服务商链接：

[价格实惠的 RackNerd](https://my.racknerd.com/aff.php?aff=7454)

[国内线路优化的 Bandwagon 搬瓦工](https://bandwagonhost.com/aff.php?aff=74873)

[可免费更换 IP 的 Vultr](https://www.vultr.com/?ref=9408843)

[微软 Azure](https://azure.microsoft.com/zh-cn)

[亚马逊 Amazon](https://aws.amazon.com/cn/)

[腾讯云](https://cloud.tencent.com/)

[阿里云](https://cn.aliyun.com)

好了，今天就到这里，如果您按照上述步骤购买了 RackNerd VPS，欢迎分享您的经验。

如果您对 VPS 还有疑问，欢迎您加入我们的“云端生活交流群”，和其它小伙伴一起学习交流。另外您希望我下一篇写什么内容，也欢迎在评论区留言。

如果你觉得我的文章对你有帮助，可以[请我喝咖啡](https://www.buymeacoffee.com/zhurong052Q)

<img src="https://sat02pap005files.storage.live.com/y4m1bQmI2HjlYf8y0-p5ILDLqV4klxYZjjhDZYzn60HpwCTOEot0HfRqsp5RrXVXKechgLZmehuN6udGTqYc3Qudqo73s1tqUAIJul__ZG1-YBMQGkzr8FC9gRj_ywS7n9a_Vpp87CQm1enxUNgrZSKE5wIDvhjixZA3QdOTcwjGnYZRk62QXEWOOAg83tq7Mu1?width=256&height=200&cropmode=none" alt="请我喝咖啡" width="256" height="200" />
