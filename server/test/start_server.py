#!/usr/bin/env python3
"""
启动Smart ERP Agent服务器
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def start_server():
    """启动FastAPI服务器"""
    print("正在启动Smart ERP Agent服务器...")
    print("使用端口: 8001")
    print("访问地址: http://localhost:8001")
    print("API文档: http://localhost:8001/docs")
    print("-" * 50)
    
    # 切换到项目根目录
    project_root = Path(__file__).parent.parent
    
    try:
        # 启动uvicorn服务器
        cmd = [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--port", "8001"]
        process = subprocess.Popen(cmd, cwd=project_root)
        
        print("服务器已启动!")
        print("按 Ctrl+C 停止服务器")
        
        # 等待进程结束
        process.wait()
        
    except KeyboardInterrupt:
        print("\n正在停止服务器...")
        process.terminate()
        process.wait()
        print("服务器已停止")
    except Exception as e:
        print(f"启动服务器时发生错误: {e}")

if __name__ == "__main__":
    start_server() 