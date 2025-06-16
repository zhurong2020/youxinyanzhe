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
excerpt: "探索云技术、量化投资与生活思考的交汇点"
intro: 
  - excerpt: '分享云技术应用、量化投资策略和个人成长心得，让技术真正为生活赋能。'
feature_row:
  - image_path: https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/c553d355-9a2e-4753-4a47-9009b7cab200/public?format=auto&width=600&quality=75
    alt: "普通人云生活系列"
    title: "普通人云生活系列"
    excerpt: "利用云技术让普通人提高效率，享受数字化生活的便利。从域名注册、网站搭建到云服务应用，打造个人数字生态系统的全方位指南。"
    url: "/categories/云生活/"
    btn_label: "了解更多"
    btn_class: "btn--primary"
  - image_path: https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/e35cd10a-83b4-4939-ecb6-35edeb1a2d00/public?format=auto&width=600&quality=75
    alt: "量化投资系列"
    title: "量化投资系列"
    excerpt: "探索量化交易平台、算法策略开发与自动化投资工具。让数据驱动决策，实现更科学的投资方法。分享实用的量化分析技术与工具。"
    url: "/categories/量化投资/"
    btn_label: "了解更多"
    btn_class: "btn--primary"
  - image_path: https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/25b4d7c3-4f8e-4b62-5b9e-9fe1a6c10200/public?format=auto&width=600&quality=75
    alt: "技术与阅读心得"
    title: "技术与阅读心得"
    excerpt: "分享技术实践经验、工具使用技巧以及读书笔记。记录思考的火花，启发创新的灵感。让知识转化为实践的力量，提升个人与职业发展。"
    url: "/categories/心得/"
    btn_label: "了解更多"
    btn_class: "btn--primary"
---

{% include feature_row id="intro" type="center" %}

<style>
.feature__item p {
  text-align: center !important;
  margin-top: 2em !important;
}
.feature__item p a.btn.btn--primary {
  display: table !important;
  margin: 0 auto !important;
}

/* 新增样式 */
.view-more-btn {
  text-align: center;
  margin-top: 2em;
  margin-bottom: 2em;
  clear: both;
}
.view-more-btn .btn {
  padding: 0.75em 1.5em;
  font-size: 1.1em;
}
</style>

{% include feature_row %}

<div class="latest-posts">
  <h2 class="archive__subtitle">最新文章</h2>
  <div class="grid__wrapper">
    {% for post in site.posts limit:5 %}
      {% include archive-single.html type="grid" %}
    {% endfor %}
  </div>
  {% if site.posts.size > 5 %}
  <div class="view-more-btn">
    <a href="{{ site.baseurl }}/posts/" class="btn btn--primary">查看更多文章</a>
  </div>
  {% endif %}
</div>

<div style="clear: both; margin-top: 3em;"></div>

<div class="featured-post">
  <h2 class="archive__subtitle">精选推荐</h2>
  {% assign featured_posts = site.tags.featured | default: site.posts | slice: 0, 5 %}
  {% if featured_posts.size > 0 %}
    <div class="grid__wrapper">
      {% for post in featured_posts limit:5 %}
        {% include archive-single.html type="grid" %}
      {% endfor %}
    </div>
    {% if featured_posts.size > 5 %}
    <div class="view-more-btn">
      <a href="{{ site.baseurl }}/tags/featured/" class="btn btn--primary">查看更多文章</a>
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
    <p style="margin-bottom: 1.5em;">输入您的邮箱地址，获取最新文章和独家内容的通知。</p>
    <form action="https://formspree.io/f/xpwqvvop" method="POST" class="subscription-form" style="max-width: 500px; margin: 0 auto;">
      <div style="display: flex; justify-content: center; max-width: 400px; margin: 0 auto;">
        <input type="email" name="email" placeholder="您的邮箱地址" required style="padding: 10px; width: 70%; border: 1px solid #ddd; border-radius: 4px 0 0 4px; font-size: 16px;">
        <button type="submit" class="btn btn--primary" style="border-radius: 0 4px 4px 0; margin: 0; flex-shrink: 0;">订阅</button>
      </div>
      <input type="hidden" name="_subject" value="新订阅 - 有心言者">
      <input type="hidden" name="_next" value="{{ site.url }}{{ site.baseurl }}/thanks/">
    </form>
    <p style="font-size: 0.8em; margin-top: 1em; color: #666;">我们尊重您的隐私，绝不会分享您的邮箱地址。</p>
  </div>
</div>