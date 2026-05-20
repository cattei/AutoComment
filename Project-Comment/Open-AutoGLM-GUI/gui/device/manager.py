"""
设备管理器模块
"""

import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import os
import re

from .utils import get_device_list, get_device_model


class DeviceManager:
    """设备管理器"""
    
    def __init__(self, root, status_var=None):
        self.root = root
        self.status_var = status_var
        
        # 设备列表
        self.connected_devices = []
        self.selected_device_id = tk.StringVar(value="")
        
        # 设备类型
        self.device_type = tk.StringVar(value="安卓")
        
        # iOS设备IP
        self.ios_device_ip = tk.StringVar(value="localhost")
        
        # 环境变量设备ID
        self.env_device_id = os.environ.get('PHONE_AGENT_DEVICE_ID', '')
    
    def async_refresh_devices(self):
        """异步刷新设备列表"""
        threading.Thread(target=self._background_refresh_devices, daemon=True).start()
    
    def _background_refresh_devices(self):
        """后台刷新设备列表"""
        try:
            device_type = self.device_type.get()
            device_type_map = {"安卓": "adb", "iOS": "ios", "鸿蒙": "hdc"}
            device_type_en = device_type_map.get(device_type, "adb")
            
            if device_type_en == "ios":
                # iOS设备暂不支持自动扫描
                self.root.after(0, lambda: self._update_device_display([]))
                return
            
            # 获取设备列表
            devices = get_device_list(device_type_en)
            
            # 获取设备详细信息
            device_list = []
            for device_id, status in devices:
                model = get_device_model(device_id, device_type_en)
                device_list.append({
                    'id': device_id,
                    'status': status,
                    'model': model,
                    'type': device_type_en
                })
            
            # 在主线程中更新显示
            self.root.after(0, lambda: self._update_device_display(device_list))
            
        except Exception as e:
            print(f"刷新设备列表失败: {e}")
            self.root.after(0, lambda: self._update_device_display([]))
    
    def refresh_devices(self):
        """同步刷新设备列表"""
        try:
            device_type = self.device_type.get()
            device_type_map = {"安卓": "adb", "iOS": "ios", "鸿蒙": "hdc"}
            device_type_en = device_type_map.get(device_type, "adb")
            
            if device_type_en == "ios":
                self._update_device_display([])
                return
            
            devices = get_device_list(device_type_en)
            
            device_list = []
            for device_id, status in devices:
                model = get_device_model(device_id, device_type_en)
                device_list.append({
                    'id': device_id,
                    'status': status,
                    'model': model,
                    'type': device_type_en
                })
            
            self._update_device_display(device_list)
            
        except Exception as e:
            print(f"刷新设备列表失败: {e}")
            self._update_device_display([])
    
    def _update_device_display(self, device_list):
        """更新设备显示"""
        self.connected_devices = device_list
        
        if self.status_var:
            if device_list:
                self.status_var.set(f"✅ 已连接 {len(device_list)} 个设备")
            else:
                self.status_var.set("⚠️ 未检测到设备")
    
    def on_device_type_change(self):
        """设备类型改变时的处理"""
        # 清空设备列表
        self.connected_devices = []
        self.selected_device_id.set("")
        
        # 异步刷新设备
        self.async_refresh_devices()
    
    def get_selected_device(self):
        """获取选中的设备ID"""
        device_id = self.selected_device_id.get()
        if device_id:
            # 提取设备ID（去掉型号信息）
            return device_id.split(' ')[0]
        return None
    
    def connect_remote_device(self, ip, port):
        """
        连接远程设备
        
        Args:
            ip: 设备IP地址
            port: 端口号
        
        Returns:
            (success, message) 元组
        """
        try:
            device_type = self.device_type.get()
            device_type_map = {"安卓": "adb", "iOS": "ios", "鸿蒙": "hdc"}
            device_type_en = device_type_map.get(device_type, "adb")
            
            address = f"{ip}:{port}"
            
            if device_type_en == "hdc":
                cmd = ["hdc", "tconn", address]
            else:
                cmd = ["adb", "connect", address]
            
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=10,
                creationflags=creationflags
            )
            
            if result.returncode == 0:
                # 连接成功，刷新设备列表
                self.async_refresh_devices()
                return True, f"成功连接到 {address}"
            else:
                return False, f"连接失败: {result.stderr}"
                
        except Exception as e:
            return False, f"连接异常: {str(e)}"
    
    def disconnect_device(self, device_id=None):
        """
        断开设备连接
        
        Args:
            device_id: 设备ID，如果为None则断开所有设备
        
        Returns:
            (success, message) 元组
        """
        try:
            device_type = self.device_type.get()
            device_type_map = {"安卓": "adb", "iOS": "ios", "鸿蒙": "hdc"}
            device_type_en = device_type_map.get(device_type, "adb")
            
            if device_type_en == "hdc":
                if device_id:
                    cmd = ["hdc", "tdisconn", device_id]
                else:
                    return False, "HDC不支持断开所有设备"
            else:
                if device_id:
                    cmd = ["adb", "disconnect", device_id]
                else:
                    cmd = ["adb", "disconnect"]
            
            creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=10,
                creationflags=creationflags
            )
            
            if result.returncode == 0:
                self.async_refresh_devices()
                return True, "断开连接成功"
            else:
                return False, f"断开连接失败: {result.stderr}"
                
        except Exception as e:
            return False, f"断开连接异常: {str(e)}"
