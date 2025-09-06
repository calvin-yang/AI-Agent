"""
Celery配置文件
"""
from celery.schedules import crontab

# 导入的任务模块
CELERY_IMPORTS = (
    'app.schedules.alert',
    'app.schedules.chat_tasks',
    'app.schedules.project.nftfair_task',
    'app.schedules.user_task',  # 用户相关任务
    # 'app.schedules.project.other_project_task',  # 其他项目任务（待添加）
)

# 定时任务配置
CELERYBEAT_SCHEDULE = {
    # 系统健康检查 - 每5分钟执行一次
    'system-health-check': {
        'task': 'app.schedules.alert.check_system_health',
        'schedule': crontab(minute='*/5'),
    },
    
    # NFT数据同步 - 每小时执行一次
    'nft-data-sync': {
        'task': 'app.schedules.project.nftfair_task.sync_nft_data',
        'schedule': crontab(minute=0),  # 每小时的第0分钟执行
    },
    
    # 每日告警检查 - 每天上午9点执行
    'daily-alert-check': {
        'task': 'app.schedules.alert.send_alert',
        'schedule': crontab(hour=9, minute=0),
        'args': ('系统每日健康检查', 'info'),
    },
    
    # 可以添加更多定时任务
    # 'weekly-report': {
    #     'task': 'app.schedules.reports.generate_weekly_report',
    #     'schedule': crontab(hour=8, minute=0, day_of_week=1),  # 每周一上午8点
    # },
}

# 任务路由配置
CELERY_ROUTES = {
    # 告警任务使用高优先级队列
    'app.schedules.alert.*': {'queue': 'alerts'},
    
    # 聊天任务使用默认队列
    'app.schedules.chat_tasks.*': {'queue': 'default'},
    
    # NFT相关任务使用专用队列
    'app.schedules.project.nftfair_task.*': {'queue': 'nft'},
    
    # 可以添加更多路由规则
    # 'app.schedules.reports.*': {'queue': 'reports'},
}

# 队列配置
CELERY_QUEUES = {
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
    'alerts': {
        'exchange': 'alerts',
        'routing_key': 'alerts',
    },
    'nft': {
        'exchange': 'nft',
        'routing_key': 'nft',
    },
    # 可以添加更多队列
    # 'reports': {
    #     'exchange': 'reports',
    #     'routing_key': 'reports',
    # },
}

# 任务执行配置
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_DEFAULT_EXCHANGE = 'default'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'default'

# 任务结果配置
CELERY_RESULT_EXPIRES = 3600  # 结果过期时间（秒）
CELERY_TASK_RESULT_EXPIRES = 3600

# 任务重试配置
CELERY_TASK_ANNOTATIONS = {
    '*': {
        'rate_limit': '100/m',  # 每分钟最多100个任务
        'time_limit': 300,      # 5分钟硬超时
        'soft_time_limit': 240, # 4分钟软超时
        'retry': True,
        'retry_kwargs': {
            'max_retries': 3,
            'countdown': 60,    # 重试间隔60秒
        },
    },
    # 特定任务的重试配置
    'app.schedules.alert.send_alert': {
        'rate_limit': '10/m',   # 告警任务限制更严格
        'time_limit': 60,       # 1分钟超时
    },
    'app.schedules.project.nftfair_task.sync_nft_data': {
        'rate_limit': '1/h',    # NFT同步任务每小时最多1次
        'time_limit': 1800,     # 30分钟超时
    },
}

# 工作进程配置
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_DISABLE_RATE_LIMITS = False

# 操作系统兼容性配置
import platform
if platform.system() == 'Darwin':  # macOS
    # macOS兼容性配置 - 避免fork()问题
    CELERY_WORKER_POOL = 'solo'  # 使用solo模式避免fork()问题
    CELERY_WORKER_CONCURRENCY = 1  # solo模式下只能使用1个并发
    print("🍎 检测到macOS，使用solo模式避免fork()问题")
else:
    # Linux/Windows使用默认配置
    CELERY_WORKER_POOL = 'prefork'  # 默认使用prefork模式
    CELERY_WORKER_CONCURRENCY = 4  # 默认4个并发

# 序列化配置
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

# 时区配置
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_ENABLE_UTC = True

# 监控配置
CELERY_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True
