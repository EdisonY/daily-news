"""
游戏设计灵感抓取模块
抓取游戏设计相关的优秀方案和成果思路
重点关注玩法创新
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from utils import fetch_url, get_headers, truncate_text, get_today_date


def fetch_gamedev_news() -> List[Dict[str, Any]]:
    """
    抓取 GameDev.net 游戏开发社区内容
    """
    url = "https://www.gamedev.net/news/"
    html = fetch_url(url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    news_list = []
    
    # 查找文章列表
    articles = soup.find_all('div', class_='article-item')
    
    for article in articles[:15]:
        try:
            # 提取标题
            title_elem = article.find('a', class_='title')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            link = title_elem.get('href', '')
            if link and not link.startswith('http'):
                link = f"https://www.gamedev.net{link}"
            
            # 提取摘要
            summary_elem = article.find('p', class_='summary')
            summary = summary_elem.get_text(strip=True) if summary_elem else ''
            
            # 提取时间
            time_elem = article.find('span', class_='time')
            pub_time = time_elem.get_text(strip=True) if time_elem else ''
            
            # 判断文章类型
            article_type = classify_article_type(title, summary)
            
            news = {
                'title': title,
                'url': link,
                'summary': truncate_text(summary, 200),
                'pub_time': pub_time,
                'source': 'GameDev.net',
                'category': 'game',
                'type': article_type
            }
            
            news_list.append(news)
            
        except Exception as e:
            continue
    
    return news_list


def fetch_gamasutra_news() -> List[Dict[str, Any]]:
    """
    抓取 Gamasutra 游戏设计文章
    """
    url = "https://www.gamasutra.com/news/"
    html = fetch_url(url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    news_list = []
    
    # 查找文章列表
    articles = soup.find_all('div', class_='news-item')
    
    for article in articles[:15]:
        try:
            # 提取标题
            title_elem = article.find('a', class_='title')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            link = title_elem.get('href', '')
            if link and not link.startswith('http'):
                link = f"https://www.gamasutra.com{link}"
            
            # 提取摘要
            summary_elem = article.find('p', class_='summary')
            summary = summary_elem.get_text(strip=True) if summary_elem else ''
            
            # 提取时间
            time_elem = article.find('span', class_='time')
            pub_time = time_elem.get_text(strip=True) if time_elem else ''
            
            # 判断文章类型
            article_type = classify_article_type(title, summary)
            
            news = {
                'title': title,
                'url': link,
                'summary': truncate_text(summary, 200),
                'pub_time': pub_time,
                'source': 'Gamasutra',
                'category': 'game',
                'type': article_type
            }
            
            news_list.append(news)
            
        except Exception as e:
            continue
    
    return news_list


def fetch_indiedb_news() -> List[Dict[str, Any]]:
    """
    抓取 IndieDB 独立游戏新闻
    """
    url = "https://www.indiedb.com/news"
    html = fetch_url(url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    news_list = []
    
    # 查找新闻列表
    items = soup.find_all('div', class_='news-item')
    
    for item in items[:15]:
        try:
            # 提取标题
            title_elem = item.find('a', class_='title')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            link = title_elem.get('href', '')
            if link and not link.startswith('http'):
                link = f"https://www.indiedb.com{link}"
            
            # 提取摘要
            summary_elem = item.find('p', class_='summary')
            summary = summary_elem.get_text(strip=True) if summary_elem else ''
            
            # 提取时间
            time_elem = item.find('span', class_='time')
            pub_time = time_elem.get_text(strip=True) if time_elem else ''
            
            # 判断文章类型
            article_type = classify_article_type(title, summary)
            
            news = {
                'title': title,
                'url': link,
                'summary': truncate_text(summary, 200),
                'pub_time': pub_time,
                'source': 'IndieDB',
                'category': 'game',
                'type': article_type
            }
            
            news_list.append(news)
            
        except Exception as e:
            continue
    
    return news_list


def fetch_steam_newreleases() -> List[Dict[str, Any]]:
    """
    抓取 Steam 新品发布
    """
    url = "https://store.steampowered.com/explore/new/"
    html = fetch_url(url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    news_list = []
    
    # 查找新品列表
    items = soup.find_all('div', class_='newrelease_item')
    
    for item in items[:15]:
        try:
            # 提取标题
            title_elem = item.find('a', class_='title')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            link = title_elem.get('href', '')
            
            # 提取摘要
            summary_elem = item.find('p', class_='desc')
            summary = summary_elem.get_text(strip=True) if summary_elem else ''
            
            # 提取标签
            tags_elem = item.find('div', class_='tags')
            tags = tags_elem.get_text(strip=True) if tags_elem else ''
            
            # 判断文章类型
            article_type = classify_article_type(title, summary)
            
            news = {
                'title': title,
                'url': link,
                'summary': truncate_text(summary, 200),
                'pub_time': '',
                'source': 'Steam',
                'category': 'game',
                'type': article_type,
                'tags': tags
            }
            
            news_list.append(news)
            
        except Exception as e:
            continue
    
    return news_list


def fetch_chule_news() -> List[Dict[str, Any]]:
    """
    抓取触乐游戏设计文章
    """
    url = "https://www.chuapp.com/"
    html = fetch_url(url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    news_list = []
    
    # 查找文章列表
    articles = soup.find_all('div', class_='article-item')
    
    for article in articles[:15]:
        try:
            # 提取标题
            title_elem = article.find('a', class_='title')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            link = title_elem.get('href', '')
            if link and not link.startswith('http'):
                link = f"https://www.chuapp.com{link}"
            
            # 提取摘要
            summary_elem = article.find('p', class_='summary')
            summary = summary_elem.get_text(strip=True) if summary_elem else ''
            
            # 提取时间
            time_elem = article.find('span', class_='time')
            pub_time = time_elem.get_text(strip=True) if time_elem else ''
            
            # 判断文章类型
            article_type = classify_article_type(title, summary)
            
            news = {
                'title': title,
                'url': link,
                'summary': truncate_text(summary, 200),
                'pub_time': pub_time,
                'source': '触乐',
                'category': 'game',
                'type': article_type
            }
            
            news_list.append(news)
            
        except Exception as e:
            continue
    
    return news_list


def fetch_yyst_news() -> List[Dict[str, Any]]:
    """
    抓取游研社游戏设计文章
    """
    url = "https://www.yystv.cn/"
    html = fetch_url(url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    news_list = []
    
    # 查找文章列表
    articles = soup.find_all('div', class_='article-item')
    
    for article in articles[:15]:
        try:
            # 提取标题
            title_elem = article.find('a', class_='title')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            link = title_elem.get('href', '')
            if link and not link.startswith('http'):
                link = f"https://www.yystv.cn{link}"
            
            # 提取摘要
            summary_elem = article.find('p', class_='summary')
            summary = summary_elem.get_text(strip=True) if summary_elem else ''
            
            # 提取时间
            time_elem = article.find('span', class_='time')
            pub_time = time_elem.get_text(strip=True) if time_elem else ''
            
            # 判断文章类型
            article_type = classify_article_type(title, summary)
            
            news = {
                'title': title,
                'url': link,
                'summary': truncate_text(summary, 200),
                'pub_time': pub_time,
                'source': '游研社',
                'category': 'game',
                'type': article_type
            }
            
            news_list.append(news)
            
        except Exception as e:
            continue
    
    return news_list


def classify_article_type(title: str, summary: str) -> str:
    """
    根据标题和摘要判断文章类型
    返回：gameplay / art / narrative / tech / indie
    """
    text = f"{title} {summary}".lower()
    
    # 玩法创新相关关键词
    gameplay_keywords = ['玩法', '机制', '创新', '设计', 'gameplay', 'mechanic', 'innovation', 'design']
    # 美术风格相关关键词
    art_keywords = ['美术', '风格', '画面', '视觉', 'art', 'style', 'visual', 'graphics']
    # 叙事设计相关关键词
    narrative_keywords = ['叙事', '剧情', '故事', '世界观', 'narrative', 'story', 'plot', 'lore']
    # 技术实现相关关键词
    tech_keywords = ['技术', '引擎', '程序', '开发', 'tech', 'engine', 'programming', 'development']
    # 独立游戏相关关键词
    indie_keywords = ['独立', 'indie', '独立游戏', 'indie game']
    
    # 判断类型
    if any(keyword in text for keyword in gameplay_keywords):
        return 'gameplay'
    elif any(keyword in text for keyword in art_keywords):
        return 'art'
    elif any(keyword in text for keyword in narrative_keywords):
        return 'narrative'
    elif any(keyword in text for keyword in tech_keywords):
        return 'tech'
    elif any(keyword in text for keyword in indie_keywords):
        return 'indie'
    else:
        return 'general'


def fetch_game_news() -> List[Dict[str, Any]]:
    """
    抓取游戏设计灵感（汇总多个来源）
    """
    all_news = []
    
    # 抓取各个来源
    sources = [
        ('GameDev.net', fetch_gamedev_news),
        ('Gamasutra', fetch_gamasutra_news),
        ('IndieDB', fetch_indiedb_news),
        ('Steam', fetch_steam_newreleases),
        ('触乐', fetch_chule_news),
        ('游研社', fetch_yyst_news)
    ]
    
    for source_name, fetch_func in sources:
        try:
            print(f"正在抓取 {source_name}...")
            news = fetch_func()
            if news:
                all_news.extend(news)
                print(f"  成功获取 {len(news)} 条内容")
            else:
                print(f"  未获取到内容")
        except Exception as e:
            print(f"  抓取 {source_name} 失败: {e}")
    
    # 过滤游戏设计相关关键词
    game_keywords = ['游戏', '玩法', '设计', '开发', '独立', 'game', 'design', 'gameplay', 'indie']
    filtered_news = []
    
    for news in all_news:
        text = f"{news.get('title', '')} {news.get('summary', '')}"
        if any(keyword in text.lower() for keyword in game_keywords):
            filtered_news.append(news)
    
    # 按时间排序（如果有时间信息）
    filtered_news.sort(key=lambda x: x.get('pub_time', ''), reverse=True)
    
    # 去重（基于标题）
    seen_titles = set()
    unique_news = []
    for news in filtered_news:
        title = news.get('title', '')
        if title not in seen_titles:
            seen_titles.add(title)
            unique_news.append(news)
    
    # 优先保留玩法创新类型
    gameplay_news = [n for n in unique_news if n.get('type') == 'gameplay']
    other_news = [n for n in unique_news if n.get('type') != 'gameplay']
    
    # 混合结果，确保玩法创新占一定比例
    result = []
    gameplay_count = min(5, len(gameplay_news))
    other_count = 10 - gameplay_count
    
    result.extend(gameplay_news[:gameplay_count])
    result.extend(other_news[:other_count])
    
    return result[:10]


def format_game_markdown(news_list: List[Dict[str, Any]], date: str = None) -> str:
    """
    格式化为 Markdown
    """
    if date is None:
        date = get_today_date()
    
    # 统计类型分布
    type_counts = {}
    for news in news_list:
        article_type = news.get('type', 'general')
        type_counts[article_type] = type_counts.get(article_type, 0) + 1
    
    type_labels = {
        'gameplay': '🎮 玩法创新',
        'art': '🎨 美术风格',
        'narrative': '📖 叙事设计',
        'tech': '⚙️ 技术实现',
        'indie': '🎯 独立游戏',
        'general': '📰 综合'
    }
    
    lines = [
        f"# 🎮 游戏设计灵感 - {date}",
        "",
        f"今日发现 {len(news_list)} 条游戏设计相关内容",
        "",
        "**类型分布**:",
    ]
    
    for article_type, count in type_counts.items():
        label = type_labels.get(article_type, article_type)
        lines.append(f"- {label}: {count} 条")
    
    lines.extend(["", "---", ""])
    
    for i, news in enumerate(news_list, 1):
        article_type = news.get('type', 'general')
        type_label = type_labels.get(article_type, article_type)
        
        lines.extend([
            f"## {i}. [{news['title']}]({news['url']})",
            "",
            f"**类型**: {type_label}",
            f"**来源**: {news.get('source', '未知')}",
        ])
        
        if news.get('pub_time'):
            lines.append(f"**时间**: {news['pub_time']}")
        
        lines.append("")
        
        if news.get('summary'):
            lines.append(f"**摘要**: {news['summary']}")
            lines.append("")
        
        if news.get('tags'):
            lines.append(f"**标签**: {news['tags']}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return '\n'.join(lines)


def main():
    """
    主函数（用于测试）
    """
    print("正在抓取游戏设计灵感...")
    news_list = fetch_game_news()
    
    if news_list:
        print(f"成功获取 {len(news_list)} 条内容")
        
        # 生成 Markdown
        markdown = format_game_markdown(news_list)
        
        # 保存到文件
        from utils import save_markdown, get_today_date
        filepath = f"data/{get_today_date()}/game-design.md"
        save_markdown(markdown, filepath)
        print(f"已保存到 {filepath}")
        
        # 打印前 3 条
        print("\n前 3 条内容:")
        for i, news in enumerate(news_list[:3], 1):
            print(f"{i}. [{news.get('type', 'general')}] {news['title']}")
    else:
        print("未获取到内容")


if __name__ == '__main__':
    main()
