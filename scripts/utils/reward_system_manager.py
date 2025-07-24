"""
微信内容变现系统管理器
整合GitHub Release、邮件发送、内容打包等功能
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse

# 导入项目模块
sys.path.append(str(Path(__file__).parent))

from github_release_manager import create_github_manager
from email_sender import create_email_sender
from package_creator import create_package_creator


class RewardSystemManager:
    """微信内容变现系统管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 初始化各个组件
        try:
            self.github_manager = create_github_manager()
            self.email_sender = create_email_sender()
            self.package_creator = create_package_creator()
        except Exception as e:
            self.logger.error(f"初始化组件失败: {e}")
            raise
        
        # 数据存储
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "_data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.pending_requests_file = self.data_dir / "pending_reward_requests.json"
        self.processed_requests_file = self.data_dir / "processed_reward_requests.json"
    
    def create_article_package(self, article_path: str, upload_to_github: bool = True) -> Tuple[bool, Dict]:
        """
        为文章创建完整的资料包并上传到GitHub Release
        
        Args:
            article_path: 文章文件路径
            upload_to_github: 是否上传到GitHub Release
            
        Returns:
            (success, result_info)
        """
        try:
            self.logger.info(f"开始为文章创建资料包: {article_path}")
            
            # 1. 创建内容包
            package_success, package_result = self.package_creator.create_package(article_path)
            if not package_success:
                return False, {"error": f"内容包创建失败: {package_result.get('error')}"}
            
            result = {
                "article_path": article_path,
                "package_path": package_result["package_path"],
                "title": package_result["title"],
                "date": package_result["date"],
                "package_info": package_result
            }
            
            # 2. 上传到GitHub Release（可选）
            if upload_to_github:
                self.logger.info("开始上传到GitHub Release...")
                release_success, release_result = self.github_manager.create_release(
                    package_result["title"],
                    package_result["package_path"],
                    package_result["date"]
                )
                
                if release_success:
                    result["github_release"] = {
                        "success": True,
                        "download_url": release_result["asset_url"],
                        "release_url": release_result["html_url"],
                        "tag_name": release_result["tag_name"]
                    }
                    self.logger.info(f"✅ GitHub Release创建成功: {release_result['html_url']}")
                else:
                    result["github_release"] = {
                        "success": False,
                        "error": release_result.get("error", "未知错误")
                    }
                    self.logger.warning(f"GitHub Release创建失败: {release_result.get('error')}")
            
            return True, result
            
        except Exception as e:
            error_msg = f"创建文章资料包时发生错误: {e}"
            self.logger.error(error_msg)
            return False, {"error": error_msg}
    
    def send_reward_to_user(self, user_email: str, article_title: str, 
                           user_name: str = None) -> Tuple[bool, str]:
        """
        向用户发送奖励内容包
        
        Args:
            user_email: 用户邮箱
            article_title: 文章标题
            user_name: 用户名（可选）
            
        Returns:
            (success, message)
        """
        try:
            # 1. 获取GitHub Release下载链接
            release_info = self.github_manager.get_release_by_article(article_title)
            if not release_info:
                return False, f"未找到文章《{article_title}》的资料包"
            
            download_url = release_info["asset_url"]
            
            # 2. 发送邮件
            email_success, email_message = self.email_sender.send_reward_package(
                user_email, article_title, download_url, user_name
            )
            
            if email_success:
                # 3. 记录处理结果
                self._record_processed_request(user_email, article_title, download_url, True)
                return True, f"资料包已成功发送到 {user_email}"
            else:
                self._record_processed_request(user_email, article_title, download_url, False, email_message)
                return False, f"邮件发送失败: {email_message}"
                
        except Exception as e:
            error_msg = f"发送奖励时发生错误: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def add_pending_request(self, user_email: str, article_title: str, 
                           wechat_user_id: str = None, user_name: str = None) -> bool:
        """
        添加待处理的奖励请求
        
        Args:
            user_email: 用户邮箱
            article_title: 文章标题
            wechat_user_id: 微信用户ID（可选）
            user_name: 用户名（可选）
            
        Returns:
            是否添加成功
        """
        try:
            # 加载现有请求
            pending_requests = self._load_pending_requests()
            
            # 创建新请求
            request = {
                "id": f"{len(pending_requests) + 1:04d}",
                "user_email": user_email,
                "article_title": article_title,
                "wechat_user_id": wechat_user_id,
                "user_name": user_name,
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            }
            
            pending_requests.append(request)
            
            # 保存
            self._save_pending_requests(pending_requests)
            
            self.logger.info(f"添加待处理请求: {user_email} - {article_title}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加待处理请求失败: {e}")
            return False
    
    def process_pending_requests(self, batch_size: int = 10) -> Dict:
        """
        批量处理待处理的奖励请求
        
        Args:
            batch_size: 批处理大小
            
        Returns:
            处理结果统计
        """
        try:
            pending_requests = self._load_pending_requests()
            pending_requests = [r for r in pending_requests if r["status"] == "pending"]
            
            if not pending_requests:
                return {"processed": 0, "failed": 0, "message": "没有待处理的请求"}
            
            # 限制批处理大小
            requests_to_process = pending_requests[:batch_size]
            
            processed_count = 0
            failed_count = 0
            results = []
            
            for request in requests_to_process:
                success, message = self.send_reward_to_user(
                    request["user_email"],
                    request["article_title"],
                    request.get("user_name")
                )
                
                # 更新请求状态
                request["status"] = "processed" if success else "failed"
                request["processed_at"] = datetime.now().isoformat()
                request["result_message"] = message
                
                if success:
                    processed_count += 1
                else:
                    failed_count += 1
                
                results.append({
                    "request_id": request["id"],
                    "email": request["user_email"],
                    "article": request["article_title"],
                    "success": success,
                    "message": message
                })
            
            # 保存更新后的请求列表
            self._save_pending_requests(pending_requests)
            
            result = {
                "processed": processed_count,
                "failed": failed_count,
                "total": len(requests_to_process),
                "remaining": len([r for r in pending_requests if r["status"] == "pending"]),
                "details": results
            }
            
            self.logger.info(f"批量处理完成: 成功 {processed_count}, 失败 {failed_count}")
            return result
            
        except Exception as e:
            error_msg = f"批量处理失败: {e}"
            self.logger.error(error_msg)
            return {"processed": 0, "failed": 0, "error": error_msg}
    
    def get_system_stats(self) -> Dict:
        """获取系统统计信息"""
        try:
            # GitHub统计
            github_stats = self.github_manager.get_stats()
            
            # GitHub Token状态
            token_status = self.github_manager.get_token_expiry_status()
            
            # 邮件统计
            email_stats = self.email_sender.get_stats()
            
            # 请求统计
            pending_requests = self._load_pending_requests()
            processed_requests = self._load_processed_requests()
            
            pending_count = len([r for r in pending_requests if r["status"] == "pending"])
            
            stats = {
                "github_releases": {
                    "total_releases": github_stats.get("total_releases", 0),
                    "total_downloads": github_stats.get("total_downloads", 0)
                },
                "github_token": {
                    "days_until_expiry": token_status.get("days_until_expiry"),
                    "needs_renewal": token_status.get("needs_renewal", False),
                    "last_checked": token_status.get("checked_at")
                },
                "email_delivery": {
                    "total_sent": email_stats.get("total_sent", 0),
                    "total_failed": email_stats.get("total_failed", 0),
                    "success_rate": email_stats.get("success_rate", 0)
                },
                "reward_requests": {
                    "pending": pending_count,
                    "processed": len(processed_requests),
                    "total": len(pending_requests) + len(processed_requests)
                },
                "last_updated": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")
            return {}
    
    def _load_pending_requests(self) -> List[Dict]:
        """加载待处理请求"""
        if self.pending_requests_file.exists():
            try:
                with open(self.pending_requests_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return []
    
    def _save_pending_requests(self, requests: List[Dict]) -> None:
        """保存待处理请求"""
        try:
            with open(self.pending_requests_file, 'w', encoding='utf-8') as f:
                json.dump(requests, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存待处理请求失败: {e}")
    
    def _load_processed_requests(self) -> List[Dict]:
        """加载已处理请求"""
        if self.processed_requests_file.exists():
            try:
                with open(self.processed_requests_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return []
    
    def _record_processed_request(self, user_email: str, article_title: str, 
                                 download_url: str, success: bool, message: str = "") -> None:
        """记录已处理的请求"""
        try:
            processed_requests = self._load_processed_requests()
            
            record = {
                "user_email": user_email,
                "article_title": article_title,
                "download_url": download_url,
                "success": success,
                "message": message,
                "processed_at": datetime.now().isoformat()
            }
            
            processed_requests.append(record)
            
            with open(self.processed_requests_file, 'w', encoding='utf-8') as f:
                json.dump(processed_requests, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"记录处理结果失败: {e}")


def main():
    """命令行接口"""
    parser = argparse.ArgumentParser(description="微信内容变现系统管理器")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 创建资料包命令
    create_parser = subparsers.add_parser('create', help='为文章创建资料包')
    create_parser.add_argument('article_path', help='文章文件路径')
    create_parser.add_argument('--no-upload', action='store_true', help='不上传到GitHub Release')
    
    # 发送奖励命令
    send_parser = subparsers.add_parser('send', help='发送奖励给用户')
    send_parser.add_argument('email', help='用户邮箱')
    send_parser.add_argument('article_title', help='文章标题')
    send_parser.add_argument('--name', help='用户名')
    
    # 添加请求命令
    add_parser = subparsers.add_parser('add', help='添加待处理请求')
    add_parser.add_argument('email', help='用户邮箱')
    add_parser.add_argument('article_title', help='文章标题')
    add_parser.add_argument('--name', help='用户名')
    
    # 批量处理命令
    process_parser = subparsers.add_parser('process', help='批量处理待处理请求')
    process_parser.add_argument('--batch-size', type=int, default=10, help='批处理大小')
    
    # 统计信息命令
    subparsers.add_parser('stats', help='显示系统统计信息')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        manager = RewardSystemManager()
        
        if args.command == 'create':
            success, result = manager.create_article_package(
                args.article_path, 
                not args.no_upload
            )
            if success:
                print(f"✅ 资料包创建成功!")
                print(f"文件: {result['package_path']}")
                if 'github_release' in result and result['github_release']['success']:
                    print(f"GitHub Release: {result['github_release']['release_url']}")
                    print(f"下载链接: {result['github_release']['download_url']}")
            else:
                print(f"❌ 创建失败: {result.get('error')}")
        
        elif args.command == 'send':
            success, message = manager.send_reward_to_user(
                args.email, args.article_title, args.name
            )
            print(f"{'✅' if success else '❌'} {message}")
        
        elif args.command == 'add':
            success = manager.add_pending_request(
                args.email, args.article_title, user_name=args.name
            )
            print(f"{'✅' if success else '❌'} {'添加成功' if success else '添加失败'}")
        
        elif args.command == 'process':
            result = manager.process_pending_requests(args.batch_size)
            print(f"✅ 处理完成: 成功 {result['processed']}, 失败 {result['failed']}")
            print(f"剩余待处理: {result['remaining']}")
            
            if result.get('details'):
                print("\n详细结果:")
                for detail in result['details']:
                    status = "✅" if detail['success'] else "❌"
                    print(f"  {status} {detail['email']} - {detail['article']}: {detail['message']}")
        
        elif args.command == 'stats':
            stats = manager.get_system_stats()
            print("📊 系统统计信息:")
            
            # GitHub Token状态
            token_info = stats.get('github_token', {})
            if token_info.get('days_until_expiry'):
                days_left = token_info['days_until_expiry']
                if days_left <= 7:
                    print(f"⚠️  GitHub Token: {days_left} 天后过期 (需要更新!)")
                elif days_left <= 14:
                    print(f"📅 GitHub Token: {days_left} 天后过期 (建议更新)")
                else:
                    print(f"✅ GitHub Token: {days_left} 天后过期")
            else:
                print("🔍 GitHub Token: 状态检查中...")
            
            print(f"GitHub Releases: {stats['github_releases']['total_releases']} 个")
            print(f"总下载次数: {stats['github_releases']['total_downloads']} 次")
            print(f"邮件发送: {stats['email_delivery']['total_sent']} 成功, {stats['email_delivery']['total_failed']} 失败")
            print(f"成功率: {stats['email_delivery']['success_rate']:.1f}%")
            print(f"待处理请求: {stats['reward_requests']['pending']} 个")
            print(f"已处理请求: {stats['reward_requests']['processed']} 个")
    
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    main()