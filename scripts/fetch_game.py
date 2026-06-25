"""
游戏设计灵感抓取模块
重点：玩法创新、机制设计、独立游戏创意
来源覆盖：英文技术站 + 中文游戏媒体 + Reddit/HN 游戏讨论
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
                    'summary': truncate_text(re.sub(r'<[^>]+>', '', desc), 200),
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
    if any(kw in text for kw in ['玩法', '机制', '创新', 'gameplay', 'mechanic', 'design',
                                   'level', '关卡', 'roguelike', 'puzzle', 'platformer',
                                   'turn-based', 'real-time', 'combat', 'battle', 'interaction']):
        return 'gameplay'
    if any(kw in text for kw in ['美术', '风格', '画面', 'art', 'visual', 'pixel', '像素',
                                   '3d', 'animation', 'shader', 'vfx', '特效']):
        return 'art'
    if any(kw in text for kw in ['叙事', '剧情', '故事', 'narrative', 'story', 'writing',
                                   'worldbuilding', '剧本', 'dialogue']):
        return 'narrative'
    if any(kw in text for kw in ['技术', '引擎', 'unity', 'unreal', 'godot', 'shader',
                                   '编程', 'coding', 'procedural', 'optimization']):
        return 'tech'
    if any(kw in text for kw in ['独立', 'indie', 'solo', '小团队', 'jam', 'gamejam']):
        return 'indie'
    return 'general'


# ========== 英文来源 ==========

def fetch_gamedev_rss() -> List[Dict[str, Any]]:
    """GameDev.net RSS"""
    xml = fetch_url("https://www.gamedev.net/rss/", timeout=15)
    return _parse_rss(xml, 'GameDev.net') if xml else []


def fetch_gamasutra_rss() -> List[Dict[str, Any]]:
    """Gamasutra (Game Developer) RSS"""
    xml = fetch_url("https://www.gamedeveloper.com/rss.xml", timeout=15)
    return _parse_rss(xml, 'Game Developer') if xml else []


def fetch_indiedb_rss() -> List[Dict[str, Any]]:
    """IndieDB RSS"""
    xml = fetch_url("https://www.indiedb.com/rss/news", timeout=15)
    return _parse_rss(xml, 'IndieDB') if xml else []


def fetch_steam_newreleases() -> List[Dict[str, Any]]:
    """Steam 新品+热门"""
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
            img = item.get('header_image', '')
            items.append({
                'title': name, 'url': url,
                'summary': truncate_text(desc, 200),
                'pub_time': '', 'source': 'Steam',
                'category': 'game', 'type': classify_type(name, desc),
                'image': img
            })
    return items[:10]


def fetch_itchio_newest() -> List[Dict[str, Any]]:
    """itch.io 最新游戏"""
    html = fetch_url("https://itch.io/games/newest", timeout=15)
    if not html:
        return []
    items = []
    try:
        soup = BeautifulSoup(html, 'lxml')
        for game in soup.select('.game_cell')[:15]:
            title_el = game.select_one('.title')
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link_el = game.select_one('a.game_link')
            link = link_el.get('href', '') if link_el else ''
            desc_el = game.select_one('.game_text')
            desc = desc_el.get_text(strip=True) if desc_el else ''
            img_el = game.select_one('img')
            # itch.io 用 data-lazy_src 做懒加载
            img = ''
            if img_el:
                img = img_el.get('data-lazy_src', '') or img_el.get('src', '')
            items.append({
                'title': title, 'url': link,
                'summary': truncate_text(desc, 200),
                'pub_time': '', 'source': 'itch.io',
                'category': 'game', 'type': classify_type(title, desc),
                'image': img
            })
    except Exception as e:
        print(f"  itch.io parse error: {e}")
    return items


def fetch_itchio_top_rated() -> List[Dict[str, Any]]:
    """itch.io 高评分游戏"""
    html = fetch_url("https://itch.io/games/top-rated", timeout=15)
    if not html:
        return []
    items = []
    try:
        soup = BeautifulSoup(html, 'lxml')
        for game in soup.select('.game_cell')[:15]:
            title_el = game.select_one('.title')
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link_el = game.select_one('a.game_link')
            link = link_el.get('href', '') if link_el else ''
            desc_el = game.select_one('.game_text')
            desc = desc_el.get_text(strip=True) if desc_el else ''
            img_el = game.select_one('img')
            img = ''
            if img_el:
                img = img_el.get('data-lazy_src', '') or img_el.get('src', '')
            items.append({
                'title': title, 'url': link,
                'summary': truncate_text(desc, 200),
                'pub_time': '', 'source': 'itch.io Top Rated',
                'category': 'game', 'type': classify_type(title, desc),
                'image': img
            })
    except Exception:
        pass
    return items


def fetch_itchio_game_design_jam() -> List[Dict[str, Any]]:
    """itch.io Game Design 相关"""
    html = fetch_url("https://itch.io/game-assets/tag-game-design", timeout=15)
    if not html:
        return []
    items = []
    try:
        soup = BeautifulSoup(html, 'lxml')
        for game in soup.select('.game_cell, .game_cell_with_cover')[:10]:
            title_el = game.select_one('.title')
            if not title_el:
                continue
            title = title_el.get_text(strip=True)
            link_el = game.select_one('a.game_link')
            link = link_el.get('href', '') if link_el else ''
            desc_el = game.select_one('.game_text')
            desc = desc_el.get_text(strip=True) if desc_el else ''
            img_el = game.select_one('img')
            img = ''
            if img_el:
                img = img_el.get('data-lazy_src', '') or img_el.get('src', '')
            items.append({
                'title': title, 'url': link,
                'summary': truncate_text(desc, 200),
                'pub_time': '', 'source': 'itch.io Game Design',
                'category': 'game', 'type': 'gameplay',
                'image': img
            })
    except Exception:
        pass
    return items


def fetch_gamedeveloper_articles() -> List[Dict[str, Any]]:
    """Game Developer 深度文章"""
    xml = fetch_url("https://www.gamedeveloper.com/rss.xml", timeout=15)
    return _parse_rss(xml, 'Game Developer') if xml else []


# ========== 中文来源 ==========

def fetch_chule_rss() -> List[Dict[str, Any]]:
    """触乐 RSS"""
    for url in ["https://www.chuapp.com/rss", "https://www.chuapp.com/feed"]:
        xml = fetch_url(url, timeout=15)
        if xml and '<rss' in xml:
            return _parse_rss(xml, '触乐')
    return []


def fetch_yystv_rss() -> List[Dict[str, Any]]:
    """游研社 RSS"""
    for url in ["https://www.yystv.cn/rss/feed", "https://www.yystv.cn/rss"]:
        xml = fetch_url(url, timeout=15)
        if xml and '<rss' in xml:
            return _parse_rss(xml, '游研社')
    return []


# ========== 讨论/论坛来源 ==========

def fetch_hn_gamedev() -> List[Dict[str, Any]]:
    """Hacker News 游戏开发讨论"""
    data = fetch_json("https://hacker-news.firebaseio.com/v0/topstories.json")
    if not data:
        return []
    items = []
    kw = ['game', 'gamedev', 'unity', 'unreal', 'godot', 'gameplay', 'roguelike',
          'indie', 'pixel', 'shader', 'procedural', 'interactive', 'playtest',
          'game design', 'game jam', 'level design', 'game engine']
    for sid in data[:80]:
        story = fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
        if not story or story.get('type') != 'story':
            continue
        title = story.get('title', '')
        if any(k in title.lower() for k in kw):
            url = story.get('url', f"https://news.ycombinator.com/item?id={sid}")
            items.append({
                'title': title, 'url': url,
                'summary': '',
                'pub_time': '', 'source': 'Hacker News',
                'category': 'game', 'type': classify_type(title, ''),
                'image': ''
            })
        if len(items) >= 5:
            break
    return items


def fetch_reddit_gamedesign() -> List[Dict[str, Any]]:
    """Reddit r/gamedesign"""
    data = fetch_json(
        "https://www.reddit.com/r/gamedesign/hot.json?limit=15",
        headers={'User-Agent': 'DailyNewsBot/1.0'},
        timeout=15
    )
    if not data or 'data' not in data:
        return []
    items = []
    for child in data['data'].get('children', []):
        post = child.get('data', {})
        title = post.get('title', '')
        url = f"https://reddit.com{post.get('permalink', '')}"
        selftext = post.get('selftext', '')
        thumbnail = post.get('thumbnail', '')
        if not thumbnail.startswith('http'):
            thumbnail = ''
        items.append({
            'title': title, 'url': url,
            'summary': truncate_text(selftext, 200),
            'pub_time': '', 'source': 'Reddit/r/gamedesign',
            'category': 'game', 'type': classify_type(title, selftext),
            'image': thumbnail
        })
    return items[:10]


def fetch_reddit_indiegaming() -> List[Dict[str, Any]]:
    """Reddit r/indiegaming"""
    data = fetch_json(
        "https://www.reddit.com/r/indiegaming/hot.json?limit=15",
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
        thumbnail = post.get('thumbnail', '')
        if not thumbnail.startswith('http'):
            thumbnail = ''
        items.append({
            'title': title, 'url': url,
            'summary': truncate_text(selftext, 200),
            'pub_time': '', 'source': 'Reddit/r/indiegaming',
            'category': 'game', 'type': classify_type(title, selftext),
            'image': thumbnail
        })
    return items[:10]


def fetch_reddit_roguelikes() -> List[Dict[str, Any]]:
    """Reddit r/roguelikes - 玩法创新灵感"""
    data = fetch_json(
        "https://www.reddit.com/r/roguelikes/hot.json?limit=10",
        headers={'User-Agent': 'DailyNewsBot/1.0'},
        timeout=15
    )
    if not data or 'data' not in data:
        return []
    items = []
    for child in data['data'].get('children', []):
        post = child.get('data', {})
        title = post.get('title', '')
        url = f"https://reddit.com{post.get('permalink', '')}"
        selftext = post.get('selftext', '')
        items.append({
            'title': title, 'url': url,
            'summary': truncate_text(selftext, 200),
            'pub_time': '', 'source': 'Reddit/r/roguelikes',
            'category': 'game', 'type': 'gameplay',
            'image': ''
        })
    return items[:8]


# ========== 主函数 ==========

def fetch_game_news() -> List[Dict[str, Any]]:
    all_news = []
    sources = [
        # 英文技术站
        ('GameDev.net', fetch_gamedev_rss),
        ('Game Developer', fetch_gamedeveloper_articles),
        ('IndieDB', fetch_indiedb_rss),
        # Steam/itch.io
        ('Steam', fetch_steam_newreleases),
        ('itch.io Newest', fetch_itchio_newest),
        ('itch.io Top Rated', fetch_itchio_top_rated),
        # 中文媒体
        ('触乐', fetch_chule_rss),
        ('游研社', fetch_yystv_rss),
        # 讨论/论坛（玩法灵感重要来源）
        ('Reddit/r/gamedesign', fetch_reddit_gamedesign),
        ('Reddit/r/indiegaming', fetch_reddit_indiegaming),
        ('Reddit/r/roguelikes', fetch_reddit_roguelikes),
        ('Hacker News', fetch_hn_gamedev),
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

    # 优先玩法创新，目标 15 条
    gameplay = [n for n in unique if n.get('type') == 'gameplay']
    art = [n for n in unique if n.get('type') == 'art']
    narrative = [n for n in unique if n.get('type') == 'narrative']
    tech = [n for n in unique if n.get('type') == 'tech']
    indie = [n for n in unique if n.get('type') == 'indie']
    other = [n for n in unique if n.get('type') not in ('gameplay', 'art', 'narrative', 'tech', 'indie')]

    # 分配：玩法创新 5+，其他各 2-3
    result = gameplay[:5] + art[:3] + narrative[:2] + tech[:2] + indie[:2] + other[:1]
    return result[:15]


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
    for n in news[:5]:
        print(f"  [{n.get('type')}] {n['source']}: {n['title'][:60]}")
