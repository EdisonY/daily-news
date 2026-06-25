"""
Server酱推送模块
通过 Server酱 将消息推送到微信
注册地址: https://sct.ftqq.com/
"""

import os
import requests
from typing import List, Dict, Any, Optional
import sys
sys.path.insert(0, os.path.dirname(__file__))
from utils import get_today_date


class ServerChanNotifier:
    """
    Server酱通知器
    消息会推送到微信公众号「方糖」的对话框
    """

    def __init__(self, send_key: Optional[str] = None):
        """
        初始化

        Args:
            send_key: Server酱的 SendKey
        """
        self.send_key = send_key or os.environ.get('SERVERCHAN_SENDKEY')

        if not self.send_key:
            print("警告: 未配置 SERVERCHAN_SENDKEY")

    def send(self, title: str, content: str) -> bool:
        """
        发送消息

        Args:
            title: 消息标题（最多 256 字符）
            content: 消息内容（Markdown 格式）

        Returns:
            是否发送成功
        """
        if not self.send_key:
            print("错误: 未配置 SERVERCHAN_SENDKEY")
            return False

        url = f"https://sctapi.ftqq.com/{self.send_key}.send"
        data = {
            "title": title[:256],
            "content": content,
            "channel": "9"  # 微信服务号
        }

        try:
            response = requests.post(url, data=data, timeout=15)
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    print("Server酱消息发送成功")
                    return True
                else:
                    print(f"Server酱消息发送失败: {result.get('message', '未知错误')}")
                    return False
            else:
                print(f"Server酱消息发送失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"Server酱消息发送异常: {e}")
            return False

    def format_daily_report(
        self,
        github_news: List[Dict[str, Any]],
        startup_news: List[Dict[str, Any]],
        opportunities_news: List[Dict[str, Any]],
        game_news: List[Dict[str, Any]],
        report_url: Optional[str] = None
    ) -> tuple:
        """
        格式化每日报告

        Returns:
            (title, content) 元组
        """
        date = get_today_date()
        total_count = len(github_news) + len(startup_news) + len(opportunities_news) + len(game_news)

        title = f"📰 每日新鲜事 {date} | 共{total_count}条"

        lines = []

        # GitHub 热门项目
        if github_news:
            lines.append("## 🔥 GitHub 热门项目")
            for i, p in enumerate(github_news[:10], 1):
                desc = p.get('description', '') or '暂无描述'
                if len(desc) > 80:
                    desc = desc[:77] + '...'
                lang = p.get('language', '')
                stars = p.get('stars_formatted', '')
                lang_tag = f" `{lang}`" if lang else ""
                lines.append(f"{i}. ⭐{stars}{lang_tag} [{p['title']}]({p['url']})")
                lines.append(f"   {desc}")
            lines.append("")

        # 创业投资新闻
        if startup_news:
            lines.append("## 💼 创业投资新闻")
            for i, n in enumerate(startup_news[:10], 1):
                desc = n.get('summary', '') or n.get('description', '') or ''
                if len(desc) > 80:
                    desc = desc[:77] + '...'
                source = n.get('source', '')
                source_tag = f" `{source}`" if source else ""
                lines.append(f"{i}.{source_tag} [{n['title']}]({n['url']})")
                if desc:
                    lines.append(f"   {desc}")
            lines.append("")

        # 小成本创业机会
        if opportunities_news:
            lines.append("## 💰 小成本创业机会")
            for i, n in enumerate(opportunities_news[:10], 1):
                desc = n.get('summary', '') or n.get('description', '') or ''
                if len(desc) > 80:
                    desc = desc[:77] + '...'
                source = n.get('source', '')
                source_tag = f" `{source}`" if source else ""
                lines.append(f"{i}.{source_tag} [{n['title']}]({n['url']})")
                if desc:
                    lines.append(f"   {desc}")
            lines.append("")

        # 游戏设计灵感
        if game_news:
            lines.append("## 🎮 游戏设计灵感")
            type_labels = {
                'gameplay': '玩法创新', 'art': '视觉设计', 'narrative': '叙事设计',
                'tech': '技术实现', 'indie': '独立游戏', 'general': '行业资讯'
            }
            for i, n in enumerate(game_news[:10], 1):
                tag = type_labels.get(n.get('type', 'general'), '资讯')
                desc = n.get('summary', '') or n.get('description', '') or ''
                if len(desc) > 80:
                    desc = desc[:77] + '...'
                lines.append(f"{i}. `#{tag}` [{n['title']}]({n['url']})")
                if desc:
                    lines.append(f"   {desc}")
            lines.append("")

        # 底部：报告地址
        if report_url:
            pages_url = report_url
            if pages_url.endswith('.md'):
                pages_url = pages_url.rsplit('/', 1)[0] + '/'
            lines.append(f"---")
            lines.append(f"📊 [查看完整报告]({pages_url})")

        return title, '\n'.join(lines)

    def send_daily_report(
        self,
        github_news: List[Dict[str, Any]],
        startup_news: List[Dict[str, Any]],
        opportunities_news: List[Dict[str, Any]],
        game_news: List[Dict[str, Any]],
        report_url: Optional[str] = None
    ) -> bool:
        """
        发送每日报告

        Returns:
            是否发送成功
        """
        title, content = self.format_daily_report(
            github_news, startup_news, opportunities_news, game_news, report_url
        )
        return self.send(title, content)
