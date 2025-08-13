"""
集成的内容处理工作流
整合AI处理器、平台处理器、图片处理器等所有模块
"""
import frontmatter
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from .content_workflow import ContentProcessingWorkflow
from ..processors.ai_processor import AIProcessor  
from ..processors.platform_processor import PlatformProcessor
from ..processors.image_processor import ImageProcessor
from ..managers.publish_manager import PublishingStatusManager


class IntegratedContentWorkflow(ContentProcessingWorkflow):
    """集成内容处理工作流"""
    
    def __init__(self, 
                 ai_processor: Optional[AIProcessor] = None,
                 platform_processor: Optional[PlatformProcessor] = None, 
                 image_processor: Optional[ImageProcessor] = None,
                 status_manager: Optional[PublishingStatusManager] = None,
                 logger: Optional[logging.Logger] = None):
        """
        初始化集成工作流
        
        Args:
            ai_processor: AI处理器实例
            platform_processor: 平台处理器实例  
            image_processor: 图片处理器实例
            status_manager: 状态管理器实例
            logger: 日志记录器
        """
        super().__init__(logger)
        self.ai_processor = ai_processor
        self.platform_processor = platform_processor
        self.image_processor = image_processor
        self.status_manager = status_manager
        
    def _parse_frontmatter(self, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """解析Front Matter"""
        content = results['load_content']
        
        try:
            post = frontmatter.loads(content)
            return {
                "post": post,
                "frontmatter": post.metadata,
                "content_body": post.content
            }
        except Exception as e:
            # 尝试修复front matter
            self.log(f"Front matter解析失败，尝试修复: {str(e)}", level="warning")
            fixed_content = self._fix_frontmatter_quotes(content)
            try:
                post = frontmatter.loads(fixed_content)
                return {
                    "post": post,
                    "frontmatter": post.metadata, 
                    "content_body": post.content,
                    "content_fixed": True
                }
            except Exception as e2:
                raise ValueError(f"Front matter解析失败: {str(e2)}")
    
    def _validate_content(self, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """验证内容完整性"""
        post = results['parse_frontmatter']['post']
        
        # 验证必需字段
        required_fields = ['title', 'date']
        missing_fields = []
        
        for field in required_fields:
            if field not in post.metadata or not post.metadata[field]:
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"缺少必需字段: {', '.join(missing_fields)}")
        
        # 验证内容长度
        if len(post.content) < 100:
            raise ValueError("文章内容过短")
            
        return {
            "content_valid": True,
            "required_fields_present": True,
            "content_length": len(post.content)
        }
    
    def _process_images(self, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """处理图片资源"""
        if not self.image_processor:
            self.log("图片处理器未初始化，跳过图片处理", level="warning")
            return {"images_processed": False, "skipped": True}
        
        draft_path = context['draft_path']
        
        try:
            # 检查图片路径
            content = results['load_content']
            problematic_images = self.image_processor.check_image_paths(content)
            
            if problematic_images:
                self.log(f"发现需要处理的图片: {len(problematic_images)}", level="info")
                # 这里可以添加具体的图片处理逻辑
                
            return {
                "images_processed": True,
                "problematic_images_count": len(problematic_images),
                "problematic_images": problematic_images
            }
            
        except Exception as e:
            self.log(f"图片处理失败: {str(e)}", level="error")
            # 图片处理是可选的，不应该中断整个流程
            return {"images_processed": False, "error": str(e)}
    
    def _enhance_content(self, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """AI内容增强"""
        if not self.ai_processor:
            self.log("AI处理器未初始化，跳过内容增强", level="warning") 
            return {"content_enhanced": False, "skipped": True}
        
        content = results['load_content']
        post = results['parse_frontmatter']['post']
        
        try:
            enhanced_results = {}
            
            # 内容润色（可选）
            if context.get('enable_polish', False):
                polished_content = self.ai_processor.polish_content(content)
                if polished_content and polished_content != content:
                    enhanced_results['polished_content'] = polished_content
                    self.log("✨ 内容润色完成", level="info")
            
            # 生成摘要
            if 'excerpt' not in post.metadata or not post.metadata['excerpt']:
                excerpt = self.ai_processor.generate_excerpt(post.content)
                if excerpt:
                    enhanced_results['generated_excerpt'] = excerpt
                    post.metadata['excerpt'] = excerpt
                    self.log(f"📝 生成摘要: {excerpt}", level="info")
            
            # 生成分类和标签
            if context.get('enable_categorization', True):
                available_categories = context.get('available_categories', {})
                if available_categories:
                    categories, tags = self.ai_processor.generate_categories_and_tags(
                        post.content, available_categories
                    )
                    if categories:
                        enhanced_results['suggested_categories'] = categories
                        enhanced_results['suggested_tags'] = tags
                        self.log(f"🏷️ 建议分类: {categories}, 标签: {tags}", level="info")
            
            return {
                "content_enhanced": True,
                "enhanced_results": enhanced_results,
                "updated_post": post
            }
            
        except Exception as e:
            self.log(f"AI内容增强失败: {str(e)}", level="error")
            # AI增强是可选的，不应该中断整个流程
            return {"content_enhanced": False, "error": str(e)}
    
    def _generate_platforms_content(self, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """生成平台适配内容"""
        if not self.platform_processor:
            self.log("平台处理器未初始化，使用原内容", level="warning")
            platforms = context.get('platforms', [])
            content = results['load_content']
            return {
                "platform_contents": {platform: content for platform in platforms}
            }
        
        platforms = context.get('platforms', [])
        base_content = results['load_content']
        
        # 使用增强后的内容（如果有）
        if 'enhance_content' in results and results['enhance_content'].get('enhanced_results', {}).get('polished_content'):
            base_content = results['enhance_content']['enhanced_results']['polished_content']
        
        platform_contents = {}
        
        for platform in platforms:
            try:
                adapted_content = self.platform_processor.generate_platform_content(base_content, platform)
                platform_contents[platform] = adapted_content
                self.log(f"🔄 为平台 {platform} 生成适配内容", level="info")
                
            except Exception as e:
                self.log(f"为平台 {platform} 生成内容失败: {str(e)}", level="error")
                platform_contents[platform] = base_content  # 回退到原内容
        
        return {"platform_contents": platform_contents}
    
    def _publish_to_platforms(self, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """发布到各平台"""
        if not self.platform_processor:
            self.log("平台处理器未初始化，无法发布", level="warning")
            return {"publish_results": {}, "successful_platforms": []}
        
        platforms = context.get('platforms', [])
        platform_contents = results.get('generate_platforms_content', {}).get('platform_contents', {})
        
        publish_results = {}
        successful_platforms = []
        
        for platform in platforms:
            content = platform_contents.get(platform, results['load_content'])
            
            try:
                success = self.platform_processor.publish_to_platform(content, platform)
                publish_results[platform] = success
                
                if success:
                    successful_platforms.append(platform)
                    self.log(f"✅ 成功发布到 {platform}", level="info")
                else:
                    self.log(f"❌ 发布到 {platform} 失败", level="error")
                    
            except Exception as e:
                publish_results[platform] = False
                self.log(f"❌ 发布到 {platform} 异常: {str(e)}", level="error")
        
        return {
            "publish_results": publish_results,
            "successful_platforms": successful_platforms,
            "total_platforms": len(platforms)
        }
    
    def _update_status(self, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """更新发布状态"""
        if not self.status_manager:
            self.log("状态管理器未初始化，跳过状态更新", level="warning")
            return {"status_updated": False}
        
        draft_path = context['draft_path']
        publish_results = results.get('publish_to_platforms', {})
        successful_platforms = publish_results.get('successful_platforms', [])
        
        try:
            # 更新发布状态
            self.status_manager.update_published_platforms(
                draft_path.stem, successful_platforms
            )
            
            self.log(f"📊 更新发布状态: {len(successful_platforms)} 个平台", level="info")
            
            return {
                "status_updated": True,
                "successful_platforms": successful_platforms,
                "total_platforms": publish_results.get('total_platforms', 0)
            }
            
        except Exception as e:
            self.log(f"更新状态失败: {str(e)}", level="error")
            return {"status_updated": False, "error": str(e)}
    
    def _fix_frontmatter_quotes(self, content: str) -> str:
        """修复front matter中的引号问题"""
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


# 注册集成工作流到全局注册器
from .content_workflow import workflow_registry
workflow_registry.register("integrated_processing", IntegratedContentWorkflow)