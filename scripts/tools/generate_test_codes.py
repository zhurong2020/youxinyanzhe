#!/usr/bin/env python3
"""
快速生成测试验证码工具
用于管理员测试会员系统功能
"""

import random
import string
from datetime import datetime, timedelta

def generate_random_suffix(length=7):
    """生成随机后缀"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_test_codes():
    """生成一套完整的测试验证码"""
    
    # 计算各种有效期的到期日期
    today = datetime.now()
    dates = {
        'admin': (today + timedelta(days=3650)).strftime('%Y%m%d'),  # 10年
        'vip1': (today + timedelta(days=7)).strftime('%Y%m%d'),     # 7天
        'vip2': (today + timedelta(days=30)).strftime('%Y%m%d'),    # 30天
        'vip3': (today + timedelta(days=90)).strftime('%Y%m%d'),    # 90天
        'vip4': (today + timedelta(days=365)).strftime('%Y%m%d'),   # 365天
    }
    
    # 生成验证码
    codes = {
        'ADMIN': f"ADMIN_{dates['admin']}_MGR{generate_random_suffix(4)}",
        'VIP1': f"VIP1_{dates['vip1']}_T{generate_random_suffix(5)}",
        'VIP2': f"VIP2_{dates['vip2']}_T{generate_random_suffix(5)}",
        'VIP3': f"VIP3_{dates['vip3']}_T{generate_random_suffix(5)}",
        'VIP4': f"VIP4_{dates['vip4']}_T{generate_random_suffix(5)}",
    }
    
    return codes, dates

def print_test_codes():
    """打印测试验证码"""
    codes, dates = generate_test_codes()
    
    print("🧪 管理员测试验证码")
    print("=" * 50)
    print(f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    descriptions = {
        'ADMIN': '管理员验证码 (10年有效)',
        'VIP1': '体验会员测试码 (7天有效)',
        'VIP2': '月度会员测试码 (30天有效)', 
        'VIP3': '季度会员测试码 (90天有效)',
        'VIP4': '年度会员测试码 (365天有效)',
    }
    
    for level, code in codes.items():
        expiry_date = dates[level.lower()]
        expiry_formatted = f"{expiry_date[:4]}-{expiry_date[4:6]}-{expiry_date[6:8]}"
        print(f"🔑 {descriptions[level]}")
        print(f"   验证码: {code}")
        print(f"   到期日: {expiry_formatted}")
        print()
    
    # 输出.env格式
    print("\n📋 .env文件格式 (可直接复制)")
    print("-" * 50)
    for level, code in codes.items():
        print(f"TEST_{level}_CODE={code}")
    
    print("\n⚠️ 安全提醒:")
    print("- 这些验证码仅用于开发测试")
    print("- 生产环境请删除所有测试验证码")
    print("- 不要将包含真实验证码的.env文件提交到Git")

def generate_single_code(level='VIP2', days=30):
    """生成单个验证码"""
    today = datetime.now()
    expiry = (today + timedelta(days=days)).strftime('%Y%m%d')
    random_suffix = generate_random_suffix(6)
    
    if level == 'ADMIN':
        code = f"ADMIN_{expiry}_ADM{random_suffix[:4]}"
    else:
        code = f"{level}_{expiry}_T{random_suffix[:5]}"
    
    expiry_formatted = f"{expiry[:4]}-{expiry[4:6]}-{expiry[6:8]}"
    
    print(f"🔑 新生成的{level}验证码:")
    print(f"   验证码: {code}")
    print(f"   到期日: {expiry_formatted}")
    
    return code

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'single':
        # 生成单个验证码
        level = sys.argv[2] if len(sys.argv) > 2 else 'VIP2'
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        generate_single_code(level, days)
    else:
        # 生成完整套装
        print_test_codes()
    
    print(f"\n💡 使用说明:")
    print(f"   完整套装: python {sys.argv[0]}")
    print(f"   单个验证码: python {sys.argv[0]} single VIP3 90")