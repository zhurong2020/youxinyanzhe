---
date: 2025-09-24 10:30:00
excerpt: 授人以鱼不如授人以渔。本文不会直接给你代码，而是通过一系列思考题，引导你自主探索、理解和改造策略。从突破限制到个性化设计，让我们一起踏上从使用者到创造者的进阶之路。
header:
  overlay_filter: 0.5
  overlay_image: https://7fp1fj-my.sharepoint.com/personal/zhurong_7fp1fj_onmicrosoft_com/_layouts/15/download.aspx?share=EY_ogmzVDz9GndR0KF8kPkMB0ePTv-VlMrgdW_JsTDGTvQ
  teaser: https://7fp1fj-my.sharepoint.com/personal/zhurong_7fp1fj_onmicrosoft_com/_layouts/15/download.aspx?share=EY_ogmzVDz9GndR0KF8kPkMB0ePTv-VlMrgdW_JsTDGTvQ
last_modified_at: '2025-09-24 11:00:00'
title: 开源定投策略改造指南：从使用者到创造者
---

授人以鱼不如授人以渔。本文不会直接给你代码，而是通过一系列思考题，引导你自主探索、理解和改造策略。从突破限制到个性化设计，让我们一起踏上从使用者到创造者的进阶之路。

<!-- more -->

## 🎧 音频版本

如果您更喜欢收听而非阅读，我们提供了本文的音频版本：

<div class="video-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; background: #000;">
  <iframe src='https://www.youtube.com/embed/ZPZcNALqwek?rel=0&showinfo=0&color=white&iv_load_policy=3'
          style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
          frameborder='0'
          allowfullscreen>
  </iframe>
</div>

> 💡 **提示**: 音频版本包含了文章的核心内容，配合数据图表阅读效果更佳。音频内容为AI生成，请注意辨别。

---

## 系列文章导航

