#!/usr/bin/env python3
"""
检查项目中所有脚本的路径计算是否正确
用于发现重构后可能的路径指向问题
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any

def analyze_path_calculation(file_path: Path) -> Dict[str, Any]:
    """分析单个文件的路径计算"""
    result = {
        'file': str(file_path),
        'relative_to_project': str(file_path.relative_to(Path.cwd())),
        'expected_parent_count': 0,
        'found_patterns': [],
        'issues': [],
        'status': 'unknown'
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 计算文件到项目根目录需要多少个.parent
        relative_path = file_path.relative_to(Path.cwd())
        expected_parent_count = len(relative_path.parts) - 1
        result['expected_parent_count'] = expected_parent_count
        
        # 查找各种路径计算模式
        patterns = [
            (r'project_root\s*=\s*Path\(__file__\)((?:\.parent)*)', 'project_root_assignment'),
            (r'sys\.path\.(?:append|insert)\(.*?Path\(__file__\)((?:\.parent)*)', 'sys_path_append'),
            (r'Path\(__file__\)((?:\.parent)*)', 'general_path_calculation'),
        ]
        
        for pattern, pattern_type in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                parent_count = match.count('.parent') if match else 0
                result['found_patterns'].append({
                    'type': pattern_type,
                    'parent_count': parent_count,
                    'match': match
                })
                
                # 检查路径计算是否正确
                if pattern_type in ['project_root_assignment', 'sys_path_append']:
                    if parent_count != expected_parent_count:
                        result['issues'].append({
                            'type': 'incorrect_parent_count',
                            'expected': expected_parent_count,
                            'found': parent_count,
                            'pattern_type': pattern_type
                        })
        
        # 确定状态
        if result['issues']:
            result['status'] = 'has_issues'
        elif result['found_patterns']:
            result['status'] = 'correct'
        else:
            result['status'] = 'no_path_calculation'
            
    except Exception as e:
        result['issues'].append({
            'type': 'read_error',
            'error': str(e)
        })
        result['status'] = 'error'
    
    return result

def test_import_capability(file_path: Path) -> Dict[str, Any]:
    """测试文件的导入能力"""
    result = {
        'can_import': False,
        'import_error': None,
        'test_import': None
    }
    
    try:
        # 尝试测试导入（基本验证）
        relative_path = file_path.relative_to(Path.cwd())
        
        # 检查是否是可执行脚本
        if relative_path.suffix == '.py':
            # 模拟从项目根目录运行
            old_cwd = os.getcwd()
            try:
                # 确保在项目根目录
                project_root = Path.cwd()
                
                # 构建相对模块路径
                module_parts = list(relative_path.parts[:-1]) + [relative_path.stem]
                module_path = '.'.join(module_parts)
                
                # 简单语法检查（不实际导入，避免副作用）
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查基本语法
                try:
                    compile(content, str(file_path), 'exec')
                    result['can_import'] = True
                    result['test_import'] = 'syntax_ok'
                except SyntaxError as e:
                    result['import_error'] = f"Syntax error: {e}"
                    result['test_import'] = 'syntax_error'
                    
            finally:
                os.chdir(old_cwd)
                
    except Exception as e:
        result['import_error'] = str(e)
        result['test_import'] = 'test_failed'
    
    return result

def main():
    """主检查函数"""
    print("🔍 检查项目中所有脚本的路径计算")
    print("=" * 60)
    
    # 获取所有相关文件
    project_root = Path.cwd()
    files_with_path_calc = [
        project_root / f for f in [
            'scripts/tools/checks/check_youtube_oauth.py',
            'scripts/tools/checks/check_github_token.py',
            'scripts/tools/youtube/youtube_oauth_complete.py',
            'scripts/tools/youtube/youtube_oauth_manual.py',
            'scripts/tools/oauth/restore_youtube_oauth.py',
            'scripts/core/content_pipeline.py',
            'scripts/tools/cleanup_onedrive_cloud.py',
            'scripts/tools/onedrive_date_downloader.py',
            'scripts/tools/content/format_draft.py',
            'scripts/tools/content/topic_inspiration_generator.py',
            'scripts/tools/youtube/youtube_single_upload.py',
            'scripts/tools/youtube/youtube_upload.py',
            'scripts/tools/youtube/upload_single.py',
            'scripts/tools/youtube/youtube_video_gen.py',
            'scripts/tools/testing/test_reward_system.py',
            'scripts/tools/create_valid_token.py',
            'scripts/tools/oauth/generate_oauth_token.py',
            'scripts/utils/package_creator.py',
            'scripts/utils/audio_link_replacer.py',
            'scripts/tools/elevenlabs/elevenlabs_voice_test.py',
            'scripts/tools/elevenlabs/elevenlabs_pro_setup.py',
            'scripts/tools/elevenlabs/elevenlabs_voice_manager.py',
            'scripts/tools/youtube/youtube_upload_tester.py',
            'scripts/utils/youtube_link_mapper.py',
            'scripts/tools/youtube/youtube_video_generator.py',
            'scripts/utils/reward_system_manager.py',
            'scripts/tools/patched_podcastfy.py',
            'scripts/tools/testing/test_podcastfy_api.py',
            'scripts/tools/verify_gemini_model.py',
            'scripts/tools/testing/test_content_generation.py',
            'scripts/tools/elevenlabs/test_dual_voice_podcast.py',
            'scripts/tools/regenerate_youtube_article.py',
            'scripts/tools/debug_podcastfy.py',
            'scripts/tools/simple_test.py',
            'scripts/core/wechat_publisher.py'
        ] if (project_root / f).exists()
    ]
    
    print(f"📁 找到 {len(files_with_path_calc)} 个包含路径计算的文件")
    print()
    
    # 分析结果
    results = []
    issues_found = []
    
    for file_path in files_with_path_calc:
        analysis = analyze_path_calculation(file_path)
        results.append(analysis)
        
        if analysis['status'] == 'has_issues':
            issues_found.append(analysis)
    
    # 报告结果
    print("📊 分析结果统计:")
    status_counts = {}
    for result in results:
        status = result['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in status_counts.items():
        icon = "✅" if status == 'correct' else "❌" if status == 'has_issues' else "⚠️"
        print(f"   {icon} {status}: {count} 个文件")
    
    print()
    
    # 详细报告有问题的文件
    if issues_found:
        print("🚨 发现路径计算问题的文件:")
        print("=" * 40)
        
        for i, result in enumerate(issues_found, 1):
            print(f"{i}. 📁 {result['relative_to_project']}")
            print(f"   期望的.parent数量: {result['expected_parent_count']}")
            
            for issue in result['issues']:
                if issue['type'] == 'incorrect_parent_count':
                    print(f"   ❌ 发现错误: {issue['pattern_type']}")
                    print(f"      • 当前使用: {issue['found']} 个 .parent")
                    print(f"      • 应该使用: {issue['expected']} 个 .parent")
                else:
                    print(f"   ❌ 其他问题: {issue['type']} - {issue.get('error', '')}")
            print()
    else:
        print("🎉 所有文件的路径计算都正确！")
    
    print()
    print("💡 修复建议:")
    print("   对于有问题的文件，将路径计算修改为:")
    print("   project_root = Path(__file__).parent.parent.parent... (正确数量的.parent)")
    
    return len(issues_found)

if __name__ == "__main__":
    issues_count = main()
    sys.exit(issues_count)  # 返回问题数量作为退出码