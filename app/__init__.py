import os
from flask import Flask
from flask_cors import CORS
from app.ext import redis_store, celery, socketio, init_extensions
from app.blueprints.chat import chat_bp
from app.blueprints.api import api_bp
from app.config import Config
from app.socketio import register_socketio_events

def create_app(is_socketio=False):
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(Config)
    
    # 检查是否有测试配置
    if os.path.exists(os.path.join(app.root_path, 'testing.py')):
        print('加载测试配置')
        app.debug = True
        app.config.from_pyfile('testing.py')
    
    # 初始化扩展
    init_extensions(app)
    
    # 配置CORS
    cors = CORS(app, supports_credentials=True)
    cors.init_app(app, resources={r"/*": {"origins": "*"}})
    
    # 注册蓝图
    app.register_blueprint(chat_bp, url_prefix='/')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 配置SocketIO事件处理
    register_socketio_events(app)
    
    return app
