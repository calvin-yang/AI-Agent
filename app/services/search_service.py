import requests
from typing import List, Dict
from flask import current_app
from ddgs import DDGS
from googlesearch import search as google_search
import time
import random

class SearchService:
    """搜索引擎服务类"""
    
    def __init__(self):
        # 尝试从Flask应用上下文获取配置，如果没有则使用默认配置
        try:
            if current_app:
                self.config = current_app.config['SEARCH_ENGINES']
                self.user_agent = current_app.config['CRAWLER_CONFIG']['user_agent']
            else:
                raise RuntimeError("No Flask app context")
        except:
            # 如果没有Flask应用上下文，使用默认配置
            self.config = {
                'duckduckgo': {
                    'enabled': True,
                    'weight': 0.6,
                    'max_results': 5
                },
                'google': {
                    'enabled': True,
                    'weight': 0.4,
                    'max_results': 3
                }
            }
            self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    def search(self, keywords: str) -> List[Dict]:
        """
        使用多个搜索引擎搜索关键词
        
        Args:
            keywords: 搜索关键词
            
        Returns:
            List[Dict]: 搜索结果列表，包含url、title、content等信息
        """
        all_results = []
        
        # DuckDuckGo搜索
        if self.config['duckduckgo']['enabled']:
            ddg_results = self._search_duckduckgo(keywords)
            all_results.extend(ddg_results)
        
        # Google搜索
        if self.config['google']['enabled']:
            google_results = self._search_google(keywords)
            all_results.extend(google_results)
        
        # 去重和排序
        unique_results = self._deduplicate_results(all_results)
        sorted_results = self._sort_results_by_relevance(unique_results, keywords)
        
        return sorted_results[:10]  # 返回前10个结果
    
    def _search_duckduckgo(self, keywords: str) -> List[Dict]:
        """使用DuckDuckGo搜索"""
        try:
            ddgs = DDGS()
            results = ddgs.text(
                keywords, 
                max_results=self.config['duckduckgo']['max_results']
            )
            
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'url': result.get('href', ''),
                    'title': result.get('title', ''),
                    'content': result.get('body', ''),
                    'source': 'duckduckgo',
                    'weight': self.config['duckduckgo']['weight']
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"DuckDuckGo搜索失败: {str(e)}")
            return []
    
    def _search_google(self, keywords: str) -> List[Dict]:
        """使用Google搜索"""
        try:
            results = google_search(
                keywords, 
                num_results=self.config['google']['max_results'],
                sleep_interval=1
            )
            
            formatted_results = []
            for url in results:
                formatted_results.append({
                    'url': url,
                    'title': '',  # Google搜索API不直接提供标题
                    'content': '',
                    'source': 'google',
                    'weight': self.config['google']['weight']
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Google搜索失败: {str(e)}")
            return []
    
    def _deduplicate_results(self, results: List[Dict]) -> List[Dict]:
        """去除重复的搜索结果"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = result.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
    
    def _sort_results_by_relevance(self, results: List[Dict], keywords: str) -> List[Dict]:
        """根据相关性对结果进行排序"""
        def relevance_score(result):
            score = 0
            title = result.get('title', '').lower()
            content = result.get('content', '').lower()
            keywords_lower = keywords.lower()
            
            # 标题匹配权重更高
            if keywords_lower in title:
                score += 3
            
            # 内容匹配
            if keywords_lower in content:
                score += 1
            
            # 搜索引擎权重
            score += result.get('weight', 0)
            
            return score
        
        return sorted(results, key=relevance_score, reverse=True)
