#!/usr/bin/env python3
"""
会员管理系统
用于生成验证码、管理会员信息、发送邮件等
"""

import json
import random
import string
import smtplib
import csv
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import os
from typing import Dict, List, Optional

class MemberManager:
    def __init__(self, data_dir: str = ".tmp/member_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据文件路径
        self.registrations_file = self.data_dir / "registrations.json"
        self.access_codes_file = self.data_dir / "access_codes.json"
        self.email_log_file = self.data_dir / "email_log.json"
        
        # 会员等级配置
        self.member_levels = {
            'experience': {'code': 'VIP1', 'days': 7, 'price': 5, 'name': '体验会员'},
            'monthly': {'code': 'VIP2', 'days': 30, 'price': 35, 'name': '月度会员'},
            'quarterly': {'code': 'VIP3', 'days': 90, 'price': 108, 'name': '季度会员'},
            'yearly': {'code': 'VIP4', 'days': 365, 'price': 180, 'name': '年度会员'}
        }
        
        # 邮件配置（需要在环境变量中设置）
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.email_user)
    
    def generate_access_code(self, level: str, custom_expiry: Optional[datetime] = None) -> str:
        """生成访问码"""
        if level not in self.member_levels:
            raise ValueError(f"无效的会员等级: {level}")
        
        level_config = self.member_levels[level]
        level_code = level_config['code']
        
        # 计算过期时间
        if custom_expiry:
            expiry_date = custom_expiry
        else:
            expiry_date = datetime.now() + timedelta(days=level_config['days'])
        
        # 格式化日期为 YYYYMMDD
        expiry_str = expiry_date.strftime('%Y%m%d')
        
        # 生成随机字符串
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        
        # 组合访问码：LEVEL_EXPIRY_RANDOM
        access_code = f"{level_code}_{expiry_str}_{random_part}"
        
        return access_code
    
    def validate_access_code(self, access_code: str) -> Dict:
        """验证访问码"""
        try:
            parts = access_code.split('_')
            if len(parts) != 3:
                return {'valid': False, 'reason': '格式错误'}
            
            level_code, expiry_str, random_part = parts
            
            # 验证等级代码
            level_map = {v['code']: k for k, v in self.member_levels.items()}
            if level_code not in level_map:
                return {'valid': False, 'reason': '无效等级代码'}
            
            # 验证日期格式
            if len(expiry_str) != 8 or not expiry_str.isdigit():
                return {'valid': False, 'reason': '日期格式错误'}
            
            # 解析过期日期
            try:
                expiry_date = datetime.strptime(expiry_str, '%Y%m%d')
            except ValueError:
                return {'valid': False, 'reason': '无效日期'}
            
            # 检查是否过期
            if expiry_date.date() < datetime.now().date():
                return {'valid': False, 'reason': '访问码已过期'}
            
            # 返回验证结果
            level = level_map[level_code]
            return {
                'valid': True,
                'level': level,
                'level_name': self.member_levels[level]['name'],
                'expiry_date': expiry_date,
                'days_remaining': (expiry_date.date() - datetime.now().date()).days
            }
            
        except Exception as e:
            return {'valid': False, 'reason': f'验证错误: {str(e)}'}
    
    def save_registration(self, registration_data: Dict) -> str:
        """保存会员注册信息"""
        # 添加时间戳和ID
        registration_id = f"REG_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        registration_data.update({
            'id': registration_id,
            'registration_time': datetime.now().isoformat(),
            'status': 'pending'  # pending, processed, cancelled
        })
        
        # 读取现有数据
        registrations = self._load_json(self.registrations_file, [])
        registrations.append(registration_data)
        
        # 保存数据
        self._save_json(self.registrations_file, registrations)
        
        return registration_id
    
    def get_pending_registrations(self) -> List[Dict]:
        """获取待处理的注册"""
        registrations = self._load_json(self.registrations_file, [])
        return [r for r in registrations if r.get('status') == 'pending']
    
    def process_registration(self, registration_id: str, generate_code: bool = True) -> Optional[str]:
        """处理注册并生成访问码"""
        registrations = self._load_json(self.registrations_file, [])
        
        # 查找注册记录
        registration = None
        for i, reg in enumerate(registrations):
            if reg['id'] == registration_id:
                registration = reg
                registration_index = i
                break
        
        if not registration:
            print(f"未找到注册记录: {registration_id}")
            return None
        
        if not generate_code:
            # 只更新状态为已处理
            registrations[registration_index]['status'] = 'processed'
            registrations[registration_index]['processed_time'] = datetime.now().isoformat()
            self._save_json(self.registrations_file, registrations)
            return None
        
        # 生成访问码
        try:
            access_code = self.generate_access_code(registration['memberLevel'])
            
            # 保存访问码记录
            access_codes = self._load_json(self.access_codes_file, [])
            code_record = {
                'access_code': access_code,
                'registration_id': registration_id,
                'email': registration['email'],
                'level': registration['memberLevel'],
                'generated_time': datetime.now().isoformat(),
                'status': 'active'
            }
            access_codes.append(code_record)
            self._save_json(self.access_codes_file, access_codes)
            
            # 更新注册状态
            registrations[registration_index]['status'] = 'processed'
            registrations[registration_index]['access_code'] = access_code
            registrations[registration_index]['processed_time'] = datetime.now().isoformat()
            self._save_json(self.registrations_file, registrations)
            
            print(f"已为 {registration['email']} 生成访问码: {access_code}")
            return access_code
            
        except Exception as e:
            print(f"处理注册失败: {str(e)}")
            return None
    
    def send_access_code_email(self, email: str, access_code: str, member_level: str) -> bool:
        """发送访问码邮件"""
        if not all([self.email_user, self.email_password]):
            print("邮件配置未完成，请设置环境变量 EMAIL_USER 和 EMAIL_PASSWORD")
            return False
        
        # 确保必要的配置存在
        if not self.email_user or not self.email_password or not self.from_email:
            print("邮件配置不完整")
            return False
        
        try:
            # 验证访问码获取详细信息
            validation_result = self.validate_access_code(access_code)
            if not validation_result['valid']:
                print(f"访问码无效: {validation_result['reason']}")
                return False
            
            level_name = validation_result['level_name']
            expiry_date = validation_result['expiry_date'].strftime('%Y年%m月%d日')
            days_remaining = validation_result['days_remaining']
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = email
            msg['Subject'] = f"您的{level_name}访问码已生成"
            
            # 邮件正文
            body = f"""
亲爱的会员，

感谢您对我们博客内容的支持！您的{level_name}访问码已生成。

🔑 您的专属访问码：{access_code}

📅 有效期至：{expiry_date} (剩余{days_remaining}天)

🌐 使用方法：
1. 访问会员专区：https://youxinyanzhe.github.io/members/
2. 在验证框中输入上述访问码
3. 点击"验证访问"即可查看专享内容

📚 您可以享受的会员权益：
• 深度投资策略分析和完整代码实现
• 技术实现细节和配置文件
• 马斯克帝国商业数据深度解析
• 独家研究资料和工具资源包
{f"• VIP专享内容和个人投资组合分享" if member_level.endswith('3') or member_level.endswith('4') else ""}
{f"• 一对一咨询机会和专属讨论群" if member_level.endswith('4') else ""}

💡 小贴士：
- 访问码在有效期内可在任意设备使用
- 建议收藏会员专区页面以便随时访问
- 如有任何问题，请通过微信公众号联系我们

再次感谢您的支持，希望我们的内容能为您的学习和投资之路带来帮助！

此致
敬礼！

---
有心眼者博客团队
"""
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            text = msg.as_string()
            server.sendmail(self.from_email, email, text)
            server.quit()
            
            # 记录发送日志
            self._log_email(email, access_code, True, "成功发送")
            
            print(f"访问码邮件已发送至: {email}")
            return True
            
        except Exception as e:
            error_msg = f"发送邮件失败: {str(e)}"
            print(error_msg)
            self._log_email(email, access_code, False, error_msg)
            return False
    
    def batch_process_registrations(self, send_email: bool = True) -> None:
        """批量处理待处理的注册"""
        pending_registrations = self.get_pending_registrations()
        
        if not pending_registrations:
            print("没有待处理的注册")
            return
        
        print(f"发现 {len(pending_registrations)} 个待处理注册")
        
        for registration in pending_registrations:
            print(f"\n处理注册: {registration['id']}")
            print(f"邮箱: {registration['email']}")
            print(f"会员等级: {registration['memberLevel']}")
            print(f"支付金额: ¥{registration['paymentAmount']}")
            
            # 生成访问码
            access_code = self.process_registration(registration['id'])
            
            if access_code and send_email:
                # 发送邮件
                success = self.send_access_code_email(
                    registration['email'],
                    access_code,
                    registration['memberLevel']
                )
                
                if success:
                    print("✅ 处理完成")
                else:
                    print("❌ 邮件发送失败")
            elif access_code:
                print(f"✅ 访问码已生成: {access_code}")
            else:
                print("❌ 访问码生成失败")
    
    def export_registrations_csv(self, filename: Optional[str] = None) -> str:
        """导出注册数据为CSV"""
        if not filename:
            filename = f"registrations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        registrations = self._load_json(self.registrations_file, [])
        
        if not registrations:
            print("没有注册数据可导出")
            return ""
        
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'email', 'wechatId', 'memberLevel', 'paymentAmount', 
                         'paymentTime', 'interests', 'message', 'registration_time', 
                         'status', 'access_code', 'processed_time']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for reg in registrations:
                # 处理interests字段（列表转字符串）
                reg_copy = reg.copy()
                if 'interests' in reg_copy and isinstance(reg_copy['interests'], list):
                    reg_copy['interests'] = ', '.join(reg_copy['interests'])
                
                writer.writerow(reg_copy)
        
        print(f"注册数据已导出至: {filepath}")
        return str(filepath)
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        registrations = self._load_json(self.registrations_file, [])
        access_codes = self._load_json(self.access_codes_file, [])
        
        stats = {
            'total_registrations': len(registrations),
            'pending_registrations': len([r for r in registrations if r.get('status') == 'pending']),
            'processed_registrations': len([r for r in registrations if r.get('status') == 'processed']),
            'total_access_codes': len(access_codes),
            'active_access_codes': len([c for c in access_codes if c.get('status') == 'active']),
            'level_distribution': {},
            'total_revenue': 0
        }
        
        # 统计会员等级分布和收入
        for reg in registrations:
            level = reg.get('memberLevel', 'unknown')
            if level not in stats['level_distribution']:
                stats['level_distribution'][level] = 0
            stats['level_distribution'][level] += 1
            
            if reg.get('status') == 'processed':
                stats['total_revenue'] += float(reg.get('paymentAmount', 0))
        
        return stats
    
    def _load_json(self, filepath: Path, default=None):
        """加载JSON文件"""
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"读取文件失败 {filepath}: {e}")
        return default or {}
    
    def _save_json(self, filepath: Path, data):
        """保存JSON文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存文件失败 {filepath}: {e}")
    
    def _log_email(self, email: str, access_code: str, success: bool, message: str):
        """记录邮件发送日志"""
        email_logs = self._load_json(self.email_log_file, [])
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'email': email,
            'access_code': access_code,
            'success': success,
            'message': message
        }
        
        email_logs.append(log_entry)
        self._save_json(self.email_log_file, email_logs)


def main():
    """命令行界面"""
    import argparse
    
    parser = argparse.ArgumentParser(description='会员管理系统')
    parser.add_argument('command', choices=['generate', 'validate', 'process', 'stats', 'export'], 
                       help='要执行的命令')
    parser.add_argument('--level', choices=['experience', 'monthly', 'quarterly', 'yearly'],
                       help='会员等级')
    parser.add_argument('--code', help='要验证的访问码')
    parser.add_argument('--email', help='邮箱地址')
    parser.add_argument('--no-email', action='store_true', help='不发送邮件')
    
    args = parser.parse_args()
    
    manager = MemberManager()
    
    if args.command == 'generate':
        if not args.level:
            print("请指定会员等级 --level")
            return
        
        code = manager.generate_access_code(args.level)
        print(f"生成的访问码: {code}")
        
        if args.email:
            manager.send_access_code_email(args.email, code, args.level)
    
    elif args.command == 'validate':
        if not args.code:
            print("请指定访问码 --code")
            return
        
        result = manager.validate_access_code(args.code)
        # 转换datetime对象为字符串以便JSON序列化
        if 'expiry_date' in result and result['expiry_date']:
            result['expiry_date'] = result['expiry_date'].strftime('%Y-%m-%d')
        print(f"验证结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    elif args.command == 'process':
        manager.batch_process_registrations(send_email=not args.no_email)
    
    elif args.command == 'stats':
        stats = manager.get_stats()
        print("统计信息:")
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    elif args.command == 'export':
        filepath = manager.export_registrations_csv()
        print(f"导出完成: {filepath}")


if __name__ == '__main__':
    main()