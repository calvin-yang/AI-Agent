#!/usr/bin/env python3
"""
Celery Worker启动脚本
"""

import os
import sys
from dotenv import load_dotenv

def main():
    """主函数"""
    print("🔄 启动Celery Worker...")
    
    # 切换到项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    print(f"✅ 切换到项目根目录: {project_root}")
    
    # 加载环境变量
    env_file = os.path.join(project_root, '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print("✅ 已加载环境变量")
    
    # 检查必要的环境变量
    if not os.getenv('DEEPSEEK_API_KEY'):
        print("❌ 错误：未设置DEEPSEEK_API_KEY环境变量")
        sys.exit(1)
    
    try:
        # 启动Celery Worker
        from app.ext import celery
        
        # 确保Celery配置已加载
        celery.config_from_object('app.celeryconfig')
        
        # 显示已注册的任务
        registered_tasks = list(celery.tasks.keys())
        schedule_tasks = [task for task in registered_tasks if 'schedules' in task]
        
        print("🚀 Celery Worker已启动")
        print(f"   已注册任务数量: {len(registered_tasks)}")
        print(f"   Schedules任务: {len(schedule_tasks)}")
        if schedule_tasks:
            print("   任务列表:")
            for task in schedule_tasks:
                print(f"     - {task}")
        print("   等待任务...")
        print("   按 Ctrl+C 停止")
        print("=" * 50)
        
        # 启动Worker
        celery.worker_main(['worker', '--loglevel=info'])
        
    except KeyboardInterrupt:
        print("\n👋 Worker已停止")
    except Exception as e:
        print(f"❌ Worker启动失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
