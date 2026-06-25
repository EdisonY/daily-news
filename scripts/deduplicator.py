"""
去重模块
提供标题去重、内容去重、历史记录去重功能
"""

import re
import hashlib
from collections import defaultdict
from typing import List, Dict, Any, Tuple, Set
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from utils import preprocess_text, load_history, add_to_history, cleanup_old_news


class SimHash:
    """
    SimHash 算法实现
    用于内容去重
    """
    
    def __init__(self, bits: int = 64):
        self.bits = bits
    
    def _hash(self, token: str) -> int:
        """计算 token 的 hash 值"""
        return int(hashlib.md5(token.encode()).hexdigest(), 16)
    
    def _int_to_bin(self, num: int, bits: int) -> str:
        """整数转二进制字符串"""
        return bin(num)[2:].zfill(bits)
    
    def simhash(self, text: str) -> int:
        """计算文本的 SimHash 值"""
        if not text:
            return 0
        
        # 分词
        import jieba
        tokens = jieba.lcut(text)
        
        # 初始化向量
        v = [0] * self.bits
        
        for token in tokens:
            if len(token) < 2:
                continue
            
            # 计算 token 的 hash
            token_hash = self._hash(token)
            token_bin = self._int_to_bin(token_hash, self.bits)
            
            # 累加权重
            for i in range(self.bits):
                if token_bin[i] == '1':
                    v[i] += 1
                else:
                    v[i] -= 1
        
        # 生成最终 hash
        fingerprint = 0
        for i in range(self.bits):
            if v[i] > 0:
                fingerprint |= (1 << i)
        
        return fingerprint
    
    def hamming_distance(self, hash1: int, hash2: int) -> int:
        """计算两个 hash 的汉明距离"""
        x = hash1 ^ hash2
        distance = 0
        while x:
            distance += 1
            x &= x - 1
        return distance
    
    def is_duplicate(self, hash1: int, hash2: int, threshold: int = 3) -> bool:
        """判断是否重复"""
        return self.hamming_distance(hash1, hash2) <= threshold


