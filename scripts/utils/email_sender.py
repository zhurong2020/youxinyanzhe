"""
邮件发送系统
用于自动发送内容包下载链接给打赏用户
"""

import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class EmailRecord:
    """邮件记录数据类"""
    recipient: str
    article_title: str
    sent_at: str
    status: str
    download_url: str
    attempt_count: int = 1


class EmailSender:
    """邮件发送管理器"""
    
    def __init__(self, smtp_server: str, smtp_port: int, 
                 sender_email: str, sender_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 邮件记录文件
        self.records_file = Path("_data/email_records.json")
        self.records_file.parent.mkdir(exist_ok=True)
        
        # 邮件模板
        self.setup_templates()
    
    def setup_templates(self):
        """设置邮件模板"""
        self.html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>感谢您的支持</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #52adc8;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #52adc8;
            margin: 0;
            font-size: 24px;
        }}
        .content {{
            margin-bottom: 30px;
        }}
        .article-info {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #52adc8;
        }}
        .download-section {{
            background-color: #e8f4f8;
            padding: 25px;
            border-radius: 8px;
            text-align: center;
            margin: 25px 0;
        }}
        .download-btn {{
            display: inline-block;
            background-color: #52adc8;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin-top: 15px;
            transition: background-color 0.3s;
        }}
        .download-btn:hover {{
            background-color: #3d8ba3;
        }}
        .package-contents {{
            margin: 20px 0;
        }}
        .package-contents ul {{
            list-style: none;
            padding: 0;
        }}
        .package-contents li {{
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .package-contents li:before {{
            content: "📄 ";
            margin-right: 8px;
        }}
        .footer {{
            text-align: center;
            font-size: 12px;
            color: #666;
            border-top: 1px solid #eee;
            padding-top: 20px;
            margin-top: 30px;
        }}
        .support-info {{
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border: 1px solid #ffeaa7;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 感谢您的支持！</h1>
            <p>您的完整内容包已经准备好了</p>
        </div>
        
        <div class="content">
            <p>亲爱的读者，</p>
            <p>感谢您对我们内容的支持和认可！您所请求的完整资料包已经为您准备好了。</p>
            
            <div class="article-info">
                <h3>📚 文章信息</h3>
                <p><strong>标题</strong>: {article_title}</p>
                <p><strong>发送时间</strong>: {send_time}</p>
            </div>
            
            <div class="package-contents">
                <h3>📦 资料包内容</h3>
                <ul>
                    <li><strong>完整深度版PDF</strong> - 包含详细技术分析与数据解读</li>
                    <li><strong>高清图表合集</strong> - 文章中所有图表的高清版本</li>
                    <li><strong>参考资料汇总</strong> - 权威来源链接和补充材料</li>
                    <li><strong>资源链接清单</strong> - 相关工具和扩展阅读资源</li>
                </ul>
            </div>
            
            <div class="download-section">
                <h3>⬇️ 立即下载</h3>
                <p>点击下方按钮下载您的完整资料包：</p>
                <a href="{download_url}" class="download-btn">📥 下载完整资料包</a>
                <p><small>链接永久有效，支持多次下载</small></p>
            </div>
            
            <div class="support-info">
                <h4>💡 使用说明</h4>
                <p>• 下载的是ZIP压缩文件，请解压后查看</p>
                <p>• 如果遇到下载问题，请尝试更换浏览器或网络</p>
                <p>• 资料仅供个人学习使用，请勿商业传播</p>
            </div>
            
            <p>再次感谢您的支持！如果您觉得内容有价值，欢迎分享给更多朋友。</p>
            <p>如有任何问题，请随时通过微信公众号与我们联系。</p>
        </div>
        
        <div class="footer">
            <p>此邮件由系统自动发送，请勿直接回复</p>
            <p>📱 微信公众号：有心言者 | 🌐 博客：zhurong2020.github.io</p>
            <p>© 2025 有心言者. 保留所有权利.</p>
        </div>
    </div>
</body>
</html>
        """
        
        self.text_template = """
感谢您的支持！

亲爱的读者，

感谢您对我们内容的支持和认可！您所请求的完整资料包已经为您准备好了。

📚 文章信息
标题: {article_title}
发送时间: {send_time}

📦 资料包内容
• 完整深度版PDF - 包含详细技术分析与数据解读
• 高清图表合集 - 文章中所有图表的高清版本  
• 参考资料汇总 - 权威来源链接和补充材料
• 资源链接清单 - 相关工具和扩展阅读资源

⬇️ 下载链接
{download_url}

💡 使用说明
• 下载的是ZIP压缩文件，请解压后查看
• 如果遇到下载问题，请尝试更换浏览器或网络
• 资料仅供个人学习使用，请勿商业传播

再次感谢您的支持！如果您觉得内容有价值，欢迎分享给更多朋友。

如有任何问题，请随时通过微信公众号与我们联系。

---
此邮件由系统自动发送，请勿直接回复
微信公众号：有心言者 | 博客：zhurong2020.github.io
© 2025 有心言者. 保留所有权利.
        """
    
    def _load_email_records(self) -> List[Dict]:
        """加载邮件记录"""
        if self.records_file.exists():
            try:
                with open(self.records_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.logger.warning("无法加载邮件记录，将创建新文件")
        return []
    
    def _save_email_records(self, records: List[Dict]) -> None:
        """保存邮件记录"""
        try:
            with open(self.records_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存邮件记录失败: {e}")
    
    def send_reward_package(self, recipient_email: str, article_title: str, 
                          download_url: str, user_name: Optional[str] = None) -> Tuple[bool, str]:
        """
        发送奖励内容包邮件
        
        Args:
            recipient_email: 收件人邮箱
            article_title: 文章标题
            download_url: 下载链接
            user_name: 用户名（可选）
            
        Returns:
            (success, message)
        """
        try:
            # 检查是否已发送过
            records = self._load_email_records()
            for record in records:
                if (record["recipient"] == recipient_email and 
                    record["article_title"] == article_title and
                    record["status"] == "sent"):
                    return True, "该用户已收到此文章的资料包"
            
            # 准备邮件内容
            send_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
            subject = f"📦 《{article_title}》完整资料包 - 感谢您的支持！"
            
            # 格式化模板
            html_content = self.html_template.format(
                article_title=article_title,
                send_time=send_time,
                download_url=download_url,
                user_name=user_name or "尊敬的读者"
            )
            
            text_content = self.text_template.format(
                article_title=article_title,
                send_time=send_time,
                download_url=download_url
            )
            
            # 创建邮件
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"有心言者 <{self.sender_email}>"
            message["To"] = recipient_email
            
            # 添加内容
            text_part = MIMEText(text_content, "plain", "utf-8")
            html_part = MIMEText(html_content, "html", "utf-8")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # 发送邮件
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                text = message.as_string()
                server.sendmail(self.sender_email, recipient_email, text)
            
            # 记录发送结果
            email_record = {
                "recipient": recipient_email,
                "article_title": article_title,
                "download_url": download_url,
                "sent_at": datetime.now().isoformat(),
                "status": "sent",
                "attempt_count": 1,
                "user_name": user_name
            }
            
            records.append(email_record)
            self._save_email_records(records)
            
            self.logger.info(f"邮件发送成功: {recipient_email} - {article_title}")
            return True, "邮件发送成功"
            
        except smtplib.SMTPAuthenticationError:
            error_msg = "SMTP认证失败，请检查邮箱密码"
            self.logger.error(error_msg)
            return False, error_msg
        except smtplib.SMTPException as e:
            error_msg = f"SMTP错误: {e}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"发送邮件时发生错误: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_send_records(self, article_title: Optional[str] = None) -> List[Dict]:
        """获取发送记录"""
        records = self._load_email_records()
        if article_title:
            return [r for r in records if r["article_title"] == article_title]
        return records
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        records = self._load_email_records()
        
        total_sent = len([r for r in records if r["status"] == "sent"])
        total_failed = len([r for r in records if r["status"] == "failed"])
        
        # 按文章统计
        article_stats = {}
        for record in records:
            title = record["article_title"]
            if title not in article_stats:
                article_stats[title] = {"sent": 0, "failed": 0}
            article_stats[title][record["status"]] += 1
        
        return {
            "total_emails": len(records),
            "total_sent": total_sent,
            "total_failed": total_failed,
            "success_rate": (total_sent / len(records) * 100) if records else 0,
            "article_stats": article_stats,
            "last_sent": records[-1]["sent_at"] if records else None
        }
    
    def test_connection(self) -> Tuple[bool, str]:
        """测试SMTP连接"""
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
            return True, "SMTP连接测试成功"
        except Exception as e:
            return False, f"SMTP连接测试失败: {e}"


def create_email_sender() -> EmailSender:
    """创建邮件发送器实例"""
    from dotenv import load_dotenv
    load_dotenv()
    
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("GMAIL_USER")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")
    
    if not sender_email or not sender_password:
        raise ValueError("请在.env文件中设置GMAIL_USER和GMAIL_APP_PASSWORD")
    
    return EmailSender(smtp_server, smtp_port, sender_email, sender_password)


if __name__ == "__main__":
    # 测试脚本
    import sys
    
    if len(sys.argv) == 2 and sys.argv[1] == "test":
        try:
            sender = create_email_sender()
            success, message = sender.test_connection()
            print(f"{'✅' if success else '❌'} {message}")
        except Exception as e:
            print(f"❌ 错误: {e}")
    elif len(sys.argv) == 4:
        recipient = sys.argv[1]
        article_title = sys.argv[2]
        download_url = sys.argv[3]
        
        try:
            sender = create_email_sender()
            success, message = sender.send_reward_package(recipient, article_title, download_url)
            print(f"{'✅' if success else '❌'} {message}")
        except Exception as e:
            print(f"❌ 错误: {e}")
    else:
        print("用法:")
        print("  测试连接: python email_sender.py test")
        print("  发送邮件: python email_sender.py <email> <article_title> <download_url>")