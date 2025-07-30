# 日志记录优化方案

## 优化目标

在新的菜单系统更新后，确保能够通过统一的日志文件追踪所有功能脚本的使用情况和问题，保持日志尽量简洁但包含关键信息。

## 现状分析

### 主要问题
1. **分散的日志记录**：大部分工具脚本只使用print()，无法统一追踪
2. **缺乏执行状态记录**：通过run.py调用的脚本执行情况不明确
3. **错误信息不完整**：subprocess执行失败时缺乏详细的错误上下文

### 已有的日志基础
- ✅ `ContentPipeline`有完善的日志系统 (`.build/logs/pipeline.log`)
- ✅ 支持智能日志级别过滤和会话跟踪
- ✅ 已记录用户菜单操作选择

## 优化方案

### 1. 统一脚本执行日志记录

**新增辅助函数**: `execute_script_with_logging()`

**功能特点**:
- 统一记录脚本执行命令和参数
- 自动捕获执行结果和错误信息
- 智能提取关键输出信息（只记录包含✅❌⚠️等关键标识的行）
- 限制错误信息长度避免日志膨胀
- 支持超时控制（5分钟）

**日志格式示例**:
```
2025-07-25 14:30:15 - INFO - 开始执行: 创建内容变现包 - python scripts/utils/reward_system_manager.py create-package article.md
2025-07-25 14:30:22 - INFO - 执行成功: 创建内容变现包
2025-07-25 14:30:22 - INFO - 关键输出: ✅ GitHub Release创建成功; 📦 内容包已准备完毕
```

### 2. 独立脚本日志增强

为关键脚本添加基本日志记录支持：

**已优化的脚本**:
- ✅ `scripts/tools/wechat_api_debug.py` - 微信API调试
- ✅ `scripts/tools/check_github_token.py` - GitHub Token检查

**日志标识符**:
- `[微信API调试]` - 微信相关调试信息
- `[GitHub Token检查]` - Token状态检查信息

### 3. 菜单操作追踪

**已实现的追踪**:
- 用户会话开始和结束
- 主菜单选择记录
- 子菜单操作记录
- 脚本执行状态追踪

**日志示例**:
```
2025-07-25 10:01:40 - INFO - ===== 用户会话开始 [253] =====
2025-07-25 10:01:40 - INFO - 用户选择操作: 4 (内容变现管理)
2025-07-25 10:01:53 - INFO - 内容变现管理 - 用户选择: 2
2025-07-25 10:02:03 - INFO - 开始执行: 查看奖励发送状态 - python scripts/utils/reward_system_manager.py status
```

## 日志记录原则

### 简洁性原则
- **只记录关键信息**：执行状态、错误、重要结果
- **避免重复记录**：相同信息不重复写入
- **限制长度**：错误信息截断到200字符
- **智能过滤**：只记录包含关键标识符的输出行

### 实用性原则
- **便于问题定位**：记录完整的执行命令
- **状态清晰**：明确标识成功/失败/异常
- **时间追踪**：所有操作都有时间戳
- **会话关联**：通过会话ID关联相关操作

### 可维护性原则
- **统一格式**：所有日志使用相同的格式标准
- **模块标识**：不同脚本使用不同的标识符
- **级别控制**：支持不同的日志级别控制

## 具体实现

### run.py中的日志记录

```python
def execute_script_with_logging(pipeline, script_path: Path, args: list, description: str):
    """执行脚本并记录日志的辅助函数"""
    cmd = [sys.executable, str(script_path)] + args
    pipeline.log(f"开始执行: {description} - {' '.join(cmd)}", level="info", force=True)
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    
    if result.returncode == 0:
        pipeline.log(f"执行成功: {description}", level="info", force=True)
        # 只记录关键输出行
        key_lines = [line for line in result.stdout.split('\n') 
                    if any(keyword in line for keyword in ['✅', '❌', '⚠️', 'ERROR', 'SUCCESS'])]
        if key_lines:
            pipeline.log(f"关键输出: {'; '.join(key_lines[:3])}", level="info", force=True)
    else:
        pipeline.log(f"执行失败: {description} (返回码: {result.returncode})", level="error", force=True)
```

### 独立脚本中的日志配置

```python
def setup_logging():
    """设置日志配置"""
    log_dir = Path(".build/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - [脚本标识] %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "pipeline.log", encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)
```

## 使用建议

### 日常监控
1. **查看实时日志**: `tail -f .build/logs/pipeline.log`
2. **过滤特定操作**: `grep "内容变现管理" .build/logs/pipeline.log`
3. **查看错误信息**: `grep "ERROR\|执行失败" .build/logs/pipeline.log`

### 问题排查
1. **定位用户操作**: 通过会话ID和时间戳找到相关操作
2. **检查脚本执行**: 查找"开始执行"和"执行成功/失败"记录
3. **分析错误原因**: 查看错误详情和返回码

### 性能分析
1. **执行频率统计**: 统计各功能模块的使用频率
2. **错误率分析**: 计算各脚本的成功/失败比例
3. **响应时间监控**: 通过时间戳分析操作响应时间

## 后续优化方向

1. **日志轮转**: 自动清理旧日志文件
2. **性能指标**: 记录脚本执行耗时
3. **错误分类**: 对常见错误进行分类和建议
4. **用户行为分析**: 统计用户使用习惯和偏好

---

**更新时间**: 2025-07-25  
**版本**: v1.0 - 基础日志优化版本