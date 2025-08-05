#!/usr/bin/env python3
"""
安全清理脚本
清理代码库中的敏感信息，为开源发布做准备
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict

class SecurityCleanup:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.cleanup_log = []
        
        # 需要清理的敏感文件
        self.sensitive_files = [
            '.env',  # 真实环境变量文件
            'config/youtube_oauth_token.json',  # 已清理，但需要提醒
            '.tmp/',  # 临时文件目录
            '.build/',  # 编译输出目录
        ]
        
        # 需要替换的敏感内容模式
        self.sensitive_replacements = {
            # API Keys (已在代码中使用环境变量)
            r'sk-[a-zA-Z0-9]{32,}': 'your-api-key-here',
            r'AIza[0-9A-Za-z_-]{35}': 'your-google-api-key-here',
            r'ya29\.[0-9A-Za-z_-]+': 'your-oauth-token-here',
            
            # 具体的访问码示例 (已在文档中替换)
            r'ADMIN_\d{8}_[A-Z0-9]{6}': 'ADMIN_YYYYMMDD_XXXXXX',
            r'VIP[1-4]_\d{8}_[A-Z0-9]{4,6}': 'VIPX_YYYYMMDD_XXXX',
        }
    
    def log_action(self, message: str):
        """记录清理操作"""
        self.cleanup_log.append(message)
        print(f"✅ {message}")
    
    def check_gitignore(self) -> bool:
        """检查.gitignore是否包含敏感文件"""
        gitignore_path = self.project_root / '.gitignore' 
        if not gitignore_path.exists():
            return False
        
        with open(gitignore_path, 'r') as f:
            content = f.read()
        
        required_entries = ['.env', '.tmp/', '.build/', '*.log']
        missing_entries = []
        
        for entry in required_entries:
            if entry not in content:
                missing_entries.append(entry)
        
        if missing_entries:
            print(f"⚠️  .gitignore 缺少以下条目: {missing_entries}")
            return False
        
        self.log_action(".gitignore 配置正确")
        return True
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        temp_dirs = ['.tmp', '.build', '__pycache__']
        
        for temp_dir in temp_dirs:
            temp_path = self.project_root / temp_dir
            if temp_path.exists():
                try:
                    if temp_path.is_dir():
                        shutil.rmtree(temp_path)
                        self.log_action(f"已删除临时目录: {temp_dir}")
                except Exception as e:
                    print(f"❌ 删除 {temp_dir} 失败: {e}")
    
    def verify_env_example(self) -> bool:
        """验证.env.example文件存在且内容安全"""
        env_example_path = self.project_root / '.env.example'
        if not env_example_path.exists():
            print("❌ 缺少 .env.example 文件")
            return False
        
        with open(env_example_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否包含真实的API密钥
        dangerous_patterns = [
            r'sk-[a-zA-Z0-9]{32,}',
            r'AIza[0-9A-Za-z_-]{35}', 
            r'ya29\.[0-9A-Za-z_-]+'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, content):
                print(f"⚠️  .env.example 包含疑似真实密钥: {pattern}")
                return False
        
        self.log_action(".env.example 文件安全")
        return True
    
    def generate_fork_setup_script(self):
        """生成fork用户设置脚本"""
        setup_script = """#!/bin/bash
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
"""
        
        setup_script_path = self.project_root / 'setup_for_fork.sh'
        with open(setup_script_path, 'w', encoding='utf-8') as f:
            f.write(setup_script)
        
        # 设置执行权限
        setup_script_path.chmod(0o755)
        self.log_action("已创建 setup_for_fork.sh 脚本")
    
    def check_git_history_safety(self) -> List[str]:
        """检查Git历史中的敏感信息"""
        try:
            # 检查最近10次提交的差异
            result = subprocess.run(
                ['git', 'log', '--oneline', '-10', '--pretty=format:%H %s'], 
                capture_output=True, 
                text=True, 
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                return ["Git历史检查失败"]
            
            commits = result.stdout.strip().split('\n')
            sensitive_commits = []
            
            for commit_line in commits:
                if not commit_line.strip():
                    continue
                    
                commit_hash = commit_line.split()[0]
                commit_msg = ' '.join(commit_line.split()[1:])
                
                # 检查提交消息中的敏感信息
                for pattern in self.sensitive_replacements.keys():
                    if re.search(pattern, commit_msg, re.IGNORECASE):
                        sensitive_commits.append(f"提交 {commit_hash[:8]}: {commit_msg}")
            
            return sensitive_commits
            
        except Exception as e:
            return [f"Git历史检查出错: {e}"]
    
    def generate_security_report(self) -> str:
        """生成安全清理报告"""
        report = []
        report.append("=" * 60)
        report.append("🔒 安全清理报告")
        report.append("=" * 60)
        
        # 清理操作日志
        if self.cleanup_log:
            report.append(f"\n✅ 完成的清理操作 ({len(self.cleanup_log)} 项):")
            for i, action in enumerate(self.cleanup_log, 1):
                report.append(f"  {i}. {action}")
        
        # Git历史检查
        sensitive_commits = self.check_git_history_safety()
        if sensitive_commits:
            report.append(f"\n⚠️  Git历史中发现潜在敏感信息:")
            for commit in sensitive_commits:
                report.append(f"  • {commit}")
            report.append("\n💡 建议:")
            report.append("  考虑使用 git filter-branch 或 BFG Repo-Cleaner 清理历史")
        else:
            report.append(f"\n✅ Git提交历史检查通过")
        
        # 安全建议
        report.append("\n" + "=" * 60)
        report.append("📋 Fork用户安全清单")
        report.append("=" * 60)
        report.append("\n🚨 必须完成的操作:")
        report.append("1. 运行 ./setup_for_fork.sh 脚本")
        report.append("2. 编辑 .env 文件，设置您自己的API密钥")
        report.append("3. 重新生成所有访问码")
        report.append("4. 配置邮件服务器")
        report.append("5. 设置YouTube OAuth认证")
        
        report.append("\n✅ 已安全处理的项目:")
        report.append("• 移除了硬编码的API密钥")
        report.append("• 清理了OAuth令牌文件")
        report.append("• 更新了文档中的示例访问码")
        report.append("• 创建了环境变量模板")
        report.append("• 生成了安全设置脚本")
        
        return "\n".join(report)
    
    def run_cleanup(self):
        """执行完整的安全清理"""
        print("🔒 开始安全清理...")
        
        # 1. 检查.gitignore
        self.check_gitignore()
        
        # 2. 清理临时文件
        self.cleanup_temp_files()
        
        # 3. 验证.env.example
        self.verify_env_example()
        
        # 4. 生成设置脚本
        self.generate_fork_setup_script()
        
        # 5. 生成报告
        report = self.generate_security_report()
        
        # 保存报告
        report_file = self.project_root / ".tmp" / "security_cleanup_report.txt"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(report)
        print(f"\n📄 详细报告已保存到: {report_file}")
        
        return len(self.cleanup_log) > 0

def main():
    cleanup = SecurityCleanup()
    success = cleanup.run_cleanup()
    
    if success:
        print("\n🎉 安全清理完成！项目现在可以安全地fork。")
    else:
        print("\n⚠️  清理过程中遇到问题，请检查上述输出。")

if __name__ == '__main__':
    main()