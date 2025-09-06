#!/usr/bin/env python3
"""
macOS专用的Celery Worker启动脚本
解决macOS上的fork()线程安全问题
"""

import os
import sys
from dotenv import load_dotenv

def main():
    """主函数"""
    print("🍎 启动macOS兼容的Celery Worker...")
    
    # 加载环境变量
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print("✅ 已加载环境变量")
    else:
        print("⚠️  未找到.env文件，使用系统环境变量")
    
    # 检查必要的环境变量
    if not os.getenv('DEEPSEEK_API_KEY'):
        print("❌ 错误：未设置DEEPSEEK_API_KEY环境变量")
        print("   请在.env文件中设置或通过环境变量设置")
        sys.exit(1)
    
    # 显示配置信息
    print(f"   DEEPSEEK_API_KEY: {'已设置' if os.getenv('DEEPSEEK_API_KEY') else '未设置'}")
    print(f"   CELERY_BROKER_URL: {os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')}")
    print(f"   CELERY_RESULT_BACKEND: {os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')}")
    
    try:
        # 导入并启动Celery Worker
        from app.ext import celery
        
        # 确保Celery配置已加载
        celery.config_from_object('app.celeryconfig')
        
        # 初始化MongoDB连接（在Worker启动时）
        print("🔗 初始化MongoDB连接...")
        try:
            from mongoengine import connect
            from app.config import Config
            connect(host=Config.MONGODB_HOST)
            print("✅ MongoDB连接初始化成功")
        except Exception as e:
            print(f"⚠️ MongoDB连接初始化失败: {e}")
            print("   任务执行时会尝试重新连接")
        
        # 显示已注册的任务
        registered_tasks = list(celery.tasks.keys())
        schedule_tasks = [task for task in registered_tasks if 'schedules' in task]
        
        print("🚀 macOS兼容的Celery Worker已启动")
        print(f"   已注册任务数量: {len(registered_tasks)}")
        print(f"   Schedules任务: {len(schedule_tasks)}")
        if schedule_tasks:
            print("   任务列表:")
            for task in schedule_tasks:
                print(f"     - {task}")
        print("   使用solo模式避免macOS fork()问题")
        print("   等待任务...")
        print("   按 Ctrl+C 停止")
        print("=" * 50)
        
        # 启动Worker - 强制使用solo模式
        celery.worker_main([
            'worker', 
            '--loglevel=info', 
            '--pool=solo',  # 使用solo模式
            '--concurrency=1'  # solo模式下只能使用1个并发
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Worker已停止")
    except Exception as e:
        print(f"❌ Worker启动失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
