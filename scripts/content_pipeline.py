import os
import re
import yaml
import logging
import subprocess
import shutil
import frontmatter
import json
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import google.generativeai as genai
from google.generativeai import GenerationConfig, GenerativeModel  # 更新导入
from dotenv import load_dotenv
from google.api_core import exceptions, retry
from google.generativeai.types import (
    BlockedPromptException,
    BrokenResponseError,
    IncompleteIterationError,
    StopCandidateException
)
from scripts import setup_logger
import argparse

# 导入本地模块
from .image_mapper import CloudflareImageMapper

class ContentPipeline:
    def __init__(self, config_path: str = "config/pipeline_config.yml", verbose: bool = False):
        """初始化内容处理管道
        Args:
            config_path: 配置文件路径
            verbose: 是否输出详细日志
        """
        self.verbose = verbose
        self.logger = logging.getLogger("ContentPipeline")
        
        # 初始化API状态
        self.api_available = True
        
        # 加载配置
        try:
            # 加载主配置文件
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            self.logger.debug(f"加载配置文件: {config_path}")
            
            # 加载完整配置（包括导入的配置文件）
            self.config = self._load_config()
            
            # 验证环境变量
            account_id = os.getenv('CLOUDFLARE_ACCOUNT_ID')
            account_hash = os.getenv('CLOUDFLARE_ACCOUNT_HASH')
            api_token = os.getenv('CLOUDFLARE_API_TOKEN')
            
            if not all([account_id, account_hash, api_token]):
                raise ValueError("❌ Cloudflare 环境变量未正确设置")
            
            # 初始化Cloudflare Images客户端
            self.image_mapper = CloudflareImageMapper(
                account_id=account_id,
                account_hash=account_hash,
                api_token=api_token
            )
        except Exception as e:
            self.logger.error(f"加载配置失败: {str(e)}", exc_info=True)
            raise
        
        self._setup_logging()
        
        # 加载模板和平台配置
        # 检查是否有post_templates键，如果没有但有front_matter键，则使用front_matter
        if 'post_templates' in self.config:
            self.templates = self.config['post_templates']
        elif 'front_matter' in self.config:
            self.templates = {'front_matter': self.config['front_matter']}
            if 'categories' in self.config:
                self.templates['categories'] = self.config['categories']
            if 'footer' in self.config:
                self.templates['footer'] = self.config['footer']
            self.logger.debug("从配置中加载模板成功")
        else:
            self.templates = {}
            self.logger.warning("未加载模板或模板为空")
        
        self.platforms_config = self.config.get('platforms', {})
        
        # 设置API
        self._setup_apis()
        self._setup_site_url()
        
    def log(self, message: str, level: str = "info", force: bool = False):
        """统一的日志处理
        Args:
            message: 日志消息
            level: 日志级别 (debug/info/warning/error)
            force: 是否强制显示（忽略verbose设置）
        """
        if self.verbose or force or level in ["error", "warning"]:
            getattr(self.logger, level)(message)
        
        # 始终写入日志文件
        with open("logs/pipeline.log", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {level.upper()} - {message}\n")
    
    def _load_config(self) -> dict:
        """加载所有配置"""
        config_dir = Path("config")
        config = {}
        
        try:
            # 加载主配置
            with open(config_dir / "pipeline_config.yml", 'r', encoding='utf-8') as f:
                config.update(yaml.safe_load(f))
            
            # 加载导入的配置
            for import_file in config.get("imports", []):
                try:
                    with open(config_dir / import_file, 'r', encoding='utf-8') as f:
                        imported_config = yaml.safe_load(f)
                        if imported_config:
                            # 递归更新配置，保持嵌套结构
                            self._deep_update(config, imported_config)
                            self.logger.debug(f"成功导入配置: {import_file}")
                        else:
                            self.logger.warning(f"导入的配置为空: {import_file}")
                except FileNotFoundError:
                    self.logger.warning(f"导入的配置文件不存在: {import_file}")
                except yaml.YAMLError as e:
                    self.logger.warning(f"导入的配置文件格式错误: {import_file}, {str(e)}")
                    
            return config
            
        except FileNotFoundError as e:
            logging.error(f"配置文件不存在: {e.filename}")
            raise
        except yaml.YAMLError as e:
            logging.error(f"配置文件格式错误: {str(e)}")
            raise
    
    def _deep_update(self, d: dict, u: dict) -> dict:
        """递归更新字典，保持嵌套结构"""
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._deep_update(d.get(k, {}), v)
            else:
                d[k] = v
        return d
    
    def _setup_logging(self):
        """配置日志"""
        log_path = Path(self.config["paths"]["logs"])
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 同时输出到文件和控制台
        handlers = [
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler()
        ]
        
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=handlers
        )
    
    def _setup_apis(self):
        """设置API客户端"""
        load_dotenv(override=True)  # 确保重新加载环境变量
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        try:
            # 配置 API
            genai.configure(api_key=api_key)
            
            # 获取可用模型列表
            self.log("正在获取可用模型列表...", level="info")
            try:
                models = genai.list_models()
                model_names = [model.name for model in models]
                self.log(f"可用模型: {model_names}", level="info", force=True)
                
                # 优先选择 Gemini 2.0 Flash 模型，然后是 Pro 模型
                preferred_models = [
                    # 根据用户需求，优先使用 Flash 模型
                    "models/gemini-2.0-flash",
                    "models/gemini-2.0-pro",
                    "models/gemini-1.5-flash",
                    "models/gemini-1.5-pro"
                ]
                
                # 查找最佳匹配模型
                model_name = None
                for preferred in preferred_models:
                    matching_models = [name for name in model_names if preferred in name]
                    if matching_models:
                        # 优先选择没有 "exp" 或 "experimental" 的稳定版本
                        stable_models = [name for name in matching_models if "exp" not in name.lower()]
                        if stable_models:
                            model_name = stable_models[0]
                            self.log(f"找到稳定版本模型: {model_name}", level="info")
                        else:
                            model_name = matching_models[0]
                            self.log(f"找到实验版本模型: {model_name}", level="info")
                        break
                
                # 如果没有找到匹配的模型，使用任何可用的 Gemini 模型
                if not model_name:
                    gemini_models = [name for name in model_names if 'gemini' in name.lower()]
                    if gemini_models:
                        # 过滤掉已知的弃用模型
                        valid_models = [name for name in gemini_models if 'gemini-1.0' not in name]
                        if valid_models:
                            model_name = valid_models[0]
                        else:
                            model_name = gemini_models[0]
                            self.log(f"警告：可能使用了已弃用的模型", level="warning", force=True)
                    else:
                        # 如果找不到 Gemini 模型，尝试使用配置中的模型
                        model_name = self.config["content_processing"]["gemini"]["model"]
                        self.log(f"未找到 Gemini 模型，尝试使用配置的模型: {model_name}", level="warning", force=True)
                
                self.log(f"选择使用模型: {model_name}", level="info", force=True)
                
            except Exception as e:
                self.log(f"获取模型列表失败: {str(e)}", level="warning")
                # 尝试使用最新的 Gemini 模型名称
                model_name = "models/gemini-2.0-flash"
                self.log(f"尝试使用最新模型: {model_name}", level="info", force=True)
            
            # 创建模型实例
            self.model = genai.GenerativeModel(model_name)
            
            # 测试连接
            try:
                response = self.model.generate_content(
                    "Test connection",
                    generation_config=GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=10
                    )
                )
                if response:
                    self.log("✅ Gemini API 连接成功", level="info", force=True)
                    
                    # 更新配置中的模型名称
                    self.config["content_processing"]["gemini"]["model"] = model_name
                    
                    # 验证模板加载
                    self._validate_templates()
            except exceptions.ResourceExhausted as e:
                self.log(f"❌ API 配额已耗尽，请稍后再试: {str(e)}", level="error", force=True)
                # 不抛出异常，允许程序继续运行，但标记API不可用
                self.api_available = False
            except Exception as e:
                self.log(f"❌ Gemini API 连接测试失败: {str(e)}", level="error", force=True)
        except Exception as e:
            self.log(f"❌ 设置API失败: {str(e)}", level="error", force=True)
            raise
            
    def _validate_templates(self):
        """验证模板是否正确加载"""
        if not hasattr(self, 'templates') or not self.templates:
            self.log("未加载模板或模板为空", level="warning")
            return
            
        self.log(f"已加载模板: {list(self.templates.keys())}", level="debug")
        self.log(f"模板内容: {self.templates}", level="debug")
        
        # 验证前端模板
        if 'front_matter' in self.templates:
            if 'default' in self.templates['front_matter']:
                default_template = self.templates['front_matter']['default']
                self.log(f"默认前端模板包含 {len(default_template)} 个设置", level="info")
                # 检查关键设置
                if 'toc' in default_template and default_template['toc']:
                    self.log("✅ 目录设置已加载", level="info")
                else:
                    self.log("⚠️ 目录设置未加载或未启用", level="warning")
            else:
                self.log("⚠️ 未找到默认前端模板", level="warning")
                self.log(f"可用的前端模板: {list(self.templates['front_matter'].keys())}", level="debug")
        else:
            self.log("⚠️ 未找到前端模板配置", level="warning")
            
        # 验证页脚模板
        if 'footer' in self.templates:
            footer_platforms = list(self.templates['footer'].keys())
            self.log(f"页脚模板平台: {footer_platforms}", level="info")
            
            # 检查GitHub Pages页脚
            if 'github_pages' in self.templates['footer']:
                footer_content = self.templates['footer']['github_pages']
                if footer_content and len(footer_content) > 10:
                    self.log("✅ GitHub Pages页脚模板已加载", level="info")
                else:
                    self.log("⚠️ GitHub Pages页脚模板为空或内容过短", level="warning")
            else:
                self.log("⚠️ 未找到GitHub Pages页脚模板", level="warning")
        else:
            self.log("⚠️ 未找到页脚模板配置", level="warning")
    
    def list_drafts(self) -> List[Path]:
        """列出所有草稿文件"""
        drafts_dir = Path(self.config["paths"]["drafts"])
        all_drafts = list(drafts_dir.glob("*.md"))
        
        # 过滤出有效的草稿文件
        valid_drafts = []
        for draft in all_drafts:
            if self._is_valid_draft(draft):
                valid_drafts.append(draft)
            else:
                self.log(f"⚠️ 跳过无效草稿: {draft.name}", level="warning")
        
        return valid_drafts
    
    def select_draft(self) -> Optional[Path]:
        """让用户选择要处理的草稿"""
        drafts = self.list_drafts()
        if not drafts:
            print("没有找到草稿文件")
            return None
            
        print("\n可用的草稿文件：")
        for i, draft in enumerate(drafts, 1):
            print(f"{i}. {draft.name}")
            
        while True:
            try:
                choice = int(input("\n请选择要处理的草稿 (输入序号): "))
                if 1 <= choice <= len(drafts):
                    return drafts[choice-1]
                print("无效的选择")
            except ValueError:
                print("请输入有效的数字")
    
    def select_platforms(self) -> List[str]:
        """让用户选择发布平台"""
        available_platforms = [name for name, config in self.config["platforms"].items() 
                            if config.get("enabled", False)]
        
        print("\n可用的发布平台：")
        for i, platform in enumerate(available_platforms, 1):
            print(f"{i}. {platform}")
            
        selections = input("\n请选择发布平台 (多个平台用逗号分隔): ").split(",")
        selected_platforms = []
        
        for sel in selections:
            try:
                idx = int(sel.strip()) - 1
                if 0 <= idx < len(available_platforms):
                    selected_platforms.append(available_platforms[idx])
            except ValueError:
                continue
                
        return selected_platforms
    
    def process_draft(self, draft_path: Path, platforms: List[str]) -> bool:
        """处理草稿文件"""
        try:
            self.log(f"============================== 开始处理草稿 ==============================", force=True)
            self.log(f"草稿文件: {draft_path}", force=True)
            
            all_success = True  # 跟踪所有操作是否成功
            console = Console()
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                # 1. 读取内容
                task = progress.add_task("📖 读取文章内容...", total=None)
                with open(draft_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                progress.update(task, completed=True)
                
                # 检查内容完整性
                if len(content) < 100:
                    self.log("❌ 文章内容过短，可能不完整", level="error", force=True)
                    return False
                
                # 预处理 front matter 中的引号问题
                try:
                    # 尝试解析 front matter
                    post = frontmatter.loads(content)
                except Exception as e:
                    self.log(f"⚠️ Front matter 解析错误: {str(e)}", level="warning")
                    # 尝试修复常见的引号问题
                    content = self._fix_frontmatter_quotes(content)
                    try:
                        post = frontmatter.loads(content)
                    except Exception as e:
                        self.log(f"❌ 修复后仍无法解析 front matter: {str(e)}", level="error")
                        return False
                
                # 2. 处理图片
                task = progress.add_task("🖼️ 处理文章图片...", total=None)
                image_mappings = self.process_post_images(draft_path)
                
                if image_mappings:
                    # 替换正文中的图片链接
                    content = self._replace_images(content, image_mappings)
                    
                    # 更新front matter中的图片链接
                    post = self._update_header_images(post, image_mappings)
                    
                    # 重新生成带有更新后图片链接的内容
                    content = frontmatter.dumps(post)
                    self.log("✅ 图片链接替换完成", level="info")
                else:
                    self.log("⚠️ 没有找到需要处理的图片或处理失败", level="warning")
                
                progress.update(task, completed=True)
                
                # 3. 润色内容
                task = progress.add_task("✨ 润色文章内容...", total=None)
                polished_content = self._polish_content(content)
                if not polished_content:
                    self.log("❌ 内容润色失败，使用原内容", level="warning", force=True)
                    polished_content = content
                progress.update(task, completed=True)
                
                # 4. 生成各平台内容
                platform_contents = {}
                platform_success = {}  # 跟踪每个平台的处理结果
                
                for platform in platforms:
                    task = progress.add_task(f"📝 处理 {platform} 平台...", total=None)
                    platform_content = self._generate_platform_content(
                        polished_content,
                        image_mappings,
                        platform,
                        draft_path
                    )
                    
                    # 验证内容完整性
                    if len(platform_content) < len(polished_content) * 0.9:
                        self.log(f"❌ {platform}平台内容可能不完整", level="error", force=True)
                        platform_success[platform] = False
                    else:
                        platform_contents[platform] = platform_content
                        platform_success[platform] = True
                    
                    progress.update(task, completed=True)
                
                # 5. 发布内容
                for platform, content in platform_contents.items():
                    if not platform_success.get(platform, False):
                        continue
                        
                    task = progress.add_task(f"🚀 发布到 {platform}...", total=None)
                    if platform == "github_pages":
                        publish_success = self._publish_to_github_pages(draft_path, content)
                        platform_success[platform] = publish_success
                    elif platform == "wechat":
                        self._publish_to_wechat(content)
                    elif platform == "wordpress":
                        self._publish_to_wordpress(content)
                    progress.update(task, completed=True)
                
                # 检查所有平台是否都成功
                all_success = all_success and all(platform_success.values())
                
                # 6. 归档草稿
                if all_success:
                    task = progress.add_task("📦 归档草稿...", total=None)
                    self._archive_draft(draft_path)
                    progress.update(task, completed=True)
                else:
                    self.log("⚠️ 处理未完全成功，跳过归档步骤", level="warning", force=True)
                
            return all_success
            
        except Exception as e:
            self.logger.error(f"处理草稿时出错: {str(e)}")
            return False
    
    def _preprocess_content(self, text: str) -> str:
        """预处理内容，处理特殊格式"""
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('excerpt:'):
                # 将单行 excerpt 转换为多行格式
                content = line.split(':', 1)[1].strip().strip('"')
                lines[i] = 'excerpt: |'
                lines.insert(i + 1, '  ' + content)
        return '\n'.join(lines)
    
    def _fix_frontmatter_quotes(self, content: str) -> str:
        """修复 front matter 中的引号问题"""
        # 分离 front matter 和正文
        parts = content.split('---', 2)
        if len(parts) < 3:
            self.log("❌ 无法识别 front matter，格式可能不正确", level="error")
            return content
        
        front_matter = parts[1]
        body = parts[2]
        
        # 处理 front matter 中的引号问题
        lines = front_matter.split('\n')
        for i, line in enumerate(lines):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # 处理 excerpt 字段
                if key == 'excerpt' and value.startswith('"') and '"' in value[1:]:
                    # 将 excerpt 转换为多行格式
                    lines[i] = 'excerpt: |'
                    # 去掉引号，添加缩进
                    clean_value = value.strip('"')
                    lines.insert(i + 1, '  ' + clean_value)
                
                # 处理其他包含引号的字段
                elif '"' in value and not (value.startswith('"') and value.endswith('"')):
                    # 使用 | 语法处理多行内容
                    lines[i] = f'{key}: |'
                    lines.insert(i + 1, '  ' + value.strip('"'))
        
        # 重新组合内容
        fixed_front_matter = '\n'.join(lines)
        return f"---\n{fixed_front_matter}\n---{body}"
    
    def _polish_content(self, content: str) -> Optional[str]:
        """使用AI润色文章内容"""
        if not self.api_available:
            self.log("API不可用，跳过润色", level="warning")
            return content
        
        try:
            # 解析front matter
            try:
                post = frontmatter.loads(content)
            except Exception as e:
                self.log(f"解析front matter失败: {str(e)}", level="warning")
                # 尝试修复
                content = self._fix_frontmatter_quotes(content)
                try:
                    post = frontmatter.loads(content)
                except Exception as e:
                    self.log(f"修复后仍无法解析front matter: {str(e)}", level="error")
                    return content
            
            # 提取正文内容
            content_text = post.content
            
            # 如果内容太短，不进行润色
            if len(content_text) < 100:
                self.log("内容太短，不进行润色", level="warning")
                return content
            
            # 构建提示词
            prompt = f"""
            请对以下文章内容进行润色，使其更加流畅、易读，同时保持原文的核心思想和信息。
            不要添加任何额外的评论或前言，直接返回润色后的内容。
            不要修改文章的结构或添加新的章节。
            
            {content_text}
            """
            
            # 调用API
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                # 更新内容
                post.content = response.text.strip()
                return frontmatter.dumps(post)
            else:
                self.log("API返回为空", level="warning")
                return content
            
        except exceptions.ResourceExhausted as e:
            self.log(f"API配额已用尽: {str(e)}", level="error", force=True)
            self.api_available = False
            return content
        except Exception as e:
            self.log(f"润色内容时出错: {str(e)}", level="error")
            return content
    
    def _generate_platform_content(self, content: str, images: Dict[str, str], platform: str, draft_path: Path) -> str:
        """为特定平台生成内容"""
        try:
            # 获取平台配置
            platform_config = self.platforms_config.get(platform, {})
            
            # 尝试解析内容
            try:
                post = frontmatter.loads(content)
            except Exception as e:
                self.log(f"⚠️ 解析 front matter 失败: {str(e)}", level="warning")
                # 尝试修复 front matter
                content = self._fix_frontmatter_quotes(content)
                try:
                    post = frontmatter.loads(content)
                except Exception as e:
                    self.log(f"❌ 修复后仍无法解析 front matter: {str(e)}", level="error")
                    return content
            
            # 确保内容完整性
            if not post.content:
                self.log("❌ 文章内容为空", level="error", force=True)
                return content
            content_text = post.content
            
            # 应用默认模板
            default_template = self.templates.get('front_matter', {}).get('default', {})
            for key, value in default_template.items():
                if key not in post:
                    post[key] = value
                    self.log(f"应用默认模板: {key}={value}", level="info")
            
            # 添加或更新最后修改时间
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            post['last_modified_at'] = current_time
            self.log(f"更新最后修改时间: {current_time}", level="info")
            
            # 确保作者信息正确
            if platform_config.get('author', None):
                post['author'] = platform_config.get('author')
                self.log(f"设置作者: {post['author']}", level="info")
            
            # 确保author_profile设置为true
            if 'author_profile' not in post or not post['author_profile']:
                post['author_profile'] = True
                self.log("启用作者资料显示", level="info")
            
            # 先处理图片（如果需要）
            if platform_config.get('replace_images', True):
                content_text = self._replace_images(content_text, images)
                post = self._update_header_images(post, images)
            
            # 分析分类和标签（如果需要）
            # 将analyze_content默认设为True，确保始终分析内容
            if platform_config.get('analyze_content', True):
                # 即使已有分类和标签，也重新分析以确保最新
                categories, tags = self._analyze_content_categories(content_text)
                if categories:
                    post['categories'] = categories
                    self.log(f"添加分类: {categories}", level="info")
                if tags:
                    post['tags'] = tags
                    self.log(f"添加标签: {tags}", level="info")
            
            # 润色内容（如果需要）
            if platform_config.get('polish_content', True):
                polished_content = self._polish_content(content_text)
                if polished_content:
                    content_text = polished_content
            
            # 添加页脚（如果需要）
            if platform_config.get('append_footer', False):
                # 获取页脚模板
                footer_template = self.templates.get('footer', {}).get(platform, '')
                self.log(f"页脚模板: {footer_template[:50]}...", level="info")
                
                if footer_template:
                    # 确保页脚前有足够的空行
                    if not content_text.endswith('\n\n'):
                        content_text = content_text.rstrip() + '\n\n'
                    
                    content_text = f"{content_text}{footer_template}"
                    self.log(f"添加页脚成功", level="info", force=True)
                else:
                    self.log(f"未找到平台 {platform} 的页脚模板", level="warning", force=True)
            
            # 更新内容和作者
            post.content = content_text
            post['author'] = platform_config.get('author', post.get('author', ''))
            
            # 验证内容完整性
            result = frontmatter.dumps(post)
            if len(result) < len(content) * 0.9:  # 如果内容减少超过10%
                self.log("⚠️ 警告：生成的内容可能不完整", level="warning", force=True)
            
            return result
            
        except Exception as e:
            self.log(f"生成{platform}内容时出错: {str(e)}", level="error", force=True)
            return content
    
    def _publish_contents(self, draft_path: Path, 
                         platform_contents: Dict[str, str]):
        """发布内容到各平台"""
        for platform, content in platform_contents.items():
            if platform == "github_pages":
                self._publish_to_github_pages(draft_path, content)
            elif platform == "wechat":
                self._publish_to_wechat(content)
            elif platform == "wordpress":
                self._publish_to_wordpress(content)
                
    def _archive_draft(self, draft_path: Path):
        """归档已处理的草稿"""
        try:
            archive_dir = Path(self.config["paths"]["archive"])
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            new_path = archive_dir / draft_path.name
            if new_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_path = archive_dir / f"{draft_path.stem}_{timestamp}{draft_path.suffix}"
                logging.info(f"目标文件已存在，使用时间戳重命名: {new_path.name}")
            
            # 添加更详细的路径信息
            logging.info(f"归档草稿:")
            logging.info(f"  从: {draft_path}")
            logging.info(f"  到: {new_path}")
            
            draft_path.rename(new_path)
            logging.info(f"✅ 归档完成")
            
        except Exception as e:
            logging.error(f"归档草稿时出错: {str(e)}")
            logging.debug("错误详情:", exc_info=True)
    
    def _convert_links_to_new_window(self, content: str) -> str:
        """将Markdown链接转换为在新窗口打开的HTML链接"""
        # 匹配Markdown链接格式 [text](url)
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        def replace_link(match):
            text = match.group(1)
            url = match.group(2)
            # 跳过图片链接
            if text.startswith('!'):
                return match.group(0)
            # 跳过已经是HTML链接的情况
            if '<a ' in text and '</a>' in text:
                return match.group(0)
            # 转换为HTML链接，添加target="_blank"属性
            return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{text}</a>'
        
        # 替换所有链接
        converted_content = re.sub(pattern, replace_link, content)
        
        # 也处理已经存在的HTML链接，但没有target="_blank"的情况
        html_link_pattern = r'<a\s+(?![^>]*target="_blank")([^>]*)href="([^"]+)"([^>]*)>(.*?)</a>'
        
        def add_target_blank(match):
            attrs_before = match.group(1)
            url = match.group(2)
            attrs_after = match.group(3)
            text = match.group(4)
            return f'<a {attrs_before}href="{url}"{attrs_after} target="_blank" rel="noopener noreferrer">{text}</a>'
        
        # 为现有HTML链接添加target="_blank"
        converted_content = re.sub(html_link_pattern, add_target_blank, converted_content)
        
        self.log("✅ 已将所有链接设置为在新窗口打开", level="debug")
        return converted_content

    def _generate_blog_content(self, content: str, images: Dict[str, str], draft_path: Path) -> str:
        """生成博客内容"""
        try:
            # 尝试解析front matter
            try:
                post = frontmatter.loads(content)
            except Exception as e:
                self.log(f"⚠️ 解析 front matter 失败: {str(e)}", level="warning")
                # 尝试修复 front matter
                content = self._fix_frontmatter_quotes(content)
                try:
                    post = frontmatter.loads(content)
                except Exception as e:
                    self.log(f"❌ 修复后仍无法解析 front matter: {str(e)}", level="error")
                    return content
            
            # 确保内容完整性
            if not post.content:
                self.log("❌ 文章内容为空", level="error", force=True)
                return content
            
            # 应用默认模板
            default_template = self.templates.get('front_matter', {}).get('default', {})
            if default_template:
                for key, value in default_template.items():
                    if key not in post:
                        post[key] = value
                        self.log(f"应用默认模板: {key}={value}", level="info")
                self.log(f"已应用默认模板设置", level="info")
            else:
                self.log(f"未找到默认模板设置", level="warning")
            
            # 更新文章中的图片链接
            updated_content = post.content
            for local_name, cloudflare_url in images.items():
                # 构建本地路径模式
                date_str = draft_path.stem[:10]
                post_name = draft_path.stem[11:]
                local_path = f"/assets/images/posts/{date_str[:4]}/{date_str[5:7]}/{post_name}/{local_name}"
                
                # 替换内容中的图片链接
                updated_content = updated_content.replace(local_path, cloudflare_url)
                self.log(f"✅ 替换图片URL: {local_name} -> {cloudflare_url}", level="info")
                
                # 更新 front matter 中的图片链接
                if "header" in post and "image" in post["header"]:
                    if post["header"]["image"] == local_path:
                        post["header"]["image"] = cloudflare_url
                        self.log(f"更新 header 图片: {cloudflare_url}", level="info")
            
            # 更新内容
            post.content = updated_content
            
            # 将Markdown链接转换为在新窗口打开的HTML链接
            post.content = self._convert_links_to_new_window(post.content)
            self.log("✅ 已将链接设置为在新窗口打开", level="info")
            
            # 添加页脚
            platform_config = self.platforms_config.get('github_pages', {})
            if platform_config.get('append_footer', False):
                footer_template = self.templates.get('footer', {}).get('github_pages', '')
                if footer_template:
                    # 确保页脚前有足够的空行
                    if not post.content.endswith('\n\n'):
                        post.content = post.content.rstrip() + '\n\n'
                    
                    post.content = f"{post.content}{footer_template}"
                    self.log(f"添加页脚成功", level="info")
                else:
                    self.log(f"未找到 github_pages 的页脚模板", level="warning")
            
            # 添加调试日志
            self.log(f"处理后的内容长度: {len(post.content)}", level="debug")
            
            return frontmatter.dumps(post)
            
        except Exception as e:
            self.log(f"生成博客内容时出错: {str(e)}", level="error")
            return content

    def _generate_wechat_content(self, content: str, images: Dict[str, str]) -> str:
        """生成微信公众号内容"""
        # TODO: 实现微信公众号的内容转换
        # 1. 处理图片链接
        # 2. 调整格式
        # 3. 添加微信特定的样式
        return content

    def _generate_wordpress_content(self, content: str, images: Dict[str, str]) -> str:
        """生成WordPress内容"""
        # TODO: 实现WordPress的内容转换
        # 1. 处理图片链接
        # 2. 转换Markdown为HTML
        # 3. 添加WordPress特定的格式
        return content

    def _publish_to_github_pages(self, draft_path: Path, content: str) -> bool:
        """发布到GitHub Pages，返回是否成功"""
        try:
            publish_path = Path(self.config["paths"]["posts"]) / draft_path.name
            
            # 检查内容是否以front matter开头
            if not content.startswith('---'):
                self.log("⚠️ 内容不是以front matter开头，尝试修复", level="warning")
                try:
                    post = frontmatter.loads(content)
                    content = frontmatter.dumps(post)
                    # 确保内容以front matter开头
                    if not content.startswith('---'):
                        self.log("❌ 无法修复front matter格式", level="error")
                        return False
                except Exception as e:
                    self.log(f"❌ 解析front matter失败: {str(e)}", level="error")
                    return False
            
            # 保存文件
            with open(publish_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.log(f"✅ 内容已发布到: {publish_path}", force=True)
            
            # Git 操作
            try:
                # 先拉取最新代码
                subprocess.run(["git", "pull"], check=True)
                
                # 添加文件
                subprocess.run(["git", "add", str(publish_path)], check=True)
                
                # 检查文件状态
                status = subprocess.run(
                    ["git", "status", "--porcelain", str(publish_path)],
                    capture_output=True,
                    text=True
                ).stdout.strip()
                
                if not status:
                    self.log("没有需要提交的更改", level="warning")
                    return False
                
                # 提交更改
                subprocess.run(["git", "commit", "-m", f"发布: {draft_path.name}"], check=True)
                
                # 推送
                subprocess.run(["git", "push"], check=True)
                self.log("✅ 已推送到 GitHub", force=True)
                return True
                
            except Exception as e:
                self.log(f"❌ Git操作失败: {str(e)}", level="error")
                return False
                
        except Exception as e:
            self.log(f"❌ 发布到GitHub Pages失败: {str(e)}", level="error")
            return False

    def _publish_to_wechat(self, content: str):
        """发布到微信公众号"""
        # TODO: 实现微信公众号发布
        logging.info("微信公众号发布功能尚未实现")

    def _publish_to_wordpress(self, content: str):
        """发布到WordPress"""
        # TODO: 实现WordPress发布
        logging.info("WordPress发布功能尚未实现")

    def generate_test_content(self) -> Optional[Path]:
        """使用Gemini生成测试文章"""
        try:
            prompt = self.config["content_processing"]["gemini"]["prompts"]["test"]
            
            response = self.model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=self.config["content_processing"]["gemini"]["temperature"],
                    max_output_tokens=self.config["content_processing"]["gemini"]["max_output_tokens"],
                    top_p=self.config["content_processing"]["gemini"]["top_p"]
                )
            )
            
            if response:
                try:
                    # 获取响应内容
                    if hasattr(response, 'candidates') and response.candidates:
                        content = response.candidates[0].content.parts[0].text
                    else:
                        content = ' '.join(part.text for part in response.parts)
                    
                    logging.debug(f"原始响应类型: {type(content)}")
                    logging.debug(f"原始响应内容: {content[:100]}...")
                    
                    # 创建文章内容
                    post = {
                        "layout": "single",
                        "title": "自动化测试实践：从CI到CD的最佳实践",
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S +0000"),
                        "categories": ["技术"],
                        "tags": ["自动化测试", "CI/CD", "DevOps"],
                        "header": {
                            "image": "/assets/images/posts/2025/02/test-post/header.webp",
                            "overlay_filter": 0.5
                        }
                    }
                    
                    # 先转换为字符串
                    post_text = frontmatter.dumps(frontmatter.Post(content, **post))
                    
                    # 写入文件
                    draft_path = Path("_drafts/2025-02-20-auto-test.md")
                    draft_path.parent.mkdir(parents=True, exist_ok=True)
                    draft_path.write_text(post_text, encoding='utf-8')
                    
                    logging.info(f"✅ 已生成测试文章: {draft_path}")
                    return draft_path
                    
                except Exception as e:
                    logging.error(f"处理响应内容时出错: {str(e)}")
                    logging.debug("错误详情:", exc_info=True)
                    return None
                
        except Exception as e:
            logging.error(f"生成测试文章失败: {str(e)}")
            logging.debug("错误详情:", exc_info=True)
            return None

    def process_post_images(self, post_path: Path) -> Dict[str, str]:
        """处理文章中的图片"""
        # 获取文章中的本地图片
        local_images = {}
        with open(post_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 尝试解析 front matter
            try:
                # 从front matter中提取图片
                post = frontmatter.loads(content)
            except Exception as e:
                self.log(f"⚠️ 解析 front matter 失败: {str(e)}", level="warning")
                # 尝试修复 front matter
                content = self._fix_frontmatter_quotes(content)
                try:
                    post = frontmatter.loads(content)
                except Exception as e:
                    self.log(f"❌ 修复后仍无法解析 front matter: {str(e)}", level="error")
                    return {}
            
            if 'header' in post:
                for img_field in ['image', 'og_image', 'overlay_image', 'teaser']:
                    if img_field in post['header']:
                        img_path = post['header'][img_field]
                        if img_path and img_path.startswith('/assets/images/'):
                            name = Path(img_path).name
                            full_path = Path.cwd() / img_path.lstrip('/')
                            if full_path.exists():
                                local_images[name] = full_path
                                self.log(f"找到头图: {name}", level="debug")
                            else:
                                self.log(f"头图不存在: {img_path}", level="warning")
            
            # 查找markdown图片语法
            for match in re.finditer(r'!\[.*?\]\((.*?)\)', content):
                img_path = match.group(1)
                # 跳过已经是Cloudflare URL的图片
                if img_path.startswith('https://imagedelivery.net'):
                    self.log(f"跳过已有的Cloudflare图片: {img_path}", level="debug")
                    continue
                    
                if img_path.startswith('/assets/images/'):
                    name = Path(img_path).name
                    # 获取图片的完整路径
                    full_path = Path.cwd() / img_path.lstrip('/')
                    
                    if full_path.exists():
                        local_images[name] = full_path
                        self.log(f"找到正文图片: {name}", level="debug")
                    else:
                        self.log(f"正文图片不存在: {img_path}", level="warning")
                
        if not local_images:
            self.log("没有找到任何有效的图片", level="warning")
            return {}
        
        # 上传到Cloudflare并获取映射
        self.log(f"开始处理 {len(local_images)} 张图片", level="info")
        image_mappings = self.image_mapper.map_images(local_images)
        self.log(f"图片处理完成，共 {len(image_mappings)} 张", level="info")
        return image_mappings

    def _setup_site_url(self):
        """设置站点URL"""
        # 从平台配置中获取域名
        if 'platforms' in self.config and 'github_pages' in self.config['platforms']:
            self.site_url = self.config['platforms']['github_pages'].get('domain', 'arong.eu.org/youxinyanzhe')
        else:
            # 默认值
            self.site_url = 'arong.eu.org/youxinyanzhe'
        
        self.log(f"站点URL: {self.site_url}", level="debug")
    
    def _is_valid_draft(self, file_path: Path) -> bool:
        """检查文件是否是有效的草稿文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否有 front matter
            if not content.startswith('---'):
                return False
            
            # 尝试解析 front matter
            try:
                post = frontmatter.loads(content)
                # 检查必要的字段
                required_fields = ['title', 'date', 'layout']
                for field in required_fields:
                    if field not in post:
                        self.log(f"草稿缺少必要字段: {field}", level="warning")
                        return False
                return True
            except Exception as e:
                self.log(f"解析草稿 front matter 失败: {str(e)}", level="warning")
                # 尝试修复
                fixed_content = self._fix_frontmatter_quotes(content)
                try:
                    post = frontmatter.loads(fixed_content)
                    return True
                except Exception:
                    return False
        except Exception:
            return False
    
    def _get_available_categories(self) -> Dict[str, List[str]]:
        """获取可用的分类和标签"""
        return self.templates.get('categories', {})
    
    def _suggest_categories(self, content: str) -> List[str]:
        """根据内容建议分类"""
        categories = []
        available_cats = self._get_available_categories()
        
        if not available_cats:
            self.log("❌ 无法获取可用分类", level="error")
            return []
            
        # 将内容转为小写以进行不区分大小写的匹配
        content_lower = content.lower()
        
        # 主分类关键词映射（增加更多关键词以提高匹配准确性）
        category_keywords = {
            "人工智能": ["ai", "人工智能", "机器学习", "深度学习", "神经网络", "大模型", "llm", "chatgpt", "gemini"],
            "学习成长": ["学习", "成长", "教育", "知识", "技能", "思维", "认知", "思考", "阅读"],
            "量化交易": ["量化", "交易", "策略", "投资", "股票", "期货", "金融", "市场", "回测"],
            "技术实践": ["技术", "编程", "开发", "部署", "工具", "软件", "应用", "云服务", "代码"],
            "美国见闻": ["美国", "留学", "海外", "国外", "见闻", "生活", "文化", "教育", "体验"],
            "智能理财": ["理财", "投资", "基金", "股票", "资产", "财务", "金融", "收益", "风险"],
            "项目与创新": ["项目", "创新", "创业", "产品", "设计", "方案", "解决方案", "创意", "发明"]
        }
        
        # 先尝试使用关键词匹配
        for main_cat, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in content_lower:
                    categories.append(main_cat)
                    break
        
        # 如果没有匹配到关键词，尝试使用子分类匹配
        if not categories:
            for main_cat, sub_cats in available_cats.items():
                for sub_cat in sub_cats:
                    if sub_cat.lower() in content_lower:
                        categories.append(main_cat)
                        break
        
        # 如果仍然没有匹配到，返回默认分类
        if not categories:
            self.log("⚠️ 无法匹配到合适的分类，使用默认分类", level="warning")
            return ["技术实践"]
            
        self.log(f"通过关键词匹配找到分类: {categories}", level="info")
        return list(set(categories))  # 去重

    def _analyze_content_categories(self, content: str) -> Tuple[List[str], List[str]]:
        """使用 Gemini 分析文章内容，返回建议的分类和标签"""
        try:
            # 获取可用分类
            available_cats = self._get_available_categories()
            if not available_cats:
                self.log("❌ 无法获取可用分类", level="error")
                return [], []
                
            self.log(f"可用分类: {list(available_cats.keys())}", level="debug")
            
            # 构建 prompt
            prompt = f"""
            请分析以下文章内容，并从给定的分类中选择最合适的主分类和子分类，同时生成相关标签。
            
            可用的分类结构：
            {yaml.dump(available_cats, allow_unicode=True)}
            
            要求：
            1. 返回1-2个主分类
            2. 每个主分类下选择1-2个最相关的子分类
            3. 生成3-5个相关标签
            4. 使用JSON格式返回结果，格式如下：
            {{
                "categories": ["主分类1", "主分类2"],
                "tags": ["标签1", "标签2", "标签3", "标签4", "标签5"]
            }}
            
            文章内容：
            {content[:3000]}  # 增加内容长度，提高分析准确性
            """
            
            self.log("开始分析文章分类和标签...", level="info")
            response = self.model.generate_content(prompt)
            
            if response:
                try:
                    # 尝试解析JSON响应
                    result_text = response.text.strip()
                    # 如果响应不是以{开头，尝试提取JSON部分
                    if not result_text.startswith('{'):
                        json_start = result_text.find('{')
                        json_end = result_text.rfind('}') + 1
                        if json_start >= 0 and json_end > json_start:
                            result_text = result_text[json_start:json_end]
                    
                    result = json.loads(result_text)
                    categories = result.get('categories', [])
                    tags = result.get('tags', [])
                    
                    self.log(f"✅ 分析完成，建议分类: {categories}", level="info")
                    self.log(f"✅ 分析完成，建议标签: {tags}", level="info")
                    
                    return categories, tags
                except json.JSONDecodeError as e:
                    self.log(f"JSON解析失败: {str(e)}", level="warning")
                    self.log(f"原始响应: {response.text[:200]}...", level="debug")
                    # 失败时回退到简单匹配
                    categories = self._suggest_categories(content)
                    self.log(f"使用简单匹配的分类: {categories}", level="info")
                    return categories, []
            else:
                self.log("❌ 模型未返回响应", level="error")
                return self._suggest_categories(content), []
                
        except Exception as e:
            self.log(f"分析文章分类时出错: {str(e)}", level="error")
            # 失败时回退到简单匹配
            categories = self._suggest_categories(content)
            self.log(f"使用简单匹配的分类: {categories}", level="info")
            return categories, []
    
    def _replace_images(self, content: str, images: Dict[str, str]) -> str:
        """替换内容中的图片URL"""
        if not images:
            self.log("没有图片需要替换", level="warning")
            return content
        
        replaced_count = 0
        for local_name, cloudflare_id in images.items():
            # 确保不重复添加前缀，检查cloudflare_id是否已经是完整URL
            if cloudflare_id.startswith("https://imagedelivery.net"):
                cloudflare_url = cloudflare_id
            else:
                cloudflare_url = f"https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/{cloudflare_id}/public"
            
            # 匹配各种可能的图片引用格式
            patterns = [
                f'!\\[([^\\]]*)\\]\\(/assets/images/posts/.*?/{re.escape(local_name)}\\)',  # 完整路径
                f'!\\[([^\\]]*)\\]\\(/assets/images/{re.escape(local_name)}\\)',           # 简化路径
                f'!\\[([^\\]]*)\\]\\({re.escape(local_name)}\\)'                           # 仅文件名
            ]
            
            # 检查这个特定图片是否已经有Cloudflare URL，避免重复替换
            cloudflare_pattern = f'!\\[([^\\]]*)\\]\\({re.escape(cloudflare_url)}\\)'
            if re.search(cloudflare_pattern, content):
                self.log(f"⚠️ 图片 {local_name} 已有Cloudflare URL，跳过替换", level="debug")
                continue
            
            replaced_this_image = False
            for pattern in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, f'![\\1]({cloudflare_url})', content)
                    replaced_count += len(matches)
                    replaced_this_image = True
            
            if replaced_this_image:
                self.log(f"✅ 替换图片URL: {local_name} -> {cloudflare_url}", level="info")
        
        if replaced_count > 0:
            self.log(f"总共替换了 {replaced_count} 处图片引用", level="info")
        else:
            self.log("没有找到需要替换的图片引用", level="warning")
        return content

    def _update_header_images(self, post: dict, images: Dict[str, str]) -> dict:
        """更新文章头部的图片URL"""
        if not images:
            self.log("没有图片需要更新头部", level="warning")
            return post
        
        if 'header' not in post:
            self.log("文章没有header部分", level="warning")
            return post
        
        updated_count = 0
        for img_field in ['image', 'og_image', 'overlay_image', 'teaser']:
            if img_field in post['header']:
                img_path = post['header'][img_field]
                if not img_path:
                    continue
                
                img_name = Path(img_path).name
                
                if img_name in images:
                    # 检查是否已经是Cloudflare URL
                    if img_path.startswith("https://imagedelivery.net"):
                        self.log(f"⚠️ 头图 {img_field} 已是Cloudflare URL，跳过替换", level="debug")
                        continue
                    
                    # 确保不重复添加前缀
                    cloudflare_id = images[img_name]
                    if cloudflare_id.startswith("https://imagedelivery.net"):
                        cloudflare_url = cloudflare_id
                    else:
                        cloudflare_url = f"https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/{cloudflare_id}/public"
                    
                    post['header'][img_field] = cloudflare_url
                    updated_count += 1
                    self.log(f"✅ 更新头图: {img_field} = {img_name} -> {cloudflare_url}", level="info")
        
        if updated_count > 0:
            self.log(f"总共更新了 {updated_count} 处头部图片", level="info")
        return post

def main():
    parser = argparse.ArgumentParser(description="内容处理流水线")
    parser.add_argument("--config", type=str, help="配置文件路径")
    parser.add_argument("--verbose", action="store_true", help="启用详细日志")
    
    args = parser.parse_args()
    
    pipeline = ContentPipeline(args.config, args.verbose)
    
    # 选择操作
    print("\n请选择操作：")
    print("1. 处理现有草稿")
    print("2. 生成测试文章")
    
    choice = input("\n请输入选项 (1/2): ").strip()
    
    if choice == "1":
        # 处理现有草稿
        draft = pipeline.select_draft()
        if not draft:
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