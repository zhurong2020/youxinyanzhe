/**
 * 订阅表单处理脚本
 * 
 * 这个脚本处理订阅表单的提交，并显示相应的成功或错误消息
 */
document.addEventListener('DOMContentLoaded', function() {
  const subscriptionForm = document.querySelector('.subscription-form');
  
  if (subscriptionForm) {
    // 检查表单配置
    const formAction = subscriptionForm.getAttribute('action');
    if (formAction.includes('YOUR_FORM_ID')) {
      console.warn('请替换Formspree表单ID: 您需要在Formspree创建一个表单，并用获得的ID替换YOUR_FORM_ID');
      showMessage('订阅功能尚未完全配置，请联系网站管理员', 'warning');
    }
    
    subscriptionForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // 如果表单未配置，显示提示信息
      if (formAction.includes('YOUR_FORM_ID')) {
        showMessage('订阅功能尚未完全配置，请联系网站管理员', 'warning');
        return;
      }
      
      const emailInput = this.querySelector('input[type="email"]');
      const email = emailInput.value.trim();
      
      if (!email) {
        showMessage('请输入有效的邮箱地址', 'error');
        return;
      }
      
      // 显示加载状态
      const submitButton = this.querySelector('button[type="submit"]');
      const originalButtonText = submitButton.textContent;
      submitButton.textContent = '提交中...';
      submitButton.disabled = true;
      
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
        // 恢复按钮状态
        submitButton.textContent = originalButtonText;
        submitButton.disabled = false;
        
        if (response.ok) {
          return response.json();
        }
        throw new Error('网络响应出错 (状态码: ' + response.status + ')');
      })
      .then(data => {
        // 清空输入框
        emailInput.value = '';
        
        // 显示成功消息
        showMessage('订阅成功！感谢您的关注。', 'success');
        
        // 如果设置了重定向，3秒后跳转
        const nextUrl = subscriptionForm.querySelector('input[name="_next"]');
        if (nextUrl && nextUrl.value) {
          setTimeout(() => {
            window.location.href = nextUrl.value;
          }, 2000);
        }
      })
      .catch(error => {
        console.error('Error:', error);
        // 恢复按钮状态
        submitButton.textContent = originalButtonText;
        submitButton.disabled = false;
        
        // 显示详细错误信息
        showMessage('订阅失败: ' + error.message + '。请检查Formspree配置或稍后再试。', 'error');
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
    
    // 5秒后自动隐藏消息
    setTimeout(() => {
      messageElement.style.opacity = '0';
      setTimeout(() => {
        messageElement.remove();
      }, 300);
    }, 5000);
  }
}); 