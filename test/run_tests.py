#!/usr/bin/env python3
"""
测试运行脚本
运行所有测试用例
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    """运行所有测试"""
    # 发现并运行所有测试
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()

if __name__ == '__main__':
    print("开始运行AI Agent测试套件...")
    print("=" * 50)
    
    success = run_tests()
    
    print("=" * 50)
    if success:
        print("✅ 所有测试通过！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败！")
        sys.exit(1)
