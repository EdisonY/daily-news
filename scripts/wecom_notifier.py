"""
企业微信推送模块
发送消息到企业微信群机器人
"""

import json
import os
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from utils import get_today_date


class WeChatNotifier:
    """
    企业微信机器人通知器
    """
    
    def __init__(self, webhook_url: Optional[str] = None):
        """
        初始化
        
        Args:
            webhook_url: 企业微信机器人 Webhook URL
        """
        self.webhook_url = webhook_url or os.environ.get('WECOM_WEBHOOK_URL')
        
        if not self.webhook_url:
            print("警告: 未配置企业微信 Webhook URL")
    
    def send_markdown(self, content: str) -> bool:
        """
        发送 Markdown 消息
        
        Args:
            content: Markdown 格式的消息内容
            
        Returns:
            是否发送成功
        """
        if not self.webhook_url:
            print("错误: 未配置企业微信 Webhook URL")
            return False
        
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    print("企业微信消息发送成功")
                    return True
                else:
                    print(f"企业微信消息发送失败: {result.get('errmsg', '未知错误')}")
                    return False
            else:
                print(f"企业微信消息发送失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"企业微信消息发送异常: {e}")
            return False
    
    def send_text(self, content: str) -> bool:
        """
        发送文本消息
        
        Args:
            content: 文本消息内容
            
        Returns:
            是否发送成功
        """
        if not self.webhook_url:
            print("错误: 未配置企业微信 Webhook URL")
            return False
        
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    print("企业微信消息发送成功")
                    return True
                else:
                    print(f"企业微信消息发送失败: {result.get('errmsg', '未知错误')}")
                    return False
            else:
                print(f"企业微信消息发送失败: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"企业微信消息发送异常: {e}")
            return False
    
    def format_daily_report(
        self,
        github_news: List[Dict[str, Any]],
        startup_news: List[Dict[str, Any]],
        opportunities_news: List[Dict[str, Any]],
        game_news: List[Dict[str, Any]],
        report_url: Optional[str] = None
    ) -> str:
        """
        格式化每日报告为 Markdown
        
        Args:
            github_news: GitHub 热门项目
            startup_news: 创业投资新闻
            opportunities_news: 小成本创业机会
            game_news: 游戏设计灵感
            report_url: 完整报告链接
            
        Returns:
            Markdown 格式的报告
        """
        date = get_today_date()
        total_count = len(github_news) + len(startup_news) + len(opportunities_news) + len(game_news)
        
        lines = [
            f"# 📰 每日新鲜事 - {date}",
            "",
            f"今日共收集 **{total_count}** 条内容",
            "",
            "---",
            ""
        ]
        
        # GitHub 热门项目
        if github_news:
            lines.extend([
                "## 🔥 GitHub 热门项目",
                ""
            ])
            for i, project in enumerate(github_news[:3], 1):
                lines.append(f"{i}. [{project['title']}]({project['url']}) - ⭐ {project.get('stars_formatted', '')}")
            if len(github_news) > 3:
                lines.append(f"... 还有 {len(github_news) - 3} 个项目")
            lines.append("")
        
        # 创业投资新闻
        if startup_news:
            lines.extend([
                "## 💼 创业投资新闻",
                ""
            ])
            for i, news in enumerate(startup_news[:3], 1):
                lines.append(f"{i}. [{news['title']}]({news['url']})")
            if len(startup_news) > 3:
                lines.append(f"... 还有 {len(startup_news) - 3} 条新闻")
            lines.append("")
        
        # 小成本创业机会
        if opportunities_news:
            lines.extend([
                "## 💰 小成本创业机会",
                ""
            ])
            for i, news in enumerate(opportunities_news[:3], 1):
                lines.append(f"{i}. [{news['title']}]({news['url']})")
            if len(opportunities_news) > 3:
                lines.append(f"... 还有 {len(opportunities_news) - 3} 个机会")
            lines.append("")
        
        # 游戏设计灵感
        if game_news:
            lines.extend([
                "## 🎮 游戏设计灵感",
                ""
            ])
            type_labels = {
                'gameplay': '🎮',
                'art': '🎨',
                'narrative': '📖',
                'tech': '⚙️',
                'indie': '🎯',
                'general': '📰'
            }
            for i, news in enumerate(game_news[:3], 1):
                article_type = news.get('type', 'general')
                type_icon = type_labels.get(article_type, '📰')
                lines.append(f"{i}. {type_icon} [{news['title']}]({news['url']})")
            if len(game_news) > 3:
                lines.append(f"... 还有 {len(game_news) - 3} 条内容")
            lines.append("")
        
        # 完整报告链接
        if report_url:
            lines.extend([
                "---",
                "",
                f"📊 [查看完整报告]({report_url})"
            ])
        
        return '\n'.join(lines)
    
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
        
        Args:
            github_news: GitHub 热门项目
            startup_news: 创业投资新闻
            opportunities_news: 小成本创业机会
            game_news: 游戏设计灵感
            report_url: 完整报告链接
            
        Returns:
            是否发送成功
        """
        content = self.format_daily_report(
            github_news,
            startup_news,
            opportunities_news,
            game_news,
            report_url
        )
        
        return self.send_markdown(content)


def main():
    """
    主函数（用于测试）
    """
    # 测试数据
    test_github = [
        {'title': 'test/project', 'url': 'https://github.com/test', 'stars_formatted': '1.2K'}
    ]
    
    test_startup = [
        {'title': '测试新闻', 'url': 'https://example.com'}
    ]
    
    test_opportunities = [
        {'title': '低成本创业', 'url': 'https://example.com'}
    ]
    
    test_game = [
        {'title': '游戏设计', 'url': 'https://example.com', 'type': 'gameplay'}
    ]
    
    print("测试企业微信推送...")
    
    # 检查环境变量
    webhook_url = os.environ.get('WECOM_WEBHOOK_URL')
    if webhook_url:
        print(f"Webhook URL: {webhook_url[:20]}...")
        
        notifier = WeChatNotifier(webhook_url)
        
        # 生成报告内容
        content = notifier.format_daily_report(
            test_github,
            test_startup,
            test_opportunities,
            test_game,
            "https://example.com/report"
        )
        
        print("\n报告内容预览:")
        print(content[:500] + "...")
        
        # 发送测试消息
        # notifier.send_daily_report(test_github, test_startup, test_opportunities, test_game)
    else:
        print("未配置 WECOM_WEBHOOK_URL 环境变量")
        print("请在 GitHub Secrets 中添加 WECOM_WEBHOOK_URL")


if __name__ == '__main__':
    main()
