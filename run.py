#!/usr/bin/env python3
"""
Face Recognition System - CLI Entry Point
快速启动人脸识别系统的各种工具
"""

import os
import sys
import argparse
import subprocess
import time
from pathlib import Path

# 确保导入路径正确
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

PROJECT_DIR = Path(__file__).resolve().parent
REACT_UI_DIR = PROJECT_DIR / "frontend"


def build_react():
    """Build the React frontend. Returns True on success."""
    if not (REACT_UI_DIR / "package.json").exists():
        print("[WARN] React UI project not found, skipping build.")
        return True  # Not an error — maybe the user only wants the API

    print("[BUILD] Building React frontend...")
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    try:
        subprocess.run([npm, "install"], cwd=str(REACT_UI_DIR), check=True)
        subprocess.run([npm, "run", "build"], cwd=str(REACT_UI_DIR), check=True)
        print("[BUILD] React frontend built successfully.")                 
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] React build failed: {e}")                                                                        
        return False
    except FileNotFoundError:
        print("[ERROR] npm not found. Please install Node.js.")                         
        return False                                          
                                                                                                                                                                                                                                                                         
     
def start_api():
    """Start FastAPI (serves API + React frontend if built)."""              
    print("Starting FastAPI...")       
    print(f"\n  React UI:   http://127.0.0.1:8000")
    print(f"  API docs:   http://127.0.0.1:8000/docs")                                          
    print(f"  Press Ctrl+C to stop\n")                                                                                                                                                                                                                                                                           
    subprocess.run([                            
        sys.executable, "-m", "uvicorn",                                                                                                                                                                                                                 
        "apps.recognition_system.api.main:app",     
        "--host", "127.0.0.1", "--port", "8000",
    ]      )
                                                                                                   

def start_react_dev():
    """Start Vite dev server for React (hot reload)."""
    print("[DEV] Starting React dev server...")
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    try:
        subprocess.run([npm, "run", "dev"], cwd=str(REACT_UI_DIR))
    except FileNotFoundError:
        print("[ERROR] npm not found.")


def show_menu():
    """显示主菜单"""
    print("\n" + "=" * 50)
    print("   人脸识别系统 (Face Recognition System)")
    print("=" * 50)
    print("1.  Start React UI (Vite dev server)")
    print("2.  Start API (FastAPI + React build)")
    print("3.  Start Full System (Build React + API)")
    print("4.  Start API + React Dev (Hot Reload)")
    print("5.  Face Database Manager")
    print("6.  Register Faces")
    print("7.  Recognize Image")
    print("8.  Camera Recognition")
    print("0.  Exit")
    print("=" * 50)


def main():
    """主程序"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        args = sys.argv[2:]

        if command == "api":
            start_api()
        elif command == "web" or command == "gui" or command == "streamlit":
            # Legacy: now serves React UI
            build_react()
            start_api()
        elif command == "full":
            if build_react():
                start_api()
        elif command == "dev":
            # API + React dev server (hot reload)
            api_proc = subprocess.Popen([
                sys.executable, "-m", "uvicorn",
                "apps.recognition_system.api.main:app",
                "--host", "127.0.0.1", "--port", "8000",
            ])
            try:
                time.sleep(2)
                start_react_dev()
            finally:
                api_proc.terminate()
        elif command == "build":
            build_react()
        elif command == "react-dev":
            start_react_dev()
        elif command == "manager":
            from apps.recognition_system.add_person_to_db import main as manager_main
            manager_main()
        elif command == "register":
            from apps.recognition_system.core.cli import main as cli_main
            sys.argv = [sys.argv[0], "register-dir"] + args
            cli_main()
        elif command == "recognize-image":
            from apps.recognition_system.core.cli import main as cli_main
            sys.argv = [sys.argv[0], "recognize-image"] + args
            cli_main()
        elif command == "recognize-camera":
            from apps.recognition_system.core.cli import main as cli_main
            sys.argv = [sys.argv[0], "recognize-camera"] + args
            cli_main()
        elif command == "cli":
            from apps.recognition_system.core.cli import main as cli_main
            sys.argv = [sys.argv[0]] + args
            cli_main()
        else:
            print(f"Unknown command: {command}")
            print("\nAvailable commands:")
            print("  api            - Start FastAPI (serves React build at http://127.0.0.1:8000)")
            print("  full           - Build React + start API")
            print("  dev            - API + React dev server (hot reload)")
            print("  build          - Build React frontend only")
            print("  react-dev      - Start React dev server only")
            print("  manager        - Face database manager")
            print("  register       - Register faces from directory")
            print("  recognize-image - Recognize faces in image")
            print("  recognize-camera - Real-time camera recognition")
            print("  cli            - Command-line interface")
            sys.exit(1)
    else:
        show_menu()
        choice = input("\n请选择 (Select): ").strip()

        try:
            if choice == "1":
                start_react_dev()
            elif choice == "2":
                start_api()
            elif choice == "3":
                if build_react():
                    start_api()
            elif choice == "4":
                api_proc = subprocess.Popen([
                    sys.executable, "-m", "uvicorn",
                    "apps.recognition_system.api.main:app",
                    "--host", "127.0.0.1", "--port", "8000",
                ])
                try:
                    time.sleep(2)
                    start_react_dev()
                finally:
                    api_proc.terminate()
            elif choice == "5":
                print("启动人脸库管理...")
                from apps.recognition_system.add_person_to_db import main
                main()
            elif choice == "6":
                print("启动注册工具...")
                from apps.recognition_system.core.cli import main
                sys.argv = ["python", "register-dir", "--help"]
                main()
            elif choice == "7":
                print("启动识别工具...")
                from apps.recognition_system.core.cli import main
                sys.argv = ["python", "recognize-image", "--help"]
                main()
            elif choice == "8":
                print("启动摄像头识别...")
                from apps.recognition_system.core.cli import main
                sys.argv = ["python", "recognize-camera", "--help"]
                main()
            elif choice == "0":
                print("退出系统")
                sys.exit(0)
            else:
                print("无效选择 (Invalid choice)")
        except Exception as e:
            print(f"错误 (Error): {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
