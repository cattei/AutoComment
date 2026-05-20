"""
配置管理模块
AI模型API地址 + API Key 配置
"""

import os
import sys
import json
import threading
import tkinter as tk
from tkinter import messagebox


def get_resource_path(relative_path):
    """获取资源文件的绝对路径（兼容 PyInstaller 打包）"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后，数据文件解压到临时目录
        base_path = sys._MEIPASS
    else:
        # 开发环境，使用项目根目录
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_path, relative_path)


class ConfigManager:
    """配置管理器"""

    def __init__(self, root, config_file=None):
        self.root = root
        # 配置文件路径：打包后放到用户可写目录，不覆盖 _MEIPASS 中的只读版本
        if config_file is None:
            # 获取应用可执行文件所在目录（用于用户配置读写）
            if getattr(sys, 'frozen', False):
                # 打包后：配置文件放在 exe 同目录下的 config/
                app_dir = os.path.dirname(os.path.abspath(sys.executable))
            else:
                # 开发环境
                app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_dir = os.path.join(app_dir, 'config')
            os.makedirs(config_dir, exist_ok=True)
            self.config_file = os.path.join(config_dir, 'gui_config.json')
        else:
            self.config_file = config_file

        # AI模型配置
        self.model = tk.StringVar(value='autoglm-phone')
        self.base_url = tk.StringVar(value='')   # AI模型API地址
        self.apikey = tk.StringVar(value='')     # AI模型API Key

        # 任务配置
        self.task = tk.StringVar(value='输入你想要执行的任务')
        self.max_steps = tk.StringVar(value='200')
        self.temperature = tk.StringVar(value='0.2')
        self.device_type = tk.StringVar(value='安卓')
        self.selected_device_id = tk.StringVar(value='')
        self.ios_device_ip = tk.StringVar(value='localhost')
        self.platform = tk.StringVar(value='小红书')
        self.operation_checkpoint = tk.BooleanVar(value=True)
        self.operation_comment = tk.BooleanVar(value=True)
        self.operation_collect = tk.BooleanVar(value=False)
        self.operation_follow = tk.BooleanVar(value=False)

        # 远程连接配置
        self.last_remote_connection = {'ip': '192.168.1.100', 'port': '5555'}
        self.last_wireless_pair = {'pair_address': '10.10.10.100:41717', 'connect_address': '10.10.10.100:5555'}
        self.last_legacy_wireless = {'ip': '192.168.1.100', 'port': '5555'}

        self.env_device_id = os.environ.get('DEVICE_ID', '')
        self.status_var = tk.StringVar(value='✅ 就绪')
    
    def load_config_async(self):
        """异步加载配置"""
        threading.Thread(target=self._background_load_config, daemon=True).start()
    
    def _background_load_config(self):
        """后台加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                self.root.after(0, lambda: self._apply_config(config_data))
            else:
                self.root.after(0, self._create_default_config)
        except Exception as e:
            print(f"加载配置失败: {e}")
    
    def _apply_config(self, config):
        """应用配置"""
        try:
            # AI模型配置
            self.model.set(config.get('model', 'autoglm-phone'))
            self.base_url.set(config.get('base_url', ''))
            self.apikey.set(config.get('apikey', ''))

            self.task.set(config.get('task', ''))
            self.max_steps.set(str(config.get('max_steps', '200')))
            self.temperature.set(str(config.get('temperature', '0.0')))

            device_type_value = config.get('device_type', 'adb')
            device_type_map = {'adb': '安卓', 'ios': 'iOS', 'hdc': '鸿蒙'}
            self.device_type.set(device_type_map.get(device_type_value, '安卓'))

            self.ios_device_ip.set(config.get('ios_device_ip', 'localhost'))
            self.platform.set(config.get('platform', '小红书'))
            self.operation_checkpoint.set(config.get('operation_checkpoint', True))
            self.operation_comment.set(config.get('operation_comment', True))
            self.operation_collect.set(config.get('operation_collect', False))
            self.operation_follow.set(config.get('operation_follow', False))

            selected_device = self.env_device_id or config.get('selected_device', '')
            self.selected_device_id.set(selected_device)

            self.last_remote_connection = config.get('remote_connection', self.last_remote_connection)
            self.last_wireless_pair = config.get('wireless_pair', self.last_wireless_pair)
            self.last_legacy_wireless = config.get('legacy_wireless', self.last_legacy_wireless)

            lock_password = config.get('lock_password', '')
            if lock_password:
                os.environ['PHONE_AGENT_LOCK_PASSWORD'] = lock_password

            self.status_var.set("✅ 配置已加载")
        except Exception as e:
            print(f"应用配置失败: {e}")
    
    def save_config(self):
        """保存配置"""
        try:
            config = {
                'base_url': self.base_url.get(),
                'model': self.model.get(),
                'apikey': self.apikey.get(),
                'task': self.task.get(),
                'max_steps': int(self.max_steps.get() or 200),
                'temperature': float(self.temperature.get() or 0.0),
                'device_type': self._get_device_type_value(),
                'selected_device': self.selected_device_id.get(),
                'remote_connection': self.last_remote_connection,
                'wireless_pair': self.last_wireless_pair,
                'legacy_wireless': self.last_legacy_wireless,
                'ios_device_ip': self.ios_device_ip.get(),
                'platform': self.platform.get(),
                'operation_checkpoint': self.operation_checkpoint.get(),
                'operation_comment': self.operation_comment.get(),
                'operation_collect': self.operation_collect.get(),
                'operation_follow': self.operation_follow.get()
            }

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("成功", "配置已保存")
            self.status_var.set("✅ 配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {e}")
    
    def save_config_silent(self):
        """静默保存配置"""
        try:
            config = {
                'base_url': self.base_url.get(),
                'model': self.model.get(),
                'apikey': self.apikey.get(),
                'task': self.task.get(),
                'max_steps': int(self.max_steps.get() or 200),
                'temperature': float(self.temperature.get() or 0.0),
                'device_type': self._get_device_type_value(),
                'selected_device': self.selected_device_id.get(),
                'remote_connection': self.last_remote_connection,
                'wireless_pair': self.last_wireless_pair,
                'legacy_wireless': self.last_legacy_wireless,
                'ios_device_ip': self.ios_device_ip.get(),
                'platform': self.platform.get(),
                'operation_checkpoint': self.operation_checkpoint.get(),
                'operation_comment': self.operation_comment.get(),
                'operation_collect': self.operation_collect.get(),
                'operation_follow': self.operation_follow.get()
            }

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _get_device_type_value(self):
        """获取设备类型英文值"""
        device_type_map = {"安卓": "adb", "iOS": "ios", "鸿蒙": "hdc"}
        return device_type_map.get(self.device_type.get(), "adb")
    
    def _create_default_config(self):
        """创建默认配置"""
        self.status_var.set("📝 使用默认配置")
