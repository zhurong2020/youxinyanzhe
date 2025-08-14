#!/usr/bin/env python3
"""
智能路径解析器
提供健壮的项目根目录查找功能，适用于各种运行环境
"""

import os
import sys
from pathlib import Path
from typing import Optional


def find_project_root(start_path: Optional[Path] = None) -> Path:
    """
    智能查找项目根目录
    
    Args:
        start_path: 起始路径，默认为当前脚本路径
    
    Returns:
        项目根目录的Path对象
    """
    if start_path is None:
        # 获取调用者的文件路径
        import inspect
        frame = inspect.currentframe().f_back
        caller_file = frame.f_globals.get('__file__')
        if caller_file:
            start_path = Path(caller_file).resolve()
        else:
            start_path = Path.cwd()
    
    current = Path(start_path).resolve()
    
    # 项目标识文件/目录
    project_markers = [
        'run.py',           # 主程序文件
        'scripts',          # 脚本目录
        '.git',             # Git仓库
        'CLAUDE.md',        # 项目说明文件
        'requirements.txt'  # 依赖文件
    ]
    
    # 向上查找直到找到包含项目标识的目录
    for path in [current] + list(current.parents):
        if any((path / marker).exists() for marker in project_markers):
            # 额外验证：确保这确实是我们的项目
            if (path / 'run.py').exists() and (path / 'scripts').exists():
                return path
    
    # 如果没找到，使用当前工作目录作为后备
    if (Path.cwd() / 'run.py').exists():
        return Path.cwd()
    
    # 最后的后备方案：基于脚本路径推测
    if start_path.is_file():
        # 计算脚本相对于预期项目结构的位置
        try:
            parts = start_path.parts
            if 'scripts' in parts:
                scripts_index = parts.index('scripts')
                project_root = Path(*parts[:scripts_index])
                if (project_root / 'run.py').exists():
                    return project_root
        except:
            pass
    
    # 如果所有方法都失败，返回当前工作目录
    return Path.cwd()


def setup_project_imports(script_file: str = None) -> Path:
    """
    设置项目导入路径
    
    Args:
        script_file: 脚本文件路径（通常是 __file__）
    
    Returns:
        项目根目录路径
    """
    if script_file:
        project_root = find_project_root(Path(script_file))
    else:
        project_root = find_project_root()
    
    # 添加到 Python 路径（如果还没有）
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    
    return project_root


def get_relative_path(file_path: Path, base_path: Path = None) -> Path:
    """
    获取相对于项目根目录的路径
    
    Args:
        file_path: 文件路径
        base_path: 基准路径，默认为项目根目录
    
    Returns:
        相对路径
    """
    if base_path is None:
        base_path = find_project_root()
    
    try:
        return file_path.relative_to(base_path)
    except ValueError:
        # 如果文件不在项目目录内，返回绝对路径
        return file_path.resolve()


# 便捷函数
def project_root() -> Path:
    """获取项目根目录"""
    return find_project_root()


def ensure_imports() -> Path:
    """确保项目导入路径已设置"""
    return setup_project_imports()


if __name__ == "__main__":
    # 测试功能
    print("🔍 路径解析器测试")
    print("=" * 40)
    
    root = find_project_root()
    print(f"项目根目录: {root}")
    print(f"run.py 存在: {(root / 'run.py').exists()}")
    print(f"scripts 目录存在: {(root / 'scripts').exists()}")
    
    # 测试导入设置
    setup_project_imports(__file__)
    print(f"Python 路径已设置: {str(root) in sys.path}")
    
    # 测试导入
    try:
        from scripts.utils.github_release_manager import create_github_manager
        print("✅ 测试导入成功!")
    except ImportError as e:
        print(f"❌ 测试导入失败: {e}")