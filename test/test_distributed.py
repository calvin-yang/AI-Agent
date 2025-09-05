#!/usr/bin/env python3
"""
分布式架构测试脚本
测试多实例之间的SocketIO通信
"""

import asyncio
import aiohttp
import time
import json
import socketio
from concurrent.futures import ThreadPoolExecutor
import statistics

class DistributedTester:
    def __init__(self, base_url="http://localhost", instances=3):
        self.base_url = base_url
        self.instances = instances
        self.socketio_clients = []
        self.results = []
    
    async def test_http_load_balancing(self, num_requests=30):
        """测试HTTP负载均衡"""
        print(f"🧪 测试HTTP负载均衡 ({num_requests} 个请求)...")
        
        questions = [
            "什么是人工智能？",
            "今天有什么新闻？",
            "Python有什么特点？",
            "如何学习编程？",
            "最新的科技趋势是什么？"
        ]
        
        # 生成测试问题列表
        test_questions = []
        for i in range(num_requests):
            test_questions.append(questions[i % len(questions)] + f" (请求 {i+1})")
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i, question in enumerate(test_questions):
                # 轮询不同的实例
                instance_port = 8002 + (i % self.instances)
                url = f"{self.base_url}:{instance_port}/api/process"
                task = self.send_http_request(session, url, question, i)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 统计结果
        successful_requests = [r for r in results if r.get('success', False)]
        failed_requests = [r for r in results if not r.get('success', False)]
        
        print(f"✅ HTTP负载均衡测试完成！")
        print(f"   总请求数: {num_requests}")
        print(f"   成功请求: {len(successful_requests)}")
        print(f"   失败请求: {len(failed_requests)}")
        print(f"   总耗时: {total_time:.2f} 秒")
        print(f"   平均响应时间: {total_time/num_requests:.2f} 秒")
        print(f"   吞吐量: {num_requests/total_time:.2f} 请求/秒")
        
        return {
            'total_requests': num_requests,
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'total_time': total_time,
            'throughput': num_requests/total_time
        }
    
    async def send_http_request(self, session, url, question, request_id):
        """发送HTTP请求"""
        try:
            async with session.post(url, 
                                  json={'question': question},
                                  timeout=aiohttp.ClientTimeout(total=30)) as response:
                result = await response.json()
                return {
                    'success': result.get('success', False),
                    'request_id': request_id,
                    'url': url,
                    'question': question
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'request_id': request_id,
                'url': url,
                'question': question
            }
    
    def test_socketio_distribution(self, num_clients=10):
        """测试SocketIO分布式通信"""
        print(f"🧪 测试SocketIO分布式通信 ({num_clients} 个客户端)...")
        
        def create_socketio_client(client_id):
            """创建SocketIO客户端"""
            sio = socketio.Client()
            results = {'connected': False, 'messages_received': 0, 'errors': []}
            
            @sio.event
            def connect():
                results['connected'] = True
                print(f"✅ 客户端 {client_id} 已连接")
            
            @sio.event
            def disconnect():
                print(f"👋 客户端 {client_id} 已断开")
            
            @sio.event
            def connected(data):
                results['session_id'] = data.get('session_id')
                print(f"✅ 客户端 {client_id} 会话建立: {results['session_id']}")
            
            @sio.event
            def task_update(data):
                results['messages_received'] += 1
                print(f"📨 客户端 {client_id} 收到消息: {data.get('status', 'Unknown')}")
            
            @sio.event
            def error(data):
                results['errors'].append(data.get('message', 'Unknown error'))
                print(f"❌ 客户端 {client_id} 错误: {data.get('message', 'Unknown error')}")
            
            try:
                # 连接到不同的实例
                instance_port = 8002 + (client_id % self.instances)
                sio.connect(f"{self.base_url}:{instance_port}")
                
                # 发送测试问题
                if results['session_id']:
                    sio.emit('ask_question', {
                        'question': f'测试问题 {client_id}',
                        'session_id': results['session_id']
                    })
                
                # 等待一段时间接收消息
                time.sleep(5)
                
                sio.disconnect()
                
            except Exception as e:
                results['errors'].append(str(e))
                print(f"❌ 客户端 {client_id} 连接失败: {str(e)}")
            
            return results
        
        # 创建多个客户端
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_clients) as executor:
            futures = [executor.submit(create_socketio_client, i) for i in range(num_clients)]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 统计结果
        connected_clients = [r for r in results if r['connected']]
        total_messages = sum(r['messages_received'] for r in results)
        total_errors = sum(len(r['errors']) for r in results)
        
        print(f"✅ SocketIO分布式通信测试完成！")
        print(f"   客户端数: {num_clients}")
        print(f"   成功连接: {len(connected_clients)}")
        print(f"   总消息数: {total_messages}")
        print(f"   总错误数: {total_errors}")
        print(f"   总耗时: {total_time:.2f} 秒")
        
        return {
            'clients': num_clients,
            'connected_clients': len(connected_clients),
            'total_messages': total_messages,
            'total_errors': total_errors,
            'total_time': total_time
        }
    
    def test_redis_connection(self):
        """测试Redis连接"""
        print("🧪 测试Redis连接...")
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
            print("✅ Redis连接成功")
            
            # 测试不同数据库
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
    
    async def run_comprehensive_test(self):
        """运行综合测试"""
        print("🚀 分布式架构综合测试")
        print("=" * 50)
        
        # 测试Redis连接
        redis_ok = self.test_redis_connection()
        if not redis_ok:
            print("❌ Redis连接失败，请确保Redis服务正在运行")
            return
        
        print("\n" + "=" * 50)
        
        # 测试HTTP负载均衡
        http_results = await self.test_http_load_balancing(30)
        
        print("\n" + "=" * 50)
        
        # 测试SocketIO分布式通信
        socketio_results = self.test_socketio_distribution(5)
        
        # 总结报告
        print("\n" + "=" * 50)
        print("📈 分布式架构测试总结")
        print("=" * 50)
        
        print(f"HTTP负载均衡:")
        print(f"   成功率: {http_results['successful_requests']/http_results['total_requests']*100:.1f}%")
        print(f"   吞吐量: {http_results['throughput']:.2f} 请求/秒")
        
        print(f"\nSocketIO分布式通信:")
        print(f"   连接成功率: {socketio_results['connected_clients']/socketio_results['clients']*100:.1f}%")
        print(f"   消息接收率: {socketio_results['total_messages']/socketio_results['connected_clients']:.1f} 消息/客户端")
        
        # 性能评估
        if http_results['throughput'] > 5 and socketio_results['connected_clients'] > 0:
            print("\n🎉 分布式架构性能优秀！")
            print("   系统可以处理高并发请求")
            print("   SocketIO通信正常")
        elif http_results['throughput'] > 2:
            print("\n✅ 分布式架构性能良好")
            print("   可以处理中等并发请求")
        else:
            print("\n⚠️  分布式架构性能需要优化")
            print("   建议检查配置和资源")

async def main():
    """主函数"""
    tester = DistributedTester(instances=3)
    await tester.run_comprehensive_test()

if __name__ == '__main__':
    asyncio.run(main())
