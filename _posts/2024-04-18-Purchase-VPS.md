---
author_profile: true
breadcrumbs: true
categories:
- tech-empowerment
comments: true
date: 2024-04-18 16:45:00 +0000
excerpt: 云主机是开启云端生活的基础设施，本文主要介绍其概念以及如何在RackNerd购买VPS。
header:
  overlay_filter: 0.5
  overlay_image: https://1drv.ms/i/c/5644dab129afda10/IQQQ2q8psdpEIIBWixABAAAAAUSduQ3pBsC8IxuwJNnvW98?width=1024
  teaser: https://1drv.ms/i/c/5644dab129afda10/IQQQ2q8psdpEIIBWixABAAAAAUSduQ3pBsC8IxuwJNnvW98?width=1024
last_modified_at: '2025-06-20 11:00:00'
layout: single
related: true
share: true
tags:
- VPS
- 云服务器
- RackNerd
- 网站搭建
- Linux
- 开源应用
title: 云端启航：轻松拥有自己的VPS，开启你的云端之旅
toc: true
toc_icon: list
toc_label: 本页内容
toc_sticky: true
---

## 引言

在这个数字化和网络化日益深入的时代，掌握关键技术已成为现代人的一项重要能力。《云端生活入门：从小白到网络达人》系列文章，将带您逐步进入技术世界。我们将从基本概念入手，让您了解云端生活的原理，并通过实践操作，完成个人网站搭建、安装开源应用、定制家庭云等功能。

