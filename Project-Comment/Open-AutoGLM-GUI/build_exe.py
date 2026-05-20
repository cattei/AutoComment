#!/usr/bin/env python3
"""
PyInstaller 打包脚本 - 将评论神器 GUI 打包为单个 exe 文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

def check_dependencies():
    """检查并安装必要的打包依赖"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller 已安装 (版本: {PyInstaller.__version__})")
    except ImportError:
        print("正在安装 PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller 安装完成")

def clean_build_files():
    """清理旧的构建文件"""
    print("\n清理旧的构建文件...")
    for dir_name in ['build', 'dist', '__pycache__']:
        dir_path = PROJECT_ROOT / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  已删除: {dir_path}")
    
    spec_file = PROJECT_ROOT / "评论神器.spec"
    if spec_file.exists():
        spec_file.unlink()
        print(f"  已删除: {spec_file}")

def build_exe():
    """执行 PyInstaller 打包"""
    print("\n开始打包 exe...")
    
    # 构建数据文件参数
    # 包含 tools 目录（adb, hdc, scrcpy 等工具）
    tools_path = PROJECT_ROOT / "tools"
    datas_args = []
    if tools_path.exists():
        datas_args.extend(["--add-data", f"{tools_path}{os.pathsep}tools"])
    
    # 包含 config 目录（配置文件）
    config_path = PROJECT_ROOT / "config"
    if config_path.exists():
        datas_args.extend(["--add-data", f"{config_path}{os.pathsep}config"])
    
    # 包含 assets 目录（图标、图片等资源）
    assets_path = PROJECT_ROOT / "assets"
    if assets_path.exists():
        datas_args.extend(["--add-data", f"{assets_path}{os.pathsep}assets"])
    
    # 包含 gui/ui 目录（UI HTML 文件）
    gui_ui_path = PROJECT_ROOT / "gui" / "ui"
    if gui_ui_path.exists():
        datas_args.extend(["--add-data", f"{gui_ui_path}{os.pathsep}gui/ui"])
    
    # 构建 PyInstaller 命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=评论神器",           # exe 文件名
        "--onefile",                 # 打包成单个 exe
        "--windowed",                # 无控制台窗口
        "--icon=assets/icons/app.ico",  # 应用图标
        "--clean",                   # 清理临时文件
        "--noconfirm",               # 覆盖输出目录
        "--hidden-import=phone_agent",
        "--hidden-import=phone_agent.agent",
        "--hidden-import=phone_agent.device_factory",
        "--hidden-import=phone_agent.adb",
        "--hidden-import=phone_agent.hdc",
        "--hidden-import=phone_agent.xctest",
        "--hidden-import=phone_agent.actions",
        "--hidden-import=phone_agent.model",
        "--hidden-import=phone_agent.config",
        "--hidden-import=gui",
        "--hidden-import=gui.app",
        "--hidden-import=gui.main",
        "--hidden-import=gui.core",
        "--hidden-import=gui.device",
        "--hidden-import=gui.task",
        "--hidden-import=gui.ui",
        "--hidden-import=client",
        "--hidden-import=customtkinter",
        "--hidden-import=PIL",
        "--hidden-import=openai",
        "--hidden-import=aiohttp",
        "--hidden-import=httpx",
        "--hidden-import=json",
        "--hidden-import=asyncio",
        "--hidden-import=sqlite3",
        "--hidden-import=hashlib",
        "--hidden-import=hmac",
        "--hidden-import=socket",
        "--hidden-import=uuid",
        "--hidden-import=tempfile",
        "--hidden-import=subprocess",
        "--hidden-import=shutil",
        "--hidden-import=pathlib",
        "--hidden-import=logging",
        "--hidden-import=typing",
        "--hidden-import=enum",
        "--hidden-import=dataclasses",
        "--hidden-import=collections",
        "--hidden-import=inspect",
        "--hidden-import=io",
        "--hidden-import=time",
        "--hidden-import=threading",
        "--hidden-import=concurrent.futures",
        "--hidden-import=webbrowser",
        "--hidden-import=urllib",
        "--hidden-import=urllib3",
        "--hidden-import=ssl",
        "--hidden-import=certifi",
        "--hidden-import=tqdm",
        "--hidden-import=tiktoken",
        "--hidden-import=yaml",
        "--hidden-import=toml",
    ]
    
    # 添加数据文件参数
    cmd.extend(datas_args)
    
    # 添加入口脚本
    cmd.append(str(PROJECT_ROOT / "gui.py"))
    
    print(f"执行命令: {' '.join(cmd[:5])} ...")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    
    if result.returncode == 0:
        print("\n✓ 打包成功！")
        exe_path = PROJECT_ROOT / "dist" / "评论神器.exe"
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"  输出文件: {exe_path}")
            print(f"  文件大小: {size_mb:.2f} MB")
        return True
    else:
        print("\n✗ 打包失败！")
        return False

def main():
    print("=" * 60)
    print("评论神器 - EXE 打包工具")
    print("=" * 60)
    
    # 检查依赖
    check_dependencies()
    
    # 清理旧文件
    clean_build_files()
    
    # 打包
    success = build_exe()
    
    if success:
        print("\n" + "=" * 60)
        print("打包完成！生成的 exe 文件位于: dist/评论神器.exe")
        print("此 exe 文件可以在任何 Windows 电脑上直接运行，无需安装其他依赖。")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("打包失败，请检查错误信息并重试。")
        print("=" * 60)
        sys.exit(1)

if __name__ == '__main__':
    main()
