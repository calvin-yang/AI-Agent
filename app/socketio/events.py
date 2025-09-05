"""
SocketIO事件处理器
处理WebSocket连接、断开、消息等事件
"""

import uuid
from flask_socketio import emit, join_room, leave_room
from .hooks import hook_manager
from app.schedules.chat_tasks import process_question_async, get_suggestions_async, task_status_callback


def register_socketio_events(app):
    """注册所有SocketIO事件处理器"""
    
    @app.socketio.on('connect')
    def handle_connect():
        """客户端连接事件"""
        try:
            # 执行连接前钩子
            if not hook_manager.execute_before_connect():
                emit('error', {'message': '连接被拒绝：权限验证失败'})
                return False
            
            # 生成会话ID
            session_id = str(uuid.uuid4())
            
            # 加入房间
            join_room(session_id)
            
            # 执行连接后钩子
            auth_hook = hook_manager.get_hook('auth')
            user_agent = auth_hook._get_auth().get_user_agent() if auth_hook else 'unknown'
            ip_address = auth_hook._get_auth().get_client_ip() if auth_hook else 'unknown'
            
            if not hook_manager.execute_after_connect(
                session_id, 
                user_agent=user_agent,
                ip_address=ip_address
            ):
                emit('error', {'message': '连接后处理失败'})
                return False
            
            # 发送连接成功消息
            emit('connected', {
                'session_id': session_id,
                'message': '连接成功'
            })
            
            print(f"✅ 客户端已连接，会话ID: {session_id}")
            return True
            
        except Exception as e:
            print(f"❌ 连接处理失败: {str(e)}")
            emit('error', {'message': f'连接失败: {str(e)}'})
            return False
    
    @app.socketio.on('disconnect')
    def handle_disconnect():
        """客户端断开连接事件"""
        try:
            # 获取当前会话ID（如果可用）
            auth_hook = hook_manager.get_hook('auth')
            session_id = auth_hook._get_auth().get_current_session_id() if auth_hook else None
            
            if session_id:
                # 执行断开连接前钩子
                hook_manager.execute_before_disconnect(session_id)
                
                # 执行断开连接后钩子
                hook_manager.execute_after_disconnect(session_id)
                
                print(f"✅ 会话已清理: {session_id}")
            
            print("👋 客户端已断开连接")
            
        except Exception as e:
            print(f"❌ 断开连接处理失败: {str(e)}")
    
    @app.socketio.on('join_room')
    def handle_join_room(data):
        """加入房间"""
        try:
            session_id = data.get('session_id')
            if not session_id:
                emit('error', {'message': '会话ID不能为空'})
                return
            
            # 权限验证
            if not auth.verify_room_access(session_id):
                emit('error', {'message': '无权访问该房间'})
                return
            
            join_room(session_id)
            emit('joined_room', {'session_id': session_id})
            print(f"✅ 客户端加入房间: {session_id}")
            
        except Exception as e:
            print(f"❌ 加入房间失败: {str(e)}")
            emit('error', {'message': f'加入房间失败: {str(e)}'})
    
    @app.socketio.on('leave_room')
    def handle_leave_room(data):
        """离开房间"""
        try:
            session_id = data.get('session_id')
            if not session_id:
                emit('error', {'message': '会话ID不能为空'})
                return
            
            leave_room(session_id)
            emit('left_room', {'session_id': session_id})
            print(f"✅ 客户端离开房间: {session_id}")
            
        except Exception as e:
            print(f"❌ 离开房间失败: {str(e)}")
            emit('error', {'message': f'离开房间失败: {str(e)}'})
    
    @app.socketio.on('ask_question')
    def handle_ask_question(data):
        """处理用户问题"""
        try:
            question = data.get('question', '').strip()
            session_id = data.get('session_id')
            
            # 输入验证
            if not question:
                emit('error', {'message': '问题不能为空'})
                return
            
            if not session_id:
                emit('error', {'message': '会话ID缺失'})
                return
            
            # 执行问题提交前钩子
            if not hook_manager.execute_before_question(session_id, question):
                emit('error', {'message': '无权提交此问题'})
                return
            
            # 发送初始状态
            emit('task_started', {
                'status': '开始处理您的问题...',
                'progress': 0,
                'question': question
            })
            
            # 启动异步任务
            task = process_question_async.delay(question, session_id)
            
            # 存储任务信息
            storage_hook = hook_manager.get_hook('storage')
            if storage_hook:
                storage = storage_hook._get_storage()
                storage.store_task(session_id, task.id, {
                    'question': question,
                    'status': 'started',
                    'created_at': storage.get_current_timestamp()
                })
            
            # 执行问题提交后钩子
            hook_manager.execute_after_question(session_id, question, task.id)
            
            # 发送任务ID
            emit('task_id', {'task_id': task.id})
            
            # 启动状态监控任务
            task_status_callback.delay(task.id, session_id)
            
            print(f"✅ 问题处理任务已启动: {task.id}")
            
        except Exception as e:
            print(f"❌ 问题处理失败: {str(e)}")
            emit('error', {'message': f'启动任务失败: {str(e)}'})
    
    @app.socketio.on('get_suggestions')
    def handle_get_suggestions(data):
        """获取搜索建议"""
        try:
            question = data.get('question', '').strip()
            session_id = data.get('session_id')
            
            # 输入验证
            if not question:
                emit('error', {'message': '问题不能为空'})
                return
            
            if not session_id:
                emit('error', {'message': '会话ID缺失'})
                return
            
            # 权限验证
            if not auth.verify_suggestion_access(session_id, question):
                emit('error', {'message': '无权获取建议'})
                return
            
            # 启动异步任务
            task = get_suggestions_async.delay(question, session_id)
            
            # 存储建议任务信息
            storage.store_suggestion_task(session_id, task.id, {
                'question': question,
                'status': 'started',
                'created_at': storage.get_current_timestamp()
            })
            
            # 发送任务ID
            emit('suggestion_task_id', {'task_id': task.id})
            
            print(f"✅ 建议获取任务已启动: {task.id}")
            
        except Exception as e:
            print(f"❌ 建议获取失败: {str(e)}")
            emit('error', {'message': f'获取建议失败: {str(e)}'})
    
    @app.socketio.on('get_history')
    def handle_get_history(data):
        """获取历史记录"""
        try:
            session_id = data.get('session_id')
            
            if not session_id:
                emit('error', {'message': '会话ID缺失'})
                return
            
            # 权限验证
            if not auth.verify_history_access(session_id):
                emit('error', {'message': '无权访问历史记录'})
                return
            
            # 获取历史记录
            history = storage.get_session_history(session_id)
            
            emit('history_data', {
                'session_id': session_id,
                'history': history
            })
            
            print(f"✅ 历史记录已发送: {session_id}")
            
        except Exception as e:
            print(f"❌ 获取历史记录失败: {str(e)}")
            emit('error', {'message': f'获取历史记录失败: {str(e)}'})
    
    @app.socketio.on('clear_history')
    def handle_clear_history(data):
        """清除历史记录"""
        try:
            session_id = data.get('session_id')
            
            if not session_id:
                emit('error', {'message': '会话ID缺失'})
                return
            
            # 权限验证
            if not auth.verify_history_access(session_id):
                emit('error', {'message': '无权清除历史记录'})
                return
            
            # 清除历史记录
            storage.clear_session_history(session_id)
            
            emit('history_cleared', {
                'session_id': session_id,
                'message': '历史记录已清除'
            })
            
            print(f"✅ 历史记录已清除: {session_id}")
            
        except Exception as e:
            print(f"❌ 清除历史记录失败: {str(e)}")
            emit('error', {'message': f'清除历史记录失败: {str(e)}'})
