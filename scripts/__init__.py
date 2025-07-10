"""
Content Pipeline Scripts
处理博客内容的自动化工具集
"""

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
import yaml

def setup_logger(name: str, config_path: str = "config/pipeline_config.yml") -> logging.Logger:
    """
    配置并返回一个命名的logger
    
    Args:
        name: logger名称
        config_path: 配置文件路径
    
    Returns:
        配置好的logger实例
    """
    # 加载配置
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 获取日志配置
    log_config = config.get("logging", {})
    log_level = getattr(logging, log_config.get("level", "INFO"))
    log_format = log_config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # 确保日志目录存在
    log_path = Path(config["paths"]["logs"])
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 清除现有的处理器
    logger.handlers.clear()
    
    # 创建文件处理器
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=log_config.get("max_size", 10*1024*1024),
        backupCount=log_config.get("backup_count", 5),
        encoding='utf-8',
        mode=log_config.get("file_mode", "a")
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(log_level)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    console_handler.setLevel(log_level)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 避免循环导入
__all__ = ['setup_logger']

# 版本信息
__version__ = "1.0.0" 