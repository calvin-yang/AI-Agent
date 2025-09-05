from flask import Blueprint, request, jsonify
from app.services.deepseek_service import DeepSeekService
from app.services.search_service import SearchService
from app.services.crawler_service import CrawlerService
from app.services.ai_agent_service import AIAgentService

api_bp = Blueprint('api', __name__)

@api_bp.route('/analyze', methods=['POST'])
def analyze_question():
    """分析问题是否需要搜索"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': '问题不能为空'
            }), 400
        
        deepseek_service = DeepSeekService()
        result = deepseek_service.analyze_question(question)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'分析问题时发生错误: {str(e)}'
        }), 500

@api_bp.route('/search', methods=['POST'])
def search():
    """搜索接口"""
    try:
        data = request.get_json()
        keywords = data.get('keywords', '').strip()
        
        if not keywords:
            return jsonify({
                'success': False,
                'error': '搜索关键词不能为空'
            }), 400
        
        search_service = SearchService()
        results = search_service.search(keywords)
        
        return jsonify({
            'success': True,
            'data': {
                'keywords': keywords,
                'results': results,
                'count': len(results)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'搜索时发生错误: {str(e)}'
        }), 500

@api_bp.route('/crawl', methods=['POST'])
def crawl():
    """爬取网页内容"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls or not isinstance(urls, list):
            return jsonify({
                'success': False,
                'error': 'URL列表不能为空'
            }), 400
        
        crawler_service = CrawlerService()
        results = crawler_service.crawl_multiple_urls(urls)
        
        return jsonify({
            'success': True,
            'data': {
                'urls': urls,
                'results': results,
                'count': len(results)
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'爬取网页时发生错误: {str(e)}'
        }), 500

@api_bp.route('/process', methods=['POST'])
def process_question():
    """完整的问题处理流程"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': '问题不能为空'
            }), 400
        
        ai_agent = AIAgentService()
        result = ai_agent.process_question(question)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'处理问题时发生错误: {str(e)}'
        }), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'success': True,
        'message': 'AI Agent服务运行正常',
        'status': 'healthy'
    })
