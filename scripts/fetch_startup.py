"""
创业投资新闻抓取模块（RSS/API 版本）
使用 RSS 源和公开 API，不依赖网页爬取
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import xml.etree.ElementTree as ET
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from utils import fetch_url, fetch_json, truncate_text, get_today_date


def _parse_rss(xml_text: str, source_name: str, base_url: str = '') -> List[Dict[str, Any]]:
    """通用 RSS 解析"""
    items = []
    try:
        root = ET.fromstring(xml_text)
        # 支持 RSS 2.0 和 Atom
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        # RSS 2.0: //channel/item
        for item in root.findall('.//item'):
            title = item.findtext('title', '').strip()
            link = item.findtext('link', '').strip()
            desc = item.findtext('description', '').strip()
            pub = item.findtext('pubDate', '').strip()
            if title:
                items.append({
                    'title': title,
                    'url': link,
                    'summary': truncate_text(re.sub(r'<[^>]+>', '', desc), 120),
                    'pub_time': pub,
                    'source': source_name,
                    'category': 'startup',
                    'type': 'investment'
                })
        # Atom: //entry
        for entry in root.findall('.//atom:entry', ns):
            title = entry.findtext('atom:title', '', ns).strip()
            link_el = entry.find('atom:link', ns)
            link = link_el.get('href', '') if link_el is not None else ''
            summary = entry.findtext('atom:summary', '', ns).strip()
            updated = entry.findtext('atom:updated', '', ns).strip()
            if title:
                items.append({
                    'title': title,
                    'url': link,
                    'summary': truncate_text(re.sub(r'<[^>]+>', '', summary), 120),
                    'pub_time': updated,
                    'source': source_name,
                    'category': 'startup',
                    'type': 'investment'
                })
    except Exception as e:
        print(f"  RSS parse error ({source_name}): {e}")
    return items


def fetch_36kr_rss() -> List[Dict[str, Any]]:
    """36氪 RSS"""
    xml = fetch_url("https://36kr.com/feed", timeout=15)
    if not xml:
        return []
    return _parse_rss(xml, '36氪')


def fetch_hackernews() -> List[Dict[str, Any]]:
    """Hacker News 创业相关 Top Stories"""
    data = fetch_json("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not data:
        return []
    items = []
    startup_kw = ['startup', 'founder', 'launch', 'fund', 'invest', 'saas', 'mvp', 'revenue', 'bootstr', 'y combinator', 'seed']
    for sid in data[:60]:
        story = fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
        if not story or story.get('type') != 'story':
            continue
        title = story.get('title', '')
        text = title.lower()
        if any(kw in text for kw in startup_kw):
            url = story.get('url', f"https://news.ycombinator.com/item?id={sid}")
            items.append({
                'title': title,
                'url': url,
                'summary': '',
                'pub_time': '',
                'source': 'Hacker News',
                'category': 'startup',
                'type': 'investment'
            })
        if len(items) >= 10:
            break
    return items


def fetch_producthunt() -> List[Dict[str, Any]]:
    """Product Hunt 每日热门"""
    xml = fetch_url("https://www.producthunt.com/feed", timeout=15)
    if not xml:
        return []
    return _parse_rss(xml, 'Product Hunt')


def fetch_startup_news() -> List[Dict[str, Any]]:
    """抓取创业投资新闻"""
    all_news = []
    sources = [
        ('36氪 RSS', fetch_36kr_rss),
        ('Hacker News', fetch_hackernews),
        ('Product Hunt', fetch_producthunt),
    ]
    for name, func in sources:
        try:
            print(f"正在抓取 {name}...")
            news = func()
            if news:
                all_news.extend(news)
                print(f"  成功获取 {len(news)} 条")
            else:
                print(f"  未获取到")
        except Exception as e:
            print(f"  抓取失败: {e}")

    seen = set()
    unique = []
    for n in all_news:
        if n['title'] not in seen:
            seen.add(n['title'])
            unique.append(n)
    return unique[:10]


def format_startup_markdown(news_list: List[Dict[str, Any]], date: str = None) -> str:
    if date is None:
        date = get_today_date()
    lines = [f"# 💼 创业投资新闻 - {date}", "", f"今日 {len(news_list)} 条", "", "---", ""]
    for i, n in enumerate(news_list, 1):
        lines.extend([f"## {i}. [{n['title']}]({n['url']})", f"**来源**: {n.get('source', '')}", ""])
        if n.get('summary'):
            lines.extend([f"**摘要**: {n['summary']}", ""])
        lines.extend(["---", ""])
    return '\n'.join(lines)


if __name__ == '__main__':
    news = fetch_startup_news()
    print(f"\n共 {len(news)} 条")
    for n in news[:3]:
        print(f"  {n['source']}: {n['title']}")
