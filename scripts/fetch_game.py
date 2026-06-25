"""
游戏设计灵感抓取模块
覆盖更多来源：GameDev、Steam、itch.io、IndieDB、触乐、游研社
"""

from typing import List, Dict, Any
import xml.etree.ElementTree as ET
import re
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from utils import fetch_url, fetch_json, truncate_text, get_today_date
from bs4 import BeautifulSoup


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
                    'category': 'game',
                    'type': classify_type(title, desc),
                    'image': img
                })
    except Exception as e:
        print(f"  RSS parse error ({source_name}): {e}")
    return items


def classify_type(title: str, summary: str) -> str:
    text = f"{title} {summary}".lower()
    if any(kw in text for kw in ['玩法', '机制', '创新', 'gameplay', 'mechanic', 'design', 'level', '关卡']):
        return 'gameplay'
    if any(kw in text for kw in ['美术', '风格', '画面', 'art', 'visual', 'pixel', '像素', '3d model']):
        return 'art'
    if any(kw in text for kw in ['叙事', '剧情', '故事', 'narrative', 'story', 'writing', '剧本']):
        return 'narrative'
    if any(kw in text for kw in ['技术', '引擎', 'unity', 'unreal', 'godot', 'shader', '编程']):
        return 'tech'
    if any(kw in text for kw in ['独立', 'indie', 'solo', '小团队']):
        return 'indie'
    return 'general'


def fetch_gamedev_rss() -> List[Dict[str, Any]]:
    """GameDev.net RSS"""
    xml = fetch_url("https://www.gamedev.net/rss/", timeout=15)
    if not xml:
        return []
    return _parse_rss(xml, 'GameDev.net')


def fetch_gamedev_news_api() -> List[Dict[str, Any]]:
    """GameDev.net 新闻（HTML 解析）"""
    html = fetch_url("https://www.gamedev.net/news/", timeout=15)
    if not html:
        return []
    items = []
    try:
        soup = BeautifulSoup(html, 'lxml')
        for card in soup.select('.a-project-card, .content-item, article')[:15]:
            title_el = card.select_one('h2 a, h3 a, .title a, a.title')
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link = title_el.get('href', '')
            if link and not link.startswith('http'):
                link = f"https://www.gamedev.net{link}"
            desc_el = card.select_one('.desc, .summary, p')
            desc = desc_el.get_text(strip=True) if desc_el else ''
            img_el = card.select_one('img')
            img = img_el.get('src', '') if img_el else ''
            items.append({
                'title': title, 'url': link,
                'summary': truncate_text(desc, 150),
                'pub_time': '', 'source': 'GameDev.net',
                'category': 'game', 'type': classify_type(title, desc),
                'image': img
            })
    except Exception as e:
        print(f"  GameDev parse error: {e}")
    return items


def fetch_indiedb_rss() -> List[Dict[str, Any]]:
    """IndieDB RSS"""
    xml = fetch_url("https://www.indiedb.com/rss/news", timeout=15)
    if not xml:
        return []
    return _parse_rss(xml, 'IndieDB')


def fetch_steam_newreleases() -> List[Dict[str, Any]]:
    """Steam 新品"""
    data = fetch_json(
        "https://store.steampowered.com/api/featuredcategories?cc=cn",
        timeout=15
    )
    if not data:
        return []
    items = []
    for key in ['new_releases', 'top_sellers', 'specials', 'upcoming']:
        for item in data.get(key, {}).get('items', [])[:5]:
            name = item.get('name', '')
            id_ = item.get('id', '')
            url = f"https://store.steampowered.com/app/{id_}" if id_ else ''
            desc = item.get('short_description', '')
            # Steam 有 header_image
            img = item.get('header_image', '')
            items.append({
                'title': name, 'url': url,
                'summary': truncate_text(desc, 150),
                'pub_time': '', 'source': 'Steam',
                'category': 'game', 'type': classify_type(name, desc),
                'image': img
            })
    return items[:10]


