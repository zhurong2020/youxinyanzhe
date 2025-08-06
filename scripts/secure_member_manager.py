#!/usr/bin/env python3
"""
安全会员管理系统
实施方案3：访问码白名单机制，防止Fork用户绕过验证
"""

import os
import json
import hashlib
import hmac
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from member_management import MemberManager

class SecureMemberManager(MemberManager):
    """
    安全的会员管理器
    实施白名单机制，只有通过此系统生成的访问码才能通过验证
    """
    
    def __init__(self, data_dir: str = ".tmp/member_data"):
        super().__init__(data_dir)
        
        # 白名单文件 - 不提交到Git
        self.whitelist_file = self.data_dir / "access_codes_whitelist.json"
        self.security_key = self._get_or_create_security_key()
        
        # 确保.gitignore包含白名单文件
        self._ensure_gitignore()
    
    def _get_or_create_security_key(self) -> str:
        """获取或创建安全密钥"""
        key_file = self.data_dir / ".security_key"
        
        if key_file.exists():
            try:
                with open(key_file, 'r') as f:
                    return f.read().strip()
            except Exception:
                pass
        
        # 生成新的安全密钥
        import secrets
        security_key = secrets.token_hex(32)
        
        try:
            with open(key_file, 'w') as f:
                f.write(security_key)
            
            # 设置文件权限为只读
            os.chmod(key_file, 0o600)
            print(f"✅ 已生成新的安全密钥: {key_file}")
        except Exception as e:
            print(f"⚠️  无法保存安全密钥: {e}")
        
        return security_key
    
    def _ensure_gitignore(self):
        """确保敏感文件被Git忽略"""
        gitignore_path = Path(".gitignore")
        ignore_patterns = [
            ".tmp/member_data/access_codes_whitelist.json",
            ".tmp/member_data/.security_key"
        ]
        
        existing_content = ""
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                existing_content = f.read()
        
        # 检查并添加缺失的忽略模式
        need_update = False
        for pattern in ignore_patterns:
            if pattern not in existing_content:
                existing_content += f"\n# 会员系统安全文件\n{pattern}\n"
                need_update = True
        
        if need_update:
            with open(gitignore_path, 'w') as f:
                f.write(existing_content)
            print("✅ 已更新.gitignore，保护安全文件")
    
    def generate_secure_access_code(self, level: str, custom_expiry: Optional[datetime] = None) -> str:
        """
        生成安全访问码并加入白名单
        
        Args:
            level: 会员等级
            custom_expiry: 自定义过期时间
        
        Returns:
            安全的访问码
        """
        # 使用父类方法生成基础访问码
        access_code = self.generate_access_code(level, custom_expiry)
        
        # 加入白名单
        self._add_to_whitelist(access_code, level)
        
        print(f"✅ 已生成安全访问码并加入白名单: {access_code}")
        return access_code
    
    def _add_to_whitelist(self, code: str, level: str):
        """将访问码加入白名单"""
        whitelist = self._load_json(self.whitelist_file, {})
        
        # 生成签名以验证访问码的真实性
        signature = self._generate_signature(code)
        
        whitelist[code] = {
            'level': level,
            'generated_time': datetime.now().isoformat(),
            'signature': signature,
            'status': 'active'
        }
        
        self._save_json(self.whitelist_file, whitelist)
    
    def _generate_signature(self, access_code: str) -> str:
        """为访问码生成HMAC签名"""
        message = f"{access_code}_{self.security_key}".encode('utf-8')
        signature = hmac.new(
            self.security_key.encode('utf-8'),
            message,
            hashlib.sha256
        ).hexdigest()[:16]  # 取前16位
        return signature
    
    def validate_secure_access_code(self, access_code: str) -> Dict:
        """
        安全验证访问码
        只有在白名单中且签名正确的访问码才能通过验证
        
        Args:
            access_code: 待验证的访问码
        
        Returns:
            验证结果字典
        """
        # 首先进行基础格式验证
        basic_result = self.validate_access_code(access_code)
        if not basic_result['valid']:
            return basic_result
        
        # 检查是否在白名单中
        if not self.is_code_whitelisted(access_code):
            return {
                'valid': False,
                'reason': '访问码未通过安全验证',
                'security_check': 'failed'
            }
        
        # 验证签名
        if not self._verify_signature(access_code):
            return {
                'valid': False,
                'reason': '访问码签名验证失败',
                'security_check': 'signature_failed'
            }
        
        # 所有验证通过
        basic_result['security_check'] = 'passed'
        print(f"✅ 访问码安全验证通过: {access_code}")
        return basic_result
    
    def is_code_whitelisted(self, code: str) -> bool:
        """检查访问码是否在白名单中"""
        whitelist = self._load_json(self.whitelist_file, {})
        return (
            code in whitelist and 
            whitelist[code].get('status') == 'active'
        )
    
    def _verify_signature(self, access_code: str) -> bool:
        """验证访问码的签名"""
        whitelist = self._load_json(self.whitelist_file, {})
        if access_code not in whitelist:
            return False
        
        stored_signature = whitelist[access_code].get('signature', '')
        expected_signature = self._generate_signature(access_code)
        
        return hmac.compare_digest(stored_signature, expected_signature)
    
    def revoke_access_code(self, access_code: str) -> bool:
        """撤销访问码"""
        whitelist = self._load_json(self.whitelist_file, {})
        
        if access_code in whitelist:
            whitelist[access_code]['status'] = 'revoked'
            whitelist[access_code]['revoked_time'] = datetime.now().isoformat()
            self._save_json(self.whitelist_file, whitelist)
            print(f"✅ 已撤销访问码: {access_code}")
            return True
        else:
            print(f"❌ 访问码不存在: {access_code}")
            return False
    
    def list_active_codes(self) -> List[Dict]:
        """列出所有活跃的访问码"""
        whitelist = self._load_json(self.whitelist_file, {})
        active_codes = []
        
        for code, info in whitelist.items():
            if info.get('status') == 'active':
                # 验证访问码是否仍然有效
                validation = self.validate_access_code(code)
                if validation['valid']:
                    active_codes.append({
                        'code': code,
                        'level': info['level'],
                        'generated_time': info['generated_time'],
                        'expiry': validation.get('expiry_date'),
                        'days_remaining': validation.get('days_remaining', 0)
                    })
        
        return active_codes
    
    def get_whitelist_stats(self) -> Dict:
        """获取白名单统计信息"""
        whitelist = self._load_json(self.whitelist_file, {})
        
        stats = {
            'total_codes': len(whitelist),
            'active_codes': 0,
            'revoked_codes': 0,
            'expired_codes': 0,
            'level_distribution': {}
        }
        
        for code, info in whitelist.items():
            level = info.get('level', 'unknown')
            if level not in stats['level_distribution']:
                stats['level_distribution'][level] = 0
            
            if info.get('status') == 'active':
                # 检查是否过期
                validation = self.validate_access_code(code)
                if validation['valid']:
                    stats['active_codes'] += 1
                    stats['level_distribution'][level] += 1
                else:
                    stats['expired_codes'] += 1
            else:
                stats['revoked_codes'] += 1
        
        return stats

