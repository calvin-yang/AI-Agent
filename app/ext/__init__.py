import os
from flask_redis import FlaskRedis
from flask_socketio import SocketIO
from celery import Celery
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('.env')

# 初始化Flask扩展实例
redis_store = FlaskRedis(decode_responses=True)
socketio = SocketIO()
celery = Celery()

def init_extensions(app):
    """初始化所有Flask扩展"""
    # 初始化Redis
    redis_store.init_app(app)
    
    # 初始化Celery
    celery.conf.update(
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND'],
        task_serializer=app.config['CELERY_TASK_SERIALIZER'],
        result_serializer=app.config['CELERY_RESULT_SERIALIZER'],
        accept_content=app.config['CELERY_ACCEPT_CONTENT'],
        timezone=app.config['CELERY_TIMEZONE'],
        enable_utc=app.config['CELERY_ENABLE_UTC'],
    )
    
    # 加载Celery配置
    celery.config_from_object('app.celeryconfig')
    
    # 设置Celery任务上下文
    class ContextTask(celery.Task):
        """确保任务在Flask应用上下文中运行"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    
    # 初始化SocketIO
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
    
    socketio.init_app(
        app,
        cors_allowed_origins="*",
        async_mode=async_mode,
        message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'],
        channel=app.config['SOCKETIO_CHANNEL']
    )
    
    # 将扩展实例添加到app对象中
    app.redis = redis_store
    app.celery = celery
    app.socketio = socketio
