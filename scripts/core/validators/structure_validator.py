"""
文档结构验证器
检查Markdown文档的结构和格式问题
"""
import re
from typing import Dict, Any, List, Optional

from .content_validator import (
    ContentValidator,
    ValidationResult,
    ValidationSeverity,
    ValidationRule
)


class StructureValidator(ContentValidator):
    """文档结构验证器"""
    
    def _setup_rules(self) -> None:
        """设置验证规则"""
        self.rules = [
            ValidationRule(
                name="more_tag",
                description="检查是否有<!-- more -->标签",
                severity=ValidationSeverity.WARNING
            ),
            ValidationRule(
                name="heading_hierarchy",
                description="检查标题层级结构",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="content_length",
                description="检查内容长度",
                severity=ValidationSeverity.WARNING
            ),
            ValidationRule(
                name="paragraph_structure",
                description="检查段落结构",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="list_formatting",
                description="检查列表格式",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="code_blocks",
                description="检查代码块格式",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="link_format",
                description="检查链接格式",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="quote_blocks",
                description="检查引用块格式",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="table_format",
                description="检查表格格式",
                severity=ValidationSeverity.INFO
            )
        ]
    
    def validate_content(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[ValidationResult]:
        """验证文档结构"""
        results = []
        
        # 分离Front Matter和正文内容
        body_content = self._extract_body_content(content)
        
        # 检查<!-- more -->标签
        if '<!-- more -->' not in content:
            results.append(ValidationResult(
                rule_name="more_tag",
                severity=ValidationSeverity.WARNING,
                message="缺少<!-- more -->分页标签",
                suggestion="添加<!-- more -->标签分隔摘要和正文，提供更好的首页体验"
            ))
        
        # 检查内容长度
        clean_content = self._clean_content_for_length_check(body_content)
        content_length = len(clean_content.strip())
        
        if content_length < 300:
            results.append(ValidationResult(
                rule_name="content_length",
                severity=ValidationSeverity.WARNING,
                message=f"内容过短 ({content_length}字符)",
                suggestion="建议文章内容至少500字符以提供有价值的信息"
            ))
        elif content_length < 500:
            results.append(ValidationResult(
                rule_name="content_length",
                severity=ValidationSeverity.INFO,
                message=f"内容较短 ({content_length}字符)",
                suggestion="考虑丰富内容以提供更全面的信息"
            ))
        
        # 检查标题层级
        heading_issues = self._check_heading_hierarchy(body_content)
        results.extend(heading_issues)
        
        # 检查段落结构
        paragraph_issues = self._check_paragraph_structure(body_content)
        results.extend(paragraph_issues)
        
        # 检查列表格式
        list_issues = self._check_list_formatting(body_content)
        results.extend(list_issues)
        
        # 检查代码块格式
        code_issues = self._check_code_blocks(body_content)
        results.extend(code_issues)
        
        # 检查链接格式
        link_issues = self._check_link_format(body_content)
        results.extend(link_issues)
        
        # 检查引用块格式
        quote_issues = self._check_quote_blocks(body_content)
        results.extend(quote_issues)
        
        # 检查表格格式
        table_issues = self._check_table_format(body_content)
        results.extend(table_issues)
        
        return results
    
    def _extract_body_content(self, content: str) -> str:
        """提取正文内容，排除Front Matter"""
        if content.strip().startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content
    
    def _clean_content_for_length_check(self, content: str) -> str:
        """清理内容用于长度检查"""
        # 移除Markdown语法标记
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
    
    def _check_heading_hierarchy(self, content: str) -> List[ValidationResult]:
        """检查标题层级结构"""
        results = []
        heading_pattern = r'^(#{1,6})\s+(.*)$'
        headings = []
        
        for line_num, line in enumerate(content.split('\n'), 1):
            match = re.match(heading_pattern, line.strip())
            if match:
                level = len(match.group(1))
                text = match.group(2).strip()
                headings.append((level, text, line_num))
        
        if not headings:
            results.append(ValidationResult(
                rule_name="heading_hierarchy",
                severity=ValidationSeverity.INFO,
                message="文档没有使用标题结构",
                suggestion="考虑使用标题(# ## ###)来组织内容结构"
            ))
            return results
        
        # 检查标题层级跳跃
        for i in range(1, len(headings)):
            prev_level = headings[i-1][0]
            curr_level = headings[i][0]
            
            if curr_level > prev_level + 1:
                results.append(ValidationResult(
                    rule_name="heading_hierarchy",
                    severity=ValidationSeverity.INFO,
                    message=f"标题层级跳跃：从H{prev_level}跳到H{curr_level} (行{headings[i][2]})",
                    suggestion="建议按顺序使用标题层级，如H1→H2→H3"
                ))
        
        # 检查是否从H1开始
        if headings and headings[0][0] > 2:
            results.append(ValidationResult(
                rule_name="heading_hierarchy",
                severity=ValidationSeverity.INFO,
                message=f"文档从H{headings[0][0]}开始",
                suggestion="建议从H1或H2标题开始文档结构"
            ))
        
        return results
    
    def _check_paragraph_structure(self, content: str) -> List[ValidationResult]:
        """检查段落结构"""
        results = []
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        # 检查是否有段落
        if len(paragraphs) < 2:
            results.append(ValidationResult(
                rule_name="paragraph_structure",
                severity=ValidationSeverity.INFO,
                message="内容缺少段落分隔",
                suggestion="使用空行分隔段落以提高可读性"
            ))
        
        # 检查过长的段落
        for i, paragraph in enumerate(paragraphs):
            if len(paragraph) > 1000:
                results.append(ValidationResult(
                    rule_name="paragraph_structure",
                    severity=ValidationSeverity.INFO,
                    message=f"第{i+1}段过长 ({len(paragraph)}字符)",
                    suggestion="考虑将长段落分解为多个较短的段落"
                ))
        
        return results
    
    def _check_list_formatting(self, content: str) -> List[ValidationResult]:
        """检查列表格式"""
        results = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 检查列表项格式
            if re.match(r'^[-*+]\s', stripped):
                # 检查列表项后是否有空格
                if re.match(r'^[-*+][^\s]', stripped):
                    results.append(ValidationResult(
                        rule_name="list_formatting",
                        severity=ValidationSeverity.INFO,
                        message=f"列表项缺少空格 (行{line_num})",
                        suggestion="列表标记后应该加一个空格：- 项目内容"
                    ))
            
            # 检查有序列表格式
            elif re.match(r'^\d+\.', stripped):
                if re.match(r'^\d+\.[^\s]', stripped):
                    results.append(ValidationResult(
                        rule_name="list_formatting",
                        severity=ValidationSeverity.INFO,
                        message=f"有序列表项缺少空格 (行{line_num})",
                        suggestion="数字后应该加空格：1. 项目内容"
                    ))
        
        return results
    
    def _check_code_blocks(self, content: str) -> List[ValidationResult]:
        """检查代码块格式"""
        results = []
        
        # 检查代码块配对
        code_block_pattern = r'```'
        code_blocks = list(re.finditer(code_block_pattern, content))
        
        if len(code_blocks) % 2 != 0:
            results.append(ValidationResult(
                rule_name="code_blocks",
                severity=ValidationSeverity.ERROR,
                message="代码块标记不配对",
                suggestion="确保每个```开始标记都有对应的结束标记"
            ))
        
        # 检查内联代码
        inline_code_pattern = r'`[^`\n]*`'
        single_backticks = re.findall(r'`', content)
        inline_codes = re.findall(inline_code_pattern, content)
        
        if len(single_backticks) != len(inline_codes) * 2:
            # 可能有未配对的内联代码标记
            results.append(ValidationResult(
                rule_name="code_blocks",
                severity=ValidationSeverity.INFO,
                message="可能存在未配对的内联代码标记",
                suggestion="检查所有反引号(`)是否正确配对"
            ))
        
        return results
    
    def _check_link_format(self, content: str) -> List[ValidationResult]:
        """检查链接格式"""
        results = []
        
        # 检查Markdown链接格式
        link_pattern = r'\[([^\]]*)\]\(([^)]*)\)'
        links = re.findall(link_pattern, content)
        
        for link_text, link_url in links:
            if not link_text.strip():
                results.append(ValidationResult(
                    rule_name="link_format",
                    severity=ValidationSeverity.INFO,
                    message=f"链接缺少描述文本: {link_url[:50]}",
                    suggestion="为链接添加描述性文本有助于用户体验和无障碍访问"
                ))
            
            if not link_url.strip():
                results.append(ValidationResult(
                    rule_name="link_format",
                    severity=ValidationSeverity.ERROR,
                    message=f"链接缺少URL: [{link_text}]",
                    suggestion="为链接添加有效的URL"
                ))
        
        # 检查可能的裸URL
        url_pattern = r'https?://[^\s<>"]+[^\s<>"\.]'
        bare_urls = re.findall(url_pattern, content)
        
        if bare_urls:
            results.append(ValidationResult(
                rule_name="link_format",
                severity=ValidationSeverity.INFO,
                message=f"发现{len(bare_urls)}个裸URL",
                suggestion="考虑将裸URL转换为Markdown链接格式：[描述](URL)"
            ))
        
        return results
    
    def _check_quote_blocks(self, content: str) -> List[ValidationResult]:
        """检查引用块格式"""
        results = []
        lines = content.split('\n')
        
        in_quote = False
        quote_start = None
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if stripped.startswith('>'):
                if not in_quote:
                    in_quote = True
                    quote_start = line_num
                    
                # 检查引用格式
                if not re.match(r'^>\s+', stripped) and len(stripped) > 1:
                    results.append(ValidationResult(
                        rule_name="quote_blocks",
                        severity=ValidationSeverity.INFO,
                        message=f"引用块格式不规范 (行{line_num})",
                        suggestion="引用标记>后应该加空格"
                    ))
            else:
                if in_quote:
                    in_quote = False
                    quote_start = None
        
        return results
    
    def _check_table_format(self, content: str) -> List[ValidationResult]:
        """检查表格格式"""
        results = []
        lines = content.split('\n')
        
        in_table = False
        table_start = None
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 检查是否是表格行
            if '|' in stripped and stripped.count('|') >= 2:
                if not in_table:
                    in_table = True
                    table_start = line_num
                
                # 检查表格格式
                if not stripped.startswith('|') or not stripped.endswith('|'):
                    results.append(ValidationResult(
                        rule_name="table_format",
                        severity=ValidationSeverity.INFO,
                        message=f"表格行格式不规范 (行{line_num})",
                        suggestion="表格行应该以|开始和结束"
                    ))
            else:
                if in_table:
                    in_table = False
                    table_start = None
        
        return results