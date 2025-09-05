#!/usr/bin/env python3
"""
分布式AI Agent启动脚本
支持多实例部署和负载均衡
"""

import os
import sys
import subprocess
import time
import argparse
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

def start_web_instance(instance_id, port):
    """启动Web服务实例"""
    print(f"🔄 启动Web实例 {instance_id} (端口: {port})...")
    try:
        env = os.environ.copy()
        env['INSTANCE_ID'] = instance_id
        env['PORT'] = str(port)
        
        cmd = [sys.executable, 'app.py']
        return subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"❌ Web实例 {instance_id} 启动失败: {str(e)}")
        return None

def start_worker_instance(worker_id):
    """启动Worker实例"""
    print(f"🔄 启动Worker实例 {worker_id}...")
    try:
        env = os.environ.copy()
        env['WORKER_ID'] = worker_id
        
        cmd = [sys.executable, 'scripts/start_worker.py']
        return subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"❌ Worker实例 {worker_id} 启动失败: {str(e)}")
        return None

def start_flower():
    """启动Flower监控"""
    print("🔄 启动Flower监控...")
    try:
        cmd = [sys.executable, '-m', 'celery', '-A', 'app.ext', 'flower', '--port=5555']
        return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"❌ Flower启动失败: {str(e)}")
        return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='分布式AI Agent启动脚本')
    parser.add_argument('--instances', type=int, default=3, help='Web实例数量 (默认: 3)')
    parser.add_argument('--workers', type=int, default=3, help='Worker实例数量 (默认: 3)')
    parser.add_argument('--base-port', type=int, default=8002, help='基础端口号 (默认: 8002)')
    parser.add_argument('--no-flower', action='store_true', help='不启动Flower监控')
    parser.add_argument('--docker', action='store_true', help='使用Docker Compose启动')
    
    args = parser.parse_args()
    
    print("🚀 启动分布式AI Agent服务")
    print("=" * 50)
    print(f"Web实例数: {args.instances}")
    print(f"Worker实例数: {args.workers}")
    print(f"基础端口: {args.base_port}")
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
    
    # 如果使用Docker
    if args.docker:
        print("🐳 使用Docker Compose启动分布式服务...")
        try:
            subprocess.run(['docker-compose', '-f', 'docker-compose-distributed.yml', 'up', '-d'], check=True)
            print("✅ Docker服务已启动")
            print("   访问地址: http://localhost")
            print("   监控地址: http://localhost:5555")
            return
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker启动失败: {str(e)}")
            sys.exit(1)
    
    # 检查Redis
    if not check_redis():
        print("⚠️  Redis未运行，尝试启动...")
        if not start_redis():
            print("❌ 请手动启动Redis服务")
            sys.exit(1)
    
    # 启动Web实例
    web_processes = []
    for i in range(args.instances):
        port = args.base_port + i
        process = start_web_instance(f"web{i+1}", port)
        if process:
            web_processes.append(process)
        time.sleep(1)  # 避免端口冲突
    
    # 启动Worker实例
    worker_processes = []
    for i in range(args.workers):
        process = start_worker_instance(f"worker{i+1}")
        if process:
            worker_processes.append(process)
        time.sleep(1)
    
    # 启动Flower监控
    flower_process = None
    if not args.no_flower:
        flower_process = start_flower()
    
    print(f"\n✅ 分布式服务已启动")
    print(f"   Web实例: {len(web_processes)} 个")
    print(f"   Worker实例: {len(worker_processes)} 个")
    if flower_process:
        print(f"   监控地址: http://localhost:5555")
    print(f"   访问地址: http://localhost:{args.base_port}")
    print("   按 Ctrl+C 停止所有服务")
    print("=" * 50)
    
    try:
        # 等待所有进程
        while True:
            time.sleep(1)
            
            # 检查进程状态
            for i, process in enumerate(web_processes):
                if process.poll() is not None:
                    print(f"⚠️  Web实例 {i+1} 已停止")
            
            for i, process in enumerate(worker_processes):
                if process.poll() is not None:
                    print(f"⚠️  Worker实例 {i+1} 已停止")
            
            if flower_process and flower_process.poll() is not None:
                print("⚠️  Flower监控已停止")
                
    except KeyboardInterrupt:
        print("\n👋 正在停止所有服务...")
        
        # 停止所有进程
        for process in web_processes:
            if process.poll() is None:
                process.terminate()
        
        for process in worker_processes:
            if process.poll() is None:
                process.terminate()
        
        if flower_process and flower_process.poll() is None:
            flower_process.terminate()
        
        print("✅ 所有服务已停止")

if __name__ == '__main__':
    main()
