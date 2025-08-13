"""
内容质量验证器
检查内容的质量、可读性和完整性
"""
import re
from typing import Dict, Any, List, Optional
from collections import Counter

from .content_validator import (
    ContentValidator,
    ValidationResult,
    ValidationSeverity,
    ValidationRule
)


class QualityValidator(ContentValidator):
    """内容质量验证器"""
    
    def _setup_rules(self) -> None:
        """设置验证规则"""
        self.rules = [
            ValidationRule(
                name="readability",
                description="检查内容可读性",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="word_count",
                description="检查字数统计",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="sentence_length",
                description="检查句子长度",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="repetition",
                description="检查内容重复",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="completeness",
                description="检查内容完整性",
                severity=ValidationSeverity.WARNING
            ),
            ValidationRule(
                name="formatting_consistency",
                description="检查格式一致性",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="language_quality",
                description="检查语言质量",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="technical_terms",
                description="检查技术术语使用",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="call_to_action",
                description="检查行动号召",
                severity=ValidationSeverity.INFO
            )
        ]
    
    def validate_content(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[ValidationResult]:
        """验证内容质量"""
        results = []
        
        # 提取正文内容
        body_content = self._extract_body_content(content)
        
        # 检查字数和可读性
        word_stats = self._analyze_word_statistics(body_content)
        readability_results = self._check_readability(body_content, word_stats)
        results.extend(readability_results)
        
        # 检查句子长度
        sentence_results = self._check_sentence_length(body_content)
        results.extend(sentence_results)
        
        # 检查内容重复
        repetition_results = self._check_repetition(body_content)
        results.extend(repetition_results)
        
        # 检查内容完整性
        completeness_results = self._check_completeness(content)
        results.extend(completeness_results)
        
        # 检查格式一致性
        formatting_results = self._check_formatting_consistency(body_content)
        results.extend(formatting_results)
        
        # 检查语言质量
        language_results = self._check_language_quality(body_content)
        results.extend(language_results)
        
        # 检查技术术语
        tech_results = self._check_technical_terms(body_content)
        results.extend(tech_results)
        
        # 检查行动号召
        cta_results = self._check_call_to_action(body_content)
        results.extend(cta_results)
        
        return results
    
    def _extract_body_content(self, content: str) -> str:
        """提取正文内容"""
        if content.strip().startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content
    
    def _analyze_word_statistics(self, content: str) -> Dict[str, Any]:
        """分析文字统计信息"""
        # 清理内容
        clean_text = self._clean_text_for_analysis(content)
        
        # 中文字符统计
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', clean_text))
        
        # 英文单词统计
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', clean_text))
        
        # 句子统计
        sentences = re.split(r'[.!?。！？]+', clean_text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # 段落统计
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)
        
        return {
            'chinese_chars': chinese_chars,
            'english_words': english_words,
            'total_words': chinese_chars + english_words,
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count,
            'clean_text': clean_text
        }
    
    def _clean_text_for_analysis(self, content: str) -> str:
        """清理文本用于分析"""
        # 移除Markdown语法
        clean = re.sub(r'```.*?```', '', content, flags=re.DOTALL)  # 代码块
        clean = re.sub(r'`[^`]*`', '', clean)                       # 内联代码
        clean = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', clean)          # 图片
        clean = re.sub(r'\[[^\]]*\]\([^)]*\)', '', clean)           # 链接
        clean = re.sub(r'^#+\s*', '', clean, flags=re.MULTILINE)    # 标题
        clean = re.sub(r'^\s*[-*+]\s*', '', clean, flags=re.MULTILINE)  # 列表
        clean = re.sub(r'^\s*>\s*', '', clean, flags=re.MULTILINE)  # 引用
        clean = re.sub(r'\*\*([^*]*)\*\*', r'\1', clean)           # 粗体
        clean = re.sub(r'\*([^*]*)\*', r'\1', clean)               # 斜体
        clean = re.sub(r'~~([^~]*)~~', r'\1', clean)               # 删除线
        
        return clean
    
    def _check_readability(self, content: str, stats: Dict[str, Any]) -> List[ValidationResult]:
        """检查可读性"""
        results = []
        
        # 字数检查
        total_words = stats['total_words']
        if total_words < 300:
            results.append(ValidationResult(
                rule_name="word_count",
                severity=ValidationSeverity.WARNING,
                message=f"内容偏短 ({total_words}字)",
                suggestion="建议文章至少500字以提供充分的信息价值"
            ))
        elif total_words < 500:
            results.append(ValidationResult(
                rule_name="word_count",
                severity=ValidationSeverity.INFO,
                message=f"内容中等长度 ({total_words}字)",
                suggestion="可考虑适当展开内容以提供更深入的见解"
            ))
        elif total_words > 3000:
            results.append(ValidationResult(
                rule_name="word_count",
                severity=ValidationSeverity.INFO,
                message=f"内容较长 ({total_words}字)",
                suggestion="考虑使用小标题分段，或分拆为系列文章"
            ))
        
        # 段落密度检查
        if stats['paragraph_count'] > 0:
            words_per_paragraph = total_words / stats['paragraph_count']
            if words_per_paragraph > 200:
                results.append(ValidationResult(
                    rule_name="readability",
                    severity=ValidationSeverity.INFO,
                    message=f"段落平均长度较长 ({words_per_paragraph:.0f}字/段)",
                    suggestion="考虑将长段落分解为更短的段落以提高可读性"
                ))
        
        # 句子密度检查
        if stats['sentence_count'] > 0:
            words_per_sentence = total_words / stats['sentence_count']
            if words_per_sentence > 30:
                results.append(ValidationResult(
                    rule_name="readability",
                    severity=ValidationSeverity.INFO,
                    message=f"句子平均长度较长 ({words_per_sentence:.0f}字/句)",
                    suggestion="考虑使用更短的句子以提高可读性"
                ))
        
        return results
    
    def _check_sentence_length(self, content: str) -> List[ValidationResult]:
        """检查句子长度"""
        results = []
        
        # 分割句子
        sentences = re.split(r'[.!?。！？]+', content)
        long_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 100:  # 超过100字符的句子
                long_sentences.append(sentence[:50] + "...")
        
        if long_sentences:
            results.append(ValidationResult(
                rule_name="sentence_length",
                severity=ValidationSeverity.INFO,
                message=f"发现{len(long_sentences)}个过长句子",
                suggestion="考虑将长句分解为更短、更易理解的句子"
            ))
        
        return results
    
    def _check_repetition(self, content: str) -> List[ValidationResult]:
        """检查内容重复"""
        results = []
        
        # 检查词语重复
        words = re.findall(r'[\u4e00-\u9fff]+|\b[a-zA-Z]+\b', content.lower())
        word_counts = Counter(words)
        
        # 找出高频词（排除常见词）
        common_words = {'的', '了', '是', '在', '和', '有', '一', '这', '我', '们', '你', '他', '她', '它',
                       'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        high_freq_words = [(word, count) for word, count in word_counts.most_common(10) 
                          if count > 5 and word not in common_words and len(word) > 2]
        
        if high_freq_words:
            results.append(ValidationResult(
                rule_name="repetition",
                severity=ValidationSeverity.INFO,
                message=f"词语重复较多: {', '.join([f'{w}({c}次)' for w, c in high_freq_words[:3]])}",
                suggestion="考虑使用同义词或重新组织内容以减少重复"
            ))
        
        # 检查句子重复
        sentences = [s.strip() for s in re.split(r'[.!?。！？]+', content) if s.strip()]
        sentence_counts = Counter(sentences)
        repeated_sentences = [(s, c) for s, c in sentence_counts.items() if c > 1 and len(s) > 10]
        
        if repeated_sentences:
            results.append(ValidationResult(
                rule_name="repetition",
                severity=ValidationSeverity.WARNING,
                message=f"发现{len(repeated_sentences)}个重复句子",
                suggestion="检查并消除重复的句子"
            ))
        
        return results
    
    def _check_completeness(self, content: str) -> List[ValidationResult]:
        """检查内容完整性"""
        results = []
        
        # 检查是否有结论
        body_content = self._extract_body_content(content)
        
        conclusion_indicators = ['总结', '结论', '综上', '最后', '总的来说', '总而言之', 
                               'conclusion', 'summary', 'in conclusion', 'to summarize']
        
        has_conclusion = any(indicator in body_content.lower() for indicator in conclusion_indicators)
        
        if not has_conclusion and len(body_content) > 500:
            results.append(ValidationResult(
                rule_name="completeness",
                severity=ValidationSeverity.INFO,
                message="文章可能缺少总结或结论",
                suggestion="考虑添加总结段落以帮助读者理解要点"
            ))
        
        # 检查是否有引言
        first_paragraph = body_content.split('\n\n')[0] if '\n\n' in body_content else body_content[:200]
        intro_indicators = ['本文', '本篇', '这篇文章', '今天', '我们将', '让我们', 
                           'this article', 'in this post', 'today we']
        
        has_intro = any(indicator in first_paragraph.lower() for indicator in intro_indicators)
        
        if not has_intro and len(body_content) > 800:
            results.append(ValidationResult(
                rule_name="completeness",
                severity=ValidationSeverity.INFO,
                message="文章可能缺少明确的引言",
                suggestion="考虑在开头说明文章的主题和目标"
            ))
        
        return results
    
    def _check_formatting_consistency(self, content: str) -> List[ValidationResult]:
        """检查格式一致性"""
        results = []
        
        # 检查列表标记一致性
        list_markers = re.findall(r'^(\s*)([-*+])\s', content, re.MULTILINE)
        if list_markers:
            markers = [marker[1] for marker in list_markers]
            unique_markers = set(markers)
            if len(unique_markers) > 1:
                results.append(ValidationResult(
                    rule_name="formatting_consistency",
                    severity=ValidationSeverity.INFO,
                    message=f"使用了多种列表标记: {', '.join(unique_markers)}",
                    suggestion="建议在整篇文章中使用一致的列表标记"
                ))
        
        # 检查强调标记一致性
        bold_single = len(re.findall(r'\*[^*]+\*(?!\*)', content))
        bold_double = len(re.findall(r'\*\*[^*]+\*\*', content))
        
        if bold_single > 0 and bold_double > 0:
            results.append(ValidationResult(
                rule_name="formatting_consistency",
                severity=ValidationSeverity.INFO,
                message="混合使用了*和**进行强调",
                suggestion="建议统一使用**表示粗体，*表示斜体"
            ))
        
        return results
    
    def _check_language_quality(self, content: str) -> List[ValidationResult]:
        """检查语言质量"""
        results = []
        
        # 检查常见语言问题
        issues = []
        
        # 检查重复标点
        if re.search(r'[。！？]{2,}', content):
            issues.append("重复标点符号")
        
        # 检查空格使用（中英文之间）
        if re.search(r'[\u4e00-\u9fff][a-zA-Z]|[a-zA-Z][\u4e00-\u9fff]', content):
            space_issues = len(re.findall(r'[\u4e00-\u9fff][a-zA-Z]|[a-zA-Z][\u4e00-\u9fff]', content))
            if space_issues > 3:  # 允许少量不规范
                issues.append("中英文之间缺少空格")
        
        # 检查全角半角混用
        if re.search(r'[，。！？].*[,\.!?]|[,\.!?].*[，。！？]', content):
            issues.append("全角半角标点混用")
        
        if issues:
            results.append(ValidationResult(
                rule_name="language_quality",
                severity=ValidationSeverity.INFO,
                message=f"语言格式问题: {', '.join(issues)}",
                suggestion="检查并修正语言格式问题以提高专业性"
            ))
        
        return results
    
    def _check_technical_terms(self, content: str) -> List[ValidationResult]:
        """检查技术术语使用"""
        results = []
        
        # 检查是否定义了专业术语
        tech_terms = re.findall(r'\b[A-Z]{2,}\b|\b[A-Z][a-z]*[A-Z][A-Za-z]*\b', content)
        unique_terms = list(set(term for term in tech_terms if len(term) > 2))
        
        if len(unique_terms) > 5:
            results.append(ValidationResult(
                rule_name="technical_terms",
                severity=ValidationSeverity.INFO,
                message=f"使用了较多技术术语 ({len(unique_terms)}个)",
                suggestion="考虑为首次出现的专业术语添加解释"
            ))
        
        return results
    
    def _check_call_to_action(self, content: str) -> List[ValidationResult]:
        """检查行动号召"""
        results = []
        
        # 常见的行动号召词汇
        cta_indicators = ['关注', '订阅', '分享', '评论', '点赞', '收藏', '转发', 
                         '联系', '咨询', '了解更多', '访问', '下载', '购买',
                         'follow', 'subscribe', 'share', 'comment', 'like', 
                         'bookmark', 'contact', 'learn more', 'visit', 'download']
        
        has_cta = any(indicator in content.lower() for indicator in cta_indicators)
        
        if not has_cta and len(content) > 800:
            results.append(ValidationResult(
                rule_name="call_to_action",
                severity=ValidationSeverity.INFO,
                message="文章可能缺少行动号召",
                suggestion="考虑在文末添加鼓励读者互动的内容"
            ))
        
        return results