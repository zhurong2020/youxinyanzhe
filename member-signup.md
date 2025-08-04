---
layout: single
title: "会员信息登记"
permalink: /member-signup/
author_profile: true
classes: wide
header:
  overlay_color: "#000"
  overlay_filter: "0.5"
excerpt: "完成付费后，请填写以下信息以便我们为您发放访问码"
---

<div class="signup-container">
  <div class="notice--info">
    <h4><i class="fas fa-user-plus"></i> 会员信息登记</h4>
    <p>请在完成微信公众号打赏后填写以下信息，我们将在24小时内通过邮件发送您的专属访问码。</p>
  </div>

  <form id="memberSignupForm" class="signup-form">
    <div class="form-group">
      <label for="email"><i class="fas fa-envelope"></i> 邮箱地址 *</label>
      <input type="email" id="email" name="email" required placeholder="用于接收访问码">
      <small>我们承诺不会向第三方泄露您的邮箱信息</small>
    </div>

    <div class="form-group">
      <label for="wechatId"><i class="fab fa-weixin"></i> 微信号/昵称</label>
      <input type="text" id="wechatId" name="wechatId" placeholder="便于核对打赏记录（可选）">
    </div>

    <div class="form-group">
      <label for="memberLevel"><i class="fas fa-crown"></i> 选择会员等级 *</label>
      <select id="memberLevel" name="memberLevel" required>
        <option value="">请选择会员等级</option>
        <option value="experience">体验会员 (￥5/7天)</option>
        <option value="monthly">月度会员 (￥35/30天) - 对应1杯咖啡($5)</option>
        <option value="quarterly">季度会员 (￥108/90天) - 对应3杯咖啡($15)</option>
        <option value="yearly">年度会员 (￥180/365天) - 对应5杯咖啡($25)</option>
      </select>
    </div>

    <div class="form-group">
      <label for="paymentAmount"><i class="fas fa-yen-sign"></i> 打赏金额 *</label>
      <input type="number" id="paymentAmount" name="paymentAmount" required placeholder="请输入实际打赏金额" min="5">
      <small>用于核对支付记录，确保准确发放对应等级访问码</small>
    </div>

    <div class="form-group">
      <label for="paymentTime"><i class="fas fa-clock"></i> 打赏时间 *</label>
      <input type="datetime-local" id="paymentTime" name="paymentTime" required>
      <small>请选择您完成打赏的大致时间</small>
    </div>

    <div class="form-group">
      <label for="interests"><i class="fas fa-heart"></i> 感兴趣的内容 (多选)</label>
      <div class="checkbox-group">
        <label class="checkbox-item">
          <input type="checkbox" name="interests" value="investment"> 投资策略分析
        </label>
        <label class="checkbox-item">
          <input type="checkbox" name="interests" value="technology"> 技术实现方案
        </label>
        <label class="checkbox-item">
          <input type="checkbox" name="interests" value="musk-empire"> 马斯克帝国解析
        </label>
        <label class="checkbox-item">
          <input type="checkbox" name="interests" value="ai-tools"> AI工具应用
        </label>
        <label class="checkbox-item">
          <input type="checkbox" name="interests" value="quantitative"> 量化交易
        </label>
      </div>
    </div>

    <div class="form-group">
      <label for="message"><i class="fas fa-comment"></i> 留言 (可选)</label>
      <textarea id="message" name="message" rows="4" placeholder="有什么想对我说的话，或者希望看到的内容？"></textarea>
    </div>

    <div class="form-group">
      <label class="checkbox-item privacy-agreement">
        <input type="checkbox" id="privacyAgreement" required>
        我已阅读并同意 <a href="#" onclick="showPrivacyPolicy()">隐私政策</a> *
      </label>
    </div>

    <button type="submit" class="submit-btn">
      <i class="fas fa-paper-plane"></i> 提交信息
    </button>
  </form>

  <div id="submitMessage" class="submit-message" style="display: none;"></div>
</div>

## 📋 处理流程说明

