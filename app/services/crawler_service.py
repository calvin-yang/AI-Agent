import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
from flask import current_app
import time
import random

class CrawlerService:
    """网页爬虫服务类"""
    
    def __init__(self):
        self.config = current_app.config['CRAWLER_CONFIG']
        self.headers = {
            'User-Agent': self.config['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def crawl_url(self, url: str) -> Optional[Dict]:
        """
        爬取指定URL的网页内容
        
        Args:
            url: 要爬取的URL
            
        Returns:
            Dict: 包含标题、内容、元数据的字典，失败时返回None
        """
        try:
            # 添加随机延迟避免被封
            time.sleep(random.uniform(0.5, 2.0))
            print(f"爬取URL: {url}")
            
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=self.config['timeout'],
                allow_redirects=True
            )
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'lxml')
            
            # 提取标题
            title = self._extract_title(soup)
            
            # 提取主要内容
            content = self._extract_content(soup)
            
            # 检查提取的文本内容长度（而不是原始HTML长度）
            if len(content) > self.config['max_content_length']:
                print(f"提取的文本内容过长，截断: {url}")
                content = content[:self.config['max_content_length']] + "..."
            
            # 提取元数据
            metadata = self._extract_metadata(soup)
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'metadata': metadata,
                'content_length': len(content)
            }
            
        except requests.exceptions.RequestException as e:
            print(f"请求失败 {url}: {str(e)}")
            return None
        except Exception as e:
            print(f"解析失败 {url}: {str(e)}")
            return None
    
    def crawl_multiple_urls(self, urls: list) -> list:
        """
        批量爬取多个URL
        
        Args:
            urls: URL列表
            
        Returns:
            list: 爬取结果列表
        """
        results = []
        
        for url in urls:
            result = self.crawl_url(url)
            if result:
                results.append(result)
            
            # 避免请求过于频繁
            time.sleep(random.uniform(1.0, 3.0))
        
        return results
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取网页标题"""
        # 尝试多种标题选择器
        title_selectors = [
            'title',
            'h1',
            '.title',
            '.headline',
            '[class*="title"]',
            '[class*="headline"]'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        
        return "无标题"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """提取网页主要内容"""
        # 移除不需要的标签
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside', 'advertisement']):
            tag.decompose()
        
        # 尝试多种内容选择器
        content_selectors = [
            'article',
            '.content',
            '.main-content',
            '.post-content',
            '.entry-content',
            'main',
            '.article-body',
            '[class*="content"]',
            '[class*="article"]',
            '[class*="post"]'
        ]
        
        content = ""
        
        # 首先尝试找到主要内容区域
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    text = element.get_text(separator=' ', strip=True)
                    if len(text) > len(content):
                        content = text
                break
        
        # 如果没有找到特定内容区域，使用body
        if not content:
            body = soup.find('body')
            if body:
                content = body.get_text(separator=' ', strip=True)
        
        # 清理内容
        content = self._clean_content(content)
        
        return content
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """提取网页元数据"""
        metadata = {}
        
        # 提取meta标签
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property')
            content = tag.get('content')
            if name and content:
                metadata[name] = content
        
        # 提取描述
        description = metadata.get('description') or metadata.get('og:description')
        if description:
            metadata['description'] = description
        
        return metadata
    
    def _clean_content(self, content: str) -> str:
        """清理文本内容"""
        # 移除多余的空白字符
        import re
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        # 限制长度
        max_length = self.config['max_content_length']
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        return content
