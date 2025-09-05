#!/usr/bin/env python3
"""
依赖更新脚本
更新duckduckgo_search到ddgs
"""

import subprocess
import sys
import os

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
    print("🔄 更新AI Agent依赖包")
    print("=" * 50)
    
    # 切换到项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    print(f"✅ 切换到项目根目录: {project_root}")
    
    # 卸载旧的duckduckgo_search包
    print("📦 卸载旧的duckduckgo_search包...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "duckduckgo-search", "-y"], 
                      check=False, capture_output=True)
        print("✅ 旧包已卸载")
    except:
        print("ℹ️  旧包可能未安装")
    
    # 安装新的ddgs包
    if not run_command("pip install ddgs==3.9.6", "安装新的ddgs包"):
        print("❌ 依赖更新失败")
        sys.exit(1)
    
    # 重新安装其他依赖
    if not run_command("pip install -r requirements.txt", "重新安装所有依赖"):
        print("❌ 依赖安装失败")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 依赖更新完成！")
    print("\n📋 更新内容：")
    print("- duckduckgo_search → ddgs")
    print("- 搜索服务已更新为使用新的包")
    print("\n🚀 现在可以正常运行应用了：")
    print("python scripts/start.py")

if __name__ == '__main__':
    main()
