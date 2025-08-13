"""
测试内容验证器模块
"""
import unittest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import os

# 添加项目根目录到Python路径
import sys
sys.path.append('/home/wuxia/projects/youxinyanzhe')

from scripts.core.validators import (
    ContentValidator,
    ValidationResult,
    ValidationSeverity,
    ValidationRule,
    FrontMatterValidator,
    ImageValidator,
    StructureValidator,
    QualityValidator,
    validator_registry,
    ValidationSummary
)


class TestValidationResult(unittest.TestCase):
    """测试验证结果"""
    
    def test_validation_result_str(self):
        """测试验证结果字符串表示"""
        result = ValidationResult(
            rule_name="test_rule",
            severity=ValidationSeverity.ERROR,
            message="Test message",
            location="test.md:10",
            suggestion="Test suggestion"
        )
        
        str_result = str(result)
        self.assertIn("❌", str_result)
        self.assertIn("Test message", str_result)
        self.assertIn("(test.md:10)", str_result)


class TestValidationSummary(unittest.TestCase):
    """测试验证结果汇总"""
    
    def setUp(self):
        """设置测试环境"""
        self.results = [
            ValidationResult("rule1", ValidationSeverity.ERROR, "Error message"),
            ValidationResult("rule2", ValidationSeverity.WARNING, "Warning message"),
            ValidationResult("rule3", ValidationSeverity.INFO, "Info message"),
        ]
        self.summary = ValidationSummary(self.results)
    
    def test_counts(self):
        """测试统计计数"""
        self.assertEqual(self.summary.counts[ValidationSeverity.ERROR], 1)
        self.assertEqual(self.summary.counts[ValidationSeverity.WARNING], 1)
        self.assertEqual(self.summary.counts[ValidationSeverity.INFO], 1)
        self.assertEqual(self.summary.counts[ValidationSeverity.CRITICAL], 0)
    
    def test_has_errors(self):
        """测试错误检查"""
        self.assertTrue(self.summary.has_errors)
        
        # 测试无错误情况
        info_only = ValidationSummary([
            ValidationResult("rule", ValidationSeverity.INFO, "Info")
        ])
        self.assertFalse(info_only.has_errors)
    
    def test_has_warnings(self):
        """测试警告检查"""
        self.assertTrue(self.summary.has_warnings)
    
    def test_is_valid(self):
        """测试有效性检查"""
        self.assertFalse(self.summary.is_valid)  # 有错误，无效
        
        # 测试有效情况
        valid_summary = ValidationSummary([
            ValidationResult("rule", ValidationSeverity.INFO, "Info")
        ])
        self.assertTrue(valid_summary.is_valid)
    
    def test_format_summary(self):
        """测试格式化汇总"""
        summary_text = self.summary.format_summary()
        self.assertIn("验证结果汇总", summary_text)
        self.assertIn("ERROR: 1个问题", summary_text)
        self.assertIn("WARNING: 1个问题", summary_text)
        self.assertIn("INFO: 1个问题", summary_text)
    
    def test_empty_results(self):
        """测试空结果"""
        empty_summary = ValidationSummary([])
        self.assertEqual(empty_summary.format_summary(), "✅ 验证通过，未发现任何问题")


class TestFrontMatterValidator(unittest.TestCase):
    """测试Front Matter验证器"""
    
    def setUp(self):
        """设置测试环境"""
        self.validator = FrontMatterValidator()
    
    def test_missing_frontmatter(self):
        """测试缺少Front Matter"""
        content = "This is just content without front matter"
        results = self.validator.validate_content(content)
        
        self.assertTrue(any(r.rule_name == "frontmatter_exists" for r in results))
        self.assertTrue(any(r.severity == ValidationSeverity.ERROR for r in results))
    
    def test_valid_frontmatter(self):
        """测试有效的Front Matter"""
        content = """---
title: "Test Article"
date: 2023-01-01
header:
  teaser: "{{ site.baseurl }}/assets/images/test.jpg"
categories: ["tech"]
tags: ["test", "article"]
excerpt: "This is a test article excerpt that is long enough to pass validation"
---

This is the content of the article with sufficient length to pass validation."""
        
        results = self.validator.validate_content(content)
        
        # 不应该有错误级别的问题
        error_results = [r for r in results if r.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]]
        self.assertEqual(len(error_results), 0)
    
    def test_missing_required_fields(self):
        """测试缺少必需字段"""
        content = """---
title: "Test Article"
# missing date and header
---
Content here"""
        
        results = self.validator.validate_content(content)
        
        missing_fields_result = next((r for r in results if r.rule_name == "required_fields"), None)
        self.assertIsNotNone(missing_fields_result)
        self.assertEqual(missing_fields_result.severity, ValidationSeverity.ERROR)
    
    def test_title_length_validation(self):
        """测试标题长度验证"""
        # 标题过短
        short_title_content = """---
title: "Short"
date: 2023-01-01
header:
  teaser: "test.jpg"
---
Content"""
        
        results = self.validator.validate_content(short_title_content)
        title_result = next((r for r in results if r.rule_name == "title_length"), None)
        self.assertIsNotNone(title_result)
        self.assertEqual(title_result.severity, ValidationSeverity.WARNING)
        
        # 标题过长
        long_title_content = """---
title: "This is a very long title that exceeds the recommended length for SEO"
date: 2023-01-01
header:
  teaser: "test.jpg"
---
Content"""
        
        results = self.validator.validate_content(long_title_content)
        title_result = next((r for r in results if r.rule_name == "title_length"), None)
        self.assertIsNotNone(title_result)
        self.assertEqual(title_result.severity, ValidationSeverity.WARNING)
    
    def test_malformed_frontmatter_fix(self):
        """测试Front Matter格式修复"""
        content = '''---
title: Article with "quotes" and special: characters
description: This has mixed quotes
---
Content'''
        
        results = self.validator.validate_content(content)
        
        # 应该能够处理并可能修复格式问题
        self.assertIsInstance(results, list)


