from typing import Dict, List
from app.services.deepseek_service import DeepSeekService
from app.services.search_service import SearchService
from app.services.crawler_service import CrawlerService

class AIAgentService:
    """AI Agent核心服务类"""
    
    def __init__(self):
        self.deepseek_service = DeepSeekService()
        self.search_service = SearchService()
        self.crawler_service = CrawlerService()
    
    def process_question(self, question: str) -> Dict:
        """
        处理用户问题的完整流程
        
        Args:
            question: 用户问题
            
        Returns:
            Dict: 包含回答和元数据的响应
        """
        try:
            # 步骤1: 分析问题是否需要联网搜索
            analysis_result = self.deepseek_service.analyze_question(question)
            
            if not analysis_result.get('need_search', False):
                # 不需要搜索，直接回答
                return self._direct_answer(question, analysis_result)
            
            # 步骤2: 进行联网搜索
            search_keywords = analysis_result.get('search_keywords', question)
            search_results = self.search_service.search(search_keywords)
            
            if not search_results:
                return {
                    'answer': '抱歉，无法找到相关的搜索结果来回答您的问题。',
                    'search_performed': True,
                    'search_keywords': search_keywords,
                    'sources': [],
                    'error': '搜索无结果'
                }
            
            # 步骤3: 爬取网页内容
            urls = [result['url'] for result in search_results if result.get('url')]
            crawled_content = self.crawler_service.crawl_multiple_urls(urls)
            
            # 步骤4: 结合搜索结果和爬取内容进行分析
            enriched_results = self._enrich_search_results(search_results, crawled_content)
            
            # 步骤5: AI分析并生成回答
            answer = self.deepseek_service.analyze_with_context(question, enriched_results)
            
            return {
                'answer': answer,
                'search_performed': True,
                'search_keywords': search_keywords,
                'sources': enriched_results,
                'analysis_reason': analysis_result.get('reason', '')
            }
            
        except Exception as e:
            return {
                'answer': f'处理问题时发生错误: {str(e)}',
                'search_performed': False,
                'search_keywords': '',
                'sources': [],
                'error': str(e)
            }
    
    def _direct_answer(self, question: str, analysis_result: Dict) -> Dict:
        """
        直接回答不需要搜索的问题
        
        Args:
            question: 用户问题
            analysis_result: 分析结果
            
        Returns:
            Dict: 回答结果
        """
        try:
            # 使用DeepSeek直接回答问题
            system_prompt = """你是一个智能助手，请直接回答用户的问题。要求回答准确、有用、简洁明了。请用中文回答。"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
            
            answer = self.deepseek_service._make_request(messages)
            
            return {
                'answer': answer,
                'search_performed': False,
                'search_keywords': '',
                'sources': [],
                'analysis_reason': analysis_result.get('reason', '问题不需要实时信息')
            }
            
        except Exception as e:
            return {
                'answer': f'回答问题时发生错误: {str(e)}',
                'search_performed': False,
                'search_keywords': '',
                'sources': [],
                'error': str(e)
            }
    
    def _enrich_search_results(self, search_results: List[Dict], crawled_content: List[Dict]) -> List[Dict]:
        """
        将搜索结果与爬取内容结合
        
        Args:
            search_results: 搜索结果
            crawled_content: 爬取的内容
            
        Returns:
            List[Dict]: 丰富后的结果
        """
        enriched_results = []
        
        # 创建URL到爬取内容的映射
        crawled_dict = {item['url']: item for item in crawled_content}
        
        for result in search_results:
            url = result.get('url', '')
            enriched_result = result.copy()
            
            # 如果有对应的爬取内容，使用爬取的内容
            if url in crawled_dict:
                crawled = crawled_dict[url]
                enriched_result.update({
                    'title': crawled.get('title', result.get('title', '')),
                    'content': crawled.get('content', result.get('content', '')),
                    'metadata': crawled.get('metadata', {}),
                    'content_length': crawled.get('content_length', 0)
                })
            
            enriched_results.append(enriched_result)
        
        return enriched_results
    
    def get_search_suggestions(self, question: str) -> List[str]:
        """
        获取搜索建议
        
        Args:
            question: 用户问题
            
        Returns:
            List[str]: 搜索建议列表
        """
        try:
            # 使用AI生成搜索建议
            system_prompt = """基于用户的问题，生成3-5个相关的搜索关键词建议。每个建议应该简洁明了，能够帮助找到相关信息。

请以JSON数组格式返回，例如：["关键词1", "关键词2", "关键词3"]"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"问题: {question}"}
            ]
            
            response = self.deepseek_service._make_request(messages)
            
            # 尝试解析JSON
            import json
            suggestions = json.loads(response)
            
            if isinstance(suggestions, list):
                return suggestions[:5]  # 最多返回5个建议
            
            return []
            
        except Exception as e:
            print(f"生成搜索建议失败: {str(e)}")
            return []