![云端生活](https://1drv.ms/u/c/5644dab129afda10/UQQQ2q8psdpEIIBWghABAAAAACQqWwcwo_DyaCs?height=660)

本系列文章将涵盖以下主题：

- **网站托管**：学习如何使用 VPS 托管个人或商业网站，并搭建 WordPress 网站。
- **开发和测试环境**：学习重新安装 Linux 系统，配置 LNMP 环境，使用 SSH 登录并部署应用。
- **私人云存储**：学习借助 Cloudreve 和 Rclone，创建一个跨平台、多用户的文件存储系统。
- **游戏服务器**：如果您的 VPS 配置允许，可以尝试搭建 Minecraft 或其他游戏的私服。
- **其他用途**：介绍开源应用 Xray、Webmin、NextChat、Trilium 等软件的使用方法。

如果您只想按照步骤实现特定功能，可以直接跳转到相应操作部分。例如，本文将主要介绍 VPS 以及如何购买 RackNerd VPS。

## What & Why - 什么是主机、VPS，为什么要用 VPS？

### 主机及主机服务商

本系列文章旨在通过现代技术，帮助您实现“云端生活”。 这意味着您可以在一台24小时在线的服务器上，安装并运行各种开源程序，并通过网络随时随地访问这些服务。我们常说的主机服务商，例如国外的谷歌、亚马逊、微软，以及国内的阿里、腾讯、华为等，就是提供这类主机服务的公司。

![主机服务商云机房](https://1drv.ms/u/c/5644dab129afda10/UQQQ2q8psdpEIIBWgxABAAAAABY9nJwQ4mFitvo?height=660)

### 主机服务及 VPS

主机服务商通常提供多种主机服务，包括共享主机、虚拟私人服务器（VPS）、专用服务器和云托管等。每种服务都适用于不同的需求和客户。对于个人用户而言，VPS凭借其独特的性价比，提供了类似专用服务器的体验，但成本更低，是理想的云端入门选择。

### 为何选择 VPS 入门？

选择 VPS 的理由在于它的平衡性：相比共享主机，VPS 提供更多控制权和性能；而相比专用服务器和高端云托管服务，它的成本更低。 对于初学者，VPS 是一个理想的学习和实践平台，它结合了经济性、灵活性和足够的资源，让您可以在学习过程中获得充分的实践机会。

## 我推荐的主机服务商 - RackNerd 及 VPS 入门配置

RackNerd 是一家成立于 2019 年的主机服务商，以其高性能、低成本的 VPS 方案而闻名，非常适合入门用户。以下是一些推荐的配置方案：

### 入门 VPS 配置推荐

以下是根据不同需求推荐的三款高性价比 RackNerd KVM VPS 套餐，均为年付价格，非常实惠。

| 套餐名称 | vCPU | 内存 | SSD 存储 | 月流量 | 价格 (年付) | 购买链接 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **入门之选** <br> 适合初学者和基础用户 | 1 核 | 1 GB | 20 GB | 2 TB | **$10.96** | [**点击购买**](https://my.racknerd.com/aff.php?aff=7454&pid=912) |
| **建站优选** <br> 适合搭建网站或开源应用 | 3 核 | 3.5 GB | 60 GB | 5 TB | **$29.89** | [**点击购买**](https://my.racknerd.com/aff.php?aff=7454&pid=914) |
| **性能之选** <br> 适合家庭云盘或游戏私服 | 4 核 | 5 GB | 100 GB | 10 TB | **$54.99** | [**点击购买**](https://my.racknerd.com/aff.php?aff=7454&pid=915) |

---

### 温馨提示

💡 如果点击上方链接后，页面提示 **“Out of Stock”** 或 **“Sold Out”**，这说明该特价套餐已暂时售罄。RackNerd 的优惠活动经常更新，您可以访问其 [**主页**](https://my.racknerd.com/aff.php?aff=7454) 查看当前正在进行的其他优惠活动。

## 购买 VPS 过程

1. **选择套餐：** 首先确定您的需求，然后选择适合自己的套餐，这里以我在2023年购买的$23.88的套餐为例：

请注意，如果您选择的是其它套餐或者其他服务商提供的 VPS，以下步骤仅供参考。

点击购买链接，将跳转到 Racknerd 的购物车页面。如果您想使用中文，可以在 View Cart 按钮旁边选择“中文”，或者使用浏览器的翻译功能。后续介绍将以英文界面为主，如果阅读英文有困难，请自行摸索是否有中文界面或使用浏览器翻译功能进行调整。

2. **确认配置：** 如果您想跟随本系列文章，一步一步完成多个家庭应用的搭建，建议至少选择内存2G以上的套餐。点击链接后，应该会看到类似这样的画面：

![vps conf](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWeBABAAAAAERnB9d1Fj51XRE?width=660)

这个截图列出了您选择的 VPS 的基本配置，包括 2 核 CPU、2.5G 内存、38G SSD 硬盘、6000G 月带宽、1G 连接速度以及 1 个 IPv4 公网 IP 地址。 此外，还包含用于管理 VPS 的控制面板，并允许选择全球多个数据中心。付费周期为年付 23.88 美元。

如果您想调整部分参数（包括硬件配置），下面的画面提供了可选参数：

![可选参数](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWeRABAAAAAHpUXvHhEiJri8o?width=660)

如果您是中国大陆的用户，建议只调整 Operating System（操作系统）和 Location（机房位置）这两个参数。 Operating System 选择 Ubuntu 22.04 64 Bit，Location 选择 San Jose CA。查看一下 Order Summary，合计金额应该还是 23.88 美元。点击 Continue，进入确认页面：

![确认页面](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWehABAAAAAEiX0TN_1fWZO6Y?width=660)

3. **填写个人信息：** 点击绿色的 Checkout 按钮，填入个人信息。 注意页面中已经有 China 相关选项，您可以填写自己的真实地址。

![填写个人信息](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWexABAAAAAM-9-N_LC5iYB7Y?width=660)

4. **付款：** 在 Payment Details（付款）中，选择您喜欢的付款方式，包括支付宝和银联卡。

![](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWfBABAAAAAMvAFGXQR9HsDsU?width=946&height=363)

最后，勾选 "I have read and agree to the Terms of Service" 并点击 "Complete Order" 即可。

5. **查收邮件：** 之后您会收到多封 RackNerd 发来的欢迎邮件，其中会告知您如何登录自己的账户、如何获得支持、订单支付情况和发票等信息。 特别注意一封名为 "KVM VPS Login Information" 的邮件，请务必保存其中的 root password。

![确认邮件](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWfRABAAAAAGLUlL290GCeduY?width=602&height=550)

至此，购买 VPS 的步骤就完成了！ 您已经拥有一台完全可控、可以 24 小时访问的服务器。 后续我们将探讨如何管理这台 VPS，并利用免费的开源项目，完成私有云存储、家庭影院、代理服务器、共享 ChatGPT 等各种实用功能。 这样，您就能构建一个 7*24 小时可用的、家庭或小范围的私有云端服务。 下面是一些使用这台 VPS 搭建的应用示例：

使用开源项目 Cloudreve，搭建免费的私有化云存储方案：

![cloudreve](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWkhABAAAAAENDRKObZ8mnQzQ?width=660)

使用开源项目 Trilium，搭建免费的个人笔记（知识库）系统：

![trilium](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWgBABAAAAABbCG9Mx5P0ezD0?width=660)

使用开源项目 NextChat，搭建免费的共享 LLM，可使用ChatGPT 或 Gemini等模型：

![nextchat](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWgRABAAAAAHEM9bf9PGrkDp4?width=660)

使用开源项目 Jellyfin，搭建免费的家庭影音系统：

![jellyfin](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWlBABAAAAAKhaUh0xYmeqHOc?width=660)

今天，我们完成了对主机、主机服务商和 VPS 的初步认识，并通过 RackNerd 网站完成了用户注册购买的流程。

## 结论

通过选择购买 RackNerd VPS，您已经迈出了成为网络达人的第一步。 接下来的文章将介绍如何管理和优化您的 VPS，确保您可以最大限度地利用这项技术。

## 附录

### FAQ

- 如果购买 VPS 套餐时，浏览器页面显示 "out of stock"，说明该优惠套餐已售罄。您可以自行[在 RackNerd 中选购](https://my.racknerd.com/aff.php?aff=7454)其他套餐。

- 上面提到的 VPS 的具体配置中，"Location" 指的是机房位置。 一般选择离中国大陆比较近的美国西海岸机房，速度可能会更快一些。

- 在付款页面，RackNerd 目前支持多种付款方式：PayPal、信用卡、支付宝、加密货币等。 一般选择支付宝即可。勾选 "同意服务条款"，点击 "Complete Order" 完成订单，并在跳转页面使用支付宝扫码付款即可完成购买。

- 建议购买至少 1GB 内存配置的 VPS，以获得更好的使用体验。如果考虑个人建站和多种应用搭建的需求，至少应选择 2GB 双核以上的配置，预算充足的话，最好选择 4GB 以上的配置。

- 国内用户在购买成功之后，最好通过客户端 ping 测试一下 VPS 的 IP 地址。 如果分配到了被墙的 IP，可以在购买后 72 小时内免费更换 (点击 "Change IP" 按钮自助更换)。之后更换一次 IP 需支付 3 美元。

- 如果您发现购买的 VPS 不能满足应用安装的需求，可以通过 ticket 的方式向 RackNerd 说明。如果沟通顺畅，可以贴补差价来更换配置更好的 VPS。 我当时第一次选择了内存不到 1G 的 VPS，后来发现 Ubuntu22 操作系统和部分开源项目都需要至少 1G 内存。通过沟通，在首次购买 10 天后成功支付差价更换了新的 VPS 套餐。

### 资源链接

其实主机服务商有很多，都各有特色。 如果希望多了解一些，您可以自行上网探索。 以下是一些常用的主机服务商链接：

[价格实惠的 RackNerd](https://my.racknerd.com/aff.php?aff=7454)

[国内线路优化的 Bandwagon 搬瓦工](https://bandwagonhost.com/aff.php?aff=74873)

[可免费更换 IP 的 Vultr](https://www.vultr.com/?ref=9408843)

[微软 Azure](https://azure.microsoft.com/zh-cn)

[亚马逊 Amazon](https://aws.amazon.com/cn/)

[腾讯云](https://cloud.tencent.com/)

[阿里云](https://cn.aliyun.com)

好了，今天就到这里。如果您按照上述步骤购买了 RackNerd VPS，欢迎分享您的经验。

如果您对 VPS 还有疑问，欢迎您加入我们的“云端生活交流群”，和其他小伙伴一起学习交流。另外，您希望我下一篇写什么内容，也欢迎在评论区留言。


如果你觉得我的文章对你有帮助，可以[请我喝咖啡](https://www.buymeacoffee.com/zhurong052Q)

<a href="https://www.buymeacoffee.com/zhurong052Q" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

> 💬 **发表评论**: 您需要有一个 GitHub 账号来发表评论。