def main():
    """命令行界面"""
    import argparse
    
    parser = argparse.ArgumentParser(description='安全会员管理系统')
    parser.add_argument('command', choices=[
        'generate', 'validate', 'revoke', 'list', 'stats'
    ], help='要执行的命令')
    parser.add_argument('--level', choices=['experience', 'monthly', 'quarterly', 'yearly'],
                       help='会员等级')
    parser.add_argument('--code', help='访问码')
    parser.add_argument('--email', help='邮箱地址')
    
    args = parser.parse_args()
    
    manager = SecureMemberManager()
    
    if args.command == 'generate':
        if not args.level:
            print("请指定会员等级 --level")
            return
        
        code = manager.generate_secure_access_code(args.level)
        print(f"生成的安全访问码: {code}")
        
        if args.email:
            success = manager.send_access_code_email(args.email, code, args.level)
            if success:
                print("✅ 邮件发送成功")
            else:
                print("❌ 邮件发送失败")
    
    elif args.command == 'validate':
        if not args.code:
            print("请指定访问码 --code")
            return
        
        result = manager.validate_secure_access_code(args.code)
        # 转换datetime对象为字符串以便JSON序列化
        if 'expiry_date' in result and result['expiry_date']:
            result['expiry_date'] = result['expiry_date'].strftime('%Y-%m-%d')
        print(f"验证结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
    
    elif args.command == 'revoke':
        if not args.code:
            print("请指定访问码 --code")
            return
        
        manager.revoke_access_code(args.code)
    
    elif args.command == 'list':
        codes = manager.list_active_codes()
        if codes:
            print("活跃的访问码:")
            for code_info in codes:
                print(f"  {code_info['code']} | {code_info['level']} | "
                      f"剩余{code_info['days_remaining']}天")
        else:
            print("没有活跃的访问码")
    
    elif args.command == 'stats':
        stats = manager.get_whitelist_stats()
        print("白名单统计:")
        print(json.dumps(stats, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()