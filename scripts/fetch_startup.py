"""
创业投资新闻抓取模块
使用 RSS 源 + 公开 API + 可靠的中文网站
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import xml.etree.ElementTree as ET
import re
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from utils import fetch_url, fetch_json, truncate_text, get_today_date


def _parse_rss(xml_text: str, source_name: str) -> List[Dict[str, Any]]:
    items = []
    try:
        root = ET.fromstring(xml_text)
        for item in root.findall('.//item'):
            title = item.findtext('title', '').strip()
            link = item.findtext('link', '').strip()
            desc = item.findtext('description', '').strip()
            pub = item.findtext('pubDate', '').strip()
            # 提取 RSS 中的图片
            img = ''
            enclosure = item.find('enclosure')
            if enclosure is not None:
                img = enclosure.get('url', '')
            # 有些 RSS 在 description 里嵌 <img>
            if not img:
                m = re.search(r'<img[^>]+src=["\']([^"\']+)', desc)
                if m:
                    img = m.group(1)
            if title:
                items.append({
                    'title': title,
                    'url': link,
                    'summary': truncate_text(re.sub(r'<[^>]+>', '', desc), 150),
                    'pub_time': pub,
                    'source': source_name,
                    'category': 'startup',
                    'type': 'investment',
                    'image': img
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


def fetch_36kr_api() -> List[Dict[str, Any]]:
    """36氪 API（更可靠）"""
    data = fetch_json(
        "https://gateway.36kr.com/api/newsflash/catalog?per_page=20",
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://36kr.com/newsflashes'
        },
        timeout=15
    )
    if not data or not data.get('data', {}).get('items'):
        return []
    items = []
    for item in data['data']['items']:
        title = item.get('title', '')
        news_id = item.get('id', '')
        desc = item.get('description', '') or item.get('summary', '')
        img = item.get('cover', '') or item.get('material', {}).get('cover', '') if isinstance(item.get('material'), dict) else ''
        if title:
            items.append({
                'title': title,
                'url': f"https://36kr.com/newsflashes/{news_id}",
                'summary': truncate_text(re.sub(r'<[^>]+>', '', desc), 150),
                'pub_time': item.get('published_at', ''),
                'source': '36氪',
                'category': 'startup',
                'type': 'investment',
                'image': img
            })
    return items[:15]


def fetch_hackernews() -> List[Dict[str, Any]]:
    """Hacker News 创业相关"""
    data = fetch_json("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not data:
        return []
    items = []
    kw = ['startup', 'founder', 'launch', 'fund', 'invest', 'saas', 'mvp',
          'revenue', 'bootstr', 'y combinator', 'seed', 'series', 'venture',
          'billion', 'million', 'profit', 'growth', 'acqui']
    for sid in data[:80]:
        story = fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
        if not story or story.get('type') != 'story':
            continue
        title = story.get('title', '')
        if any(kw in title.lower() for kw in kw):
            url = story.get('url', f"https://news.ycombinator.com/item?id={sid}")
            items.append({
                'title': title,
                'url': url,
                'summary': '',
                'pub_time': '',
                'source': 'Hacker News',
                'category': 'startup',
                'type': 'investment',
                'image': ''
            })
        if len(items) >= 10:
            break
    return items


def fetch_producthunt() -> List[Dict[str, Any]]:
    """Product Hunt 每日热门"""
    xml = fetch_url("https://www.producthunt.com/feed", timeout=15)
    if not xml:
        return []
    items = _parse_rss(xml, 'Product Hunt')
    # PH 的 RSS 通常没有图片，但链接质量高
    return items


def fetch_techcrunch_rss() -> List[Dict[str, Any]]:
    """TechCrunch 创投"""
    xml = fetch_url("https://techcrunch.com/category/venture/feed/", timeout=15)
    if not xml:
        return []
    return _parse_rss(xml, 'TechCrunch')


def fetch_startup_news() -> List[Dict[str, Any]]:
    """抓取创业投资新闻"""
    all_news = []
    sources = [
        ('36氪 API', fetch_36kr_api),
        ('36氪 RSS', fetch_36kr_rss),
        ('Product Hunt', fetch_producthunt),
        ('TechCrunch', fetch_techcrunch_rss),
        ('Hacker News', fetch_hackernews),
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
        img = n.get('image', '')
        lines.extend([f"## {i}. [{n['title']}]({n['url']})", f"**来源**: {n.get('source', '')}", ""])
        if img:
            lines.extend([f"![img]({img})", ""])
        if n.get('summary'):
            lines.extend([f"**摘要**: {n['summary']}", ""])
        lines.extend(["---", ""])
    return '\n'.join(lines)


if __name__ == '__main__':
    news = fetch_startup_news()
    print(f"\n共 {len(news)} 条")
    for n in news[:3]:
        print(f"  {n['source']}: {n['title']}")
