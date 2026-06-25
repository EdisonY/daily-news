"""
GitHub 热门项目抓取模块
抓取昨日新增 star 最多的 10 个项目
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from utils import fetch_json, get_headers, format_number, truncate_text


def fetch_github_trending() -> List[Dict[str, Any]]:
    """
    抓取 GitHub 热门项目
    使用 GitHub Search API 获取昨日创建的项目，按 star 数排序
    """
    # 计算昨天的日期
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    
    # GitHub Search API 查询
    # 搜索昨天创建的项目，按 star 数降序排序
    query = f"created:>{date_str} stars:>10"
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=20"
    
    headers = get_headers()
    headers['Accept'] = 'application/vnd.github.v3+json'
    
    data = fetch_json(url, headers=headers)
    
    if not data or 'items' not in data:
        print("Failed to fetch GitHub trending data")
        return []
    
    projects = []
    
    for item in data['items'][:15]:  # 获取 15 个，后续去重可能减少
        try:
            # 提取项目信息
            project = {
                'title': item.get('full_name', ''),
                'url': item.get('html_url', ''),
                'description': item.get('description', ''),
                'language': item.get('language', ''),
                'stars': item.get('stargazers_count', 0),
                'forks': item.get('forks_count', 0),
                'watchers': item.get('watchers_count', 0),
                'created_at': item.get('created_at', ''),
                'updated_at': item.get('updated_at', ''),
                'topics': item.get('topics', []),
                'license': item.get('license', {}).get('name', '') if item.get('license') else '',
                'homepage': item.get('homepage', ''),
                'open_issues': item.get('open_issues_count', 0),
                'default_branch': item.get('default_branch', 'main'),
                'source': 'GitHub',
                'category': 'github'
            }
            
            # 格式化 star 数
            project['stars_formatted'] = format_number(project['stars'])
            
            # 截断描述
            project['description'] = truncate_text(project['description'], 200)
            
            projects.append(project)
            
        except Exception as e:
            print(f"Error processing GitHub project: {e}")
            continue
    
    # 按 star 数排序
    projects.sort(key=lambda x: x.get('stars', 0), reverse=True)
    
    # 只返回前 10 个
    return projects[:10]


def fetch_github_trending_by_language(language: str = '') -> List[Dict[str, Any]]:
    """
    按语言筛选 GitHub 热门项目
    """
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    
    # 构建查询
    query = f"created:>{date_str} stars:>10"
    if language:
        query += f" language:{language}"
    
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=20"
    
    headers = get_headers()
    headers['Accept'] = 'application/vnd.github.v3+json'
    
    data = fetch_json(url, headers=headers)
    
    if not data or 'items' not in data:
        return []
    
    projects = []
    
    for item in data['items'][:15]:
        try:
            project = {
                'title': item.get('full_name', ''),
                'url': item.get('html_url', ''),
                'description': item.get('description', ''),
                'language': item.get('language', ''),
                'stars': item.get('stargazers_count', 0),
                'forks': item.get('forks_count', 0),
                'created_at': item.get('created_at', ''),
                'source': 'GitHub',
                'category': 'github'
            }
            
            project['stars_formatted'] = format_number(project['stars'])
            project['description'] = truncate_text(project['description'], 200)
            
            projects.append(project)
            
        except Exception as e:
            continue
    
    projects.sort(key=lambda x: x.get('stars', 0), reverse=True)
    
    return projects[:10]


def format_github_markdown(projects: List[Dict[str, Any]], date: str = None) -> str:
    """
    格式化为 Markdown
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    lines = [
        f"# 🔥 GitHub 热门项目 - {date}",
        "",
        f"昨日新增 star 最多的 {len(projects)} 个项目",
        "",
        "---",
        ""
    ]
    
    for i, project in enumerate(projects, 1):
        lines.extend([
            f"## {i}. [{project['title']}]({project['url']})",
            "",
            f"⭐ **{project['stars_formatted']}** stars | 🍴 {project.get('forks', 0)} forks",
            "",
            f"**语言**: {project.get('language', '未知')}",
            "",
            f"**描述**: {project.get('description', '无描述')}",
            ""
        ])
        
        # 添加 topics
        if project.get('topics'):
            topics_str = ' '.join([f"`{t}`" for t in project['topics'][:5]])
            lines.append(f"**标签**: {topics_str}")
            lines.append("")
        
        # 添加 homepage
        if project.get('homepage'):
            lines.append(f"**主页**: [{project['homepage']}]({project['homepage']})")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return '\n'.join(lines)


def main():
    """
    主函数（用于测试）
    """
    print("正在抓取 GitHub 热门项目...")
    projects = fetch_github_trending()
    
    if projects:
        print(f"成功获取 {len(projects)} 个项目")
        
        # 生成 Markdown
        markdown = format_github_markdown(projects)
        
        # 保存到文件
        from utils import save_markdown, get_today_date
        filepath = f"data/{get_today_date()}/github-trending.md"
        save_markdown(markdown, filepath)
        print(f"已保存到 {filepath}")
        
        # 打印前 3 个
        print("\n前 3 个项目:")
        for i, project in enumerate(projects[:3], 1):
            print(f"{i}. {project['title']} - ⭐ {project['stars_formatted']}")
    else:
        print("未获取到项目")


if __name__ == '__main__':
    main()
