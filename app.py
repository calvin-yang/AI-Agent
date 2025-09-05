import os
from app import create_app
from app.ext import socketio

# 创建Flask应用
def create_app_with_socketio():
    """创建带有SocketIO的Flask应用"""
    # 设置模板和静态文件目录
    template_dir = os.path.join(os.path.dirname(__file__), 'app', 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), 'app', 'static')
    
    app = create_app()
    
    # 设置模板和静态文件目录
    app.template_folder = template_dir
    app.static_folder = static_dir
    
    return app, socketio


if __name__ == '__main__':
    app, socketio = create_app_with_socketio()
    socketio.run(app, debug=True, host='0.0.0.0', port=8002)
