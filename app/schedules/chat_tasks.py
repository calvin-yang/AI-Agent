"""
聊天相关任务 - 从原tasks.py迁移
"""
from app.services.ai_agent_service import AIAgentService
from flask_socketio import emit
from flask import current_app
import traceback

# 导入celery实例
from app.ext import celery

@celery.task(bind=True)
def process_question_async(self, question, session_id):
    """
    异步处理用户问题
    
    Args:
        question: 用户问题
        session_id: 会话ID
        
    Returns:
        dict: 处理结果
    """
    try:
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={'status': '开始分析问题...', 'progress': 10}
        )
        
        # 创建AI Agent服务实例
        ai_agent = AIAgentService()
        
        # 分析问题
        self.update_state(
            state='PROGRESS',
            meta={'status': '分析问题是否需要搜索...', 'progress': 20}
        )
        
        result = ai_agent.process_question(question)
        
        # 更新最终状态
        self.update_state(
            state='SUCCESS',
            meta={
                'status': '处理完成',
                'progress': 100,
                'result': result
            }
        )
        
        return {
            'status': 'SUCCESS',
            'result': result,
            'session_id': session_id
        }
        
    except Exception as e:
        # 更新错误状态
        self.update_state(
            state='FAILURE',
            meta={
                'status': f'处理失败: {str(e)}',
                'progress': 0,
                'error': str(e)
            }
        )
        
        return {
            'status': 'FAILURE',
            'error': str(e),
            'session_id': session_id
        }

@celery.task(bind=True)
def get_suggestions_async(self, question, session_id):
    """
    异步获取搜索建议
    
    Args:
        question: 用户问题
        session_id: 会话ID
        
    Returns:
        dict: 建议结果
    """
    try:
        self.update_state(
            state='PROGRESS',
            meta={'status': '生成搜索建议...', 'progress': 50}
        )
        
        ai_agent = AIAgentService()
        suggestions = ai_agent.get_search_suggestions(question)
        
        self.update_state(
            state='SUCCESS',
            meta={
                'status': '建议生成完成',
                'progress': 100,
                'suggestions': suggestions
            }
        )
        
        return {
            'status': 'SUCCESS',
            'suggestions': suggestions,
            'session_id': session_id
        }
        
    except Exception as e:
        self.update_state(
            state='FAILURE',
            meta={
                'status': f'生成建议失败: {str(e)}',
                'progress': 0,
                'error': str(e)
            }
        )
        
        return {
            'status': 'FAILURE',
            'error': str(e),
            'session_id': session_id
        }

def send_socketio_message(response, session_id):
    """发送SocketIO消息的辅助函数"""
    try:
        print(f"🚀 准备发送SocketIO消息...")
        print(f"   会话ID: {session_id}")
        print(f"   响应内容: {response}")
        
        # 直接使用SocketIO发送消息
        from flask_socketio import SocketIO
        from app.config import Config
        
        # 创建SocketIO实例
        socketio = SocketIO(message_queue=Config.SOCKETIO_MESSAGE_QUEUE, channel=Config.SOCKETIO_CHANNEL)
        print(f"📡 SocketIO实例已创建")
        
        socketio.emit('task_update', response, room=session_id)
        print(f"✅ SocketIO消息已发送")
        print(f"   发送到房间: {session_id}")
        print(f"   消息内容: {response}")
    except Exception as e:
        print(f"❌ SocketIO发送失败: {str(e)}")
        import traceback
        traceback.print_exc()

# 任务状态回调
@celery.task(bind=True)
def task_status_callback(self, task_id, session_id):
    """
    任务状态回调，用于实时更新前端
    
    Args:
        task_id: 任务ID
        session_id: 会话ID
    """
    import time
    
    try:
        print(f"🔄 开始监控任务状态: {task_id}")
        
        # 持续监控任务直到完成
        while True:
            task = celery.AsyncResult(task_id)
            print(f"🔍 检查任务状态: {task.state}")
            
            if task.state == 'PENDING':
                response = {
                    'task_id': task_id,
                    'state': task.state,
                    'status': '等待处理...',
                    'progress': 0
                }
            elif task.state == 'PROGRESS':
                response = {
                    'task_id': task_id,
                    'state': task.state,
                    'status': task.info.get('status', '处理中...'),
                    'progress': task.info.get('progress', 0)
                }
            elif task.state == 'SUCCESS':
                # 获取任务结果
                task_result = task.info.get('result', {})
                print(f"🔍 调试 - 任务结果: {task_result}")
                print(f"🔍 调试 - 任务结果类型: {type(task_result)}")
                
                if isinstance(task_result, dict) and 'result' in task_result:
                    # 如果result字段存在，使用它
                    actual_result = task_result['result']
                    print(f"🔍 调试 - 使用嵌套result: {actual_result}")
                else:
                    # 否则直接使用task_result
                    actual_result = task_result
                    print(f"🔍 调试 - 直接使用task_result: {actual_result}")
                    
                response = {
                    'task_id': task_id,
                    'state': task.state,
                    'status': '处理完成',
                    'progress': 100,
                    'result': actual_result
                }
                print(f"🔍 调试 - 最终响应: {response}")
                
                # 发送完成消息
                send_socketio_message(response, session_id)
                print(f"✅ 任务完成，监控结束")
                break
                
            elif task.state == 'FAILURE':
                response = {
                    'task_id': task_id,
                    'state': task.state,
                    'status': '处理失败',
                    'progress': 0,
                    'error': task.info.get('error', '未知错误')
                }
                # 发送失败消息
                send_socketio_message(response, session_id)
                print(f"❌ 任务失败，监控结束")
                break
            else:
                # 其他状态，继续等待
                response = {
                    'task_id': task_id,
                    'state': task.state,
                    'status': f'状态: {task.state}',
                    'progress': 0
                }
            
            # 发送状态更新
            send_socketio_message(response, session_id)
            
            # 如果任务还在进行中，等待一段时间再检查
            if task.state in ['PENDING', 'PROGRESS']:
                time.sleep(1)  # 等待1秒
            else:
                break
        
        return response
        
    except Exception as e:
        error_response = {
            'task_id': task_id,
            'state': 'FAILURE',
            'status': '状态更新失败',
            'progress': 0,
            'error': str(e)
        }
        
        # 发送错误消息
        send_socketio_message(error_response, session_id)
        print(f"❌ 监控任务出错: {str(e)}")
        
        return error_response
