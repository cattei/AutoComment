"""
GUI主入口 - 评论神器
CustomTkinter 版本
"""

import customtkinter as ctk
import sys
import os

# 隐藏控制台窗口（Windows）
if sys.platform == 'win32' and sys.executable.lower().endswith('python.exe'):
    import ctypes
    try:
        ctypes.windll.user32.ShowWindow(
            ctypes.windll.kernel32.GetConsoleWindow(), 0
        )
    except Exception:
        pass

from gui.app import AutoFlowGUI


def main():
    """主函数"""
    root = ctk.CTk()
    app = AutoFlowGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
