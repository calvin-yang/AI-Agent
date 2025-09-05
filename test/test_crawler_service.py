import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.crawler_service import CrawlerService

class TestCrawlerService(unittest.TestCase):
    """爬虫服务测试类"""
    
    def setUp(self):
        """测试前准备"""
        with patch('app.services.crawler_service.current_app') as mock_app:
            mock_app.config = {
                'CRAWLER_CONFIG': {
                    'timeout': 10,
                    'max_content_length': 50000,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            }
            self.service = CrawlerService()
    
    @patch('app.services.crawler_service.requests.get')
    def test_crawl_url_success(self, mock_get):
        """测试成功爬取URL"""
        # 模拟HTTP响应
        mock_response = MagicMock()
        mock_response.content = b'<html><head><title>Test Title</title></head><body><h1>Test Content</h1></body></html>'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with patch('app.services.crawler_service.BeautifulSoup') as mock_soup:
            # 模拟BeautifulSoup解析
            mock_soup_instance = MagicMock()
            mock_soup_instance.select_one.return_value = MagicMock(get_text=lambda: "Test Title")
            mock_soup_instance.find.return_value = MagicMock(get_text=lambda separator, strip: "Test Content")
            mock_soup_instance.find_all.return_value = []
            mock_soup.return_value = mock_soup_instance
            
            result = self.service.crawl_url("http://test.com")
            
            self.assertIsNotNone(result)
            self.assertEqual(result['url'], "http://test.com")
            self.assertEqual(result['title'], "Test Title")
            self.assertEqual(result['content'], "Test Content")
    
    @patch('app.services.crawler_service.requests.get')
    def test_crawl_url_failure(self, mock_get):
        """测试爬取URL失败"""
        # 模拟请求异常
        mock_get.side_effect = Exception("网络错误")
        
        result = self.service.crawl_url("http://test.com")
        
        self.assertIsNone(result)
    
    @patch('app.services.crawler_service.CrawlerService.crawl_url')
    def test_crawl_multiple_urls(self, mock_crawl_url):
        """测试批量爬取URL"""
        # 模拟单个URL爬取结果
        mock_crawl_url.side_effect = [
            {'url': 'http://test1.com', 'title': 'Title1', 'content': 'Content1'},
            None,  # 第二个URL爬取失败
            {'url': 'http://test3.com', 'title': 'Title3', 'content': 'Content3'}
        ]
        
        urls = ['http://test1.com', 'http://test2.com', 'http://test3.com']
        results = self.service.crawl_multiple_urls(urls)
        
        self.assertEqual(len(results), 2)  # 只有2个成功的结果
        self.assertEqual(results[0]['url'], 'http://test1.com')
        self.assertEqual(results[1]['url'], 'http://test3.com')
    
    def test_extract_title(self):
        """测试标题提取"""
        with patch('app.services.crawler_service.BeautifulSoup') as mock_soup:
            # 模拟找到title标签
            mock_title = MagicMock()
            mock_title.get_text.return_value = "Test Title"
            mock_soup_instance = MagicMock()
            mock_soup_instance.select_one.return_value = mock_title
            mock_soup.return_value = mock_soup_instance
            
            result = self.service._extract_title(mock_soup_instance)
            
            self.assertEqual(result, "Test Title")
    
    def test_extract_content(self):
        """测试内容提取"""
        with patch('app.services.crawler_service.BeautifulSoup') as mock_soup:
            # 模拟找到article标签
            mock_article = MagicMock()
            mock_article.get_text.return_value = "Test Article Content"
            mock_soup_instance = MagicMock()
            mock_soup_instance.select.return_value = [mock_article]
            mock_soup_instance.find.return_value = None
            mock_soup.return_value = mock_soup_instance
            
            result = self.service._extract_content(mock_soup_instance)
            
            self.assertEqual(result, "Test Article Content")
    
    def test_clean_content(self):
        """测试内容清理"""
        dirty_content = "  Test   Content  \n\n  Multiple   Spaces  "
        clean_content = self.service._clean_content(dirty_content)
        
        self.assertEqual(clean_content, "Test Content Multiple Spaces")

if __name__ == '__main__':
    unittest.main()
