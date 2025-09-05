import os

class Config:
    """应用配置类"""
    
    # Flask基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # DeepSeek API配置
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY') or 'your-deepseek-api-key'
    DEEPSEEK_BASE_URL = 'https://api.deepseek.com/v1'
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
