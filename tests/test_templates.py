#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试post_templates.yml的加载和应用
"""

import os
import sys
import yaml
import frontmatter
from pathlib import Path
from rich.console import Console
from rich.table import Table
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入ContentPipeline类
from scripts.core.content_pipeline import ContentPipeline

# 初始化控制台
console = Console()

def load_template_config():
    """加载模板配置"""
    config_path = Path("config/post_templates.yml")
    if not config_path.exists():
        console.print("[bold red]❌ 模板配置文件不存在[/bold red]")
        return None
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            console.print("[bold green]✅ 成功加载模板配置[/bold green]")
            
            # 显示模板配置
            if 'front_matter' in config and 'default' in config['front_matter']:
                default_template = config['front_matter']['default']
                
                table = Table(title="默认前端模板设置")
                table.add_column("设置项", style="cyan")
                table.add_column("值", style="green")
                
                for key, value in default_template.items():
                    table.add_row(key, str(value))
                
                console.print(table)
            else:
                console.print("[bold red]❌ 未找到默认前端模板设置[/bold red]")
            
            return config
    except Exception as e:
        console.print(f"[bold red]❌ 加载模板配置失败: {str(e)}[/bold red]")
        return None

def create_test_content(templates):
    """创建测试内容"""
    console.print("[bold green]✅ 创建测试内容[/bold green]")
    
    # 创建一个包含技术相关内容的测试文章
    content = """---
date: '2025-03-04'
layout: single
title: 测试模板应用
---


## 测试内容

这是一个测试文章，用于验证模板应用功能。本文将介绍一些技术实践相关的内容，包括云服务和应用部署。

### 云服务介绍

云服务是指通过网络以按需、易扩展的方式获取计算资源的服务模式。常见的云服务提供商包括AWS、Azure和Google Cloud Platform。

### 应用部署流程

应用部署是将开发完成的应用程序发布到生产环境的过程。现代应用部署通常采用CI/CD流水线，实现自动化测试和部署。

### 技术工具

