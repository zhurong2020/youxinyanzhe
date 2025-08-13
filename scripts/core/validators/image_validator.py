"""
图片验证器
检查Markdown内容中的图片路径和格式问题
"""
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

from .content_validator import (
    ContentValidator,
    ValidationResult,
    ValidationSeverity,
    ValidationRule
)


class ImageValidator(ContentValidator):
    """图片验证器"""
    
    def __init__(self, project_root: Optional[Path] = None, logger=None):
        self.project_root = project_root or Path.cwd()
        super().__init__(logger)
    
    def _setup_rules(self) -> None:
        """设置验证规则"""
        self.rules = [
            ValidationRule(
                name="image_paths",
                description="检查图片路径格式",
                severity=ValidationSeverity.WARNING
            ),
            ValidationRule(
                name="image_exists",
                description="检查图片文件是否存在",
                severity=ValidationSeverity.ERROR
            ),
            ValidationRule(
                name="image_size",
                description="检查图片文件大小",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="alt_text",
                description="检查图片alt文本",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="liquid_syntax",
                description="检查Jekyll Liquid语法",
                severity=ValidationSeverity.WARNING
            ),
            ValidationRule(
                name="external_links",
                description="检查外部图片链接",
                severity=ValidationSeverity.INFO
            ),
            ValidationRule(
                name="windows_paths",
                description="检查Windows路径格式",
                severity=ValidationSeverity.ERROR
            )
        ]
    
    def validate_content(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> List[ValidationResult]:
        """验证图片相关问题"""
        results = []
        
        # 查找所有图片引用
        image_patterns = [
            r'!\[([^\]]*)\]\(([^)]+)\)',  # Markdown语法: ![alt](url)
            r'<img[^>]+src=["\'](([^"\']+))["\'][^>]*>',  # HTML img标签
            r'teaser:\s*["\']?([^"\'\n]+)["\']?'  # Front Matter中的teaser
        ]
        
        found_images = []
        for pattern in image_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if match.lastindex is not None and match.lastindex >= 2:
                    alt_text = match.group(1) if match.lastindex >= 1 else ""
                    image_url = match.group(2)
                elif len(match.groups()) == 1:
                    alt_text = ""
                    image_url = match.group(1)
                else:
                    continue
                    
                found_images.append({
                    'alt': alt_text,
                    'url': image_url,
                    'full_match': match.group(0),
                    'start': match.start(),
                    'end': match.end()
                })
        
        # 验证每个图片
        for img in found_images:
            img_results = self._validate_single_image(img)
            results.extend(img_results)
        
        # 检查是否使用了正确的Jekyll baseurl
        if not self._uses_jekyll_baseurl(content):
            has_relative_paths = any(
                not img['url'].startswith(('http', 'https', '//')) 
                for img in found_images
            )
            if has_relative_paths:
                results.append(ValidationResult(
                    rule_name="liquid_syntax",
                    severity=ValidationSeverity.WARNING,
                    message="建议使用Jekyll baseurl语法",
                    suggestion="使用 {{ site.baseurl }}/assets/images/... 格式确保部署兼容性"
                ))
        
        return results
    
    def _validate_single_image(self, img_info: Dict[str, str]) -> List[ValidationResult]:
        """验证单个图片"""
        results = []
        url = img_info['url']
        alt_text = img_info['alt']
        
        # 检查Windows路径
        if self._is_windows_path(url):
            results.append(ValidationResult(
                rule_name="windows_paths",
                severity=ValidationSeverity.ERROR,
                message=f"使用Windows绝对路径: {url[:50]}{'...' if len(url) > 50 else ''}",
                suggestion="请使用相对路径或{{ site.baseurl }}/assets/images/格式"
            ))
        
        # 检查外部链接
        elif self._is_external_url(url):
            results.append(ValidationResult(
                rule_name="external_links",
                severity=ValidationSeverity.INFO,
                message=f"使用外部图片链接: {self._truncate_url(url)}",
                suggestion="考虑将图片下载到本地assets目录以提高加载速度"
            ))
        
        # 检查本地文件是否存在
        elif not self._is_external_url(url) and not url.startswith('{{'):
            local_path = self._resolve_local_path(url)
            if local_path and not local_path.exists():
                results.append(ValidationResult(
                    rule_name="image_exists",
                    severity=ValidationSeverity.ERROR,
                    message=f"图片文件不存在: {url}",
                    suggestion="检查文件路径是否正确，或确保图片文件已上传"
                ))
            elif local_path and local_path.exists():
                # 检查文件大小
                file_size = local_path.stat().st_size
                if file_size > 2 * 1024 * 1024:  # 2MB
                    results.append(ValidationResult(
                        rule_name="image_size",
                        severity=ValidationSeverity.INFO,
                        message=f"图片文件较大: {self._format_size(file_size)} ({local_path.name})",
                        suggestion="考虑压缩图片以提高页面加载速度"
                    ))
        
        # 检查alt文本
        if not alt_text or alt_text.strip() == "":
            results.append(ValidationResult(
                rule_name="alt_text",
                severity=ValidationSeverity.INFO,
                message=f"图片缺少alt文本: {self._truncate_url(url)}",
                suggestion="添加描述性的alt文本有助于无障碍访问和SEO"
            ))
        elif len(alt_text.strip()) < 3:
            results.append(ValidationResult(
                rule_name="alt_text",
                severity=ValidationSeverity.INFO,
                message=f"alt文本过短: '{alt_text}'",
                suggestion="alt文本应该简洁地描述图片内容"
            ))
        
        return results
    
    def _is_windows_path(self, path: str) -> bool:
        """检查是否是Windows路径"""
        return bool(re.match(r'^[a-zA-Z]:[/\\]', path))
    
    def _is_external_url(self, url: str) -> bool:
        """检查是否是外部URL"""
        return url.startswith(('http://', 'https://', '//'))
    
    def _uses_jekyll_baseurl(self, content: str) -> bool:
        """检查是否使用了Jekyll baseurl语法"""
        return '{{ site.baseurl }}' in content
    
    def _resolve_local_path(self, url: str) -> Optional[Path]:
        """解析本地路径"""
        try:
            # 移除Jekyll语法
            clean_url = url.replace('{{ site.baseurl }}', '').lstrip('/')
            
            # 尝试相对于项目根目录的路径
            potential_paths = [
                self.project_root / clean_url,
                self.project_root / 'assets' / clean_url,
                self.project_root / '_site' / clean_url,
            ]
            
            for path in potential_paths:
                if path.exists():
                    return path
                    
            return self.project_root / clean_url
        except Exception:
            return None
    
    def _truncate_url(self, url: str, max_length: int = 50) -> str:
        """截断URL用于显示"""
        if len(url) <= max_length:
            return url
        return f"{url[:max_length-3]}..."
    
    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        size: float = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"
    
    def get_problematic_image_paths(self, content: str) -> List[str]:
        """获取有问题的图片路径列表（与原有方法兼容）"""
        _ = self.validate_content(content)
        problematic_paths = []
        
        # 查找所有图片引用
        image_patterns = [
            r'!\[([^\]]*)\]\(([^)]+)\)',  # Markdown语法
            r'<img[^>]+src=["\'](([^"\']+))["\'][^>]*>',  # HTML img标签
        ]
        
        for pattern in image_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    image_url = match.group(2)
                elif len(match.groups()) == 1:
                    image_url = match.group(1)
                else:
                    continue
                
                # 检查是否是有问题的路径
                if (self._is_windows_path(image_url) or 
                    (not self._is_external_url(image_url) and 
                     not image_url.startswith('{{ site.baseurl }}'))):
                    problematic_paths.append(image_url)
        
        return problematic_paths
    
    def set_project_root(self, project_root: Path) -> None:
        """设置项目根目录"""
        self.project_root = project_root