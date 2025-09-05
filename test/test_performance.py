#!/usr/bin/env python3
"""
性能测试脚本
测试异步架构的并发处理能力
"""

import asyncio
import aiohttp
import time
import json
from concurrent.futures import ThreadPoolExecutor
import statistics

async def send_question(session, question, session_id):
    """发送单个问题"""
    try:
        async with session.post('http://localhost:8002/api/process', 
                              json={'question': question}) as response:
            result = await response.json()
            return {
                'success': result.get('success', False),
                'response_time': response.headers.get('X-Response-Time', 0),
                'question': question
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'question': question
        }

async def test_concurrent_requests(num_requests=10):
    """测试并发请求"""
    print(f"🧪 开始测试 {num_requests} 个并发请求...")
    
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
            task = send_question(session, question, f"test_session_{i}")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # 统计结果
    successful_requests = [r for r in results if r.get('success', False)]
    failed_requests = [r for r in results if not r.get('success', False)]
    
    print(f"✅ 测试完成！")
    print(f"   总请求数: {num_requests}")
    print(f"   成功请求: {len(successful_requests)}")
    print(f"   失败请求: {len(failed_requests)}")
    print(f"   总耗时: {total_time:.2f} 秒")
    print(f"   平均响应时间: {total_time/num_requests:.2f} 秒")
    print(f"   吞吐量: {num_requests/total_time:.2f} 请求/秒")
    
    if failed_requests:
        print(f"\n❌ 失败的请求:")
        for req in failed_requests[:5]:  # 只显示前5个失败请求
            print(f"   - {req.get('question', 'Unknown')}: {req.get('error', 'Unknown error')}")
    
    return {
        'total_requests': num_requests,
        'successful_requests': len(successful_requests),
        'failed_requests': len(failed_requests),
        'total_time': total_time,
        'throughput': num_requests/total_time
    }

def test_socketio_connection():
    """测试SocketIO连接"""
    try:
        import socketio
        print("🧪 测试SocketIO连接...")
        
        sio = socketio.Client()
        
        @sio.event
        def connect():
            print("✅ SocketIO连接成功")
        
        @sio.event
        def disconnect():
            print("👋 SocketIO连接断开")
        
        @sio.event
        def connected(data):
            print(f"✅ 会话建立成功: {data.get('session_id')}")
        
        sio.connect('http://localhost:8002')
        time.sleep(2)
        sio.disconnect()
        
        return True
    except Exception as e:
        print(f"❌ SocketIO连接失败: {str(e)}")
        return False

async def main():
    """主函数"""
    print("🚀 AI Agent 性能测试")
    print("=" * 50)
    
    # 测试SocketIO连接
    socketio_ok = test_socketio_connection()
    
    if not socketio_ok:
        print("❌ SocketIO连接失败，请确保服务正在运行")
        return
    
    print("\n" + "=" * 50)
    
    # 测试不同并发级别
    test_cases = [5, 10, 20, 50]
    
    results = []
    for num_requests in test_cases:
        print(f"\n📊 测试 {num_requests} 个并发请求...")
        result = await test_concurrent_requests(num_requests)
        results.append(result)
        time.sleep(2)  # 等待2秒再进行下一轮测试
    
    # 总结报告
    print("\n" + "=" * 50)
    print("📈 性能测试总结")
    print("=" * 50)
    
    for i, result in enumerate(results):
        num_requests = test_cases[i]
        print(f"并发数 {num_requests:2d}: "
              f"成功率 {result['successful_requests']/result['total_requests']*100:5.1f}% | "
              f"吞吐量 {result['throughput']:5.2f} 请求/秒 | "
              f"总耗时 {result['total_time']:5.2f} 秒")
    
    # 计算平均性能
    avg_throughput = statistics.mean([r['throughput'] for r in results])
    avg_success_rate = statistics.mean([r['successful_requests']/r['total_requests'] for r in results])
    
    print(f"\n📊 平均性能:")
    print(f"   平均吞吐量: {avg_throughput:.2f} 请求/秒")
    print(f"   平均成功率: {avg_success_rate*100:.1f}%")
    
    if avg_throughput > 10:
        print("🎉 性能优秀！系统可以处理高并发请求")
    elif avg_throughput > 5:
        print("✅ 性能良好，可以处理中等并发请求")
    else:
        print("⚠️  性能需要优化，建议检查系统配置")

if __name__ == '__main__':
    asyncio.run(main())
