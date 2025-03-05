---
author_profile: true
breadcrumbs: true
categories:
- 技术实践
comments: true
date: 2024-04-27 16:45:00 +0000
excerpt: Putty 和 WinSCP 是最重要的二个工具，帮助 Windows 用户实现远程登录 VPS 和文件传输，本文介绍这两个工具的介绍、下载、安装和配套使用案例
header:
  overlay_filter: 0.5
  overlay_image: https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/ad82ce33-b9f3-4dd7-fe15-8e5df7091e00/public
  teaser: https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/ad82ce33-b9f3-4dd7-fe15-8e5df7091e00/public
last_modified_at: '2025-03-05 08:40:44'
layout: single
related: true
share: true
tags:
- VPS
- PuTTY
- WinSCP
- 服务器管理
- Linux
title: VPS管理指南：掌握PuTTY与WinSCP的协同魔法
toc: true
toc_icon: list
toc_label: 本页内容
toc_sticky: true
---

## VPS 管理指南：掌握 PuTTY 与 WinSCP 的协同魔法

PuTTY 和 WinSCP 是管理 VPS 的两款必备工具，它们能帮助 Windows 用户轻松实现远程登录和文件传输。本文将详细介绍这两款工具的功能、下载、安装，并通过实际案例演示它们的协同使用。此外，文末还提供了 Linux Ubuntu 下的常用命令，供您参考。

<!-- more -->

@[toc]

### 引言

云计算的普及，降低了服务器管理的门槛。无论是 IT 新手还是经验丰富的用户，PuTTY 和 WinSCP 都能让 VPS 管理工作变得简单而高效。本文将介绍这两款工具的核心功能、下载与安装步骤，并通过实例引导您快速上手。同时，我们还精心准备了 Linux Ubuntu 常用命令指南，助您轻松驾驭云端操作。

