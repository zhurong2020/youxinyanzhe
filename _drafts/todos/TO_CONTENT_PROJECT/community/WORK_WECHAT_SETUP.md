# 🤖 企业微信群配置指南

> **企业名称**: aRong's techforum  
> **群名称**: 有心量化-DCA策略交流群  
> **创建时间**: 2025年9月10日

## 🚀 立即执行任务

### Step 1: 添加群机器人

#### 1.1 创建机器人
```
操作路径：
1. 打开企业微信
2. 进入"有心量化-DCA策略交流群"
3. 点击右上角"..."
4. 选择"群机器人"
5. 点击"添加机器人"
6. 设置机器人名称："有心量化助手"
7. 获取Webhook地址（保存好）
```

#### 1.2 测试机器人
```python
# 测试脚本 - 发送第一条消息
import requests
import json

# 替换为您的Webhook地址
webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY_HERE"

def test_robot():
    data = {
        "msgtype": "text",
        "text": {
            "content": "🤖 机器人配置成功！\n我是有心量化助手，将为大家提供自动化服务。"
        }
    }
    response = requests.post(webhook_url, json=data)
    print(f"发送状态: {response.status_code}")
    print(f"返回信息: {response.text}")

# 运行测试
test_robot()
```

### Step 2: 设置群欢迎语

#### 2.1 配置路径
```
手机端：
工作台 → 客户联系 → 加入群聊 → 欢迎语设置

电脑端：
管理后台 → 客户联系 → 加入群聊 → 配置
```

#### 2.2 欢迎语内容
```
🎉 欢迎加入有心量化-DCA策略交流群！

📚 新人必读：
1️⃣ 查看群公告了解群规则
2️⃣ 文件区获取策略和教程
3️⃣ 有问题随时@群管理员

💡 本群由aRong's techforum运营
专注量化策略技术交流分享

⚠️ 内容仅供学习，非投资建议
```

### Step 3: 配置群公告

```
【有心量化-DCA策略交流群】

🏢 运营方：aRong's techforum
📱 管理员：有心量化

📦 资源获取：
- DCA策略文件：群文件下载
- 使用教程：查看群文件
- 开户指南：@管理员获取

⚠️ 重要声明：
本群提供技术交流服务
分享内容仅供参考学习
投资决策请独立判断
盈亏风险自行承担

💬 联系方式：
微信：youxin_quant
群内：@有心量化

更新：2025.09.10
```

### Step 4: 上传群文件

#### 需要上传的文件
1. **DCA策略文件**
   - 文件名：DCA免费版策略_v2.10.3.zip
   - 位置：releases/

2. **使用教程**
   - 文件名：DCA策略使用教程.pdf
   - 内容：从FAQ文档生成

3. **常见问题**
   - 文件名：常见问题FAQ.pdf
   - 内容：docs/promotion/DCA_FREE_FAQ_SIMPLE.md

4. **开户指南**
   - 文件名：Moomoo开户指南.pdf
   - 内容：docs/tutorials/MOOMOO_ACCOUNT_SETUP_GUIDE.md

### Step 5: 设置定时消息

#### 5.1 使用Python脚本定时发送
```python
# cron_messages.py - 定时消息脚本
import requests
import schedule
import time
from datetime import datetime

webhook_url = "YOUR_WEBHOOK_URL"

def send_message(content):
    data = {
        "msgtype": "text",
        "text": {"content": content}
    }
    requests.post(webhook_url, json=data)

def morning_message():
    content = """☀️ 早安，有心量化的朋友们！
    
今天是 {date}
美股开盘时间：21:30
记得检查策略运行状态

祝大家投资顺利！
    """.format(date=datetime.now().strftime("%Y-%m-%d"))
    send_message(content)

def market_open_reminder():
    content = """🔔 美股即将开盘！
    
开盘时间：21:30（还有30分钟）
DCA策略将自动执行
无需手动操作

有问题随时交流~
    """
    send_message(content)

# 设置定时任务
schedule.every().day.at("09:00").do(morning_message)
schedule.every().day.at("21:00").do(market_open_reminder)

# 持续运行
while True:
    schedule.run_pending()
    time.sleep(60)
```

## 📱 群二维码管理

### 生成群活码
```
路径：群设置 → 群二维码 → 创建活码
优势：永不过期，自动换群
用途：对外推广统一入口
```

### 二维码使用场景
- 知乎文章结尾
- 朋友圈分享
- 博客文章
- 私聊邀请

## 🔧 高级配置

### 关键词自动回复（需开发）
```python
# 监听群消息并自动回复
keywords_reply = {
    "策略": "策略文件请在群文件下载",
    "教程": "使用教程在群文件中查看",
    "开户": "开户指南请查看群文件",
    "付费": "付费版咨询请私聊管理员",
    "报错": "请截图发群里，大家会帮助你"
}
```

### 数据统计配置
```
查看路径：
管理后台 → 数据统计 → 客户群统计

关注指标：
- 群成员数量变化
- 群活跃度（消息数）
- 新增/退群趋势
```

## 🎯 今日必做清单

- [ ] 添加群机器人
- [ ] 测试机器人消息
- [ ] 设置群公告
- [ ] 上传策略文件
- [ ] 配置欢迎语
- [ ] 生成群二维码
- [ ] 保存webhook地址

## 📝 运营建议

### 初期运营重点
1. **每天查看2次**：早9晚9
2. **及时回复问题**：2小时内
3. **主动分享内容**：每天1-2条
4. **收集用户反馈**：持续优化

### 群活跃技巧
- 早安问候带话题
- 分享市场观点
- 定期发布数据
- 鼓励用户分享

## ⚠️ 注意事项

1. **Webhook地址保密**：不要泄露给他人
2. **内容合规**：避免投资建议
3. **及时更新**：文件和公告
4. **备份重要信息**：聊天记录

---

最后更新：2025-09-10
负责人：有心量化