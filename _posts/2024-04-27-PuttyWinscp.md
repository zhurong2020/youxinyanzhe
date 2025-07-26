---
author_profile: true
breadcrumbs: true
categories:
- tech-empowerment
comments: true
date: 2024-04-27 16:45:00 +0000
excerpt: Putty 和 WinSCP 是远程登录VPS最重要的二个工具，本文介绍这两个工具的介绍、下载、安装和配套使用案例。
header:
  overlay_filter: 0.5
  overlay_image: https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWCREBAAAAAA48lEQjPg-XcKw?width=660
  teaser: https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWCREBAAAAAA48lEQjPg-XcKw?width=660
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


### 引言

云计算时代，服务器管理不再遥不可及。PuTTY 和 WinSCP 这两款工具，无论是对于 IT 初学者还是资深用户，都能让 VPS 管理工作变得简单高效。本文将介绍它们的核心功能、下载安装过程，并通过实例助你快速入门。此外，文末还准备了 Linux Ubuntu 下的常用命令，助力你的云端操作。

![PuttyWinSCP](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWCREBAAAAAA48lEQjPg-XcKw?width=660)

### 为什么选择这两款工具？

拥有 VPS 后，你需要进行各种远程操作，例如软件安装和日常维护。PuTTY 和 WinSCP 正是你与服务器沟通的桥梁。PuTTY 提供稳定的命令行访问，方便你在 VPS 上运行各种操作；WinSCP 则简化了文件的上传和下载过程。二者结合，能带来直观高效的服务器管理体验，尤其在数据安全和操作便利性方面，更胜一筹。

### PuTTY 篇

#### PuTTY 是什么？

PuTTY 是一款适用于 Windows 的 SSH 和 Telnet 客户端，是远程服务器管理的利器。只需简单几步，你就能通过它登录 VPS 并执行所需命令。掌握基本功能后，建议学习如何通过 PuTTYgen 生成 SSH 密钥对，实现更安全的免密码登录。

![Putty网址](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWAxEBAAAAAFppTKcu8cfS2Eo?width=660)

例如，当你需要查看 VPS 的硬盘容量或操作系统信息时，就需要先通过 PuTTY 登录 VPS，然后执行相应的指令。

![Putty已登录](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWBhEBAAAAAAQe7bvCcv0ZAMg?width=660)

##### 如何下载 PuTTY

访问 PuTTY 官网：https://www.putty.org/，点击 "Download PuTTY"。根据你的操作系统选择合适的版本下载安装。本文末尾提供了 64 位 Windows 版本 (0.81) 的安装文件。

![Putty下载页面](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWBREBAAAAAAhNnTuuzWjx57M?width=660)

##### 如何安装 PuTTY

运行下载的 Windows 安装文件，按照屏幕提示操作即可完成安装。

![Putty安装界面](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWBBEBAAAAAP4tETGqIc2pBDc?width=621&height=486)

##### 基本使用方法

1.  **连接到 VPS：** 输入你的 VPS IP 地址和 SSH 端口，建立连接。

    ![Putty登录](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWDREBAAAAAB6UjS6nu__2fa8?width=619&height=551)

2.  **常用命令和操作：** 连接到 VPS 后，你需要熟悉 Linux 的一些基本命令，例如更新软件包、安装应用程序等。文末附录了 Linux 下的 8 类常用命令，你可以逐一尝试，具体命令详见附件。

##### 进阶技巧分享

**自动登录设置：** 学习如何在 PuTTY 中保存会话，提高效率。

![putty自动登录](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWFREBAAAAAKluovpN148Tggw?width=619&height=551)

文末提供了 PuTTY 的帮助文档。

### WinSCP 篇

#### WinSCP 是什么？

WinSCP 是一款强大的文件管理工具，能让你轻松在本地和服务器之间传输文件。它的同步功能还能有效管理文件版本，确保数据的一致性和完整性。

