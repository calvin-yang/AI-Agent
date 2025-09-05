import os
from flask import Flask
from app.blueprints.chat import chat_bp
from app.blueprints.api import api_bp
from app.config import Config

def create_app():
    # 设置模板和静态文件目录
    template_dir = os.path.join(os.path.dirname(__file__), 'app', 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'app', 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    app.config.from_object(Config)

    # 注册蓝图
    app.register_blueprint(chat_bp, url_prefix='/')
    app.register_blueprint(api_bp, url_prefix='/api')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8002)
