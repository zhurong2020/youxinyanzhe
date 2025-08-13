"""
Front Matter验证器
验证Jekyll/Markdown Front Matter的格式和必需字段
"""
import re
from typing import Dict, Any, List, Optional
import frontmatter

from .content_validator import (
    ContentValidator,
    ValidationResult,
    ValidationSeverity,
    ValidationRule
)


class FrontMatterValidator(ContentValidator):
    """Front Matter验证器"""
    
    def __init__(self, required_fields: Optional[List[str]] = None, logger=None):
        self.required_fields = required_fields or ['title', 'date', 'header']
        self.recommended_fields = ['categories', 'tags', 'excerpt']
        super().__init__(logger)
    
    def _setup_rules(self) -> None:
        """设置验证规则"""
        self.rules = [
            ValidationRule(
                name="frontmatter_exists",
                description="检查是否存在Front Matter",
                severity=ValidationSeverity.ERROR
            ),
            ValidationRule(
                name="frontmatter_format",
                description="检查Front Matter格式是否正确",
                severity=ValidationSeverity.ERROR
            ),
            ValidationRule(
                name="required_fields",
                description="检查必需字段是否存在",
                severity=ValidationSeverity.ERROR
            ),
            ValidationRule(
                name="title_length",
                description="检查标题长度是否合适",
                severity=ValidationSeverity.WARNING
            ),
            ValidationRule(
                name="date_format",
                description="检查日期格式",
                severity=ValidationSeverity.WARNING
            ),
            ValidationRule(
                name="header_teaser",
                description="检查header.teaser图片路径",
                severity=ValidationSeverity.WARNING
            ),
            ValidationRule(
                name="recommended_fields",
                description="检查推荐字段",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="categories_format",
                description="检查分类格式",
                severity=ValidationSeverity.WARNING
            ),
            ValidationRule(
                name="tags_format", 
                description="检查标签格式",
                severity=ValidationSeverity.WARNING
            ),
            ValidationRule(
                name="excerpt_length",
                description="检查摘要长度",
                severity=ValidationSeverity.INFO
            )
        ]
    
    def validate_content(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[ValidationResult]:
        """验证Front Matter"""
        results = []
        
        # 检查是否存在Front Matter
        if not self._has_frontmatter(content):
            results.append(ValidationResult(
                rule_name="frontmatter_exists",
                severity=ValidationSeverity.ERROR,
                message="缺少Jekyll Front Matter",
                suggestion="在文件开头添加Front Matter，例如:\n---\ntitle: 文章标题\ndate: 2023-01-01\n---"
            ))
            return results
        
        # 解析Front Matter
        try:
            post = frontmatter.loads(content)
            fm_data = post.metadata
        except Exception as e:
            results.append(ValidationResult(
                rule_name="frontmatter_format",
                severity=ValidationSeverity.ERROR,
                message=f"Front Matter格式错误: {str(e)}",
                suggestion="检查YAML格式是否正确，确保引号配对、缩进正确"
            ))
            # 尝试修复并重新解析
            fixed_content = self._try_fix_frontmatter(content)
            if fixed_content != content:
                try:
                    post = frontmatter.loads(fixed_content)
                    fm_data = post.metadata
                    results.append(ValidationResult(
                        rule_name="frontmatter_format",
                        severity=ValidationSeverity.INFO,
                        message="Front Matter已自动修复",
                        suggestion="建议检查修复后的格式是否正确"
                    ))
                except Exception:
                    return results
            else:
                return results
        
        # 检查必需字段
        missing_fields = [field for field in self.required_fields if field not in fm_data or not fm_data[field]]
        if missing_fields:
            results.append(ValidationResult(
                rule_name="required_fields",
                severity=ValidationSeverity.ERROR,
                message=f"缺少必需字段: {', '.join(missing_fields)}",
                suggestion=f"请在Front Matter中添加: {', '.join(missing_fields)}"
            ))
        
        # 检查标题长度
        if 'title' in fm_data:
            title = str(fm_data['title'])
            title_len = len(title)
            if title_len < 10:
                results.append(ValidationResult(
                    rule_name="title_length",
                    severity=ValidationSeverity.WARNING,
                    message=f"标题过短 ({title_len}字符)",
                    suggestion="建议标题长度为25-35字符，更有利于SEO"
                ))
            elif title_len > 60:
                results.append(ValidationResult(
                    rule_name="title_length",
                    severity=ValidationSeverity.WARNING,
                    message=f"标题过长 ({title_len}字符)",
                    suggestion="建议标题长度为25-35字符，避免在搜索结果中被截断"
                ))
        
        # 检查日期格式
        if 'date' in fm_data:
            date_str = str(fm_data['date'])
            if not self._is_valid_date_format(date_str):
                results.append(ValidationResult(
                    rule_name="date_format",
                    severity=ValidationSeverity.WARNING,
                    message=f"日期格式不规范: {date_str}",
                    suggestion="建议使用格式: YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS"
                ))
        
        # 检查header.teaser路径
        if 'header' in fm_data and isinstance(fm_data['header'], dict):
            if 'teaser' in fm_data['header']:
                teaser_path = str(fm_data['header']['teaser'])
                if self._has_problematic_image_path(teaser_path):
                    results.append(ValidationResult(
                        rule_name="header_teaser",
                        severity=ValidationSeverity.WARNING,
                        message="header.teaser使用本地路径",
                        suggestion="建议使用相对路径: {{ site.baseurl }}/assets/images/..."
                    ))
        
        # 检查推荐字段
        missing_recommended = [field for field in self.recommended_fields 
                             if field not in fm_data or not fm_data[field]]
        if missing_recommended:
            results.append(ValidationResult(
                rule_name="recommended_fields",
                severity=ValidationSeverity.INFO,
                message=f"建议添加字段: {', '.join(missing_recommended)}",
                suggestion="这些字段有助于内容分类和SEO优化"
            ))
        
        # 检查分类格式
        if 'categories' in fm_data:
            categories = fm_data['categories']
            if not isinstance(categories, list):
                results.append(ValidationResult(
                    rule_name="categories_format",
                    severity=ValidationSeverity.WARNING,
                    message="分类应该是数组格式",
                    suggestion="使用格式: categories: [\"category1\", \"category2\"]"
                ))
            elif len(categories) == 0:
                results.append(ValidationResult(
                    rule_name="categories_format",
                    severity=ValidationSeverity.INFO,
                    message="未设置分类",
                    suggestion="建议添加1-2个相关分类"
                ))
        
        # 检查标签格式
        if 'tags' in fm_data:
            tags = fm_data['tags']
            if not isinstance(tags, list):
                results.append(ValidationResult(
                    rule_name="tags_format",
                    severity=ValidationSeverity.WARNING,
                    message="标签应该是数组格式",
                    suggestion="使用格式: tags: [\"tag1\", \"tag2\", \"tag3\"]"
                ))
            elif len(tags) == 0:
                results.append(ValidationResult(
                    rule_name="tags_format",
                    severity=ValidationSeverity.INFO,
                    message="未设置标签",
                    suggestion="建议添加3-5个相关标签"
                ))
            elif len(tags) > 8:
                results.append(ValidationResult(
                    rule_name="tags_format",
                    severity=ValidationSeverity.WARNING,
                    message=f"标签过多 ({len(tags)}个)",
                    suggestion="建议控制在3-8个标签以内"
                ))
        
        # 检查摘要长度
        if 'excerpt' in fm_data:
            excerpt = str(fm_data['excerpt'])
            excerpt_len = len(excerpt)
            if excerpt_len < 30:
                results.append(ValidationResult(
                    rule_name="excerpt_length",
                    severity=ValidationSeverity.INFO,
                    message=f"摘要过短 ({excerpt_len}字符)",
                    suggestion="建议摘要长度为50-150字符"
                ))
            elif excerpt_len > 200:
                results.append(ValidationResult(
                    rule_name="excerpt_length",
                    severity=ValidationSeverity.WARNING,
                    message=f"摘要过长 ({excerpt_len}字符)",
                    suggestion="建议摘要长度为50-150字符"
                ))
        
        return results
    
    def _has_frontmatter(self, content: str) -> bool:
        """检查是否有Front Matter"""
        return content.strip().startswith('---')
    
    def _is_valid_date_format(self, date_str: str) -> bool:
        """检查日期格式是否有效"""
        date_patterns = [
            r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',  # YYYY-MM-DD HH:MM:SS
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$',  # ISO format
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$',  # YYYY-MM-DD HH:MM
        ]
        
        return any(re.match(pattern, date_str) for pattern in date_patterns)
    
    def _has_problematic_image_path(self, path: str) -> bool:
        """检查是否是有问题的图片路径"""
        problematic_patterns = [
            r'^[a-zA-Z]:',  # Windows绝对路径
            r'^/',  # Unix绝对路径
            r'file://',  # 文件协议
        ]
        
        return any(re.match(pattern, path) for pattern in problematic_patterns)
    
    def _try_fix_frontmatter(self, content: str) -> str:
        """尝试修复Front Matter中的常见问题"""
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
                    # 如果值包含特殊字符，添加引号
                    if any(char in value for char in ['"', "'", ':', '\n', '#']):
                        # 转义现有的双引号
                        value = value.replace('"', '\\"')
                        value = f'"{value}"'
                fixed_lines.append(f"{key}: {value}")
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def set_required_fields(self, fields: List[str]) -> None:
        """设置必需字段"""
        self.required_fields = fields
    
    def add_required_field(self, field: str) -> None:
        """添加必需字段"""
        if field not in self.required_fields:
            self.required_fields.append(field)
    
    def remove_required_field(self, field: str) -> None:
        """移除必需字段"""
        if field in self.required_fields:
            self.required_fields.remove(field)