def fetch_itchio_rss() -> List[Dict[str, Any]]:
    """itch.io 最新游戏（HTML 解析）"""
    html = fetch_url("https://itch.io/games/newest", timeout=15)
    if not html:
        return []
    items = []
    try:
        soup = BeautifulSoup(html, 'lxml')
        for game in soup.select('.game_cell')[:10]:
            title_el = game.select_one('.title')
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link_el = game.select_one('a.game_link')
            link = link_el.get('href', '') if link_el else ''
            desc_el = game.select_one('.game_text')
            desc = desc_el.get_text(strip=True) if desc_el else ''
            img_el = game.select_one('img.game_thumb, img')
            img = img_el.get('src', '') if img_el else ''
            items.append({
                'title': title, 'url': link,
                'summary': truncate_text(desc, 150),
                'pub_time': '', 'source': 'itch.io',
                'category': 'game', 'type': classify_type(title, desc),
                'image': img
            })
    except Exception as e:
        print(f"  itch.io parse error: {e}")
    return items


def fetch_chule_rss() -> List[Dict[str, Any]]:
    """触乐 RSS"""
    xml = fetch_url("https://www.chuapp.com/rss", timeout=15)
    if not xml or '<rss' not in xml:
        # 尝试备用
        xml = fetch_url("https://www.chuapp.com/feed", timeout=15)
    if not xml or '<rss' not in xml:
        return []
    return _parse_rss(xml, '触乐')


def fetch_yystv_rss() -> List[Dict[str, Any]]:
    """游研社 RSS"""
    xml = fetch_url("https://www.yystv.cn/rss/feed", timeout=15)
    if not xml or '<rss' not in xml:
        xml = fetch_url("https://www.yystv.cn/rss", timeout=15)
    if not xml or '<rss' not in xml:
        return []
    return _parse_rss(xml, '游研社')


def fetch_game_news() -> List[Dict[str, Any]]:
    all_news = []
    sources = [
        ('GameDev.net RSS', fetch_gamedev_rss),
        ('GameDev.net News', fetch_gamedev_news_api),
        ('IndieDB', fetch_indiedb_rss),
        ('Steam', fetch_steam_newreleases),
        ('itch.io', fetch_itchio_rss),
        ('触乐', fetch_chule_rss),
        ('游研社', fetch_yystv_rss),
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

    # 优先玩法创新
    gameplay = [n for n in unique if n.get('type') == 'gameplay']
    others = [n for n in unique if n.get('type') != 'gameplay']
    result = gameplay[:6] + others[:4]
    return result[:10]


def format_game_markdown(news_list: List[Dict[str, Any]], date: str = None) -> str:
    if date is None:
        date = get_today_date()
    type_labels = {
        'gameplay': '🎮 玩法创新', 'art': '🎨 视觉设计',
        'narrative': '📖 叙事设计', 'tech': '⚙️ 技术实现',
        'indie': '🎯 独立游戏', 'general': '📰 行业资讯'
    }
    lines = [f"# 🎮 游戏设计灵感 - {date}", "", f"今日 {len(news_list)} 条", "", "---", ""]
    for i, n in enumerate(news_list, 1):
        tag = type_labels.get(n.get('type', 'general'), '📰')
        lines.extend([f"## {i}. `#{tag}` [{n['title']}]({n['url']})", f"**来源**: {n.get('source', '')}", ""])
        if n.get('image'):
            lines.extend([f"![img]({n['image']})", ""])
        if n.get('summary'):
            lines.extend([f"**摘要**: {n['summary']}", ""])
        lines.extend(["---", ""])
    return '\n'.join(lines)


if __name__ == '__main__':
    news = fetch_game_news()
    print(f"\n共 {len(news)} 条")
    for n in news[:3]:
        print(f"  [{n.get('type')}] {n['source']}: {n['title']}")
