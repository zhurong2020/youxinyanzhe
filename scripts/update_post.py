#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import shutil
from pathlib import Path
import argparse
import subprocess
import re

def setup_argparse():
    """设置命令行参数"""
    parser = argparse.ArgumentParser(description='更新已发布的文章')
    parser.add_argument('post_name', help='文章名称，例如：2025-02-18-shenshi-newspoint')
    parser.add_argument('--mode', choices=['direct', 'pipeline'], default='direct',
                      help='更新模式：direct=直接编辑并提交，pipeline=使用完整处理流程')
    parser.add_argument('--message', '-m', default='Update post',
                      help='Git提交信息')
    return parser.parse_args()

def find_post_file(post_name):
    """查找文章文件"""
    # 检查是否包含完整的日期前缀
    if not re.match(r'^\d{4}-\d{2}-\d{2}-', post_name):
        print("警告: 文章名称应包含日期前缀 (YYYY-MM-DD-)")
        # 尝试查找匹配的文件
        posts_dir = Path('_posts')
        matching_files = list(posts_dir.glob(f'*{post_name}*.md'))
        if matching_files:
            print(f"找到可能匹配的文件:")
            for i, file in enumerate(matching_files):
                print(f"  {i+1}. {file.name}")
            choice = input("请选择文件编号 (或按Enter取消): ")
            if choice and choice.isdigit() and 1 <= int(choice) <= len(matching_files):
                return matching_files[int(choice)-1]
            else:
                print("已取消操作")
                sys.exit(1)
        else:
            print(f"错误: 未找到匹配 '{post_name}' 的文件")
            sys.exit(1)
    
    # 检查文件扩展名
    if not post_name.endswith('.md'):
        post_name += '.md'
    
    # 查找发布的文章
    post_path = Path('_posts') / post_name
    if not post_path.exists():
        print(f"错误: 未找到文章 '{post_path}'")
        sys.exit(1)
    
    return post_path

def direct_update(post_path, commit_message):
    """直接更新文章并提交到Git"""
    print(f"准备更新文章: {post_path}")
    
    # 打开编辑器编辑文件
    editor = os.environ.get('EDITOR', 'notepad.exe' if os.name == 'nt' else 'nano')
    try:
        subprocess.run([editor, str(post_path)], check=True)
    except subprocess.CalledProcessError:
        print("编辑器启动失败，请手动编辑文件后继续")
        input("编辑完成后按Enter继续...")
    
    # 提交更改
    try:
        # 检查是否有更改
        status = subprocess.run(
            ["git", "status", "--porcelain", str(post_path)],
            capture_output=True,
            text=True
        ).stdout.strip()
        
        if not status:
            print("文件未更改，无需提交")
            return
        
        # 添加文件
        subprocess.run(["git", "add", str(post_path)], check=True)
        
        # 提交更改
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # 推送更改
        subprocess.run(["git", "push"], check=True)
        
        print(f"✅ 文章已更新并推送到GitHub")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git操作失败: {e}")
        sys.exit(1)

def pipeline_update(post_path):
    """使用完整处理流程更新文章"""
    print(f"准备使用处理流程更新文章: {post_path}")
    
    # 获取文件名
    post_name = post_path.name
    
    # 检查归档文件是否存在
    archived_path = Path('_drafts/archived') / post_name
    draft_path = Path('_drafts') / post_name
    
    if not archived_path.exists():
        print(f"警告: 未找到归档文件 '{archived_path}'")
        # 创建草稿文件
        print(f"正在创建草稿文件: {draft_path}")
        shutil.copy2(post_path, draft_path)
    else:
        # 移动归档文件到草稿目录
        print(f"正在恢复归档文件: {archived_path} -> {draft_path}")
        shutil.copy2(archived_path, draft_path)
    
    # 删除已发布的文件
    print(f"正在删除已发布的文件: {post_path}")
    post_path.unlink()
    
    # 运行处理流程
    print("正在启动处理流程...")
    try:
        subprocess.run(["python", "run.py"], check=True)
        print(f"✅ 文章已通过处理流程更新")
    except subprocess.CalledProcessError as e:
        print(f"❌ 处理流程失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    args = setup_argparse()
    
    # 查找文章文件
    post_path = find_post_file(args.post_name)
    
    # 根据模式更新文章
    if args.mode == 'direct':
        direct_update(post_path, args.message)
    else:
        pipeline_update(post_path)

if __name__ == "__main__":
    main() 