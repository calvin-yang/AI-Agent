import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.search_service import SearchService

class TestSearchService(unittest.TestCase):
    """搜索服务测试类"""
    
    def setUp(self):
        """测试前准备"""
        with patch('app.services.search_service.current_app') as mock_app:
            mock_app.config = {
                'SEARCH_ENGINES': {
                    'duckduckgo': {'enabled': True, 'weight': 0.6, 'max_results': 5},
                    'google': {'enabled': True, 'weight': 0.4, 'max_results': 3}
                },
                'CRAWLER_CONFIG': {
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            }
            self.service = SearchService()
    
    @patch('app.services.search_service.DDGS')
    def test_search_duckduckgo(self, mock_ddgs):
        """测试DuckDuckGo搜索"""
        # 模拟DDGS返回结果
        mock_ddgs_instance = MagicMock()
        mock_ddgs_instance.text.return_value = [
            {
                'href': 'http://test1.com',
                'title': '测试标题1',
                'body': '测试内容1'
            },
            {
                'href': 'http://test2.com',
                'title': '测试标题2',
                'body': '测试内容2'
            }
        ]
        mock_ddgs.return_value = mock_ddgs_instance
        
        results = self.service._search_duckduckgo("测试关键词")
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['url'], 'http://test1.com')
        self.assertEqual(results[0]['title'], '测试标题1')
        self.assertEqual(results[0]['source'], 'duckduckgo')
        self.assertEqual(results[0]['weight'], 0.6)
    
    @patch('app.services.search_service.google_search')
    def test_search_google(self, mock_google_search):
        """测试Google搜索"""
        # 模拟Google搜索返回结果
        mock_google_search.return_value = [
            'http://google-test1.com',
            'http://google-test2.com'
        ]
        
        results = self.service._search_google("测试关键词")
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['url'], 'http://google-test1.com')
        self.assertEqual(results[0]['source'], 'google')
        self.assertEqual(results[0]['weight'], 0.4)
    
    def test_deduplicate_results(self):
        """测试去重功能"""
        results = [
            {'url': 'http://test1.com', 'title': '标题1'},
            {'url': 'http://test2.com', 'title': '标题2'},
            {'url': 'http://test1.com', 'title': '重复标题1'},  # 重复URL
            {'url': 'http://test3.com', 'title': '标题3'}
        ]
        
        unique_results = self.service._deduplicate_results(results)
        
        self.assertEqual(len(unique_results), 3)
        urls = [result['url'] for result in unique_results]
        self.assertEqual(len(set(urls)), 3)  # 确保没有重复URL
    
    def test_sort_results_by_relevance(self):
        """测试相关性排序"""
        results = [
            {'title': '不相关标题', 'content': '不相关内容', 'weight': 0.1},
            {'title': '测试相关标题', 'content': '测试相关内容', 'weight': 0.5},
            {'title': '普通标题', 'content': '普通内容', 'weight': 0.3}
        ]
        
        sorted_results = self.service._sort_results_by_relevance(results, "测试")
        
        # 最相关的结果应该排在前面
        self.assertIn("测试相关", sorted_results[0]['title'])
    
    @patch('app.services.search_service.SearchService._search_duckduckgo')
    @patch('app.services.search_service.SearchService._search_google')
    def test_search_integration(self, mock_google, mock_ddg):
        """测试完整搜索流程"""
        # 模拟搜索结果
        mock_ddg.return_value = [
            {'url': 'http://ddg-test.com', 'title': 'DDG结果', 'content': 'DDG内容', 'source': 'duckduckgo', 'weight': 0.6}
        ]
        mock_google.return_value = [
            {'url': 'http://google-test.com', 'title': 'Google结果', 'content': 'Google内容', 'source': 'google', 'weight': 0.4}
        ]
        
        results = self.service.search("测试关键词")
        
        self.assertEqual(len(results), 2)
        # 验证两个搜索引擎都被调用了
        mock_ddg.assert_called_once_with("测试关键词")
        mock_google.assert_called_once_with("测试关键词")

if __name__ == '__main__':
    unittest.main()
