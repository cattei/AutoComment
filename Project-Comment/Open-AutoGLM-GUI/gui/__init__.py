"""
GUI模块 - AutoFlow 智能自动化助手

使用方式：
    from gui import AutoFlowGUI
    或
    python -m gui.main
"""

from .app import AutoFlowGUI
from .main import main

__version__ = '2.0.0'
__all__ = ['AutoFlowGUI', 'main']
