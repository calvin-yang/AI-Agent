import os

class Config:
    """应用配置类"""
    
    # Flask基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Redis配置
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Flask-Redis配置
    REDIS_HOST = os.environ.get('REDIS_HOST') or 'localhost'
    REDIS_PORT = int(os.environ.get('REDIS_PORT') or 6379)
    REDIS_DB = int(os.environ.get('REDIS_DB') or 0)
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
    
    # Celery配置
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Asia/Shanghai'
    CELERY_ENABLE_UTC = True
    
    # SocketIO配置
    SOCKETIO_MESSAGE_QUEUE = os.environ.get('SOCKETIO_MESSAGE_QUEUE') or 'redis://localhost:6379/1'
    SOCKETIO_CHANNEL = os.environ.get('SOCKETIO_CHANNEL') or 'ai_agent_socketio'
    
    # DeepSeek API配置
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY') or 'your-deepseek-api-key'
    DEEPSEEK_BASE_URL = 'https://api.deepseek.com'
    DEEPSEEK_MODEL = 'deepseek-chat'
    
    # 搜索引擎配置
    SEARCH_ENGINES = {
        'duckduckgo': {
            'enabled': True,
            'weight': 0.6,
            'max_results': 5
        },
        'google': {
            'enabled': True,
            'weight': 0.4,
            'max_results': 3
        }
    }
    
    # 网页爬取配置
    CRAWLER_CONFIG = {
        'timeout': 10,
        'max_content_length': 50000,  # 提取的文本内容最大长度（字符数）
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # AI分析配置
    AI_ANALYSIS_CONFIG = {
        'max_context_length': 8000,
        'temperature': 0.7
    }
    
    # MongoDB配置
    MONGODB_HOST = os.environ.get('MONGODB_HOST') or "mongodb://admin:123456@127.0.0.1:27017/ai_agent_db?authSource=admin"
    
    # 钱包认证配置
    WALLET_AUTH_CONFIG = {
        'jwt_secret': os.environ.get('JWT_SECRET') or 'wallet-auth-secret-key',
        'jwt_expiration': 86400,  # 24小时
        'supported_chains': [1, 56, 137, 250],  # Ethereum, BSC, Polygon, Fantom
        'nonce_expiration': 300  # 5分钟
    }