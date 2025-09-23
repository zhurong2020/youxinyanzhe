#!/usr/bin/env python3
"""
简单的YouTube视频上传工具
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def upload_video_to_youtube(video_path: str, title: str = None, description: str = None):
    """上传视频到YouTube"""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload

        token_file = project_root / "config" / "youtube_oauth_token.json"

        if not token_file.exists():
            print(f"❌ OAuth token文件不存在: {token_file}")
            return False

        # 加载认证
        creds = Credentials.from_authorized_user_file(str(token_file))

        # 刷新token如果需要
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

        # 创建YouTube服务
        youtube = build('youtube', 'v3', credentials=creds)

        # 准备视频元数据
        video_file = Path(video_path)
        if not title:
            title = video_file.stem.replace('-', ' ').replace('_', ' ').title()

        if not description:
            description = f"Video uploaded on {datetime.now().strftime('%Y-%m-%d')}"

        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': ['TQQQ', 'Investment', '投资', '定投', 'DCA'],
                'categoryId': '22'  # People & Blogs
            },
            'status': {
                'privacyStatus': 'unlisted',  # 先设为不公开
                'selfDeclaredMadeForKids': False
            }
        }

        # 创建媒体上传对象
        media = MediaFileUpload(
            video_path,
            mimetype='video/mp4',
            resumable=True
        )

        print(f"📤 正在上传视频: {video_file.name}")
        print(f"📝 标题: {title}")
        print(f"📏 文件大小: {video_file.stat().st_size / 1024 / 1024:.2f} MB")

        # 执行上传
        request = youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"⏳ 上传进度: {int(status.progress() * 100)}%")

        print(f"✅ 视频上传成功!")
        print(f"🔗 视频ID: {response['id']}")
        print(f"🌐 视频链接: https://youtu.be/{response['id']}")

        return True

    except Exception as e:
        print(f"❌ 上传失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    # 视频文件路径
    video_path = "/home/wuxia/projects/youxinyanzhe/.tmp/youtube_videos/2025-09-22-tqqq-dca-backtest-analysis_wav.mp4"

    # 视频信息
    title = "2025年TQQQ定投回测分析：从-60%回撤到盈利的逆袭之路"
    description = """当今年4月TQQQ暴跌60%时，很多投资者选择了割肉离场。然而，坚持定投的投资者在4个月后就已收获了20%+的回报。

本视频通过真实回测数据，揭示了智能定投策略如何将市场恐慌转化为财富机遇。

📊 关键数据：
- 测试周期：2025年1月1日至9月19日
- 最大回撤：-60%
- 最终收益：33-51%

🏷️ 标签：#TQQQ #定投 #量化投资 #美股投资 #DCA

⚠️ 风险提示：本视频不构成投资建议，仅供教育参考。投资有风险，入市需谨慎。
"""

    # 执行上传
    upload_video_to_youtube(video_path, title, description)

if __name__ == "__main__":
    main()