#!/usr/bin/env python3
"""
异步AI Agent启动脚本
"""

import os
import sys
import subprocess
import time
from dotenv import load_dotenv

def check_redis():
    """检查Redis是否运行"""
    try:
        from flask_redis import FlaskRedis
        from flask import Flask
        app = Flask(__name__)
        app.config['REDIS_HOST'] = 'localhost'
        app.config['REDIS_PORT'] = 6379
        app.config['REDIS_DB'] = 0
        redis_client = FlaskRedis(app)
        redis_client.ping()
        return True
    except:
        return False

def start_redis():
    """启动Redis服务"""
    print("🔄 启动Redis服务...")
    try:
        if os.name == 'nt':  # Windows
            subprocess.Popen(['redis-server'], shell=True)
        else:  # Unix/Linux/macOS
            subprocess.Popen(['redis-server'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 等待Redis启动
        for i in range(10):
            if check_redis():
                print("✅ Redis服务已启动")
                return True
            time.sleep(1)
        
        print("❌ Redis启动失败")
        return False
    except Exception as e:
        print(f"❌ Redis启动失败: {str(e)}")
        return False

def start_celery_worker():
    """启动Celery Worker"""
    print("🔄 启动Celery Worker...")
    try:
        cmd = [sys.executable, '-m', 'celery', '-A', 'app.celery_app', 'worker', '--loglevel=info']
        return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"❌ Celery Worker启动失败: {str(e)}")
        return None

def main():
    """主函数"""
    print("🚀 启动异步AI Agent服务")
    print("=" * 50)
    
    # 切换到项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    print(f"✅ 切换到项目根目录: {project_root}")
    
    # 加载环境变量
    env_file = os.path.join(project_root, '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print("✅ 已加载环境变量")
    else:
        print("⚠️  未找到.env文件，请确保已配置DEEPSEEK_API_KEY")
    
    # 检查必要的环境变量
    if not os.getenv('DEEPSEEK_API_KEY'):
        print("❌ 错误：未设置DEEPSEEK_API_KEY环境变量")
        sys.exit(1)
    
    # 检查Redis
    if not check_redis():
        print("⚠️  Redis未运行，尝试启动...")
        if not start_redis():
            print("❌ 请手动启动Redis服务")
            print("   macOS: brew services start redis")
            print("   Ubuntu: sudo systemctl start redis")
            print("   Windows: 下载并启动Redis")
            sys.exit(1)
    
    # 启动Celery Worker
    celery_process = start_celery_worker()
    if not celery_process:
        print("❌ Celery Worker启动失败")
        sys.exit(1)
    
    print("✅ Celery Worker已启动")
    
    try:
        print("\n🚀 启动Flask应用...")
        print("   访问地址: http://localhost:8002")
        print("   按 Ctrl+C 停止服务")
        print("=" * 50)
        
        # 启动Flask应用
        import sys
        import os
        # 添加项目根目录到Python路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from app import create_app
        app, socketio = create_app()
        socketio.run(app, debug=True, host='0.0.0.0', port=8002)
        
    except KeyboardInterrupt:
        print("\n👋 正在停止服务...")
        if celery_process:
            celery_process.terminate()
        print("✅ 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        if celery_process:
            celery_process.terminate()
        sys.exit(1)

if __name__ == '__main__':
    main()
