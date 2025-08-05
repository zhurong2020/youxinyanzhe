#!/usr/bin/env python3
"""
管理员访问码生成器
生成长期有效的管理员专用访问码，无需邮件验证，适合开发和管理使用
"""

import json
import random
import string
from datetime import datetime, timedelta
from pathlib import Path

class AdminAccessGenerator:
    def __init__(self):
        self.data_dir = Path(".tmp/admin_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.admin_codes_file = self.data_dir / "admin_codes.json"
    
    def generate_admin_code(self, purpose: str = "development", days: int = 365) -> str:
        """生成管理员访问码"""
        # 使用ADMIN前缀区分管理员码
        expiry_date = datetime.now() + timedelta(days=days)
        expiry_str = expiry_date.strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        admin_code = f"ADMIN_{expiry_str}_{random_part}"
        
        # 保存记录
        self._save_admin_code(admin_code, purpose, expiry_date)
        
        return admin_code
    
    def generate_quick_test_codes(self) -> dict:
        """生成用于快速测试的各级别访问码"""
        codes = {}
        levels = {
            'experience': {'code': 'VIP1', 'days': 30},  # 延长体验期便于测试
            'monthly': {'code': 'VIP2', 'days': 90},
            'quarterly': {'code': 'VIP3', 'days': 180},
            'yearly': {'code': 'VIP4', 'days': 365}
        }
        
        for level, config in levels.items():
            expiry_date = datetime.now() + timedelta(days=config['days'])
            expiry_str = expiry_date.strftime('%Y%m%d')
            random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
            
            test_code = f"{config['code']}_{expiry_str}_TEST{random_part}"
            codes[level] = {
                'code': test_code,
                'expiry': expiry_date.strftime('%Y-%m-%d'),
                'days': config['days']
            }
            
            # 保存测试码记录
            self._save_admin_code(test_code, f"test_{level}", expiry_date)
        
        return codes
    
    def validate_admin_code(self, code: str) -> dict:
        """验证管理员访问码"""
        if code.startswith('ADMIN_'):
            # 管理员码验证
            parts = code.split('_')
            if len(parts) != 3:
                return {'valid': False, 'reason': '格式错误'}
            
            try:
                expiry_str = parts[1]
                expiry_date = datetime.strptime(expiry_str, '%Y%m%d')
                
                if expiry_date.date() < datetime.now().date():
                    return {'valid': False, 'reason': '管理员码已过期'}
                
                return {
                    'valid': True,
                    'type': 'admin',
                    'level': 'admin',
                    'level_name': '管理员',
                    'expiry_date': expiry_date,
                    'days_remaining': (expiry_date.date() - datetime.now().date()).days
                }
            except ValueError:
                return {'valid': False, 'reason': '日期格式错误'}
        else:
            # 普通会员码验证（兼容原系统）
            from member_management import MemberManager
            manager = MemberManager()
            return manager.validate_access_code(code)
    
    def list_admin_codes(self) -> list:
        """列出所有管理员访问码"""
        admin_codes = self._load_json(self.admin_codes_file, [])
        
        # 过滤未过期的码
        active_codes = []
        for code_record in admin_codes:
            expiry_date = datetime.fromisoformat(code_record['expiry_date'])
            if expiry_date.date() >= datetime.now().date():
                code_record['days_remaining'] = (expiry_date.date() - datetime.now().date()).days
                active_codes.append(code_record)
        
        return active_codes
    
    def _save_admin_code(self, code: str, purpose: str, expiry_date: datetime):
        """保存管理员码记录"""
        admin_codes = self._load_json(self.admin_codes_file, [])
        
        record = {
            'code': code,
            'purpose': purpose,
            'generated_time': datetime.now().isoformat(),
            'expiry_date': expiry_date.isoformat(),
            'status': 'active'
        }
        
        admin_codes.append(record)
        self._save_json(self.admin_codes_file, admin_codes)
    
    def _load_json(self, filepath: Path, default=None):
        """加载JSON文件"""
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"读取文件失败 {filepath}: {e}")
        return default or []
    
    def _save_json(self, filepath: Path, data):
        """保存JSON文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存文件失败 {filepath}: {e}")


def main():
    """命令行界面"""
    import argparse
    
    parser = argparse.ArgumentParser(description='管理员访问码生成器')
    parser.add_argument('command', choices=['admin', 'test', 'list', 'validate'], 
                       help='要执行的命令')
    parser.add_argument('--purpose', default='development', help='访问码用途')
    parser.add_argument('--days', type=int, default=365, help='有效天数')
    parser.add_argument('--code', help='要验证的访问码')
    
    args = parser.parse_args()
    
    generator = AdminAccessGenerator()
    
    if args.command == 'admin':
        code = generator.generate_admin_code(args.purpose, args.days)
        print(f"管理员访问码: {code}")
        print(f"用途: {args.purpose}")
        print(f"有效期: {args.days} 天")
    
    elif args.command == 'test':
        codes = generator.generate_quick_test_codes()
        print("测试用访问码:")
        for level, info in codes.items():
            print(f"  {level}: {info['code']} (有效至: {info['expiry']})")
    
    elif args.command == 'list':
        codes = generator.list_admin_codes()
        if codes:
            print("活跃的管理员访问码:")
            for record in codes:
                expiry = datetime.fromisoformat(record['expiry_date']).strftime('%Y-%m-%d')
                print(f"  {record['code']} - {record['purpose']} (剩余: {record['days_remaining']}天, 到期: {expiry})")
        else:
            print("没有活跃的管理员访问码")
    
    elif args.command == 'validate':
        if not args.code:
            print("请指定访问码 --code")
            return
        
        result = generator.validate_admin_code(args.code)
        if 'expiry_date' in result and result['expiry_date']:
            result['expiry_date'] = result['expiry_date'].strftime('%Y-%m-%d')
        print(f"验证结果: {json.dumps(result, ensure_ascii=False, indent=2)}")


if __name__ == '__main__':
    main()