#!/usr/bin/env python3
"""
修复脚本导入路径问题
创建一个更健壮的路径解决方案
"""

import re
from pathlib import Path

def create_robust_path_solution() -> str:
    """创建健壮的路径解决方案代码"""
    return '''# 添加项目根目录到Python路径 - 健壮版本
import os
import sys
from pathlib import Path

def find_project_root():
    """查找项目根目录"""
    current = Path(__file__).resolve()
    
    # 向上查找直到找到包含特定标识文件的目录
    for parent in [current] + list(current.parents):
        if (parent / 'run.py').exists() and (parent / 'scripts').exists():
            return parent
    
    # 如果没找到，回退到基于文件位置的计算
    relative_path = Path(__file__).resolve()
    try:
        # 尝试基于当前工作目录计算
        if Path.cwd().name == 'youxinyanzhe':
            return Path.cwd()
        relative_to_cwd = relative_path.relative_to(Path.cwd())
        return Path.cwd()
    except ValueError:
        # 基于文件路径计算 (脚本直接运行的情况)
        parts_to_project = len(relative_path.relative_to(Path.cwd()).parts) - 1
        return relative_path.parents[parts_to_project - 1]

project_root = find_project_root()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))'''

def apply_robust_path_fix(file_path: Path) -> bool:
    """将健壮的路径解决方案应用到文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找现有的路径计算代码
        patterns = [
            r'# 添加项目.*?到Python路径.*?\nsys\.path\.[^)]+\)\)',
            r'project_root = Path\(__file__\)\.parent[.parent]*\nsys\.path\.[^)]+\)\)',
            r'sys\.path\.[^)]*Path\(__file__\)[^)]+\)\)',
        ]
        
        has_changes = False
        for pattern in patterns:
            if re.search(pattern, content, re.DOTALL):
                # 替换为健壮版本
                robust_solution = create_robust_path_solution()
                content = re.sub(pattern, robust_solution, content, flags=re.DOTALL)
                has_changes = True
                break
        
        if has_changes:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ 处理文件 {file_path} 时出错: {e}")
        return False

def main():
    """主函数"""
    print("🔧 升级为健壮的导入路径解决方案")
    print("=" * 50)
    
    # 关键的脚本文件，需要健壮的路径解决方案
    critical_files = [
        'scripts/tools/checks/check_github_token.py',
        'scripts/tools/checks/check_youtube_oauth.py',
        'scripts/tools/youtube/youtube_oauth_complete.py',
        'scripts/tools/youtube/youtube_oauth_manual.py',
    ]
    
    project_root = Path.cwd()
    files_to_fix = [project_root / f for f in critical_files if (project_root / f).exists()]
    
    print(f"📁 升级 {len(files_to_fix)} 个关键文件")
    print()
    
    fixed_count = 0
    
    for file_path in files_to_fix:
        print(f"🔧 升级: {file_path.relative_to(project_root)}")
        if apply_robust_path_fix(file_path):
            print(f"   ✅ 已升级为健壮路径解决方案")
            fixed_count += 1
        else:
            print(f"   ℹ️ 无需修改或未找到匹配模式")
    
    print()
    print(f"📊 升级完成: {fixed_count} 个文件")
    
    if fixed_count > 0:
        print("🎉 关键脚本已升级为健壮的路径解决方案！")
        print("💡 现在这些脚本应该能在各种环境下正常工作")

if __name__ == "__main__":
    main()