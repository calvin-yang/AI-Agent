from flask import Blueprint, render_template, request, jsonify, g
from app.services.ai_agent_service import AIAgentService
from app.models.user import User, ChatSession
from app.decorators.auth import optional_wallet_auth
from app.schedules.chat_tasks import process_question_async
import json

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
def index():
    """聊天页面"""
    return render_template('chat.html')

@chat_bp.route('/chat', methods=['POST'])
@optional_wallet_auth
def chat():
    """处理聊天请求 - 新版本，支持会话记录"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        session_id = data.get('session_id', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': '问题不能为空'
            }), 400
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': '会话ID不能为空'
            }), 400
        
        # 如果用户已登录，先保存用户消息到会话
        if g.current_user:
            user = User.get_by_wallet_address(g.current_user['wallet_address'])
            if user:
                session = ChatSession.get_by_session_id(session_id, user=user)
                if session:
                    # 添加用户消息到会话
                    session.add_message(
                        message_type='user',
                        content=question
                    )
        
        # 启动异步任务处理问题
        task = process_question_async.delay(question, session_id)
        
        return jsonify({
            'success': True,
            'data': {
                'task_id': task.id,
                'session_id': session_id,
                'message': '问题已提交，正在处理中...'
            }
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
