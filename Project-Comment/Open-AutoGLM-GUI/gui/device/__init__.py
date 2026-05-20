"""
设备管理模块
"""

from .utils import *
from .manager import DeviceManager

__all__ = ['DeviceManager', 'adb_shell', 'is_screen_on', 'wake_and_unlock', 
           'ensure_awake_and_unlocked', 'get_device_list', 'get_device_model']
