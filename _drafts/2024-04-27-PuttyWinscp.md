---
# layout: post
title: "VPS管理指南：掌握PuTTY与WinSCP的协同魔法"
date: 2024-04-27 11:17:48 +0000
categories: [技术实践, 工具]
tags: [vps, putty, winscp, ssh, telnet, linux]
pin: false
image:
  # 1200px*630px，860px*780px
  path: "/assets/img/202404/puttywinscp.png"
  lqip: "/assets/img/202404/puttywinscp.png"
  alt: "两款管理VPS的神器Putty和WinSCP"
# 以下文章中涉及的所有的图片均需要增加alt描述

# 下面是WordPress插件Git it Write的字段
post_status: publish
# post_status: draft
post_excerpt: 两款管理VPS的神器Putty和WinSCP
featured_image: /assets/img/202404/puttywinscp.png
taxonomy:
  category:
    - 技术实践
    - 工具
  post_tag:
    - vps
    - putty
    - winscp
    - ssh
    - telnet
    - linux
# custom_fields:
# field1: value 1
# field2: value 2
comment_status: open
stick_post: no
---

VPS 管理指南：掌握 PuTTY 与 WinSCP 的协同魔法

在管理 VPS 时，Putty 和 WinSCP 是最重要的二个工具，帮助 Windows 用户实现远程登录 VPS 和文件传输。本文涉及这两个工具的功能介绍、下载、安装和配套使用案例，另外文末还附上了 Linux Ubuntu 下的常用命令。

<!-- more -->

@[toc]

### 引言：

云计算时代让服务器管理不再是遥不可及的技术壁垒。不论是 IT 初学者还是资深用户，两款神器——PuTTY 和 WinSCP——能令你的虚拟私人服务器（VPS）管理工作变得简单而高效。本文将介绍这两款工具的核心功能、下载与安装过程，并通过实例帮助你快速入门。此外，文末还精心准备了 Linux Ubuntu 下的常用命令指南，让你的云端操作得心应手。

![PuttyWinSCP](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169897&authkey=%21AA48lEQjPg-XcKw&width=660)

### 为什么选择这两款工具

拥有 VPS 后，你需要进行各种远程操作——从软件安装到日常维护，它们是你与服务器沟通的桥梁。PuTTY 提供稳定的命令行访问，使你能够在 VPS 上运行各种操作，而 WinSCP 则简化了文件的上传与下载过程。它们的结合带来了直观高效的服务器管理体验，特别是在数据安全和操作便利性方面，它们比市面上其他工具更加出色。

### Putty 篇章：

#### Putty 是什么

PuTTY，这个适用于 Windows 的 SSH 和 telnet 客户端，是远程服务器管理的利器。简单几步，你就可以通过它登录 VPS 并执行所需命令。当您掌握了它的基本功能后，建议学习如何通过 PuTTYgen 生成 SSH 密钥对，实现更加安全的无密码登录体验。

![Putty网址](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169891&authkey=%21AFppTKcu8cfS2Eo&width=660)

比如，当你需要查看 VPS 的硬盘容量，操作系统信息时，你就需要先通过 Putty 来登录 VPS，然后执行相应的指令。

![Putty已登录](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169894&authkey=%21AAQe7bvCcv0ZAMg&width=660)

##### 如何下载 Putty

首先进入 Putty 官网：https://www.putty.org/，点击“Download Putty”。
根据自己机器的情况，选择合适的版本进行下载安装。我在文末提供了 64 位 windows 版本（0.81）的安装文件。

![Putty下载页面](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169893&authkey=%21AAhNnTuuzWjx57M&width=660)

##### 如何安装

运行刚才下载的 windows 下的安装文件，根据屏幕提示点击，很快就能完成安装。

![Putty安装界面](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169892&authkey=%21AP4tETGqIc2pBDc&width=621&height=486)

##### 基本使用方法

1. 连接到 VPS：介绍如何利用 Putty 输入你的 VPS IP 地址和 SSH 端口来建立连接。

![Putty登录](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169901&authkey=%21AB6UjS6nu__2fa8&width=619&height=551)

2. 常用命令和操作：连接到 VPS 后，你需要熟悉 Linux 的一些基本命令，如更新软件包、安装应用程序等，文末我附上了 Linux 下的 8 类命令，你可以逐一尝试，具体命令详见附件。

##### 进阶技巧分享

自动登录设置：教导如何在 Putty 中保存会话，以提高效率。
![putty自动东路](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169909&authkey=%21AKluovpN148Tggw&width=619&height=551)

文末提供了 Putty 的帮助文档。

### WinSCP 篇章：

#### WinSCP 是什么

WinSCP，一款功能强大的文件管理工具，让文件在本地与服务器之间的传输变得轻而易举。此外，它的同步功能能有效管理文件版本，确保数据的一致性和完整性。
![winscp介绍](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169995&authkey=%21AI1HMr5jnFokoCQ&width=660)

