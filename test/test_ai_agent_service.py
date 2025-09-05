import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ai_agent_service import AIAgentService

class TestAIAgentService(unittest.TestCase):
    """AI Agent服务测试类"""
    
    def setUp(self):
        """测试前准备"""
        with patch('app.services.ai_agent_service.DeepSeekService'), \
             patch('app.services.ai_agent_service.SearchService'), \
             patch('app.services.ai_agent_service.CrawlerService'):
            self.service = AIAgentService()
    
    @patch('app.services.ai_agent_service.DeepSeekService')
    @patch('app.services.ai_agent_service.SearchService')
    @patch('app.services.ai_agent_service.CrawlerService')
    def test_process_question_no_search(self, mock_crawler, mock_search, mock_deepseek):
        """测试不需要搜索的问题处理"""
        # 模拟DeepSeek分析结果 - 不需要搜索
        mock_deepseek_instance = MagicMock()
        mock_deepseek_instance.analyze_question.return_value = {
            'need_search': False,
            'search_keywords': '',
            'reason': '历史知识问题'
        }
        mock_deepseek.return_value = mock_deepseek_instance
        
        # 模拟直接回答
        mock_deepseek_instance._make_request.return_value = "这是一个关于Python的历史知识问题。"
        
        result = self.service.process_question("什么是Python？")
        
        self.assertFalse(result['search_performed'])
        self.assertEqual(result['analysis_reason'], '历史知识问题')
        self.assertIn("Python", result['answer'])
    
    @patch('app.services.ai_agent_service.DeepSeekService')
    @patch('app.services.ai_agent_service.SearchService')
    @patch('app.services.ai_agent_service.CrawlerService')
    def test_process_question_with_search(self, mock_crawler, mock_search, mock_deepseek):
        """测试需要搜索的问题处理"""
        # 模拟DeepSeek分析结果 - 需要搜索
        mock_deepseek_instance = MagicMock()
        mock_deepseek_instance.analyze_question.return_value = {
            'need_search': True,
            'search_keywords': '最新新闻',
            'reason': '涉及实时信息'
        }
        mock_deepseek.return_value = mock_deepseek_instance
        
        # 模拟搜索结果
        mock_search_instance = MagicMock()
        mock_search_instance.search.return_value = [
            {'url': 'http://test1.com', 'title': '新闻1', 'content': '内容1'},
            {'url': 'http://test2.com', 'title': '新闻2', 'content': '内容2'}
        ]
        mock_search.return_value = mock_search_instance
        
        # 模拟爬取结果
        mock_crawler_instance = MagicMock()
        mock_crawler_instance.crawl_multiple_urls.return_value = [
            {'url': 'http://test1.com', 'title': '新闻1', 'content': '详细内容1'},
            {'url': 'http://test2.com', 'title': '新闻2', 'content': '详细内容2'}
        ]
        mock_crawler.return_value = mock_crawler_instance
        
        # 模拟最终分析结果
        mock_deepseek_instance.analyze_with_context.return_value = "根据最新搜索结果，今天有以下重要新闻..."
        
        result = self.service.process_question("今天有什么最新新闻？")
        
        self.assertTrue(result['search_performed'])
        self.assertEqual(result['search_keywords'], '最新新闻')
        self.assertEqual(len(result['sources']), 2)
        self.assertIn("新闻", result['answer'])
    
    @patch('app.services.ai_agent_service.DeepSeekService')
    @patch('app.services.ai_agent_service.SearchService')
    @patch('app.services.ai_agent_service.CrawlerService')
    def test_process_question_search_no_results(self, mock_crawler, mock_search, mock_deepseek):
        """测试搜索无结果的情况"""
        # 模拟DeepSeek分析结果 - 需要搜索
        mock_deepseek_instance = MagicMock()
        mock_deepseek_instance.analyze_question.return_value = {
            'need_search': True,
            'search_keywords': '测试关键词',
            'reason': '需要搜索'
        }
        mock_deepseek.return_value = mock_deepseek_instance
        
        # 模拟搜索无结果
        mock_search_instance = MagicMock()
        mock_search_instance.search.return_value = []
        mock_search.return_value = mock_search_instance
        
        result = self.service.process_question("测试问题")
        
        self.assertTrue(result['search_performed'])
        self.assertEqual(result['error'], '搜索无结果')
        self.assertIn("无法找到", result['answer'])
    
    @patch('app.services.ai_agent_service.DeepSeekService')
    def test_get_search_suggestions(self, mock_deepseek):
        """测试获取搜索建议"""
        # 模拟DeepSeek返回搜索建议
        mock_deepseek_instance = MagicMock()
        mock_deepseek_instance._make_request.return_value = '["AI技术", "人工智能", "机器学习"]'
        mock_deepseek.return_value = mock_deepseek_instance
        
        suggestions = self.service.get_search_suggestions("什么是AI？")
        
        self.assertEqual(len(suggestions), 3)
        self.assertIn("AI技术", suggestions)
        self.assertIn("人工智能", suggestions)
        self.assertIn("机器学习", suggestions)
    
    def test_enrich_search_results(self):
        """测试搜索结果丰富化"""
        search_results = [
            {'url': 'http://test1.com', 'title': '原始标题1', 'content': '原始内容1'},
            {'url': 'http://test2.com', 'title': '原始标题2', 'content': '原始内容2'}
        ]
        
        crawled_content = [
            {'url': 'http://test1.com', 'title': '爬取标题1', 'content': '爬取内容1', 'metadata': {}},
            {'url': 'http://test3.com', 'title': '爬取标题3', 'content': '爬取内容3', 'metadata': {}}  # 不匹配的URL
        ]
        
        enriched_results = self.service._enrich_search_results(search_results, crawled_content)
        
        self.assertEqual(len(enriched_results), 2)
        # 第一个结果应该被丰富化
        self.assertEqual(enriched_results[0]['title'], '爬取标题1')
        self.assertEqual(enriched_results[0]['content'], '爬取内容1')
        # 第二个结果保持原样
        self.assertEqual(enriched_results[1]['title'], '原始标题2')
        self.assertEqual(enriched_results[1]['content'], '原始内容2')

if __name__ == '__main__':
    unittest.main()
