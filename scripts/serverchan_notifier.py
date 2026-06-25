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
from utils import get_today_date, translate_to_zh


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
        bilibili_news: List[Dict[str, Any]] = None,
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

        def _desc(item, max_len=120):
            d = item.get('summary', '') or item.get('description', '') or ''
            if not d:
                return ''
            d = translate_to_zh(d)
            return d[:max_len-3] + '...' if len(d) > max_len else d

        def _title_zh(item):
            t = item.get('title', '')
            return translate_to_zh(t)

        def _img_line(item):
            img = item.get('image', '')
            return f"![]({img})" if img else ""

        # GitHub 热门项目
        if github_news:
            lines.append("## 🔥 GitHub 热门项目")
            for i, p in enumerate(github_news[:10], 1):
                lang = p.get('language', '')
                stars = p.get('stars_formatted', '')
                lang_tag = f" `{lang}`" if lang else ""
                title_zh = _title_zh(p)
                desc = _desc(p)
                lines.append(f"{i}. ⭐{stars}{lang_tag} [{title_zh}]({p['url']})")
                if desc:
                    lines.append(f"   {desc}")
            lines.append("")

        # 创业投资新闻
        if startup_news:
            lines.append("## 💼 创业投资新闻")
            for i, n in enumerate(startup_news[:10], 1):
                source = n.get('source', '')
                source_tag = f" `{source}`" if source else ""
                title_zh = _title_zh(n)
                img = _img_line(n)
                desc = _desc(n)
                lines.append(f"{i}.{source_tag} [{title_zh}]({n['url']})")
                if img:
                    lines.append(img)
                if desc:
                    lines.append(f"   {desc}")
            lines.append("")

        # 小成本创业机会
        if opportunities_news:
            lines.append("## 💰 小成本创业机会")
            for i, n in enumerate(opportunities_news[:10], 1):
                source = n.get('source', '')
                source_tag = f" `{source}`" if source else ""
                title_zh = _title_zh(n)
                img = _img_line(n)
                desc = _desc(n)
                lines.append(f"{i}.{source_tag} [{title_zh}]({n['url']})")
                if img:
                    lines.append(img)
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
                title_zh = _title_zh(n)
                img = _img_line(n)
                desc = _desc(n)
                lines.append(f"{i}. `#{tag}` [{title_zh}]({n['url']})")
                if img:
                    lines.append(img)
                if desc:
                    lines.append(f"   {desc}")
            lines.append("")

        # B站 UP主更新
        if bilibili_news:
            lines.append("## 📺 B站 UP主更新")
            for i, n in enumerate(bilibili_news[:10], 1):
                up = n.get('up_name', '')
                up_tag = f" `{up}`" if up else ""
                title_zh = _title_zh(n)
                img = _img_line(n)
                desc = _desc(n)
                lines.append(f"{i}.{up_tag} [{title_zh}]({n['url']})")
                if img:
                    lines.append(img)
                if desc:
                    lines.append(f"   {desc}")
            lines.append("")

        # 底部
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
        bilibili_news: List[Dict[str, Any]] = None,
        report_url: Optional[str] = None
    ) -> bool:
        """
        发送每日报告

        Returns:
            是否发送成功
        """
        title, content = self.format_daily_report(
            github_news, startup_news, opportunities_news, game_news, bilibili_news, report_url
        )
        return self.send(title, content)
