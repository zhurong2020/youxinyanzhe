#!/usr/bin/env python3
"""
YouTube音频上传工具启动脚本
简化版入口，方便直接运行
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入并运行主工具
from scripts.tools.youtube_upload_tester import main

if __name__ == "__main__":
    main()