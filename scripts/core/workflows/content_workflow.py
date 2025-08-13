"""
内容处理工作流抽象层
提供统一的内容处理工作流接口和实现
"""
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class WorkflowStepStatus(Enum):
    """工作流步骤状态"""
    PENDING = "pending"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WorkflowStep:
    """工作流步骤"""
    name: str
    description: str
    function: Callable
    required: bool = True
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    result: Any = None
    error: Optional[str] = None
    
@dataclass 
class WorkflowResult:
    """工作流执行结果"""
    success: bool
    steps_completed: int
    steps_failed: int
    steps_skipped: int
    results: Dict[str, Any]
    errors: List[str]
    
class WorkflowEngine(ABC):
    """工作流引擎抽象基类"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.steps: List[WorkflowStep] = []
        
    def add_step(self, name: str, description: str, function: Callable, required: bool = True):
        """添加工作流步骤"""
        step = WorkflowStep(name, description, function, required)
        self.steps.append(step)
        return step
        
    def log(self, message: str, level: str = "info", force: bool = False) -> None:
        """记录日志"""
        if self.logger:
            getattr(self.logger, level)(message)
            if force:
                print(f"[{level.upper()}] {message}")
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> WorkflowResult:
        """执行工作流"""
        pass
        
class ContentProcessingWorkflow(WorkflowEngine):
    """内容处理工作流"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        super().__init__(logger)
        self._setup_default_steps()
        
    def _setup_default_steps(self):
        """设置默认的处理步骤"""
        # 这些步骤将在子类中或通过配置进行具体实现
        self.add_step("validate_input", "📋 验证输入参数", self._validate_input)
        self.add_step("load_content", "📖 加载文章内容", self._load_content)
        self.add_step("parse_frontmatter", "📄 解析Front Matter", self._parse_frontmatter)
        self.add_step("validate_content", "✅ 验证内容完整性", self._validate_content)
        self.add_step("process_images", "🖼️ 处理图片资源", self._process_images, required=False)
        self.add_step("enhance_content", "✨ AI内容增强", self._enhance_content, required=False)
        self.add_step("generate_platforms_content", "🔄 生成平台适配内容", self._generate_platforms_content)
        self.add_step("publish_to_platforms", "🚀 发布到各平台", self._publish_to_platforms)
        self.add_step("update_status", "📊 更新发布状态", self._update_status)
        
    def execute(self, context: Dict[str, Any]) -> WorkflowResult:
        """执行内容处理工作流"""
        self.log("🚀 开始执行内容处理工作流", level="info", force=True)
        
        results = {}
        errors = []
        steps_completed = 0
        steps_failed = 0
        steps_skipped = 0
        
        for step in self.steps:
            try:
                self.log(f"{step.description}...", level="info", force=True)
                step.status = WorkflowStepStatus.RUNNING
                
                # 执行步骤
                step.result = step.function(context, results)
                step.status = WorkflowStepStatus.COMPLETED
                results[step.name] = step.result
                steps_completed += 1
                
                self.log(f"✅ {step.description} - 完成", level="info")
                
            except Exception as e:
                step.error = str(e)
                error_msg = f"❌ {step.description} - 失败: {str(e)}"
                errors.append(error_msg)
                self.log(error_msg, level="error", force=True)
                
                if step.required:
                    step.status = WorkflowStepStatus.FAILED
                    steps_failed += 1
                    # 必需步骤失败，中断工作流
                    self.log("🛑 关键步骤失败，中断工作流", level="error", force=True)
                    break
                else:
                    step.status = WorkflowStepStatus.SKIPPED
                    steps_skipped += 1
                    self.log("⚠️ 可选步骤失败，继续执行", level="warning")
        
        # 工作流成功：没有必需步骤失败，且完成了一些步骤
        success = steps_failed == 0 and steps_completed > 0
        
        workflow_result = WorkflowResult(
            success=success,
            steps_completed=steps_completed,
            steps_failed=steps_failed,
            steps_skipped=steps_skipped,
            results=results,
            errors=errors
        )
        
        if success:
            self.log("🎉 工作流执行成功完成", level="info", force=True)
        else:
            self.log("💥 工作流执行失败", level="error", force=True)
            
        return workflow_result
    
    # 默认步骤实现（可以被子类覆盖）
    def _validate_input(self, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """验证输入参数"""
        required_keys = ['draft_path', 'platforms']
        for key in required_keys:
            if key not in context:
                raise ValueError(f"缺少必需参数: {key}")
        
        draft_path = context['draft_path']
        if not isinstance(draft_path, Path) or not draft_path.exists():
            raise ValueError(f"草稿文件不存在: {draft_path}")
            
        return {"valid": True}
    
    def _load_content(self, context: Dict[str, Any], results: Dict[str, Any]) -> str:
        """加载文章内容"""
        draft_path = context['draft_path']
        with open(draft_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content) < 100:
            raise ValueError("文章内容过短，可能不完整")
            
        return content
    
    def _parse_frontmatter(self, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """解析Front Matter"""
        content = results['load_content']
        
        # 这里需要导入frontmatter并解析
        # 为了避免循环导入，这个方法在实际使用时需要被具体实现覆盖
        return {"frontmatter_parsed": True, "content": content}
    
    def _validate_content(self, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """验证内容完整性"""
        # 基本验证逻辑，可以被具体的验证器覆盖
        return {"content_valid": True}
    
    def _process_images(self, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """处理图片资源"""
        # 图片处理逻辑，将委托给图片处理器
        return {"images_processed": True}
    
    def _enhance_content(self, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """AI内容增强"""
        # AI处理逻辑，将委托给AI处理器
        return {"content_enhanced": True}
    
    def _generate_platforms_content(self, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """生成平台适配内容"""
        platforms = context.get('platforms', [])
        platform_contents = {}
        
        for platform in platforms:
            # 这里将委托给平台处理器
            platform_contents[platform] = results.get('load_content', '')
            
        return {"platform_contents": platform_contents}
    
    def _publish_to_platforms(self, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """发布到各平台"""
        platforms = context.get('platforms', [])
        platform_contents = results.get('generate_platforms_content', {}).get('platform_contents', {})
        
        publish_results = {}
        for platform in platforms:
            # 这里将委托给平台处理器
            publish_results[platform] = True  # 模拟发布成功
            
        return {"publish_results": publish_results}
    
    def _update_status(self, context: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """更新发布状态"""
        publish_results = results.get('publish_to_platforms', {}).get('publish_results', {})
        successful_platforms = [p for p, success in publish_results.items() if success]
        
        return {
            "successful_platforms": successful_platforms,
            "total_platforms": len(context.get('platforms', [])),
            "status_updated": True
        }


class WorkflowRegistry:
    """工作流注册器"""
    
    def __init__(self):
        self._workflows = {}
        
    def register(self, name: str, workflow_class: type):
        """注册工作流"""
        self._workflows[name] = workflow_class
        
    def get(self, name: str) -> Optional[type]:
        """获取工作流类"""
        return self._workflows.get(name)
    
    def list_workflows(self) -> List[str]:
        """列出所有注册的工作流"""
        return list(self._workflows.keys())
    
# 全局工作流注册器实例
workflow_registry = WorkflowRegistry()

# 注册默认工作流
workflow_registry.register("content_processing", ContentProcessingWorkflow)