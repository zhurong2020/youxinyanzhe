import os
import re
import yaml
import logging
import subprocess
import frontmatter
# tempfile在image_processor中使用
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
# google.generativeai导入移动到AI处理器中
from google.generativeai.client import configure
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.types import GenerationConfig
# BlockedPromptException移动到AI处理器中
from google.api_core.exceptions import ResourceExhausted
import argparse
import requests
from dotenv import load_dotenv

# 导入本地模块
from .wechat_publisher import WechatPublisher
from .managers.publish_manager import PublishingStatusManager
from .processors.image_processor import ImageProcessor
from .processors.ai_processor import AIProcessor
from .processors.platform_processor import PlatformProcessor
from ..utils.reward_system_manager import RewardSystemManager


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
            
            # 初始化图片处理器
            self.image_processor = ImageProcessor(self.logger)
            
            # AI处理器将在模型初始化后设置
            self.ai_processor = None
            
            # 初始化存量文档状态
            posts_dir = Path(self.config["paths"]["posts"])
            self.status_manager.initialize_legacy_post_status(posts_dir)
            
            # 初始化内容变现系统管理器（可选）
            self.reward_manager = None
            if self.reward_manager:
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
            
            # 现在可以初始化AI处理器
            self.ai_processor = AIProcessor(self.model, self.logger)
            
            # 初始化平台处理器
            self.platform_processor = PlatformProcessor(self.platforms_config, self.project_root, self.logger)
            
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
    
    def list_drafts(self, filter_valid: bool = True) -> List[Path]:
        """列出所有草稿文件

        Args:
            filter_valid: 是否只返回有效的草稿（默认True，用于发布）
        """
        drafts_dir = Path(self.config["paths"]["drafts"])
        all_drafts = list(drafts_dir.glob("*.md"))

        if not filter_valid:
            # 返回所有草稿（用于格式化等操作）
            return all_drafts

        # 过滤出有效的草稿文件（用于发布）
        valid_drafts = []
        for draft in all_drafts:
            if self._is_valid_draft(draft):
                valid_drafts.append(draft)
            # 不在这里输出日志，在select_draft中统一显示

        return valid_drafts
    
    def analyze_draft_status(self, draft_path: Path) -> str:
        """
        分析草稿状态，只显示严重问题（发布无法自动处理的）

        Args:
            draft_path: 草稿文件路径

        Returns:
            状态信息字符串
        """
        serious_issues = []

        try:
            # 读取草稿内容
            with open(draft_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 只检查严重问题
            # 1. 检查图片路径问题（需要手动处理）
            image_issues = self.check_image_paths(content)
            if image_issues:
                serious_issues.append("🖼️ 图片")

            # 2. 检查Front Matter（必须存在）
            if not content.strip().startswith('---'):
                serious_issues.append("📋 格式")

            # 3. 内容过短（小于200字符才算严重问题）
            clean_content = content.replace('---', '').replace('<!-- more -->', '')
            if len(clean_content.strip()) < 200:
                serious_issues.append("📏 内容过短")

            # 注意：以下问题发布时可自动处理，不显示
            # - 缺少<!-- more -->（格式化时会添加）
            # - 缺少分类/标签（发布时会生成）
            # - excerpt问题（发布时会处理）

        except Exception:
            serious_issues.append("❌ 读取")

        if serious_issues:
            return f" ⚠️ [{', '.join(serious_issues)}]"
        else:
            return " ✅"
    
    def check_image_paths(self, content: str) -> List[str]:
        """
        检查内容中的图片路径问题
        
        Args:
            content: 文章内容
            
        Returns:
            问题图片路径列表
        """
        return self.image_processor.check_image_paths(content)
    
    def check_draft_issues(self, draft_path: Path) -> List[str]:
        """
        检查草稿的具体问题
        
        Args:
            draft_path: 草稿文件路径
            
        Returns:
            问题描述列表
        """
        issues = []
        
        try:
            with open(draft_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 1. 检查图片路径问题
            image_issues = self.check_image_paths(content)
            if image_issues:
                issues.append(f"🖼️ 图片路径不规范 ({len(image_issues)}个图片需要OneDrive处理)")
                for img in image_issues[:2]:  # 最多显示2个示例
                    issues.append(f"      例如: {img}")
                if len(image_issues) > 2:
                    issues.append(f"      ... 还有{len(image_issues)-2}个图片")
            
            # 2. 检查Front Matter
            if not content.strip().startswith('---'):
                issues.append("📋 缺少Jekyll Front Matter (需要标题、分类、标签等)")
            else:
                # 解析Front Matter检查必需字段
                try:
                    import frontmatter
                    post = frontmatter.loads(content)
                    required_fields = ['title', 'date', 'header']
                    missing_fields = [field for field in required_fields if field not in post.metadata]
                    if missing_fields:
                        issues.append(f"📋 Front Matter缺少必需字段: {', '.join(missing_fields)}")
                    
                    # 检查特定字段格式
                    if 'title' in post.metadata:
                        title_len = len(str(post.metadata['title']))
                        if title_len < 10:
                            issues.append("📝 标题过短，建议25-35字符")
                        elif title_len > 60:
                            issues.append("📝 标题过长，建议25-35字符")
                    
                    if 'header' in post.metadata and isinstance(post.metadata['header'], dict):
                        if 'teaser' in post.metadata['header']:
                            teaser_path = str(post.metadata['header']['teaser'])
                            if teaser_path.startswith('c:') or teaser_path.startswith('C:'):
                                issues.append("🖼️ 头图使用了本地路径，需要OneDrive处理")
                    
                    # 检查VIP文章的特殊要求
                    member_tier = post.metadata.get('member_tier')
                    if member_tier and member_tier != 'free':
                        # 检查VIP文章必须有member-post布局
                        if post.metadata.get('layout') != 'member-post':
                            issues.append("🔐 VIP文章缺少 'layout: member-post' 设置，访问控制将失效")
                        
                        # 检查VIP等级合法性
                        valid_tiers = ['experience', 'monthly', 'quarterly', 'yearly']
                        if member_tier not in valid_tiers:
                            issues.append(f"🔐 无效的会员等级: {member_tier}，有效值: {', '.join(valid_tiers)}")
                        
                        # 检查VIP文章标题是否包含等级标识
                        title = str(post.metadata.get('title', ''))
                        vip_indicators = ['VIP2', 'VIP3', 'VIP4', '专享', '会员']
                        if not any(indicator in title for indicator in vip_indicators):
                            issues.append("🔐 VIP文章标题建议包含等级标识 (如 VIP2专享、VIP3专享)")
                
                except Exception as e:
                    # 只报告一次Front Matter错误，避免重复
                    if "while parsing" not in str(e):
                        issues.append(f"📋 Front Matter格式错误: {str(e)}")
            
            # 3. 检查内容结构
            if '<!-- more -->' not in content:
                issues.append("✂️ 缺少首页分页标记 <!-- more -->，格式化工具会自动添加")
            
            if 'excerpt:' not in content and content.strip().startswith('---'):
                issues.append("📄 缺少摘要字段 (excerpt) 影响SEO")
            
            # 检查摘要长度规范（新增）
            summary_issues = self._check_summary_lengths(content)
            issues.extend(summary_issues)
            
            # 4. 检查内容质量
            clean_content = content.replace('---', '').replace('<!-- more -->', '')
            content_lines = [line.strip() for line in clean_content.split('\n') if line.strip()]
            
            if len(clean_content.strip()) < 500:
                issues.append("📏 内容过短 (建议至少500字符)")
            
            # 检查是否有明显的结尾
            if len(content_lines) > 0:
                # 过滤掉Jekyll格式的结尾行，只检查实际文章内容
                content_ending_lines = []
                for line in reversed(content_lines):
                    # 跳过Jekyll模板、打赏链接、评论提示等格式化内容
                    if any(pattern in line for pattern in [
                        '{% ', '%}', '{{', '}}',  # Jekyll液体模板
                        'GitHub 账号', '发表评论', '请我喝咖啡',  # 标准页脚
                        '<a href', '<img src', '](http',  # HTML和链接
                        '💬', '☕', '💰', '🎯'  # 页脚常用emoji
                    ]):
                        continue
                    # 找到实际内容行
                    content_ending_lines.append(line)
                    if len(content_ending_lines) >= 3:  # 检查最后3行实际内容
                        break
                
                # 检查最后的实际内容是否有合适的结尾
                if content_ending_lines:
                    last_content_line = content_ending_lines[0]
                    # 降低结尾要求，考虑到有些文章以清单、引用等结尾
                    if (len(last_content_line) < 15 and 
                        not any(punct in last_content_line for punct in ['。', '？', '！', '.', '?', '!']) and
                        not any(ending in last_content_line for ending in ['思考', '总结', '展望', '参考', '资料', '清单'])):
                        issues.append("📝 文章可能没有合适的结尾段落")
            
            # 5. 检查分类标签
            if content.strip().startswith('---'):
                try:
                    import frontmatter
                    post = frontmatter.loads(content)
                    if 'categories' not in post.metadata and 'category' not in post.metadata:
                        issues.append("🏷️ 缺少分类信息，建议使用四大分类之一")
                    
                    if 'tags' not in post.metadata or not post.metadata.get('tags'):
                        issues.append("🏷️ 缺少标签信息，有助于内容发现")
                except:
                    pass  # Front Matter已检查过
                    
        except Exception as e:
            issues.append(f"❌ 文件读取错误: {str(e)}")
        
        return issues
    
    def _clean_content_for_length_check(self, content: str) -> str:
        """清理内容用于长度检查，移除Markdown语法标记"""
        import re
        clean = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', content)  # 图片
        clean = re.sub(r'\[[^\]]*\]\([^)]*\)', '', clean)     # 链接
        clean = re.sub(r'`[^`]*`', '', clean)                 # 内联代码
        clean = re.sub(r'```[^`]*```', '', clean, flags=re.DOTALL)  # 代码块
        clean = re.sub(r'^#+\s*', '', clean, flags=re.MULTILINE)    # 标题
        clean = re.sub(r'^\s*[-*+]\s*', '', clean, flags=re.MULTILINE)  # 列表
        clean = re.sub(r'^\s*>\s*', '', clean, flags=re.MULTILINE)      # 引用
        clean = re.sub(r'\*\*([^*]*)\*\*', r'\1', clean)     # 粗体
        clean = re.sub(r'\*([^*]*)\*', r'\1', clean)         # 斜体
        clean = re.sub(r'~~([^~]*)~~', r'\1', clean)         # 删除线
        return clean
    
    def _extract_body_before_more(self, content: str) -> str:
        """提取Front Matter后到<!-- more -->之间的内容"""
        if content.strip().startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                body_content = parts[2].strip()
                more_pos = body_content.find('<!-- more -->')
                if more_pos != -1:
                    return body_content[:more_pos].strip()
        return ""
    
    def _check_summary_lengths(self, content: str) -> List[str]:
        """检查excerpt字段和<!-- more -->前内容的长度规范"""
        issues = []

        try:
            # 1. 检查excerpt字段长度
            if content.strip().startswith('---'):
                import frontmatter
                post = frontmatter.loads(content)
                excerpt = post.metadata.get('excerpt', '')

                if not excerpt:
                    issues.append("📝 缺少excerpt字段，将使用Gemini自动生成")
                else:
                    excerpt_len = len(excerpt.strip())
                    if excerpt_len < 40:
                        issues.append(f"📏 excerpt过短({excerpt_len}字符)，建议50字符左右")
                    elif excerpt_len > 70:
                        issues.append(f"📏 excerpt过长({excerpt_len}字符)，建议50字符左右")

            # 2. 检查<!-- more -->前内容长度
            # 注意：如果文件刚被格式化过，不再重复检查<!-- more -->前内容
            # 格式化工具已经处理了<!-- more -->的插入位置
            more_pos = content.find('<!-- more -->')
            if more_pos != -1:
                before_more = self._extract_body_before_more(content)
                if before_more:
                    # 清理内容，移除引用块、标题等
                    clean_content = self._clean_content_for_length_check(before_more)
                    # 过滤掉只包含引用或信息状态的内容
                    actual_content_lines = []
                    for line in clean_content.split('\n'):
                        line = line.strip()
                        if line and not line.startswith(('>', '*', '-', '#')):
                            actual_content_lines.append(line)

                    actual_content = ' '.join(actual_content_lines)
                    clean_length = len(actual_content.strip())

                    # 只有当实际内容确实过短或过长时才报告
                    # 考虑到引用块等特殊情况，放宽限制
                    if actual_content and clean_length < 30:
                        issues.append(f"📏 <!-- more -->前内容过短({clean_length}字符)，建议添加简短介绍")
                    elif clean_length > 150:
                        issues.append(f"📏 <!-- more -->前内容过长({clean_length}字符)，建议精简首页预览")

        except Exception as e:
            # 静默处理，避免重复报错
            pass

        return issues
    
    def _auto_generate_excerpt_if_missing(self, draft_path: Path, content: str) -> bool:
        """如果缺少excerpt字段，自动生成并更新文件"""
        try:
            if not content.strip().startswith('---'):
                return False
                
            import frontmatter
            post = frontmatter.loads(content)
            
            if 'excerpt' not in post.metadata or not post.metadata['excerpt']:
                self.log("检测到缺少excerpt，正在使用Gemini生成...", level="info", force=True)
                print("🤖 检测到缺少excerpt，正在使用Gemini生成...")
                
                # 调用AI生成excerpt
                if self.ai_processor:
                    generated_excerpt = self.ai_processor.generate_excerpt(content)
                    if generated_excerpt and generated_excerpt != "这是一篇有价值的文章，值得阅读。":
                        # 更新front matter
                        post.metadata['excerpt'] = generated_excerpt
                        
                        # 重新构建文件内容
                        updated_content = frontmatter.dumps(post)
                        
                        # 写回文件
                        with open(draft_path, 'w', encoding='utf-8') as f:
                            f.write(updated_content)
                        
                        print(f"✅ 已自动生成excerpt: {generated_excerpt}")
                        self.log(f"✅ 自动生成excerpt成功: {generated_excerpt}", level="info", force=True)
                        return True
                    else:
                        print("❌ Gemini excerpt生成失败，请手动添加")
                        self.log("❌ Gemini excerpt生成失败", level="warning")
                        return False
                else:
                    print("❌ AI处理器不可用，无法生成excerpt")
                    self.log("❌ AI处理器不可用，无法生成excerpt", level="warning")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ excerpt生成异常: {str(e)}")
            self.log(f"❌ excerpt生成异常: {str(e)}", level="error")
            return False
    
    def _get_summary_fix_suggestions(self, issues: List[str]) -> List[str]:
        """根据摘要问题提供修复建议"""
        suggestions = []
        
        for issue in issues:
            if "excerpt过短" in issue:
                suggestions.append("💡 建议: 丰富excerpt描述，或使用Gemini重新生成")
            elif "excerpt过长" in issue:
                suggestions.append("💡 建议: 精简excerpt内容，保留核心要点")
            elif "<!-- more -->前内容过短" in issue:
                suggestions.append("💡 建议: 在<!-- more -->前添加背景说明或引言")
            elif "<!-- more -->前内容过长" in issue:
                suggestions.append("💡 建议: 将部分内容移至<!-- more -->后，保留精华开头")
            elif "缺少excerpt" in issue:
                suggestions.append("💡 系统将自动调用Gemini生成excerpt")
        
        return suggestions
    
    def comprehensive_content_check(self, file_path: Path, auto_fix: bool = False) -> Dict[str, Any]:
        """
        统一的内容质量检查和修复接口
        
        Args:
            file_path: 要检查的文件路径
            auto_fix: 是否自动修复可修复的问题
            
        Returns:
            检查结果字典，包含问题列表、修复状态等
        """
        results = {
            'file_path': str(file_path),
            'issues': [],
            'auto_fixes_applied': [],
            'manual_fixes_needed': [],
            'check_passed': False,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # 1. 执行完整的草稿问题检查
            issues = self.check_draft_issues(file_path)
            results['issues'] = issues
            
            if not issues:
                results['check_passed'] = True
                self.log(f"✅ 内容质量检查通过: {file_path.name}", level="info")
                return results
            
            # 2. 尝试自动修复
            if auto_fix:
                # 读取文件内容
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 自动修复excerpt缺失
                excerpt_issues = [issue for issue in issues if "缺少excerpt字段" in issue]
                if excerpt_issues:
                    if self._auto_generate_excerpt_if_missing(file_path, content):
                        results['auto_fixes_applied'].append("自动生成excerpt字段")
                        # 重新读取更新后的内容
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                
                # 重新检查，更新问题列表
                updated_issues = self.check_draft_issues(file_path)
                results['issues'] = updated_issues
                
                if not updated_issues:
                    results['check_passed'] = True
            
            # 3. 分类剩余问题
            for issue in results['issues']:
                if any(keyword in issue for keyword in ["excerpt", "more", "摘要"]):
                    # 摘要相关问题需要手动处理
                    results['manual_fixes_needed'].append({
                        'issue': issue,
                        'category': 'summary',
                        'suggestions': self._get_summary_fix_suggestions([issue])
                    })
                elif "图片" in issue:
                    # 图片相关问题
                    results['manual_fixes_needed'].append({
                        'issue': issue,
                        'category': 'images',
                        'suggestions': ["使用OneDrive图床管理处理图片路径"]
                    })
                elif any(keyword in issue for keyword in ["格式", "分页"]):
                    # 格式相关问题（长度问题单独处理）
                    results['manual_fixes_needed'].append({
                        'issue': issue,
                        'category': 'format',
                        'suggestions': ["使用内容规范化处理修复格式问题"]
                    })
                elif "长度" in issue and "<!-- more -->" in issue:
                    # <!-- more -->前内容长度问题，通常已由格式化工具处理
                    # 降低优先级，作为提示而非错误
                    results['manual_fixes_needed'].append({
                        'issue': issue,
                        'category': 'info',
                        'suggestions': ["格式化工具已优化<!-- more -->位置，此提示仅供参考"]
                    })
                else:
                    # 其他问题
                    results['manual_fixes_needed'].append({
                        'issue': issue,
                        'category': 'other',
                        'suggestions': ["需要手动检查和修复"]
                    })
            
            # 4. 记录处理结果
            if results['auto_fixes_applied']:
                self.log(f"🔧 自动修复完成: {', '.join(results['auto_fixes_applied'])}", level="info")
            
            if results['manual_fixes_needed']:
                self.log(f"⚠️ 需要手动处理 {len(results['manual_fixes_needed'])} 个问题", level="warning")
            else:
                results['check_passed'] = True
                
        except Exception as e:
            self.log(f"❌ 内容质量检查异常: {str(e)}", level="error")
            results['issues'].append(f"检查过程异常: {str(e)}")
        
        return results
    
    def get_preprocessing_suggestions(self, issues: List[str]) -> List[str]:
        """
        根据问题提供预处理建议
        
        Args:
            issues: 问题列表
            
        Returns:
            建议列表
        """
        suggestions = []
        
        # 分析问题类型并给出相应建议
        has_image_issues = any('图片' in issue for issue in issues)
        has_format_issues = any(any(keyword in issue for keyword in ['Front Matter', '分页', '摘要', '内容过短']) for issue in issues)
        
        if has_image_issues:
            suggestions.append("🖼️  14. OneDrive图床管理 - 处理图片上传和路径规范化")
        
        if has_format_issues:
            suggestions.append("📝 4. 内容规范化处理 - 完善Front Matter和内容结构")
        
        if not suggestions:
            suggestions.append("📋 建议先检查文件内容和格式是否符合Jekyll规范")
        
        suggestions.append("💡 或者继续发布，系统会尝试自动处理部分问题")
        
        return suggestions
    
    def select_draft(self) -> Optional[Path] | str:
        """让用户选择要处理的草稿"""
        # 获取所有草稿，包括无效的
        all_drafts = self.list_drafts(filter_valid=False)
        valid_drafts = self.list_drafts(filter_valid=True)

        # 分离有效和无效草稿
        invalid_drafts = [d for d in all_drafts if d not in valid_drafts]

        if not valid_drafts and not invalid_drafts:
            print("📝 没有找到规范化草稿文件")
            print("\n🔍 快速创作建议：")
            print("   🎯 5. 主题灵感生成器 - AI生成文章主题和大纲")
            print("   🎬 8. YouTube播客生成器 - 将YouTube视频转换为文章")
            print("   📝 4. 内容规范化处理 - 处理手工草稿或其他内容")
            print("   📄 3. 生成测试文章 - 快速生成示例内容")
            
            print("\n🛠️ 其他选项：")
            print("   📁 手工创建：在 _drafts/ 目录创建 .md 文件")
            print("   📰 2. 重新发布已发布文章 - 将已发布文章转为草稿")
            
            print("\n💡 推荐工作流程：")
            print("   创作内容 → 4.内容规范化处理 → 1.发布规范化草稿")
            
            while True:
                choice = input("\n选择快速操作 (5=灵感生成/8=YouTube/4=规范化/3=测试/N=返回): ").strip().lower()
                if choice == '5':
                    print("🎯 正在跳转到主题灵感生成器...")
                    return 'redirect_to_inspiration'  # 特殊返回值
                elif choice == '8':
                    print("🎬 正在跳转到YouTube播客生成器...")
                    return 'redirect_to_youtube'  # 特殊返回值
                elif choice == '4':
                    print("📝 正在跳转到内容规范化处理...")
                    return 'redirect_to_normalization'  # 特殊返回值
                elif choice == '3':
                    return self.generate_test_content()
                elif choice in ['n', 'no', '']:
                    return None
                else:
                    print("请输入 5、8、4、3 或 N")
            
        # 显示草稿列表
        if invalid_drafts:
            invalid_names = [d.name for d in invalid_drafts]
            if len(invalid_names) == 1:
                print(f"\nWARNING - ⚠️ 草稿缺少Front Matter，需要先格式化: {invalid_names[0]}")
            else:
                print(f"\nWARNING - ⚠️ 以下草稿缺少Front Matter，需要先格式化:")
                for name in invalid_names:
                    print(f"  - {name}")
            print("")

        print("可用的草稿文件：")
        if valid_drafts:
            for i, draft in enumerate(valid_drafts, 1):
                # 检查草稿状态和问题
                status_info = self.analyze_draft_status(draft)
                print(f"{i}. {draft.name}{status_info}")
        else:
            print("（没有有效的草稿文件）")
        print("0. 退出")
            
        while True:
            try:
                choice = int(input("\n请选择要处理的草稿 (输入序号，0退出): "))
                if choice == 0:
                    return None
                if 1 <= choice <= len(valid_drafts):
                    selected_draft = valid_drafts[choice-1]
                    
                    # 检查选择的草稿是否有严重问题
                    issues = self.check_draft_issues(selected_draft)

                    # 过滤出严重问题（发布无法自动解决的）
                    serious_issues = []
                    for issue in issues:
                        # 以下问题发布时可以自动处理，不需要提示
                        auto_fixable = [
                            '缺少分类信息',
                            '缺少标签信息',
                            'excerpt过短',
                            'excerpt过长',
                            '缺少excerpt字段'
                        ]
                        if not any(fixable in issue for fixable in auto_fixable):
                            serious_issues.append(issue)

                    if serious_issues:
                        print(f"\n⚠️  草稿 '{selected_draft.name}' 检测到需要手动处理的问题：")
                        for issue in serious_issues:
                            print(f"   • {issue}")

                        print("\n🔧 建议的预处理步骤：")
                        print("   📝 4. 内容规范化处理 - 修复结构问题")

                        proceed = input("\n是否继续发布？系统将尝试自动处理其他问题 (y/N): ").strip().lower()
                        if proceed not in ['y', 'yes']:
                            print("💡 您可以先处理这些问题，然后再回来发布")
                            continue
                    
                    return selected_draft
                print("无效的选择")
            except ValueError:
                print("请输入有效的数字")
    
    def list_published_posts(self, days_limit: int = 30) -> List[Path]:
        """列出已发布的文章

        Args:
            days_limit: 只显示最近N天内的文章，默认30天
        """
        posts_dir = Path(self.config["paths"]["posts"])
        if not posts_dir.exists():
            return []

        import time
        from datetime import datetime, timedelta

        # 计算时间限制
        cutoff_time = time.time() - (days_limit * 24 * 60 * 60)

        posts = []
        older_posts_count = 0

        for file in posts_dir.glob("*.md"):
            if file.is_file():
                # 检查文件修改时间
                if file.stat().st_mtime >= cutoff_time:
                    posts.append(file)
                else:
                    older_posts_count += 1

        # 如果有更早的文章，提示用户
        if older_posts_count > 0:
            print(f"\n💡 提示：还有 {older_posts_count} 篇超过 {days_limit} 天的文章未显示")
            print(f"   如需发布更早的文章，请手工编辑 _drafts/.publishing/ 目录下对应的yml文件")
            print(f"   将 'published_platforms: - github_pages' 添加到文件中\n")

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
    
    def select_member_tier(self) -> Optional[str]:
        """让用户选择文章的会员分级"""
        print("\n👥 会员分级选项：")
        print("  1. 免费内容 - 所有用户可访问")
        print("  2. 体验会员 (VIP1) - ¥35/7天")
        print("  3. 月度会员 (VIP2) - ¥108/30天")
        print("  4. 季度会员 (VIP3) - ¥288/90天")
        print("  5. 年度会员 (VIP4) - ¥720/365天")
        print("  0. 跳过设置")
        
        tier_mapping = {
            '1': 'free',
            '2': 'experience', 
            '3': 'monthly',
            '4': 'quarterly',
            '5': 'yearly'
        }
        
        try:
            choice = input("\n请选择会员分级 (1-5，默认为1): ").strip()
            
            if choice == '0':
                print("⏭️  跳过会员分级设置")
                return None
            elif choice in tier_mapping:
                tier = tier_mapping[choice]
                tier_names = {
                    'free': '免费内容',
                    'experience': '体验会员',
                    'monthly': '月度会员', 
                    'quarterly': '季度会员',
                    'yearly': '年度会员'
                }
                print(f"✅ 已设置为 {tier_names[tier]}")
                return tier
            else:
                print("✅ 默认设置为免费内容")
                return 'free'
        except (EOFError, KeyboardInterrupt):
            print("\n✅ 默认设置为免费内容")
            return 'free'

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
    
    def process_draft(self, draft_path: Path, platforms: List[str], enable_monetization: bool = False, member_tier: Optional[str] = None) -> dict:
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
                            'error': f'front matter解析失败: {str(e)}',
                        }
                
                # 添加会员分级信息
                if member_tier:
                    post['member_tier'] = member_tier
                    # 如果不是免费内容，使用会员文章布局
                    if member_tier != 'free':
                        post['layout'] = 'member-post'
                    tier_names = {
                        'free': '免费内容',
                        'experience': '体验会员',
                        'monthly': '月度会员', 
                        'quarterly': '季度会员',
                        'yearly': '年度会员'
                    }
                    self.log(f"设置会员分级: {tier_names.get(member_tier, member_tier)}", level="info")
                
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
                
                # 7. 归档草稿处理
                archived_file_path = None
                published_platforms = self.status_manager.get_published_platforms(draft_path.stem)
                
                if all_success:
                    # 如果本次发布的所有平台都成功，询问是否归档
                    self.log(f"📋 本次发布成功的平台: {', '.join(successful_platforms)}", level="info", force=True)
                    
                    # 检查这是否是首次发布（即之前没有发布过任何平台）
                    previous_platforms = set(published_platforms) - set(successful_platforms)
                    is_first_time = len(previous_platforms) == 0
                    
                    if is_first_time:
                        # 首次发布，自动归档（避免交互式输入卡死）
                        self.log("✅ 首次发布成功！自动归档草稿到 archived/ 目录", level="info", force=True)
                        task = progress.add_task("📦 归档草稿...", total=None)
                        archived_file_path = self._archive_draft(draft_path)
                        progress.update(task, completed=True)
                        self.log("✅ 草稿已自动归档", level="info", force=True)
                    else:
                        # 非首次发布，检查是否已在所有启用平台发布
                        all_enabled_platforms = [name for name, config in self.config["platforms"].items() 
                                               if config.get("enabled", False)]
                        if set(published_platforms) >= set(all_enabled_platforms):
                            # 已在所有启用平台发布，自动归档
                            task = progress.add_task("📦 归档草稿...", total=None)
                            archived_file_path = self._archive_draft(draft_path)
                            progress.update(task, completed=True)
                            self.log("✅ 已在所有启用平台发布，草稿已自动归档", level="info", force=True)
                        else:
                            unpublished_platforms = set(all_enabled_platforms) - set(published_platforms)
                            self.log(f"💾 已发布到: {', '.join(published_platforms)}", level="info", force=True)
                            self.log(f"📋 未发布平台: {', '.join(unpublished_platforms)} (可稍后发布)", level="info", force=True)
                else:
                    self.log("⚠️ 部分发布失败，跳过归档步骤", level="warning", force=True)
                
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
                'error': str(e),
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
        return self.ai_processor.polish_content(content)
    
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
        return self.ai_processor.generate_excerpt(content)

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
            append_footer = platform_config.get('append_footer', False)
            self.log(f"平台 {platform} append_footer 配置: {append_footer}", level="info", force=True)
            
            if append_footer:
                # 获取页脚模板 - 兼容不同的配置结构
                footer_templates = self.templates.get('footer', {})
                if not footer_templates and 'footer' in self.config:
                    # 直接从config中获取footer配置
                    footer_templates = self.config.get('footer', {})
                
                self.log(f"可用的页脚模板: {list(footer_templates.keys())}", level="info", force=True)
                
                footer_template = footer_templates.get(platform, '')
                self.log(f"获取到的页脚模板长度: {len(footer_template) if footer_template else 0}", level="info", force=True)
                
                if footer_template:
                    # 确保页脚前有足够的空行
                    if not content_text.endswith('\n\n'):
                        content_text = content_text.rstrip() + '\n\n'
                    
                    content_text = f"{content_text}{footer_template}"
                    self.log(f"✅ 添加页脚成功，页脚长度: {len(footer_template)} 字符", level="info", force=True)
                else:
                    self.log(f"❌ 未找到平台 {platform} 的页脚模板", level="warning", force=True)
            else:
                self.log(f"平台 {platform} 未启用页脚添加", level="info")
            
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
            
            # 页脚已在 _generate_platform_content 中处理，此处不重复添加
            self.log("页脚处理已在内容生成阶段完成", level="info")
            
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
            
            # 在保存前替换音频链接为YouTube嵌入
            try:
                from ..utils.audio_link_replacer import AudioLinkReplacer
                replacer = AudioLinkReplacer()
                content, replaced_count = replacer.replace_audio_links(content, draft_path.stem)
                if replaced_count > 0:
                    self.log(f"🎬 已替换 {replaced_count} 个音频链接为YouTube嵌入", level="info", force=True)
            except Exception as e:
                self.log(f"⚠️ 音频链接替换失败: {e}", level="warning")
            
            # 保存文件
            with open(publish_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.log(f"✅ 内容已发布到: {publish_path}", force=True)
            
            # Git 操作
            try:
                # 检查当前分支是否有上游跟踪分支
                try:
                    result = subprocess.run(
                        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    has_upstream = result.returncode == 0 and result.stdout.strip()
                except:
                    has_upstream = False
                
                # 如果有上游分支，先拉取最新代码
                if has_upstream:
                    try:
                        subprocess.run(["git", "pull"], check=True)
                    except subprocess.CalledProcessError:
                        self.log("拉取代码失败，继续发布流程", level="warning")
                else:
                    self.log("当前分支无上游跟踪分支，跳过拉取", level="info")
                
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
                
                # 推送（如果无上游分支，自动设置）
                if has_upstream:
                    subprocess.run(["git", "push"], check=True)
                else:
                    # 获取当前分支名
                    current_branch = subprocess.run(
                        ["git", "branch", "--show-current"],
                        capture_output=True,
                        text=True,
                        check=True
                    ).stdout.strip()
                    
                    # 设置上游分支并推送
                    subprocess.run(["git", "push", "--set-upstream", "origin", current_branch], check=True)
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
        print("\n📱 === 微信公众号发布 ===")

        if not self.wechat_publisher:
            self.log("微信发布器未初始化，跳过发布。", level="error", force=True)
            print("❌ 微信发布器未初始化")
            return False

        try:
            post = frontmatter.loads(content)
            platform_config = self.platforms_config.get("wechat", {})
            publish_mode = platform_config.get("publish_mode", "guide")  # 默认为 guide 模式

            self.log(f"微信发布模式: {publish_mode.upper()}", level="info", force=True)
            print(f"🔄 发布模式: {publish_mode.upper()}")

            if publish_mode == "api":
                # API模式：直接发布到草稿箱
                print("🌐 使用API模式直接发布到微信草稿箱...")
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
                print("📝 使用指南模式生成手动发布指南...")
                success = self.wechat_publisher.generate_guide_file(
                    project_root=self.project_root,
                    front_matter=post.metadata,
                    markdown_content=post.content
                )
                if success:
                    # Find the latest guide file
                    import time
                    guide_dir = self.project_root / ".tmp/output/wechat_guides"
                    if guide_dir.exists():
                        latest_files = sorted(guide_dir.glob("*_guide.md"), key=lambda p: p.stat().st_mtime, reverse=True)
                        if latest_files:
                            self.log(f"✅ 成功生成微信发布指南文件: {latest_files[0]}", force=True)
                        else:
                            self.log("✅ 成功生成微信发布指南文件。", force=True)
                    else:
                        self.log("✅ 成功生成微信发布指南文件。", force=True)
                else:
                    self.log("❌ 生成微信发布指南文件失败。", level="error", force=True)
                return success

        except Exception as e:
            self.log(f"发布到微信时发生未知错误: {e}", level="error", force=True)
            print(f"❌ 发布到微信时出错: {e}")
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
            response = None
            # 配置安全设置以允许技术内容生成
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
            ]
            
            for attempt in range(max_retries):
                if attempt > 0:
                    print(f"⚠️ 第{attempt + 1}次尝试生成...")
                    logging.info(f"重试生成测试文章，第{attempt + 1}次尝试")
                
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
        return self.image_processor.process_post_images(post_path)
    
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
        """检查文件是否是有效的草稿文件（用于发布）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查是否有 front matter
            if not content.startswith('---'):
                # 没有Front Matter的文件不能直接发布
                # 不在这里记录日志，避免重复提示
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
        # 获取可用分类
        available_cats = self._get_available_categories()
        if not available_cats:
            self.log("❌ 无法获取可用分类", level="error")
            return [], []
        
        return self.ai_processor.generate_categories_and_tags(content, available_cats)
    
    def _replace_images(self, content: str, images: Dict[str, str], temp_dir_path: Path) -> str:
        """替换文章中的图片链接"""
        return self.image_processor.replace_images_in_content(content, images, temp_dir_path)

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

    # ===================== 统一处理接口 =====================
    
    def format_content_file(self, input_file: Path, **kwargs) -> Dict[str, Any]:
        """
        统一的内容文件格式化接口
        
        Args:
            input_file: 输入文件路径
            **kwargs: 传递给format_draft.py的参数
            
        Returns:
            处理结果字典
        """
        from pathlib import Path
        import subprocess
        import sys
        
        result = {
            'success': False,
            'output_file': None,
            'issues': [],
            'error': None
        }
        
        try:
            if not input_file.exists():
                result['error'] = f"输入文件不存在: {input_file}"
                return result
            
            # 构建format_draft.py调用参数
            script_path = Path("scripts/tools/content/format_draft.py")
            if not script_path.exists():
                result['error'] = f"格式化脚本不存在: {script_path}"
                return result
            
            cmd = [sys.executable, str(script_path), str(input_file)]
            
            # 添加可选参数
            if 'title' in kwargs:
                cmd.extend(['-t', kwargs['title']])
            if 'category' in kwargs:
                cmd.extend(['-c', kwargs['category']])
            if 'tags' in kwargs:
                cmd.extend(['--tags'] + kwargs['tags'])
            if 'output' in kwargs:
                cmd.extend(['-o', str(kwargs['output'])])
            
            # 执行格式化
            process_result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                cwd=Path.cwd()
            )
            
            if process_result.returncode == 0:
                result['success'] = True
                
                # 解析输出找到生成的文件路径
                output_lines = process_result.stdout.split('\n')
                for line in output_lines:
                    # 兼容emoji前缀的格式化完成标记
                    if '格式化完成:' in line:
                        # 分割并清理路径字符串，去除可能的emoji等前缀
                        output_file_str = line.split('格式化完成:')[-1].strip()
                        result['output_file'] = Path(output_file_str)
                        break
                
                # 如果格式化成功，进行质量检查
                if result['output_file'] and result['output_file'].exists():
                    check_result = self.comprehensive_content_check(
                        result['output_file'], 
                        auto_fix=True
                    )
                    result.update(check_result)
                    
                    self.log(f"统一格式化完成: {input_file} → {result['output_file']}", level="info")
                else:
                    result['error'] = "无法确定输出文件路径"
                    result['success'] = False
            else:
                result['error'] = process_result.stderr or "格式化失败"
                
        except Exception as e:
            result['error'] = f"格式化过程异常: {str(e)}"
            self.log(f"格式化文件失败: {input_file}, 错误: {str(e)}", level="error")
            
        return result
    
    def process_onedrive_images(self, draft_file: Path, mode: str = "single") -> Dict[str, Any]:
        """
        统一的OneDrive图片处理接口
        
        Args:
            draft_file: 草稿文件路径
            mode: 处理模式 ("single" 或 "batch")
            
        Returns:
            处理结果字典
        """
        import subprocess
        import sys
        
        result = {
            'success': False,
            'processed_images': 0,
            'issues': [],
            'error': None
        }
        
        try:
            if not draft_file.exists():
                result['error'] = f"草稿文件不存在: {draft_file}"
                return result
            
            # 检查草稿中的图片问题
            with open(draft_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            image_issues = self.check_image_paths(content)
            if not image_issues:
                result['success'] = True
                result['processed_images'] = 0
                self.log(f"草稿无需图片处理: {draft_file}", level="info")
                return result
            
            # 调用OneDrive图片处理脚本
            script_path = Path("scripts/tools/onedrive_blog_images.py")
            if not script_path.exists():
                result['error'] = f"OneDrive处理脚本不存在: {script_path}"
                return result
            
            cmd = [sys.executable, str(script_path), "--draft", str(draft_file)]
            
            process_result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            
            if process_result.returncode == 0:
                result['success'] = True
                result['processed_images'] = len(image_issues)
                
                # 重新检查处理后的图片状态
                with open(draft_file, 'r', encoding='utf-8') as f:
                    updated_content = f.read()
                remaining_issues = self.check_image_paths(updated_content)
                result['issues'] = remaining_issues
                
                self.log(f"OneDrive图片处理完成: {draft_file}, 处理 {result['processed_images']} 张图片", level="info")
            else:
                result['error'] = process_result.stderr or "OneDrive图片处理失败"
                
        except Exception as e:
            result['error'] = f"OneDrive图片处理异常: {str(e)}"
            self.log(f"OneDrive图片处理失败: {draft_file}, 错误: {str(e)}", level="error")
            
        return result

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
        elif isinstance(draft, str) and draft.startswith('redirect_to_'):
            # 处理重定向 - 在直接调用时不支持重定向，跳过
            print("此模式下不支持重定向，请直接选择草稿文件")
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
        
    # 确保draft是Path类型
    if not isinstance(draft, Path):
        print("错误：无效的草稿类型")
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