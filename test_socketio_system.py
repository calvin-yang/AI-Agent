#!/usr/bin/env python3
"""
测试SocketIO扩展系统
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_imports():
    """测试导入"""
    print("🧪 测试SocketIO扩展系统导入...")
    
    try:
        from app.socketio import register_socketio_events, hook_manager
        print("✅ 主要模块导入成功")
        
        from app.socketio.auth import SocketIOAuth
        print("✅ 认证模块导入成功")
        
        from app.socketio.storage import SocketIOStorage
        print("✅ 存储模块导入成功")
        
        from app.socketio.hooks import SocketIOHook, HookManager
        print("✅ 钩子系统导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        return False

def test_hook_manager():
    """测试钩子管理器"""
    print("\n🧪 测试钩子管理器...")
    
    try:
        from app.socketio.hooks import hook_manager
        
        print(f"✅ 钩子管理器创建成功")
        print(f"   已注册钩子数量: {len(hook_manager.hooks)}")
        
        print("   钩子列表:")
        for hook in hook_manager.hooks:
            status = "✅ 启用" if hook.enabled else "❌ 禁用"
            print(f"     - {hook.name} ({hook.__class__.__name__}) - 优先级: {hook.priority} - {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ 钩子管理器测试失败: {str(e)}")
        return False

def test_auth_module():
    """测试认证模块"""
    print("\n🧪 测试认证模块...")
    
    try:
        from app.socketio.auth import SocketIOAuth
        
        auth = SocketIOAuth()
        print("✅ 认证模块创建成功")
        
        # 测试基本方法
        client_ip = auth.get_client_ip()
        user_agent = auth.get_user_agent()
        
        print(f"   客户端IP: {client_ip}")
        print(f"   用户代理: {user_agent}")
        
        return True
        
    except Exception as e:
        print(f"❌ 认证模块测试失败: {str(e)}")
        return False

def test_storage_module():
    """测试存储模块"""
    print("\n🧪 测试存储模块...")
    
    try:
        from app.socketio.storage import SocketIOStorage
        
        storage = SocketIOStorage()
        print("✅ 存储模块创建成功")
        
        # 测试基本方法
        timestamp = storage.get_current_timestamp()
        print(f"   当前时间戳: {timestamp}")
        
        return True
        
    except Exception as e:
        print(f"❌ 存储模块测试失败: {str(e)}")
        return False

def test_app_creation():
    """测试应用创建"""
    print("\n🧪 测试应用创建...")
    
    try:
        from app import create_app
        
        app = create_app()
        print("✅ Flask应用创建成功")
        
        # 检查扩展是否正确初始化
        if hasattr(app, 'redis'):
            print("✅ Redis扩展已初始化")
        
        if hasattr(app, 'celery'):
            print("✅ Celery扩展已初始化")
        
        if hasattr(app, 'socketio'):
            print("✅ SocketIO扩展已初始化")
        
        return True
        
    except Exception as e:
        print(f"❌ 应用创建测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试SocketIO扩展系统")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_hook_manager,
        test_auth_module,
        test_storage_module,
        test_app_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！SocketIO扩展系统工作正常")
        return True
    else:
        print("❌ 部分测试失败，请检查错误信息")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
