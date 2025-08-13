"""
内容验证器抽象基类和核心类
提供统一的内容验证接口和结果管理
"""
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class ValidationSeverity(Enum):
    """验证问题严重级别"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """验证结果"""
    rule_name: str
    severity: ValidationSeverity
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None
    
    def __str__(self) -> str:
        icon_map = {
            ValidationSeverity.INFO: "ℹ️",
            ValidationSeverity.WARNING: "⚠️",
            ValidationSeverity.ERROR: "❌",
            ValidationSeverity.CRITICAL: "💥"
        }
        icon = icon_map.get(self.severity, "❓")
        location_str = f" ({self.location})" if self.location else ""
        return f"{icon} {self.message}{location_str}"


@dataclass
class ValidationRule:
    """验证规则"""
    name: str
    description: str
    severity: ValidationSeverity
    enabled: bool = True
    
    
class ContentValidator(ABC):
    """内容验证器抽象基类"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.rules: List[ValidationRule] = []
        self._setup_rules()
    
    @abstractmethod
    def _setup_rules(self) -> None:
        """设置验证规则"""
        pass
    
    @abstractmethod
    def validate_content(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[ValidationResult]:
        """验证内容"""
        pass
    
    def validate_file(self, file_path: Path) -> List[ValidationResult]:
        """验证文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.validate_content(content)
        except Exception as e:
            return [ValidationResult(
                rule_name="file_read",
                severity=ValidationSeverity.CRITICAL,
                message=f"文件读取失败: {str(e)}",
                location=str(file_path)
            )]
    
    def get_rule(self, rule_name: str) -> Optional[ValidationRule]:
        """获取指定规则"""
        return next((rule for rule in self.rules if rule.name == rule_name), None)
    
    def enable_rule(self, rule_name: str) -> bool:
        """启用规则"""
        rule = self.get_rule(rule_name)
        if rule:
            rule.enabled = True
            return True
        return False
    
    def disable_rule(self, rule_name: str) -> bool:
        """禁用规则"""
        rule = self.get_rule(rule_name)
        if rule:
            rule.enabled = False
            return True
        return False
    
    def log(self, message: str, level: str = "info", force: bool = False) -> None:
        """记录日志"""
        if self.logger:
            getattr(self.logger, level)(message)
            if force:
                print(f"[{level.upper()}] {message}")


class ValidationSummary:
    """验证结果汇总"""
    
    def __init__(self, results: List[ValidationResult]):
        self.results = results
        self.counts = self._count_by_severity()
        
    def _count_by_severity(self) -> Dict[ValidationSeverity, int]:
        """按严重程度统计"""
        counts = {severity: 0 for severity in ValidationSeverity}
        for result in self.results:
            counts[result.severity] += 1
        return counts
    
    @property
    def has_errors(self) -> bool:
        """是否有错误"""
        return self.counts[ValidationSeverity.ERROR] > 0 or self.counts[ValidationSeverity.CRITICAL] > 0
    
    @property
    def has_warnings(self) -> bool:
        """是否有警告"""
        return self.counts[ValidationSeverity.WARNING] > 0
    
    @property
    def is_valid(self) -> bool:
        """内容是否有效（无错误和严重问题）"""
        return not self.has_errors
    
    def get_results_by_severity(self, severity: ValidationSeverity) -> List[ValidationResult]:
        """获取指定严重级别的结果"""
        return [r for r in self.results if r.severity == severity]
    
    def format_summary(self) -> str:
        """格式化汇总信息"""
        if not self.results:
            return "✅ 验证通过，未发现任何问题"
        
        lines = ["📋 验证结果汇总:"]
        
        for severity in ValidationSeverity:
            count = self.counts[severity]
            if count > 0:
                icon_map = {
                    ValidationSeverity.INFO: "ℹ️",
                    ValidationSeverity.WARNING: "⚠️", 
                    ValidationSeverity.ERROR: "❌",
                    ValidationSeverity.CRITICAL: "💥"
                }
                icon = icon_map.get(severity, "❓")
                lines.append(f"  {icon} {severity.value.upper()}: {count}个问题")
        
        return "\n".join(lines)
    
    def format_detailed_report(self) -> str:
        """格式化详细报告"""
        if not self.results:
            return "✅ 验证通过，未发现任何问题"
        
        lines = [self.format_summary(), ""]
        
        # 按严重级别分组显示
        for severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR, 
                        ValidationSeverity.WARNING, ValidationSeverity.INFO]:
            results = self.get_results_by_severity(severity)
            if results:
                lines.append(f"📋 {severity.value.upper()} 问题:")
                for result in results:
                    lines.append(f"  {result}")
                    if result.suggestion:
                        lines.append(f"    💡 建议: {result.suggestion}")
                lines.append("")
        
        return "\n".join(lines)


class ValidatorRegistry:
    """验证器注册表"""
    
    def __init__(self):
        self._validators: Dict[str, ContentValidator] = {}
    
    def register(self, name: str, validator: ContentValidator) -> None:
        """注册验证器"""
        self._validators[name] = validator
    
    def get(self, name: str) -> Optional[ContentValidator]:
        """获取验证器"""
        return self._validators.get(name)
    
    def list_validators(self) -> List[str]:
        """列出所有验证器"""
        return list(self._validators.keys())
    
    def validate_with_all(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> ValidationSummary:
        """使用所有验证器验证内容"""
        all_results = []
        for validator in self._validators.values():
            results = validator.validate_content(content, metadata)
            all_results.extend(results)
        
        return ValidationSummary(all_results)


# 全局验证器注册表
validator_registry = ValidatorRegistry()

# 延迟导入和注册具体的验证器，避免循环导入
def _register_default_validators():
    """注册默认验证器"""
    try:
        from .frontmatter_validator import FrontMatterValidator
        from .image_validator import ImageValidator
        from .structure_validator import StructureValidator
        from .quality_validator import QualityValidator
        
        validator_registry.register("frontmatter", FrontMatterValidator())
        validator_registry.register("image", ImageValidator()) 
        validator_registry.register("structure", StructureValidator())
        validator_registry.register("quality", QualityValidator())
        
    except ImportError as e:
        # 在测试或特殊环境中可能缺少某些依赖
        pass

# 自动注册默认验证器
_register_default_validators()


class CompositeValidator(ContentValidator):
    """组合验证器 - 集成多个验证器"""
    
    def __init__(self, validators: List[ContentValidator], logger: Optional[logging.Logger] = None):
        self.validators = validators
        super().__init__(logger)
        
    def _setup_rules(self) -> None:
        """集成所有验证器的规则"""
        for validator in self.validators:
            self.rules.extend(validator.rules)
    
    def validate_content(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[ValidationResult]:
        """使用所有验证器验证内容"""
        all_results = []
        for validator in self.validators:
            try:
                results = validator.validate_content(content, metadata)
                all_results.extend(results)
            except Exception as e:
                self.log(f"验证器 {type(validator).__name__} 执行失败: {str(e)}", level="error")
                all_results.append(ValidationResult(
                    rule_name=f"{type(validator).__name__.lower()}_error",
                    severity=ValidationSeverity.ERROR,
                    message=f"验证器执行失败: {str(e)}"
                ))
        
        return all_results
    
    def validate_file(self, file_path: Path) -> List[ValidationResult]:
        """使用所有验证器验证文件"""
        all_results = []
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return [ValidationResult(
                rule_name="file_read",
                severity=ValidationSeverity.CRITICAL,
                message=f"文件读取失败: {str(e)}",
                location=str(file_path)
            )]
        
        # 执行所有验证器
        for validator in self.validators:
            try:
                results = validator.validate_content(content)
                # 为每个结果添加文件位置信息
                for result in results:
                    if not result.location:
                        result.location = str(file_path)
                all_results.extend(results)
            except Exception as e:
                self.log(f"验证器 {type(validator).__name__} 执行失败: {str(e)}", level="error")
                all_results.append(ValidationResult(
                    rule_name=f"{type(validator).__name__.lower()}_error",
                    severity=ValidationSeverity.ERROR,
                    message=f"验证器执行失败: {str(e)}",
                    location=str(file_path)
                ))
        
        return all_results