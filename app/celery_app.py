from celery import Celery

def make_celery(app=None):
    """创建Celery应用"""
    if app:
        # 从Flask应用配置中读取Celery配置
        celery = Celery(
            app.import_name,
            broker=app.config['CELERY_BROKER_URL'],
            backend=app.config['CELERY_RESULT_BACKEND']
        )
        
        # 加载Celery配置
        celery.config_from_object('app.celeryconfig')
        
        # 更新Flask特定的Celery配置
        celery.conf.update(
            task_serializer=app.config['CELERY_TASK_SERIALIZER'],
            result_serializer=app.config['CELERY_RESULT_SERIALIZER'],
            accept_content=app.config['CELERY_ACCEPT_CONTENT'],
            timezone=app.config['CELERY_TIMEZONE'],
            enable_utc=app.config['CELERY_ENABLE_UTC'],
        )
    else:
        # 如果没有Flask应用，使用默认配置（用于独立启动Worker）
        from app.config import Config
        celery = Celery(
            'ai_agent',
            broker=Config.CELERY_BROKER_URL,
            backend=Config.CELERY_RESULT_BACKEND
        )
        
        # 加载Celery配置
        celery.config_from_object('app.celeryconfig')
        
        # 更新默认配置
        celery.conf.update(
            task_serializer=Config.CELERY_TASK_SERIALIZER,
            result_serializer=Config.CELERY_RESULT_SERIALIZER,
            accept_content=Config.CELERY_ACCEPT_CONTENT,
            timezone=Config.CELERY_TIMEZONE,
            enable_utc=Config.CELERY_ENABLE_UTC,
        )
    
    if app:
        class ContextTask(celery.Task):
            """确保任务在Flask应用上下文中运行"""
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = ContextTask
    
    return celery
