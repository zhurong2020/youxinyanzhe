/**
 * 订阅表单处理脚本
 * 
 * 这个脚本处理订阅表单的提交，并显示相应的成功或错误消息
 */
document.addEventListener('DOMContentLoaded', function() {
  const subscriptionForm = document.querySelector('.subscription-form');
  
  if (subscriptionForm) {
    subscriptionForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const emailInput = this.querySelector('input[type="email"]');
      const email = emailInput.value.trim();
      
      if (!email) {
        showMessage('请输入有效的邮箱地址', 'error');
        return;
      }
      
      // 这里可以替换为实际的API端点
      const formAction = this.getAttribute('action');
      
      // 创建一个FormData对象
      const formData = new FormData();
      formData.append('email', email);
      
      // 发送AJAX请求
      fetch(formAction, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json'
        }
      })
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('网络响应出错');
      })
      .then(data => {
        // 清空输入框
        emailInput.value = '';
        
        // 显示成功消息
        showMessage('订阅成功！感谢您的关注。', 'success');
      })
      .catch(error => {
        console.error('Error:', error);
        showMessage('订阅失败，请稍后再试。', 'error');
      });
    });
  }
  
  // 显示消息函数
  function showMessage(message, type) {
    // 检查是否已存在消息元素
    let messageElement = document.querySelector('.subscription-message');
    
    if (!messageElement) {
      // 创建消息元素
      messageElement = document.createElement('div');
      messageElement.className = 'subscription-message';
      
      // 将消息元素添加到表单后面
      subscriptionForm.insertAdjacentElement('afterend', messageElement);
    }
    
    // 设置消息内容和样式
    messageElement.textContent = message;
    messageElement.className = `subscription-message ${type}`;
    
    // 3秒后自动隐藏消息
    setTimeout(() => {
      messageElement.style.opacity = '0';
      setTimeout(() => {
        messageElement.remove();
      }, 300);
    }, 3000);
  }
}); 