![winscp介绍](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWaxEBAAAAAI1HMr5jnFokoCQ?width=660)

##### 如何下载 WinSCP

访问 WinSCP 官网：https://winscp.net/，点击 "Download"。选择合适的方式下载安装。本文末尾提供了 WinSCP 6.3.3 的安装文件。

![winscp官网](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWahEBAAAAADN8miBvroI2tTo?width=660)

##### 如何安装 WinSCP

运行下载的 Windows 安装文件，按照屏幕提示操作即可完成安装。

![winscp安装](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWbBEBAAAAAIDXkk0S0PpIapo?width=660)

##### 基本使用方法

安装完成后，运行 WinSCP，会出现以下界面：

![winscp界面](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWChEBAAAAAF_TbjZHTZJ_tBI?width=660)

1.  **连接到 VPS：** 和 PuTTY 类似，输入目标服务器的 IP 地址和用户名。

    ![winscp登录vps](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWCxEBAAAAAIBL9O4eQcJptyQ?width=480&height=380)

    成功登录后，界面如下：

    ![winscp成功登录](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWDBEBAAAAABhq1zmcSa2dk5g?height=660)

2.  **使用鼠标拖放完成文件操作：**
    界面左侧是本地目录文件，右侧是服务器端的文件。如果需要复制文件，直接拖动即可。

### 结合使用 PuTTY 和 WinSCP

通过 PuTTY 和 WinSCP 的协作，你可以在 WinSCP 中轻松管理文件，同时在 PuTTY 中执行必要的命令操作。例如，使用 WinSCP 的图形界面上传文件，然后在 PuTTY 中执行服务器上的安装脚本。两者的协同工作能让 VPS 的维护和管理变得无比简便。

#### 先使用 PuTTY 登录你的服务器

连接并登录服务器后，可以看到命令行的窗口。使用常用命令切换目录并列出当前目录下的文件：

![putty登录VPS](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWbhEBAAAAAEOPj5-BvOpgyUE?width=660)

如果你对 Linux 不熟悉，请注意观察屏幕，绿色光标为可以输入命令的提示符，光标之前分别显示登录用户、VPS 的主机名称和当前目录。
文末附录了 Linux Ubuntu 下的常用命令，小伙伴们可以逐个练习。后期安装开源软件时，可能用到的命令不多，但需要习惯 Linux 下命令的输入和回显形式。

#### 接着打开 WinSCP 登录服务器

使用 PuTTY 连接 VPS 后，你就可以在 VPS 端输入各种命令了。但进行文件操作时，新手可能会对 Linux 下的命令行感到困惑。这时可以使用 WinSCP 来操作。同样使用 WinSCP 先登录服务器，注意观察以下界面：

![winscp登录vps](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWbxEBAAAAAFJJc5KfQDOdcsk?height=660)

#### 从本地复制文件到 VPS

WinSCP 界面中有很多要素，最重要的是当前目录。注意屏幕的左半部分是本地目录，右半部分是 VPS 目录。如果你想从本地向 VPS 传输文件，选择好对应的目录后，将左侧需要复制的文件拖动到右侧窗口即可。如果遇到以下提示：

![winscp登录错误](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWbREBAAAAAFZb0R_niJQ8mq8?width=621&height=300)

说明服务器上的目录没有权限，你需要在 VPS 上使用命令更改权限，或者更换一个你有权限的目录。权限正常后，你就能看到复制进度：

![winscp复制文件](https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWcBEBAAAAAFXEFgh1DMYbfeQ?width=442&height=255)

#### 其他

##### 高级技巧

PuTTY 和 WinSCP 都有更高级的技巧，例如通过创建 SSH 密钥对实现免密码登录，共享会话，使用 WinSCP 进行定时备份服务器文件，以及直接从 WinSCP 中拖放文件到 PuTTY 窗口等。熟悉基本功能后，可以深入探索这些高级技巧。

