import requests
import json
from flask import current_app
from typing import Dict, List, Optional

class DeepSeekService:
    """DeepSeek API服务类"""
    
    def __init__(self):
        self.api_key = current_app.config['DEEPSEEK_API_KEY']
        self.base_url = current_app.config['DEEPSEEK_BASE_URL']
        self.model = current_app.config['DEEPSEEK_MODEL']
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def analyze_question(self, question: str) -> Dict:
        """
        分析用户问题，判断是否需要联网搜索
        
        Args:
            question: 用户问题
            
        Returns:
            Dict: 包含是否需要搜索和搜索关键词的分析结果
        """
        system_prompt = """你是一个智能助手，需要分析用户的问题是否需要进行实时联网搜索。

请分析以下问题，并返回JSON格式的响应：
{
    "need_search": true/false,
    "search_keywords": "搜索关键词",
    "reason": "分析原因"
}

判断标准：
1. 如果问题涉及实时信息、最新新闻、当前事件、股票价格、天气等，需要搜索
2. 如果问题涉及历史知识、常识、理论等，不需要搜索
3. 如果问题模糊不清，建议搜索获取更多信息

请只返回JSON格式，不要其他内容。"""

        try:
            response = self._make_request([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ])
            
            # 解析JSON响应
            result = json.loads(response)
            return result
            
        except Exception as e:
            # 如果解析失败，返回默认需要搜索
            return {
                "need_search": True,
                "search_keywords": question,
                "reason": f"分析失败，默认进行搜索: {str(e)}"
            }
    
    def analyze_with_context(self, question: str, search_results: List[Dict]) -> str:
        """
        结合搜索结果分析问题并生成回答
        
        Args:
            question: 原始问题
            search_results: 搜索结果列表
            
        Returns:
            str: AI生成的回答
        """
        # 构建上下文
        context = "基于以下搜索结果，请回答用户的问题：\n\n"
        for i, result in enumerate(search_results, 1):
            context += f"搜索结果 {i}:\n"
            context += f"标题: {result.get('title', 'N/A')}\n"
            context += f"URL: {result.get('url', 'N/A')}\n"
            context += f"内容摘要: {result.get('content', 'N/A')}\n\n"
        
        system_prompt = """你是一个智能助手，请基于提供的搜索结果来回答用户的问题。

要求：
1. 仔细分析搜索结果中的相关信息
2. 提供准确、有用的回答
3. 如果搜索结果不足以回答问题，请说明
4. 引用相关的信息来源
5. 回答要简洁明了，重点突出

请用中文回答。"""

        try:
            response = self._make_request([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"问题: {question}\n\n{context}"}
            ])
            
            return response
            
        except Exception as e:
            return f"分析过程中出现错误: {str(e)}"
    
    def _make_request(self, messages: List[Dict]) -> str:
        """
        向DeepSeek API发送请求
        
        Args:
            messages: 消息列表
            
        Returns:
            str: API响应内容
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": current_app.config['AI_ANALYSIS_CONFIG']['temperature'],
            "max_tokens": 2000
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=120)
            response.raise_for_status()
            
            data = response.json()
            return data['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"DeepSeek API请求失败: {str(e)}")
        except KeyError as e:
            raise Exception(f"DeepSeek API响应格式错误: {str(e)}")
        except Exception as e:
            raise Exception(f"未知错误: {str(e)}")
