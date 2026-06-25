"""
报告生成模块
生成 Markdown 报告和 HTML 报告
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from utils import save_markdown, get_today_date, ensure_dir


def generate_summary_report(
    github_news: List[Dict[str, Any]],
    startup_news: List[Dict[str, Any]],
    opportunities_news: List[Dict[str, Any]],
    game_news: List[Dict[str, Any]],
    date: str = None
) -> str:
    """
    生成汇总报告
    """
    if date is None:
        date = get_today_date()
    
    lines = [
        f"# 📰 每日新鲜事 - {date}",
        "",
        f"今日共收集 {len(github_news) + len(startup_news) + len(opportunities_news) + len(game_news)} 条内容",
        "",
        "## 📊 内容概览",
        "",
        f"| 模块 | 数量 | 类型 |",
        f"|------|------|------|",
        f"| 🔥 GitHub 热门项目 | {len(github_news)} | 开源项目 |",
        f"| 💼 创业投资新闻 | {len(startup_news)} | 创投动态 |",
        f"| 💰 小成本创业机会 | {len(opportunities_news)} | 低成本创业 |",
        f"| 🎮 游戏设计灵感 | {len(game_news)} | 游戏设计 |",
        "",
        "---",
        ""
    ]
    
    # GitHub 热门项目
    if github_news:
        lines.extend([
            "## 🔥 GitHub 热门项目",
            "",
            f"昨日新增 star 最多的 {len(github_news)} 个项目",
            ""
        ])
        
        for i, project in enumerate(github_news[:5], 1):
            lines.append(f"{i}. [{project['title']}]({project['url']}) - ⭐ {project.get('stars_formatted', '')}")
        
        if len(github_news) > 5:
            lines.append(f"... 还有 {len(github_news) - 5} 个项目")
        
        lines.extend(["", "---", ""])
    
    # 创业投资新闻
    if startup_news:
        lines.extend([
            "## 💼 创业投资新闻",
            "",
            f"今日创业投资领域最新 {len(startup_news)} 条新闻",
            ""
        ])
        
        for i, news in enumerate(startup_news[:5], 1):
            lines.append(f"{i}. [{news['title']}]({news['url']})")
        
        if len(startup_news) > 5:
            lines.append(f"... 还有 {len(startup_news) - 5} 条新闻")
        
        lines.extend(["", "---", ""])
    
    # 小成本创业机会
    if opportunities_news:
        lines.extend([
            "## 💰 小成本创业机会",
            "",
            f"今日发现 {len(opportunities_news)} 个低成本创业机会",
            ""
        ])
        
        for i, news in enumerate(opportunities_news[:5], 1):
            lines.append(f"{i}. [{news['title']}]({news['url']})")
        
        if len(opportunities_news) > 5:
            lines.append(f"... 还有 {len(opportunities_news) - 5} 个机会")
        
        lines.extend(["", "---", ""])
    
    # 游戏设计灵感
    if game_news:
        lines.extend([
            "## 🎮 游戏设计灵感",
            "",
            f"今日发现 {len(game_news)} 条游戏设计相关内容",
            ""
        ])
        
        for i, news in enumerate(game_news[:5], 1):
            article_type = news.get('type', 'general')
            type_labels = {
                'gameplay': '🎮',
                'art': '🎨',
                'narrative': '📖',
                'tech': '⚙️',
                'indie': '🎯',
                'general': '📰'
            }
            type_icon = type_labels.get(article_type, '📰')
            lines.append(f"{i}. {type_icon} [{news['title']}]({news['url']})")
        
        if len(game_news) > 5:
            lines.append(f"... 还有 {len(game_news) - 5} 条内容")
        
        lines.extend(["", "---", ""])
    
    # 生成时间
    lines.extend([
        f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        "",
        "---",
        "",
        "## 📖 完整报告",
        "",
        f"- [GitHub 热门项目](github-trending.md)",
        f"- [创业投资新闻](startup-news.md)",
        f"- [小成本创业机会](startup-opportunities.md)",
        f"- [游戏设计灵感](game-design.md)",
    ])
    
    return '\n'.join(lines)


def generate_html_report(
    github_news: List[Dict[str, Any]],
    startup_news: List[Dict[str, Any]],
    opportunities_news: List[Dict[str, Any]],
    game_news: List[Dict[str, Any]],
    date: str = None
) -> str:
    """
    生成 HTML 报告
    """
    if date is None:
        date = get_today_date()
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日新鲜事 - {date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        .container {{
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            padding: 30px;
            margin-bottom: 20px;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        
        h2 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            padding-bottom: 5px;
            border-bottom: 1px solid #eee;
        }}
        
        .summary-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        
        .summary-table th,
        .summary-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        
        .summary-table th {{
            background-color: #3498db;
            color: white;
        }}
        
        .summary-table tr:hover {{
            background-color: #f5f5f5;
        }}
        
        .news-item {{
            padding: 15px;
            margin: 10px 0;
            background-color: #f9f9f9;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }}
        
        .news-item h3 {{
            margin-bottom: 10px;
        }}
        
        .news-item h3 a {{
            color: #2c3e50;
            text-decoration: none;
        }}
        
        .news-item h3 a:hover {{
            color: #3498db;
        }}
        
        .news-meta {{
            font-size: 0.9em;
            color: #7f8c8d;
            margin-bottom: 10px;
        }}
        
        .news-summary {{
            color: #555;
            line-height: 1.5;
        }}
        
        .tag {{
            display: inline-block;
            padding: 2px 8px;
            background-color: #e0e0e0;
            border-radius: 3px;
            font-size: 0.8em;
            margin-right: 5px;
        }}
        
        .type-gameplay {{ background-color: #27ae60; color: white; }}
        .type-art {{ background-color: #8e44ad; color: white; }}
        .type-narrative {{ background-color: #e67e22; color: white; }}
        .type-tech {{ background-color: #2980b9; color: white; }}
        .type-indie {{ background-color: #e74c3c; color: white; }}
        
        .star-count {{
            color: #f39c12;
            font-weight: bold;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
        
        .view-more {{
            display: inline-block;
            padding: 10px 20px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 10px;
        }}
        
        .view-more:hover {{
            background-color: #2980b9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📰 每日新鲜事 - {date}</h1>
        
        <p>今日共收集 {len(github_news) + len(startup_news) + len(opportunities_news) + len(game_news)} 条内容</p>
        
        <h2>📊 内容概览</h2>
        
        <table class="summary-table">
            <thead>
                <tr>
                    <th>模块</th>
                    <th>数量</th>
                    <th>类型</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>🔥 GitHub 热门项目</td>
                    <td>{len(github_news)}</td>
                    <td>开源项目</td>
                </tr>
                <tr>
                    <td>💼 创业投资新闻</td>
                    <td>{len(startup_news)}</td>
                    <td>创投动态</td>
                </tr>
                <tr>
                    <td>💰 小成本创业机会</td>
                    <td>{len(opportunities_news)}</td>
                    <td>低成本创业</td>
                </tr>
                <tr>
                    <td>🎮 游戏设计灵感</td>
                    <td>{len(game_news)}</td>
                    <td>游戏设计</td>
                </tr>
            </tbody>
        </table>
"""
    
    # GitHub 热门项目
    if github_news:
        html += """
        <h2>🔥 GitHub 热门项目</h2>
        <p>昨日新增 star 最多的项目</p>
"""
        for i, project in enumerate(github_news[:5], 1):
            html += f"""
        <div class="news-item">
            <h3><a href="{project['url']}" target="_blank">{i}. {project['title']}</a></h3>
            <div class="news-meta">
                ⭐ <span class="star-count">{project.get('stars_formatted', '')}</span> stars | 
                🍴 {project.get('forks', 0)} forks | 
                💻 {project.get('language', '未知')}
            </div>
            <div class="news-summary">{project.get('description', '')}</div>
        </div>
"""
        
        if len(github_news) > 5:
            html += f"""
        <p><a href="github-trending.md" class="view-more">查看全部 {len(github_news)} 个项目</a></p>
"""
    
    # 创业投资新闻
    if startup_news:
        html += """
        <h2>💼 创业投资新闻</h2>
        <p>今日创业投资领域最新新闻</p>
"""
        for i, news in enumerate(startup_news[:5], 1):
            html += f"""
        <div class="news-item">
            <h3><a href="{news['url']}" target="_blank">{i}. {news['title']}</a></h3>
            <div class="news-meta">
                📰 {news.get('source', '未知')} | 
                🕐 {news.get('pub_time', '')}
            </div>
            <div class="news-summary">{news.get('summary', '')}</div>
        </div>
"""
        
        if len(startup_news) > 5:
            html += f"""
        <p><a href="startup-news.md" class="view-more">查看全部 {len(startup_news)} 条新闻</a></p>
"""
    
    # 小成本创业机会
    if opportunities_news:
        html += """
        <h2>💰 小成本创业机会</h2>
        <p>今日发现的低成本创业机会</p>
"""
        for i, news in enumerate(opportunities_news[:5], 1):
            html += f"""
        <div class="news-item">
            <h3><a href="{news['url']}" target="_blank">{i}. {news['title']}</a></h3>
            <div class="news-meta">
                📰 {news.get('source', '未知')} | 
                🕐 {news.get('pub_time', '')}
            </div>
            <div class="news-summary">{news.get('summary', '')}</div>
        </div>
"""
        
        if len(opportunities_news) > 5:
            html += f"""
        <p><a href="startup-opportunities.md" class="view-more">查看全部 {len(opportunities_news)} 个机会</a></p>
"""
    
    # 游戏设计灵感
    if game_news:
        html += """
        <h2>🎮 游戏设计灵感</h2>
        <p>今日发现的游戏设计相关内容</p>
"""
        type_labels = {
            'gameplay': '🎮 玩法创新',
            'art': '🎨 美术风格',
            'narrative': '📖 叙事设计',
            'tech': '⚙️ 技术实现',
            'indie': '🎯 独立游戏',
            'general': '📰 综合'
        }
        
        for i, news in enumerate(game_news[:5], 1):
            article_type = news.get('type', 'general')
            type_label = type_labels.get(article_type, '📰 综合')
            type_class = f"type-{article_type}" if article_type != 'general' else ''
            
            html += f"""
        <div class="news-item">
            <h3><a href="{news['url']}" target="_blank">{i}. {news['title']}</a></h3>
            <div class="news-meta">
                <span class="tag {type_class}">{type_label}</span>
                📰 {news.get('source', '未知')} | 
                🕐 {news.get('pub_time', '')}
            </div>
            <div class="news-summary">{news.get('summary', '')}</div>
        </div>
"""
        
        if len(game_news) > 5:
            html += f"""
        <p><a href="game-design.md" class="view-more">查看全部 {len(game_news)} 条内容</a></p>
"""
    
    # 页脚
    html += f"""
        <div class="footer">
            <p>报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>由 Daily News 自动化系统生成</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def save_reports(
    github_news: List[Dict[str, Any]],
    startup_news: List[Dict[str, Any]],
    opportunities_news: List[Dict[str, Any]],
    game_news: List[Dict[str, Any]],
    date: str = None
) -> Dict[str, str]:
    """
    保存所有报告
    
    Returns:
        Dict with report file paths
    """
    if date is None:
        date = get_today_date()
    
    # 创建输出目录
    output_dir = f"data/{date}"
    ensure_dir(output_dir)
    
    # 生成报告
    summary_md = generate_summary_report(github_news, startup_news, opportunities_news, game_news, date)
    html_report = generate_html_report(github_news, startup_news, opportunities_news, game_news, date)
    
    # 保存文件
    files = {
        'summary': f"{output_dir}/summary.md",
        'html': f"{output_dir}/index.html",
        'github': f"{output_dir}/github-trending.md",
        'startup': f"{output_dir}/startup-news.md",
        'opportunities': f"{output_dir}/startup-opportunities.md",
        'game': f"{output_dir}/game-design.md"
    }
    
    save_markdown(summary_md, files['summary'])
    save_markdown(html_report, files['html'])
    
    return files


def main():
    """
    主函数（用于测试）
    """
    # 测试数据
    test_github = [
        {'title': 'test/project', 'url': 'https://github.com/test', 'stars_formatted': '1.2K', 'forks': 100, 'language': 'Python', 'description': 'Test project'}
    ]
    
    test_startup = [
        {'title': '测试新闻', 'url': 'https://example.com', 'source': '36氪', 'pub_time': '2小时前', 'summary': '测试摘要'}
    ]
    
    test_opportunities = [
        {'title': '低成本创业', 'url': 'https://example.com', 'source': '知乎', 'pub_time': '1天前', 'summary': '测试摘要'}
    ]
    
    test_game = [
        {'title': '游戏设计', 'url': 'https://example.com', 'source': 'GameDev.net', 'pub_time': '3小时前', 'summary': '测试摘要', 'type': 'gameplay'}
    ]
    
    print("测试报告生成...")
    files = save_reports(test_github, test_startup, test_opportunities, test_game)
    
    print("生成的文件:")
    for name, path in files.items():
        print(f"  {name}: {path}")


if __name__ == '__main__':
    main()