<div class="process-steps">
  <div class="step">
    <div class="step-number">1</div>
    <div class="step-content">
      <h4>微信公众号打赏</h4>
      <p>在微信公众号内选择合适的会员等级完成打赏支付</p>
    </div>
  </div>

  <div class="step">
    <div class="step-number">2</div>
    <div class="step-content">
      <h4>填写登记信息</h4>
      <p>在本页面填写邮箱、会员等级等必要信息</p>
    </div>
  </div>

  <div class="step">
    <div class="step-number">3</div>
    <div class="step-content">
      <h4>信息核对确认</h4>
      <p>我们会核对打赏记录与登记信息，确保准确性</p>
    </div>
  </div>

  <div class="step">
    <div class="step-number">4</div>
    <div class="step-content">
      <h4>发放访问码</h4>
      <p>24小时内通过邮件发送对应等级的专属访问码</p>
    </div>
  </div>
</div>

## ❓ 常见问题

**Q: 填写信息后多久能收到访问码？**
A: 通常24小时内发放，工作日可能更快。请注意查收邮件。

**Q: 如果没有收到邮件怎么办？**
A: 请检查垃圾邮件箱，或通过公众号联系我们重新发送。

**Q: 可以修改已提交的信息吗？**
A: 如需修改，请通过公众号联系我们说明情况。

**Q: 访问码是否可以分享？**
A: 访问码仅供个人使用，请勿分享给他人。

---

<div id="privacyModal" class="modal" style="display: none;">
  <div class="modal-content">
    <span class="close" onclick="closePrivacyPolicy()">&times;</span>
    <h3>隐私政策</h3>
    <div class="privacy-content">
      <h4>信息收集</h4>
      <p>我们只收集必要的信息用于会员服务：</p>
      <ul>
        <li>邮箱地址：用于发送访问码和重要通知</li>
        <li>微信信息：用于核对支付记录</li>
        <li>兴趣偏好：用于优化内容推荐</li>
      </ul>
      
      <h4>信息使用</h4>
      <p>您的信息仅用于：</p>
      <ul>
        <li>会员身份验证和访问码发放</li>
        <li>内容推荐和服务改进</li>
        <li>重要通知和会员服务</li>
      </ul>
      
      <h4>信息保护</h4>
      <p>我们承诺：</p>
      <ul>
        <li>不会向任何第三方出售或泄露您的个人信息</li>
        <li>采用安全措施保护您的数据</li>
        <li>您可随时要求删除您的个人信息</li>
      </ul>
    </div>
  </div>
</div>

<script>
document.getElementById('memberSignupForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // 收集表单数据
    const formData = new FormData(this);
    const data = {};
    
    // 处理普通字段
    for (let [key, value] of formData.entries()) {
        if (key === 'interests') {
            if (!data.interests) data.interests = [];
            data.interests.push(value);
        } else {
            data[key] = value;
        }
    }
    
    // 验证必填字段
    if (!data.email || !data.memberLevel || !data.paymentAmount || !data.paymentTime) {
        showSubmitMessage('请填写所有必填字段', 'error');
        return;
    }
    
    // 验证邮箱格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
        showSubmitMessage('请输入有效的邮箱地址', 'error');
        return;
    }
    
    // 验证金额与会员等级匹配
    const levelPrices = {
        'experience': 5,
        'monthly': 35,
        'quarterly': 108,
        'yearly': 180
    };
    
    if (parseInt(data.paymentAmount) < levelPrices[data.memberLevel]) {
        showSubmitMessage('打赏金额与选择的会员等级不匹配', 'error');
        return;
    }
    
    // 模拟提交处理
    showSubmitMessage('正在处理您的信息...', 'info');
    
    setTimeout(() => {
        // 这里应该连接到实际的后端处理
        console.log('会员登记信息:', data);
        
        // 保存到本地存储（实际应用中应发送到服务器）
        const timestamp = new Date().toISOString();
        const registrationData = {
            ...data,
            timestamp: timestamp,
            id: 'REG_' + Date.now()
        };
        
        // 模拟保存
        let registrations = JSON.parse(localStorage.getItem('memberRegistrations') || '[]');
        registrations.push(registrationData);
        localStorage.setItem('memberRegistrations', JSON.stringify(registrations));
        
        showSubmitMessage(
            '信息提交成功！我们将在24小时内核对您的支付记录并通过邮件发送访问码。请注意查收邮件。', 
            'success'
        );
        
        // 清空表单
        this.reset();
        
    }, 2000);
});

