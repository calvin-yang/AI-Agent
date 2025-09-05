import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.deepseek_service import DeepSeekService

class TestDeepSeekService(unittest.TestCase):
    """DeepSeek服务测试类"""
    
    def setUp(self):
        """测试前准备"""
        with patch('app.services.deepseek_service.current_app') as mock_app:
            mock_app.config = {
                'DEEPSEEK_API_KEY': 'test-api-key',
                'DEEPSEEK_BASE_URL': 'https://api.deepseek.com/v1',
                'DEEPSEEK_MODEL': 'deepseek-chat',
                'AI_ANALYSIS_CONFIG': {'temperature': 0.7}
            }
            self.service = DeepSeekService()
    
    @patch('app.services.deepseek_service.requests.post')
    def test_analyze_question_need_search(self, mock_post):
        """测试分析问题需要搜索的情况"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': '{"need_search": true, "search_keywords": "最新新闻", "reason": "涉及实时信息"}'}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.service.analyze_question("今天有什么最新新闻？")
        
        self.assertTrue(result['need_search'])
        self.assertEqual(result['search_keywords'], "最新新闻")
        self.assertEqual(result['reason'], "涉及实时信息")
    
    @patch('app.services.deepseek_service.requests.post')
    def test_analyze_question_no_search(self, mock_post):
        """测试分析问题不需要搜索的情况"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': '{"need_search": false, "search_keywords": "", "reason": "历史知识问题"}'}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = self.service.analyze_question("什么是Python？")
        
        self.assertFalse(result['need_search'])
        self.assertEqual(result['reason'], "历史知识问题")
    
    @patch('app.services.deepseek_service.requests.post')
    def test_analyze_with_context(self, mock_post):
        """测试结合上下文分析"""
        # 模拟API响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': '根据搜索结果，这是一个关于AI的测试回答。'}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        search_results = [
            {'title': 'AI测试', 'url': 'http://test.com', 'content': '测试内容'}
        ]
        
        result = self.service.analyze_with_context("什么是AI？", search_results)
        
        self.assertIn("AI", result)
        mock_post.assert_called_once()
    
    def test_analyze_question_json_parse_error(self):
        """测试JSON解析错误的情况"""
        with patch.object(self.service, '_make_request', side_effect=Exception("解析失败")):
            result = self.service.analyze_question("测试问题")
            
            self.assertTrue(result['need_search'])
            self.assertEqual(result['search_keywords'], "测试问题")
            self.assertIn("分析失败", result['reason'])

if __name__ == '__main__':
    unittest.main()
