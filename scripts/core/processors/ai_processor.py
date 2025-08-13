"""
AI处理模块
负责AI内容生成、优化和格式化
"""
import logging
import frontmatter
# Path在未来可能需要
from typing import Optional, Dict, Any, List
from google.generativeai.generative_models import GenerativeModel
from google.api_core.exceptions import ResourceExhausted


class AIProcessor:
    """AI处理器 - 负责AI相关的所有操作"""
    
    def __init__(self, model: GenerativeModel, logger: Optional[logging.Logger] = None):
        """
        初始化AI处理器
        
        Args:
            model: Google Gemini模型实例
            logger: 日志记录器
        """
        self.model = model
        self.logger = logger or logging.getLogger(__name__)
        self.api_available = model is not None
    
    def log(self, message: str, level: str = "info", force: bool = False) -> None:
        """
        记录日志
        
        Args:
            message: 日志消息
            level: 日志级别
            force: 是否强制输出
        """
        if self.logger:
            log_func = getattr(self.logger, level)
            log_func(message)
            if force:
                print(f"[{level.upper()}] {message}")
    
    def polish_content(self, content: str) -> Optional[str]:
        """
        使用AI润色文章内容
        
        Args:
            content: 原始内容
            
        Returns:
            润色后的内容，失败时返回原内容
        """
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
                polished_text = self.clean_ai_generated_content(response.text)
                
                # 重新构建完整内容
                post.content = polished_text
                polished_content = frontmatter.dumps(post)
                
                self.log("✅ 内容润色完成", level="info")
                return polished_content
            else:
                self.log("AI响应为空，使用原内容", level="warning")
                return content
                
        except ResourceExhausted:
            self.log("API配额不足，跳过润色", level="warning")
            return content
        except Exception as e:
            self.log(f"润色内容时出错: {str(e)}", level="error")
            return content
    
    def generate_excerpt(self, content: str) -> str:
        """
        生成文章摘要
        
        Args:
            content: 文章内容
            
        Returns:
            生成的摘要
        """
        if not self.api_available:
            self.log("API不可用，使用默认摘要", level="warning")
            return "这是一篇有价值的文章，值得阅读。"
        
        try:
            # 构建简洁的提示词
            prompt = f"""
            请为以下文章生成一个简洁的摘要，要求：
            1. 50-60个字符
            2. 概括文章主要观点
            3. 吸引读者兴趣
            4. 不包含引号或特殊符号
            
            文章内容：
            {content[:1000]}...
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                excerpt = response.text.strip()
                # 确保长度合适
                if len(excerpt) > 100:
                    excerpt = excerpt[:97] + "..."
                
                self.log(f"✅ 生成摘要: {excerpt}", level="debug")
                return excerpt
            else:
                return "探索新知，分享见解。"
                
        except Exception as e:
            self.log(f"生成摘要时出错: {str(e)}", level="error")
            return "这是一篇值得阅读的文章。"
    
    def generate_categories_and_tags(self, content: str, available_categories: Dict[str, List[str]]) -> tuple:
        """
        使用AI生成文章分类和标签
        
        Args:
            content: 文章内容
            available_categories: 可用分类字典
            
        Returns:
            (categories, tags) 元组
        """
        if not self.api_available:
            self.log("API不可用，使用简单匹配分类", level="warning")
            return self._suggest_categories_simple(content, available_categories), []
        
        try:
            # 准备分类选项
            category_options = ", ".join(available_categories.keys())
            
            prompt = f"""
            分析以下文章内容，从给定的分类中选择最合适的1-2个分类，并生成3-5个相关标签。

            可用分类: {category_options}

            要求：
            1. 分类必须从给定选项中选择
            2. 标签应该简洁且相关
            3. 用JSON格式返回，如: {{"categories": ["分类1"], "tags": ["标签1", "标签2"]}}

            文章内容：
            {content[:1500]}
            """
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                import json
                try:
                    result = json.loads(response.text.strip())
                    categories = result.get('categories', [])
                    tags = result.get('tags', [])
                    
                    # 验证分类有效性
                    valid_categories = [cat for cat in categories if cat in available_categories]
                    
                    if valid_categories:
                        self.log(f"✅ AI生成分类: {valid_categories}, 标签: {tags}", level="info")
                        return valid_categories, tags
                    else:
                        self.log("AI生成的分类无效，使用简单匹配", level="warning")
                        return self._suggest_categories_simple(content, available_categories), tags
                        
                except json.JSONDecodeError:
                    self.log("AI响应格式错误，使用简单匹配", level="warning")
                    return self._suggest_categories_simple(content, available_categories), []
            else:
                self.log("AI响应为空，使用简单匹配", level="warning")
                return self._suggest_categories_simple(content, available_categories), []
                
        except Exception as e:
            self.log(f"AI生成分类时出错: {str(e)}", level="error")
            return self._suggest_categories_simple(content, available_categories), []
    
    def generate_platform_content(self, content: str, platform: str, platform_config: Dict[str, Any]) -> str:
        """
        为特定平台生成适配内容
        
        Args:
            content: 原始内容
            platform: 目标平台
            platform_config: 平台配置
            
        Returns:
            适配后的内容
        """
        if not self.api_available:
            self.log(f"API不可用，直接返回原内容用于{platform}平台", level="warning")
            return content
        
        try:
            # 解析内容
            post = frontmatter.loads(content)
            
            # 根据平台类型选择处理方式
            if platform == "blog":
                return self._generate_blog_content(post, platform_config)
            elif platform == "wechat":
                return self._generate_wechat_content(post, platform_config)
            elif platform == "wordpress":
                return self._generate_wordpress_content(post, platform_config)
            else:
                self.log(f"未知平台: {platform}", level="warning")
                return content
                
        except Exception as e:
            self.log(f"生成{platform}平台内容时出错: {str(e)}", level="error")
            return content
    
    def _generate_blog_content(self, post: frontmatter.Post, config: Dict[str, Any]) -> str:
        """生成博客内容"""
        # 为博客平台优化内容格式
        content = post.content
        
        # 添加目录（如果配置要求）
        if config.get("add_toc", False):
            content = self._add_table_of_contents(content)
        
        # 添加阅读时间估算
        if config.get("add_reading_time", False):
            reading_time = self._calculate_reading_time(content)
            content = f"📖 预计阅读时间：{reading_time}分钟\n\n{content}"
        
        return frontmatter.dumps(post)
    
    def _generate_wechat_content(self, post: frontmatter.Post, config: Dict[str, Any]) -> str:
        """生成微信公众号内容"""
        # 微信平台的特殊格式要求
        content = post.content
        
        # 添加emoji和格式优化
        if config.get("optimize_format", True):
            content = self._optimize_wechat_format(content)
        
        return frontmatter.dumps(post)
    
    def _generate_wordpress_content(self, post: frontmatter.Post, config: Dict[str, Any]) -> str:
        """生成WordPress内容"""
        # WordPress平台的格式适配  
        # 目前直接返回原内容，未来可以根据config进行定制
        _ = config  # 避免未使用参数警告
        return frontmatter.dumps(post)
    
    def clean_ai_generated_content(self, content: str) -> str:
        """
        清理AI生成的内容
        
        Args:
            content: AI生成的内容
            
        Returns:
            清理后的内容
        """
        # 移除常见的AI生成标识
        prefixes_to_remove = [
            "以下是润色后的内容：",
            "润色后的文章如下：",
            "修改后的内容：",
            "Here is the polished content:",
            "The refined content is:",
        ]
        
        cleaned_content = content.strip()
        
        for prefix in prefixes_to_remove:
            if cleaned_content.startswith(prefix):
                cleaned_content = cleaned_content[len(prefix):].strip()
        
        # 移除多余的引号
        if cleaned_content.startswith('"') and cleaned_content.endswith('"'):
            cleaned_content = cleaned_content[1:-1].strip()
        
        if cleaned_content.startswith("'") and cleaned_content.endswith("'"):
            cleaned_content = cleaned_content[1:-1].strip()
        
        return cleaned_content.strip()
    
    def _fix_frontmatter_quotes(self, content: str) -> str:
        """
        修复front matter中的引号问题
        
        Args:
            content: 原始内容
            
        Returns:
            修复后的内容
        """
        # 简单的引号修复逻辑
        lines = content.split('\n')
        fixed_lines = []
        in_frontmatter = False
        
        for line in lines:
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                fixed_lines.append(line)
            elif in_frontmatter and ':' in line:
                # 修复YAML中的引号问题
                key, value = line.split(':', 1)
                value = value.strip()
                if value and not value.startswith('"') and not value.startswith("'"):
                    if any(char in value for char in ['"', "'", ':', '\n']):
                        value = f'"{value.replace(chr(92), chr(92)+chr(92)).replace(chr(34), chr(92)+chr(34))}"'
                fixed_lines.append(f"{key}: {value}")
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _suggest_categories_simple(self, content: str, available_categories: Dict[str, List[str]]) -> List[str]:
        """
        简单的分类建议（作为AI的备选方案）
        
        Args:
            content: 文章内容
            available_categories: 可用分类
            
        Returns:
            建议的分类列表
        """
        content_lower = content.lower()
        suggested_categories = []
        
        # 基于关键词匹配
        keyword_mapping = {
            "技术赋能": ["技术", "编程", "代码", "开发", "软件", "工具", "自动化"],
            "认知升级": ["思维", "学习", "认知", "心理", "方法", "模式"],
            "全球视野": ["国际", "全球", "世界", "文化", "趋势", "海外"],
            "投资理财": ["投资", "理财", "金融", "股票", "基金", "经济"]
        }
        
        for category, keywords in keyword_mapping.items():
            if category in available_categories:
                if any(keyword in content_lower for keyword in keywords):
                    suggested_categories.append(category)
        
        return suggested_categories[:2]  # 最多返回2个分类
    
    def _add_table_of_contents(self, content: str) -> str:
        """添加目录"""
        # 简单的目录生成
        import re
        headers = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        
        if len(headers) > 2:
            toc = "## 📋 目录\n\n"
            for i, header in enumerate(headers, 1):
                toc += f"{i}. {header}\n"
            toc += "\n---\n\n"
            return toc + content
        
        return content
    
    def _calculate_reading_time(self, content: str) -> int:
        """计算阅读时间（分钟）"""
        # 假设平均阅读速度为每分钟300字
        word_count = len(content.replace(' ', ''))
        return max(1, round(word_count / 300))
    
    def _optimize_wechat_format(self, content: str) -> str:
        """优化微信格式"""
        # 添加一些微信友好的格式
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            # 为标题添加emoji
            if line.startswith('##'):
                if not any(emoji in line for emoji in ['🔥', '💡', '📊', '🎯', '✨']):
                    line = line.replace('##', '## 💡')
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)