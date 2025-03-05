---
author_profile: true
breadcrumbs: true
categories:
- 技术实践
- 云服务
comments: true
date: 2024-04-27 16:45:00 +0000
excerpt: Putty 和 WinSCP 是最重要的二个工具，帮助 Windows 用户实现远程登录 VPS 和文件传输，本文介绍这两个工具的介绍、下载、安装和配套使用案例
header:
  overlay_filter: 0.5
  overlay_image: https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/09dcfb9b-8b95-406a-231f-cf9d93970c00/public
  teaser: https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/09dcfb9b-8b95-406a-231f-cf9d93970c00/public
last_modified_at: '2025-03-05 10:24:43'
layout: single
related: true
share: true
tags:
- VPS
- PuTTY
- WinSCP
- Linux
- 服务器管理
title: VPS管理指南：掌握PuTTY与WinSCP的协同魔法
toc: true
toc_icon: list
toc_label: 本页内容
toc_sticky: true
---

## VPS 管理指南：利用 PuTTY 与 WinSCP 提升效率

PuTTY 和 WinSCP 是管理 VPS 的两款重要工具，尤其能帮助 Windows 用户轻松实现远程登录和文件传输。本文将介绍这两款工具的功能、下载、安装以及协同使用的方法，并在文末提供 Linux Ubuntu 常用命令参考。

@[toc]

### 引言

云计算时代，服务器管理不再遥不可及。PuTTY 和 WinSCP 这两款工具，无论是对于 IT 初学者还是资深用户，都能让 VPS 管理工作变得简单高效。本文将介绍它们的核心功能、下载安装过程，并通过实例助你快速入门。此外，文末还准备了 Linux Ubuntu 下的常用命令，助力你的云端操作。

![PuttyWinSCP](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/70499ab7-ba41-40c5-e54b-333dd58a7600/public)

### 为什么选择这两款工具？

拥有 VPS 后，你需要进行各种远程操作，例如软件安装和日常维护。PuTTY 和 WinSCP 正是你与服务器沟通的桥梁。PuTTY 提供稳定的命令行访问，方便你在 VPS 上运行各种操作；WinSCP 则简化了文件的上传和下载过程。二者结合，能带来直观高效的服务器管理体验，尤其在数据安全和操作便利性方面，更胜一筹。

### PuTTY 篇

#### PuTTY 是什么？

PuTTY 是一款适用于 Windows 的 SSH 和 Telnet 客户端，是远程服务器管理的利器。只需简单几步，你就能通过它登录 VPS 并执行所需命令。掌握基本功能后，建议学习如何通过 PuTTYgen 生成 SSH 密钥对，实现更安全的免密码登录。

![Putty网址](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c9ddab05-ab4e-4009-e0f3-b8958948c500/public)

例如，当你需要查看 VPS 的硬盘容量或操作系统信息时，就需要先通过 PuTTY 登录 VPS，然后执行相应的指令。

![Putty已登录](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/3fcd957d-cbaf-4031-dfea-db1242547100/public)

##### 如何下载 PuTTY

访问 PuTTY 官网：https://www.putty.org/，点击 "Download PuTTY"。根据你的操作系统选择合适的版本下载安装。本文末尾提供了 64 位 Windows 版本 (0.81) 的安装文件。

![Putty下载页面](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/6f072324-fc7a-4b47-792b-44eaa6a51200/public)

##### 如何安装 PuTTY

运行下载的 Windows 安装文件，按照屏幕提示操作即可完成安装。

![Putty安装界面](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/f34cda6f-1f8d-4890-b14b-69f09acc5400/public)

##### 基本使用方法

1.  **连接到 VPS：** 输入你的 VPS IP 地址和 SSH 端口，建立连接。

    ![Putty登录](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c8ed5dc1-3c3f-48a7-eddf-1de8b03ecb00/public)

2.  **常用命令和操作：** 连接到 VPS 后，你需要熟悉 Linux 的一些基本命令，例如更新软件包、安装应用程序等。文末附录了 Linux 下的 8 类常用命令，你可以逐一尝试，具体命令详见附件。

##### 进阶技巧分享

**自动登录设置：** 学习如何在 PuTTY 中保存会话，提高效率。

![putty自动东路](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/f724bbef-8e9b-4ace-005e-b48863c90e00/public)

文末提供了 PuTTY 的帮助文档。

### WinSCP 篇

#### WinSCP 是什么？

