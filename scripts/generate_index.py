"""
生成 GitHub Pages 首页
列出所有日期的报告
"""

import os
import sys
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, os.path.dirname(__file__))

from utils import get_today_date, ensure_dir


def get_report_dates() -> List[str]:
    """
    获取所有报告日期
    """
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    dates = []
    
    if os.path.exists(data_dir):
        for item in os.listdir(data_dir):
            item_path = os.path.join(data_dir, item)
            if os.path.isdir(item_path) and item != 'history':
                # 检查是否是日期格式
                try:
                    datetime.strptime(item, '%Y-%m-%d')
                    dates.append(item)
                except ValueError:
                    continue
    
    # 按日期降序排序
    dates.sort(reverse=True)
    return dates


def generate_index_html(dates: List[str]) -> str:
    """
    生成首页 HTML
    """
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日新鲜事 - Daily News</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        
        .container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            padding: 30px;
            margin-bottom: 20px;
        }
        
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        
        .description {
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }
        
        .date-list {
            list-style: none;
        }
        
        .date-item {
            padding: 15px;
            margin: 10px 0;
            background-color: #f9f9f9;
            border-radius: 5px;
            border-left: 4px solid #3498db;
            transition: all 0.3s ease;
        }
        
        .date-item:hover {
            background-color: #eef5ff;
            transform: translateX(5px);
        }
        
        .date-item a {
            color: #2c3e50;
            text-decoration: none;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .date-item a:hover {
            color: #3498db;
        }
        
        .date-item .date {
            font-size: 1.2em;
            font-weight: bold;
        }
        
        .date-item .view {
            color: #3498db;
            font-size: 0.9em;
        }
        
        .no-reports {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            margin: 30px 0;
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }
        
        .stat-label {
            color: #7f8c8d;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📰 每日新鲜事 - Daily News</h1>
        
        <p class="description">
            每日自动抓取 GitHub 热门项目、创业投资新闻、小成本创业机会和游戏设计灵感。
            <br>
            由 GitHub Actions 定时触发，自动部署到 GitHub Pages。
        </p>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">""" + str(len(dates)) + """</div>
                <div class="stat-label">天数</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">40+</div>
                <div class="stat-label">每日条目</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">4</div>
                <div class="stat-label">模块</div>
            </div>
        </div>
        
        <h2>📅 历史报告</h2>
"""
    
    if dates:
        html += """
        <ul class="date-list">
"""
        for date in dates[:30]:  # 最多显示 30 天
            html += f"""
            <li class="date-item">
                <a href="{date}/">
                    <span class="date">📆 {date}</span>
                    <span class="view">查看报告 →</span>
                </a>
            </li>
"""
        
        html += """
        </ul>
"""
        
        if len(dates) > 30:
            html += f"""
        <p style="text-align: center; color: #7f8c8d; margin-top: 20px;">
            ... 还有 {len(dates) - 30} 天的历史报告
        </p>
"""
    else:
        html += """
        <div class="no-reports">
            <p>暂无报告</p>
            <p>报告将在每天北京时间 08:00 自动生成</p>
        </div>
"""
    
    html += f"""
        <div class="footer">
            <p>最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>由 Daily News 自动化系统生成</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def main():
    """
    主函数
    """
    print("生成 GitHub Pages 首页...")
    
    # 获取报告日期
    dates = get_report_dates()
    print(f"找到 {len(dates)} 个报告日期")
    
    # 生成首页
    html = generate_index_html(dates)
    
    # 保存到 data/index.html
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
    ensure_dir(data_dir)
    
    index_path = os.path.join(data_dir, 'index.html')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"首页已生成: {index_path}")


if __name__ == '__main__':
    main()