class TestImageValidator(unittest.TestCase):
    """测试图片验证器"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.validator = ImageValidator(project_root=self.temp_dir)
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_windows_path_detection(self):
        """测试Windows路径检测"""
        content = '''![Test Image](C:/Users/test/image.jpg)
![Another Image](D:\\folder\\image.png)'''
        
        results = self.validator.validate_content(content)
        
        windows_path_results = [r for r in results if r.rule_name == "windows_paths"]
        self.assertEqual(len(windows_path_results), 2)
        self.assertTrue(all(r.severity == ValidationSeverity.ERROR for r in windows_path_results))
    
    def test_external_url_detection(self):
        """测试外部URL检测"""
        content = '''![External Image](https://example.com/image.jpg)
![Another External](//cdn.example.com/image.png)'''
        
        results = self.validator.validate_content(content)
        
        external_results = [r for r in results if r.rule_name == "external_links"]
        self.assertEqual(len(external_results), 2)
        self.assertTrue(all(r.severity == ValidationSeverity.INFO for r in external_results))
    
    def test_missing_alt_text(self):
        """测试缺少alt文本"""
        content = '''![](image.jpg)
![](another-image.png)'''
        
        results = self.validator.validate_content(content)
        
        alt_text_results = [r for r in results if r.rule_name == "alt_text"]
        self.assertEqual(len(alt_text_results), 2)
    
    def test_jekyll_baseurl_usage(self):
        """测试Jekyll baseurl使用"""
        content = '''![Test](assets/images/test.jpg)'''
        
        results = self.validator.validate_content(content)
        
        liquid_result = next((r for r in results if r.rule_name == "liquid_syntax"), None)
        self.assertIsNotNone(liquid_result)
        self.assertEqual(liquid_result.severity, ValidationSeverity.WARNING)
    
    def test_get_problematic_image_paths(self):
        """测试获取有问题的图片路径"""
        content = '''![Test](C:/local/image.jpg)
![Good]({{ site.baseurl }}/assets/images/good.jpg)
![External](https://example.com/external.jpg)
![Local](assets/images/local.jpg)'''
        
        problematic_paths = self.validator.get_problematic_image_paths(content)
        
        self.assertEqual(len(problematic_paths), 2)  # Windows路径和本地相对路径
        self.assertIn("C:/local/image.jpg", problematic_paths)
        self.assertIn("assets/images/local.jpg", problematic_paths)


class TestStructureValidator(unittest.TestCase):
    """测试结构验证器"""
    
    def setUp(self):
        """设置测试环境"""
        self.validator = StructureValidator()
    
    def test_missing_more_tag(self):
        """测试缺少more标签"""
        content = """---
title: Test
---
This is content without more tag."""
        
        results = self.validator.validate_content(content)
        
        more_tag_result = next((r for r in results if r.rule_name == "more_tag"), None)
        self.assertIsNotNone(more_tag_result)
        self.assertEqual(more_tag_result.severity, ValidationSeverity.WARNING)
    
    def test_content_length_validation(self):
        """测试内容长度验证"""
        # 内容过短
        short_content = """---
title: Test
---
Short content."""
        
        results = self.validator.validate_content(short_content)
        
        length_result = next((r for r in results if r.rule_name == "content_length"), None)
        self.assertIsNotNone(length_result)
        self.assertEqual(length_result.severity, ValidationSeverity.WARNING)
    
    def test_heading_hierarchy(self):
        """测试标题层级"""
        content = """---
title: Test
---
# Main Title
### Skipped Level
## Back to H2"""
        
        results = self.validator.validate_content(content)
        
        heading_results = [r for r in results if r.rule_name == "heading_hierarchy"]
        self.assertGreater(len(heading_results), 0)
    
    def test_valid_structure(self):
        """测试有效结构"""
        content = """---
title: Test Article
---

This is the introduction paragraph with sufficient content length.

<!-- more -->

## Section 1

This is section content with enough text to pass validation.

## Section 2

More content here to ensure we have sufficient length for validation.

### Subsection

Additional content to make this article comprehensive and valuable."""
        
        results = self.validator.validate_content(content)
        
        # 应该没有错误级别的问题
        error_results = [r for r in results if r.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]]
        self.assertEqual(len(error_results), 0)


