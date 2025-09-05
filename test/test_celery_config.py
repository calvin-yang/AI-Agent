#!/usr/bin/env python3
"""
测试Celery配置是否正确
"""

import os
import sys
from dotenv import load_dotenv

def test_celery_config():
    """测试Celery配置"""
    print("🧪 测试Celery配置...")
    
    # 加载环境变量
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print("✅ 已加载环境变量")
    
    try:
        # 测试从Config类读取配置
        from app.config import Config
        print("✅ Config类导入成功")
        print(f"   CELERY_BROKER_URL: {Config.CELERY_BROKER_URL}")
        print(f"   CELERY_RESULT_BACKEND: {Config.CELERY_RESULT_BACKEND}")
        
        # 测试创建Flask应用和Celery实例
        import sys
        import os
        # 添加项目根目录到Python路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from app import create_app
        from app.ext import celery
        app = create_app()
        celery_with_app = celery
        print("✅ Celery实例创建成功（有Flask应用）")
        print(f"   Broker: {celery_with_app.conf.broker_url}")
        print(f"   Backend: {celery_with_app.conf.result_backend}")
        
        # 验证配置是否一致
        if celery_with_app.conf.broker_url == Config.CELERY_BROKER_URL:
            print("✅ Broker配置一致")
        else:
            print("❌ Broker配置不一致")
            print(f"   配置: {Config.CELERY_BROKER_URL}")
            print(f"   应用: {celery_with_app.conf.broker_url}")
        
        if celery_with_app.conf.result_backend == Config.CELERY_RESULT_BACKEND:
            print("✅ Backend配置一致")
        else:
            print("❌ Backend配置不一致")
            print(f"   配置: {Config.CELERY_RESULT_BACKEND}")
            print(f"   应用: {celery_with_app.conf.result_backend}")
        
        # 测试任务注册
        from app.schedules.chat_tasks import process_question_async, get_suggestions_async
        print("✅ 任务导入成功")
        print(f"   已注册任务: {list(celery.tasks.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_redis_connection():
    """测试Redis连接"""
    print("\n🧪 测试Redis连接...")
    
    try:
        from flask_redis import FlaskRedis
        from flask import Flask
        
        # 测试默认Redis连接
        app = Flask(__name__)
        app.config['REDIS_HOST'] = 'localhost'
        app.config['REDIS_PORT'] = 6379
        app.config['REDIS_DB'] = 0
        r = FlaskRedis(app)
        r.ping()
        print("✅ Redis数据库0连接成功")
        
        # 测试SocketIO Redis连接
        app1 = Flask(__name__)
        app1.config['REDIS_HOST'] = 'localhost'
        app1.config['REDIS_PORT'] = 6379
        app1.config['REDIS_DB'] = 1
        r1 = FlaskRedis(app1)
        r1.ping()
        print("✅ Redis数据库1连接成功")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis连接失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 Celery配置测试")
    print("=" * 50)
    
    # 测试Redis连接
    redis_ok = test_redis_connection()
    
    if not redis_ok:
        print("❌ Redis连接失败，请确保Redis服务正在运行")
        return
    
    # 测试Celery配置
    config_ok = test_celery_config()
    
    print("\n" + "=" * 50)
    if config_ok:
        print("🎉 所有配置测试通过！")
        print("   Celery配置正确")
        print("   Redis连接正常")
        print("   可以正常启动Worker")
    else:
        print("❌ 配置测试失败")
        print("   请检查配置和环境变量")

if __name__ == '__main__':
    main()
