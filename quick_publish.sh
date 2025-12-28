#!/bin/bash
# 快速发布pyobfus文章的脚本

echo "=================================="
echo "📝 准备发布文章"
echo "文章：别让你的Python代码'裸奔'了"
echo "=================================="

cd /home/wuxia/projects/youxinyanzhe

echo ""
echo "当前草稿文件："
ls -la _drafts/2025-12-27-protect-your-python-code-with-pyobfus.md

echo ""
echo "启动发布流程..."
echo "请按以下步骤操作："
echo "1. 选择 '1' - 智能内容发布"
echo "2. 选择 '1' - 发布新草稿"
echo "3. 选择您的文章进行发布"
echo ""

./venv/bin/python run.py