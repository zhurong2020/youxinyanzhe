#!/usr/bin/env python3
"""
功能回归测试器
防止重构过程中的功能退化，确保所有功能的完整性
"""

import json
import sys
import re
import ast
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import argparse

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

class FunctionStatusDetector:
    def __init__(self, mapping_file: str = "config/function_mapping.json"):
        self.project_root = project_root
        self.mapping_file = self.project_root / mapping_file
        self.mapping = self.load_mapping()
        self.baseline_file = self.project_root / "config/function_baseline.json"
    
    def load_mapping(self) -> Dict:
        """加载功能映射配置"""
        try:
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ 功能映射文件不存在: {self.mapping_file}")
            return {"function_mapping": {"categories": {}}}
        except json.JSONDecodeError as e:
            print(f"❌ 功能映射文件格式错误: {e}")
            return {"function_mapping": {"categories": {}}}
    
    def detect_all_functions(self) -> Dict[str, Dict]:
        """检测所有功能的实际状态"""
        print("🔍 开始功能状态检测...")
        results = {}
        
        mapping = self.mapping.get("function_mapping", {})
        categories = mapping.get("categories", {})
        
        for category_id, category_info in categories.items():
            print(f"\n📂 检测分类: {category_info.get('display_name', category_id)}")
            
            functions = category_info.get("functions", {})
            for func_id, func_info in functions.items():
                full_func_id = f"{category_id}.{func_id}"
                print(f"  🔍 检测功能: {func_info.get('display_name', func_id)}")
                
                status_result = self.check_function_status(func_info)
                results[full_func_id] = {
                    "status": status_result["status"],
                    "details": status_result,
                    "display_name": func_info.get("display_name", func_id),
                    "last_checked": datetime.now().isoformat()
                }
                
                # 显示检测结果
                status_icon = self.get_status_icon(status_result["status"])
                print(f"    {status_icon} {status_result['status']}")
                
                if status_result.get("issues"):
                    for issue in status_result["issues"]:
                        print(f"      ⚠️ {issue}")
        
        return results
    
    def check_function_status(self, func_info: Dict) -> Dict[str, Any]:
        """检测单个功能状态"""
        issues = []
        
        # 1. 检查菜单方法是否存在且非占位符
        menu_status, menu_issues = self.check_menu_implementation(func_info)
        issues.extend(menu_issues)
        
        # 2. 检查核心实现是否可导入和调用
        impl_status, impl_issues = self.check_core_implementation(func_info)
        issues.extend(impl_issues)
        
        # 3. 检查依赖是否满足
        deps_status, deps_issues = self.check_dependencies(func_info)
        issues.extend(deps_issues)
        
        # 确定总体状态
        if all([menu_status, impl_status, deps_status]):
            status = "active"
        elif impl_status and deps_status:
            status = "implementation_ready"  # 实现就绪但菜单未集成
        elif menu_status:
            status = "menu_only"  # 菜单存在但实现缺失
        else:
            status = "incomplete"
        
        return {
            "status": status,
            "menu_ok": menu_status,
            "implementation_ok": impl_status,
            "dependencies_ok": deps_status,
            "issues": issues
        }
    
    def check_menu_implementation(self, func_info: Dict) -> Tuple[bool, List[str]]:
        """检查菜单实现状态"""
        issues = []
        
        menu_path = func_info.get("menu_path")
        menu_method = func_info.get("menu_method")
        
        if not menu_path or not menu_method:
            issues.append("菜单路径或方法名未配置")
            return False, issues
        
        menu_file = self.project_root / menu_path
        if not menu_file.exists():
            issues.append(f"菜单文件不存在: {menu_path}")
            return False, issues
        
        # 读取菜单文件内容
        try:
            with open(menu_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            issues.append(f"无法读取菜单文件: {e}")
            return False, issues
        
        # 检查方法是否存在
        method_pattern = rf"def {re.escape(menu_method)}\s*\("
        if not re.search(method_pattern, content):
            issues.append(f"菜单方法不存在: {menu_method}")
            return False, issues
        
        # 检查是否是占位符实现
        placeholder_patterns = self.mapping.get("function_mapping", {}).get("placeholders", {}).get("patterns", [])
        
        # 提取方法内容
        method_content = self.extract_method_content(content, menu_method)
        if method_content:
            for pattern in placeholder_patterns:
                if pattern in method_content:
                    issues.append(f"检测到占位符代码: {pattern}")
                    return False, issues
        
        return True, issues
    
    def extract_method_content(self, content: str, method_name: str) -> str:
        """提取方法的内容"""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == method_name:
                    # 获取方法在源码中的行号范围
                    start_line = node.lineno
                    end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 10
                    
                    lines = content.split('\n')
                    if start_line <= len(lines):
                        method_lines = lines[start_line-1:end_line]
                        return '\n'.join(method_lines)
        except:
            # 如果AST解析失败，使用简单的文本匹配
            lines = content.split('\n')
            in_method = False
            method_lines = []
            indent_level = None
            
            for line in lines:
                if f"def {method_name}(" in line:
                    in_method = True
                    indent_level = len(line) - len(line.lstrip())
                    method_lines.append(line)
                elif in_method:
                    if line.strip() == "":
                        method_lines.append(line)
                    elif len(line) - len(line.lstrip()) <= indent_level and line.strip(): # type: ignore
                        # 遇到同级或更高级的代码，方法结束
                        break
                    else:
                        method_lines.append(line)
            
            return '\n'.join(method_lines)
        
        return ""
    
    def check_core_implementation(self, func_info: Dict) -> Tuple[bool, List[str]]:
        """检查核心实现状态"""
        issues = []
        
        core_impl = func_info.get("core_implementation")
        test_command = func_info.get("test_command")
        
        if not core_impl:
            issues.append("核心实现路径未配置")
            return False, issues
        
        # 解析实现路径 (format: path/to/file.py:ClassName.method_name)
        if ":" in core_impl:
            file_path, class_method = core_impl.split(":", 1)
        else:
            file_path = core_impl
            class_method = None
        
        impl_file = self.project_root / file_path
        if not impl_file.exists():
            issues.append(f"实现文件不存在: {file_path}")
            return False, issues
        
        # 检查是否可以导入
        if test_command:
            try:
                # 在受限环境中执行测试命令
                local_vars = {}
                exec(test_command, {"__builtins__": __builtins__}, local_vars)
                return True, issues
            except ImportError as e:
                issues.append(f"导入失败: {e}")
                return False, issues
            except Exception as e:
                issues.append(f"测试命令执行失败: {e}")
                return False, issues
        
        # 如果没有测试命令，只检查文件存在性
        return True, issues
    
    def check_dependencies(self, func_info: Dict) -> Tuple[bool, List[str]]:
        """检查依赖项状态"""
        issues = []
        
        dependencies = func_info.get("dependencies", [])
        if not dependencies:
            return True, issues
        
        critical_deps = self.mapping.get("function_mapping", {}).get("critical_dependencies", {})
        
        for dep in dependencies:
            if dep in critical_deps:
                dep_info = critical_deps[dep]
                check_command = dep_info.get("check_command")
                
                if check_command:
                    try:
                        exec(check_command)
                    except ImportError:
                        issues.append(f"依赖缺失: {dep} - {dep_info.get('description', '')}")
                        return False, issues
                    except Exception as e:
                        issues.append(f"依赖检查失败: {dep} - {e}")
                        return False, issues
        
        return True, issues
    
    def get_status_icon(self, status: str) -> str:
        """获取状态图标"""
        icons = {
            "active": "✅",
            "implementation_ready": "🟡",
            "menu_only": "🟠", 
            "incomplete": "❌"
        }
        return icons.get(status, "❓")
    
    def create_baseline(self, output_file: Optional[str] = None) -> str:
        """创建功能状态基线"""
        print("📊 创建功能状态基线...")
        
        current_status = self.detect_all_functions()
        
        baseline_data = {
            "created_at": datetime.now().isoformat(),
            "version": self.mapping.get("function_mapping", {}).get("version", "unknown"),
            "total_functions": len(current_status),
            "status_summary": self.get_status_summary(current_status),
            "functions": current_status
        }
        
        output_path = output_file or self.baseline_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(baseline_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 功能基线已保存: {output_path}")
        self.print_status_summary(baseline_data["status_summary"])
        
        return str(output_path)
    
    def check_regression(self) -> bool:
        """检查功能回归"""
        print("🔍 检查功能回归...")
        
        if not self.baseline_file.exists():
            print("❌ 基线文件不存在，请先创建基线")
            print("💡 运行: python scripts/tools/testing/function_regression_test.py --create-baseline")
            return False
        
        # 加载基线
        with open(self.baseline_file, 'r', encoding='utf-8') as f:
            baseline_data = json.load(f)
        
        baseline_status = {k: v["status"] for k, v in baseline_data["functions"].items()}
        
        # 检测当前状态
        current_status = self.detect_all_functions()
        current_status_simple = {k: v["status"] for k, v in current_status.items()}
        
        # 发现回归
        regressions = self.find_regressions(baseline_status, current_status_simple)
        
        if regressions:
            print(f"\n❌ 发现 {len(regressions)} 个功能回归:")
            for regression in regressions:
                print(f"  🔴 {regression['function']}: {regression['from']} → {regression['to']}")
                print(f"     {regression.get('description', '')}")
            return False
        else:
            print("\n✅ 未发现功能回归")
            return True
    
    def find_regressions(self, baseline: Dict[str, str], current: Dict[str, str]) -> List[Dict]:
        """发现功能退化"""
        regressions = []
        
        # 定义状态优先级
        status_priority = {
            "active": 4,
            "implementation_ready": 3,
            "menu_only": 2,
            "incomplete": 1,
            "missing": 0
        }
        
        for func_id, baseline_status in baseline.items():
            current_status = current.get(func_id, "missing")
            
            if status_priority[current_status] < status_priority[baseline_status]:
                severity = "high" if baseline_status == "active" else "medium"
                regressions.append({
                    "function": func_id,
                    "from": baseline_status,
                    "to": current_status,
                    "severity": severity,
                    "description": f"功能从 {baseline_status} 退化为 {current_status}"
                })
        
        # 检查新增的incomplete功能
        for func_id, current_status in current.items():
            if func_id not in baseline and current_status == "incomplete":
                regressions.append({
                    "function": func_id,
                    "from": "new",
                    "to": current_status,
                    "severity": "low",
                    "description": f"新功能添加但状态为 {current_status}"
                })
        
        return regressions
    
    def get_status_summary(self, status_data: Dict) -> Dict[str, int]:
        """获取状态汇总"""
        summary = {}
        for func_data in status_data.values():
            status = func_data["status"]
            summary[status] = summary.get(status, 0) + 1
        return summary
    
    def print_status_summary(self, summary: Dict[str, int]):
        """打印状态汇总"""
        print(f"\n📊 功能状态汇总:")
        total = sum(summary.values())
        for status, count in summary.items():
            icon = self.get_status_icon(status)
            percentage = (count / total * 100) if total > 0 else 0
            print(f"  {icon} {status}: {count} ({percentage:.1f}%)")
        print(f"  📋 总计: {total} 个功能")
    
    def update_baseline(self) -> bool:
        """更新基线"""
        print("📊 更新功能状态基线...")
        self.create_baseline()
        return True


def main():
    parser = argparse.ArgumentParser(description='功能回归测试器')
    parser.add_argument('--create-baseline', action='store_true', help='创建功能状态基线')
    parser.add_argument('--check', action='store_true', help='检查功能回归')
    parser.add_argument('--update-baseline', action='store_true', help='更新基线')
    parser.add_argument('--output', type=str, help='输出文件路径')
    
    args = parser.parse_args()
    
    detector = FunctionStatusDetector()
    
    if args.create_baseline:
        detector.create_baseline(args.output)
    elif args.check:
        success = detector.check_regression()
        sys.exit(0 if success else 1)
    elif args.update_baseline:
        detector.update_baseline()
    else:
        # 默认行为：检测所有功能状态
        current_status = detector.detect_all_functions()
        summary = detector.get_status_summary(current_status)
        detector.print_status_summary(summary)


if __name__ == "__main__":
    main()