#!/usr/bin/env python3
"""
安全检查脚本
检查代码库中的潜在敏感信息泄露
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Tuple

class SecurityChecker:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []
        
        # 敏感信息模式
        self.sensitive_patterns = {
            'access_codes': [
                r'ADMIN_\d{8}_[A-Z0-9]{6}',  # 管理员访问码
                r'VIP[1-4]_\d{8}_[A-Z0-9]{4,6}',  # 会员访问码
            ],
            'api_keys': [
                r'sk-[a-zA-Z0-9]{32,}',  # OpenAI API keys
                r'AIza[0-9A-Za-z_-]{35}',  # Google API keys
                r'ya29\.[0-9A-Za-z_-]+',  # Google OAuth tokens
            ],
            'passwords': [
                r'password\s*[:=]\s*["\'][^"\']{8,}["\']',
                r'passwd\s*[:=]\s*["\'][^"\']{8,}["\']',
            ],
            'secrets': [
                r'secret\s*[:=]\s*["\'][^"\']{16,}["\']',
                r'SECRET\s*[:=]\s*["\'][^"\']{16,}["\']',
            ]
        }
        
        # 应该忽略的文件和目录
        self.ignore_patterns = [
            r'\.git/',
            r'\.tmp/',
            r'__pycache__/',
            r'node_modules/',
            r'\.env\.example',
            r'security_check\.py',  # 忽略自己
            r'SECURITY\.md'  # 安全文档中的示例
        ]
    
    def should_ignore_file(self, file_path: str) -> bool:
        """检查文件是否应该被忽略"""
        for pattern in self.ignore_patterns:
            if re.search(pattern, file_path):
                return True
        return False
    
    def check_file(self, file_path: Path) -> List[Dict]:
        """检查单个文件"""
        if self.should_ignore_file(str(file_path)):
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"无法读取文件 {file_path}: {e}")
            return []
        
        issues = []
        lines = content.split('\n')
        
        for category, patterns in self.sensitive_patterns.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    matches = re.findall(pattern, line, re.IGNORECASE)
                    for match in matches:
                        issues.append({
                            'file': str(file_path),
                            'line': line_num,
                            'category': category,
                            'pattern': pattern,
                            'match': match,
                            'context': line.strip()
                        })
        
        return issues
    
    def scan_directory(self) -> List[Dict]:
        """扫描整个项目目录"""
        all_issues = []
        
        # 扫描常见文件类型
        file_extensions = ['.py', '.js', '.md', '.yml', '.yaml', '.json', '.txt', '.sh']
        
        for ext in file_extensions:
            for file_path in self.project_root.rglob(f'*{ext}'):
                if file_path.is_file():
                    issues = self.check_file(file_path)
                    all_issues.extend(issues)
        
        return all_issues
    
    def check_git_history(self) -> List[str]:
        """检查Git提交历史中的敏感信息"""
        issues = []
        
        try:
            # 检查最近10次提交的消息
            import subprocess
            result = subprocess.run(
                ['git', 'log', '--oneline', '-10'], 
                capture_output=True, 
                text=True, 
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                commit_messages = result.stdout
                
                for category, patterns in self.sensitive_patterns.items():
                    for pattern in patterns:
                        matches = re.findall(pattern, commit_messages, re.IGNORECASE)
                        if matches:
                            issues.append(f"Git提交历史中发现{category}: {matches}")
            
        except Exception as e:
            print(f"检查Git历史失败: {e}")
        
        return issues
    
    def generate_report(self) -> str:
        """生成安全检查报告"""
        print("🔍 开始安全检查...")
        
        # 扫描文件
        file_issues = self.scan_directory()
        
        # 检查Git历史
        git_issues = self.check_git_history()
        
        report = []
        report.append("=" * 60)
        report.append("🔒 安全检查报告")
        report.append("=" * 60)
        
        # 文件中的问题
        if file_issues:
            report.append(f"\n⚠️  在文件中发现 {len(file_issues)} 个潜在安全问题:")
            report.append("-" * 40)
            
            by_category = {}
            for issue in file_issues:
                category = issue['category']
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(issue)
            
            for category, issues in by_category.items():
                report.append(f"\n📋 {category.upper()}:")
                for issue in issues:
                    report.append(f"  📁 {issue['file']}:{issue['line']}")
                    report.append(f"     🔍 匹配: {issue['match']}")
                    report.append(f"     📄 上下文: {issue['context'][:80]}{'...' if len(issue['context']) > 80 else ''}")
                    report.append("")
        else:
            report.append("\n✅ 在代码文件中未发现敏感信息")
        
        # Git历史中的问题
        if git_issues:
            report.append(f"\n⚠️  在Git历史中发现 {len(git_issues)} 个潜在问题:")
            report.append("-" * 40)
            for issue in git_issues:
                report.append(f"  🔍 {issue}")
        else:
            report.append("\n✅ 在Git提交历史中未发现敏感信息")
        
        # 安全建议
        report.append("\n" + "=" * 60)
        report.append("💡 安全建议")
        report.append("=" * 60)
        
        if file_issues or git_issues:
            report.append("\n🚨 立即行动:")
            report.append("1. 立即更换所有发现的访问码/密钥")
            report.append("2. 从代码中移除敏感信息")
            report.append("3. 使用环境变量替代硬编码")
            report.append("4. 考虑清理Git历史记录")
            
            if git_issues:
                report.append("\n🔄 清理Git历史:")
                report.append("git filter-branch --msg-filter 'sed \"s/ADMIN_[0-9]*_[A-Z0-9]*/ADMIN_XXXXXX_XXXXXX/g\"' HEAD")
        else:
            report.append("\n🎉 太好了！未发现明显的安全问题")
            report.append("   建议定期运行此检查脚本")
        
        report.append("\n📋 最佳实践:")
        report.append("• 使用 .env 文件存储敏感配置")
        report.append("• 定期轮换访问码和API密钥")
        report.append("• 提交前运行安全检查")
        report.append("• 设置pre-commit钩子防止意外提交")
        
        return "\n".join(report)

def main():
    checker = SecurityChecker()
    report = checker.generate_report()
    print(report)
    
    # 保存报告
    report_file = Path(".tmp/security_report.txt")
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 详细报告已保存到: {report_file}")

if __name__ == '__main__':
    main()