##### 如何下载 WinSCP

首先进入[WinSCP 的官网](https://winscp.net/)：https://winscp.net/，点击“Download”。
选择合适的方式进行下载安装。我在文末提供了 WinSCP6.3.3 的安装文件。
![winscp官网](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169994&authkey=%21ADN8miBvroI2tTo&width=660)

##### 如何安装 WinSCP

运行刚才下载的 windows 下的安装文件，根据屏幕提示点击，很快就能完成安装。
![winscp安装](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169996&authkey=%21AIDXkk0S0PpIapo&width=660)

##### 基本使用方法

安装完成后，运行 winscp，会出现以下画面：
![winscp界面](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169898&authkey=%21AF_TbjZHTZJ_tBI&width=660)

1. 连接到 VPS，和 putty 类似，输入目标服务器的 IP 地址，用户名，继续：
   ![winscp登录vps](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169899&authkey=%21AIBL9O4eQcJptyQ&width=480&height=380)
   成功登录后，会出现这样：
   ![winscp成功登录](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169900&authkey=%21ABhq1zmcSa2dk5g&height=660)

2. 使用鼠标拖放既能完成文件操作
   画面左面是本地的目录文件，右面是服务器端的文件，如果需要复制文件，只要拖动就可以了。

### 结合使用 Putty 和 WinSCP：

通过 PuTTY 和 WinSCP 的协作，你可以在 WinSCP 中轻松管理文件，同时在 PuTTY 中执行必要的命令操作。例如，使用 WinSCP 的图形界面上传文件，然后在 PuTTY 中执行服务器上的安装脚本，两者的协同工作使得 VPS 的维护和管理变得无比简便。

#### 先使用 putty 登录自己的服务器

连接并登录服务器后，可以看到命令行的窗口，我们使用常用命令，切换一个目录并列出当前目录下的文件：
![putty登录VPS](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169998&authkey=%21AEOPj5-BvOpgyUE&width=660)
对 Linux 不熟悉的伙伴，注意观察屏幕，绿色光标为可以输入命令的提示符，光标之前分别能看出登录用户、VPS 的主机名称和当前目录。
我在文末附上了 Linux Ubuntu 下经常使用的命令，小伙伴们可以逐个练习。后期我们安装开源软件时，可能用到的命令并不多，但需要习惯 Linux 下命令的输入和回显形式。

#### 接着打开 winscp 登录服务器

使用 Putty 连接 VPS 后，你就可以在 VPS 端输入各种命令了。不过当你需要进行文件操作时，新手对 Linux 下的命令行可能一头雾水，这时候你可以使用 WinSCP 来操作，同样使用 WinSCP 先登录服务器，注意观察以下画面：
![winscp登录vps](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169999&authkey=%21AFJJc5KfQDOdcsk&height=660)

#### 从本地复制文件到 VPS

WinSCP 画面中有很多要素，最重要的是当前目录，注意屏幕的左半部分是本地目录，右半部分是 VPS 目录。如果你想从本地向 VPS 传输文件，选择好对应的目录后，把在左面需要复制的文件，拖动到右面窗口，就可以了，如果遇到这个画面：
![winscp登录错误](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169997&authkey=%21AFZb0R_niJQ8mq8&width=621&height=300)
是服务器上的目录没有权限，你需要在 VPS 上使用命令更改权限，或者更换换一个自己有权限的目录，权限正常后，你就能看到复制进度：

![winscp复制文件](https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2170000&authkey=%21AFXEFgh1DMYbfeQ&width=442&height=255)

#### 其它

##### 高级技巧

Putty 和 WinSCP 都有更高级的技巧，比如通过创建 SSH 密钥对以实现免密码登录，共享会话，使用 WinSCP 进行定时备份服务器文件,直接从 WinSCP 中拖放文件到 Putty 窗口等。
在熟悉使用基本功能后，可以深入探索上述高级技巧。

##### 实战案例

今天，我们提供一个具体的案例，让大家练习上面提到的工具以及常用 Linux 命令。通过这个案例，我们可以实现将在线的帮助文档保存到本地的功能，如果你掌握了这个案例的用法，还可以玩出很多新花样。

WinSCP 目前没有提供离线的帮助文档，但我们使用 Linux 的 wget 命令，再综合利用本文提到的 Putty 和 WinSCP，可以实现从 WinSCP 网站的在线文档“https://winscp.net/eng/docs/”中下载所有页面，再通过WinSCP软件传输到Windows，实现本地查看。答案见文末。

### 结语：

今天，我们介绍了 Putty 和 WinSCP 这两个免费软件的功能、下载安装方法，并对软件使用进行了简单演示，文末还提供了一些资源链接，旨在帮助你快速上手 VPS 管理。如果您对今天介绍的软件还有疑问，欢迎您加入我们的“云端生活交流群”。
您可以添加以下微信，等待确认后会拉你入群，请先查看群公告完成群代办，之后就可以和其他伙伴愉快交流了。我们将聚合一些志同道合的朋友，以便在知识探索的路上互相帮助，互相成就。另外您希望我下一篇写什么内容，也欢迎在评论区留言。

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169811&authkey=%21ABRiiNUJymdww3o&height=256" alt="monty二维码" width="auto" height="256" />

如果你觉得我的文章对你有帮助，可以[请我喝咖啡](https://www.buymeacoffee.com/zhurong052Q)

<img src="https://sat02pap005files.storage.live.com/y4m1bQmI2HjlYf8y0-p5ILDLqV4klxYZjjhDZYzn60HpwCTOEot0HfRqsp5RrXVXKechgLZmehuN6udGTqYc3Qudqo73s1tqUAIJul__ZG1-YBMQGkzr8FC9gRj_ywS7n9a_Vpp87CQm1enxUNgrZSKE5wIDvhjixZA3QdOTcwjGnYZRk62QXEWOOAg83tq7Mu1?width=256&height=200&cropmode=none" alt="请我喝咖啡" width="256" height="200" />

> 💬 **发表评论**: 本博客的评论功能由 Gitalk 提供，您需要有一个 GitHub 账号来发表评论。如果您还没有账号，请访问 [GitHub](https://github.com/join) 免费注册。注册后，您不仅可以在这里参与讨论，还可以在 GitHub 上发现无数精彩项目和技术交流的机会！

### 附件（以下为百度网盘下载链接）：

[Putty Windows 64 0.81 提取码：hhyp](https://pan.baidu.com/s/1rqTE1YxkeJvCStnUmeuPqQ?pwd=hhyp)

[Putty 帮助文档 提取码：b3yl](https://pan.baidu.com/s/1KlThDxnC91weq03x1w48Pg?pwd=b3yl)

[WinSCP 6.3.3（Windows）提取码：wp3c](https://pan.baidu.com/s/1PMw9hjCbeBHw8WD3-9R9vQ?pwd=wp3c)

[WinSCP 帮助文档 提取码：3q3t](https://pan.baidu.com/s/10KVbtlHgH_5vVI8VFzARow?pwd=3q3t)

[Linux 常用的操作命令 提取码：7ekv](https://pan.baidu.com/s/1lB0MHBjADbrxRWc1Whwzww?pwd=7ekv)

关于实战案例的答案：

1. 使用 Putty 登录 VPS
2. 查看 WinSCP 的在线文档结构
   1. 发现这些文档都是在这个网址：https://winscp.net/eng/docs/
   2. 比如介绍页面是：“https://winscp.net/eng/docs/introduction”
   3. 比如配置要求页面是：“https://winscp.net/eng/docs/requirements”
3. 使用 wget 下载 WinSCP 的在线文档
   1. 如果没有 wget，可以先安装
      1. sudo apt update
      2. sudo apt install wget
   2. 使用 wget 命令下载：
      1. wget -r -np -p -k --adjust-extension --no-check-certificate -H -Dwinscp.net -I /eng/docs https://winscp.net/eng/docs
      2. 参数详解：
         1. -r (--recursive): 递归下载，表示 wget 将递归地下载所有遇到的链接。
         2. -np (--no-parent): 在递归下载时不爬行父目录。这样，wget 不会返回到/eng/docs 之上的目录层次去下载内容。
         3. -p (--page-requisites): 下载显示 HTML 页面所需要的所有资源，包括图片、CSS、JavaScript 等。
         4. -k (--convert-links): 转换页面中的链接，下载后可以离线查看。它会尝试将每个页面的链接转换为本地相对链接，这样本地浏览时所有链接都能正确指向。
         5. --adjust-extension: 如果下载的文件是 HTML 或 CSS，并且 URL 没有以.html 或.css 结尾，wget 将自动添加相应的扩展名。这有助于本地文件与其原有的 MIME 类型相匹配。
         6. --no-check-certificate: 跳过 SSL 证书验证。这在你访问的服务器证书无效或者你的环境中缺少必要的 CA 证书时很有用。
         7. -H (--span-hosts): 允许递归下载操作跨越到不同的主机。这是必须的，因为某些页面的资源可能托管在与页面不同的域上。
         8. -Dwinscp.net: 限制-H，使 wget 只在 winscp.net 域内跨越主机下载。
         9. -I /eng/docs: 限制 wget 的递归下载到指定的目录路径。这意味着只有当 URL 路径以/eng/docs 开始时，wget 才会下载。
4. 使用 WinSCP 登录 VPS，并切换到争取的目录
5. 通过 WinSCP 将已经下载后的文档（目录）复制到 Windows 本地
6. 找到目录中的 Index.html，双击查看
