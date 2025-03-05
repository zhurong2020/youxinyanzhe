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
title: "聊天机器人小秘诀：Prompt让AI更懂你"
date: 2024-03-06 19:55:48 +0000
categories: [技术实践, AI&开源, 人工智能]
tags: [chatgpt, ai, prompt, llm]
pin: false
image:
  # 1200px*630px，860px*780px
  path: "/assets/img/202403/prompt-engineering1200.png"
  lqip: "/assets/img/202403/prompt-engineering860.png"
  alt: "掌握Prompt才能让AI更懂你"
  # 其它所有的图片均需要增加alt描述
# 下面是WordPress插件Git it Write的字段
post_status: publish
# post_status: draft
post_excerpt: 掌握Prompt才能让AI更懂你
featured_image: /assets/img/202403/prompt-engineering1200.png
taxonomy:
  category:
    - 技术实践
    - AI&开源
    - 人工智能
  post_tag:
    - chatgpt
    - ai
    - prompt
    - llm
# custom_fields:
# field1: value 1
# field2: value 2
comment_status: open
stick_post: no
---

嘿，亲爱的朋友们，欢迎来到我们这个小小的科技角落！你是否曾幻想过，拥有一位无所不能的 AI 好友？它可以帮你解决难题，陪伴你度过漫漫长夜，甚至成为你创意的灵感缪斯。如今，随着人工智能技术的飞速发展，这个梦想不再遥远。OpenAI 的 ChatGPT，Google 的 Gemini 等大型语言模型 (LLM) 已经拥有了强大的学习和理解能力，它们能够完成各种复杂的任务，甚至创作出令人惊叹的艺术作品。

但是，如何才能让这些 AI 真正理解你的心声，成为你的知己呢？答案就是需要精准的Prompt（指令或者提示词，以下均使用英文）。Prompt 就是你给 AI 的指令。它可以是一句话，一段文字，也可以是一个代码片段。通过精准的 Prompt，你可以告诉 AI 你想要它做什么。

Prompt 是人与 AI 交流的桥梁。通过精心设计的 Prompt，你可以让 LLM 发挥出无限的潜力。然而，仅仅会使用 Prompt 还不够。要想真正驾驭 LLM，你需要掌握 Prompt Engineering的技巧。就是通过设计高效精准的 Prompt，引导 LLM 完成你想要的任务，Prompt Engineering 是一门新兴的技术，正在为 LLM 的应用打开无限可能。

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169445&authkey=%21AFiOKokgrzGsNxQ&width=660" alt="Prompt Engingeering" width="660" height="auto" />

### AI 的耳朵：

让我给你讲个小故事。想象一下，你刚搬到一个新城市，邻居送来一盆植物作为欢迎礼物。可是，你对植物一窍不通！于是，你决定求助于 AI。你会怎么说呢？如果你只是说：这盆植物怎么了？可能 AI 会一头雾水，不知道怎么回复你。但如果你说：亲爱的小助手，这是我邻居送的仙人掌，我该怎么照顾它？这样问问题，AI 才更有可能给出有用的回答。这就是 Prompt 的魔力，它就像是 AI 的耳朵，只有对准AI的耳朵好好说话，AI 才能理解你的需求和具体情境。

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169449&authkey=%21AN4a37FAMNzX4Dc&width=660"  alt="robot's ear" width="660" height="auto" />

### 点拨秘籍：

现在，让我们一起探索如何变成 AI 交流的小能手吧！
#### 身份表明
首先，我们向AI表明自己的身份，你可能是一个办公室职员，那么你就需要告诉AI具体的岗位，这样AI就能像朋友一样了解你，也容易帮助你。

#### 背景信息
其次，一定要提供完成任务的背景信息。就像你告诉邻居你虽然不懂植物，但希望在自家阳台上进行种植，这其实也是背景信息，

#### 任务要求
接下来，需要简洁明了地表明自己的任务，任务具体是需要完成什么，如果是生成文本，需要按什么格式要求，字数要求等等。

#### 适度调味
最后，就像我们在说话时会加入自己的个性一样，适当地给 Prompt 加点“调味品”会让交流更加有趣。你可以告诉AI，你是一个喜欢幽默的人，或者你喜欢用比喻来表达自己的想法。

