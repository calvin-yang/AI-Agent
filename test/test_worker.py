#!/usr/bin/env python3
"""
测试Worker启动
"""

import os
import sys
from dotenv import load_dotenv

def test_worker_startup():
    """测试Worker启动"""
    print("🧪 测试Worker启动...")
    
    # 加载环境变量
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print("✅ 已加载环境变量")
    
    try:
        # 测试服务类初始化
        print("🔄 测试服务类初始化...")
        
        from app.services.deepseek_service import DeepSeekService
        deepseek_service = DeepSeekService()
        print("✅ DeepSeekService初始化成功")
        
        from app.services.search_service import SearchService
        search_service = SearchService()
        print("✅ SearchService初始化成功")
        
        from app.services.crawler_service import CrawlerService
        crawler_service = CrawlerService()
        print("✅ CrawlerService初始化成功")
        
        from app.services.ai_agent_service import AIAgentService
        ai_agent_service = AIAgentService()
        print("✅ AIAgentService初始化成功")
        
        # 测试Celery实例创建
        print("🔄 测试Celery实例创建...")
        from app.ext import celery
        print("✅ Celery实例创建成功")
        
        # 测试任务注册
        print("🔄 测试任务注册...")
        from app.schedules.chat_tasks import process_question_async, get_suggestions_async
        print("✅ 任务导入成功")
        print(f"   已注册任务: {list(celery.tasks.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Worker启动测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 Worker启动测试")
    print("=" * 50)
    
    success = test_worker_startup()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Worker启动测试通过！")
        print("   所有服务类可以正常初始化")
        print("   Celery实例创建成功")
        print("   任务注册正常")
        print("\n💡 现在可以启动Worker:")
        print("   python celery_worker.py")
    else:
        print("❌ Worker启动测试失败")
        print("   请检查配置和环境变量")

if __name__ == '__main__':
    main()
