"""
创业投资新闻抓取模块
抓取创业投资领域的最新新闻
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from utils import fetch_url, get_headers, truncate_text, get_today_date


def fetch_36kr_news() -> List[Dict[str, Any]]:
    """
    抓取 36氪 创投新闻
    """
    url = "https://36kr.com/information/investment/"
    html = fetch_url(url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    news_list = []
    
    # 查找新闻列表
    articles = soup.find_all('div', class_='article-item')
    
    for article in articles[:15]:
        try:
            # 提取标题
            title_elem = article.find('a', class_='article-item-title')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            link = title_elem.get('href', '')
            if link and not link.startswith('http'):
                link = f"https://36kr.com{link}"
            
            # 提取摘要
            summary_elem = article.find('p', class_='article-item-description')
            summary = summary_elem.get_text(strip=True) if summary_elem else ''
            
            # 提取时间
            time_elem = article.find('span', class_='article-item-time')
            pub_time = time_elem.get_text(strip=True) if time_elem else ''
            
            # 提取来源
            source_elem = article.find('span', class_='article-item-source')
            source = source_elem.get_text(strip=True) if source_elem else '36氪'
            
            news = {
                'title': title,
                'url': link,
                'summary': truncate_text(summary, 200),
                'pub_time': pub_time,
                'source': source,
                'category': 'startup',
                'type': 'investment'
            }
            
            news_list.append(news)
            
        except Exception as e:
            print(f"Error processing 36kr article: {e}")
            continue
    
    return news_list


def fetch_itjuzi_news() -> List[Dict[str, Any]]:
    """
    抓取 IT桔子 投资新闻
    """
    url = "https://www.itjuzi.com/investevents"
    html = fetch_url(url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    news_list = []
    
    # 查找投资事件列表
    items = soup.find_all('div', class_='list-item')
    
    for item in items[:15]:
        try:
            # 提取标题
            title_elem = item.find('a', class_='title')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            link = title_elem.get('href', '')
            if link and not link.startswith('http'):
                link = f"https://www.itjuzi.com{link}"
            
            # 提取详情
            detail_elem = item.find('div', class_='detail')
            detail = detail_elem.get_text(strip=True) if detail_elem else ''
            
            # 提取时间
            time_elem = item.find('span', class_='time')
            pub_time = time_elem.get_text(strip=True) if time_elem else ''
            
            news = {
                'title': title,
                'url': link,
                'summary': truncate_text(detail, 200),
                'pub_time': pub_time,
                'source': 'IT桔子',
                'category': 'startup',
                'type': 'investment'
            }
            
            news_list.append(news)
            
        except Exception as e:
            continue
    
    return news_list


def fetch_cyzb_news() -> List[Dict[str, Any]]:
    """
    抓取 创业邦 新闻
    """
    url = "https://www.cyzone.cn/news/"
    html = fetch_url(url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    news_list = []
    
    # 查找新闻列表
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
                link = f"https://www.cyzone.cn{link}"
            
            # 提取摘要
            summary_elem = article.find('p', class_='summary')
            summary = summary_elem.get_text(strip=True) if summary_elem else ''
            
            # 提取时间
            time_elem = article.find('span', class_='time')
            pub_time = time_elem.get_text(strip=True) if time_elem else ''
            
            news = {
                'title': title,
                'url': link,
                'summary': truncate_text(summary, 200),
                'pub_time': pub_time,
                'source': '创业邦',
                'category': 'startup',
                'type': 'investment'
            }
            
            news_list.append(news)
            
        except Exception as e:
            continue
    
    return news_list


def fetch_tzj_news() -> List[Dict[str, Any]]:
    """
    抓取 投资界 新闻
    """
    url = "https://www.pedaily.cn/news"
    html = fetch_url(url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    news_list = []
    
    # 查找新闻列表
    articles = soup.find_all('div', class_='news-list-item')
    
    for article in articles[:15]:
        try:
            # 提取标题
            title_elem = article.find('a', class_='title')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            link = title_elem.get('href', '')
            if link and not link.startswith('http'):
                link = f"https://www.pedaily.cn{link}"
            
            # 提取摘要
            summary_elem = article.find('p', class_='summary')
            summary = summary_elem.get_text(strip=True) if summary_elem else ''
            
            # 提取时间
            time_elem = article.find('span', class_='time')
            pub_time = time_elem.get_text(strip=True) if time_elem else ''
            
            news = {
                'title': title,
                'url': link,
                'summary': truncate_text(summary, 200),
                'pub_time': pub_time,
                'source': '投资界',
                'category': 'startup',
                'type': 'investment'
            }
            
            news_list.append(news)
            
        except Exception as e:
            continue
    
    return news_list


def fetch_startup_news() -> List[Dict[str, Any]]:
    """
    抓取创业投资新闻（汇总多个来源）
    """
    all_news = []
    
    # 抓取各个来源
    sources = [
        ('36氪', fetch_36kr_news),
        ('IT桔子', fetch_itjuzi_news),
        ('创业邦', fetch_cyzb_news),
        ('投资界', fetch_tzj_news)
    ]
    
    for source_name, fetch_func in sources:
        try:
            print(f"正在抓取 {source_name}...")
            news = fetch_func()
            if news:
                all_news.extend(news)
                print(f"  成功获取 {len(news)} 条新闻")
            else:
                print(f"  未获取到新闻")
        except Exception as e:
            print(f"  抓取 {source_name} 失败: {e}")
    
    # 按时间排序（如果有时间信息）
    all_news.sort(key=lambda x: x.get('pub_time', ''), reverse=True)
    
    # 去重（基于标题）
    seen_titles = set()
    unique_news = []
    for news in all_news:
        title = news.get('title', '')
        if title not in seen_titles:
            seen_titles.add(title)
            unique_news.append(news)
    
    return unique_news[:10]


def format_startup_markdown(news_list: List[Dict[str, Any]], date: str = None) -> str:
    """
    格式化为 Markdown
    """
    if date is None:
        date = get_today_date()
    
    lines = [
        f"# 💼 创业投资新闻 - {date}",
        "",
        f"今日创业投资领域最新 {len(news_list)} 条新闻",
        "",
        "---",
        ""
    ]
    
    for i, news in enumerate(news_list, 1):
        lines.extend([
            f"## {i}. [{news['title']}]({news['url']})",
            "",
            f"**来源**: {news.get('source', '未知')}",
        ])
        
        if news.get('pub_time'):
            lines.append(f"**时间**: {news['pub_time']}")
        
        lines.append("")
        
        if news.get('summary'):
            lines.append(f"**摘要**: {news['summary']}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return '\n'.join(lines)


def main():
    """
    主函数（用于测试）
    """
    print("正在抓取创业投资新闻...")
    news_list = fetch_startup_news()
    
    if news_list:
        print(f"成功获取 {len(news_list)} 条新闻")
        
        # 生成 Markdown
        markdown = format_startup_markdown(news_list)
        
        # 保存到文件
        from utils import save_markdown, get_today_date
        filepath = f"data/{get_today_date()}/startup-news.md"
        save_markdown(markdown, filepath)
        print(f"已保存到 {filepath}")
        
        # 打印前 3 条
        print("\n前 3 条新闻:")
        for i, news in enumerate(news_list[:3], 1):
            print(f"{i}. {news['title']}")
    else:
        print("未获取到新闻")


if __name__ == '__main__':
    main()
