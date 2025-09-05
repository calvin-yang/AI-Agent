#!/usr/bin/env python3
"""
启动脚本 - 支持MongoDB和钱包认证功能
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_mongodb_connection():
    """检查MongoDB连接"""
    try:
        from pymongo import MongoClient
        from app.config import Config
        
        # 解析MongoDB连接字符串
        mongodb_host = Config.MONGODB_HOST
        client = MongoClient(mongodb_host, serverSelectionTimeoutMS=5000)
        client.server_info()  # 测试连接
        client.close()
        print("✅ MongoDB连接成功")
        return True
    except Exception as e:
        print(f"❌ MongoDB连接失败: {e}")
        return False

def check_dependencies():
    """检查依赖包"""
    required_packages = [
        'flask', 'flask_mongoengine', 'pymongo', 'mongoengine',
        'web3', 'eth_account', 'PyJWT'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def check_env_file():
    """检查环境变量文件"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  未找到.env文件，使用默认配置")
        print("建议复制env.example为.env并修改配置")
        return False
    
    print("✅ 找到.env配置文件")
    return True

def start_application():
    """启动应用"""
    print("\n🚀 启动AI Agent应用...")
    
    # 设置环境变量
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = 'development'
    
    try:
        # 启动Flask应用
        subprocess.run([sys.executable, 'app.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print("🔍 AI Agent 启动检查\n")
    
    # 1. 检查依赖包
    if not check_dependencies():
        return
    
    # 2. 检查环境配置
    check_env_file()
    
    # 3. 检查MongoDB连接
    if not check_mongodb_connection():
        print("\n💡 MongoDB连接失败，请检查：")
        print("   1. MongoDB服务是否运行")
        print("   2. 连接配置是否正确")
        print("   3. 用户名密码是否正确")
        print("   4. 网络连接是否正常")
        return
    
    # 4. 启动应用
    start_application()

if __name__ == "__main__":
    main()