class TextDeduplicator:
    """
    文本去重器
    支持标题去重和内容去重
    """
    
    def __init__(self, title_threshold: float = 0.7, content_threshold: int = 3):
        """
        初始化
        
        Args:
            title_threshold: 标题相似度阈值（0-1）
            content_threshold: 内容汉明距离阈值
        """
        self.title_threshold = title_threshold
        self.content_threshold = content_threshold
        self.simhash = SimHash()
    
    def preprocess_texts(self, texts: List[str]) -> List[str]:
        """预处理文本列表"""
        return [preprocess_text(text) for text in texts]
    
    def calculate_tfidf_similarity(self, texts: List[str]) -> np.ndarray:
        """
        计算 TF-IDF 相似度矩阵
        """
        if not texts:
            return np.array([])
        
        # TF-IDF 向量化
        vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(2, 4),
            max_features=10000
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            similarity_matrix = cosine_similarity(tfidf_matrix)
            return similarity_matrix
        except Exception as e:
            print(f"Error calculating TF-IDF similarity: {e}")
            return np.zeros((len(texts), len(texts)))
    
    def find_title_duplicates(self, news_list: List[Dict[str, Any]]) -> List[Tuple[int, int, float]]:
        """
        查找标题重复的新闻
        
        Returns:
            List of (index1, index2, similarity) tuples
        """
        if len(news_list) < 2:
            return []
        
        # 提取标题
        titles = [news.get('title', '') for news in news_list]
        
        # 预处理
        processed_titles = self.preprocess_texts(titles)
        
        # 计算相似度
        similarity_matrix = self.calculate_tfidf_similarity(processed_titles)
        
        # 查找重复
        duplicates = []
        for i in range(len(news_list)):
            for j in range(i + 1, len(news_list)):
                similarity = similarity_matrix[i][j]
                if similarity > self.title_threshold:
                    duplicates.append((i, j, similarity))
        
        return duplicates
    
    def find_content_duplicates(self, news_list: List[Dict[str, Any]]) -> List[Tuple[int, int, int]]:
        """
        查找内容重复的新闻
        
        Returns:
            List of (index1, index2, hamming_distance) tuples
        """
        if len(news_list) < 2:
            return []
        
        # 计算 SimHash
        hashes = []
        for news in news_list:
            content = f"{news.get('title', '')} {news.get('summary', '')}"
            content_hash = self.simhash.simhash(content)
            hashes.append(content_hash)
        
        # 查找重复
        duplicates = []
        for i in range(len(news_list)):
            for j in range(i + 1, len(news_list)):
                distance = self.simhash.hamming_distance(hashes[i], hashes[j])
                if distance <= self.content_threshold:
                    duplicates.append((i, j, distance))
        
        return duplicates
    
    def find_history_duplicates(self, news_list: List[Dict[str, Any]], category: str) -> Set[int]:
        """
        查找与历史记录重复的新闻
        
        Returns:
            Set of duplicate indices
        """
        history = load_history()
        if not history.get('news'):
            return set()
        
        # 提取历史新闻的文本
        historical_news = [
            news for news in history['news']
            if news.get('category') == category
        ]
        
        if not historical_news:
            return set()
        
        historical_texts = [
            f"{news.get('title', '')} {news.get('summary', '')}"
            for news in historical_news
        ]
        
        # 计算 SimHash
        historical_hashes = [
            self.simhash.simhash(text) for text in historical_texts
        ]
        
        # 检查新新闻与历史记录的重复
        duplicate_indices = set()
        for i, news in enumerate(news_list):
            content = f"{news.get('title', '')} {news.get('summary', '')}"
            content_hash = self.simhash.simhash(content)
            
            for hist_hash in historical_hashes:
                if self.simhash.is_duplicate(content_hash, hist_hash, self.content_threshold):
                    duplicate_indices.add(i)
                    break
        
        return duplicate_indices
    
    def deduplicate(self, news_list: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
        """
        去重新闻列表
        
        Args:
            news_list: 新闻列表
            category: 新闻类别（用于历史记录去重）
            
        Returns:
            去重后的新闻列表
        """
        if not news_list:
            return []
        
        # 1. 标题去重
        title_duplicates = self.find_title_duplicates(news_list)
        
        # 标记要删除的索引
        duplicate_indices = set()
        for i, j, similarity in title_duplicates:
            # 保留较新的新闻（假设列表顺序表示时间顺序）
            # 如果有时间信息，使用时间信息
            time_i = news_list[i].get('pub_time', '')
            time_j = news_list[j].get('pub_time', '')
            
            if time_i > time_j:
                duplicate_indices.add(j)
            else:
                duplicate_indices.add(i)
        
        # 2. 内容去重
        content_duplicates = self.find_content_duplicates(news_list)
        for i, j, distance in content_duplicates:
            if i not in duplicate_indices and j not in duplicate_indices:
                # 保留较新的新闻
                time_i = news_list[i].get('pub_time', '')
                time_j = news_list[j].get('pub_time', '')
                
                if time_i > time_j:
                    duplicate_indices.add(j)
                else:
                    duplicate_indices.add(i)
        
        # 3. 历史记录去重
        history_duplicates = self.find_history_duplicates(news_list, category)
        duplicate_indices.update(history_duplicates)
        
        # 4. 过滤重复项
        filtered_news = []
        for i, news in enumerate(news_list):
            if i not in duplicate_indices:
                # 添加到历史记录
                add_to_history(news, category)
                filtered_news.append(news)
        
        return filtered_news


class RelevanceSorter:
    """
    相关性排序器
    根据时间、来源、关键词等因素排序
    """
    
    def __init__(self):
        # 来源权重
        self.source_weights = {
            '36氪': 0.9,
            'IT桔子': 0.85,
            '创业邦': 0.8,
            '投资界': 0.8,
            'GameDev.net': 0.85,
            'Gamasutra': 0.9,
            'IndieDB': 0.8,
            'Steam': 0.75,
            '触乐': 0.8,
            '游研社': 0.8,
            'GitHub': 0.9,
            '知乎': 0.7,
            '小红书': 0.6,
            'IndieHackers': 0.75
        }
        
        # 关键词权重
        self.keyword_weights = {
            'startup': {
                '融资': 0.3,
                '投资': 0.3,
                '创业': 0.2,
                'A轮': 0.4,
                'B轮': 0.4,
                '种子轮': 0.3,
                '低成本': 0.2,
                '小投入': 0.2,
                '副业': 0.15,
                '轻创业': 0.2
            },
            'game': {
                '玩法': 0.3,
                '机制': 0.3,
                '创新': 0.3,
                '设计': 0.2,
                '独立游戏': 0.2,
                'indie': 0.2,
                'gameplay': 0.3,
                'mechanic': 0.3
            }
        }
    
    def calculate_relevance_score(self, news: Dict[str, Any], category: str) -> float:
        """
        计算单条新闻的相关性分数
        """
        score = 0.0
        
        # 1. 时间权重（越新越好）
        pub_time = news.get('pub_time', '')
        if pub_time:
            try:
                # 尝试解析时间
                if '小时前' in pub_time:
                    hours = int(re.search(r'(\d+)小时前', pub_time).group(1))
                    time_weight = max(0, 1 - hours / 24)
                elif '天前' in pub_time:
                    days = int(re.search(r'(\d+)天前', pub_time).group(1))
                    time_weight = max(0, 1 - days / 7)
                else:
                    time_weight = 0.5  # 默认权重
                
                score += time_weight * 0.3
            except:
                score += 0.15  # 默认时间权重
        
        # 2. 来源权重
        source = news.get('source', '')
        source_weight = self.source_weights.get(source, 0.5)
        score += source_weight * 0.2
        
        # 3. 关键词权重
        text = f"{news.get('title', '')} {news.get('summary', '')}"
        keywords = self.keyword_weights.get(category, {})
        
        keyword_score = 0
        for keyword, weight in keywords.items():
            if keyword in text.lower():
                keyword_score += weight
        
        # 限制关键词分数
        keyword_score = min(keyword_score, 0.5)
        score += keyword_score
        
        # 4. 内容质量权重（基于摘要长度）
        summary = news.get('summary', '')
        if len(summary) > 100:
            score += 0.1
        elif len(summary) > 50:
            score += 0.05
        
        return score
    
    def sort_by_relevance(self, news_list: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
        """
        按相关性排序
        """
        # 计算每条新闻的分数
        for news in news_list:
            news['relevance_score'] = self.calculate_relevance_score(news, category)
        
        # 按分数降序排序
        return sorted(news_list, key=lambda x: x.get('relevance_score', 0), reverse=True)


def deduplicate_news(news_list: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
    """
    去重新闻列表（主函数）
    
    Args:
        news_list: 新闻列表
        category: 新闻类别
        
    Returns:
        去重后的新闻列表
    """
    deduplicator = TextDeduplicator()
    return deduplicator.deduplicate(news_list, category)


def sort_news_by_relevance(news_list: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
    """
    按相关性排序（主函数）
    
    Args:
        news_list: 新闻列表
        category: 新闻类别
        
    Returns:
        排序后的新闻列表
    """
    sorter = RelevanceSorter()
    return sorter.sort_by_relevance(news_list, category)


def main():
    """
    主函数（用于测试）
    """
    # 测试数据
    test_news = [
        {
            'title': '某公司获得A轮融资1000万美元',
            'summary': '某科技公司宣布获得A轮融资，金额1000万美元',
            'source': '36氪',
            'pub_time': '2小时前'
        },
        {
            'title': '某公司完成A轮融资，金额1000万美元',
            'summary': '某公司今日宣布完成A轮融资',
            'source': 'IT桔子',
            'pub_time': '3小时前'
        },
        {
            'title': '创新玩法：如何设计一个有趣的游戏机制',
            'summary': '探讨游戏设计中的创新玩法机制',
            'source': 'GameDev.net',
            'pub_time': '1天前'
        }
    ]
    
    print("测试去重功能...")
    deduplicated = deduplicate_news(test_news, 'startup')
    print(f"去重后剩余 {len(deduplicated)} 条新闻")
    
    print("\n测试排序功能...")
    sorted_news = sort_news_by_relevance(deduplicated, 'startup')
    for i, news in enumerate(sorted_news, 1):
        print(f"{i}. {news['title']} (分数: {news.get('relevance_score', 0):.2f})")


if __name__ == '__main__':
    main()