其实，以上方法，已经初步具备了 Prompt Engineering的技巧，通过设计高效的 Prompt，我们可以更好地引导AI完成你想要的任务。在 2023 年，Prompt Engineering 已经成为了一项能改变游戏规则的技能，随着 LLM 的不断发展，这项技能的重要性将越来越凸显。

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169444&authkey=%21AGLGExYmIa7CY4s&width=660"  alt="game-changing skill" width="660" height="auto" />

带着这份小秘籍，我相信你很快就能和 AI 聊得热火朝天啦！继续往下看，我们还有更多有趣的小技巧等着你！

### 小绊脚石：

走在与 AI 交流的道路上，我们难免会遇到一些小绊脚石。
有时候，我们以为我们的指示清晰明了，却得到了一些让人摸不着头脑的回答。比如，如果你问 AI：“你能告诉我关于那个东西的信息吗？”AI 可能会回答：“对不起，我不确定你指的是哪个‘东西’。”，或者你告诉它“请帮我写一篇年终总结”，AI大概率也不会有很大帮助，这就是典型的太模糊的 Prompt。
另一种情况是，我们可能给出了太多细节，让 AI 混淆了重点，就像是在说：“在下雨的星期二，我穿着蓝色衬衫去超市，突然想知道番茄的营养价值。”AI 可能会回答：“对不起，我不懂你的问题。”所以，找到合适的平衡，避免模糊和过度细化，是与 AI 愉快对话的关键。

### 成功故事：

记得那个新城市的小故事吗？让我来给你示范应该如何向AI提问：
#### 案例一
亲爱的小助手，我需要为一款新智能手机撰写产品描述。这款手机具有以下功能：高分辨率显示屏、强大的处理器、长续航能力、出色的拍照功能等。请帮我生成一个产品描述，突出产品的核心卖点，并吸引用户购买。我希望产品描述简洁明了，语言要生动有趣。

#### 案例二
亲爱的小助手，我需要编写一段代码来实现冒泡排序算法。请帮我完成以下任务：
1.定义一个冒泡排序函数；2.在函数中，将数组中的元素进行比较，并进行交换，直到所有元素按从小到大排序；3.测试函数的正确性。

#### 案例三
亲爱的小助手，我需要一个个性化的周健身计划，请考虑我目前的具体情况，男，30岁，身高175cm，体重140斤，健身水平初级，有轻微腰椎间盘突出（L4），每周最多锻炼4天，锻炼目的希望能增肌，小区有健身房，配备了基本运动器材，还可以结合室外跑、游泳项目。

你也可以试验一下，看看和AI对话时，明确和具体的 Prompt 所带来的魔力！

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169437&authkey=%21AC-HiXa-6xNwuxI&width=660"  alt="the art of prompt" width="660" height="auto" />

### 与 AI 共舞：

与 AI 的交流就像是一场舞蹈，需要双方的默契和适时的引导。记得，AI 是你的舞伴，而不是对手。如果你发现 AI 没有按照你预期的方式回应，不妨尝试改变你的 Prompt，或者提供更多的背景信息。有时候，即使是轻微的调整，也能带来截然不同的结果。
比如，如果你对 AI 提出的建议不满意，可以尝试说：“这个建议很有趣，但我想要一些更具创意的想法。”，“还有吗？”，“这种方法的最佳实践是什么”，“如果我想要这样，应该向你提供什么材料？”，这样的迭代式对话，就像是在舞池中尝试不同的舞步，最终你们会找到那个完美的节奏。
记住，与 AI 的交流是一个不断学习和适应的过程，享受这个过程，让你的 AI 交流更加流畅和高效。

### 番外篇：小窍门大汇总

我们已经和AI一起跳过了不少舞步，现在是时候把这些小技巧收藏起来了。为了让你的 AI 对话旅程更加顺畅，这里有一份小窍门大汇总，让你随时查阅：

- 表明身份：让AI清楚你的身份，帮助AI更好地理解你的想法。
- 背景信息：提供这项任务的背景信息，让AI理解任务的逻辑。
- 明确目标：在构建 prompt 之前，先清楚地知道你想从 AI 得到什么样的信息或帮助。
- 简洁有力：尽量使你的 prompt 简洁而不失信息量，避免不必要的废话。
- 适度调味：不妨加入一些个性化的元素，让对话更有趣味。
  还记得我们谈到的关键词和迭代式对话吗？它们是舞池中的华尔兹和探戈，能让你与 AI 的对话更加和谐。

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169446&authkey=%21AAF_fr_6ihPrIIQ&width=660"  alt="the future of prompt" width="660" height="auto" />