WinSCP 是一款强大的文件管理工具，能让你轻松在本地和服务器之间传输文件。它的同步功能还能有效管理文件版本，确保数据的一致性和完整性。

![winscp介绍](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/2233ff89-3161-40fc-a090-bcc022cfbe00/public)

##### 如何下载 WinSCP

访问 WinSCP 官网：https://winscp.net/，点击 "Download"。选择合适的方式下载安装。本文末尾提供了 WinSCP 6.3.3 的安装文件。

![winscp官网](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/ef72d206-da77-447f-2816-761cc53aff00/public)

##### 如何安装 WinSCP

运行下载的 Windows 安装文件，按照屏幕提示操作即可完成安装。

![winscp安装](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/4c4e5382-c6f3-4114-129e-8d8f8e651300/public)

##### 基本使用方法

安装完成后，运行 WinSCP，会出现以下界面：

![winscp界面](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/d912faea-298f-4be6-96ad-4e38714b2700/public)

1.  **连接到 VPS：** 和 PuTTY 类似，输入目标服务器的 IP 地址和用户名。

    ![winscp登录vps](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/26e90693-aa4a-4046-5de5-2d04b4563000/public)

    成功登录后，界面如下：

    ![winscp成功登录](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/a3cf8023-d536-4bdd-6dfd-71b88b480b00/public)

2.  **使用鼠标拖放完成文件操作：**
    界面左侧是本地目录文件，右侧是服务器端的文件。如果需要复制文件，直接拖动即可。

### 结合使用 PuTTY 和 WinSCP

通过 PuTTY 和 WinSCP 的协作，你可以在 WinSCP 中轻松管理文件，同时在 PuTTY 中执行必要的命令操作。例如，使用 WinSCP 的图形界面上传文件，然后在 PuTTY 中执行服务器上的安装脚本。两者的协同工作能让 VPS 的维护和管理变得无比简便。

#### 先使用 PuTTY 登录你的服务器

连接并登录服务器后，可以看到命令行的窗口。使用常用命令切换目录并列出当前目录下的文件：

![putty登录VPS](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/823ff181-8d6d-4bc3-2504-02f63124cb00/public)

如果你对 Linux 不熟悉，请注意观察屏幕，绿色光标为可以输入命令的提示符，光标之前分别显示登录用户、VPS 的主机名称和当前目录。
文末附录了 Linux Ubuntu 下的常用命令，小伙伴们可以逐个练习。后期安装开源软件时，可能用到的命令不多，但需要习惯 Linux 下命令的输入和回显形式。

#### 接着打开 WinSCP 登录服务器

使用 PuTTY 连接 VPS 后，你就可以在 VPS 端输入各种命令了。但进行文件操作时，新手可能会对 Linux 下的命令行感到困惑。这时可以使用 WinSCP 来操作。同样使用 WinSCP 先登录服务器，注意观察以下界面：

![winscp登录vps](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/78cc0c8f-1e51-42f1-09da-2d41da09e400/public)

#### 从本地复制文件到 VPS

WinSCP 界面中有很多要素，最重要的是当前目录。注意屏幕的左半部分是本地目录，右半部分是 VPS 目录。如果你想从本地向 VPS 传输文件，选择好对应的目录后，将左侧需要复制的文件拖动到右侧窗口即可。如果遇到以下提示：

![winscp登录错误](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/fbeee394-6e8f-4d77-7db2-3d6bc09ccb00/public)

说明服务器上的目录没有权限，你需要在 VPS 上使用命令更改权限，或者更换一个你有权限的目录。权限正常后，你就能看到复制进度：

![winscp复制文件](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/cdf4caff-f7ea-4bae-4d60-f90e2c1bde00/public)

#### 其他

##### 高级技巧

PuTTY 和 WinSCP 都有更高级的技巧，例如通过创建 SSH 密钥对实现免密码登录，共享会话，使用 WinSCP 进行定时备份服务器文件，以及直接从 WinSCP 中拖放文件到 PuTTY 窗口等。熟悉基本功能后，可以深入探索这些高级技巧。

##### 实战案例

我们提供一个具体的案例，让大家练习上面提到的工具以及常用 Linux 命令，实现将在线的帮助文档保存到本地的功能。如果你掌握了这个案例的用法，还可以玩出很多新花样。

WinSCP 目前没有提供离线的帮助文档，但我们可以使用 Linux 的 wget 命令，并结合 PuTTY 和 WinSCP，从 WinSCP 网站的在线文档 "https://winscp.net/eng/docs/" 中下载所有页面，再通过 WinSCP 传输到 Windows，实现本地查看。答案见文末。