##### 实战案例

我们提供一个具体的案例，让大家练习上面提到的工具以及常用 Linux 命令，实现将 WinSCP 在线帮助文档完整保存到本地的功能。
如果你掌握了这个案例的用法，便推开了一扇新世界的大门。 我们今天使用的 wget 命令专注于下载静态网站，这仅仅是冰山一角。得益于活跃的开源社区，还有更多强大的工具等待你去发掘。比如，当你想下载的目标不再是网页，而是 YouTube 或 Bilibili 上的视频时，一个名为 yt-dlp 的命令行工具就能派上用场。

实战案例说明：
WinSCP 的在线文档网址为 https://winscp.net/eng/docs/，通常需要在线手动点击浏览。现在，我们将利用 Linux 的 wget 命令，结合 PuTTY 和 WinSCP 工具，实现一键下载所有帮助页面并在本地查看。
具体操作步骤的答案请参考文末（假设你已经跟随本系列文章，有了自己的VPS）。


### 结语

至此，你已经成功地利用 VPS 作为跳板，将一个完整的在线帮助网站离线到了本地。这个过程完美地诠释了 PuTTY、WinSCP 和 wget 如何协同工作，将复杂的任务简化为几行命令。

但请记住，这仅仅是一个开始。今天我们用 wget 爬取了网站，未来，你还可以用 yt-dlp 去下载高清视频和播放列表，用 gallery-dl 去批量抓取设计网站的画廊图片，甚至用 aria2 来实现多线程高速下载。你的 VPS 就是你的数字宝库，而这些开源命令行工具，正是打开宝库的一把把神奇钥匙。

看到这里，你是否也对这个“数字宝库”心动了呢？
你最想用哪把“钥匙”（工具）来解锁什么样的网络资源？或者，你希望我们下一篇文章深入介绍哪个工具？ 欢迎在下方评论区分享你的想法和感受，让我们一起探索更多可能！

![monty微信](https://1drv.ms/i/c/5644dab129afda10/IQQQ2q8psdpEIIBW5hABAAAAAe_NDogMezQrx4OUzK_BewM?height=660)

### 附件（以下为百度网盘下载链接）：

[Putty Windows 64 0.81 提取码：hhyp](https://pan.baidu.com/s/1rqTE1YxkeJvCStnUmeuPqQ?pwd=hhyp)

[Putty 帮助文档 提取码：b3yl](https://pan.baidu.com/s/1KlThDxnC91weq03x1w48Pg?pwd=b3yl)

[WinSCP 6.3.3（Windows）提取码：wp3c](https://pan.baidu.com/s/1PMw9hjCbeBHw8WD3-9R9vQ?pwd=wp3c)

[WinSCP 帮助文档 提取码：3q3t](https://pan.baidu.com/s/10KVbtlHgH_5vVI8VFzARow?pwd=3q3t)

[Linux 常用的操作命令 提取码：7ekv](https://pan.baidu.com/s/1lB0MHBjADbrxRWc1Whwzww?pwd=7ekv)

关于实战案例的答案：

1.  先通过浏览器查看 WinSCP 的在线文档结构特点
    1.  发现这些文档都在这个网址：https://winscp.net/eng/docs/
    2.  比如介绍页面是："https://winscp.net/eng/docs/introduction"
    3.  比如配置要求页面是："https://winscp.net/eng/docs/requirements"
1.  以下使用Linux命令实现一键下载，先使用 PuTTY 登录自己的 VPS
3.  在VPS上，使用 wget 下载 WinSCP 的在线文档
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
6.  找到本地目录中的 Index.html，双击查看


如果你觉得我的文章对你有帮助，可以[请我喝咖啡](https://www.buymeacoffee.com/zhurong052Q)

<a href="https://www.buymeacoffee.com/zhurong052Q" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

> 💬 **发表评论**: 您需要有一个 GitHub 账号来发表评论。