![PuttyWinSCP](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

### 为什么选择 PuTTY 和 WinSCP？

拥有 VPS 后，您需要进行各种远程操作，例如软件安装和日常维护。PuTTY 和 WinSCP 正是连接您与服务器的桥梁。PuTTY 提供稳定的命令行访问，让您在 VPS 上执行各种操作；WinSCP 则简化了文件的上传与下载流程。二者结合，带来直观高效的服务器管理体验，尤其在数据安全和操作便捷性方面，它们表现出色。

### PuTTY 篇

#### PuTTY 是什么？

PuTTY 是一款适用于 Windows 的 SSH 和 telnet 客户端，是远程服务器管理的强大工具。只需简单几步，您就可以通过它登录 VPS 并执行命令。掌握基本功能后，建议您学习如何通过 PuTTYgen 生成 SSH 密钥对，实现更安全的免密码登录。

![Putty网址](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

例如，当您需要查看 VPS 的硬盘容量或操作系统信息时，需要先通过 PuTTY 登录 VPS，然后执行相应的指令。

![Putty已登录](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

##### 如何下载 PuTTY

访问 PuTTY 官网：https://www.putty.org/，点击“Download PuTTY”。
根据您的操作系统选择合适的版本进行下载安装。本文末尾提供了 64 位 Windows 版本（0.81）的安装文件。

![Putty下载页面](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

##### 如何安装 PuTTY

运行下载的 Windows 安装文件，按照屏幕提示操作，即可快速完成安装。

![Putty安装界面](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

##### 基本使用方法

1.  **连接到 VPS：** 输入您的 VPS IP 地址和 SSH 端口，建立连接。

    ![Putty登录](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

2.  **常用命令和操作：** 连接到 VPS 后，您需要熟悉 Linux 的一些基本命令，例如更新软件包、安装应用程序等。文末附有 Linux 下的 8 类常用命令，您可以逐一尝试，详细命令见附件。

##### 进阶技巧分享

**自动登录设置：** 学习如何在 PuTTY 中保存会话，提高效率。

![putty自动东路](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

文末提供了 PuTTY 的帮助文档。

### WinSCP 篇

#### WinSCP 是什么？

WinSCP 是一款功能强大的文件管理工具，让本地与服务器之间的文件传输变得轻松便捷。其同步功能还能有效管理文件版本，确保数据的一致性和完整性。

![winscp介绍](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

##### 如何下载 WinSCP

访问 WinSCP 官网：https://winscp.net/，点击“Download”。
选择合适的下载方式进行安装。本文末尾提供了 WinSCP 6.3.3 的安装文件。

![winscp官网](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

##### 如何安装 WinSCP

运行下载的 Windows 安装文件，按照屏幕提示操作，即可快速完成安装。

![winscp安装](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

##### 基本使用方法

安装完成后，运行 WinSCP，会出现以下界面：

![winscp界面](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

1.  **连接到 VPS：** 类似于 PuTTY，输入目标服务器的 IP 地址、用户名和密码。

    ![winscp登录vps](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

    成功登录后，您会看到如下界面：

    ![winscp成功登录](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

2.  **使用鼠标拖放完成文件操作：** 界面左侧显示本地目录文件，右侧显示服务器端文件。您可以通过拖动文件来完成复制操作。

### 结合使用 PuTTY 和 WinSCP

通过 PuTTY 和 WinSCP 的协作，您可以在 WinSCP 中轻松管理文件，并在 PuTTY 中执行必要的命令操作。例如，使用 WinSCP 的图形界面上传文件，然后在 PuTTY 中执行服务器上的安装脚本。两者的协同工作，使 VPS 的维护和管理变得无比简便。

#### 先使用 PuTTY 登录服务器

连接并登录服务器后，您会看到命令行窗口。使用常用命令切换目录并列出当前目录下的文件：

![putty登录VPS](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

如果您对 Linux 不熟悉，请注意观察屏幕，绿色光标为命令输入提示符，光标之前分别显示了登录用户、VPS 主机名称和当前目录。文末附上了 Linux Ubuntu 下的常用命令，您可以逐个练习。在后续安装开源软件时，您可能用到的命令并不多，但需要逐渐习惯 Linux 下的命令输入和回显形式。

#### 接着打开 WinSCP 登录服务器

使用 PuTTY 连接 VPS 后，您可以在 VPS 端输入各种命令。但当您需要进行文件操作时，新手可能会对 Linux 下的命令行感到困惑。此时，您可以使用 WinSCP 进行操作。同样，首先使用 WinSCP 登录服务器，并注意观察以下界面：

![winscp登录vps](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

#### 从本地复制文件到 VPS

WinSCP 界面包含许多元素，最重要的是当前目录。请注意，屏幕的左半部分是本地目录，右半部分是 VPS 目录。如果您想从本地向 VPS 传输文件，选择好对应的目录后，将左侧需要复制的文件拖动到右侧窗口即可。如果遇到以下提示：

![winscp登录错误](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

则说明服务器上的目录没有权限。您需要在 VPS 上使用命令更改权限，或者更换一个您拥有权限的目录。权限正常后，您就能看到复制进度：

![winscp复制文件](https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c5090890-e063-4da8-c406-396d7eb23400/public)

#### 其他

##### 高级技巧

PuTTY 和 WinSCP 都有更高级的技巧，例如通过创建 SSH 密钥对实现免密码登录，共享会话，使用 WinSCP 进行定时备份服务器文件，以及直接从 WinSCP 中拖放文件到 PuTTY 窗口等。在熟悉基本功能后，您可以深入探索这些高级技巧。

##### 实战案例

下面我们提供一个具体的案例，让大家练习上面提到的工具以及常用的 Linux 命令。通过这个案例，我们可以实现将在线的帮助文档保存到本地的功能。如果您掌握了这个案例的用法，还可以玩出很多新花样。

WinSCP 目前没有提供离线的帮助文档，但我们可以使用 Linux 的 wget 命令，再结合本文提到的 PuTTY 和 WinSCP，从 WinSCP 网站的在线文档“https://winscp.net/eng/docs/”中下载所有页面，并通过 WinSCP 传输到 Windows，实现本地查看。答案见文末。

### 结语

本文介绍了 PuTTY 和 WinSCP 这两款免费软件的功能、下载安装方法，并对软件使用进行了简单演示。文末还提供了一些资源链接，旨在帮助您快速上手 VPS 管理。如果您对本文介绍的软件还有疑问，欢迎加入我们的“云端生活交流群”。
您可以添加以下微信，等待确认后会拉您入群。请先查看群公告完成群代办，之后就可以和其他伙伴愉快交流了。我们将聚集一些志同道合的朋友，以便在知识探索的道路上互相帮助，互相成就。另外，欢迎您在评论区留言，分享您希望我下一篇文章撰写的内容。

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
    2.  比如介绍页面是：“https://winscp.net/eng/docs/introduction”
    3.  比如配置要求页面是：“https://winscp.net/eng/docs/requirements”
3.  使用 wget 下载 WinSCP 的在线文档
    1.  如果没有 wget，可以先安装
        1.  sudo apt update
        2.  sudo apt install wget
    2.  使用 wget 命令下载：
        1.  wget -r -np -p -k --adjust-extension --no-check-certificate -H -Dwinscp.net -I /eng/docs https://winscp.net/eng/docs
        2.  参数详解：
            1.  -r (--recursive): 递归下载，表示 wget 将递归地下载所有遇到的链接。
            2.  -np (--no-parent): 在递归下载时不爬行父目录。这样，wget 不会返回到/eng/docs 之上的目录层次去下载内容。
            3.  -p (--page-requisites): 下载显示 HTML 页面所需要的所有资源，包括图片、CSS、JavaScript 等。
            4.  -k (--convert-links): 转换页面中的链接，下载后可以离线查看。它会尝试将每个页面的链接转换为本地相对链接，这样本地浏览时所有链接都能正确指向。
            5.  --adjust-extension: 如果下载的文件是 HTML 或 CSS，并且 URL 没有以.html 或.css 结尾，wget 将自动添加相应的扩展名。这有助于本地文件与其原有的 MIME 类型相匹配。
            6.  --no-check-certificate: 跳过 SSL 证书验证。这在你访问的服务器证书无效或者你的环境中缺少必要的 CA 证书时很有用。
            7.  -H (--span-hosts): 允许递归下载操作跨越到不同的主机。这是必须的，因为某些页面的资源可能托管在与页面不同的域上。
            8.  -Dwinscp.net: 限制-H，使 wget 只在 winscp.net 域内跨越主机下载。
            9.  -I /eng/docs: 限制 wget 的递归下载到指定的目录路径。这意味着只有当 URL 路径以/eng/docs 开始时，wget 才会下载。
4.  使用 WinSCP 登录 VPS，并切换到正确的目录
5.  通过 WinSCP 将下载后的文档（目录）复制到 Windows 本地
6.  找到目录中的 Index.html，双击查看


如果你觉得我的文章对你有帮助，可以[请我喝咖啡](https://www.buymeacoffee.com/zhurong052Q)

<a href="https://www.buymeacoffee.com/zhurong052Q" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

> 💬 **发表评论**: 您需要有一个 GitHub 账号来发表评论。