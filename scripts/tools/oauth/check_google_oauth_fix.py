#!/usr/bin/env python3
"""
Google OAuth 403错误诊断和修复指导
"""

import json
from pathlib import Path

def diagnose_oauth_issue():
    """诊断OAuth 403错误"""
    print("🔍 Google OAuth 403错误诊断")
    print("=" * 50)
    
    # 检查凭据文件
    credentials_file = Path("config/youtube_oauth_credentials.json")
    
    if not credentials_file.exists():
        print("❌ OAuth凭据文件不存在")
        return
    
    try:
        with open(credentials_file, 'r') as f:
            creds = json.load(f)
        
        client_id = creds.get('installed', {}).get('client_id', '')
        project_id = creds.get('installed', {}).get('project_id', '')
        
        print("✅ OAuth凭据文件读取成功")
        print(f"   Project ID: {project_id}")
        print(f"   Client ID: {client_id}")
        
        if project_id == "workshop-youtube-uploader":
            print("✅ 项目ID配置正确")
        else:
            print(f"⚠️  项目ID不匹配，期望: workshop-youtube-uploader")
            
    except Exception as e:
        print(f"❌ 读取凭据文件失败: {e}")
        return
    
    print("\n🚨 403错误原因分析:")
    print("   Google应用处于'测试'状态，只有测试用户可以访问")
    
    print("\n🛠️  立即修复步骤:")
    print("1. 打开 Google Cloud Console:")
    print("   https://console.cloud.google.com/")
    
    print(f"\n2. 选择项目: {project_id}")
    
    print("\n3. 导航到 OAuth consent screen:")
    print("   左侧菜单 > APIs & Services > OAuth consent screen")
    
    print("\n4. 添加测试用户:")
    print("   滚动到页面底部 'Test users' 部分")
    print("   点击 '+ ADD USERS'")
    print("   添加邮箱: zhurong0525@gmail.com")
    print("   点击 'SAVE'")
    
    print("\n5. 立即重新测试:")
    print("   python youtube_upload.py")
    
    print("\n✅ 预期结果:")
    print("   - 浏览器能正常打开授权页面")
    print("   - 能选择 zhurong0525@gmail.com 账号")
    print("   - 成功完成授权")
    print("   - 看到: ✅ YouTube OAuth2认证成功")
    
    print("\n" + "=" * 50)
    print("💡 提示: 添加测试用户通常立即生效！")

def show_manual_steps():
    """显示手动操作步骤"""
    print("\n📋 详细手动操作步骤:")
    print("1. 浏览器打开: https://console.cloud.google.com/")
    print("2. 登录你的 Google 账号 (zhurong0525@gmail.com)")
    print("3. 选择项目: workshop-youtube-uploader")
    print("4. 左侧菜单 > APIs & Services > OAuth consent screen")
    print("5. 滚动到底部找到 'Test users' 部分")
    print("6. 点击 '+ ADD USERS' 按钮")
    print("7. 输入: zhurong0525@gmail.com")
    print("8. 点击 'SAVE' 保存")
    print("9. 返回终端运行: python youtube_upload.py")

def main():
    """主函数"""
    diagnose_oauth_issue()
    
    print("\n" + "=" * 50)
    choice = input("是否需要查看详细手动操作步骤？(y/N): ").strip().lower()
    
    if choice in ['y', 'yes']:
        show_manual_steps()
    
    print("\n🚀 修复完成后，就可以开始自动化YouTube上传了！")

if __name__ == "__main__":
    main()