"""
小成本投资创业机会抓取模块
抓取低成本、轻创业相关的信息和机会
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from utils import fetch_url, get_headers, truncate_text, get_today_date


def fetch_36kr_opportunities() -> List[Dict[str, Any]]:
    """
    抓取 36氪 低成本创业相关内容
    """
    # 搜索低成本创业相关文章
    url = "https://36kr.com/search/articles/低成本创业"
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
            
            news = {
                'title': title,
                'url': link,
                'summary': truncate_text(summary, 200),
                'pub_time': pub_time,
                'source': '36氪',
                'category': 'opportunity',
                'type': 'low_cost'
            }
            
            news_list.append(news)
            
        except Exception as e:
            continue
    
    return news_list


def fetch_zhihu_opportunities() -> List[Dict[str, Any]]:
    """
    抓取知乎 低成本创业相关问题和回答
    """
    # 搜索知乎相关问题
    url = "https://www.zhihu.com/search?type=content&q=低成本创业"
    html = fetch_url(url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    news_list = []
    
    # 查找搜索结果
    items = soup.find_all('div', class_='SearchResult-Card')
    
    for item in items[:15]:
        try:
            # 提取标题
            title_elem = item.find('h2', class_='ContentItem-title')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            
            # 提取链接
            link_elem = title_elem.find('a')
            link = link_elem.get('href', '') if link_elem else ''
            if link and not link.startswith('http'):
                link = f"https://www.zhihu.com{link}"
            
            # 提取摘要
            summary_elem = item.find('span', class_='RichText')
            summary = summary_elem.get_text(strip=True) if summary_elem else ''
            
            news = {
                'title': title,
                'url': link,
                'summary': truncate_text(summary, 200),
                'pub_time': '',
                'source': '知乎',
                'category': 'opportunity',
                'type': 'low_cost'
            }
            
            news_list.append(news)
            
        except Exception as e:
            continue
    
    return news_list


def fetch_xiaohongshu_opportunities() -> List[Dict[str, Any]]:
    """
    抓取小红书 低成本创业相关内容
    """
    # 注意：小红书有反爬机制，实际使用可能需要更复杂的处理
    url = "https://www.xiaohongshu.com/search_result?keyword=低成本创业"
    html = fetch_url(url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    news_list = []
    
    # 查找笔记列表
    items = soup.find_all('div', class_='note-item')
    
    for item in items[:15]:
        try:
            # 提取标题
            title_elem = item.find('a', class_='title')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            link = title_elem.get('href', '')
            if link and not link.startswith('http'):
                link = f"https://www.xiaohongshu.com{link}"
            
            # 提取摘要
            summary_elem = item.find('p', class_='desc')
            summary = summary_elem.get_text(strip=True) if summary_elem else ''
            
            news = {
                'title': title,
                'url': link,
                'summary': truncate_text(summary, 200),
                'pub_time': '',
                'source': '小红书',
                'category': 'opportunity',
                'type': 'low_cost'
            }
            
            news_list.append(news)
            
        except Exception as e:
            continue
    
    return news_list


def fetch_indiehackers_opportunities() -> List[Dict[str, Any]]:
    """
    抓取 IndieHackers 低成本创业案例
    """
    url = "https://www.indiehackers.com/"
    html = fetch_url(url)
    
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    news_list = []
    
    # 查找帖子列表
    items = soup.find_all('div', class_='post-item')
    
    for item in items[:15]:
        try:
            # 提取标题
            title_elem = item.find('a', class_='title')
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            link = title_elem.get('href', '')
            if link and not link.startswith('http'):
                link = f"https://www.indiehackers.com{link}"
            
            # 提取摘要
            summary_elem = item.find('p', class_='summary')
            summary = summary_elem.get_text(strip=True) if summary_elem else ''
            
            news = {
                'title': title,
                'url': link,
                'summary': truncate_text(summary, 200),
                'pub_time': '',
                'source': 'IndieHackers',
                'category': 'opportunity',
                'type': 'low_cost'
            }
            
            news_list.append(news)
            
        except Exception as e:
            continue
    
    return news_list


def fetch_opportunities() -> List[Dict[str, Any]]:
    """
    抓取小成本创业机会（汇总多个来源）
    """
    all_news = []
    
    # 抓取各个来源
    sources = [
        ('36氪', fetch_36kr_opportunities),
        ('知乎', fetch_zhihu_opportunities),
        ('小红书', fetch_xiaohongshu_opportunities),
        ('IndieHackers', fetch_indiehackers_opportunities)
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
    
    # 过滤关键词（确保与低成本创业相关）
    keywords = ['低成本', '小投入', '副业', '轻创业', '0成本', '个人创业', '小本', '万元', '千元', '免费']
    filtered_news = []
    
    for news in all_news:
        text = f"{news.get('title', '')} {news.get('summary', '')}"
        if any(keyword in text for keyword in keywords):
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
    
    return unique_news[:10]


def format_opportunities_markdown(news_list: List[Dict[str, Any]], date: str = None) -> str:
    """
    格式化为 Markdown
    """
    if date is None:
        date = get_today_date()
    
    lines = [
        f"# 💰 小成本创业机会 - {date}",
        "",
        f"今日发现 {len(news_list)} 个低成本创业机会",
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
    print("正在抓取小成本创业机会...")
    news_list = fetch_opportunities()
    
    if news_list:
        print(f"成功获取 {len(news_list)} 个机会")
        
        # 生成 Markdown
        markdown = format_opportunities_markdown(news_list)
        
        # 保存到文件
        from utils import save_markdown, get_today_date
        filepath = f"data/{get_today_date()}/startup-opportunities.md"
        save_markdown(markdown, filepath)
        print(f"已保存到 {filepath}")
        
        # 打印前 3 个
        print("\n前 3 个机会:")
        for i, news in enumerate(news_list[:3], 1):
            print(f"{i}. {news['title']}")
    else:
        print("未获取到机会")


if __name__ == '__main__':
    main()
