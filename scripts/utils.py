"""
工具函数模块
提供通用的文本处理、日期处理、HTTP 请求等功能
"""

import re
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import jieba

# 配置
HISTORY_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'history')
HISTORY_FILE = os.path.join(HISTORY_DIR, 'news_history.json')

# 确保目录存在
os.makedirs(HISTORY_DIR, exist_ok=True)


def preprocess_text(text: str) -> str:
    """
    文本预处理
    - 去除 HTML 标签
    - 去除特殊字符
    - 中文分词
    - 去除停用词
    """
    if not text:
        return ''
    
    # 去除 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 去除特殊字符，保留中文、英文、数字
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)
    
    # 中文分词
    words = jieba.lcut(text)
    
    # 去除停用词
    stop_words = {
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', 
        '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', 
        '没有', '看', '好', '自己', '这', '他', '她', '它', '们', '那', '被',
        '从', '把', '让', '用', '为', '与', '对', '等', '可以', '这', '那',
        '吗', '吧', '呢', '啊', '呀', '哦', '哈', '嗯', '哎', '唉',
        'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'can', 'shall', 'to', 'of', 'in', 'for',
        'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'between', 'out', 'off', 'over',
        'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when',
        'where', 'why', 'how', 'all', 'both', 'each', 'few', 'more', 'most',
        'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
        'so', 'than', 'too', 'very', 'just', 'because', 'but', 'and', 'or',
        'if', 'while', 'about', 'against', 'up', 'down', 'this', 'that',
        'these', 'those', 'it', 'its'
    }
    
    words = [w for w in words if w not in stop_words and len(w) > 1]
    
    return ' '.join(words)


def get_headers() -> Dict[str, str]:
    """获取通用请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }


def fetch_url(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Optional[str]:
    """
    获取网页内容
    """
    try:
        if headers is None:
            headers = get_headers()
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        # 尝试检测编码
        if response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding
        
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def fetch_json(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 30) -> Optional[Dict]:
    """
    获取 JSON 数据
    """
    try:
        if headers is None:
            headers = get_headers()
        
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        print(f"Error fetching JSON from {url}: {e}")
        return None


def parse_html(html: str) -> Optional[BeautifulSoup]:
    """
    解析 HTML
    """
    try:
        return BeautifulSoup(html, 'lxml')
    except Exception as e:
        print(f"Error parsing HTML: {e}")
        return None


def get_yesterday_date() -> str:
    """获取昨天的日期字符串"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d')


def get_today_date() -> str:
    """获取今天的日期字符串"""
    return datetime.now().strftime('%Y-%m-%d')


def get_current_timestamp() -> str:
    """获取当前时间戳"""
    return datetime.now().isoformat()


def load_history() -> Dict[str, Any]:
    """
    加载历史记录
    """
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
    
    return {'news': [], 'last_cleanup': get_current_timestamp()}


def save_history(history: Dict[str, Any]) -> bool:
    """
    保存历史记录
    """
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving history: {e}")
        return False


def cleanup_old_news(history: Dict[str, Any], days: int = 30) -> Dict[str, Any]:
    """
    清理旧新闻（保留指定天数）
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    history['news'] = [
        news for news in history['news']
        if datetime.fromisoformat(news.get('timestamp', '2000-01-01')) > cutoff_date
    ]
    history['last_cleanup'] = get_current_timestamp()
    
    return history


def add_to_history(news_item: Dict[str, Any], category: str) -> bool:
    """
    添加新闻到历史记录
    """
    history = load_history()
    
    # 添加元数据
    news_item['timestamp'] = get_current_timestamp()
    news_item['category'] = category
    
    # 添加到历史
    history['news'].append(news_item)
    
    # 清理旧记录
    history = cleanup_old_news(history)
    
    # 保存
    return save_history(history)


def format_number(num: int) -> str:
    """
    格式化数字（添加千位分隔符）
    """
    if num >= 1000000:
        return f"{num / 1000000:.1f}M"
    elif num >= 1000:
        return f"{num / 1000:.1f}K"
    else:
        return str(num)


def truncate_text(text: str, max_length: int = 200) -> str:
    """
    截断文本
    """
    if not text:
        return ''
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + '...'


def extract_keywords(text: str, topk: int = 5) -> List[str]:
    """
    提取关键词
    """
    if not text:
        return []

    words = jieba.lcut(text)

    # 简单的词频统计
    word_freq = {}
    for word in words:
        if len(word) > 1:
            word_freq[word] = word_freq.get(word, 0) + 1

    # 按词频排序
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

    return [word for word, freq in sorted_words[:topk]]


# --- 翻译模块（Google Translate 免费，无需 API Key）---
_translate_fail_count = 0
_TRANSLATE_FAIL_LIMIT = 10


def translate_to_zh(text: str) -> str:
    """
    将英文文本翻译为中文
    使用 Google Translate 免费 API（无需 Key）
    """
    global _translate_fail_count
    if _translate_fail_count >= _TRANSLATE_FAIL_LIMIT:
        return text

    if not text or not text.strip():
        return text

    # 如果中文字符占比 > 30%，认为已经是中文
    cn_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    if cn_chars / max(len(text), 1) > 0.3:
        return text

    import time as _time

    for attempt in range(2):
        try:
            import requests as _req
            # Google Translate 免费 API（无需 Key，有频率限制）
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                "client": "gtx",
                "sl": "en",
                "tl": "zh-CN",
                "dt": "t",
                "q": text[:500]
            }
            resp = _req.get(url, params=params, timeout=10,
                           headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                data = resp.json()
                translated = ''.join(part[0] for part in data[0] if part[0])
                if translated:
                    _translate_fail_count = 0
                    return translated
            elif resp.status_code == 429:
                _translate_fail_count += 1
                _time.sleep(1)
                continue
            return text
        except Exception:
            _translate_fail_count += 1
            _time.sleep(0.3)
    return text


def sanitize_filename(filename: str) -> str:
    """
    清理文件名
    """
    # 移除或替换非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 限制长度
    if len(filename) > 200:
        filename = filename[:200]
    return filename


def ensure_dir(dir_path: str) -> bool:
    """
    确保目录存在
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {dir_path}: {e}")
        return False


def save_markdown(content: str, filepath: str) -> bool:
    """
    保存 Markdown 文件
    """
    try:
        ensure_dir(os.path.dirname(filepath))
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error saving markdown to {filepath}: {e}")
        return False


def load_markdown(filepath: str) -> Optional[str]:
    """
    加载 Markdown 文件
    """
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    except Exception as e:
        print(f"Error loading markdown from {filepath}: {e}")
        return None
