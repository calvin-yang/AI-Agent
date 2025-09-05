#!/usr/bin/env python3
"""
AI Agent 安装脚本
"""

import os
import sys
import subprocess

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description}完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description}失败: {e.stderr}")
        return False

def main():
    """主函数"""
    print("🤖 AI Agent - 联网智能助手安装程序")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 错误：需要Python 3.7或更高版本")
        sys.exit(1)
    
    print(f"✅ Python版本: {sys.version}")
    
    # 切换到项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    print(f"✅ 切换到项目根目录: {project_root}")
    
    # 安装依赖
    if not run_command("pip install -r requirements.txt", "安装Python依赖包"):
        print("❌ 依赖安装失败，请检查网络连接和pip配置")
        sys.exit(1)
    
    # 创建.env文件（如果不存在）
    env_file = os.path.join(project_root, '.env')
    if not os.path.exists(env_file):
        print("📝 创建.env配置文件...")
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("# DeepSeek API配置\n")
            f.write("DEEPSEEK_API_KEY=your-deepseek-api-key-here\n")
            f.write("\n")
            f.write("# Flask配置\n")
            f.write("SECRET_KEY=your-secret-key-here\n")
        print("✅ .env文件已创建")
        print("⚠️  请编辑.env文件，设置您的DeepSeek API密钥")
    else:
        print("✅ .env文件已存在")
    
    # 运行测试
    print("\n🧪 运行测试...")
    if run_command("python test/run_tests.py", "运行测试套件"):
        print("✅ 所有测试通过")
    else:
        print("⚠️  部分测试失败，但应用仍可运行")
    
    print("\n" + "=" * 50)
    print("🎉 安装完成！")
    print("\n📋 下一步操作：")
    print("1. 编辑.env文件，设置您的DeepSeek API密钥")
    print("2. 运行: python scripts/start.py")
    print("3. 打开浏览器访问: http://localhost:8002")
    print("\n📚 更多信息请查看README.md文件")

if __name__ == '__main__':
    main()
