#!/usr/bin/env python3
"""
Git钩子设置脚本
设置预提交钩子以防止功能回归
"""

import os
import stat
from pathlib import Path

def setup_pre_commit_hook():
    """设置预提交钩子"""
    project_root = Path(__file__).parent.parent.parent.parent
    git_hooks_dir = project_root / ".git" / "hooks"
    pre_commit_file = git_hooks_dir / "pre-commit"
    
    # 检查.git目录是否存在
    if not git_hooks_dir.exists():
        print("❌ .git/hooks目录不存在，请确保在Git仓库中运行")
        return False
    
    # 预提交钩子内容
    hook_content = '''#!/bin/bash
# 功能回归检测预提交钩子
# 自动生成 - 请勿手动修改

echo "🔍 运行功能回归检测..."

# 切换到项目根目录
cd "$(git rev-parse --show-toplevel)"

# 运行功能回归测试
python scripts/tools/testing/function_regression_test.py --check

exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo "❌ 功能回归检测失败，提交被拒绝"
    echo "💡 发现的问题:"
    echo "   - 某些功能可能在重构过程中被破坏"
    echo "   - 检查修改的文件是否影响了现有功能"
    echo ""
    echo "🔧 解决方案:"
    echo "   1. 运行详细检测: python scripts/tools/testing/function_regression_test.py"
    echo "   2. 修复发现的问题"
    echo "   3. 更新基线(如需要): python scripts/tools/testing/function_regression_test.py --update-baseline"
    echo "   4. 重新提交"
    echo ""
    echo "⚠️ 如果确定这是预期的功能变更，请更新基线后重新提交"
    exit 1
fi

echo "✅ 功能回归检测通过"
echo ""
'''
    
    # 写入钩子文件
    try:
        with open(pre_commit_file, 'w', encoding='utf-8') as f:
            f.write(hook_content)
        
        # 设置可执行权限
        current_permissions = os.stat(pre_commit_file).st_mode
        os.chmod(pre_commit_file, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        print(f"✅ 预提交钩子已设置: {pre_commit_file}")
        return True
        
    except Exception as e:
        print(f"❌ 设置预提交钩子失败: {e}")
        return False

def setup_commit_msg_hook():
    """设置提交消息钩子，自动记录功能状态"""
    project_root = Path(__file__).parent.parent.parent.parent
    git_hooks_dir = project_root / ".git" / "hooks"
    commit_msg_file = git_hooks_dir / "commit-msg"
    
    hook_content = '''#!/bin/bash
# 提交消息增强钩子
# 自动添加功能状态信息

commit_msg_file="$1"

# 检查是否是功能相关的提交
if grep -qE "(feat|fix|refactor|merge)" "$commit_msg_file"; then
    echo "" >> "$commit_msg_file"
    echo "功能状态检查: $(date '+%Y-%m-%d %H:%M:%S')" >> "$commit_msg_file"
fi
'''
    
    try:
        with open(commit_msg_file, 'w', encoding='utf-8') as f:
            f.write(hook_content)
        
        # 设置可执行权限
        current_permissions = os.stat(commit_msg_file).st_mode
        os.chmod(commit_msg_file, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        print(f"✅ 提交消息钩子已设置: {commit_msg_file}")
        return True
        
    except Exception as e:
        print(f"❌ 设置提交消息钩子失败: {e}")
        return False

def main():
    print("🔧 设置Git钩子以防止功能回归...")
    
    success = True
    success &= setup_pre_commit_hook()
    success &= setup_commit_msg_hook()
    
    if success:
        print("\n🎉 Git钩子设置完成!")
        print("📝 说明:")
        print("  - 每次提交前会自动检测功能回归")
        print("  - 如果发现问题，提交会被拒绝")
        print("  - 可以通过更新基线来确认预期的功能变更")
        print("\n🔍 测试钩子:")
        print("  git commit --allow-empty -m 'test commit'")
    else:
        print("\n❌ 部分钩子设置失败，请检查权限和Git仓库状态")

if __name__ == "__main__":
    main()