在开发和部署过程中，我们使用了多种技术工具，如Docker容器化技术、Kubernetes编排工具等。
"""
    
    console.print("原始内容:")
    console.print(content)
    
    return content

def test_template_application():
    """测试模板应用功能"""
    # 加载模板配置
    template_config = load_template_config()
    if not template_config:
        console.print("[bold red]❌ 加载模板配置失败[/bold red]")
        return
    
    # 创建测试内容
    content = create_test_content(template_config)
    
    # 初始化ContentPipeline
    try:
        pipeline = ContentPipeline()
        console.print("[bold green]✅ 初始化ContentPipeline[/bold green]")
        
        # 调试配置加载
        console.print("\n[bold]调试配置加载:[/bold]")
        console.print(f"导入的配置文件: {pipeline.config.get('imports', [])}")
        
        # 检查配置中是否有模板
        if hasattr(pipeline, 'templates') and pipeline.templates:
            console.print("[bold green]✅ 模板已加载[/bold green]")
            console.print(f"模板键: {list(pipeline.templates.keys())}")
            
            if 'front_matter' in pipeline.templates:
                console.print(f"前端模板键: {list(pipeline.templates['front_matter'].keys())}")
                if 'default' in pipeline.templates['front_matter']:
                    console.print(f"默认模板设置: {pipeline.templates['front_matter']['default']}")
        else:
            console.print("[bold red]❌ 模板未加载[/bold red]")
        
        # 检查配置中是否有post_templates
        if 'post_templates' in pipeline.config:
            console.print(f"配置中的post_templates: {pipeline.config['post_templates']}")
        else:
            console.print("[bold red]❌ 配置中没有post_templates键[/bold red]")
        
        # 测试_deep_update方法
        console.print("\n[bold]测试_deep_update方法:[/bold]")
        base_config = {'a': 1, 'b': {'c': 5, 'd': 3, 'g': 6}, 'e': {'f': 4}}
        update_config = {'b': {'c': 5, 'g': 6}, 'e': 7}
        result = pipeline._deep_update(base_config.copy(), update_config)
        expected = {'a': 1, 'b': {'c': 5, 'd': 3, 'g': 6}, 'e': 7}
        
        console.print(f"基础配置: {base_config}")
        console.print(f"更新配置: {update_config}")
        console.print(f"合并结果: {result}")
        console.print(f"预期结果: {expected}")
        
        # 检查导入的配置文件
        console.print("\n[bold]检查导入的配置文件:[/bold]")
        for import_file in pipeline.config.get('imports', []):
            import_path = Path(f"config/{import_file}")
            if import_path.exists():
                console.print(f"[bold green]✅ 导入文件存在: {import_path}[/bold green]")
                try:
                    with open(import_path, 'r', encoding='utf-8') as f:
                        imported_config = yaml.safe_load(f)
                        if imported_config:
                            console.print(f"[bold green]✅ 成功加载导入配置: {import_file}[/bold green]")
                            console.print(f"导入配置的键: {list(imported_config.keys())}")
                            
                            # 如果是post_templates.yml，检查其内容
                            if import_file == 'post_templates.yml':
                                console.print("[bold]post_templates.yml内容:[/bold]")
                                console.print(f"键: {list(imported_config.keys())}")
                                if 'front_matter' in imported_config:
                                    console.print(f"front_matter键: {list(imported_config['front_matter'].keys())}")
                                    if 'default' in imported_config['front_matter']:
                                        console.print(f"default设置: {imported_config['front_matter']['default']}")
                        else:
                            console.print(f"[bold yellow]⚠️ 导入的配置为空: {import_file}[/bold yellow]")
                except Exception as e:
                    console.print(f"[bold red]❌ 加载导入配置失败: {import_file}, {str(e)}[/bold red]")
            else:
                console.print(f"[bold red]❌ 导入文件不存在: {import_path}[/bold red]")
        
        # 手动添加模板
        console.print("\n[bold]手动添加模板:[/bold]")
        # 解析内容
        post = frontmatter.loads(content)
        
        # 应用默认模板
        default_template = pipeline.templates.get('front_matter', {}).get('default', {})
        if default_template:
            for key, value in default_template.items():
                if key not in post:
                    post[key] = value
                    console.print(f"应用设置: {key}={value}")
            
            # 添加last_modified_at
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            post['last_modified_at'] = current_time
            console.print(f"添加最后修改时间: {current_time}")
            
            # 分析内容分类
            if 'categories' not in post:
                # 使用简单匹配
                categories = pipeline._suggest_categories(post.content)
                if categories:
                    post['categories'] = categories
                    console.print(f"添加分类: {categories}")
                    
            # 添加标签
            if 'tags' not in post:
                post['tags'] = ["测试", "模板", "技术"]
                console.print(f"添加标签: {post['tags']}")
                
            console.print("[bold green]✅ 应用模板成功[/bold green]")
            
            # 输出处理后的内容
            processed_content = frontmatter.dumps(post)
            console.print("处理后内容:")
            console.print(processed_content)
            
            # 显示应用后的设置
            table = Table(title="应用后的设置")
            table.add_column("设置项", style="cyan")
            table.add_column("值", style="magenta")
            table.add_column("来源", style="green")
            
            for key, value in post.metadata.items():
                source = "模板" if key in default_template else "原始内容"
                if key not in ['date', 'layout', 'title'] and key not in default_template:
                    source = "自动添加"
                table.add_row(key, str(value), source)
            
            console.print(table)
        else:
            console.print("[bold red]❌ 未找到默认模板[/bold red]")
            
    except Exception as e:
        console.print(f"[bold red]❌ 测试失败: {str(e)}[/bold red]")
        import traceback
        console.print(traceback.format_exc())

if __name__ == "__main__":
    test_template_application() 