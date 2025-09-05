from flask import Blueprint, render_template, request, jsonify
from app.services.ai_agent_service import AIAgentService

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
def index():
    """聊天页面"""
    return render_template('chat.html')

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': '问题不能为空'
            }), 400
        
        # 使用AI Agent处理问题
        ai_agent = AIAgentService()
        result = ai_agent.process_question(question)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'处理请求时发生错误: {str(e)}'
        }), 500

@chat_bp.route('/suggestions', methods=['POST'])
def get_suggestions():
    """获取搜索建议"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': '问题不能为空'
            }), 400
        
        # 获取搜索建议
        ai_agent = AIAgentService()
        suggestions = ai_agent.get_search_suggestions(question)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'获取建议时发生错误: {str(e)}'
        }), 500
