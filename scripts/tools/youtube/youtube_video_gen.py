#!/usr/bin/env python3
"""
YouTube视频生成器启动脚本（简化版）
只生成视频，不上传，避免OAuth认证问题
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入并运行简化版工具
from scripts.tools.youtube.youtube_video_generator import main

if __name__ == "__main__":
    main()