"""
GitHub Release管理器
用于自动创建Release并上传内容包文件，支持微信公众号内容变现系统
"""

import os
import json
import requests
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import base64


@dataclass
class ReleaseInfo:
    """Release信息数据类"""
    tag_name: str
    name: str
    body: str
    asset_url: str
    download_count: int = 0


class GitHubReleaseManager:
    """GitHub Release管理器"""
    
    def __init__(self, token: str, username: str, repo: str):
        self.token = token
        self.username = username
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{username}/{repo}"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": f"{username}-{repo}-release-manager"
        }
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 数据存储文件
        self.data_file = Path("_data/github_releases.json")
        self.data_file.parent.mkdir(exist_ok=True)
        
        # Token状态缓存文件
        self.token_cache_file = self.data_file.parent / "github_token_status.json"
        
        # 检查token状态
        self._check_token_status()
        
    def _check_token_status(self) -> None:
        """检查GitHub Token的有效性和过期时间"""
        try:
            # 获取token信息
            token_info = self._get_token_info()
            if token_info:
                expires_at = token_info.get("expires_at")
                if expires_at:
                    # 解析过期时间
                    expire_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                    days_until_expiry = (expire_date - datetime.now(expire_date.tzinfo)).days
                    
                    # 保存token状态
                    self._save_token_status(token_info, days_until_expiry)
                    
                    # 根据剩余天数发出警告
                    if days_until_expiry <= 7:
                        self.logger.error(f"⚠️  GitHub Token将在 {days_until_expiry} 天后过期！请及时更新。")
                        print(f"⚠️  警告: GitHub Token将在 {days_until_expiry} 天后过期，请及时在GitHub设置中更新token。")
                    elif days_until_expiry <= 14:
                        self.logger.warning(f"📅 GitHub Token将在 {days_until_expiry} 天后过期，建议提前更新。")
                        print(f"📅 提醒: GitHub Token将在 {days_until_expiry} 天后过期，建议提前更新。")
                    elif days_until_expiry <= 30:
                        self.logger.info(f"GitHub Token将在 {days_until_expiry} 天后过期。")
                else:
                    # 永久token
                    self.logger.info("使用永久GitHub Token。")
        except Exception as e:
            self.logger.warning(f"无法检查GitHub Token状态: {e}")
    
    def _get_token_info(self) -> Optional[Dict]:
        """获取GitHub Token信息"""
        try:
            # 调用GitHub API获取当前token信息
            response = requests.get(
                "https://api.github.com/user",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                # 检查响应头中的token信息
                scopes = response.headers.get('X-OAuth-Scopes', '')
                rate_limit = response.headers.get('X-RateLimit-Limit', 'unknown')
                
                # 对于90天过期的token，我们使用创建后90天作为估算
                # 由于GitHub API不直接提供token过期时间，我们需要通过其他方式推断
                token_info = {
                    "type": "personal_access_token",
                    "scopes": scopes,
                    "rate_limit": rate_limit,
                    "user": user_data.get("login"),
                    "expires_at": None
                }
                
                # 尝试从缓存中获取token创建时间，如果没有则记录当前时间作为检测起点
                cached_status = self._load_token_status()
                if cached_status and cached_status.get("token_first_seen"):
                    first_seen = datetime.fromisoformat(cached_status["token_first_seen"])
                else:
                    first_seen = datetime.now()
                    # 保存首次检测时间
                    self._save_token_first_seen(first_seen)
                
                # 假设90天过期期限（用户设置的过期时间）
                estimated_expiry = first_seen + timedelta(days=90)
                token_info["expires_at"] = estimated_expiry.isoformat()
                token_info["estimated"] = True  # 标记这是估算时间
                
                return token_info
                
            elif response.status_code == 401:
                self.logger.error("GitHub Token无效或已过期！")
                raise ValueError("GitHub Token无效或已过期")
            else:
                self.logger.warning(f"无法验证GitHub Token: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            self.logger.warning(f"网络请求失败，无法验证token: {e}")
            return None
    
    def _save_token_first_seen(self, first_seen: datetime) -> None:
        """保存token首次检测时间"""
        try:
            cache_data = {"token_first_seen": first_seen.isoformat()}
            
            # 如果文件已存在，合并数据
            if self.token_cache_file.exists():
                try:
                    with open(self.token_cache_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                        if not existing_data.get("token_first_seen"):
                            existing_data["token_first_seen"] = first_seen.isoformat()
                            cache_data = existing_data
                except (json.JSONDecodeError, FileNotFoundError):
                    pass
            
            with open(self.token_cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.warning(f"保存token首次检测时间失败: {e}")
    
    def _save_token_status(self, token_info: Dict, days_until_expiry: Optional[int]) -> None:
        """保存token状态到缓存文件"""
        try:
            # 加载现有数据以保留token_first_seen
            existing_data = self._load_token_status() or {}
            
            status = {
                "checked_at": datetime.now().isoformat(),
                "token_info": token_info,
                "days_until_expiry": days_until_expiry,
                "last_warning_date": datetime.now().date().isoformat() if days_until_expiry and days_until_expiry <= 30 else None,
                "token_first_seen": existing_data.get("token_first_seen")  # 保留首次检测时间
            }
            
            with open(self.token_cache_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.warning(f"保存token状态失败: {e}")
    
    def _load_token_status(self) -> Optional[Dict]:
        """加载token状态缓存"""
        if self.token_cache_file.exists():
            try:
                with open(self.token_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return None
    
    def get_token_expiry_status(self) -> Dict:
        """获取token过期状态信息"""
        status = self._load_token_status()
        if status:
            return {
                "has_expiry_info": status.get("days_until_expiry") is not None,
                "days_until_expiry": status.get("days_until_expiry"),
                "checked_at": status.get("checked_at"),
                "needs_renewal": status.get("days_until_expiry", 999) <= 7 if status.get("days_until_expiry") else False
            }
        return {
            "has_expiry_info": False,
            "days_until_expiry": None,
            "checked_at": None,
            "needs_renewal": False
        }
        
    def _load_release_data(self) -> Dict:
        """加载Release数据"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                self.logger.warning("无法加载现有Release数据，将创建新文件")
        
        return {
            "articles": {},
            "releases": {},
            "stats": {
                "total_releases": 0,
                "total_downloads": 0,
                "created_date": datetime.now().isoformat()
            }
        }
    
    def _save_release_data(self, data: Dict) -> None:
        """保存Release数据"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存Release数据失败: {e}")
    
    def _generate_tag_name(self, article_title: str) -> str:
        """生成标签名称"""
        # 清理文章标题，生成适合的标签名
        import re
        clean_title = re.sub(r'[^\w\-]', '-', article_title.lower())
        clean_title = re.sub(r'-+', '-', clean_title).strip('-')
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"reward-{clean_title}-{timestamp}"
    
    def create_release(self, article_title: str, package_path: str, 
                      article_date: str = None) -> Tuple[bool, Dict]:
        """
        创建Release并上传内容包
        
        Args:
            article_title: 文章标题
            package_path: 内容包文件路径
            article_date: 文章发布日期
            
        Returns:
            (success, release_info)
        """
        try:
            # 生成Release信息
            tag_name = self._generate_tag_name(article_title)
            release_name = f"📦 {article_title} - 完整资料包"
            
            if article_date:
                release_body = f"""## 📄 文章信息

**标题**: {article_title}  
**发布日期**: {article_date}  

## 📦 内容包含

- 🔍 **完整深度版PDF**: 包含详细技术分析与数据解读
- 📊 **高清图表合集**: 文章中所有图表的高清版本
- 📚 **参考资料汇总**: 权威来源链接和补充材料
- 🔗 **资源链接清单**: 相关工具和扩展阅读资源

## 💡 获取方式

1. 在微信公众号打赏任意金额
2. 截图发送到公众号并提供邮箱地址
3. 24小时内自动发送到您的邮箱

---

*本资料包通过GitHub Release免费提供，支持无限次下载*
"""
            else:
                release_body = f"""## 📦 {article_title} - 完整资料包

包含文章的详细版本、高清图表和参考资料。

通过微信公众号打赏获取，详情请查看文章底部说明。
"""
            
            # 检查文件是否存在
            if not os.path.exists(package_path):
                return False, {"error": f"文件不存在: {package_path}"}
            
            # 创建Release
            release_data = {
                "tag_name": tag_name,
                "target_commitish": "main",
                "name": release_name,
                "body": release_body,
                "draft": False,
                "prerelease": False
            }
            
            self.logger.info(f"创建Release: {tag_name}")
            response = requests.post(
                f"{self.base_url}/releases",
                headers=self.headers,
                json=release_data,
                timeout=30
            )
            
            if response.status_code != 201:
                error_msg = f"创建Release失败: {response.status_code} - {response.text}"
                self.logger.error(error_msg)
                return False, {"error": error_msg}
            
            release_info = response.json()
            release_id = release_info["id"]
            upload_url = release_info["upload_url"].replace("{?name,label}", "")
            
            # 上传文件
            filename = os.path.basename(package_path)
            upload_url_with_name = f"{upload_url}?name={filename}"
            
            self.logger.info(f"上传文件: {filename}")
            with open(package_path, 'rb') as f:
                upload_response = requests.post(
                    upload_url_with_name,
                    headers={
                        "Authorization": f"token {self.token}",
                        "Content-Type": "application/zip"
                    },
                    data=f,
                    timeout=300  # 5分钟超时
                )
            
            if upload_response.status_code != 201:
                # 如果上传失败，删除已创建的Release
                self.delete_release(tag_name)
                error_msg = f"文件上传失败: {upload_response.status_code} - {upload_response.text}"
                self.logger.error(error_msg)
                return False, {"error": error_msg}
            
            asset_info = upload_response.json()
            
            # 保存到本地数据库
            data = self._load_release_data()
            
            release_record = {
                "tag_name": tag_name,
                "name": release_name,
                "body": release_body,
                "html_url": release_info["html_url"],
                "asset_url": asset_info["browser_download_url"],
                "asset_size": asset_info["size"],
                "created_at": release_info["created_at"],
                "download_count": 0
            }
            
            data["articles"][article_title] = release_record
            data["releases"][tag_name] = release_record
            data["stats"]["total_releases"] += 1
            
            self._save_release_data(data)
            
            self.logger.info(f"Release创建成功: {release_info['html_url']}")
            return True, release_record
            
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求失败: {e}"
            self.logger.error(error_msg)
            return False, {"error": error_msg}
        except Exception as e:
            error_msg = f"创建Release时发生错误: {e}"
            self.logger.error(error_msg)
            return False, {"error": error_msg}
    
    def get_release_by_article(self, article_title: str) -> Optional[Dict]:
        """根据文章标题获取Release信息"""
        data = self._load_release_data()
        return data["articles"].get(article_title)
    
    def list_releases(self) -> List[Dict]:
        """列出所有Release"""
        data = self._load_release_data()
        return list(data["releases"].values())
    
    def delete_release(self, tag_name: str) -> bool:
        """删除指定的Release"""
        try:
            # 从GitHub删除
            response = requests.get(
                f"{self.base_url}/releases/tags/{tag_name}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                release_info = response.json()
                delete_response = requests.delete(
                    f"{self.base_url}/releases/{release_info['id']}",
                    headers=self.headers
                )
                
                if delete_response.status_code == 204:
                    # 从本地数据删除
                    data = self._load_release_data()
                    
                    # 找到并删除相关记录
                    article_to_remove = None
                    for article, release in data["articles"].items():
                        if release["tag_name"] == tag_name:
                            article_to_remove = article
                            break
                    
                    if article_to_remove:
                        del data["articles"][article_to_remove]
                    
                    if tag_name in data["releases"]:
                        del data["releases"][tag_name]
                        data["stats"]["total_releases"] -= 1
                    
                    self._save_release_data(data)
                    self.logger.info(f"Release删除成功: {tag_name}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"删除Release失败: {e}")
            return False
    
    def update_download_stats(self) -> None:
        """更新下载统计"""
        try:
            # 从GitHub API获取最新统计
            response = requests.get(
                f"{self.base_url}/releases",
                headers=self.headers
            )
            
            if response.status_code == 200:
                github_releases = response.json()
                data = self._load_release_data()
                
                total_downloads = 0
                for release in github_releases:
                    tag_name = release["tag_name"]
                    if tag_name in data["releases"]:
                        # 统计所有资产的下载次数
                        downloads = sum(asset["download_count"] for asset in release.get("assets", []))
                        data["releases"][tag_name]["download_count"] = downloads
                        total_downloads += downloads
                
                data["stats"]["total_downloads"] = total_downloads
                data["stats"]["last_updated"] = datetime.now().isoformat()
                
                self._save_release_data(data)
                self.logger.info(f"统计更新完成，总下载次数: {total_downloads}")
                
        except Exception as e:
            self.logger.error(f"更新统计失败: {e}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        data = self._load_release_data()
        return data.get("stats", {})


def create_github_manager() -> GitHubReleaseManager:
    """创建GitHub Release管理器实例"""
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv("GITHUB_TOKEN")
    username = os.getenv("GITHUB_USERNAME", "zhurong2020")
    repo = os.getenv("GITHUB_REPO", "youxinyanzhe")
    
    if not token or token == "your_github_token":
        raise ValueError("请在.env文件中设置有效的GITHUB_TOKEN")
    
    return GitHubReleaseManager(token, username, repo)


if __name__ == "__main__":
    # 测试脚本
    import sys
    
    if len(sys.argv) != 3:
        print("用法: python github_release_manager.py <article_title> <package_path>")
        sys.exit(1)
    
    article_title = sys.argv[1]
    package_path = sys.argv[2]
    
    try:
        manager = create_github_manager()
        success, result = manager.create_release(article_title, package_path)
        
        if success:
            print(f"✅ Release创建成功!")
            print(f"下载链接: {result['asset_url']}")
        else:
            print(f"❌ 创建失败: {result.get('error', '未知错误')}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")