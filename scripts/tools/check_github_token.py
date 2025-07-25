#!/usr/bin/env python3
"""
GitHub Token状态检查工具
用于验证和监控GitHub Personal Access Token的有效性和过期时间
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.append(str(Path(__file__).parent.parent))

# 配置日志
def setup_logging():
    """设置日志配置"""
    log_dir = Path(".build/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 只使用文件日志，避免与stdout/stderr混淆
    file_handler = logging.FileHandler(log_dir / "pipeline.log", encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - [GitHub Token检查] %(message)s'))
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    return logging.getLogger(__name__)

logger = setup_logging()

from utils.github_release_manager import create_github_manager


def main():
    """检查GitHub Token状态"""
    print("🔍 GitHub Token状态检查\n")
    logger.info("开始GitHub Token状态检查")
    
    try:
        manager = create_github_manager()
        
        # 获取token状态
        token_status = manager.get_token_expiry_status()
        
        print("📊 Token基本信息:")
        print(f"  • 用户: {manager.username}")
        print(f"  • 仓库: {manager.repo}")
        
        if token_status.get('last_checked'):
            checked_time = datetime.fromisoformat(token_status['last_checked'])
            print(f"  • 最后检查: {checked_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print("\n🕐 过期状态:")
        if token_status.get('days_until_expiry'):
            days_left = token_status['days_until_expiry']
            
            if days_left <= 0:
                print("  ❌ Token已过期！请立即更新")
                return False
            elif days_left <= 7:
                print(f"  ⚠️  Token将在 {days_left} 天后过期")
                print("  🚨 建议立即更新token以避免服务中断")
            elif days_left <= 14:
                print(f"  📅 Token将在 {days_left} 天后过期")
                print("  💡 建议提前更新token")
            elif days_left <= 30:
                print(f"  ✅ Token将在 {days_left} 天后过期")
                print("  📝 请计划在到期前更新")
            else:
                print(f"  ✅ Token状态良好，{days_left} 天后过期")
        else:
            print("  🔍 无法确定过期时间（可能是永久token或首次检测）")
        
        print("\n🔧 如何更新GitHub Token:")
        print("  1. 访问 https://github.com/settings/tokens")
        print("  2. 点击 'Generate new token' -> 'Generate new token (classic)'")
        print("  3. 设置相同的权限：repo (Contents)")
        print("  4. 选择过期时间（建议90天）")
        print("  5. 生成token并更新到 .env 文件中的 GITHUB_TOKEN")
        
        if token_status.get('needs_renewal'):
            print("\n⚠️  紧急提醒: Token即将过期，请尽快更新！")
            
        return True
        
    except ValueError as e:
        if "GitHub Token无效或已过期" in str(e):
            print("❌ GitHub Token无效或已过期！")
            print("\n🔧 解决方案:")
            print("  1. 检查 .env 文件中的 GITHUB_TOKEN 是否正确")
            print("  2. 确认token具有正确的权限（repo - Contents）")
            print("  3. 如果token已过期，请生成新的token")
            return False
        else:
            print(f"❌ 验证失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ 检查过程中发生错误: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)