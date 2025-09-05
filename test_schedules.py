#!/usr/bin/env python3
"""
测试新的schedules目录结构
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_schedule_imports():
    """测试所有schedules模块的导入"""
    print("🔄 测试schedules模块导入...")
    
    try:
        # 测试基础模块
        from app.schedules import alert
        print("✅ alert模块导入成功")
        
        from app.schedules import chat_tasks
        print("✅ chat_tasks模块导入成功")
        
        from app.schedules import user_task
        print("✅ user_task模块导入成功")
        
        # 测试项目模块
        from app.schedules.project import nftfair_task
        print("✅ nftfair_task模块导入成功")
        
        # 测试Celery配置
        from app import celeryconfig
        print("✅ celeryconfig模块导入成功")
        
        print(f"✅ 已配置的任务模块: {celeryconfig.CELERY_IMPORTS}")
        print(f"✅ 已配置的定时任务: {list(celeryconfig.CELERYBEAT_SCHEDULE.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_celery_app():
    """测试Celery应用配置"""
    print("\n🔄 测试Celery应用配置...")
    
    try:
        from app.celery_app import make_celery
        from app.config import Config
        
        # 创建Celery实例
        celery = make_celery()
        print("✅ Celery实例创建成功")
        
        # 检查配置
        print(f"✅ Broker URL: {celery.conf.broker_url}")
        print(f"✅ Result Backend: {celery.conf.result_backend}")
        print(f"✅ 时区: {celery.conf.timezone}")
        
        # 检查任务注册
        registered_tasks = list(celery.tasks.keys())
        print(f"✅ 已注册任务数量: {len(registered_tasks)}")
        
        # 显示部分任务
        schedule_tasks = [task for task in registered_tasks if 'schedules' in task]
        print(f"✅ schedules任务: {schedule_tasks}")
        
        return True
        
    except Exception as e:
        print(f"❌ Celery配置测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试新的schedules目录结构...\n")
    
    success = True
    
    # 测试导入
    if not test_schedule_imports():
        success = False
    
    # 测试Celery配置
    if not test_celery_app():
        success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 所有测试通过！新的schedules目录结构工作正常。")
        print("\n📁 新的目录结构:")
        print("   app/schedules/")
        print("   ├── alert.py")
        print("   ├── chat_tasks.py")
        print("   ├── user_task.py")
        print("   └── project/")
        print("       └── nftfair_task.py")
        print("\n📋 配置文件:")
        print("   app/celeryconfig.py")
        print("\n✨ 现在可以轻松添加新的任务模块了！")
    else:
        print("❌ 测试失败，请检查配置。")
        sys.exit(1)

if __name__ == "__main__":
    main()
