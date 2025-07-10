---
layout: single
title: "云端生活入门：用ChatGPT-4开启个性化在线学习之旅"
date: 2024-03-04 19:55:00 +0000
excerpt: "Mr. Ranedeer AI导师项目基于GPT-4为用户提供定制化的个性化学习体验。"
header:
  overlay_image: assets/images/202403/personalizedaitutor.png
  overlay_filter: 0.5
  teaser: assets/images/202403/personalizedaitutor.png
---

### 引言

在人工智能飞速发展的今天，AI 已成为改变我们日常生活和工作方式的关键力量。ChatGPT 作为普通人首次接触的 AI 产品，自从 2022 年 11 月 30 日 OpenAI 公司首次向公众推出 GPT-3.5 起，到本文发稿时最新发布的多模态 GPT，我们可谓见证了 AI 技术的巨大进步，AI 也逐步迈向和我们有关的各个领域。

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWIAwBAAAAAImgLob5D5bD5Ak?width=660" />

ChatGPT，全称 Chat Generative Pre-trained Transformer，是一个人工智能聊天机器人程序。对普通人而言，ChatGPT 可以帮助编写学术论文、创意写作、内容创作、商业写作，甚至进行学术编辑。本系列文章将探讨如何利用这些先进技术满足个人品牌建设或家庭日常 IT 需求，本篇将探讨 AI 在个性化在线教育方面的应用

今天，我们将深入了解 ChatGPT-4 在个性化在线教育中的应用，并探索开源项目“Mr. Ranedeer AI Tutor”的用途。虽然直接使用该项目需要 ChatGPT Plus 用户权限，但通过研究作者提供的开源代码和目前的实测效果，普通用户也能为更好利用 ChatGPT 的能力打下基础。

### ChatGPT-4 和个性化教育

ChatGPT-4 为教育领域带来了强大的支持，其更好的理解能力、更精确的信息处理和更高效的交互方式，为个性化教育提供了新的可能。在最新版本中，用户能够自行设计 GPT 模型，根据特定需求定制学习体验。

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWJAwBAAAAAFKa2f_KuKNvGyc?width=660" />

### 调教 ChatGPT 以获取更好的结果

虽然 ChatGPT-4 极其强大，但它的表现在很大程度上依赖于用户如何提问。通过提出清晰、具体的问题，可以有效引导 AI 提供更准确、更相关的答案。英文读者可以参考 GitHub 上的[awesome-chatgpt-prompts](https://github.com/f/awesome-chatgpt-prompts)项目。中文读者则可以查看[ChatGPT 中文调教指南](https://github.com/PlexPt/awesome-chatgpt-prompts-zh)了解更多。

### Mr.-Ranedeer-AI-Tutor 项目介绍

“Mr. Ranedeer AI Tutor”利用 ChatGPT-4 的深度学习和自然语言处理能力，极大地改善和个性化了教育过程。用户可以在 Mr.-Ranedeer-AI-Tutor 项目页面查看详细说明。如果你是 ChatGPT Plus 用户，可以直接体验 Mr. Ranedeer 的功能，以下主要使用图文方式介绍这个项目。

#### 入口

本项目的开源网址为[Mr.-Ranedeer-AI-Tutor](https://github.com/JushBJJ/Mr.-Ranedeer-AI-Tutor/releases)，你可以上去查看作者的说明和最新动态。
如果你已经是 ChatGPT Plus（付费）用户，你可以点击这个链接[直接打开 ChatGPT](https://chat.openai.com/g/g-9PKhaweyb-mr-ranedeer)。

打开后，画面是这样的：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWCAwBAAAAAHbTfflQSBmwTsE?width=660" />

注意，你首先需要点击画面下方的"/config"进行[适当的配置](https://chat.openai.com/g/g-0XxT0SGIS-mr-ranedeer-config-wizard)，进入后继续点击下方的配置向导：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBW_wsBAAAAAON29ov0WC-JtAk?width=660"/>

在配置向导页面，主要是对学习的交流语言，学习深度，学习风格，沟通风格，语气风格，推理框架进行初始化设置：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWAAwBAAAAAAVFH9Y4e9lEk6c?width=660" />

最后将系统生成的 prompt 复制下来。比如这样的：“/config Language: 中文, Depth: 大学本科, Learning Style: 亲身实践, Communication Style: 正式的, Tone Style: 信息性的, Reasoning Framework: 类比推理”。

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWCgwBAAAAALJGldtOmtfeX44?width=660" />

回到 Mr.Ranedeer，将上述 prompt 黏贴并回车，系统会确认上述配置，然后就可以开始和机器人对话，通过定义具体的学习内容，开始学习了。

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWAgwBAAAAACa72EXRRFLF_34?width=660" />

你可以设定一个主题，让机器人制定一个学习计划，比如“让我可以在一星期内完成 PCEP 的考试准备”，机器人就会给出计划如下：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWBQwBAAAAAIEnKT3nyHXrnWY?width=660" />

如果你认可计划准备开始学习，可以输入指令"/start"：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWBgwBAAAAAMIayl8nxNWVxls?width=660" />

如果希望对某部分内容具体讲解，可以直接输入中文告诉机器人：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWBwwBAAAAAGTQUVeoPDgl4H4?width=660" />

如果想要继续后续课程，可以输入指令"/continue"，即便输错机器人也能识别：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWBAwBAAAAALBtaJp--nloRko?width=660" />

如果涉及到代码输入，你可以先在下方直接输入（或在编辑器中完成代码编辑），然后机器人会帮助你检查，有你还有其它问题，可以直接提问：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWCwwBAAAAAFbSMXOEMogpr7Y?width=660" />

你还可以要求它出一些仿真考题，来检验你的掌握程度：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWCQwBAAAAAJKJzlYPCNVsZn8?width=660" />

你可以按照考题回答后，让机器人分析并点评：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBWDAwBAAAAAAJtjiBC2LFSu6s?width=660" />

你还可以使用“还有什么”的问题形式，询问机器人，让它给你更多帮助：

<img src="https://1drv.ms/i/c/5644dab129afda10/UQQQ2q8psdpEIIBW_gsBAAAAAEm8lGVpdkA2y7M?width=660" />

未来展望
AI 在教育领域的应用正变得越来越重要。随着技术的不断进步，我们可以预见一个更加高效、互动和个性化的教育未来。项目如“Mr. Ranedeer AI Tutor”仅是众多创新应用中的一个，展示了 AI 技术在教育领域的巨大潜力。

<img src="https://1drv.ms/i/c/5644dab129afda10/IQQQ2q8psdpEIIBWHgwBAAAAAQHXxcRxlQTxwzo1Y2ghTLk?width=660" />

### 总结

“Mr. Ranedeer AI Tutor”和 ChatGPT-4 的结合为我们揭开了未来教育方式的新视野。随着技术的不断发展，我们可以期待更多创新性的学习工具的出现，进一步推动个性化教育的发展。
