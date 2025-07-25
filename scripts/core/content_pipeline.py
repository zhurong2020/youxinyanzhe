import os
import re
import yaml
import logging
import subprocess
import shutil
import frontmatter
import json
import time
import uuid
import tempfile
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, Union, Set
from datetime import datetime
import google.generativeai as genai
from google.generativeai.client import configure
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.types import GenerationConfig, BlockedPromptException
from google.api_core.exceptions import ResourceExhausted
import argparse
import requests
from dotenv import load_dotenv

# 导入本地模块
try:
    from .wechat_publisher import WechatPublisher
except ImportError:
    from scripts.core.wechat_publisher import WechatPublisher

# 内容变现系统（可选导入）
RewardSystemManager = None
try:
    from ..utils.reward_system_manager import RewardSystemManager
except ImportError:
    try:
        from scripts.utils.reward_system_manager import RewardSystemManager
    except ImportError:
        pass  # 内容变现系统模块不可用

class PublishingStatusManager:
    """发布状态管理器"""
    
    def __init__(self, drafts_dir: Path):
        self.drafts_dir = Path(drafts_dir)
        self.status_dir = self.drafts_dir / ".publishing"
        self.status_dir.mkdir(exist_ok=True)
        
    def get_status_file_path(self, article_name: str) -> Path:
        """获取文章状态文件路径"""
        # 移除文件扩展名
        article_name = article_name.replace('.md', '')
        return self.status_dir / f"{article_name}.yml"
    
    def get_published_platforms(self, article_name: str) -> List[str]:
        """获取文章已发布的平台列表"""
        status_file = self.get_status_file_path(article_name)
        
        if not status_file.exists():
            return []
            
        try:
            with open(status_file, 'r', encoding='utf-8') as f:
                status_data = yaml.safe_load(f) or {}
            return status_data.get('published_platforms', [])
        except Exception:
            return []
    
    def update_published_platforms(self, article_name: str, platforms: List[str]):
        """更新文章的发布平台列表"""
        status_file = self.get_status_file_path(article_name)
        
        # 读取现有状态
        status_data = {}
        if status_file.exists():
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    status_data = yaml.safe_load(f) or {}
            except Exception:
                status_data = {}
        
        # 更新发布平台列表（合并，避免重复）
        existing_platforms = set(status_data.get('published_platforms', []))
        new_platforms = set(platforms)
        all_platforms = list(existing_platforms.union(new_platforms))
        
        # 更新状态数据
        status_data.update({
            'article_name': article_name,
            'published_platforms': all_platforms,
            'last_updated': datetime.now().isoformat(),
            'total_publications': len(all_platforms)
        })
        
        # 保存状态文件
        try:
            with open(status_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump(status_data, f, default_flow_style=False, 
                             allow_unicode=True, sort_keys=False)
        except Exception as e:
            logging.error(f"保存发布状态失败: {e}")
    
    def get_available_platforms(self, article_name: str, all_platforms: List[str]) -> List[str]:
        """获取文章可发布的平台列表（排除已发布的）"""
        published_platforms = set(self.get_published_platforms(article_name))
        available_platforms = [p for p in all_platforms if p not in published_platforms]
        return available_platforms
    
    def initialize_legacy_post_status(self, posts_dir: Path):
        """初始化存量已发布文档的状态"""
        if not posts_dir.exists():
            return
            
        legacy_count = 0
        for post_file in posts_dir.glob("*.md"):
            article_name = post_file.stem
            
            # 检查是否已有状态文件
            if self.get_status_file_path(article_name).exists():
                continue
                
            # 为存量文档创建状态记录（默认已在github_pages发布）
            self.update_published_platforms(article_name, ['github_pages'])
            legacy_count += 1
            
        if legacy_count > 0:
            logging.info(f"已为 {legacy_count} 个存量文档初始化发布状态")
        
        return legacy_count

class ContentPipeline:
    _instance = None  # 类属性用于单例模式
    _initialized = False  # 记录是否已初始化
    
    def __init__(self, config_path: str = "config/pipeline_config.yml", verbose: bool = False):
        """初始化内容处理管道
        Args:
            config_path: 配置文件路径
            verbose: 是否输出详细日志
        """
        self.verbose = verbose
        self.logger = logging.getLogger("ContentPipeline")
        self.project_root = Path(__file__).parent.parent
        
        # 初始化API状态
        self.api_available = True
        
        # 记录是否是首次初始化
        self.is_first_init = not ContentPipeline._initialized
        
        # 加载配置
        try:
            # 加载主配置文件
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            self.logger.debug(f"加载配置文件: {config_path}")
            
            # 加载完整配置（包括导入的配置文件）
            self.config = self._load_config()
            
            # 初始化发布状态管理器
            drafts_dir = Path(self.config["paths"]["drafts"])
            self.status_manager = PublishingStatusManager(drafts_dir)
            
            # 初始化存量文档状态
            posts_dir = Path(self.config["paths"]["posts"])
            self.status_manager.initialize_legacy_post_status(posts_dir)
            
            # 初始化内容变现系统管理器（可选）
            self.reward_manager = None
            if RewardSystemManager:
                try:
                    self.reward_manager = RewardSystemManager()
                    self.logger.debug("内容变现系统管理器初始化成功")
                except Exception as e:
                    self.logger.warning(f"内容变现系统管理器初始化失败: {e}")
            else:
                self.logger.debug("内容变现系统模块未找到，跳过初始化")
            

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

        # 初始化发布器
        self.wechat_publisher = None
        try:
            if self.platforms_config.get("wechat", {}).get("enabled", False):
                # Pass the initialized Gemini model to the publisher
                self.wechat_publisher = WechatPublisher(gemini_model=self.model)
                self.log("✅ 微信发布器初始化成功", level="debug")
        except Exception as e:
            self.log(f"⚠️ 微信发布器初始化失败: {e}", level="warning")
            self.log("微信发布功能将不可用，但不影响其他功能", level="info")
        
        # 标记初始化完成
        ContentPipeline._initialized = True
        if self.is_first_init:
            self.log("🚀 系统初始化完成", level="info")
        
    def log(self, message: str, level: str = "info", force: bool = False):
        """统一的日志处理
        Args:
            message: 日志消息
            level: 日志级别 (debug/info/warning/error)
            force: 是否强制显示（忽略verbose设置）
        """
        # 统一使用logging系统，让处理器决定级别过滤
        logger_method = getattr(self.logger, level, self.logger.info)
        
        # 如果force=True或者是高级别日志，则直接记录
        if force or level in ["error", "warning"]:
            logger_method(message)
        elif level == "debug":
            # DEBUG级别只在verbose模式下记录
            if self.verbose:
                logger_method(message)
        else:
            # INFO级别正常记录
            logger_method(message)
    
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
        
        # 清除根记录器的处理器以避免重复记录
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # 文件处理器 - 使用轮转处理器防止日志文件过大
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_path, 
            maxBytes=1024*1024,  # 1MB
            backupCount=3,       # 保留3个备份文件
            encoding='utf-8'
        )
        # 只记录INFO级别及以上的消息到文件
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        
        # 控制台处理器 - 根据详细模式决定级别
        console_handler = logging.StreamHandler()
        if self.verbose:
            console_handler.setLevel(logging.DEBUG)
        else:
            console_handler.setLevel(logging.WARNING)  # 只显示警告和错误
        console_formatter = logging.Formatter("%(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        
        # 不再设置根记录器的处理器，只使用ContentPipeline特定记录器
        
        # 设置ContentPipeline特定的logger，但不添加重复处理器
        self.logger.setLevel(logging.DEBUG)
        # 防止消息传播到根记录器，避免重复记录
        self.logger.propagate = False
        # 清除现有处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        # 只给ContentPipeline logger添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # 记录初始化状态（仅在详细模式下）
        if self.verbose:
            self.log("📄 日志系统初始化完成", level="debug")
    
    def _setup_apis(self):
        """设置API客户端"""
        load_dotenv(override=True)  # 确保重新加载环境变量
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        try:
            configure(api_key=api_key)
            
            # 使用配置文件中的模型名称
            model_name = self.config["content_processing"]["gemini"]["model"]
            if self.is_first_init:
                self.log(f"使用配置的模型: {model_name}", level="info")
            else:
                self.log(f"使用配置的模型: {model_name}", level="debug")
            # 创建模型实例
            self.model = GenerativeModel(model_name)
            
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
                    if self.is_first_init:
                        self.log("✅ Gemini API 连接成功", level="info")
                    else:
                        self.log("✅ Gemini API 连接成功", level="debug")
                    
                    # 验证模板加载
                    self._validate_templates()
            except ResourceExhausted as e:
                self.log(f"❌ API 配额已耗尽，请稍后再试: {str(e)}", level="error", force=True)
                # 不抛出异常，允许程序继续运行，但标记API不可用
                self.api_available = False
            except Exception as e:
                self.log(f"❌ Gemini API 连接测试失败: {str(e)}", level="error", force=True)
                self.api_available = False
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
                self.log(f"默认前端模板包含 {len(default_template)} 个设置", level="debug")
                # 检查关键设置
                if 'toc' in default_template and default_template['toc']:
                    self.log("✅ 目录设置已加载", level="debug")
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
            self.log(f"页脚模板平台: {footer_platforms}", level="debug")
            
            # 检查GitHub Pages页脚
            if 'github_pages' in self.templates['footer']:
                footer_content = self.templates['footer']['github_pages']
                if footer_content and len(footer_content) > 10:
                    self.log("✅ GitHub Pages页脚模板已加载", level="debug")
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
            print("📝 没有找到草稿文件")
            print("\n💡 提示：")
            print("   1. 您可以在 _drafts/ 目录创建新的 .md 文件")
            print("   2. 或者选择主菜单的 '3. 生成测试文章' 选项")
            print("   3. 或者使用 '2. 重新发布已发布文章' 将已发布文章转为草稿")
            
            while True:
                choice = input("\n是否现在生成测试文章？(y/N): ").strip().lower()
                if choice in ['y', 'yes']:
                    return self.generate_test_content()
                elif choice in ['n', 'no', '']:
                    return None
                else:
                    print("请输入 y 或 N")
            
        print("\n可用的草稿文件：")
        for i, draft in enumerate(drafts, 1):
            print(f"{i}. {draft.name}")
        print("0. 退出")
            
        while True:
            try:
                choice = int(input("\n请选择要处理的草稿 (输入序号，0退出): "))
                if choice == 0:
                    return None
                if 1 <= choice <= len(drafts):
                    return drafts[choice-1]
                print("无效的选择")
            except ValueError:
                print("请输入有效的数字")
    
    def list_published_posts(self) -> List[Path]:
        """列出已发布的文章"""
        posts_dir = Path(self.config["paths"]["posts"])
        if not posts_dir.exists():
            return []
        
        posts = []
        for file in posts_dir.glob("*.md"):
            if file.is_file():
                posts.append(file)
        
        return sorted(posts, key=lambda x: x.stat().st_mtime, reverse=True)
    
    def select_published_post(self) -> Optional[Path]:
        """让用户选择要重新发布的已发布文章"""
        posts = self.list_published_posts()
        if not posts:
            print("没有找到已发布的文章")
            return None
            
        print("\n可用的已发布文章：")
        for i, post in enumerate(posts, 1):
            # 获取文章的发布状态
            article_name = post.stem
            published_platforms = self.status_manager.get_published_platforms(article_name)
            
            if published_platforms:
                platforms_str = ", ".join(published_platforms)
                print(f"{i}. {post.name} [已发布: {platforms_str}]")
            else:
                print(f"{i}. {post.name} [未发布到任何平台]")
        print("0. 退出")
            
        while True:
            try:
                choice = int(input("\n请选择要重新发布的文章 (输入序号，0退出): "))
                if choice == 0:
                    return None
                if 1 <= choice <= len(posts):
                    return posts[choice-1]
                print("无效的选择")
            except ValueError:
                print("请输入有效的数字")
    
    def copy_post_to_draft(self, post_path: Path) -> Optional[Path]:
        """将已发布文章作为源文件复制到草稿目录（如果不存在）"""
        try:
            drafts_dir = Path(self.config["paths"]["drafts"])
            drafts_dir.mkdir(exist_ok=True)
            
            # 检查是否已有同名草稿（源文件）
            original_draft_path = drafts_dir / post_path.name
            
            if original_draft_path.exists():
                # 如果草稿已存在，直接使用草稿作为源文件
                self.log(f"使用现有草稿作为源文件: {original_draft_path}", level="info", force=True)
                return original_draft_path
            else:
                # 如果草稿不存在，从已发布文章创建源文件
                # 需要清理发布时添加的内容，恢复为源文件格式
                source_content = self._convert_published_to_source(post_path)
                
                with open(original_draft_path, 'w', encoding='utf-8') as f:
                    f.write(source_content)
                
                self.log(f"已从发布文章创建源文件: {original_draft_path}", level="info", force=True)
                return original_draft_path
            
        except Exception as e:
            self.log(f"处理文章源文件失败: {str(e)}", level="error", force=True)
            return None
    
    def _convert_published_to_source(self, post_path: Path) -> str:
        """将已发布文章转换回源文件格式"""
        try:
            with open(post_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析front matter
            post = frontmatter.loads(content)
            
            # 移除发布时自动添加的字段
            auto_generated_fields = [
                'layout', 'author_profile', 'breadcrumbs', 'comments', 
                'related', 'share', 'toc', 'toc_icon', 'toc_label', 
                'toc_sticky', 'last_modified_at'
            ]
            
            for field in auto_generated_fields:
                if field in post.metadata:
                    del post.metadata[field]
            
            # 移除页脚内容（从最后一个 "---" 开始的部分）
            content_lines = post.content.split('\n')
            footer_start = -1
            
            # 从后往前查找页脚分隔符
            for i in range(len(content_lines) - 1, -1, -1):
                if content_lines[i].strip() == '---' and i < len(content_lines) - 5:
                    # 检查后面几行是否包含页脚特征（如"学习分享声明"或"请我喝咖啡"）
                    footer_section = '\n'.join(content_lines[i:])
                    if any(keyword in footer_section for keyword in 
                          ['学习分享声明', '请我喝咖啡', 'Buy Me A Coffee', '发表评论']):
                        footer_start = i
                        break
            
            if footer_start > 0:
                post.content = '\n'.join(content_lines[:footer_start]).rstrip()
            
            # 重新组装为source格式
            return frontmatter.dumps(post)
            
        except Exception as e:
            self.log(f"转换发布文章为源文件失败: {str(e)}", level="warning")
            # 如果转换失败，返回原内容
            with open(post_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def select_platforms(self, draft_path: Optional[Path] = None) -> List[str]:
        """让用户选择发布平台，支持基于发布状态的过滤"""
        all_platforms = [name for name, config in self.config["platforms"].items() 
                        if config.get("enabled", False)]
        
        if draft_path:
            # 获取文章名称
            article_name = draft_path.stem
            
            # 获取已发布平台和可用平台
            published_platforms = self.status_manager.get_published_platforms(article_name)
            available_platforms = self.status_manager.get_available_platforms(article_name, all_platforms)
            
            if published_platforms:
                print(f"\n文章 '{article_name}' 已发布平台: {', '.join(published_platforms)}")
            
            if not available_platforms:
                print("该文章已在所有启用的平台发布")
                return []
                
            print("\n可选的发布平台：")
            for i, platform in enumerate(available_platforms, 1):
                print(f"{i}. {platform}")
            print("0. 退出")
                
            platform_list = available_platforms
        else:
            # 新文章，显示所有可用平台
            print("\n可用的发布平台：")
            for i, platform in enumerate(all_platforms, 1):
                print(f"{i}. {platform}")
            print("0. 退出")
                
            platform_list = all_platforms
            
        if not platform_list:
            return []
            
        selections = input("\n请选择发布平台 (多个平台用逗号分隔，0退出): ").split(",")
        selected_platforms = []
        
        for sel in selections:
            sel_stripped = sel.strip()
            if not sel_stripped:  # 跳过空字符串
                continue
            try:
                idx = int(sel_stripped)
                if idx == 0:
                    return []  # 用户选择退出
                elif 1 <= idx <= len(platform_list):
                    selected_platforms.append(platform_list[idx - 1])
                else:
                    print(f"无效选择: {sel_stripped}")
            except ValueError:
                print(f"无效输入: {sel_stripped}")
                
        return selected_platforms
    
    def ask_monetization_preference(self) -> bool:
        """询问用户是否启用内容变现功能"""
        if not self.reward_manager:
            return False
        
        print("\n💰 内容变现选项：")
        print("  1. 启用 - 自动生成资料包并上传到GitHub Release")
        print("  2. 跳过 - 仅进行常规发布")
        
        try:
            choice = input("\n请选择 (1/2，默认为2): ").strip()
            
            if choice == "1":
                print("✅ 已启用内容变现功能")
                return True
            else:
                print("⏭️  跳过内容变现功能")
                return False
        except (EOFError, KeyboardInterrupt):
            print("\n⏭️  跳过内容变现功能")
            return False
    
    def process_draft(self, draft_path: Path, platforms: List[str], enable_monetization: bool = False) -> dict:
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
                    return {
                        'success': False,
                        'successful_platforms': [],
                        'total_platforms': len(platforms),
                        'published_platforms': [],
                        'article_name': draft_path.stem,
                        'error': '文章内容过短'
                    }
                
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
                        return {
                            'success': False,
                            'successful_platforms': [],
                            'total_platforms': len(platforms),
                            'published_platforms': [],
                            'article_name': draft_path.stem,
                            'error': f'front matter解析失败: {str(e)}'
                        }
                
                # 2. 图片处理步骤（已移除Cloudflare Images功能）
                progress.update(progress.add_task("🖼️ 图片处理（跳过）", total=1), completed=True)
                
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
                    try:
                        platform_content = self._generate_platform_content(
                            polished_content,
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
                    except ValueError as e:
                        # 处理必需字段验证失败
                        self.log(f"❌ {platform}平台处理失败: {str(e)}", level="error", force=True)
                        platform_success[platform] = False
                        all_success = False
                    except Exception as e:
                        # 处理其他错误
                        self.log(f"❌ {platform}平台处理出错: {str(e)}", level="error", force=True)
                        platform_success[platform] = False
                        all_success = False
                    
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
                        publish_success = self._publish_to_wechat(content)
                        platform_success[platform] = publish_success
                    elif platform == "wordpress":
                        publish_success = self._publish_to_wordpress(content)
                        platform_success[platform] = publish_success
                    progress.update(task, completed=True)
                
                # 检查所有平台是否都成功
                all_success = all_success and all(platform_success.values())
                
                # 6. 更新发布状态
                successful_platforms = [platform for platform, success in platform_success.items() if success]
                if successful_platforms:
                    task = progress.add_task("📊 更新发布状态...", total=None)
                    article_name = draft_path.stem
                    self.status_manager.update_published_platforms(article_name, successful_platforms)
                    self.log(f"已更新发布状态: {successful_platforms}", level="info", force=True)
                    progress.update(task, completed=True)
                
                # 7. 归档草稿（仅当首次发布且全部成功时）
                published_platforms = self.status_manager.get_published_platforms(draft_path.stem)
                all_enabled_platforms = [name for name, config in self.config["platforms"].items() 
                                        if config.get("enabled", False)]
                
                # 如果已在所有启用平台发布，则归档草稿
                archived_file_path = None
                if set(published_platforms) >= set(all_enabled_platforms):
                    task = progress.add_task("📦 归档草稿...", total=None)
                    archived_file_path = self._archive_draft(draft_path)
                    progress.update(task, completed=True)
                elif not all_success:
                    self.log("⚠️ 处理未完全成功，跳过归档步骤", level="warning", force=True)
                else:
                    # 计算未发布的平台
                    unpublished_platforms = set(all_enabled_platforms) - set(published_platforms)
                    self.log(f"💾 已发布到: {', '.join(published_platforms) if published_platforms else '无'}", level="info", force=True)
                    self.log(f"📋 未发布平台: {', '.join(unpublished_platforms)} (可稍后发布)", level="info", force=True)
                
            # 内容变现处理
            monetization_result = None
            if enable_monetization and self.reward_manager and all_success:
                try:
                    task = progress.add_task("💰 创建内容变现包...", total=None)
                    
                    # 使用已发布的文章路径（如果已发布到GitHub Pages）
                    if 'github' in published_platforms:
                        # 使用_posts目录中的文章
                        posts_dir = Path(self.config["paths"]["posts"])
                        # 使用原始文件名，不管是否已归档
                        original_filename = archived_file_path.name if archived_file_path else draft_path.name
                        published_article_path = posts_dir / original_filename
                        
                        if published_article_path.exists():
                            monetization_success, monetization_data = self.reward_manager.create_article_package(
                                str(published_article_path), 
                                upload_to_github=True
                            )
                            
                            if monetization_success:
                                monetization_result = {
                                    'success': True,
                                    'package_path': monetization_data.get('package_path'),
                                    'github_release': monetization_data.get('github_release', {})
                                }
                                self.log(f"✅ 内容变现包创建成功", level="info", force=True)
                                if monetization_data.get('github_release', {}).get('success'):
                                    download_url = monetization_data['github_release']['download_url']
                                    self.log(f"📦 下载链接: {download_url}", level="info", force=True)
                            else:
                                monetization_result = {
                                    'success': False,
                                    'error': monetization_data.get('error', '未知错误')
                                }
                                self.log(f"⚠️ 内容变现包创建失败: {monetization_data.get('error')}", level="warning", force=True)
                        else:
                            self.log(f"⚠️ 已发布文章未找到: {published_article_path}", level="warning", force=True)
                    else:
                        # 使用草稿文件或归档文件
                        source_file_path = archived_file_path if archived_file_path and archived_file_path.exists() else draft_path
                        
                        if not source_file_path.exists():
                            self.log(f"⚠️ 源文件不存在: {source_file_path}", level="warning", force=True)
                            monetization_result = {
                                'success': False,
                                'error': f'源文件不存在: {source_file_path}'
                            }
                        else:
                            monetization_success, monetization_data = self.reward_manager.create_article_package(
                                str(source_file_path), 
                                upload_to_github=True
                            )
                            
                            if monetization_success:
                                monetization_result = {
                                    'success': True,
                                    'package_path': monetization_data.get('package_path'),
                                    'github_release': monetization_data.get('github_release', {})
                                }
                                self.log(f"✅ 内容变现包创建成功", level="info", force=True)
                                if monetization_data.get('github_release', {}).get('success'):
                                    download_url = monetization_data['github_release']['download_url']
                                    self.log(f"📦 下载链接: {download_url}", level="info", force=True)
                            else:
                                monetization_result = {
                                    'success': False,
                                    'error': monetization_data.get('error', '未知错误')
                                }
                                self.log(f"⚠️ 内容变现包创建失败: {monetization_data.get('error')}", level="warning", force=True)
                    
                    progress.update(task, completed=True)
                    
                except Exception as e:
                    monetization_result = {
                        'success': False,
                        'error': str(e)
                    }
                    self.log(f"❌ 内容变现处理异常: {str(e)}", level="error", force=True)
                
            # 返回详细的发布结果
            result = {
                'success': all_success,
                'successful_platforms': successful_platforms if 'successful_platforms' in locals() else [],
                'total_platforms': len(platforms),
                'published_platforms': published_platforms if 'published_platforms' in locals() else [],
                'article_name': draft_path.stem,
                'monetization': monetization_result
            }
            return result
            
        except Exception as e:
            self.logger.error(f"处理草稿时出错: {str(e)}")
            return {
                'success': False,
                'successful_platforms': [],
                'total_platforms': len(platforms),
                'published_platforms': [],
                'article_name': draft_path.stem,
                'error': str(e)
            }
    
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
            
        except ResourceExhausted as e:
            self.log(f"API配额已用尽: {str(e)}", level="error", force=True)
            self.api_available = False
            return content
        except Exception as e:
            self.log(f"润色内容时出错: {str(e)}", level="error")
            return content
    
    def _validate_required_fields(self, post: frontmatter.Post) -> Tuple[bool, List[str]]:
        """验证必需字段是否存在
        
        Args:
            post: frontmatter.Post对象
            
        Returns:
            Tuple[bool, List[str]]: (是否通过验证, 缺失的字段列表)
        """
        required_fields = ['title', 'date', 'header']
        missing_fields = []
        
        for field in required_fields:
            if field not in post or not post[field]:
                missing_fields.append(field)
        
        return len(missing_fields) == 0, missing_fields

    def _generate_excerpt(self, content: str) -> str:
        """生成文章摘要
        
        Args:
            content: 文章内容
            
        Returns:
            str: 生成的摘要
        """
        try:
            if not self.api_available:
                self.log("API不可用，无法生成摘要", level="warning")
                return ""
            
            # 构建提示词
            prompt = f"""
请为以下文章生成一个50字左右的摘要，要求：
1. 准确概括文章主要内容
2. 语言简洁明了
3. 吸引读者阅读
4. 字数控制在50字左右

文章内容：
{content[:2000]}  # 只取前2000字符避免过长
"""
            
            # 调用API生成摘要
            model = GenerativeModel(self.config['content_processing']['gemini']['model'])
            response = model.generate_content(
                prompt,
                generation_config=GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=200,  # 摘要不需要太长
                    top_p=0.8,
                ),
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
            )
            
            # 检查finish_reason
            if response and hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason') and candidate.finish_reason != 1:  # 1 = STOP (正常完成)
                    self.log(f"API响应被过滤，finish_reason: {candidate.finish_reason}", level="warning")
                    return ""
            
            if response and hasattr(response, 'text') and response.text:
                excerpt = response.text.strip()
                self.log(f"生成摘要: {excerpt}", level="info")
                return excerpt
            elif response and hasattr(response, 'parts') and response.parts:
                # 尝试从parts获取文本
                text_parts = [part.text for part in response.parts if hasattr(part, 'text')]
                if text_parts:
                    excerpt = ''.join(text_parts).strip()
                    self.log(f"生成摘要: {excerpt}", level="info")
                    return excerpt
            
            self.log("API未返回有效摘要", level="warning")
            return ""
                
        except Exception as e:
            self.log(f"生成摘要时出错: {str(e)}", level="error")
            return ""

    def _generate_platform_content(self, content: str, platform: str, draft_path: Path) -> str:
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
            
            # 验证必需字段
            is_valid, missing_fields = self._validate_required_fields(post)
            if not is_valid:
                self.log(f"❌ 草稿缺少必需字段: {', '.join(missing_fields)}", level="error", force=True)
                self.log(f"必需字段包括: title, date, header", level="error", force=True)
                raise ValueError(f"缺少必需字段: {', '.join(missing_fields)}")
            
            # 确保内容完整性
            if not post.content:
                self.log("❌ 文章内容为空", level="error", force=True)
                return content
            content_text = post.content
            
            # 应用默认模板（强制覆盖自动生成字段）
            default_template = self.templates.get('front_matter', {}).get('default', {})
            for key, value in default_template.items():
                post[key] = value  # 强制覆盖，不检查是否存在
                self.log(f"应用默认模板: {key}={value}", level="info")
            
            # 添加或更新最后修改时间
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            post['last_modified_at'] = current_time
            self.log(f"更新最后修改时间: {current_time}", level="info")
            
            # 智能处理excerpt字段
            if 'excerpt' not in post or not post['excerpt']:
                generated_excerpt = self._generate_excerpt(content_text)
                if generated_excerpt:
                    post['excerpt'] = generated_excerpt
                    self.log(f"生成文章摘要: {generated_excerpt}", level="info")
                else:
                    self.log("未能生成摘要", level="warning")
            else:
                excerpt_text = str(post.get('excerpt', ''))
                if excerpt_text:
                    self.log(f"保留现有摘要: {excerpt_text[:50]}...", level="info")
                else:
                    self.log("现有摘要为空", level="warning")
            
            # 处理author字段（如果author_profile为true，移除author字段以避免重复）
            if post.get('author_profile', False) and 'author' in post:
                del post['author']
                self.log("移除冗余的author字段", level="info")
            # 如果需要设置作者信息且author_profile不存在，则设置author
            elif platform_config.get('author', None) and not post.get('author_profile', False):
                post['author'] = platform_config.get('author')
                self.log(f"设置作者: {post['author']}", level="info")
            
            
            # 分析分类和标签（如果需要）
            if platform_config.get('analyze_content', True):
                # 分析内容获取分类和标签
                categories, tags = self._analyze_content_categories(content_text)
                
                # 始终更新分类
                if categories:
                    post['categories'] = categories
                    self.log(f"添加分类: {categories}", level="info")
                
                # 仅在没有tags时才添加AI生成的tags
                if tags and ('tags' not in post or not post['tags']):
                    post['tags'] = tags
                    self.log(f"添加标签: {tags}", level="info")
                elif 'tags' in post and post['tags']:
                    self.log(f"保留现有标签: {post['tags']}", level="info")
            
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
            
            # 更新内容
            post.content = content_text
            
            # 验证内容完整性
            result = frontmatter.dumps(post)
            if len(result) < len(content) * 0.9:  # 如果内容减少超过10%
                self.log("⚠️ 警告：生成的内容可能不完整", level="warning", force=True)
            
            # 确保layout字段在frontmatter的第一行
            if 'layout' in post:
                # 使用OrderedDict确保layout字段在最前面
                from collections import OrderedDict
                ordered_post = OrderedDict()
                ordered_post["layout"] = post["layout"]
                
                # 添加其他字段（除了layout和content）
                for key, value in post.metadata.items():
                    if key != 'layout':
                        ordered_post[key] = value
                
                # 创建新的Post对象并设置内容
                final_post = frontmatter.Post(post.content, **ordered_post)
                result = frontmatter.dumps(final_post)
            
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
            
            # 返回新的归档文件路径
            return new_path
            
        except Exception as e:
            logging.error(f"归档草稿时出错: {str(e)}")
            logging.debug("错误详情:", exc_info=True)
            return None
    
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
            
            # 应用默认模板（强制覆盖自动生成字段）
            default_template = self.templates.get('front_matter', {}).get('default', {})
            if default_template:
                for key, value in default_template.items():
                    post[key] = value  # 强制覆盖，不检查是否存在
                    self.log(f"应用默认模板: {key}={value}", level="info")
                self.log(f"已应用默认模板设置", level="info")
            else:
                self.log(f"未找到默认模板设置", level="warning")
            
            # 添加或更新最后修改时间
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            post['last_modified_at'] = current_time
            self.log(f"更新最后修改时间: {current_time}", level="info")
            
            # 更新文章中的图片链接为标准化本地路径
            updated_content = post.content
            for local_name, _ in images.items():
                # 构建旧的本地路径模式
                date_str = draft_path.stem[:10]
                post_name = draft_path.stem[11:]
                old_local_path = f"/assets/images/posts/{date_str[:4]}/{date_str[5:7]}/{post_name}/{local_name}"
                # 新的标准化本地路径
                new_local_path = f"/assets/images/posts/{local_name}"
                
                # 替换内容中的图片链接
                updated_content = updated_content.replace(old_local_path, new_local_path)
                self.log(f"✅ 标准化图片URL: {local_name} -> {new_local_path}", level="info")
                
                # 更新 front matter 中的图片链接
                if hasattr(post, 'metadata') and "header" in post.metadata:
                    header_info = post.metadata["header"]
                    if isinstance(header_info, dict) and "image" in header_info:
                        if header_info["image"] == old_local_path:
                            header_info["image"] = new_local_path
                            post.metadata["header"] = header_info
                            self.log(f"更新 header 图片: {new_local_path}", level="info")
            
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
            
            # 始终解析并重新格式化frontmatter，确保layout字段在最前面
            try:
                post = frontmatter.loads(content)
                
                # 使用OrderedDict确保layout字段在最前面
                if 'layout' in post:
                    from collections import OrderedDict
                    ordered_post = OrderedDict()
                    ordered_post["layout"] = post["layout"]
                    
                    # 添加其他字段（除了layout和content）
                    for key, value in post.metadata.items():
                        if key != 'layout':
                            ordered_post[key] = value
                    
                    # 创建新的Post对象并设置内容
                    final_post = frontmatter.Post(post.content, **ordered_post)
                    content = frontmatter.dumps(final_post)
                else:
                    # 如果没有layout字段，添加一个
                    from collections import OrderedDict
                    ordered_post = OrderedDict()
                    ordered_post["layout"] = "single"
                    
                    # 添加其他字段
                    for key, value in post.metadata.items():
                        ordered_post[key] = value
                    
                    # 创建新的Post对象并设置内容
                    final_post = frontmatter.Post(post.content, **ordered_post)
                    content = frontmatter.dumps(final_post)
                
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

    def _publish_to_wechat(self, content: str) -> bool:
        """发布到微信公众号，根据配置决定是API发布还是生成指南。"""
        self.log("开始处理微信公众号发布...", level="info", force=True)
        if not self.wechat_publisher:
            self.log("微信发布器未初始化，跳过发布。", level="error", force=True)
            return False

        try:
            post = frontmatter.loads(content)
            platform_config = self.platforms_config.get("wechat", {})
            publish_mode = platform_config.get("publish_mode", "guide")  # 默认为 guide 模式

            self.log(f"微信发布模式: {publish_mode.upper()}", level="info", force=True)

            if publish_mode == "api":
                # API模式：直接发布到草稿箱
                media_id = self.wechat_publisher.publish_to_draft(
                    project_root=self.project_root,
                    front_matter=post.metadata,
                    markdown_content=post.content
                )
                if media_id:
                    self.log(f"✅ 成功创建微信草稿，Media ID: {media_id}", force=True)
                    return True
                else:
                    self.log("❌ 通过API创建微信草稿失败。", level="error", force=True)
                    return False
            else:
                # Guide模式：生成手动发布指南
                success = self.wechat_publisher.generate_guide_file(
                    project_root=self.project_root,
                    front_matter=post.metadata,
                    markdown_content=post.content
                )
                if success:
                    self.log("✅ 成功生成微信发布指南文件。", force=True)
                else:
                    self.log("❌ 生成微信发布指南文件失败。", level="error", force=True)
                return success

        except Exception as e:
            self.log(f"发布到微信时发生未知错误: {e}", level="error", force=True)
            self.logger.debug("错误详情:", exc_info=True)
            return False

    def _publish_to_wordpress(self, content: str):
        """发布到WordPress"""
        # TODO: 实现WordPress发布
        logging.info("WordPress发布功能尚未实现")

    def generate_test_content(self) -> Optional[Path]:
        """使用Gemini生成测试文章"""
        try:
            print("🤖 正在使用AI生成测试文章...")
            print("⏳ 正在连接Gemini AI模型，这通常需要15-30秒时间，请耐心等待...")
            print("💡 生成中: 模型正在根据CLAUDE.md规范创建完整的技术博客文章...")
            
            # 检查模型状态
            if not hasattr(self, 'model') or self.model is None:
                print("❌ Gemini模型未初始化")
                logging.error("Gemini模型未初始化")
                return None
            
            prompt = self.config["content_processing"]["gemini"]["prompts"]["test"]
            logging.debug(f"使用的prompt长度: {len(prompt)}")
            
            # 添加重试机制
            max_retries = 2
            for attempt in range(max_retries):
                if attempt > 0:
                    print(f"⚠️ 第{attempt + 1}次尝试生成...")
                    logging.info(f"重试生成测试文章，第{attempt + 1}次尝试")
                
                # 配置安全设置以允许技术内容生成
                safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
                ]
                
                response = self.model.generate_content(
                    prompt,
                    generation_config=GenerationConfig(
                        temperature=self.config["content_processing"]["gemini"]["temperature"],
                        max_output_tokens=self.config["content_processing"]["gemini"]["max_output_tokens"],
                        top_p=self.config["content_processing"]["gemini"]["top_p"]
                    ),
                    safety_settings=safety_settings
                )
                
                # 检查这次尝试是否成功
                if response and hasattr(response, 'candidates') and response.candidates:
                    if len(response.candidates) > 0 and response.candidates[0].content:
                        break  # 成功，跳出重试循环
                
                if attempt == max_retries - 1:
                    print("❌ 多次尝试后仍然生成失败")
                    logging.error("多次尝试后仍然生成失败")
                    return None
            
            if response:
                logging.debug(f"Gemini响应类型: {type(response)}")
                logging.debug(f"Gemini响应属性: candidates={hasattr(response, 'candidates')}, parts={hasattr(response, 'parts')}")
                try:
                    # 获取响应内容
                    if hasattr(response, 'candidates') and response.candidates:
                        if len(response.candidates) > 0 and response.candidates[0].content:
                            content = response.candidates[0].content.parts[0].text
                        else:
                            print("⚠️ Gemini响应中无候选结果")
                            logging.error("Gemini响应中无候选结果")
                            return None
                    elif hasattr(response, 'parts') and response.parts:
                        content = ' '.join(part.text for part in response.parts)
                    else:
                        print("⚠️ Gemini响应格式异常")
                        logging.error(f"Gemini响应格式异常: {type(response)}, hasattr candidates: {hasattr(response, 'candidates')}, hasattr parts: {hasattr(response, 'parts')}")
                        return None
                    
                    logging.debug(f"原始响应类型: {type(content)}")
                    logging.debug(f"原始响应内容: {content[:200]}...")
                    
                    print("✅ AI内容生成完成，正在保存文件...")
                    
                    # 检查响应是否完整（检查是否有明确的结尾）
                    if not self._has_complete_ending(content):
                        print("⚠️ 检测到生成内容可能不完整，正在重新生成...")
                        # 重新生成一次，使用更明确的prompt
                        complete_prompt = prompt + "\n\n【特别强调】文章必须有完整的结尾段落，包含总结或思考问题。"
                        response = self.model.generate_content(
                            complete_prompt,
                            generation_config=GenerationConfig(
                                temperature=0.6,  # 降低随机性，提高稳定性
                                max_output_tokens=self.config["content_processing"]["gemini"]["max_output_tokens"],
                                top_p=0.8
                            ),
                            safety_settings=safety_settings
                        )
                        if hasattr(response, 'candidates') and response.candidates:
                            content = response.candidates[0].content.parts[0].text
                        else:
                            content = ' '.join(part.text for part in response.parts)
                    
                    # 生成时间戳文件名避免覆盖
                    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
                    
                    # 清理和处理AI生成的内容
                    cleaned_content = self._clean_ai_generated_content(content)
                    
                    # 调试信息
                    logging.debug(f"原始内容长度: {len(content)}")
                    logging.debug(f"清理后内容长度: {len(cleaned_content)}")
                    logging.debug(f"原始内容前200字符: {content[:200]}")
                    logging.debug(f"清理后内容前200字符: {cleaned_content[:200] if cleaned_content else 'EMPTY'}")
                    
                    if not cleaned_content.strip():
                        print("❌ AI生成的内容为空或无效")
                        print(f"🔍 调试信息：原始内容长度 {len(content)}, 清理后长度 {len(cleaned_content)}")
                        logging.error(f"AI生成的内容为空或无效 - 原始长度: {len(content)}, 清理后长度: {len(cleaned_content)}")
                        logging.error(f"原始内容示例: {content[:500] if content else 'NONE'}")
                        return None
                    
                    # 检查是否已包含valid front matter
                    if cleaned_content.startswith('---') and cleaned_content.count('---') >= 2:
                        # AI生成的内容已包含front matter，直接使用
                        post_text = cleaned_content
                        print("📝 使用AI生成的完整文章格式")
                    else:
                        # 手动添加front matter
                        from collections import OrderedDict
                        post = OrderedDict()
                        post["title"] = f"AI生成测试文章 - {timestamp}"
                        post["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S +0000")
                        post["header"] = {
                            "overlay_image": "https://1drv.ms/i/c/b5f6bce7f0f6f9f8/EQl5xJjYnAJOhRfDgJ7HZFABL8y5c7d1e2f3g4h5i6j7k8l9?format=webp&width=1200",
                            "overlay_filter": 0.5
                        }
                        post_text = frontmatter.dumps(frontmatter.Post(cleaned_content, **post))
                        print("📝 添加了标准front matter")
                    
                    # 写入文件
                    draft_path = Path(f"_drafts/test-article-{timestamp}.md")
                    draft_path.parent.mkdir(parents=True, exist_ok=True)
                    draft_path.write_text(post_text, encoding='utf-8')
                    
                    print(f"✅ 测试文章已生成: {draft_path}")
                    print(f"📝 文章长度: {len(content)} 字符")
                    logging.info(f"✅ 已生成测试文章: {draft_path} (长度: {len(content)} 字符)")
                    
                    # 记录测试文章生成的详细信息
                    lines = post_text.count('\n') + 1
                    self.log(f"测试文章生成详情 - 文件: {draft_path}, 总长度: {len(content)}字符, 行数: {lines}行", level="info", force=True)
                    return draft_path
                    
                except Exception as e:
                    logging.error(f"处理响应内容时出错: {str(e)}")
                    logging.debug("错误详情:", exc_info=True)
                    return None
            else:
                print("❌ Gemini API返回空响应")
                logging.error("Gemini API返回空响应")
                return None
                
        except Exception as e:
            logging.error(f"生成测试文章失败: {str(e)}")
            logging.debug("错误详情:", exc_info=True)
            return None
    
    def _has_complete_ending(self, content: str) -> bool:
        """检查文章是否有完整的结尾"""
        # 检查是否以句号、问号或感叹号结尾
        content = content.strip()
        if not content:
            return False
            
        # 检查最后几行是否包含明显的结尾标识
        lines = content.split('\n')
        last_lines = '\n'.join(lines[-5:])  # 检查最后5行
        
        # 检查结尾特征
        ending_indicators = [
            '？', '。', '！',  # 中文标点
            '?', '.', '!',     # 英文标点
            '思考', '总结', '结论', '展望', '未来',
            '问题', '挑战', '机遇', '发展'
        ]
        
        # 检查是否包含结尾指示词
        has_ending_word = any(indicator in last_lines for indicator in ending_indicators)
        
        # 检查最后一行是否看起来像完整的句子
        last_line = lines[-1].strip() if lines else ""
        is_complete_sentence = len(last_line) > 10 and any(punct in last_line for punct in ['。', '？', '！', '.', '?', '!'])
        
        return has_ending_word and is_complete_sentence
    
    def _clean_ai_generated_content(self, content: str) -> str:
        """清理AI生成的内容，去除解释性文字和多余的格式"""
        if not content:
            return ""
        
        lines = content.split('\n')
        cleaned_lines = []
        start_found = False
        in_yaml_block = False
        in_code_block = False
        yaml_block_start = -1
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # 检测代码块
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                # 如果是包装YAML的代码块，跳过
                if 'yaml' in stripped.lower() or 'markdown' in stripped.lower():
                    continue
                # 其他代码块保留
                if not in_code_block and start_found:
                    cleaned_lines.append(line)
                continue
            
            # 在代码块内且是YAML包装，特殊处理
            if in_code_block:
                # 检查是否是嵌入的YAML front matter
                if stripped == '---':
                    if not in_yaml_block:
                        in_yaml_block = True
                        yaml_block_start = i
                    else:
                        in_yaml_block = False
                        # 跳过整个YAML块
                    continue
                elif in_yaml_block:
                    continue  # 跳过YAML块内容
                elif start_found:
                    cleaned_lines.append(line)  # 保留非嵌入YAML的代码块内容
                continue
            
            # 跳过明显的AI解释性文字
            if not start_found:
                # 跳过常见的AI解释性开头
                if (stripped.startswith('好的') or 
                    stripped.startswith('遵照') or
                    stripped.startswith('我将') or
                    stripped.startswith('根据') or
                    stripped.startswith('以下是') or
                    stripped.startswith('这里是') or
                    stripped.startswith('这是一篇') or
                    '按照您的规范' in stripped or
                    '用于测试' in stripped):
                    continue
                # 空行跳过
                elif not stripped:
                    continue
                # 找到正式内容开始
                else:
                    start_found = True
            
            # 已找到开始，保留正式内容
            if start_found:
                cleaned_lines.append(line)
        
        cleaned_content = '\n'.join(cleaned_lines)
        
        # 清理多余空行
        cleaned_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_content)
        cleaned_content = cleaned_content.strip()
        
        # 如果清理后内容为空或太短，返回原始内容
        if not cleaned_content or len(cleaned_content) < 100:
            logging.warning("内容清理后为空或过短，返回原始内容")
            return content.strip()
        
        return cleaned_content

    def process_post_images(self, post_path: Path) -> Dict[str, str]:
        """处理文章中的图片"""
        # 获取文章中的本地图片
        local_images = {}
        temp_dir = None
        
        try:
            # 创建临时目录用于存储下载的图片
            temp_dir = Path(tempfile.mkdtemp())
            self.log(f"创建临时目录用于存储下载的图片: {temp_dir}", level="debug")
            
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
                        header = post.get('header', {})
                        if isinstance(header, dict) and img_field in header:
                            img_path = header[img_field]
                            if not img_path:
                                continue
                                
                            # 处理OneDrive链接
                            if '1drv.ms' in img_path or 'onedrive.live.com' in img_path:
                                try:
                                    self.log(f"发现OneDrive头图: {img_field} = {img_path}", level="info")
                                    img_name = self._download_onedrive_image(img_path, temp_dir)
                                    if img_name:
                                        local_images[img_name] = temp_dir / img_name
                                        self.log(f"成功下载OneDrive头图: {img_name}", level="info")
                                except Exception as e:
                                    self.log(f"下载OneDrive头图失败: {str(e)}", level="error")
                            # 处理本地图片
                            elif img_path.startswith('/assets/images/'):
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
                    # 跳过已经是本地路径的图片
                    if img_path.startswith('/assets/images/'):
                        self.log(f"跳过已有的本地图片路径: {img_path}", level="debug")
                        continue
                    
                    # 处理OneDrive链接
                    if '1drv.ms' in img_path or 'onedrive.live.com' in img_path:
                        try:
                            self.log(f"发现OneDrive正文图片: {img_path}", level="info")
                            img_name = self._download_onedrive_image(img_path, temp_dir)
                            if img_name:
                                local_images[img_name] = temp_dir / img_name
                                self.log(f"成功下载OneDrive正文图片: {img_name}", level="info")
                        except Exception as e:
                            self.log(f"下载OneDrive正文图片失败: {str(e)}", level="error")
                    # 处理本地图片
                    elif img_path.startswith('/assets/images/'):
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
            # 图片处理功能已移除（不再使用Cloudflare Images）
            self.log(f"发现 {len(local_images)} 张图片，但图片上传功能已移除", level="info")
            return {}
        
        except Exception as e:
            self.log(f"处理文章图片时出错: {str(e)}", level="error")
            return {}
        
        finally:
            # 清理临时目录
            if temp_dir and temp_dir.exists():
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                    self.log(f"清理临时目录: {temp_dir}", level="debug")
                except Exception as e:
                    self.log(f"清理临时目录失败: {str(e)}", level="warning")
    
    def _download_onedrive_image(self, url: str, temp_dir: Path) -> Optional[str]:
        """下载OneDrive图片
        
        Args:
            url: OneDrive图片URL
            temp_dir: 临时目录
            
        Returns:
            成功返回图片文件名，失败返回None
        """
        try:
            self.log(f"下载OneDrive图片: {url}", level="info")
            
            # 提取OneDrive URL中的唯一标识符
            unique_id = None
            if 'onedrive.live.com' in url and 'resid=' in url:
                # 例如：https://onedrive.live.com/embed?resid=5644DAB129AFDA10%2169891&authkey=%21AFppTKcu8cfS2Eo&width=660
                resid_match = re.search(r'resid=([^&]+)', url)
                if resid_match:
                    resid = resid_match.group(1)
                    # 解码URL编码的字符
                    import urllib.parse
                    resid = urllib.parse.unquote(resid)
                    self.log(f"从URL中提取的resid: {resid}", level="debug")
                    
                    # 提取resid中的数字部分作为唯一标识符
                    id_match = re.search(r'([0-9]+)$', resid)
                    if id_match:
                        unique_id = id_match.group(1)
                        self.log(f"从resid中提取的唯一标识符: {unique_id}", level="debug")
            
            # 如果无法从URL中提取唯一标识符，则使用URL的哈希值
            if not unique_id:
                import hashlib
                unique_id = hashlib.md5(url.encode()).hexdigest()[:5]
                self.log(f"使用URL哈希值作为唯一标识符: {unique_id}", level="debug")
            
            # 下载图片
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # 确定图片格式
            content_type = response.headers.get('content-type', '')
            self.log(f"图片Content-Type: {content_type}", level="debug")
            extension = self._get_extension_from_content_type(content_type)
            
            if not extension and 'content-disposition' in response.headers:
                # 尝试从Content-Disposition头中提取文件名
                cd = response.headers['content-disposition']
                self.log(f"Content-Disposition: {cd}", level="debug")
                filename_match = re.search(r'filename="?([^";]+)"?', cd)
                if filename_match:
                    orig_filename = filename_match.group(1)
                    _, extension = os.path.splitext(orig_filename)
                    extension = extension.lstrip('.')
                    self.log(f"从Content-Disposition提取的扩展名: {extension}", level="debug")
            
            # 如果仍然无法确定扩展名，则根据内容进行判断
            if not extension:
                import filetype
                img_data = response.content
                kind = filetype.guess(img_data)
                extension = kind.extension if kind else 'jpg'  # 默认使用jpg
                self.log(f"从内容判断的图片类型: {extension}", level="debug")
            
            # 构建输出文件名
            output_filename = f"onedrive_{unique_id}.{extension}"
            output_path = temp_dir / output_filename
            
            # 保存图片
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            self.log(f"✅ 图片下载成功: {url} -> {output_filename}", level="info")
            return output_filename
        except Exception as e:
            self.log(f"❌ 下载OneDrive图片失败: {str(e)}", level="error")
            self.log("错误详情:", level="debug")
            return None

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
                # 检查必要的字段（layout不是必须的，发布时会自动添加）
                required_fields = ['title', 'date']
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
        
        # 四大核心分类关键词映射
        category_keywords = {
            "认知升级": ["思维", "认知", "思考", "学习方法", "决策", "心理学", "偏见", "成长", "知识", "思维模型", "阅读", "教育"],
            "技术赋能": ["技术", "工具", "软件", "应用", "自动化", "效率", "编程", "开发", "云服务", "ai", "人工智能", "教程", "指南"],
            "全球视野": ["全球", "国际", "趋势", "文化", "观察", "世界", "跨文化", "分析", "tesla", "马斯克", "科技", "创新", "未来"],
            "投资理财": ["投资", "理财", "金融", "股票", "基金", "量化", "交易", "财务", "资产", "收益", "风险", "策略", "美股", "qdii"]
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
            return ["技术赋能"]
            
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
            请分析以下文章内容，并从博客的四大核心分类体系中选择最合适的分类，同时生成相关标签。

            四大核心分类体系：
            🧠 认知升级：思维模型、学习方法、认知心理学、决策科学相关内容
            🛠️ 技术赋能：实用工具、技术教程、自动化方案、效率提升相关内容  
            🌍 全球视野：国际趋势、文化观察、全球化思维、科技趋势分析相关内容
            💰 投资理财：投资策略、理财方法、财务自由、量化分析相关内容

            要求：
            1. 只能从以上四个分类中选择一个最合适的主分类
            2. 分类名称必须完全匹配：认知升级、技术赋能、全球视野、投资理财
            3. 生成3-5个相关标签
            4. 使用JSON格式返回结果：
            {{
                "categories": ["选择的主分类"],
                "tags": ["标签1", "标签2", "标签3", "标签4", "标签5"]
            }}
            
            文章内容：
            {content[:3000]}
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
    
    def _replace_images(self, content: str, images: Dict[str, str], temp_dir_path: Path) -> str:
        """替换文章中的图片链接为Cloudflare链接"""
        if not images:
            self.log("⚠️ 没有有效的图片需要替换", level="warning")
            return content
            
        # 首先处理OneDrive图片
        # 定义OneDrive链接的匹配模式
        onedrive_patterns = [
            r'!\[([^\]]*)\]\((https?://onedrive\.live\.com/[^)]+)\)',  # Markdown格式
            r'<img\s+src="(https?://onedrive\.live\.com/[^"]+)".*?(?:alt="([^"]*)")?.*?>'  # HTML格式
        ]
        
        # 记录已处理的OneDrive URL，避免重复处理
        processed_urls = {}
        total_replacements = 0
        
        # 处理OneDrive链接
        for pattern in onedrive_patterns:
            matches = re.finditer(pattern, content)
            match_count = 0
            
            for match in matches:
                match_count += 1
                if 'src=' in pattern:  # HTML格式
                    onedrive_url = match.group(1)
                    alt_text = match.group(2) if (match.lastindex is not None and match.lastindex >= 2) else ""
                else:  # Markdown格式
                    alt_text = match.group(1)
                    onedrive_url = match.group(2)
                
                self.log(f"找到OneDrive链接: {onedrive_url}", level="debug")
                
                # 检查是否已经处理过这个URL
                if onedrive_url in processed_urls:
                    local_url = processed_urls[onedrive_url]
                    self.log(f"使用已处理的URL: {onedrive_url} -> {local_url}", level="debug")
                else:
                    # 查找是否有匹配的已上传图片
                    found_match = False
                    for img_name, _ in images.items():
                        if self._is_same_onedrive_image(onedrive_url, img_name):
                            # 使用本地路径替代Cloudflare URL
                            local_url = f"/assets/images/posts/{img_name}"
                            
                            processed_urls[onedrive_url] = local_url
                            found_match = True
                            self.log(f"✅ 找到匹配的本地图片: {img_name} -> {local_url}", level="debug")
                            break
                    
                    # 如果没有找到匹配的模型，使用任何可用的 Gemini 模型
                    if not found_match:
                        self.log(f"⚠️ 未找到匹配的已上传图片，尝试下载: {onedrive_url}", level="debug")
                        img_name = self._download_onedrive_image(onedrive_url, temp_dir_path)
                        if img_name:
                            img_path = temp_dir_path / img_name
                            # cloudflare_id = self.image_mapper.upload_image(img_path)
                            # if cloudflare_id:
                            #     cloudflare_url = f"https://imagedelivery.net/WQEpklwOF67ACUS0Tgsufw/{cloudflare_id}/public"
                            #     processed_urls[onedrive_url] = cloudflare_url
                            #     self.log(f"✅ 下载并上传成功: {onedrive_url} -> {cloudflare_url}", level="debug")
                            # else:
                            #     self.log(f"❌ 上传到Cloudflare失败: {img_name}", level="error")
                            #     continue
                            self.log("❌ 未实现图片上传功能（image_mapper 未定义），请实现上传逻辑", level="error")
                            continue
                        else:
                            self.log(f"❌ 下载OneDrive图片失败: {onedrive_url}", level="error")
                            continue
                
                # 替换内容中的OneDrive链接
                local_url = processed_urls.get(onedrive_url)
                if not local_url:
                    self.log(f"⚠️ 未能获取本地路径，跳过替换: {onedrive_url}", level="warning")
                    continue
                if 'src=' in pattern:  # HTML格式
                    replacement = f'<img src="{local_url}" alt="{alt_text}">'
                else:  # Markdown格式
                    replacement = f'![{alt_text}]({local_url})'
                
                # 使用精确位置替换，避免全局替换可能导致的问题
                start, end = match.span()
                content = content[:start] + replacement + content[end:]
                total_replacements += 1
                self.log(f"替换OneDrive图片链接: {onedrive_url} -> {local_url}", level="debug")
        
        # 处理本地图片路径标准化
        for local_name, _ in images.items():
            # 跳过OneDrive图片，因为它们已经在上面处理过了
            if local_name.startswith('onedrive_'):
                continue
                
            # 使用标准化的本地路径
            local_url = f"/assets/images/posts/{local_name}"
            
            # 匹配各种可能的图片引用格式
            patterns = [
                f'!\\[([^\\]]*)\\]\\(/assets/images/posts/.*?/{re.escape(local_name)}\\)',  # 完整路径
                f'!\\[([^\\]]*)\\]\\(/assets/images/{re.escape(local_name)}\\)',           # 简化路径
                f'!\\[([^\\]]*)\\]\\({re.escape(local_name)}\\)'                           # 仅文件名
            ]
            
            # 检查这个特定图片是否已经有正确的路径，避免重复替换
            local_pattern = f'!\\[([^\\]]*)\\]\\({re.escape(local_url)}\\)'
            if re.search(local_pattern, content):
                self.log(f"⚠️ 图片 {local_name} 已有正确路径，跳过替换", level="debug")
                continue
            
            replaced_this_image = False
            
            # 处理标准路径
            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    alt_text = match.group(1)
                    replacement = f'![{alt_text}]({local_url})'
                    
                    # 使用精确位置替换，避免全局替换可能导致的问题
                    start, end = match.span()
                    content = content[:start] + replacement + content[end:]
                    replaced_this_image = True
            
            if replaced_this_image:
                self.log(f"标准化本地图片路径: {local_name} -> {local_url}", level="debug")
        
        # 记录总替换数量
        if total_replacements > 0:
            self.log(f"✅ 总共替换了 {total_replacements} 个图片引用", level="info")
        else:
            self.log("⚠️ 未找到需要替换的图片引用", level="warning")
            
        return content

    def _is_same_onedrive_image(self, onedrive_url: str, image_name: str) -> bool:
        """判断OneDrive URL是否对应指定的图片名称
        
        通过比较OneDrive URL中的resid参数和图片名称中的唯一标识符来判断
        """
        # 如果图片名称不是以onedrive_开头，则无法确定对应关系
        if not image_name.startswith('onedrive_'):
            self.log(f"图片名称不是以onedrive_开头: {image_name}", level="debug")
            return False
        
        # 从图片名称中提取唯一标识符
        # 格式：onedrive_UNIQUEID.extension
        match = re.match(r'onedrive_([^.]+)\.', image_name)
        if not match:
            self.log(f"无法从图片名称中提取唯一标识符: {image_name}", level="debug")
            return False
        
        image_unique_id = match.group(1)
        self.log(f"比较OneDrive URL和图片: URL={onedrive_url}, 图片名称={image_name}, 唯一ID={image_unique_id}", level="debug")
        
        # 从OneDrive URL中提取resid参数
        if 'onedrive.live.com' in onedrive_url and 'resid=' in onedrive_url:
            resid_match = re.search(r'resid=([^&]+)', onedrive_url)
            if resid_match:
                resid = resid_match.group(1)
                # 解码URL编码的字符
                import urllib.parse
                resid = urllib.parse.unquote(resid)
                
                self.log(f"从OneDrive URL中提取的resid: {resid}", level="debug")
                
                # 检查resid中是否包含图片名称中的唯一标识符
                if image_unique_id in resid:
                    self.log(f"✅ 匹配成功: 唯一ID {image_unique_id} 在resid {resid} 中找到", level="debug")
                    return True
                
                # 提取resid中的数字部分
                id_match = re.search(r'([0-9]+)$', resid)
                if id_match:
                    resid_number = id_match.group(1)
                    self.log(f"从resid中提取的数字部分: {resid_number}", level="debug")
                    if resid_number == image_unique_id:
                        self.log(f"✅ 匹配成功: resid的数字部分 {resid_number} 与唯一ID {image_unique_id} 相同", level="debug")
                        return True
        
        # 如果无法从URL中提取resid，则使用URL的哈希值进行比较
        if len(image_unique_id) == 5:  # 基于URL的哈希值长度为5
            import hashlib
            url_hash = hashlib.md5(onedrive_url.encode()).hexdigest()[:5]
            self.log(f"URL哈希值: {url_hash}, 唯一ID: {image_unique_id}", level="debug")
            if url_hash == image_unique_id:
                self.log(f"✅ 匹配成功: URL哈希值 {url_hash} 与唯一ID {image_unique_id} 相同", level="debug")
                return True
        
        # 如果以上方法都无法确定对应关系，则使用简单的字符串匹配
        result = image_unique_id.lower() in onedrive_url.lower()
        if result:
            self.log(f"✅ 匹配成功: 唯一ID {image_unique_id} 在URL {onedrive_url} 中找到", level="debug")
        else:
            self.log(f"❌ 匹配失败: 唯一ID {image_unique_id} 在URL {onedrive_url} 中未找到", level="debug")
        return result

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
                
                # 检查是否已经是Cloudflare URL
                if img_path.startswith("https://imagedelivery.net"):
                    self.log(f"⚠️ 头图 {img_field} 已是Cloudflare URL，跳过替换", level="debug")
                    continue
                
                # 处理OneDrive链接
                if '1drv.ms' in img_path or 'onedrive.live.com' in img_path:
                    # 查找对应的已上传图片
                    found_match = False
                    for img_name, _ in images.items():
                        # 尝试匹配OneDrive链接和本地图片
                        if self._is_same_onedrive_image(img_path, img_name):
                            # 使用本地路径替代Cloudflare URL
                            local_url = f"/assets/images/posts/{img_name}"
                            
                            post['header'][img_field] = local_url
                            updated_count += 1
                            self.log(f"✅ 更新OneDrive头图: {img_field} = {img_path} -> {local_url}", level="info")
                            found_match = True
                            break
                    
                    if not found_match:
                        self.log(f"⚠️ 未找到匹配的OneDrive头图: {img_field} = {img_path}", level="warning")
                # 处理本地图片
                else:
                    img_name = Path(img_path).name
                    
                    if img_name in images:
                        # 使用本地路径替代Cloudflare URL
                        local_url = f"/assets/images/posts/{img_name}"
                        post['header'][img_field] = local_url
                        updated_count += 1
                        self.log(f"✅ 更新头图: {img_field} = {img_name} -> {local_url}", level="info")
        
        if updated_count > 0:
            self.log(f"总共更新了 {updated_count} 处头部图片", level="info")
        return post

    def _get_extension_from_content_type(self, content_type: str) -> Optional[str]:
        """从Content-Type头中提取文件扩展名
        
        Args:
            content_type: Content-Type头的值
            
        Returns:
            文件扩展名，如果无法确定则返回None
        """
        content_type = content_type.lower()
        if 'image/' not in content_type:
            return None
            
        # 常见的MIME类型映射
        mime_to_ext = {
            'image/jpeg': 'jpg',
            'image/jpg': 'jpg',
            'image/png': 'png',
            'image/gif': 'gif',
            'image/webp': 'webp',
            'image/svg+xml': 'svg',
            'image/bmp': 'bmp',
            'image/tiff': 'tiff'
        }
        
        for mime, ext in mime_to_ext.items():
            if mime in content_type:
                return ext
                
        # 如果没有匹配的MIME类型，尝试从content-type中提取子类型
        if '/' in content_type:
            subtype = content_type.split('/')[-1].split(';')[0].strip()
            if subtype and subtype != 'octet-stream':
                return subtype
                
        return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='config/pipeline_config.yml', help='Path to config file')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()

    pipeline = ContentPipeline(args.config, args.verbose)
    
    # 选择操作
    print("\n请选择操作：")
    print("1. 处理现有草稿")
    print("2. 重新发布已发布文章")
    print("3. 生成测试文章")
    
    choice = input("\n请输入选项 (1/2/3): ").strip()
    
    if choice == "1":
        # 处理现有草稿
        draft = pipeline.select_draft()
        if not draft:
            return
    elif choice == "2":
        # 重新发布已发布文章
        post = pipeline.select_published_post()
        if not post:
            return
        draft = pipeline.copy_post_to_draft(post)
        if not draft:
            return
    elif choice == "3":
        # 生成测试文章
        draft = pipeline.generate_test_content()
        if not draft:
            print("生成测试文章失败")
            return
    else:
        print("无效的选择")
        return
        
    # 选择发布平台
    platforms = pipeline.select_platforms(draft)
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