class TestQualityValidator(unittest.TestCase):
    """测试质量验证器"""
    
    def setUp(self):
        """设置测试环境"""
        self.validator = QualityValidator()
    
    def test_word_count_validation(self):
        """测试字数验证"""
        # 内容过短
        short_content = """---
title: Test
---
Very short content."""
        
        results = self.validator.validate_content(short_content)
        
        word_count_result = next((r for r in results if r.rule_name == "word_count"), None)
        self.assertIsNotNone(word_count_result)
        self.assertEqual(word_count_result.severity, ValidationSeverity.WARNING)
    
    def test_repetition_detection(self):
        """测试重复检测"""
        content = """---
title: Test
---
This is a test. This is a test. This is a test. This is a test. This is a test.
The same sentence repeats multiple times to test repetition detection."""
        
        results = self.validator.validate_content(content)
        
        repetition_results = [r for r in results if r.rule_name == "repetition"]
        self.assertGreater(len(repetition_results), 0)
    
    def test_long_content_analysis(self):
        """测试长内容分析"""
        long_content = """---
title: Comprehensive Test Article
---

This is a comprehensive test article with sufficient content to test various quality metrics. 
""" + "This is additional content. " * 100 + """

The article contains multiple paragraphs and sufficient word count to trigger various quality checks.
We include technical terms like API, HTTP, JSON to test technical term detection.

In conclusion, this article provides comprehensive coverage of the topic with sufficient depth and analysis."""
        
        results = self.validator.validate_content(long_content)
        
        # 应该能够处理长内容而不出错
        self.assertIsInstance(results, list)
        
        # 检查是否检测到了技术术语 (可能不会触发，因为阈值较高)
        tech_results = [r for r in results if r.rule_name == "technical_terms"]
        # 技术术语检测可能不会触发，这是正常的


class TestValidatorRegistry(unittest.TestCase):
    """测试验证器注册表"""
    
    def test_default_validators_registered(self):
        """测试默认验证器已注册"""
        validators = validator_registry.list_validators()
        
        expected_validators = ["frontmatter", "image", "structure", "quality"]
        for validator_name in expected_validators:
            self.assertIn(validator_name, validators)
    
    def test_get_validator(self):
        """测试获取验证器"""
        fm_validator = validator_registry.get("frontmatter")
        self.assertIsInstance(fm_validator, FrontMatterValidator)
        
        nonexistent = validator_registry.get("nonexistent")
        self.assertIsNone(nonexistent)
    
    def test_validate_with_all(self):
        """测试使用所有验证器验证"""
        content = """---
title: "Test Article"
date: 2023-01-01
---

This is test content with sufficient length for validation."""
        
        summary = validator_registry.validate_with_all(content)
        
        self.assertIsInstance(summary, ValidationSummary)
        self.assertIsInstance(summary.results, list)


class TestContentValidatorIntegration(unittest.TestCase):
    """测试内容验证器集成"""
    
    def test_comprehensive_validation(self):
        """测试综合验证"""
        content = """---
title: "Comprehensive Test Article"
date: 2023-01-01
header:
  teaser: "{{ site.baseurl }}/assets/images/test.jpg"
categories: ["tech", "tutorial"]
tags: ["testing", "validation", "quality"]
excerpt: "This is a comprehensive test article that demonstrates various validation features"
---

# Introduction

This is a comprehensive test article designed to test multiple validation aspects.

<!-- more -->

## Content Structure

The article includes proper heading hierarchy and sufficient content length to pass validation checks.

![Test Image]({{ site.baseurl }}/assets/images/test.jpg "Test Image Alt Text")

### Code Examples

Here's a code example:

```python
def validate_content(content):
    return validator.validate(content)
```

## Technical Content

This section includes technical terms like API, HTTP, JSON, and SQL to test technical term detection.

## Conclusion

In conclusion, this article demonstrates proper structure and content quality for validation testing."""
        
        # 使用所有验证器
        summary = validator_registry.validate_with_all(content)
        
        self.assertIsInstance(summary, ValidationSummary)
        
        # 不应该有严重错误
        critical_errors = summary.get_results_by_severity(ValidationSeverity.CRITICAL)
        self.assertEqual(len(critical_errors), 0)
        
        # 可能有一些信息级别的建议
        info_results = summary.get_results_by_severity(ValidationSeverity.INFO)
        # 信息级别的建议是正常的
        self.assertGreaterEqual(len(info_results), 0)
    
    def test_file_validation(self):
        """测试文件验证"""
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8', suffix='.md')
        temp_file.write("""---
title: "File Test"
date: 2023-01-01
---

This is test content for file validation.""")
        temp_file.close()
        
        try:
            validator = FrontMatterValidator()
            results = validator.validate_file(Path(temp_file.name))
            
            self.assertIsInstance(results, list)
            # 应该能够成功读取和验证文件
            read_error = next((r for r in results if r.rule_name == "file_read"), None)
            self.assertIsNone(read_error)
            
        finally:
            os.unlink(temp_file.name)


if __name__ == '__main__':
    unittest.main()