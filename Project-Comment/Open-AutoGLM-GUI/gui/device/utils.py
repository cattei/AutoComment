"""
ADB设备工具函数
"""

import subprocess
import time
import re
import os
from typing import Optional, Tuple


def adb_shell(cmd: str, adb: str = "adb", timeout: int = 5) -> str:
    """执行ADB shell命令"""
    try:
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        p = subprocess.run(
            [adb, 'shell', cmd], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            timeout=timeout, 
            creationflags=creationflags
        )
        return p.stdout.decode(errors='ignore')
    except Exception:
        return ""


def is_screen_on(adb: str = "adb") -> bool:
    """
    检查设备屏幕是否点亮
    
    Returns:
        True表示亮屏，False表示息屏
    """
    out = adb_shell('dumpsys power', adb)
    if not out:
        return False

    # 方法1: 检查mWakefulness
    m = re.search(r'mWakefulness=(\w+)', out)
    if m:
        return m.group(1).lower() == 'awake'

    # 方法2: 检查mScreenOn
    m = re.search(r'mScreenOn=(true|false)', out, re.I)
    if m:
        return m.group(1).lower() == 'true'

    # 方法3: 检查Display Power状态
    m = re.search(r'Display Power: state=(\w+)', out, re.I)
    if m:
        return m.group(1).lower() != 'off'

    # 兜底：如果包含Awake关键字则认为是亮屏
    if 'awake' in out.lower():
        return True

    return False


def wake_and_unlock(
    adb: str = "adb", 
    max_attempts: int = 3, 
    swipe: Optional[Tuple[int, int, int, int]] = None, 
    password: Optional[str] = None
) -> bool:
    """
    唤醒并尝试解锁屏幕
    
    Args:
        adb: ADB命令路径
        max_attempts: 最大尝试次数
        swipe: 滑动解锁坐标 (x1, y1, x2, y2)
        password: 解锁密码
    
    Returns:
        True表示检测到屏幕已点亮
    """
    creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    
    for _ in range(max_attempts):
        # 发送唤醒按键
        subprocess.run([adb, 'shell', 'input', 'keyevent', '224'], creationflags=creationflags)
        time.sleep(0.4)
        
        # 发送菜单按键（通常可解锁）
        subprocess.run([adb, 'shell', 'input', 'keyevent', '82'], creationflags=creationflags)
        time.sleep(0.4)
        
        # 如果提供了滑动坐标，执行滑动解锁
        if swipe:
            x1, y1, x2, y2 = swipe
            subprocess.run([adb, 'shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2)], creationflags=creationflags)
            time.sleep(0.5)

        # 如果提供了密码，尝试输入密码解锁
        if password:
            try:
                # input text对空格的处理需要替换为%s
                esc = str(password).replace(' ', '%s')
                subprocess.run([adb, 'shell', 'input', 'text', esc], creationflags=creationflags)
                time.sleep(0.3)
                # 按回车确认
                subprocess.run([adb, 'shell', 'input', 'keyevent', '66'], creationflags=creationflags)
                time.sleep(0.6)
            except Exception:
                pass

        # 检查屏幕是否已点亮
        if is_screen_on(adb):
            return True

        # 备用：短按电源键（某些机型需要）
        subprocess.run([adb, 'shell', 'input', 'keyevent', '26'], creationflags=creationflags)
        time.sleep(0.6)

    return is_screen_on(adb)


def ensure_awake_and_unlocked(
    adb: str = "adb", 
    swipe: Optional[Tuple[int, int, int, int]] = None, 
    password: Optional[str] = None
) -> bool:
    """
    确保屏幕已唤醒并尽量解锁
    
    Returns:
        True表示屏幕已唤醒（或已成功解锁）
    """
    try:
        if is_screen_on(adb):
            return True
        return wake_and_unlock(adb, swipe=swipe, password=password)
    except Exception:
        return False


def get_device_list(adb: str = "adb") -> list:
    """
    获取已连接的设备列表
    
    Returns:
        设备列表，每个元素为(device_id, status)元组
    """
    try:
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        result = subprocess.run(
            [adb, 'devices'], 
            capture_output=True, 
            text=True, 
            timeout=10,
            creationflags=creationflags
        )
        
        lines = result.stdout.strip().split('\n')
        devices = []
        
        for line in lines[1:]:  # 跳过标题行
            if line.strip() and '\t' in line:
                parts = line.split('\t')
                device_id = parts[0].strip()
                status = parts[1].strip() if len(parts) > 1 else 'unknown'
                devices.append((device_id, status))
        
        return devices
    except Exception:
        return []


def get_device_model(device_id: str, adb: str = "adb") -> str:
    """
    获取设备型号
    
    Args:
        device_id: 设备ID
        adb: ADB命令路径
    
    Returns:
        设备型号字符串
    """
    try:
        creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        result = subprocess.run(
            [adb, '-s', device_id, 'shell', 'getprop', 'ro.product.model'],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=creationflags
        )
        return result.stdout.strip() if result.stdout.strip() else "Unknown"
    except Exception:
        return "Unknown"
