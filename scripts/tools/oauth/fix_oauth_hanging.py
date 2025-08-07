#!/usr/bin/env python3
"""
修复OAuth授权卡住问题
"""

import json
import subprocess
import time
from pathlib import Path

def check_oauth_redirect_config():
    """检查OAuth重定向配置"""
    print("🔍 检查OAuth重定向配置")
    print("=" * 50)
    
    credentials_file = Path("config/youtube_oauth_credentials.json")
    
    if not credentials_file.exists():
        print("❌ OAuth凭据文件不存在")
        return False
    
    try:
        with open(credentials_file, 'r') as f:
            creds = json.load(f)
        
        redirect_uris = creds.get('installed', {}).get('redirect_uris', [])
        print(f"当前重定向URI: {redirect_uris}")
        
        # 检查是否包含正确的重定向URI
        has_localhost = any('localhost' in uri for uri in redirect_uris)
        has_oob = any('oob' in uri for uri in redirect_uris)
        
        print(f"包含localhost: {'✅' if has_localhost else '❌'}")
        print(f"包含oob: {'✅' if has_oob else '❌'}")
        
        return has_localhost or has_oob
        
    except Exception as e:
        print(f"❌ 读取配置失败: {e}")
        return False

def fix_oauth_redirect():
    """修复OAuth重定向配置"""
    print("\n🛠️ 修复OAuth重定向配置")
    
    credentials_file = Path("config/youtube_oauth_credentials.json")
    
    try:
        with open(credentials_file, 'r') as f:
            creds = json.load(f)
        
        # 确保有正确的重定向URI
        correct_uris = [
            "urn:ietf:wg:oauth:2.0:oob",
            "http://localhost:8080",
            "http://localhost"
        ]
        
        creds['installed']['redirect_uris'] = correct_uris
        
        # 保存修复后的配置
        with open(credentials_file, 'w') as f:
            json.dump(creds, f, indent=2)
        
        print("✅ OAuth重定向配置已修复")
        print(f"新的重定向URI: {correct_uris}")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

def check_port_availability():
    """检查端口可用性"""
    print("\n🔍 检查端口状态")
    
    ports_to_check = [8080, 8081, 8082]
    
    for port in ports_to_check:
        try:
            result = subprocess.run(
                ['netstat', '-an'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            
            if f":{port}" in result.stdout:
                print(f"端口 {port}: ⚠️ 可能被占用")
            else:
                print(f"端口 {port}: ✅ 可用")
                
        except:
            print(f"端口 {port}: ❓ 无法检查")

def show_manual_auth_steps():
    """显示手动授权步骤"""
    print("\n📋 手动授权步骤")
    print("=" * 30)
    print("1. 在Google授权页面中，找到以下选项：")
    print("   - 查看权限列表")
    print("   - 应该看到：'管理您的YouTube视频'")
    print()
    print("2. 点击 '允许' 或 'Allow' 按钮")
    print()
    print("3. 如果页面没有响应，尝试：")
    print("   - 刷新页面")
    print("   - 重新点击允许")
    print("   - 检查是否有弹出窗口被阻止")
    print()
    print("4. 成功后应该看到：")
    print("   - '认证完成' 或类似信息")
    print("   - 或者页面跳转到 localhost")

def provide_workaround():
    """提供替代解决方案"""
    print("\n🔄 替代解决方案")
    print("=" * 30)
    print("如果OAuth授权持续卡住，可以：")
    print()
    print("1. 停止当前脚本 (Ctrl+C)")
    print("2. 删除可能损坏的token文件：")
    print("   rm config/youtube_oauth_token.json")
    print()
    print("3. 使用改进的OAuth流程重新尝试")
    print("4. 或者临时使用简化版本：")
    print("   python youtube_video_gen.py")

def main():
    """主函数"""
    print("🔧 OAuth授权卡住问题诊断")
    print("=" * 50)
    
    # 检查配置
    config_ok = check_oauth_redirect_config()
    
    if not config_ok:
        print("\n⚠️ 检测到配置问题，正在修复...")
        if fix_oauth_redirect():
            print("✅ 配置已修复，请重新运行 python youtube_upload.py")
        else:
            print("❌ 自动修复失败")
    
    # 检查端口
    check_port_availability()
    
    # 显示手动步骤
    show_manual_auth_steps()
    
    print("\n" + "=" * 50)
    print("💡 解决方案优先级：")
    print("1. 在Google页面点击 '允许/Allow' 按钮")
    print("2. 检查浏览器是否阻止弹出窗口")
    print("3. 如果配置已修复，重新运行脚本")
    print("4. 最后考虑使用简化版本")
    
    # 提供替代方案
    provide_workaround()

if __name__ == "__main__":
    main()