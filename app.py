import os
from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_redis import FlaskRedis
from app.blueprints.chat import chat_bp
from app.blueprints.api import api_bp
from app.config import Config
from app.celery_app import make_celery
from app.tasks import process_question_async, get_suggestions_async, task_status_callback
import uuid

# 创建Flask应用
def create_app():
    # 设置模板和静态文件目录
    template_dir = os.path.join(os.path.dirname(__file__), 'app', 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'app', 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config.from_object(Config)
    
    # 初始化Flask-Redis
    redis_client = FlaskRedis(app)
    
    # 创建Celery应用
    celery = make_celery(app)
    
    # 将Celery实例和Redis客户端添加到应用上下文中，供其他模块使用
    app.celery = celery
    app.redis = redis_client
    
    # 任务已经在app.tasks中正确定义，无需额外设置
    
    # 创建SocketIO应用，使用Redis作为消息代理
    # 自动选择最佳的async_mode
    async_mode = 'threading'  # 默认使用threading模式
    
    # 尝试使用eventlet，如果失败则回退到threading
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        try:
            import gevent
            async_mode = 'gevent'
        except ImportError:
            async_mode = 'threading'
    
    print(f"🔧 使用SocketIO async_mode: {async_mode}")
    
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*", 
        async_mode=async_mode,
        message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'],
        channel=app.config['SOCKETIO_CHANNEL']
    )
    
    # 注册蓝图
    app.register_blueprint(chat_bp, url_prefix='/')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # SocketIO事件处理
    @socketio.on('connect')
    def handle_connect():
        """客户端连接事件"""
        session_id = str(uuid.uuid4())
        join_room(session_id)
        emit('connected', {'session_id': session_id})
        print(f"客户端已连接，会话ID: {session_id}")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """客户端断开连接事件"""
        print("客户端已断开连接")
    
    @socketio.on('join_room')
    def handle_join_room(data):
        """加入房间"""
        session_id = data.get('session_id')
        if session_id:
            join_room(session_id)
            emit('joined_room', {'session_id': session_id})
    
    @socketio.on('leave_room')
    def handle_leave_room(data):
        """离开房间"""
        session_id = data.get('session_id')
        if session_id:
            leave_room(session_id)
            emit('left_room', {'session_id': session_id})
    
    @socketio.on('ask_question')
    def handle_ask_question(data):
        """处理用户问题"""
        question = data.get('question', '').strip()
        session_id = data.get('session_id')
        
        if not question:
            emit('error', {'message': '问题不能为空'})
            return
        
        if not session_id:
            emit('error', {'message': '会话ID缺失'})
            return
        
        try:
            # 发送初始状态
            emit('task_started', {
                'status': '开始处理您的问题...',
                'progress': 0
            })
            
            # 启动异步任务
            task = process_question_async.delay(question, session_id)
            
            # 发送任务ID
            emit('task_id', {'task_id': task.id})
            
            # 启动状态监控任务
            task_status_callback.delay(task.id, session_id)
            
        except Exception as e:
            emit('error', {'message': f'启动任务失败: {str(e)}'})
    
    @socketio.on('get_suggestions')
    def handle_get_suggestions(data):
        """获取搜索建议"""
        question = data.get('question', '').strip()
        session_id = data.get('session_id')
        
        if not question:
            emit('error', {'message': '问题不能为空'})
            return
        
        if not session_id:
            emit('error', {'message': '会话ID缺失'})
            return
        
        try:
            # 启动异步任务
            task = get_suggestions_async.delay(question, session_id)
            
            # 发送任务ID
            emit('suggestion_task_id', {'task_id': task.id})
            
        except Exception as e:
            emit('error', {'message': f'获取建议失败: {str(e)}'})
    
    # 将socketio添加到app对象，以便在其他模块中使用
    app.socketio = socketio
    
    return app, socketio


if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=8002)
