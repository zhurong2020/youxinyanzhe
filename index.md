---
layout: splash
title: "有心言者"
header:
  overlay_color: "#000"
  overlay_filter: "0.5"
  overlay_image: https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/dfa9d2a3-3054-46d8-241e-717209aaf600/public?format=auto&width=1920&quality=85
  actions:
    - label: "浏览全部文章"
      url: "/posts/"
excerpt: "让普通人受益于科技、全球视野与终身学习的知识分享平台"
intro: 
  - excerpt: '探索认知升级、技术赋能、全球视野与投资理财，助力个人成长与财富积累的完整知识体系。'
feature_row:
  - image_path: https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/25b4d7c3-4f8e-4b62-5b9e-9fe1a6c10200/public?format=auto&width=600&quality=75
    alt: "🧠 认知升级系列"
    title: "🧠 认知升级系列"
    excerpt: "思维模型、学习方法、认知心理学与决策科学。帮你建立科学的思维框架，避免认知偏差，提升学习效率与人生决策质量。"
    url: "/categories/认知升级/"
    btn_label: "开始升级"
    btn_class: "btn--primary"
  - image_path: https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c553d355-9a2e-4753-4a47-9009b7cab200/public?format=auto&width=600&quality=75
    alt: "🛠️ 技术赋能系列"
    title: "🛠️ 技术赋能系列"
    excerpt: "实用工具推荐、技术教程与自动化方案。让科技真正为普通人赋能，提升工作效率，享受数字化生活的便利与乐趣。"
    url: "/categories/技术赋能/"
    btn_label: "获得赋能"
    btn_class: "btn--primary"
feature_row2:
  - image_path: https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/dfa9d2a3-3054-46d8-241e-717209aaf600/public?format=auto&width=600&quality=75
    alt: "🌍 全球视野系列"
    title: "🌍 全球视野系列"
    excerpt: "国际趋势洞察、文化差异观察与跨文化思维训练。开拓全球化视野，理解世界发展脉络，培养国际化思维能力。"
    url: "/categories/全球视野/"
    btn_label: "拓展视野"
    btn_class: "btn--primary"
  - image_path: https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/e35cd10a-83b4-4939-ecb6-35edeb1a2d00/public?format=auto&width=600&quality=75
    alt: "💰 投资理财系列"
    title: "💰 投资理财系列"
    excerpt: "投资思维培养、理财方法实践与财务自由规划。结合量化分析与价值投资理念，构建科学的个人财富管理体系。"
    url: "/categories/投资理财/"
    btn_label: "财富增长"
    btn_class: "btn--primary"
---

{% include feature_row id="intro" type="center" %}

<!-- 样式已移至custom.css文件 -->

{% include feature_row %}

{% include feature_row id="feature_row2" %}

<div class="latest-posts">
  <h2 class="archive__subtitle">最新文章</h2>
  <div class="grid__wrapper">
    {% for post in site.posts limit:6 %}
      {% include archive-single.html type="grid" %}
    {% endfor %}
  </div>
  {% if site.posts.size > 6 %}
  <div class="view-more-btn">
    <a href="{{ site.baseurl }}/posts/" class="btn btn--primary">查看更多文章</a>
  </div>
  {% endif %}
</div>

<div style="clear: both; margin-top: 3em;"></div>

<div class="featured-post">
  <h2 class="archive__subtitle">精选推荐</h2>
  {% assign featured_posts = site.tags.featured | default: site.categories.投资理财 | default: site.categories.认知升级 | default: site.posts | slice: 0, 6 %}
  {% if featured_posts.size > 0 %}
    <div class="grid__wrapper">
      {% for post in featured_posts limit:6 %}
        {% include archive-single.html type="grid" %}
      {% endfor %}
    </div>
    {% if site.tags.featured.size > 6 %}
    <div class="view-more-btn">
      <a href="{{ site.baseurl }}/tags/featured/" class="btn btn--primary">查看更多精选</a>
    </div>
    {% elsif site.categories.投资理财.size > 6 %}
    <div class="view-more-btn">
      <a href="{{ site.baseurl }}/categories/投资理财/" class="btn btn--primary">查看更多投资内容</a>
    </div>
    {% endif %}
  {% else %}
    <p><em>敬请期待精选内容...</em></p>
  {% endif %}
</div>

<div style="clear: both; margin-top: 3em;"></div>

<div class="subscription-container" style="margin-top: 3em; padding-top: 2em; border-top: 1px solid #eaeaea;">
  <div class="subscribe-section" style="text-align: center; padding: 2em 0; background-color: #f3f6f6; margin: 2em 0; border-radius: 5px;">
    <h2 style="margin-bottom: 0.5em;">订阅更新</h2>
    <p style="margin-bottom: 1.5em;">选择您喜欢的方式获取最新文章和独家内容的通知。</p>
    
    <!-- 选项1: RSS订阅 -->
    <div class="rss-buttons">
      <h3 style="font-size: 1.2em; margin-bottom: 0.5em;">选项1: RSS订阅（推荐）</h3>
      <p style="margin-bottom: 1em;">使用RSS阅读器自动获取更新通知，无需等待邮件。</p>
      <a href="{{ site.baseurl }}/feed.xml" class="btn btn--success" style="margin-right: 10px;">
        <i class="fas fa-rss"></i> 订阅RSS
      </a>
      <a href="https://feedly.com/i/subscription/feed/{{ site.url }}{{ site.baseurl }}/feed.xml" class="btn btn--info" target="_blank" style="margin-right: 10px;">
        通过Feedly订阅
      </a>
      <a href="https://www.inoreader.com/?add_feed={{ site.url }}{{ site.baseurl }}/feed.xml" class="btn btn--info" target="_blank">
        通过Inoreader订阅
      </a>
    </div>
    
    <!-- 选项2: 邮件订阅 -->
    <div>
      <h3 style="font-size: 1.2em; margin-bottom: 0.5em;">选项2: 邮件订阅</h3>
      <p style="margin-bottom: 1em;">输入您的邮箱地址，我们会在发布重要内容时通知您。</p>
      <form action="https://formspree.io/f/xpwqvvop" method="POST" class="subscription-form-flex" style="max-width: 400px; margin: 0 auto;">
        <div class="form-flex-container">
          <input type="email" name="email" placeholder="您的邮箱地址" required class="email-input">
          <button type="submit" class="btn btn--primary subscribe-btn">订阅</button>
        </div>
        <input type="hidden" name="_subject" value="新订阅 - 有心言者">
        <input type="hidden" name="_next" value="https://zhurong2020.github.io/youxinyanzhe/thanks/">
      </form>
      <p style="font-size: 0.8em; margin-top: 1em; color: #666;">我们尊重您的隐私，绝不会分享您的邮箱地址。邮件通知仅用于重要更新。</p>
    </div>
  </div>
</div>
