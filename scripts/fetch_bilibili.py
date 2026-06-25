"""
B站UP主视频抓取模块
通过多种方式获取指定UP主的最新视频
"""

from typing import List, Dict, Any
import json
import re
import hashlib
import time
import urllib.parse
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from utils import fetch_url, fetch_json, truncate_text, get_today_date


def _get_wbi_params() -> dict:
    """获取 B站 WBI 签名参数"""
    # 从 nav API 获取 img_key 和 sub_key
    nav = fetch_json("https://api.bilibili.com/x/web-interface/nav", timeout=10)
    if not nav or nav.get('code') != 0:
        return {}
    wbi_img = nav.get('data', {}).get('wbi_img', {})
    img_url = wbi_img.get('img_url', '')
    sub_url = wbi_img.get('sub_url', '')
    if not img_url or not sub_url:
        return {}
    img_key = img_url.split('/')[-1].split('.')[0]
    sub_key = sub_url.split('/')[-1].split('.')[0]
    return {'img_key': img_key, 'sub_key': sub_key}


def _get_mixin_key(orig: str) -> str:
    """WBI 签名 mixin key"""
    MIXIN_KEY_ENC_TAB = [
        46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
        27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
        37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
        22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52
    ]
    return ''.join([orig[i] for i in MIXIN_KEY_ENC_TAB])[:32]


def _sign_wbi(params: dict, wbi_keys: dict) -> dict:
    """WBI 签名"""
    img_key = wbi_keys.get('img_key', '')
    sub_key = wbi_keys.get('sub_key', '')
    if not img_key or not sub_key:
        return params
    mixin_key = _get_mixin_key(img_key + sub_key)
    curr_time = round(time.time())
    params['wts'] = curr_time
    # 过滤非法字符
    params = {
        k: ''.join(filter(lambda c: c not in "!'()*", str(v)))
        for k, v in sorted(params.items())
    }
    query = urllib.parse.urlencode(params)
    wbi_sign = hashlib.md5((query + mixin_key).encode()).hexdigest()
    params['w_rid'] = wbi_sign
    return params


def fetch_bilibili_up_videos(mid: int, up_name: str) -> List[Dict[str, Any]]:
    """
    通过 WBI 签名 API 获取 UP 主视频
    """
    wbi_keys = _get_wbi_params()
    if not wbi_keys:
        print("  WBI 签名获取失败")
        return []

    params = {
        'mid': str(mid),
        'ps': '10',
        'pn': '1',
        'order': 'pubdate',
    }
    signed_params = _sign_wbi(params, wbi_keys)
    query = urllib.parse.urlencode(signed_params)
    url = f"https://api.bilibili.com/x/space/wbi/arc/search?{query}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Referer': f'https://space.bilibili.com/{mid}/video',
    }
    data = fetch_json(url, headers=headers, timeout=15)
    if not data or data.get('code') != 0:
        msg = data.get('message', '') if data else '无响应'
        print(f"  API 返回错误: {msg}")
        return []

    items = []
    vlist = data.get('data', {}).get('list', {}).get('vlist', [])
    for v in vlist[:10]:
        bvid = v.get('bvid', '')
        title = v.get('title', '')
        desc = v.get('description', '')
        pic = v.get('pic', '')
        if pic and pic.startswith('//'):
            pic = 'https:' + pic
        items.append({
            'title': title,
            'url': f"https://www.bilibili.com/video/{bvid}" if bvid else '',
            'summary': truncate_text(desc, 150),
            'pub_time': '',
            'source': f'B站/{up_name}',
            'category': 'game',
            'type': 'video',
            'image': pic,
            'up_name': up_name
        })
    return items


def fetch_bilibili_space_html(mid: int, up_name: str) -> List[Dict[str, Any]]:
    """HTML 回退方案"""
    url = f"https://space.bilibili.com/{mid}/video"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Referer': f'https://space.bilibili.com/{mid}',
        'Cookie': 'buvid3=infoc; b_nut=100'
    }
    html = fetch_url(url, headers=headers, timeout=20)
    if not html:
        return []
    items = []
    try:
        m = re.search(r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\});\s*\(function', html, re.DOTALL)
        if m:
            data = json.loads(m.group(1))
            vlist = data.get('video', {}).get('list', {}).get('vlist', [])
            for v in vlist[:10]:
                bvid = v.get('bvid', '')
                title = v.get('title', '')
                desc = v.get('description', '')
                pic = v.get('pic', '')
                if pic and pic.startswith('//'):
                    pic = 'https:' + pic
                items.append({
                    'title': title,
                    'url': f"https://www.bilibili.com/video/{bvid}" if bvid else '',
                    'summary': truncate_text(desc, 150),
                    'pub_time': '', 'source': f'B站/{up_name}',
                    'category': 'game', 'type': 'video',
                    'image': pic, 'up_name': up_name
                })
    except Exception:
        pass
    return items


def fetch_bilibili_up(mid: int, up_name: str) -> List[Dict[str, Any]]:
    """获取指定 UP 主的最新视频"""
    print(f"正在抓取 B站 UP主: {up_name} ({mid})...")

    # 方式1：WBI 签名 API
    items = fetch_bilibili_up_videos(mid, up_name)
    if items:
        print(f"  ✅ 获取到 {len(items)} 个视频")
        return items

    # 方式2：HTML 回退
    items = fetch_bilibili_space_html(mid, up_name)
    if items:
        print(f"  ✅ HTML 获取到 {len(items)} 个视频")
        return items

    print(f"  ❌ 未获取到视频")
    return []


def fetch_bilibili_updates(up_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """批量获取多个 UP 主的最新视频"""
    all_videos = []
    for up in up_list:
        mid = up.get('mid')
        name = up.get('name', '')
        if not mid:
            continue
        videos = fetch_bilibili_up(mid, name)
        all_videos.extend(videos)

    seen = set()
    unique = []
    for v in all_videos:
        if v['title'] not in seen:
            seen.add(v['title'])
            unique.append(v)
    return unique


def format_bilibili_markdown(videos: List[Dict[str, Any]], date: str = None) -> str:
    if date is None:
        date = get_today_date()
    lines = [f"# 📺 B站 UP主更新 - {date}", "", f"今日关注的 UP 主共更新 {len(videos)} 个视频", "", "---", ""]
    for i, v in enumerate(videos, 1):
        img = v.get('image', '')
        lines.extend([f"## {i}. [{v['title']}]({v['url']})", f"**UP主**: {v.get('up_name', '')}", ""])
        if img:
            lines.extend([f"![img]({img})", ""])
        if v.get('summary'):
            lines.extend([f"**简介**: {v['summary']}", ""])
        lines.extend(["---", ""])
    return '\n'.join(lines)


# 默认关注的 UP 主
DEFAULT_BILIBILI_UPS = [
    {"mid": 21390661, "name": "游戏汗先生"},
    {"mid": 396395171, "name": "Lee哥的游戏开发加油站"},
]


if __name__ == '__main__':
    videos = fetch_bilibili_updates(DEFAULT_BILIBILI_UPS)
    print(f"\n共 {len(videos)} 个视频")
    for v in videos[:5]:
        print(f"  [{v['up_name']}] {v['title']}")
        print(f"  {v['url']}")
