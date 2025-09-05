import unittest
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

class TestApp(unittest.TestCase):
    """Flask应用测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_index_page(self):
        """测试首页"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI Agent', response.data)
    
    def test_chat_endpoint_empty_question(self):
        """测试聊天接口 - 空问题"""
        response = self.client.post('/chat', 
                                  json={'question': ''},
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('问题不能为空', data['error'])
    
    def test_chat_endpoint_valid_question(self):
        """测试聊天接口 - 有效问题"""
        with unittest.mock.patch('app.blueprints.chat.AIAgentService') as mock_ai_agent:
            # 模拟AI Agent返回结果
            mock_instance = mock_ai_agent.return_value
            mock_instance.process_question.return_value = {
                'answer': '这是一个测试回答',
                'search_performed': False,
                'search_keywords': '',
                'sources': [],
                'analysis_reason': '测试原因'
            }
            
            response = self.client.post('/chat',
                                      json={'question': '测试问题'},
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['answer'], '这是一个测试回答')
    
    def test_suggestions_endpoint_empty_question(self):
        """测试建议接口 - 空问题"""
        response = self.client.post('/suggestions',
                                  json={'question': ''},
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('问题不能为空', data['error'])
    
    def test_suggestions_endpoint_valid_question(self):
        """测试建议接口 - 有效问题"""
        with unittest.mock.patch('app.blueprints.chat.AIAgentService') as mock_ai_agent:
            # 模拟AI Agent返回建议
            mock_instance = mock_ai_agent.return_value
            mock_instance.get_search_suggestions.return_value = ['建议1', '建议2', '建议3']
            
            response = self.client.post('/suggestions',
                                      json={'question': '测试问题'},
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(len(data['suggestions']), 3)
    
    def test_api_health_check(self):
        """测试API健康检查"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['status'], 'healthy')
    
    def test_api_analyze_endpoint(self):
        """测试API分析接口"""
        with unittest.mock.patch('app.blueprints.api.DeepSeekService') as mock_deepseek:
            # 模拟DeepSeek服务返回结果
            mock_instance = mock_deepseek.return_value
            mock_instance.analyze_question.return_value = {
                'need_search': True,
                'search_keywords': '测试关键词',
                'reason': '需要搜索'
            }
            
            response = self.client.post('/api/analyze',
                                      json={'question': '测试问题'},
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertTrue(data['data']['need_search'])
    
    def test_api_search_endpoint(self):
        """测试API搜索接口"""
        with unittest.mock.patch('app.blueprints.api.SearchService') as mock_search:
            # 模拟搜索服务返回结果
            mock_instance = mock_search.return_value
            mock_instance.search.return_value = [
                {'url': 'http://test.com', 'title': '测试标题', 'content': '测试内容'}
            ]
            
            response = self.client.post('/api/search',
                                      json={'keywords': '测试关键词'},
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(len(data['data']['results']), 1)
    
    def test_api_crawl_endpoint(self):
        """测试API爬取接口"""
        with unittest.mock.patch('app.blueprints.api.CrawlerService') as mock_crawler:
            # 模拟爬虫服务返回结果
            mock_instance = mock_crawler.return_value
            mock_instance.crawl_multiple_urls.return_value = [
                {'url': 'http://test.com', 'title': '测试标题', 'content': '测试内容'}
            ]
            
            response = self.client.post('/api/crawl',
                                      json={'urls': ['http://test.com']},
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(len(data['data']['results']), 1)
    
    def test_api_process_endpoint(self):
        """测试API处理接口"""
        with unittest.mock.patch('app.blueprints.api.AIAgentService') as mock_ai_agent:
            # 模拟AI Agent返回结果
            mock_instance = mock_ai_agent.return_value
            mock_instance.process_question.return_value = {
                'answer': '测试回答',
                'search_performed': False,
                'search_keywords': '',
                'sources': []
            }
            
            response = self.client.post('/api/process',
                                      json={'question': '测试问题'},
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['answer'], '测试回答')

if __name__ == '__main__':
    unittest.main()
