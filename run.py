#!/usr/bin/env python
"""
内容处理流水线启动脚本
"""
import os
import sys
import argparse
import logging
from scripts.content_pipeline import ContentPipeline

# 禁用 tensorflow 警告
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# 禁用特定警告
logging.getLogger('absl').setLevel(logging.ERROR)

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    parser = argparse.ArgumentParser(description="内容处理流水线")
    parser.add_argument("-v", "--verbose", 
                       action="store_true",
                       help="显示详细日志")
    args = parser.parse_args()
    
    pipeline = ContentPipeline("config/pipeline_config.yml", verbose=args.verbose)
    
    # 选择操作
    print("\n请选择操作：")
    print("1. 处理现有草稿")
    print("2. 生成测试文章")
    
    choice = input("\n请输入选项 (1/2): ").strip()
    
    if choice == "1":
        # 处理现有草稿
        draft = pipeline.select_draft()
        if not draft:
            print("没有找到草稿文件或选择无效")
            return
    elif choice == "2":
        # 生成测试文章
        draft = pipeline.generate_test_content()
        if not draft:
            print("生成测试文章失败")
            return
    else:
        print("无效的选择")
        return
    
    # 选择发布平台
    platforms = pipeline.select_platforms()
    if not platforms:
        print("未选择任何发布平台")
        return
    
    # 处理并发布
    success = pipeline.process_draft(draft, platforms)
    if success:
        print("✅ 处理完成!")
    else:
        print("⚠️ 处理未完全成功，请检查日志")

if __name__ == "__main__":
    main() 