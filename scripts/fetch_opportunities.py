"""
小成本创业机会抓取模块
使用多个来源，覆盖独立开发者、副业、低成本创业
"""

from typing import List, Dict, Any
import xml.etree.ElementTree as ET
import re
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
            img = ''
            enclosure = item.find('enclosure')
            if enclosure is not None:
                img = enclosure.get('url', '')
            if not img:
                m = re.search(r'<img[^>]+src=["\']([^"\']+)', desc)
                if m:
                    img = m.group(1)
            if title:
                items.append({
                    'title': title,
                    'url': link,
                    'summary': truncate_text(re.sub(r'<[^>]+>', '', desc), 150),
                    'pub_time': '',
                    'source': source_name,
                    'category': 'opportunity',
                    'type': 'low_cost',
                    'image': img
                })
    except Exception as e:
        print(f"  RSS parse error ({source_name}): {e}")
    return items


def fetch_hn_show() -> List[Dict[str, Any]]:
    """Hacker News Show HN - 独立开发者项目"""
    data = fetch_json("https://hacker-news.firebaseio.com/v0/showstories.json")
    if not data:
        return []
    items = []
    for sid in data[:50]:
        story = fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
        if not story:
            continue
        title = story.get('title', '')
        url = story.get('url', f"https://news.ycombinator.com/item?id={sid}")
        text = story.get('text', '')
        summary = truncate_text(re.sub(r'<[^>]+>', '', text), 150) if text else ''
        items.append({
            'title': title,
            'url': url,
            'summary': summary,
            'pub_time': '',
            'source': 'Show HN',
            'category': 'opportunity',
            'type': 'low_cost',
            'image': ''
        })
        if len(items) >= 10:
            break
    return items


def fetch_v2ex_innovate() -> List[Dict[str, Any]]:
    """V2EX 创意/项目节点"""
    xml = fetch_url("https://www.v2ex.com/feed/tab/create.xml", timeout=15)
    if not xml:
        return []
    return _parse_rss(xml, 'V2EX')


def fetch_indiehackers_rss() -> List[Dict[str, Any]]:
    """IndieHackers"""
    # 尝试 RSS
    xml = fetch_url("https://www.indiehackers.com/feed", timeout=15)
    if xml and '<rss' in xml:
        return _parse_rss(xml, 'IndieHackers')
    # 回退到 HN 中 indie 相关内容
    return []


def fetch_reddit_sideproject() -> List[Dict[str, Any]]:
    """Reddit r/SideProject - 副业项目"""
    data = fetch_json(
        "https://www.reddit.com/r/SideProject/hot.json?limit=15",
        headers={'User-Agent': 'DailyNewsBot/1.0'},
        timeout=15
    )
    if not data or 'data' not in data:
        return []
    items = []
    for child in data['data'].get('children', []):
        post = child.get('data', {})
        title = post.get('title', '')
        url = post.get('url', '')
        if 'reddit.com' in url:
            url = f"https://reddit.com{post.get('permalink', '')}"
        selftext = post.get('selftext', '')
        summary = truncate_text(selftext, 150) if selftext else ''
        thumbnail = post.get('thumbnail', '')
        if thumbnail and thumbnail.startswith('http'):
            pass  # 有缩略图
        else:
            thumbnail = ''
        items.append({
            'title': title,
            'url': url,
            'summary': summary,
            'pub_time': '',
            'source': 'Reddit/SideProject',
            'category': 'opportunity',
            'type': 'low_cost',
            'image': thumbnail
        })
    return items[:10]


def fetch_producthunt_topics() -> List[Dict[str, Any]]:
    """Product Hunt - maker 相关"""
    xml = fetch_url("https://www.producthunt.com/feed", timeout=15)
    if not xml:
        return []
    items = _parse_rss(xml, 'Product Hunt')
    return items[:10]


def fetch_opportunities() -> List[Dict[str, Any]]:
    all_news = []
    sources = [
        ('Show HN', fetch_hn_show),
        ('Reddit/SideProject', fetch_reddit_sideproject),
        ('V2EX', fetch_v2ex_innovate),
        ('Product Hunt', fetch_producthunt_topics),
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


def format_opportunities_markdown(news_list: List[Dict[str, Any]], date: str = None) -> str:
    if date is None:
        date = get_today_date()
    lines = [f"# 💰 小成本创业机会 - {date}", "", f"今日 {len(news_list)} 条", "", "---", ""]
    for i, n in enumerate(news_list, 1):
        lines.extend([f"## {i}. [{n['title']}]({n['url']})", f"**来源**: {n.get('source', '')}", ""])
        if n.get('image'):
            lines.extend([f"![img]({n['image']})", ""])
        if n.get('summary'):
            lines.extend([f"**摘要**: {n['summary']}", ""])
        lines.extend(["---", ""])
    return '\n'.join(lines)


if __name__ == '__main__':
    opps = fetch_opportunities()
    print(f"\n共 {len(opps)} 条")
    for o in opps[:3]:
        print(f"  {o['source']}: {o['title']}")