function showSubmitMessage(message, type) {
    const messageDiv = document.getElementById('submitMessage');
    messageDiv.style.display = 'block';
    messageDiv.className = `submit-message notice--${type}`;
    messageDiv.innerHTML = `<p>${message}</p>`;
    
    messageDiv.scrollIntoView({ behavior: 'smooth' });
}

function showPrivacyPolicy() {
    document.getElementById('privacyModal').style.display = 'block';
}

function closePrivacyPolicy() {
    document.getElementById('privacyModal').style.display = 'none';
}

// 点击模态框外部关闭
window.onclick = function(event) {
    const modal = document.getElementById('privacyModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

// 根据会员等级自动设置建议金额
document.getElementById('memberLevel').addEventListener('change', function() {
    const paymentAmount = document.getElementById('paymentAmount');
    const levelPrices = {
        'experience': 5,
        'monthly': 35,
        'quarterly': 108,
        'yearly': 180
    };
    
    if (this.value && levelPrices[this.value]) {
        paymentAmount.value = levelPrices[this.value];
    }
});

// 设置默认时间为当前时间
document.addEventListener('DOMContentLoaded', function() {
    const now = new Date();
    const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000)
        .toISOString()
        .slice(0, 16);
    document.getElementById('paymentTime').value = localDateTime;
});
</script>

<style>
.signup-container {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
}

.signup-form {
    background: #f8f9fa;
    padding: 30px;
    border-radius: 8px;
    margin: 20px 0;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
    color: #2c3e50;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    box-sizing: border-box;
}

.form-group small {
    display: block;
    margin-top: 5px;
    color: #6c757d;
    font-size: 12px;
}

.checkbox-group {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 10px;
    margin-top: 10px;
}

.checkbox-item {
    display: flex;
    align-items: center;
    font-weight: normal !important;
    margin-bottom: 0 !important;
}

.checkbox-item input[type="checkbox"] {
    width: auto;
    margin-right: 8px;
}

.privacy-agreement {
    margin-top: 15px;
}

.submit-btn {
    background: #28a745;
    color: white;
    padding: 12px 30px;
    border: none;
    border-radius: 4px;
    font-size: 16px;
    cursor: pointer;
    width: 100%;
    transition: background-color 0.3s;
}

.submit-btn:hover {
    background: #218838;
}

.submit-message {
    margin-top: 20px;
    padding: 15px;
    border-radius: 4px;
}

.process-steps {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin: 30px 0;
}

.step {
    display: flex;
    align-items: flex-start;
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
}

.step-number {
    background: #007bff;
    color: white;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin-right: 15px;
    flex-shrink: 0;
}

.step-content h4 {
    margin: 0 0 8px 0;
    color: #2c3e50;
}

.step-content p {
    margin: 0;
    color: #6c757d;
    font-size: 14px;
}

/* 模态框样式 */
.modal {
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.5);
}

.modal-content {
    background-color: #fefefe;
    margin: 15% auto;
    padding: 20px;
    border: 1px solid #888;
    width: 80%;
    max-width: 600px;
    border-radius: 8px;
    position: relative;
}

.close {
    color: #aaa;
    float: right;
    font-size: 28px;
    font-weight: bold;
    position: absolute;
    right: 15px;
    top: 10px;
    cursor: pointer;
}

.close:hover {
    color: black;
}

.privacy-content h4 {
    color: #2c3e50;
    margin-top: 20px;
}

.privacy-content ul {
    margin-left: 20px;
}

@media (max-width: 768px) {
    .signup-container {
        padding: 10px;
    }
    
    .signup-form {
        padding: 20px;
    }
    
    .checkbox-group {
        grid-template-columns: 1fr;
    }
}
</style>