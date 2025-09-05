from celery import Celery

def make_celery(app=None):
    """创建Celery应用"""
    if app:
        # 从Flask应用配置中读取Celery配置
        celery = Celery(
            app.import_name,
            broker=app.config['CELERY_BROKER_URL'],
            backend=app.config['CELERY_RESULT_BACKEND'],
            include=['app.tasks']
        )
        
        # 更新Celery配置
        celery.conf.update(
            task_serializer=app.config['CELERY_TASK_SERIALIZER'],
            result_serializer=app.config['CELERY_RESULT_SERIALIZER'],
            accept_content=app.config['CELERY_ACCEPT_CONTENT'],
            timezone=app.config['CELERY_TIMEZONE'],
            enable_utc=app.config['CELERY_ENABLE_UTC'],
            task_track_started=True,
            task_time_limit=300,  # 5分钟超时
            task_soft_time_limit=240,  # 4分钟软超时
            worker_prefetch_multiplier=1,
            task_acks_late=True,
            worker_disable_rate_limits=False,
        )
    else:
        # 如果没有Flask应用，使用默认配置（用于独立启动Worker）
        from app.config import Config
        celery = Celery(
            'ai_agent',
            broker=Config.CELERY_BROKER_URL,
            backend=Config.CELERY_RESULT_BACKEND,
            include=['app.tasks']
        )
        
        # 更新Celery配置
        celery.conf.update(
            task_serializer=Config.CELERY_TASK_SERIALIZER,
            result_serializer=Config.CELERY_RESULT_SERIALIZER,
            accept_content=Config.CELERY_ACCEPT_CONTENT,
            timezone=Config.CELERY_TIMEZONE,
            enable_utc=Config.CELERY_ENABLE_UTC,
            task_track_started=True,
            task_time_limit=300,  # 5分钟超时
            task_soft_time_limit=240,  # 4分钟软超时
            worker_prefetch_multiplier=1,
            task_acks_late=True,
            worker_disable_rate_limits=False,
        )
    
    if app:
        class ContextTask(celery.Task):
            """确保任务在Flask应用上下文中运行"""
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = ContextTask
    
    return celery
