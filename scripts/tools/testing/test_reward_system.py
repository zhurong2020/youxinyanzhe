#!/usr/bin/env python3
"""
微信内容变现系统测试脚本
用于测试第一阶段功能的基本可用性
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# 修正导入路径以匹配新的项目结构，移除未使用的sys.path.append


def test_environment():
    """测试环境配置"""
    print("🔍 检查环境配置...")
    
    load_dotenv()
    
    # 检查必要的环境变量
    required_vars = {
        "GITHUB_TOKEN": "GitHub访问token",
        "GITHUB_USERNAME": "GitHub用户名", 
        "GITHUB_REPO": "GitHub仓库名",
        "GMAIL_USER": "Gmail邮箱地址",
        "GMAIL_APP_PASSWORD": "Gmail应用密码",
        "WECHAT_APPID": "微信公众号AppID",
        "WECHAT_APPSECRET": "微信公众号AppSecret"
    }
    
    missing_vars = []
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if not value or value in ["your_github_token", "your_email@gmail.com"]:
            missing_vars.append(f"  - {var}: {desc}")
        else:
            print(f"  ✅ {var}: 已配置")
    
    if missing_vars:
        print(f"\n❌ 缺少以下环境变量配置:")
        for var in missing_vars:
            print(var)
        return False
    
    print("✅ 环境配置检查通过")
    return True

def test_dependencies():
    """测试依赖包"""
    print("\n🔍 检查Python依赖包...")
    
    dependencies = [
        ("requests", "HTTP请求库"),
        ("frontmatter", "Frontmatter解析"),
        ("markdown2", "Markdown转换"),
        ("weasyprint", "PDF生成"),
        ("google.generativeai", "Gemini AI")
    ]
    
    missing_deps = []
    for package, desc in dependencies:
        try:
            __import__(package)
            print(f"  ✅ {package}: 已安装")
        except ImportError:
            missing_deps.append(f"  - {package}: {desc}")
    
    if missing_deps:
        print(f"\n❌ 缺少以下依赖包:")
        for dep in missing_deps:
            print(dep)
        print("\n请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 依赖包检查通过")
    return True

def test_smtp_connection():
    """测试SMTP连接"""
    print("\n🔍 测试邮件SMTP连接...")
    
    try:
        from ..utils.email_sender import create_email_sender
        sender = create_email_sender()
        success, message = sender.test_connection()
        
        if success:
            print(f"  ✅ {message}")
            return True
        else:
            print(f"  ❌ {message}")
            return False
            
    except Exception as e:
        print(f"  ❌ SMTP连接测试失败: {e}")
        return False

def test_github_access():
    """测试GitHub API访问"""
    print("\n🔍 测试GitHub API访问...")
    
    try:
        from ..utils.github_release_manager import create_github_manager
        manager = create_github_manager()
        
        # 测试获取统计信息
        stats = manager.get_stats()
        print(f"  ✅ GitHub API连接成功")
        print(f"  📊 当前Release数量: {stats.get('total_releases', 0)}")
        
        # 检查token状态
        token_status = manager.get_token_expiry_status()
        if token_status.get('days_until_expiry'):
            days_left = token_status['days_until_expiry']
            if days_left <= 7:
                print(f"  ⚠️  Token将在 {days_left} 天后过期！")
            elif days_left <= 30:
                print(f"  📅 Token将在 {days_left} 天后过期")
            else:
                print(f"  ✅ Token状态良好 ({days_left} 天后过期)")
        else:
            print("  🔍 Token过期时间检测中...")
        
        return True
        
    except Exception as e:
        print(f"  ❌ GitHub API访问失败: {e}")
        return False

def test_package_creator():
    """测试内容包创建器"""
    print("\n🔍 测试内容包创建器...")
    
    try:
        from ..utils.package_creator import create_package_creator
        creator = create_package_creator()
        
        # 检查输出目录是否可创建
        output_dir = creator.output_dir
        if output_dir.exists() or output_dir.parent.exists():
            print(f"  ✅ 输出目录可用: {output_dir}")
            return True
        else:
            print(f"  ❌ 输出目录不可用: {output_dir}")
            return False
            
    except Exception as e:
        print(f"  ❌ 内容包创建器测试失败: {e}")
        return False

def test_wechat_footer():
    """测试WeChat页脚模板"""
    print("\n🔍 测试WeChat页脚模板...")
    
    template_path = Path(__file__).parent.parent / "config/templates/wechat_reward_footer.html"
    
    if template_path.exists():
        print(f"  ✅ 页脚模板文件存在: {template_path}")
        
        # 检查模板内容
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "获取完整深度版本" in content and "打赏本文任意金额" in content:
                print("  ✅ 页脚模板内容正确")
                return True
            else:
                print("  ❌ 页脚模板内容不完整")
                return False
    else:
        print(f"  ❌ 页脚模板文件不存在: {template_path}")
        return False

def test_system_integration():
    """测试系统整合"""
    print("\n🔍 测试系统整合...")
    
    try:
        from scripts.utils.reward_system_manager import RewardSystemManager
        manager = RewardSystemManager()
        
        # 获取系统统计
        stats = manager.get_system_stats()
        print("  ✅ 系统管理器初始化成功")
        print(f"  📊 系统状态: GitHub {stats['github_releases']['total_releases']} 个Release")
        return True
        
    except Exception as e:
        print(f"  ❌ 系统整合测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 微信内容变现系统 - 第一阶段功能测试\n")
    
    # 设置日志级别，减少噪音
    logging.basicConfig(level=logging.WARNING)
    
    tests = [
        ("环境配置", test_environment),
        ("依赖包", test_dependencies),
        ("SMTP连接", test_smtp_connection),
        ("GitHub API", test_github_access),
        ("内容包创建", test_package_creator),
        ("WeChat页脚", test_wechat_footer),
        ("系统整合", test_system_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n❌ {test_name}测试时发生异常: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 项通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统第一阶段功能准备就绪。")
        print("\n📋 下一步操作:")
        print("1. 确保所有必要的环境变量已正确配置")
        print("2. 测试完整工作流程:")
        print("   python scripts/reward_system_manager.py create _posts/2025-07-18-tesla-ai-empire-analysis.md")
        print("3. 开始使用微信发布功能，页脚会自动包含奖励说明")
    else:
        print(f"\n⚠️  有 {total - passed} 项测试未通过，请检查配置后重新测试。")
        
        if passed >= 4:  # 如果基础功能OK
            print("\n💡 部分功能已可用，可以尝试:")
            print("   python scripts/reward_system_manager.py stats")

if __name__ == "__main__":
    main()