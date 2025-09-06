"""
聊天相关任务 - 优化版本，直接使用SocketIO推送结果
"""
from app.services.ai_agent_service import AIAgentService
from flask import current_app
from app.ext import redis_store, celery, socketio
import traceback
import json

@celery.task(bind=True)
def process_question_async(self, question, session_id):
    """
    异步处理用户问题 - 优化版本，直接通过SocketIO推送结果
    
    Args:
        question: 用户问题
        session_id: 会话ID
        
    Returns:
        dict: 处理结果
    """
    try:
        print(f"🚀 开始处理问题: {question[:50]}...")
        
        # 发送开始处理的消息
        send_socketio_message({
            'task_id': self.request.id,
            'state': 'PROGRESS',
            'status': '开始分析问题...',
            'progress': 10
        }, session_id)
        
        # 创建AI Agent服务实例
        ai_agent = AIAgentService()
        
        # 发送分析状态
        send_socketio_message({
            'task_id': self.request.id,
            'state': 'PROGRESS',
            'status': '分析问题是否需要搜索...',
            'progress': 20
        }, session_id)
        
        # 处理问题
        result = ai_agent.process_question(question)
        
        # 保存AI回答到会话（如果用户已登录）
        try:
            save_ai_response_to_session.delay(session_id, result)
        except Exception as e:
            print(f"⚠️ 保存AI回答到会话失败: {str(e)}")
        
        # 直接通过SocketIO发送完成结果
        final_response = {
            'task_id': self.request.id,
            'state': 'SUCCESS',
            'status': '处理完成',
            'progress': 100,
            'result': result
        }
        
        send_socketio_message(final_response, session_id)
        print(f"✅ 问题处理完成，结果已推送: {session_id}")
        
        return {
            'status': 'SUCCESS',
            'result': result,
            'session_id': session_id
        }
        
    except Exception as e:
        print(f"❌ 处理问题失败: {str(e)}")
        traceback.print_exc()
        
        # 直接通过SocketIO发送错误结果
        error_response = {
            'task_id': self.request.id,
            'state': 'FAILURE',
            'status': f'处理失败: {str(e)}',
            'progress': 0,
            'error': str(e)
        }
        
        send_socketio_message(error_response, session_id)
        
        return {
            'status': 'FAILURE',
            'error': str(e),
            'session_id': session_id
        }

@celery.task(bind=True)
def get_suggestions_async(self, question, session_id):
    """
    异步获取搜索建议 - 优化版本，直接通过SocketIO推送结果
    
    Args:
        question: 用户问题
        session_id: 会话ID
        
    Returns:
        dict: 建议结果
    """
    try:
        print(f"🚀 开始生成搜索建议: {question[:50]}...")
        
        # 发送开始处理的消息
        send_socketio_message({
            'task_id': self.request.id,
            'state': 'PROGRESS',
            'status': '生成搜索建议...',
            'progress': 50
        }, session_id)
        
        ai_agent = AIAgentService()
        suggestions = ai_agent.get_search_suggestions(question)
        
        # 直接通过SocketIO发送完成结果
        final_response = {
            'task_id': self.request.id,
            'state': 'SUCCESS',
            'status': '建议生成完成',
            'progress': 100,
            'suggestions': suggestions
        }
        
        send_socketio_message(final_response, session_id)
        print(f"✅ 搜索建议生成完成，结果已推送: {session_id}")
        
        return {
            'status': 'SUCCESS',
            'suggestions': suggestions,
            'session_id': session_id
        }
        
    except Exception as e:
        print(f"❌ 生成搜索建议失败: {str(e)}")
        traceback.print_exc()
        
        # 直接通过SocketIO发送错误结果
        error_response = {
            'task_id': self.request.id,
            'state': 'FAILURE',
            'status': f'生成建议失败: {str(e)}',
            'progress': 0,
            'error': str(e)
        }
        
        send_socketio_message(error_response, session_id)
        
        return {
            'status': 'FAILURE',
            'error': str(e),
            'session_id': session_id
        }

def send_socketio_message(response, session_id):
    """发送SocketIO消息的辅助函数 - 直接使用SocketIO emit"""
    try:
        print(f"🚀 准备发送SocketIO消息: 会话ID<{session_id}>; 响应内容: <{response}>")
        
        # 直接导入并使用SocketIO实例
        socketio.emit('task_update', response, room=session_id)
    except Exception as e:
        print(f"❌ SocketIO发送失败: {str(e)}; ⚠️ 回退到Redis发布方式")
        try:
            message_data = {
                'event': 'task_update',
                'data': response,
                'room': session_id,
                'namespace': '/'
            }
            redis_store.publish('ai_agent_socketio', json.dumps(message_data))
        except Exception as redis_e:
            print(f"❌ Redis发布也失败: {str(redis_e)}")
        import traceback
        traceback.print_exc()


@celery.task(bind=True)
def save_ai_response_to_session(self, session_id, ai_result):
    """
    保存AI回答到会话
    
    Args:
        session_id: 会话ID
        ai_result: AI处理结果
        
    Returns:
        dict: 保存结果
    """
    try:
        # 直接使用MongoDB连接，应用上下文已在ContextTask中设置
        from app.models.user import ChatSession
        
        # 查找会话
        session = ChatSession.objects(session_id=session_id).first()
        if not session:
            print(f"⚠️ 会话不存在: {session_id}")
            return {'status': 'WARNING', 'message': '会话不存在'}
        
        # 提取AI回答内容
        answer_content = ""
        metadata = None
        
        if isinstance(ai_result, dict):
            answer_content = ai_result.get('answer', '')
            # 构建元数据
            metadata = {
                'search_performed': ai_result.get('search_performed', False),
                'search_keywords': ai_result.get('search_keywords', ''),
                'sources': ai_result.get('sources', [])
            }
        else:
            answer_content = str(ai_result)
        
        if not answer_content:
            print(f"⚠️ AI回答内容为空")
            return {'status': 'WARNING', 'message': 'AI回答内容为空'}
        
        # 添加AI消息到会话
        session.add_message(
            message_type='ai',
            content=answer_content,
            metadata=json.dumps(metadata) if metadata else None
        )
        
        print(f"✅ AI回答已保存到会话: {session_id}")
        return {'status': 'SUCCESS', 'message': 'AI回答已保存'}
        
    except Exception as e:
        print(f"❌ 保存AI回答失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return {'status': 'ERROR', 'message': str(e)}