### 你问我答：互动环节

在我们的科普旅程接近尾声时，或许你还有一些疑问或者好奇心未被满足。不用担心，这里有一个“你问我答”的环节，就像一个友好的问答会：

Q：如果我不知道从何问起，我该怎么办？
A：从简单的问题开始，比如“你能做什么？”或者“你知道关于 XX 的有趣事实吗？”这样可以帮助你逐渐了解 AI 的能力范围。

Q：我尝试了一个 prompt，但没有得到我想要的回答，我该怎么办？
A：不要灰心，尝试调整你的 prompt，增加一些细节，或者换一种提问方式。记得，与 AI 的交流就像是一场舞蹈，需要不断地调整和尝试。

Q：AI 能理解幽默和比喻吗？
A：是的，现代的 AI 系统，特别是像 ChatGPT 这样的高级模型，能够理解并生成幽默和比喻。但它们的理解能力仍然有限，有时可能需要你的提示来把握语境。

Q: 还有什么方法让 AI 回答得更精准？
A: 当然有的，还有更高阶的 Prompt 指令，也可以让 AI 进行角色扮演，或者提前设置自定义指令，比如在 ChatGPT 提前设置有关自己的信息并要求用何种方式进行回应。当你开始一个新的对话时，ChatGPT 就能根据你提前设置的指令进行回答了。

Q: 还有吗？
A: 关于 AI，可以说的还有很多，我在文末还提供了一些文章可以给你参考，有官方的文档，也有 Github 上 100K+的项目，当然还可以比较不同的 AI，比如在有些软件中进行 AI 对话引擎的切换。

希望这些回答能帮助你更好地与 AI 聊天。记得，每次对话都是一次学习和探索的机会。享受与 AI 的舞蹈，让技术为你的生活增添更多色彩！

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169434&authkey=%21ALjmtJKLp1mbgPc&width=612&height=323"  alt="dance with robot" width="612" height="323" />

如果你渴望深入了解，或者想要探索更多的 prompt 创意，这里有一些宝贵的资源推荐给你：

- [GitHub项目 -Awesome ChatGPT Prompts](https://github.com/f/awesome-chatgpt-prompts)
- [OpenAI 官方的 Prompt Engineering 指南](https://platform.openai.com/docs/guides/prompt-engineering)
- [中文版的提示工程指南](https://www.promptingguide.ai/zh)
- [ChatGPT 中文调教指南](https://github.com/PlexPt/awesome-chatgpt-prompts-zh)

好了，今天就到这里，如果您也有实用的技巧，欢迎在评论区分享您的经验。

另外欢迎您加入我们的“云端生活交流群”，您可以添加以下微信，让志同道合的朋友们，可以在知识探索的路上互相帮助，互相成就。如果您希望我下一篇写什么内容，也欢迎在评论区留言。

<img src="https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169811&authkey=%21ABRiiNUJymdww3o&height=256" alt="monty二维码" width="auto" height="256" />

如果你觉得我的文章对你有帮助，可以[请我喝咖啡](https://www.buymeacoffee.com/zhurong052Q)

<img src="https://sat02pap005files.storage.live.com/y4m1bQmI2HjlYf8y0-p5ILDLqV4klxYZjjhDZYzn60HpwCTOEot0HfRqsp5RrXVXKechgLZmehuN6udGTqYc3Qudqo73s1tqUAIJul__ZG1-YBMQGkzr8FC9gRj_ywS7n9a_Vpp87CQm1enxUNgrZSKE5wIDvhjixZA3QdOTcwjGnYZRk62QXEWOOAg83tq7Mu1?width=256&height=200&cropmode=none" alt="请我喝咖啡" width="256" height="200" />

> 💬 **发表评论**: 本博客的评论功能由 Gitalk 提供，您需要有一个 GitHub 账号来发表评论。如果您还没有账号，请访问 [GitHub](https://github.com/join) 免费注册。注册后，您不仅可以在这里参与讨论，还可以在 GitHub 上发现无数精彩项目和技术交流的机会！