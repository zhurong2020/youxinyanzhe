---
date: 2024-03-04 19:55:00 +0000
excerpt: Mr. Ranedeer AI导师项目基于GPT-4为用户提供定制化的个性化学习体验。
header:
  overlay_filter: 0.5
  overlay_image: assets/images/202403/personalizedaitutor.png
  teaser: assets/images/202403/personalizedaitutor.png
layout: single
title: 云端生活入门：用ChatGPT-4开启个性化在线学习之旅
---

### 引言

在人工智能技术飞速发展的今天，AI 正深刻地改变着我们的日常生活和工作方式。ChatGPT 作为大众首次接触的 AI 产品，自 2022 年 11 月 30 日 OpenAI 首次发布 GPT-3.5 以来，直至最新的多模态 GPT，我们共同见证了 AI 技术的巨大进步，它正逐步渗透到与我们息息相关的各个领域。

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWIAwBAAAAAImgLob5D5bD5Ak?width=660" />

ChatGPT (Chat Generative Pre-trained Transformer) 是一款人工智能聊天机器人程序。对普通用户而言，它可以辅助编写学术论文、进行创意写作、辅助内容创作、进行商业写作，甚至提供学术编辑服务。本系列文章将探讨如何利用这些先进技术来满足个人品牌建设或家庭日常 IT 需求。本文将重点探讨 AI 在个性化在线教育领域的应用。

本文将深入了解 ChatGPT-4 在个性化在线教育中的应用，并探索开源项目“Mr. Ranedeer AI Tutor”的用途。虽然直接使用该项目需要 ChatGPT Plus 用户权限，但通过研究作者提供的开源代码及其实测效果，普通用户也能为更好地利用 ChatGPT 的强大功能打下基础。

### ChatGPT-4 与个性化教育

ChatGPT-4 为教育领域带来了强大的助力。它具备更强的理解能力、更精确的信息处理能力以及更高效的交互方式，从而为个性化教育提供了新的可能性。在最新版本中，用户可以自定义 GPT 模型，根据自身需求定制学习体验。

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWJAwBAAAAAFKa2f_KuKNvGyc?width=660" />

### 如何“调教”ChatGPT 以获得更佳结果

尽管 ChatGPT-4 功能强大，但其表现很大程度上取决于用户提问的方式。通过提出清晰、具体的问题，可以有效地引导 AI 提供更准确、更相关的答案。英文读者可以参考 GitHub 上的 [awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts) 项目。中文读者则可以查看 [ChatGPT 中文调教指南](https://github.com/PlexPt/awesome-chatgpt-prompts-zh) 了解更多技巧。

### “Mr. Ranedeer AI Tutor”项目介绍

“Mr. Ranedeer AI Tutor” 利用 ChatGPT-4 的深度学习和自然语言处理能力，显著改善并个性化教育过程。您可以在 Mr.-Ranedeer-AI-Tutor 项目页面查看详细说明。如果您是 ChatGPT Plus 用户，可以直接体验 Mr. Ranedeer 的功能。以下将主要通过图文方式介绍这个项目。

#### 入口

该项目的开源网址为 [Mr.-Ranedeer-AI-Tutor](https://github.com/JushBJJ/Mr.-Ranedeer-AI-Tutor/releases)，您可以在该页面查看作者的说明和最新动态。
如果您是 ChatGPT Plus (付费) 用户，可以点击此链接 [直接打开 ChatGPT](https://chat.openai.com/g/g-9PKhaweyb-mr-ranedeer)。

打开后，界面如下：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWCAwBAAAAAHbTfflQSBmwTsE?width=660" />

请注意，首先需要点击界面下方的“/config”进行[适当的配置](https://chat.openai.com/g/g-0XxT0SGIS-mr-ranedeer-config-wizard)，进入后继续点击配置向导：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBW_wsBAAAAAON29ov0WC-JtAk?width=660"/>

在配置向导页面，主要进行学习交流语言、学习深度、学习风格、沟通风格、语气风格、推理框架等初始化设置：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWAAwBAAAAAAVFH9Y4e9lEk6c?width=660" />

最后将系统生成的 prompt 复制下来。例如：“/config Language: 中文, Depth: 大学本科, Learning Style: 亲身实践, Communication Style: 正式的, Tone Style: 信息性的, Reasoning Framework: 类比推理”。

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWCgwBAAAAALJGldtOmtfeX44?width=660" />

回到 Mr.Ranedeer，将上述 prompt 粘贴并回车，系统会确认上述配置，然后您就可以开始和机器人对话，通过定义具体的学习内容，开始学习。

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWAgwBAAAAACa72EXRRFLF_34?width=660" />

您可以设定一个主题，让机器人制定学习计划，例如 “让我可以在一星期内完成 PCEP 的考试准备”，机器人会给出如下计划：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWBQwBAAAAAIEnKT3nyHXrnWY?width=660" />

如果您认可计划并准备开始学习，可以输入指令 “/start”：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWBgwBAAAAAMIayl8nxNWVxls?width=660" />

如果希望对某部分内容进行具体讲解，可以直接用中文告诉机器人：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWBwwBAAAAAGTQUVeoPDgl4H4?width=660" />

如果想要继续后续课程，可以输入指令 “/continue”，即使输错机器人也能识别：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWBAwBAAAAALBtaJp--nloRko?width=660" />

如果涉及到代码输入，您可以先在下方直接输入（或在编辑器中完成代码编辑），然后机器人会帮助您检查。如果您还有其他问题，可以直接提问：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWCwwBAAAAAFbSMXOEMogpr7Y?width=660" />

您还可以要求它提供一些模拟考题，以检验您的掌握程度：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWCQwBAAAAAJKJzlYPCNVsZn8?width=660" />

在您按照考题回答后，可以让机器人分析并进行点评：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWDAwBAAAAAAJtjiBC2LFSu6s?width=660" />

您还可以使用“还有什么”这种提问方式，询问机器人，让它为您提供更多帮助：

<img src="https://1drv.ms/i/c/5644dab129afda10/IQQQ2q8psdpEIIBWHgwBAAAAAQHXxcRxlQTxwzo1Y2ghTLk?width=660" />

### 未来展望

AI 在教育领域的应用正日趋重要。 随着技术的不断进步，我们可以预见一个更加高效、互动和个性化的教育未来。“Mr. Ranedeer AI Tutor”等项目仅仅是众多创新应用中的一个缩影，展示了 AI 技术在教育领域所蕴含的巨大潜力。

<img src="https://1drv.ms/i/c/5644dab129afda10/IQQQ2q8psdpEIIBWHgwBAAAAAQHXxcRxlQTxwzo1Y2ghTLk?width=660" />

### 总结

“Mr. Ranedeer AI Tutor” 与 ChatGPT-4 的结合，为我们展现了未来教育方式的新愿景。 伴随着技术的持续发展，我们有理由期待更多创新性学习工具的涌现，从而进一步推动个性化教育的发展进程。