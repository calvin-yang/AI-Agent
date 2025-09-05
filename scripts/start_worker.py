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
        from app.celery_app import make_celery
        
        # 创建Celery实例（使用默认配置）
        celery = make_celery()
        
        print("🚀 Celery Worker已启动")
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
