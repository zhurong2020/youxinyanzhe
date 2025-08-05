#!/bin/bash
# 🔒 Fork 用户安全设置脚本
# 在使用fork的项目前必须运行此脚本

echo "🔒 开始安全配置..."

# 1. 复制环境变量模板
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ 已创建 .env 文件，请编辑填入您的配置"
else
    echo "⚠️  .env 文件已存在，请检查配置"
fi

# 2. 生成新的管理员访问码
echo "🔑 生成新的访问码..."
python scripts/admin_access_generator.py admin --purpose "fork_setup" --days 365

# 3. 生成测试访问码
python scripts/admin_access_generator.py test

# 4. 运行安全检查
echo "🔍 运行安全检查..."
python scripts/security_check.py

echo ""
echo "🎉 基础安全配置完成！"
echo ""
echo "📋 接下来请务必："
echo "1. 编辑 .env 文件，填入您自己的API密钥"
echo "2. 配置邮件服务器设置"
echo "3. 设置YouTube OAuth认证"
echo "4. 测试系统功能"
echo ""
echo "⚠️  重要：不要使用任何示例中的默认值！"
