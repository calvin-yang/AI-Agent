#!/usr/bin/env python3
"""
AI Agent 启动脚本
"""

import os
import sys
from dotenv import load_dotenv

def main():
    """主函数"""
    print("🤖 AI Agent - 联网智能助手")
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
        print("   可以参考env.example文件创建.env文件")
    
    # 检查必要的环境变量
    if not os.getenv('DEEPSEEK_API_KEY'):
        print("❌ 错误：未设置DEEPSEEK_API_KEY环境变量")
        print("   请在.env文件中设置您的DeepSeek API密钥")
        sys.exit(1)
    
    print("🚀 启动AI Agent服务...")
    print("   访问地址: http://localhost:8002")
    print("   按 Ctrl+C 停止服务")
    print("=" * 50)
    
    # 启动Flask应用
    try:
        import sys
        import os
        # 添加项目根目录到Python路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from app import create_app
        app, socketio = create_app()
        socketio.run(app, debug=True, host='0.0.0.0', port=8002)
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