本文是TQQQ定投策略系列的第3篇（完结篇）：
- 第1篇：[回测分析——从-60%回撤到盈利](https://zhurong2020.github.io/workshop/posts/2025/09/from-60-percent-drawdown-to-profit-turnaround/){:target="_blank"}
- 第2篇：[TQQQ定投深度剖析：为什么周投能赢日投？](https://zhurong2020.github.io/workshop/posts/2025/09/tqqq-weekly-vs-daily-analysis/){:target="_blank"}
- **第3篇：开源定投策略改造指南**（本文）

---

## 引言：AI时代的策略改造新方法

在前两篇文章中，我们展示了定投策略的威力。但更重要的是：**如何理解策略原理，创建适合自己的定投系统**。

> "The best way to learn is to teach a machine to do it for you."
> ——现代量化投资者

**本文的核心方法**：
- ✅ 利用AI（比如ChatGPT或者国内LLM模型）理解代码
- ✅ 在Web端（或者更专业的VS Code）中借助AI改造策略
- ✅ 通过向大语言模型（LLM）提问引导思考和改造方向
- ✅ 让AI成为你的编程助手并实现自定义策略的私人定制

**推荐阅读**：
- [智能投资指南：手把手教你用量化工具定投美股](https://zhurong2020.github.io/post/zhi-neng-tou-zi-zhi-nan-shou-ba-shou-jiao-ni-yong-liang-hua-gong-ju-ding-tou-mei-gu/){:target="_blank"}
- [打造你的第一个量化交易机器人-Moomoo平台环境搭建指南](https://zhurong2020.github.io/post/da-zao-ni-de-di-yi-ge-liang-hua-jiao-yi-ji-qi-ren-moomoo-ping-tai-huan-jing-da-jian-zhi-nan/){:target="_blank"}

## 1. 为什么选择Moomoo平台

### 1.1 Moomoo量化功能介绍

**为什么是Moomoo？**
- 📱 **自定义策略支持**：Moomoo提供完整的量化功能模块
- 💻 **代码导入能力**：可直接导入自己编写的Python策略代码
- 🆓 **免费使用**：量化功能完全免费，无需额外付费
- 🎯 **实盘执行**：策略可直接用于实盘交易，自动执行定投

**工作原理**：
1. 在Moomoo软件中打开“量化”功能
2. 选择“自定义策略”
3. 将免费版代码（或自己改造的代码）粘贴进去
4. 启动策略，即可实现自动定投等功能
5. 无需编程基础，复制粘贴即可使用

![Moomoo量化功能](https://7fp1fj-my.sharepoint.com/personal/zhurong_7fp1fj_onmicrosoft_com/_layouts/15/download.aspx?share=Eau9j8NBWBdEhYY-IfsRNsgBYKCnaXaOw6la4hxORgEIHg)

> 💡 **核心价值**：本系列分享的免费版策略基于Moomoo量化框架开发，可以直接在Moomoo（Legacy版本）中运行。

### 1.2 平台准备与框架理解

> ⚠️ **开户提醒**：
> - 据悉近期Moomoo等券商已收紧新开户要求，如有疑问请和在线客服联系。
> - 建议先确认开户资格，再下载软件并通过新手引导流程进行学习。
>
> 📚 **版本选择**：
> - 推荐使用**Moomoo Windows Legacy版本**
> - 下载时选择带有Legacy标记的版本（如Ver.15.33.19958）
> - 本系列自定义策略均依托Moomoo Legacy 版本进行开发

**理解框架结构**

打开Moomoo量化功能（完成新手引导后），点击右上角“查看量化文档”，先熟悉基础约定。如果对软件下载和操作不熟悉，可以先阅读以下博文：
[Moomoo平台环境搭建指南](https://zhurong2020.github.io/post/da-zao-ni-de-di-yi-ge-liang-hua-jiao-yi-ji-qi-ren-moomoo-ping-tai-huan-jing-da-jian-zhi-nan/){:target="_blank"}

**AI修改策略代码的入门方法（最简单）**：

*国外AI工具*：
- [Claude.ai](https://claude.ai){:target="_blank"} - Anthropic的AI助手
- [ChatGPT](https://chat.openai.com){:target="_blank"} - OpenAI的对话AI

*国内AI工具*：
- [文心一言](https://yiyan.baidu.com){:target="_blank"} - 百度，中文理解能力强
- [通义千问](https://tongyi.aliyun.com){:target="_blank"} - 阿里云，支持多种智能体
- [讯飞星火](https://xinghuo.xfyun.cn){:target="_blank"} - 科大讯飞，语音交互强
- [Kimi](https://kimi.moonshot.cn){:target="_blank"} - 长文本处理能力优秀
- [智谱清言](https://chatglm.cn){:target="_blank"} - 清华背景，数据分析能力强

使用步骤：
1. 选择任一AI工具。
2. 将免费版代码复制给AI。
3. 通过对话逐步理解代码。
 
![与Kimi对话](https://7fp1fj-my.sharepoint.com/personal/zhurong_7fp1fj_onmicrosoft_com/_layouts/15/download.aspx?share=EfqSoBTsqOlGkdVA9UccnGsBuvGHjlKzxhxocE_25kHAtA)
上图展示了与Kimi讨论量化策略的画面

**推荐的进阶方法（更专业）**：
1. 使用VS Code打开已下载的策略代码（扩展名为quant文件）
2. 在VS Code中安装AI插件（如Claude Code、ChatGPT等）
3. 在安装好的编辑器内直接询问AI（初学者可以关注后续关于VS Code的文章）

**与AI的对话示例**：
```
你：“请解释这个Moomoo策略的整体结构。”
AI：“这个策略包含三个层面：基础框架函数（initialize和handle_data）……”

你：“根据Moomoo文档，trigger_symbols()函数是做什么的？最多可以设置几个？”
提示：把文档中的trigger_symbols部分一并发给AI
AI：“这个函数定义运行标的，最多可以设置8个……”

你：“请为这段代码添加详细的中文注释。”
提示：把策略代码粘贴给AI
AI：“好的，我来为每个函数添加注释说明……”
```

![VS Code中的LLM集成](https://7fp1fj-my.sharepoint.com/personal/zhurong_7fp1fj_onmicrosoft_com/_layouts/15/download.aspx?share=ES4tg8jQHXNNgT4BqN4f7n8BrH0fJ1NSnhTuE29mUAAyBg)
当你使用VS Code时，可直接与 OpenAI Codex 和 Claude Code等多个LLM对话。

> 💎 **完整版福利**：
> 购买完整版的用户将获得：
> - 📄 《Moomoo量化策略框架具体说明》整理版
> - 📄 《Moomoo量化功能常用API函数及其用法》（46个常用函数详解）
> - 避免走弯路，节省大量查找时间
> - 在和AI的对话中，附上上述文件，AI就能给出合适的代码或建议

## 2. 为什么需要量化策略？

### 2.1 一个常见的疑问

> “就为了每天或者每周定投一次，需要自己创建自定义策略这么复杂吗？我直接手动买某个股票不就行了？”

这是许多投资者的第一反应。让我们看看手动定投vs量化定投的真实差异：

**手动定投的现实**：
- 😰 **每日纠结**：“今天涨了2%，要不要等回调？”
- 😟 **执行困难**：“忙忘了……已经3天没投了”
- 😵 **情绪干扰**：“跌了20%，太可怕了，先停停吧”
- 🤔 **决策疲劳**：“到底该投多少？要不要加仓？”

![为什么使用量化策略](https://7fp1fj-my.sharepoint.com/personal/zhurong_7fp1fj_onmicrosoft_com/_layouts/15/download.aspx?share=EVwobVuYeMZNno1-L8lkKJUBTBv-0kKhGmLYdVFd5RpHwA)

**量化策略的优势**：
- ✅ **零纠结**：策略自动判断，无需思考
- ✅ **100%执行**：只要启动，绝不缺席（完整版支持"断点续投"）
- ✅ **情绪免疫**：程序没有恐惧和贪婪
- ✅ **智能加仓**：跌得越多，买得越多
- ✅ **多策略并行**：同时运行多个策略，捕捉不同市场机会

> 🚀 **未来愿景**：
> 目前需要每天手动启动策略，但我们正在开发独立运行方案：
> - 📅 **短期目标**：优化策略参数，提升稳定性
> - 🌐 **中期目标**：开发VPS云端部署方案（需向云服务商购买VPS，月费约$5-20）
> - 🤖 **终极目标**：实现7×24小时无人值守交易机器人
> - 💡 **技术路线**：独立App + API接入 + 云端监控

### 2.2 多策略协同：机会与风险并存

特殊需要着重说明，Moomoo支持**同时运行多个策略**：

![多策略同时运行示例](https://7fp1fj-my.sharepoint.com/personal/zhurong_7fp1fj_onmicrosoft_com/_layouts/15/download.aspx?share=EaIHkjEUKGpGgor5m6PDa8cB54ucAQKj0050SpG1FRkntg)
*图：在Moomoo中同时运行网格交易（2个实例）、滚轮和期权扫描共4个策略*

**可同时运行的策略组合**：
- 📈 **多个定投策略**：TQQQ激进定投 + SPY稳健定投 + QQQ平衡定投
- 🎯 **多个网格策略**：不同标的、不同价格区间的网格
- 🔄 **多个滚轮策略**：卖不同股票的Put和Call期权
- 🎰 **混合策略**：定投打底 + 网格增强 + Wheel创收

**多策略的理论优势**：
1. **风险分散**：不同策略对应不同市场状态
2. **收入多元化**：定投赚趋势、网格赚波动、Wheel赚期权费
3. **互补性**：某个策略亏损时，其他策略可能盈利

**⚠️ 但要理性看待风险**：
- **策略冲突**：Wheel卖出Call后股价大涨，错失上涨收益
- **同向风险**：极端行情下，多个策略可能同时亏损
- **管理复杂度**：策略越多，监控和调整越困难
- **资金效率**：分散投资可能降低单一策略的收益潜力

**理性认识**：
- 多策略**不是**稳赚不赔的魔法
- 目标是**长期稳健**，而非短期暴利
- 接受某个策略在特定时期的“机会成本”
- 重点是找到适合自己风险偏好的组合

## 3. AI辅助改造：从实战到进阶

> ⚠️ **重要提醒：保护你的稳定版本**
> - Moomoo的自定义策略**修改后会自动保存并上传**，无撤销功能
> - **强烈建议**：新建测试策略或使用Git版本管理
> - **切记**：先备份，再改造！

![AI辅助设计](https://7fp1fj-my.sharepoint.com/personal/zhurong_7fp1fj_onmicrosoft_com/_layouts/15/download.aspx?share=EZScRRSVqglNr-W-R6-ALH8BPtHexWHuAfhW19B2BmOLhA)

### 3.1 选择适合你的AI工具
**Web端AI**（推荐入门）：
- 国外：Claude、ChatGPT
- 国内：文心一言、通义千问、Kimi等

**改造流程**：
1. 将策略代码复制给AI。
2. 清晰说明你的改造需求。
3. 把AI生成的代码粘贴到Moomoo量化模块中测试。

### 3.2 AI不只是改代码

**AI可以帮你**：
- 📊 理解策略逻辑
- 🛡️ 发现风险漏洞
- 📈 分析回测结果
- 💡 提供创新思路

**示例对话**：
```
你：“我想改成每天投资，突破10股限制。”
AI：“修改interval_days和MAX_SHARES参数……”
```

> 🎯 **核心**：让AI成为你的策略顾问，而不只是代码生成器。

![AI顾问](https://7fp1fj-my.sharepoint.com/personal/zhurong_7fp1fj_onmicrosoft_com/_layouts/15/download.aspx?share=EY-W6rRz_xFHsTL1SsvOYdUBKhbYswJACcWK9Q_Fh5sjug)

## 4. 回测验证：改造后必做的事

### 4.1 简单有效的验证步骤

1. **在Moomoo中回测原版策略**，记录收益和回撤
2. **回测你的改造版本**，对比关键指标
3. **至少测试2个时间段**：分别覆盖一个牛市和一个熊市区间
4. **小资金实盘验证**：用$1,000-$2,000测试1个月

### 4.2 持续优化循环

**迭代改进流程**：
 1. 修改策略 → 2. 回测验证 → 3. AI分析结果 → 4. 调整参数 → 5. 重复迭代。

## 5. 进阶技巧：本地AI参数优化

> 💡 **突破性思路**：在本地利用AI进行大规模参数优化

**本地AI能做什么**：
- 📊 **历史数据回测**：使用Python/Excel进行本地模拟
- 🎯 **参数优化**：AI帮你找到最优参数组合
- 📈 **策略验证**：先本地测试，再到Moomoo实盘验证
- 🔬 **风险分析**：模拟极端行情下的策略表现

![AI参数优化](https://7fp1fj-my.sharepoint.com/personal/zhurong_7fp1fj_onmicrosoft_com/_layouts/15/download.aspx?share=EXRY39fIlQBKiH16erO-HuUBzsiMAlfjpdIjZQ_2mPQXdg)

**本地模型选择**：
- 使用云端AI：Claude、ChatGPT等（需付费）
- 使用本地模型：Ollama等开源方案（免费，但需一定硬件支持）
- 后续我们将专门介绍如何安装使用本地模型，避免高额LLM费用

**工作流程**：
1. 本地AI分析历史数据
2. 生成优化后的策略代码
3. 在Moomoo中验证效果

## 6. 社区交流

### 6.1 加入学习社区

- 🌟 **爱好者交流群**（免费版用户）
- 💎 **VIP专属群**（完整版用户）
- 📱 评论区留言即可加群

### 6.2 群内约定

![群组学习](https://7fp1fj-my.sharepoint.com/personal/zhurong_7fp1fj_onmicrosoft_com/_layouts/15/download.aspx?share=EddI4V5JkndLj3xHPNMrOvgBhVr9NjqPdUJuVLihv3Eq2A)

**❌ 请避免**：
- 伸手党：“代码发我”“怎么改？”
- 急躁者：“在吗？快回！”

**✅ 提倡**：
- 先自行探索，再讨论
- 分享你的尝试和发现

> 详细社区规范将在群内置顶公告中说明。

## 7. 学习路径目标

### 第1-2周：理解基础
- 目标：能让AI解释策略逻辑
- 成果：完成第一个简单改造

### 第3-4周：实践改造
- 目标：独立完成参数优化
- 成果：建立自己的策略版本

### 第2个月：创新探索
- 目标：开发独特功能
- 成果：成为策略创造者
  
![从复制到创造](https://7fp1fj-my.sharepoint.com/personal/zhurong_7fp1fj_onmicrosoft_com/_layouts/15/download.aspx?share=EY_ogmzVDz9GndR0KF8kPkMB0ePTv-VlMrgdW_JsTDGTvQ)

## 8. 资源获取

### 策略版本说明

**免费版策略**：
- 📦 完整功能的3层回撤系统
- 🆓 源码开放，自由改造
- 💡 适合学习和研究
- 🎯 满足90%投资需求

**完整版策略**（¥299）：
- 📖 7层深度加仓系统
- 📊 5年历史回测数据
- 📄 Moomoo文档整理版
- 👥 VIP专属交流群
- 🎯 一对一指导服务
- ♻️ 一年内免费更新

> **获取方式**：
> - 免费版：评论区留言"策略获取"
> - 完整版：评论区留言或私信作者

### 学习资源

**你真正需要的**：
- ✅ 一个AI工具（Claude或ChatGPT）
- ✅ Moomoo软件（Legacy版本）
- ✅ 探索的好奇心

![想法转化为成功](https://7fp1fj-my.sharepoint.com/personal/zhurong_7fp1fj_onmicrosoft_com/_layouts/15/download.aspx?share=EbktZxJrIwdJnfcQPbP1YqoBTmf9rKByUwe3H4P9nkBaEQ)

> 💡 **记住**：在AI时代，普通人不需要成为程序员。让AI处理技术细节，你专注于策略思路！

## 9. 写在最后

### AI时代的学习新范式

> "In the age of AI, the ability to ask the right questions is more valuable than knowing all the answers."

这个系列的核心价值：
- **学会与AI协作**，而非单打独斗
- **掌握提问技巧**，让AI成为助手
- **理解核心逻辑**，AI负责实现细节
- **快速迭代验证**，加速学习进程

### 重要提醒

> 🔔 **关键事项**：
> - **开户要求**：需要国外身份证明
> - **版本选择**：使用Legacy版本
> - **工具准备**：Web端AI即可（进阶用户可用VS Code）
> - **策略运行**：每天手动启动（完整版支持断点续投）

![从初学者到创造者](https://7fp1fj-my.sharepoint.com/personal/zhurong_7fp1fj_onmicrosoft_com/_layouts/15/download.aspx?share=EaS2943HADxArOCX4pxA62wBUsxhLNH3igdaun-8S8vKMw)

### 立即行动：你的第一个AI辅助改造

**10分钟快速开始（入门版）**：

1. **打开浏览器**，访问AI工具。
   - 国外：Claude.ai 或 ChatGPT.com
   - 国内：文心一言、通义千问、Kimi等
2. **复制免费版代码**，粘贴到对话框。
3. **询问AI**：“请解释这个策略的工作原理。”
4. **提出需求**：“我想改成每天定投，请修改代码。”
5. **复制修改后的代码**，粘贴至Moomoo量化功能中测试。

**进阶版流程**：
- 使用专业代码编辑器配合AI插件
- 详细教程将在后续文章中介绍

**第一个成功改造后**：
- 截图分享到群里
- 记录你的改造经验
- 帮助下一位新手

**记住**：AI是你的编程助手，你是策略的设计师！

![AI巅峰](https://7fp1fj-my.sharepoint.com/personal/zhurong_7fp1fj_onmicrosoft_com/_layouts/15/download.aspx?share=EV0AdfPgLk9Oo3fpmsqBlZwBLt9x8tzuObiCmFVwZPetxg)

---

## 系列总结

通过这个系列的三篇文章，我们完成了：
1. **数据验证**：-60%回撤后仍能盈利的真实案例
2. **原理剖析**：周投vs日投的数学逻辑
3. **能力培养**：从使用者到创造者的路径

**最重要的收获**：
- 真正的价值不在策略本身
- 而在于独立思考和解决问题的能力
- 这才是长期可持续的财富

如果这个系列对你有帮助：
- 💬 分享你的学习心得
- ⭐ 推荐给需要的朋友
- 🎯 加入社区共同成长
- ☕ 打赏支持作者创作
- 💎 购买完整版获得更多价值

让我们在量化投资的道路上携手前行！

---

**免责声明**：
- 本文仅供教育参考，不构成投资建议
- 策略改造风险自负
- 投资有风险，入市需谨慎

**作者简介**：前银行从业者，现专注于量化投资研究。坚信教育和分享的力量，致力于帮助普通投资者掌握科学的投资方法。

**#量化投资 #教练式学习 #开源精神 #社区文化 #TQQQ定投**


{% assign investment_tags = 'QDII基金,指数投资,标普500,纳斯达克100,定投策略,基金投资,股票投资,投资理财,量化交易,投资策略,风险管理,资产配置,投资心理,美股投资,ETF投资' | split: ',' %}
{% assign show_investment_disclaimer = false %}
{% for tag in page.tags %}
  {% if investment_tags contains tag %}
    {% assign show_investment_disclaimer = true %}
    {% break %}
  {% endif %}
{% endfor %}

{% if show_investment_disclaimer %}
---

**💭 学习分享声明**：这里记录的是我在投资理财学习路上的个人思考和实践心得。正如《金钱心理学》所言：“每个人的情况不同”，投资决策需要结合您的具体情况、风险承受能力和投资目标。本文仅供学习交流，不构成投资建议，请保持独立思考，持续学习。

{% endif %}

如果你觉得我的文章对你有帮助，可以[请我喝咖啡](https://www.buymeacoffee.com/zhurong052Q)

<a href="https://www.buymeacoffee.com/zhurong052Q" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

> 💬 **发表评论**：您需要有一个 GitHub 账号来发表评论。