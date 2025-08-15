#!/usr/bin/env python3
"""
批量修复项目中所有脚本的路径计算问题
"""

import re
from pathlib import Path
from typing import List, Dict, Any

def fix_file_path_calculation(file_path: Path) -> Dict[str, Any]:
    """修复单个文件的路径计算"""
    result = {
        'file': str(file_path),
        'relative_path': str(file_path.relative_to(Path.cwd())),
        'changed': False,
        'changes': [],
        'error': None
    }
    
    try:
        # 计算正确的.parent数量
        relative_path = file_path.relative_to(Path.cwd())
        correct_parent_count = len(relative_path.parts) - 1
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 修复模式1: project_root = Path(__file__).parent...
        def fix_project_root(match):
            current_parents = match.group(1).count('.parent')
            if current_parents != correct_parent_count:
                correct_parents = '.parent' * correct_parent_count
                result['changes'].append({
                    'type': 'project_root_assignment',
                    'from': current_parents,
                    'to': correct_parent_count
                })
                return f'project_root = Path(__file__){correct_parents}'
            return match.group(0)
        
        content = re.sub(
            r'project_root\s*=\s*Path\(__file__\)((?:\.parent)*)',
            fix_project_root,
            content
        )
        
        # 修复模式2: sys.path.append/insert(str(Path(__file__).parent...))
        def fix_sys_path(match):
            prefix = match.group(1)  # sys.path.append(或insert的部分
            current_parents = match.group(2).count('.parent')
            suffix = match.group(3)  # 剩余部分
            
            if current_parents != correct_parent_count:
                correct_parents = '.parent' * correct_parent_count
                result['changes'].append({
                    'type': 'sys_path_append',
                    'from': current_parents,
                    'to': correct_parent_count
                })
                return f'{prefix}Path(__file__){correct_parents}{suffix}'
            return match.group(0)
        
        content = re.sub(
            r'(sys\.path\.(?:append|insert)\([^)]*?Path\(__file__\))((?:\.parent)*)(.*?\))',
            fix_sys_path,
            content
        )
        
        # 检查是否有变化
        if content != original_content:
            result['changed'] = True
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
    except Exception as e:
        result['error'] = str(e)
    
    return result

def main():
    """批量修复主函数"""
    print("🔧 批量修复项目中的路径计算问题")
    print("=" * 50)
    
    # 从之前检查中发现的有问题的文件
    problem_files = [
        'scripts/tools/checks/check_youtube_oauth.py',
        'scripts/tools/checks/check_github_token.py',
        'scripts/tools/youtube/youtube_oauth_complete.py',
        'scripts/tools/youtube/youtube_oauth_manual.py',
        'scripts/core/content_pipeline.py',
        'scripts/tools/cleanup_onedrive_cloud.py',
        'scripts/tools/onedrive_date_downloader.py',
        'scripts/tools/content/topic_inspiration_generator.py',
        'scripts/tools/create_valid_token.py',
        'scripts/utils/package_creator.py',
        'scripts/utils/audio_link_replacer.py',
        'scripts/utils/youtube_link_mapper.py',
        'scripts/tools/patched_podcastfy.py',
        'scripts/tools/verify_gemini_model.py',
        'scripts/tools/regenerate_youtube_article.py',
        'scripts/tools/debug_podcastfy.py',
        'scripts/tools/simple_test.py',
        'scripts/core/wechat_publisher.py'
    ]
    
    project_root = Path.cwd()
    files_to_fix = [project_root / f for f in problem_files if (project_root / f).exists()]
    
    print(f"📁 将修复 {len(files_to_fix)} 个文件")
    print()
    
    fixed_count = 0
    error_count = 0
    results = []
    
    for file_path in files_to_fix:
        print(f"🔧 修复: {file_path.relative_to(project_root)}")
        result = fix_file_path_calculation(file_path)
        results.append(result)
        
        if result['error']:
            print(f"   ❌ 错误: {result['error']}")
            error_count += 1
        elif result['changed']:
            print(f"   ✅ 已修复")
            for change in result['changes']:
                print(f"      • {change['type']}: {change['from']} → {change['to']} 个.parent")
            fixed_count += 1
        else:
            print(f"   ℹ️ 无需修改")
    
    print()
    print("📊 修复结果统计:")
    print(f"   ✅ 成功修复: {fixed_count} 个文件")
    print(f"   ❌ 修复失败: {error_count} 个文件")
    print(f"   ℹ️ 无需修改: {len(files_to_fix) - fixed_count - error_count} 个文件")
    
    if fixed_count > 0:
        print()
        print("🎉 路径计算问题修复完成！")
        print("💡 建议运行测试验证修复效果:")
        print("   python scripts/tools/checks/check_path_calculations.py")
    
    return fixed_count

if __name__ == "__main__":
    fixed_count = main()