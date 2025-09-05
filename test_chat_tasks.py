#!/usr/bin/env python3
"""
测试chat_tasks任务
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_chat_tasks_import():
    """测试chat_tasks模块导入"""
    print("🔄 测试chat_tasks模块导入...")
    
    try:
        from app.schedules.chat_tasks import (
            process_question_async, 
            get_suggestions_async, 
            task_status_callback
        )
        print("✅ chat_tasks模块导入成功")
        print("   可用任务:")
        print("     - process_question_async")
        print("     - get_suggestions_async") 
        print("     - task_status_callback")
        return True
        
    except Exception as e:
        print(f"❌ chat_tasks导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_celery_config():
    """测试Celery配置"""
    print("\n🔄 测试Celery配置...")
    
    try:
        from app.ext import celery
        
        # 确保配置已加载
        celery.config_from_object('app.celeryconfig')
        
        # 检查chat_tasks是否已注册
        registered_tasks = list(celery.tasks.keys())
        chat_tasks = [task for task in registered_tasks if 'chat_tasks' in task]
        
        print(f"✅ Celery配置加载成功")
        print(f"   已注册任务总数: {len(registered_tasks)}")
        print(f"   chat_tasks任务: {len(chat_tasks)}")
        
        if chat_tasks:
            print("   chat_tasks任务列表:")
            for task in chat_tasks:
                print(f"     - {task}")
        else:
            print("   ⚠️  未找到chat_tasks任务")
            
        return len(chat_tasks) > 0
        
    except Exception as e:
        print(f"❌ Celery配置测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_task_registration():
    """测试任务注册"""
    print("\n🔄 测试任务注册...")
    
    try:
        from app.schedules.chat_tasks import process_question_async
        from app.ext import celery
        
        # 检查任务是否已注册
        task_name = process_question_async.name
        if task_name in celery.tasks:
            print(f"✅ 任务 {task_name} 已注册")
            return True
        else:
            print(f"❌ 任务 {task_name} 未注册")
            return False
            
    except Exception as e:
        print(f"❌ 任务注册测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试chat_tasks...\n")
    
    success = True
    
    # 测试导入
    if not test_chat_tasks_import():
        success = False
    
    # 测试Celery配置
    if not test_celery_config():
        success = False
    
    # 测试任务注册
    if not test_task_registration():
        success = False
    
    print("\n" + "="*50)
    if success:
        print("🎉 所有测试通过！chat_tasks配置正确。")
        print("\n📋 现在可以启动Worker来监听chat_tasks:")
        print("   python celery_worker.py")
        print("   或")
        print("   python scripts/start_worker.py")
    else:
        print("❌ 测试失败，请检查配置。")
        sys.exit(1)

if __name__ == "__main__":
    main()