### 结语

本文介绍了 PuTTY 和 WinSCP 这两款免费软件的功能、下载安装方法，并进行了简单演示。文末还提供了一些资源链接，旨在帮助你快速上手 VPS 管理。如果您对今天介绍的软件还有疑问，欢迎加入 "云端生活交流群"。

您可以添加以下微信，等待确认后会拉你入群。请先查看群公告完成群代办，之后就可以和其他伙伴愉快交流了。我们将聚合一些志同道合的朋友，以便在知识探索的路上互相帮助，互相成就。另外，欢迎在评论区留言，告诉我你希望下一篇写什么内容。

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169811&authkey=%21ABRiiNUJymdww3o&height=256" alt="monty二维码" width="auto" height="256" />

### 附件（以下为百度网盘下载链接）：

[Putty Windows 64 0.81 提取码：hhyp](https://pan.baidu.com/s/1rqTE1YxkeJvCStnUmeuPqQ?pwd=hhyp)

[Putty 帮助文档 提取码：b3yl](https://pan.baidu.com/s/1KlThDxnC91weq03x1w48Pg?pwd=b3yl)

[WinSCP 6.3.3（Windows）提取码：wp3c](https://pan.baidu.com/s/1PMw9hjCbeBHw8WD3-9R9vQ?pwd=wp3c)

[WinSCP 帮助文档 提取码：3q3t](https://pan.baidu.com/s/10KVbtlHgH_5vVI8VFzARow?pwd=3q3t)

[Linux 常用的操作命令 提取码：7ekv](https://pan.baidu.com/s/1lB0MHBjADbrxRWc1Whwzww?pwd=7ekv)

关于实战案例的答案：

1.  使用 PuTTY 登录 VPS
2.  查看 WinSCP 的在线文档结构
    1.  发现这些文档都在这个网址：https://winscp.net/eng/docs/
    2.  比如介绍页面是："https://winscp.net/eng/docs/introduction"
    3.  比如配置要求页面是："https://winscp.net/eng/docs/requirements"
3.  使用 wget 下载 WinSCP 的在线文档
    1.  如果没有 wget，可以先安装
        1.  sudo apt update
        2.  sudo apt install wget
    2.  使用 wget 命令下载：
        1.  wget -r -np -p -k --adjust-extension --no-check-certificate -H -Dwinscp.net -I /eng/docs https://winscp.net/eng/docs
        2.  参数详解：
            1.  -r (--recursive): 递归下载，表示 wget 将递归地下载所有遇到的链接。
            2.  -np (--no-parent): 在递归下载时不爬行父目录。这样，wget 不会返回到 /eng/docs 之上的目录层次去下载内容。
            3.  -p (--page-requisites): 下载显示 HTML 页面所需要的所有资源，包括图片、CSS、JavaScript 等。
            4.  -k (--convert-links): 转换页面中的链接，下载后可以离线查看。它会尝试将每个页面的链接转换为本地相对链接，这样本地浏览时所有链接都能正确指向。
            5.  --adjust-extension: 如果下载的文件是 HTML 或 CSS，并且 URL 没有以 .html 或 .css 结尾，wget 将自动添加相应的扩展名。这有助于本地文件与其原有的 MIME 类型相匹配。
            6.  --no-check-certificate: 跳过 SSL 证书验证。这在你访问的服务器证书无效或者你的环境中缺少必要的 CA 证书时很有用。
            7.  -H (--span-hosts): 允许递归下载操作跨越到不同的主机。这是必须的，因为某些页面的资源可能托管在与页面不同的域上。
            8.  -Dwinscp.net: 限制 -H，使 wget 只在 winscp.net 域内跨越主机下载。
            9.  -I /eng/docs: 限制 wget 的递归下载到指定的目录路径。这意味着只有当 URL 路径以 /eng/docs 开始时，wget 才会下载。
4.  使用 WinSCP 登录 VPS，并切换到正确的目录
5.  通过 WinSCP 将已经下载后的文档（目录）复制到 Windows 本地
6.  找到目录中的 Index.html，双击查看


如果你觉得我的文章对你有帮助，可以[请我喝咖啡](https://www.buymeacoffee.com/zhurong052Q)

<a href="https://www.buymeacoffee.com/zhurong052Q" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

> 💬 **发表评论**: 您需要有一个 GitHub 账号来发表评论。