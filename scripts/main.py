"""
主脚本
协调所有模块，执行完整的抓取、去重、生成报告、推送流程
"""

import os
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Any

# 添加脚本目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from utils import get_today_date, ensure_dir
from fetch_github import fetch_github_trending, format_github_markdown
from fetch_startup import fetch_startup_news, format_startup_markdown
from fetch_opportunities import fetch_opportunities, format_opportunities_markdown
from fetch_game import fetch_game_news, format_game_markdown
from fetch_bilibili import fetch_bilibili_updates, format_bilibili_markdown, DEFAULT_BILIBILI_UPS
from deduplicator import deduplicate_news, sort_news_by_relevance
from report_generator import save_reports
from wecom_notifier import WeChatNotifier
from serverchan_notifier import ServerChanNotifier


def run_daily_news(
    skip_dedup: bool = False,
    skip_notify: bool = False,
    report_url: str = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    执行每日新闻抓取流程
    
    Args:
        skip_dedup: 是否跳过去重
        skip_notify: 是否跳过推送
        report_url: 报告 URL（用于推送消息中的链接）
        
    Returns:
        包含各模块新闻的字典
    """
    print("=" * 60)
    print(f"开始执行每日新闻抓取 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 抓取新闻
    print("\n[1/5] 抓取新闻...")
    
    print("\n--- GitHub 热门项目 ---")
    github_news = fetch_github_trending()
    print(f"获取到 {len(github_news)} 个项目")
    
    print("\n--- 创业投资新闻 ---")
    startup_news = fetch_startup_news()
    print(f"获取到 {len(startup_news)} 条新闻")
    
    print("\n--- 小成本创业机会 ---")
    opportunities_news = fetch_opportunities()
    print(f"获取到 {len(opportunities_news)} 个机会")
    
    print("\n--- 游戏设计灵感 ---")
    game_news = fetch_game_news()
    print(f"获取到 {len(game_news)} 条内容")

    print("\n--- B站 UP主更新 ---")
    bilibili_news = fetch_bilibili_updates(DEFAULT_BILIBILI_UPS)
    print(f"获取到 {len(bilibili_news)} 个视频")

    # 2. 去重处理
    if not skip_dedup:
        print("\n[2/5] 去重处理...")
        
        github_news = deduplicate_news(github_news, 'github')
        startup_news = deduplicate_news(startup_news, 'startup')
        opportunities_news = deduplicate_news(opportunities_news, 'opportunity')
        game_news = deduplicate_news(game_news, 'game')
        bilibili_news = deduplicate_news(bilibili_news, 'bilibili')

        print(f"去重后: GitHub {len(github_news)}, 创投 {len(startup_news)}, 机会 {len(opportunities_news)}, 游戏 {len(game_news)}, B站 {len(bilibili_news)}")
    else:
        print("\n[2/5] 跳过去重处理")

    # 3. 相关性排序
    print("\n[3/5] 相关性排序...")

    github_news = sort_news_by_relevance(github_news, 'github')
    startup_news = sort_news_by_relevance(startup_news, 'startup')
    opportunities_news = sort_news_by_relevance(opportunities_news, 'opportunity')
    game_news = sort_news_by_relevance(game_news, 'game')
    
    # 4. 生成报告
    print("\n[4/5] 生成报告...")
    
    files = save_reports(github_news, startup_news, opportunities_news, game_news)
    
    print("生成的文件:")
    for name, path in files.items():
        print(f"  {name}: {path}")
    
    # 5. 推送通知
    if not skip_notify:
        print("\n[5/5] 推送通知...")

        # 计算报告 URL
        if not report_url:
            github_repo = os.environ.get('GITHUB_REPOSITORY', '')
            if github_repo:
                report_url = f"https://{github_repo.split('/')[0]}.github.io/{github_repo.split('/')[1]}/{get_today_date()}/"

        sent = False

        # 优先使用 Server酱（推送到微信）
        serverchan_key = os.environ.get('SERVERCHAN_SENDKEY')
        if serverchan_key:
            notifier = ServerChanNotifier(serverchan_key)
            if notifier.send_daily_report(github_news, startup_news, opportunities_news, game_news, bilibili_news, report_url):
                print("Server酱推送成功")
                sent = True
            else:
                print("Server酱推送失败，尝试企业微信...")

        # 备选：企业微信
        if not sent:
            webhook_url = os.environ.get('WECOM_WEBHOOK_URL')
            if webhook_url:
                notifier = WeChatNotifier(webhook_url)
                if notifier.send_daily_report(github_news, startup_news, opportunities_news, game_news, bilibili_news, report_url):
                    print("企业微信推送成功")
                    sent = True
                else:
                    print("企业微信推送失败")

        if not sent:
            print("未配置推送密钥（SERVERCHAN_SENDKEY 或 WECOM_WEBHOOK_URL），跳过推送")
    else:
        print("\n[5/5] 跳过推送通知")
    
    # 完成
    print("\n" + "=" * 60)
    print(f"每日新闻抓取完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return {
        'github': github_news,
        'startup': startup_news,
        'opportunities': opportunities_news,
        'game': game_news,
        'bilibili': bilibili_news
    }


def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description='每日新闻抓取工具')
    parser.add_argument('--skip-dedup', action='store_true', help='跳过去重处理')
    parser.add_argument('--skip-notify', action='store_true', help='跳过推送通知')
    parser.add_argument('--report-url', type=str, help='报告 URL（用于推送消息中的链接）')
    
    args = parser.parse_args()
    
    try:
        results = run_daily_news(
            skip_dedup=args.skip_dedup,
            skip_notify=args.skip_notify,
            report_url=args.report_url
        )
        
        # 打印统计
        print("\n📊 统计:")
        print(f"  GitHub 热门项目: {len(results['github'])} 个")
        print(f"  创业投资新闻: {len(results['startup'])} 条")
        print(f"  小成本创业机会: {len(results['opportunities'])} 个")
        print(f"  游戏设计灵感: {len(results['game'])} 条")
        print(f"  B站 UP主更新: {len(results.get('bilibili', []))} 个")
        print(f"  总计: {sum(len(v) for v in results.values())} 条")
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
