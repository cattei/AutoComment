"""

主应用类 - 评论神器 智能自动化助手

CustomTkinter 深色主题 - 严格对齐 ui.html 设计图

"""


import customtkinter as ctk

import tkinter as tk

from tkinter import messagebox

import sys

import os

import subprocess

import threading

import time

import json
import webbrowser

from datetime import datetime

from gui.core.config import get_resource_path

# 获取应用可执行目录（用于打包后读写文件）
def get_app_dir():
    """获取应用目录（打包后为 exe 所在目录，开发环境为项目根目录）"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



from gui.ui.styles import COLORS, FONTS, SIZES, LAYOUT, setup_styles

from gui.core.config import ConfigManager

from gui.device.manager import DeviceManager

from gui.task.executor import TaskExecutor, StreamOutputCollector

from gui.task.history import TaskHistory





class AutoFlowGUI:

    """评论神器 - 智能自动化助手 v2.0"""



    def __init__(self, root):

        self.root = root

        self.root.title("评论神器 - 智能自动化助手")

        self.root.minsize(1200, 800)

        self.root.configure(fg_color=COLORS['bg_primary'])

        # 默认全屏
        self.root.state('zoomed')



        # 必须先初始化字体（CTkFont 需要 root 已创建）

        from gui.ui.styles import _init_fonts

        _init_fonts()



        setup_styles(self.root)



        # ---- 核心模块 ----

        self.config_manager = ConfigManager(root)

        self.device_manager = DeviceManager(root)

        self.task_history = TaskHistory()

        self.task_executor = TaskExecutor(root, self._on_executor_output)



        # ---- 运行状态 ----

        self.is_running = False

        self.current_step = 0

        self.total_steps = 0

        self.stats = {'likes': 0, 'comments': 0, 'collects': 0, 'follows': 0}



        # ---- 配置变量 ----

        self.platform_var = self.config_manager.platform

        self.max_steps_var = self.config_manager.max_steps

        self.temperature_var = tk.DoubleVar(value=float(self.config_manager.temperature.get() or 0.0))

        self.device_type_var = self.config_manager.device_type

        self.task_var = self.config_manager.task



        # ---- 操作类型 ----

        self.op_like_var = self.config_manager.operation_checkpoint

        self.op_comment_var = self.config_manager.operation_comment

        self.op_collect_var = self.config_manager.operation_collect

        self.op_follow_var = self.config_manager.operation_follow



        # ---- 视图状态 ----

        self.current_view = 'steps'



        # ---- 设备列表变量 ----

        self.device_list_var = tk.StringVar(value='')

        self.device_combo = None



        # ---- 加载操作预设配置 ----

        self.operation_presets = self._load_operation_presets()

        self.platform_operations = self._load_platform_operations()



        # ---- 操作勾选框引用 ----

        self.operation_checkboxes = {}



        # ---- 构建 UI ----

        self._build_ui()

        self.update_clock()



        # ---- 初始化 ----

        self.log_message('系统初始化中...', 'info')

        # 延迟到 mainloop 启动后再执行（避免 'main thread is not in main loop' 错误）
        self.root.after(100, self.config_manager.load_config_async)
        self.root.after(500, self._schedule_device_scan)
        self.root.after(2000, self._sync_config_to_ui)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)



    # ================================================================

    # UI 构建 - CustomTkinter 严格对齐 ui.html 设计图

    # ================================================================



    def _build_ui(self):

        """构建完整 UI - 对齐设计图 app 容器"""

        # 主容器 grid 布局: header(0) + main(1) + toolbar(2)

        self.root.grid_rowconfigure(1, weight=1)

        self.root.grid_columnconfigure(0, weight=1)



        self._create_header()

        self._create_main_content()

        self._create_toolbar()



    # ================================================================

    # Header - 对齐设计图 .header

    # ================================================================



    def _create_header(self):

        """顶部导航栏 - 对齐设计图 header"""

        header = ctk.CTkFrame(self.root, fg_color=COLORS['bg_secondary'],

                              height=60, corner_radius=0)

        header.grid(row=0, column=0, sticky='ew')

        header.grid_propagate(False)



        inner = ctk.CTkFrame(header, fg_color='transparent')

        inner.pack(fill='x', padx=24, pady=12)



        # ---- 左侧: Logo + 标题 ----

        left = ctk.CTkFrame(inner, fg_color='transparent')

        left.pack(side='left')



        # Logo: 渐变圆角方块 + "A" (设计图: .logo)

        logo_canvas = tk.Canvas(left, width=36, height=36,

                                bg=COLORS['bg_secondary'], highlightthickness=0)

        logo_canvas.pack(side='left', padx=(0, 12))

        for i in range(36):

            ratio = i / 35

            r = int(99 + (168 - 99) * ratio)

            g = int(102 + (85 - 102) * ratio)

            b = int(241 + (247 - 241) * ratio)

            logo_canvas.create_line(0, i, 36, i, fill=f'#{r:02x}{g:02x}{b:02x}')

        logo_canvas.create_text(18, 18, text="A", fill='white',

                                font=('Microsoft YaHei', 18, 'bold'))



        # 标题

        ctk.CTkLabel(left, text="评论神器",

                     font=FONTS['title'],

                     text_color=COLORS['accent_primary']).pack(side='left')



        # ---- 右侧: 版本 + 状态徽章 + 时间 ----

        right = ctk.CTkFrame(inner, fg_color='transparent')

        right.pack(side='right')



        self.time_label = ctk.CTkLabel(right, text="", font=FONTS['mono'],

                                       text_color=COLORS['text_muted'])

        self.time_label.pack(side='right', padx=(12, 0))



        # 状态徽章 (设计图: .status-badge 圆角胶囊)

        badge_frame = ctk.CTkFrame(right, fg_color=COLORS['bg_card'],

                                    border_color=COLORS['border_color'],

                                    border_width=1, corner_radius=20, height=28)

        badge_frame.pack(side='right', padx=(12, 12))



        # 绿色圆点

        self.status_dot_canvas = tk.Canvas(badge_frame, width=7, height=7,

                                            bg=COLORS['bg_card'], highlightthickness=0)

        self.status_dot_canvas.pack(side='left', padx=(12, 6), pady=8)

        self.status_dot_canvas.create_oval(0, 0, 7, 7, fill=COLORS['accent_green'], outline='')



        self.status_label = ctk.CTkLabel(badge_frame, text="设备已连接",

                                          font=FONTS['small'],

                                          text_color=COLORS['text_secondary'])

        self.status_label.pack(side='left', padx=(0, 12))



        # ---- 打赏提示 (hover显示收款码) ----

        tip_frame = ctk.CTkFrame(right, fg_color='transparent')

        tip_frame.pack(side='right', padx=(0, 8))


        # 收款码图片（按原图比例缩放）
        wechat_img_path = get_resource_path('assets/images/wechat.jpg')

        try:
            from PIL import Image as PILImage
            wechat_pil = PILImage.open(wechat_img_path)
            # 按原图宽高比计算尺寸：固定宽度200，高度按比例
            orig_w, orig_h = wechat_pil.size
            scale_w = 200
            scale_h = int(scale_w * orig_h / orig_w)
            wechat_ctk = ctk.CTkImage(light_image=wechat_pil, dark_image=wechat_pil,
                                       size=(scale_w, scale_h))
        except Exception:
            wechat_ctk = None


        # 用一个独立顶层弹窗显示收款码
        self._qr_popup = ctk.CTkToplevel(self.root)
        self._qr_popup.withdraw()  # 隐藏
        self._qr_popup.overrideredirect(True)  # 无边框
        self._qr_popup.attributes('-topmost', True)
        self._qr_popup.configure(fg_color=COLORS['bg_card'])

        qr_inner = ctk.CTkFrame(self._qr_popup, fg_color=COLORS['bg_card'], corner_radius=8)
        qr_inner.pack(padx=4, pady=4)

        ctk.CTkLabel(qr_inner, image=wechat_ctk, text="").pack()

        self._tip_frame = tip_frame  # 保存引用用于定位

        # 根据实际图片尺寸设置弹窗大小
        try:
            if wechat_pil:
                popup_w = scale_w + 8  # 图片宽 + 内边距
                popup_h = scale_h + 8
                self._qr_popup.geometry(f"{popup_w}x{popup_h}")
        except Exception:
            pass


        def _show_qr():
            """显示收款码，定位在 tip_frame 下方"""
            try:
                x = tip_frame.winfo_rootx()
                y = tip_frame.winfo_rooty() + tip_frame.winfo_height() + 4
                self._qr_popup.geometry(f"+{x}+{y}")
                self._qr_popup.deiconify()
            except Exception:
                pass


        def _hide_qr():
            self._qr_popup.withdraw()


        tip_label = ctk.CTkLabel(tip_frame, text="请我喝一杯吧",
                     font=FONTS['subtitle'],
                     text_color=COLORS['accent_primary'],
                     cursor='hand2')
        tip_label.pack(side='left', padx=4, pady=4)

        # 点击跳转 GitHub 项目地址
        def _open_github(event=None):
            webbrowser.open('https://github.com/cattei/AutoComment')

        tip_label.bind('<Button-1>', _open_github)

        # 给 frame 和 label 都绑定事件
        for w in [tip_frame, tip_label]:
            w.bind('<Enter>', lambda e: _show_qr())
            w.bind('<Leave>', lambda e: _hide_qr())



        # 版本副标题 (放在右侧)

        ctk.CTkLabel(right, text="智能自动化助手 v2.0",

                     font=FONTS['subtitle'],

                     text_color=COLORS['text_muted']).pack(side='right', padx=(0, 16))



    # ================================================================

    # Main Content - 对齐设计图 grid 布局

    # ================================================================



    def _create_main_content(self):

        """主内容区 - 左侧: 流程配置卡片(弹性), 右侧: 平台设置 + 设备管理 + 运行统计"""

        main = ctk.CTkFrame(self.root, fg_color=COLORS['bg_primary'],

                            corner_radius=0)

        main.grid(row=1, column=0, sticky='nsew', padx=20, pady=10)

        main.grid_columnconfigure(0, weight=1)

        main.grid_columnconfigure(1, weight=0, minsize=360)

        main.grid_rowconfigure(0, weight=1)



        # 左侧面板: 只有流程配置卡片(弹性填满)

        left_panel = ctk.CTkFrame(main, fg_color='transparent')

        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))

        left_panel.grid_rowconfigure(0, weight=1)

        left_panel.grid_columnconfigure(0, weight=1)



        # 右侧面板: 平台设置 + 设备管理 + 运行统计

        right_panel = ctk.CTkFrame(main, fg_color='transparent', width=360)

        right_panel.grid(row=0, column=1, sticky='nsew')

        right_panel.grid_rowconfigure(0, weight=0)  # 平台设置固定

        right_panel.grid_rowconfigure(1, weight=0)  # 设备管理固定

        right_panel.grid_rowconfigure(2, weight=1)  # 运行统计弹性

        right_panel.grid_columnconfigure(0, weight=1)



        self._create_left_panel(left_panel)

        self._create_right_panel(right_panel)



    def _create_left_panel(self, parent):

        parent.grid_rowconfigure(0, weight=1)

        parent.grid_columnconfigure(0, weight=1)



        self._create_procedure_card(parent)



    # ----- 流程配置卡片 (设计图: procedure-area) -----

    def _create_procedure_card(self, parent):

        """自动化流程配置卡片 - 对齐设计图 procedure-area"""

        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'],

                            border_color=COLORS['border_color'],

                            border_width=1, corner_radius=SIZES['radius_lg'])

        card.grid(row=0, column=0, sticky='nsew', pady=(0, 10))

        card.grid_rowconfigure(1, weight=1)

        card.grid_columnconfigure(0, weight=1)



        # ---- card-header ----

        card_header = ctk.CTkFrame(card, fg_color='transparent', height=44)

        card_header.grid(row=0, column=0, sticky='ew', padx=14, pady=(10, 8))

        card_header.grid_columnconfigure(0, weight=1)

        card_header.grid_columnconfigure(1, weight=0)



        # 左侧: 图标(蓝色背景) + 标题 "自动化流程配置"

        left = ctk.CTkFrame(card_header, fg_color='transparent')

        left.grid(row=0, column=0, sticky='w')



        # 蓝色图标背景 (设计图: card-icon blue, accent-primary-glow)

        icon_canvas = tk.Canvas(left, width=28, height=28, bg=COLORS['bg_card'],

                                highlightthickness=0)

        icon_canvas.pack(side='left', padx=(0, 8))

        icon_canvas.create_rectangle(0, 0, 28, 28, fill=COLORS['accent_primary_glow'],

                                     outline='', stipple='')

        # 文档图标线条

        icon_canvas.create_line(8, 8, 20, 8, fill=COLORS['accent_primary'], width=2)

        icon_canvas.create_line(8, 14, 20, 14, fill=COLORS['accent_primary'], width=2)

        icon_canvas.create_line(8, 20, 16, 20, fill=COLORS['accent_primary'], width=2)



        ctk.CTkLabel(left, text="自动化流程配置", font=FONTS['heading'],

                     text_color=COLORS['text_primary']).pack(side='left')



        # 右侧: view-toggle(步骤/命令) + 模板按钮

        right = ctk.CTkFrame(card_header, fg_color='transparent')

        right.grid(row=0, column=1, sticky='e')



        # 模板按钮 (设计图: btn-ghost btn-sm + grid图标)

        template_btn = ctk.CTkButton(right, text="⊞", width=32, height=32,

                                      font=ctk.CTkFont(family='Consolas', size=14),

                                      fg_color=COLORS['bg_input'],

                                      hover_color=COLORS['bg_card_hover'],

                                      text_color=COLORS['text_secondary'],

                                      corner_radius=SIZES['radius_sm'],

                                      command=self.show_templates)

        template_btn.pack(side='right', padx=(8, 0))



        # view-toggle (设计图: 步骤/命令 切换)

        toggle_frame = ctk.CTkSegmentedButton(right,

                                               values=["步骤", "命令"],

                                               font=FONTS['tiny'],

                                               fg_color=COLORS['bg_input'],

                                               selected_color=COLORS['accent_primary'],

                                               selected_hover_color=COLORS['accent_primary_hover'],

                                               unselected_color=COLORS['bg_input'],

                                               unselected_hover_color=COLORS['bg_card_hover'],

                                               command=self._on_view_toggle)

        toggle_frame.set("步骤")

        toggle_frame.pack(side='right')

        self.view_toggle = toggle_frame



        # 分隔线

        sep = ctk.CTkFrame(card, fg_color=COLORS['border_color'], height=1)

        sep.grid(row=0, column=0, sticky='ew', pady=(46, 0))



        # ---- card-body ----

        self.card_body = ctk.CTkFrame(card, fg_color='transparent')

        self.card_body.grid(row=1, column=0, sticky='nsew')

        self.card_body.grid_rowconfigure(0, weight=1)

        self.card_body.grid_columnconfigure(0, weight=1)



        # 步骤视图 - 可编辑任务文本区域

        self.steps_container = ctk.CTkFrame(self.card_body, fg_color='transparent')

        self.steps_container.grid(row=0, column=0, sticky='nsew')

        self.steps_container.grid_rowconfigure(0, weight=1)

        self.steps_container.grid_columnconfigure(0, weight=1)



        self.task_view = ctk.CTkTextbox(self.steps_container,

                                         fg_color=COLORS['bg_input'],

                                         text_color=COLORS['text_primary'],

                                         font=FONTS['body'],

                                         corner_radius=SIZES['radius_sm'],

                                         border_color=COLORS['border_color'],

                                         border_width=1,

                                         wrap='word')

        self.task_view.grid(row=0, column=0, sticky='nsew', padx=18, pady=16)



        # 初始化任务文本

        self.task_view.insert('1.0', self.task_var.get() or "输入你想要执行的任务...")

        self.task_view.bind('<KeyRelease>', self._on_task_text_change)



        # 命令视图 - 终端风格 (设计图: command-view bg-console)

        self.cmd_view = ctk.CTkTextbox(self.card_body,

                                        fg_color=COLORS['bg_console'],

                                        text_color=COLORS['text_secondary'],

                                        font=FONTS['console'],

                                        corner_radius=0,

                                        wrap='word')

        # 命令视图默认隐藏

        self.cmd_view.grid_remove()



    # ================================================================

    # Right Panel

    # ================================================================



    def _create_right_panel(self, parent):

        self._create_platform_card(parent)

        self._create_device_card(parent)

        self._create_stats_card(parent)



    # ----- 平台设置卡片 -----

    def _create_platform_card(self, parent):

        """平台设置卡片 - 平台选择 + 参数配置 + 操作类型"""

        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'],

                            border_color=COLORS['border_color'],

                            border_width=1, corner_radius=SIZES['radius_lg'])

        card.grid(row=0, column=0, sticky='ew', pady=(0, 10))

        card.grid_columnconfigure(0, weight=1)



        # card-header

        card_header = ctk.CTkFrame(card, fg_color='transparent', height=44)

        card_header.grid(row=0, column=0, sticky='ew', padx=14, pady=(10, 8))

        card_header.grid_columnconfigure(0, weight=1)



        title_row = ctk.CTkFrame(card_header, fg_color='transparent')

        title_row.grid(row=0, column=0, sticky='w')



        icon_canvas = tk.Canvas(title_row, width=18, height=18,

                                bg=COLORS['bg_card'], highlightthickness=0)

        icon_canvas.pack(side='left', padx=(0, 8))

        icon_canvas.create_rectangle(2, 2, 16, 16, fill=COLORS['accent_primary'], outline='')

        icon_canvas.create_text(9, 9, text="⚙", fill='white', font=('Microsoft YaHei', 10))



        ctk.CTkLabel(title_row, text="平台设置", font=FONTS['heading'],

                     text_color=COLORS['text_primary']).pack(side='left')



        ctk.CTkLabel(card_header, text="", font=FONTS['body'],

                     text_color=COLORS['text_muted']).grid(row=0, column=1, sticky='e')



        ctk.CTkFrame(card, fg_color=COLORS['border_color'], height=1).grid(

            row=1, column=0, sticky='ew')



        # card-body

        body = ctk.CTkFrame(card, fg_color='transparent')

        body.grid(row=2, column=0, sticky='ew', padx=14, pady=12)



        # 平台选择

        platform_frame = ctk.CTkFrame(body, fg_color='transparent')

        platform_frame.pack(fill='x', pady=(0, 10))

        ctk.CTkLabel(platform_frame, text="平台选择", font=FONTS['small'],

                     text_color=COLORS['text_muted']).pack(anchor='w', pady=(0, 4))

        self.platform_combo = ctk.CTkComboBox(platform_frame, variable=self.platform_var,

                                               values=['小红书', '微信朋友圈', '微信视频号', '抖音', 'B站', '快手', '微博'],

                                               font=FONTS['body'],

                                               fg_color=COLORS['bg_input'],

                                               border_color=COLORS['border_color'],

                                               button_color=COLORS['border_color'],

                                               button_hover_color=COLORS['accent_primary'],

                                               dropdown_fg_color=COLORS['bg_card'],

                                               state='readonly',

                                               corner_radius=SIZES['radius_sm'],

                                               command=self._on_platform_change)

        self.platform_combo.pack(fill='x')

        self.platform_combo.bind('<Button-1>', lambda e: self.platform_combo._open_dropdown_menu())



        # 参数行: 最大步数 | 执行次数 | 温度值

        param_row = ctk.CTkFrame(body, fg_color='transparent')

        param_row.pack(fill='x', pady=(0, 10))

        param_row.grid_columnconfigure(0, weight=1)

        param_row.grid_columnconfigure(1, weight=1)

        param_row.grid_columnconfigure(2, weight=1)



        # 最大步数

        f1 = ctk.CTkFrame(param_row, fg_color='transparent')

        f1.grid(row=0, column=0, sticky='ew', padx=(0, 6))

        ctk.CTkLabel(f1, text="最大步数", font=FONTS['small'],

                     text_color=COLORS['text_muted']).pack(anchor='w', pady=(0, 3))

        self.max_steps_entry = ctk.CTkEntry(f1, textvariable=self.max_steps_var,

                                              font=FONTS['body'],

                                              fg_color=COLORS['bg_input'],

                                              border_color=COLORS['border_color'],

                                              corner_radius=SIZES['radius_sm'])

        self.max_steps_entry.pack(fill='x')



        # 执行次数

        f2 = ctk.CTkFrame(param_row, fg_color='transparent')

        f2.grid(row=0, column=1, sticky='ew', padx=(3, 3))

        ctk.CTkLabel(f2, text="执行次数", font=FONTS['small'],

                     text_color=COLORS['text_muted']).pack(anchor='w', pady=(0, 3))

        self.repeat_count_var = tk.StringVar(value='20')

        self.repeat_count_entry = ctk.CTkEntry(f2, textvariable=self.repeat_count_var,

                                                font=FONTS['body'],

                                                fg_color=COLORS['bg_input'],

                                                border_color=COLORS['border_color'],

                                                corner_radius=SIZES['radius_sm'])

        self.repeat_count_entry.pack(fill='x')

        self.repeat_count_entry.bind('<KeyRelease>', self._on_repeat_count_change)



        # 温度值

        f3 = ctk.CTkFrame(param_row, fg_color='transparent')

        f3.grid(row=0, column=2, sticky='ew', padx=(3, 0))

        ctk.CTkLabel(f3, text="温度值", font=FONTS['small'],

                     text_color=COLORS['text_muted']).pack(anchor='w', pady=(0, 3))

        temp_inner = ctk.CTkFrame(f3, fg_color='transparent')

        temp_inner.pack(fill='x')

        self.temp_slider = ctk.CTkSlider(temp_inner, from_=0, to=1,

                                          variable=self.temperature_var,

                                          number_of_steps=10,

                                          fg_color=COLORS['border_color'],

                                          progress_color=COLORS['accent_primary'],

                                          button_color=COLORS['accent_primary'],

                                          button_hover_color=COLORS['accent_primary_hover'],

                                          command=self._on_temp_change)

        self.temp_slider.pack(side='left', fill='x', expand=True)

        self.temp_value_label = ctk.CTkLabel(temp_inner, text=f"{self.temperature_var.get():.1f}",

                                              font=FONTS['body'],

                                              text_color=COLORS['accent_primary'],

                                              width=36)

        self.temp_value_label.pack(side='right', padx=(6, 0))



        # 操作类型

        self._create_operation_types_in_card(body)



    def _create_operation_types_in_card(self, parent):

        """操作类型 - 单选按钮，放在平台设置卡片内"""

        frame = ctk.CTkFrame(parent, fg_color='transparent')

        frame.pack(fill='x', pady=(0, 0))

        ctk.CTkLabel(frame, text="操作类型", font=FONTS['small'],

                     text_color=COLORS['text_muted']).pack(anchor='w', pady=(0, 6))



        checks = ctk.CTkFrame(frame, fg_color='transparent')

        checks.pack(fill='x')

        self.operation_checks_frame = checks



        # op_icons已在_create_operation_types中初始化，此处复用
        if not hasattr(self, 'op_icons'):
            self.op_icons = {
                "点赞": "👍",
                "评论": "💬",
                "点赞评论": "👍💬",
                "收藏": "⭐",
                "关注": "➕",
                "转发": "🔄",
                "分享": "📤",
                "投币": "🪙"
            }
        self.selected_operation = tk.StringVar(value="点赞")
        self._update_operation_checkboxes('小红书')



    # ----- 设备管理卡片 (设计图: device-card) -----

    def _create_device_card(self, parent):

        """ADB 设备管理卡片 - 对齐设计图"""

        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'],

                            border_color=COLORS['border_color'],

                            border_width=1, corner_radius=SIZES['radius_lg'])

        card.grid(row=1, column=0, sticky='ew', pady=(0, 8))

        card.grid_columnconfigure(0, weight=1)



        # ---- card-header ----

        ch = ctk.CTkFrame(card, fg_color='transparent')

        ch.grid(row=0, column=0, sticky='ew', padx=14, pady=(10, 8))

        ch.grid_columnconfigure(0, weight=1)

        ch.grid_columnconfigure(1, weight=0)



        left = ctk.CTkFrame(ch, fg_color='transparent')

        left.grid(row=0, column=0, sticky='w')



        # 青色图标 (设计图: card-icon cyan)

        icon_c = tk.Canvas(left, width=28, height=28, bg=COLORS['bg_card'], highlightthickness=0)

        icon_c.pack(side='left', padx=(0, 8))

        icon_c.create_rectangle(0, 0, 28, 28, fill=COLORS['accent_cyan_glow'], outline='')

        icon_c.create_rectangle(10, 3, 18, 24, outline=COLORS['accent_cyan'], width=2)

        icon_c.create_oval(12, 21, 16, 24, fill=COLORS['accent_cyan'], outline='')



        ctk.CTkLabel(left, text="ADB 设备管理", font=FONTS['heading'],

                     text_color=COLORS['text_primary']).pack(side='left')



        # 分隔线

        ctk.CTkFrame(card, fg_color=COLORS['border_color'], height=1).grid(row=1, column=0, sticky='ew')



        # ---- card-body ----

        body = ctk.CTkFrame(card, fg_color='transparent')

        body.grid(row=2, column=0, sticky='ew', padx=14, pady=(8, 10))

        body.grid_columnconfigure(0, weight=1)



        # 6个按钮 - 3x2 grid (设计图: device-actions)

        btn_frame = ctk.CTkFrame(body, fg_color='transparent')

        btn_frame.pack(fill='x', pady=(0, 8))

        for c in range(3):

            btn_frame.grid_columnconfigure(c, weight=1)



        buttons = [

            ("↻ 刷新设备", self.refresh_devices),

            ("⊕ 连接设备", self.connect_device),

            ("ℹ 设备详情", self.device_details),

            ("↓ 安装键盘", self.install_keyboard),

            ("▣ 远程桌面", self.remote_desktop),

            ("◉ 截图", self.screenshot),

        ]



        for i, (text, cmd) in enumerate(buttons):

            r, c = i // 3, i % 3

            btn = ctk.CTkButton(btn_frame, text=text,

                                 font=FONTS['tiny'],

                                 fg_color=COLORS['bg_input'],

                                 hover_color=COLORS['bg_card_hover'],

                                 text_color=COLORS['text_secondary'],

                                 border_color=COLORS['border_color'],

                                 border_width=1,

                                 corner_radius=SIZES['radius_sm'],

                                 height=28,

                                 command=cmd)

            btn.grid(row=r, column=c, padx=(0 if c == 0 else 6, 0),

                     pady=(0 if r == 0 else 6, 0), sticky='ew')



        # 选择设备区域 (设计图: device-select-area)

        ctk.CTkLabel(body, text="选择设备", font=FONTS['small'],

                     text_color=COLORS['text_secondary']).pack(anchor='w', pady=(0, 4))



        # 设备下拉选择框

        self.device_combo = ctk.CTkComboBox(body, variable=self.device_list_var,

                                              font=FONTS['mono'],

                                              fg_color=COLORS['bg_input'],

                                              border_color=COLORS['border_color'],

                                              button_color=COLORS['border_color'],

                                              button_hover_color=COLORS['accent_primary'],

                                              dropdown_fg_color=COLORS['bg_card'],

                                              state='readonly',

                                              corner_radius=SIZES['radius_sm'],

                                              height=32)

        self.device_combo.pack(fill='x', pady=(0, 4))

        self.device_combo.bind('<<ComboboxSelected>>', self._on_device_selected)



    # ----- 运行统计卡片 (设计图: stats) -----

    def _create_stats_card(self, parent):

        """运行统计 - 对齐设计图: 点赞次数/评论次数/收藏次数/关注次数"""

        card = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'],

                            border_color=COLORS['border_color'],

                            border_width=1, corner_radius=SIZES['radius_lg'])

        card.grid(row=2, column=0, sticky='ew', pady=(0, 8))

        card.grid_columnconfigure(0, weight=1)



        # ---- header ----

        ch = ctk.CTkFrame(card, fg_color='transparent')

        ch.grid(row=0, column=0, sticky='ew', padx=14, pady=(10, 6))



        icon_c = tk.Canvas(ch, width=28, height=28, bg=COLORS['bg_card'], highlightthickness=0)

        icon_c.pack(side='left', padx=(0, 8))

        icon_c.create_rectangle(0, 0, 28, 28, fill=COLORS['accent_amber_glow'], outline='')

        icon_c.create_line(7, 19, 7, 10, fill=COLORS['accent_amber'], width=3)

        icon_c.create_line(14, 19, 14, 5, fill=COLORS['accent_amber'], width=3)

        icon_c.create_line(21, 19, 21, 14, fill=COLORS['accent_amber'], width=3)



        ctk.CTkLabel(ch, text="运行统计", font=FONTS['heading'],

                     text_color=COLORS['text_primary']).pack(side='left')



        # 分隔线

        ctk.CTkFrame(card, fg_color=COLORS['border_color'], height=1).grid(row=1, column=0, sticky='ew')



        # ---- body ----
        body = ctk.CTkFrame(card, fg_color='transparent')
        body.grid(row=2, column=0, sticky='ew', padx=12, pady=(6, 8))

        # 单行4列统计网格 (紧凑布局)
        stats_frame = ctk.CTkFrame(body, fg_color='transparent')
        stats_frame.pack(fill='x', pady=(0, 6))
        for c in range(4):
            stats_frame.grid_columnconfigure(c, weight=1)

        stats_config = [
            ('likes', '点赞次数', COLORS['accent_green']),
            ('comments', '评论次数', COLORS['accent_primary']),
            ('collects', '收藏次数', COLORS['accent_amber']),
            ('follows', '关注次数', COLORS['accent_cyan']),
        ]

        for i, (key, label, color) in enumerate(stats_config):
            r, c = 0, i
            item = ctk.CTkFrame(stats_frame, fg_color=COLORS['bg_input'],
                                 border_color=COLORS['border_color'],
                                 border_width=1, corner_radius=SIZES['radius_sm'])
            item.grid(row=r, column=c, padx=(0 if c == 0 else 6, 0), sticky='ew')

            val = ctk.CTkLabel(item, text="0", font=FONTS['stat_value'],
                                text_color=color)
            val.pack(pady=(6, 0))
            ctk.CTkLabel(item, text=label, font=FONTS['tiny'],
                         text_color=COLORS['text_muted']).pack(pady=(2, 6))
            setattr(self, f'stat_{key}', val)



        # 进度

        pf = ctk.CTkFrame(body, fg_color='transparent')

        pf.pack(fill='x')



        pf_left = ctk.CTkFrame(pf, fg_color='transparent')

        pf_left.pack(fill='x')

        ctk.CTkLabel(pf_left, text="任务进度", font=FONTS['small'],

                     text_color=COLORS['text_secondary']).pack(side='left')

        self.progress_text = ctk.CTkLabel(pf_left, text="0 / 20", font=FONTS['small'],

                                           text_color=COLORS['accent_primary'])

        self.progress_text.pack(side='right')



        # 进度条 (设计图: 渐变 #6366f1 → #a855f7)

        self.progress_bar = ctk.CTkProgressBar(body, fg_color=COLORS['bg_input'],

                                                 progress_color=COLORS['accent_primary'],

                                                 corner_radius=3, height=6)

        self.progress_bar.pack(fill='x', pady=(6, 0))

        self.progress_bar.set(0)



    # ================================================================

    # Toolbar - 对齐设计图底部工具栏

    # ================================================================



    def _create_toolbar(self):

        """底部工具栏 - 对齐设计图 toolbar 布局"""

        # 顶部边框

        toolbar_outer = ctk.CTkFrame(self.root, fg_color='transparent', corner_radius=0)

        toolbar_outer.grid(row=2, column=0, sticky='ew')



        ctk.CTkFrame(toolbar_outer, fg_color=COLORS['border_color'], height=1).pack(fill='x')



        toolbar = ctk.CTkFrame(toolbar_outer, fg_color=COLORS['bg_secondary'], height=50,

                                corner_radius=0)

        toolbar.pack(fill='x')



        inner = ctk.CTkFrame(toolbar, fg_color='transparent')

        inner.pack(fill='x', padx=24, pady=12)



        # ---- 左侧: 唤醒 + 保存/加载配置 ----

        ctk.CTkButton(inner, text="🌙 唤醒", font=FONTS['small'],

                       fg_color=COLORS['bg_input'],

                       hover_color=COLORS['bg_card_hover'],

                       text_color=COLORS['text_secondary'],

                       border_color=COLORS['border_color'],

                       border_width=1,

                       corner_radius=SIZES['radius_sm'],

                       width=90, height=32,

                       command=self.wake_device).pack(side='left')



        # ---- 分隔线 ----

        sep1 = tk.Canvas(inner, width=1, height=28, bg=COLORS['border_color'],

                         highlightthickness=0)

        sep1.pack(side='left', padx=16)



        # ---- 保存/加载配置 ----

        ctk.CTkButton(inner, text="💾 保存配置", font=FONTS['small'],

                       fg_color=COLORS['bg_input'],

                       hover_color=COLORS['bg_card_hover'],

                       text_color=COLORS['text_secondary'],

                       border_color=COLORS['border_color'],

                       border_width=1,

                       corner_radius=SIZES['radius_sm'],

                       width=100, height=32,

                       command=self.save_config).pack(side='left', padx=(0, 8))



        ctk.CTkButton(inner, text="📂 加载配置", font=FONTS['small'],

                       fg_color=COLORS['bg_input'],

                       hover_color=COLORS['bg_card_hover'],

                       text_color=COLORS['text_secondary'],

                       border_color=COLORS['border_color'],

                       border_width=1,

                       corner_radius=SIZES['radius_sm'],

                       width=100, height=32,

                       command=self.load_config).pack(side='left')



        # ---- 右侧: 历史 + AI 润色 + 分隔线 + 运行 + 停止 ----

        ctk.CTkButton(inner, text="⏱ 历史", font=FONTS['small'],

                       fg_color=COLORS['bg_input'],

                       hover_color=COLORS['bg_card_hover'],

                       text_color=COLORS['text_secondary'],

                       border_color=COLORS['border_color'],

                       border_width=1,

                       corner_radius=SIZES['radius_sm'],

                       width=90, height=32,

                       command=self.show_history).pack(side='right', padx=(0, 8))



        # 设计图: btn-accent 蓝紫色 AI 润色按钮

        ctk.CTkButton(inner, text="★ AI 润色", font=FONTS['small'],

                       fg_color=COLORS['accent_primary'],

                       hover_color=COLORS['accent_primary_hover'],

                       text_color='white',

                       corner_radius=SIZES['radius_sm'],

                       width=100, height=32,

                       command=self.ai_polish).pack(side='right')



        # ---- 分隔线 ----

        sep2 = tk.Canvas(inner, width=1, height=28, bg=COLORS['border_color'],

                         highlightthickness=0)

        sep2.pack(side='right', padx=12)



        # ---- 运行 + 停止 (设计图: btn-primary 绿色 + btn-danger 红色) ----

        self.stop_btn = ctk.CTkButton(inner, text="■ 停止", font=FONTS['body'],

                                       fg_color=COLORS['accent_red'],

                                       hover_color=COLORS['accent_red_hover'],

                                       text_color='white',

                                       corner_radius=SIZES['radius_sm'],

                                       width=100, height=36,

                                       state='disabled',

                                       command=self.stop_run)

        self.stop_btn.pack(side='right', padx=(0, 8))



        self.run_btn = ctk.CTkButton(inner, text="▶ 运行", font=FONTS['body'],

                                      fg_color=COLORS['accent_green'],

                                      hover_color=COLORS['accent_green_hover'],

                                      text_color='white',

                                      corner_radius=SIZES['radius_sm'],

                                      width=100, height=36,

                                      command=self.start_run)

        self.run_btn.pack(side='right')



    # ================================================================

    # 视图切换

    # ================================================================



    def _on_view_toggle(self, value):

        """视图切换回调"""

        if value == "步骤":

            self.switch_view('steps')

        else:

            self.switch_view('cmd')



    def switch_view(self, view):

        """切换步骤/命令视图"""

        self.current_view = view

        if view == 'steps':

            self.cmd_view.grid_remove()

            self.task_view.grid(row=0, column=0, sticky='nsew', padx=18, pady=16)

        else:

            self.task_view.grid_remove()

            self.cmd_view.grid(row=0, column=0, sticky='nsew')



    # ================================================================

    # 日志输出

    # ================================================================



    def log_message(self, msg, msg_type='info'):

        """输出到左侧命令视图"""

        ts = datetime.now().strftime("%H:%M:%S")

        self.cmd_view.insert(tk.END, f"[{ts}] ", 'time')

        self.cmd_view.insert(tk.END, f"{msg}\n", msg_type)

        self.cmd_view.see(tk.END)



    def log_cmd(self, msg, msg_type='info'):

        """输出到左侧命令视图"""

        ts = datetime.now().strftime("%H:%M:%S")

        prefix_map = {

            'info': ('>', ''),

            'think': ('?', 'think'),

            'action': ('->', 'action'),

            'success': ('OK', 'success'),

            'error': ('!!', 'error'),

            'divider': ('--', 'divider'),

        }

        prefix, tag = prefix_map.get(msg_type, ('>', ''))

        self.cmd_view.insert(tk.END, f"{ts} ", 'time')

        if tag:

            self.cmd_view.insert(tk.END, f"{prefix} ", tag)

        self.cmd_view.insert(tk.END, f"{msg}\n")

        self.cmd_view.see(tk.END)



    def _on_executor_output(self, text):

        """TaskExecutor 的流式输出回调"""

        self.cmd_view.insert(tk.END, text)

        self.cmd_view.see(tk.END)



    def clear_console(self):

        self.cmd_view.delete('1.0', tk.END)

        self.log_message('控制台已清空', 'info')



    # ================================================================

    # 进度 & 时钟

    # ================================================================



    def update_progress(self, pct):

        """更新进度条"""

        try:

            self.progress_bar.set(pct / 100.0)

        except Exception:

            pass



    def update_clock(self):

        now = datetime.now()

        self.time_label.configure(text=now.strftime("%Y-%m-%d %H:%M:%S"))

        self.root.after(1000, self.update_clock)



    def _on_temp_change(self, value):

        """温度滑块变更"""

        try:

            self.temp_value_label.configure(text=f"{float(value):.1f}")

        except Exception:

            pass



    def _on_repeat_count_change(self, event=None):

        """执行次数变更时验证输入"""

        try:

            value = self.repeat_count_var.get()

            if value:

                num = int(value)

                if num < 1:

                    self.repeat_count_var.set('1')

                    num = 1

                elif num > 100:

                    self.repeat_count_var.set('100')

                    num = 100

                # 同步更新任务进度显示

                self.progress_text.configure(text=f"0 / {num}")

        except ValueError:

            # 非数字输入，恢复为20

            self.repeat_count_var.set('20')

            self.progress_text.configure(text="0 / 20")



    def _on_task_text_change(self, event=None):

        """任务文本变更时同步到 config_manager"""

        try:

            self.task_var.set(self.task_view.get('1.0', tk.END).strip())

        except Exception:

            pass



    # ================================================================

    # 运行控制 - 接入真实 PhoneAgent

    # ================================================================



    def start_run(self):

        """开始执行任务"""

        if self.is_running:

            return



        task = self.task_view.get('1.0', tk.END).strip()

        if not task or task == "输入你想要执行的任务...":

            messagebox.showwarning("提示", "请先输入要执行的任务描述")

            return



        device_id = self.device_manager.get_selected_device()

        if not device_id:

            messagebox.showwarning("提示", "请先连接并选择设备")

            return



        # 保存当前任务和配置

        self._save_current_task()



        self.is_running = True

        self.current_step = 0

        self.stats = {'likes': 0, 'comments': 0, 'collects': 0, 'follows': 0}



        self.run_btn.configure(state='disabled')

        self.stop_btn.configure(state='normal')

        self.repeat_count_entry.configure(state='disabled')  # 禁用执行次数输入框



        for key in self.stats:

            getattr(self, f'stat_{key}').configure(text='0')

        self.update_progress(0)



        # 获取执行次数

        try:

            repeat_count = int(self.repeat_count_var.get() or 1)

        except ValueError:

            repeat_count = 1



        self.progress_text.configure(text=f"0 / {repeat_count}")



        self.switch_view('cmd')

        self.cmd_view.delete('1.0', tk.END)



        platform = self.platform_var.get()



        self.log_cmd("═" * 35, 'divider')

        self.log_cmd(f"任务启动 | 平台: {platform} | 温度: {self.temperature_var.get():.1f}", 'info')

        self.log_cmd(f"最大步数: {self.max_steps_var.get()} | 执行次数: {repeat_count} | 设备: {device_id}", 'info')

        self.log_cmd("═" * 35, 'divider')

        self.log_message(f"━━━ 开始执行自动化任务 (共{repeat_count}次) ━━━", 'step')

        self._set_status("运行中", COLORS['accent_amber'])



        try:

            from phone_agent.agent import PhoneAgent, AgentConfig

            from phone_agent.model import ModelConfig

            from phone_agent.device_factory import set_device_type, DeviceType



            model_config = ModelConfig(

                base_url=self.config_manager.base_url.get(),

                api_key=self.config_manager.apikey.get(),

                model_name=self.config_manager.model.get(),

                temperature=float(self.config_manager.temperature.get() or 0.0),

                lang="cn",

            )



            agent_config = AgentConfig(

                max_steps=int(self.max_steps_var.get() or 200),

                device_id=device_id,

                lang="cn",

                verbose=True,

            )



            device_type_map = {"安卓": DeviceType.ADB, "iOS": DeviceType.IOS, "鸿蒙": DeviceType.HDC}

            set_device_type(device_type_map.get(self.device_type_var.get(), DeviceType.ADB))



            agent = PhoneAgent(

                model_config=model_config,

                agent_config=agent_config,

                confirmation_callback=self._confirmation_callback,

                takeover_callback=self._takeover_callback,

            )



            self.total_steps = agent_config.max_steps



        except Exception as e:

            self.log_cmd(f"初始化失败: {e}", 'error')

            self.log_message(f"初始化失败: {e}", 'error')

            self._finish_run(failed=True)

            return



        self.task_history.add(task, platform)



        self.current_repeat = 0

        self.total_repeats = repeat_count



        self.task_executor.running = True

        original_stdout = sys.stdout

        sys.stdout = StreamOutputCollector(self._safe_cmd_output, lambda: self.task_executor.running)



        def run_with_redirect():

            try:

                for i in range(repeat_count):

                    if not self.task_executor.running:

                        break



                    self.current_repeat = i + 1

                    self.root.after(0, lambda idx=i: self.log_cmd(f"\n━━━ 第 {idx+1}/{repeat_count} 次执行 ━━━", 'divider'))



                    result = agent.run(task)

                    self.root.after(0, lambda r=result: self.log_cmd(f"第 {self.current_repeat} 次完成: {r}", 'success'))



                    # 更新统计和进度

                    self.root.after(0, self._update_stats_from_result)

                    self.root.after(0, lambda: self._update_progress_display(self.current_repeat, repeat_count))



                self.root.after(0, lambda: self.log_cmd(f"\n全部完成: 共执行 {self.current_repeat} 次", 'success'))

                self.root.after(0, lambda: self.log_message(f"任务执行完成 (共{self.current_repeat}次)", 'success'))

            except Exception as e:

                self.root.after(0, lambda: self.log_cmd(f"\n执行出错: {e}", 'error'))

                self.root.after(0, lambda: self.log_message(f"执行出错: {e}", 'error'))

            finally:

                sys.stdout = original_stdout

                self.task_executor.running = False

                self.root.after(0, self._finish_run)



        self._agent_thread = threading.Thread(target=run_with_redirect, daemon=True)

        self._agent_thread.start()



    def _update_stats_from_result(self):

        """从执行结果更新统计数据"""

        # 每次执行完成后，根据操作类型更新统计

        operation = self.selected_operation.get()

        if '点赞' in operation:

            self.stats['likes'] += 1

            self.stat_likes.configure(text=str(self.stats['likes']))

        if '评论' in operation:

            self.stats['comments'] += 1

            self.stat_comments.configure(text=str(self.stats['comments']))

        if operation == '收藏':

            self.stats['collects'] += 1

            self.stat_collects.configure(text=str(self.stats['collects']))

        if operation == '关注':

            self.stats['follows'] += 1

            self.stat_follows.configure(text=str(self.stats['follows']))



    def _update_progress_display(self, current, total):

        """更新进度显示"""

        self.progress_text.configure(text=f"{current} / {total}")

        self.update_progress(current / total if total > 0 else 0)



    def _safe_cmd_output(self, text):

        """线程安全地输出到命令视图"""

        try:

            self.root.after(0, lambda: self.cmd_view.insert(tk.END, text))

            self.root.after(0, lambda: self.cmd_view.see(tk.END))

        except Exception:

            pass



    def _confirmation_callback(self, message: str) -> bool:

        """敏感操作确认回调"""

        result = {'confirmed': False}

        event = threading.Event()



        def show_dialog():

            result['confirmed'] = messagebox.askyesno("操作确认",

                                                       f"AI 请求执行敏感操作:\n\n{message}\n\n是否允许?")

            event.set()



        self.root.after(0, show_dialog)

        event.wait(timeout=60)

        return result['confirmed']



    def _takeover_callback(self, message: str) -> None:

        """人工接管回调"""

        event = threading.Event()



        def show_dialog():

            messagebox.showinfo("需要人工操作",

                                f"AI 请求人工接管:\n\n{message}\n\n完成操作后点击确定继续")

            event.set()



        self.root.after(0, show_dialog)

        event.wait()



    def _finish_run(self, failed=False):

        """运行结束"""

        self.is_running = False

        self.run_btn.configure(state='normal')

        self.stop_btn.configure(state='disabled')

        self.repeat_count_entry.configure(state='normal')  # 恢复执行次数输入框



        if not failed:

            self.log_cmd("任务执行结束", 'success')

            self._set_status("完成", COLORS['accent_green'])

        else:

            self._set_status("出错", COLORS['accent_red'])



        self.root.after(3000, lambda: self.switch_view('steps') if not self.is_running else None)



    def stop_run(self):

        """停止运行"""

        self.task_executor.running = False

        self.is_running = False

        self.run_btn.configure(state='normal')

        self.repeat_count_entry.configure(state='normal')  # 恢复执行次数输入框

        self.stop_btn.configure(state='disabled')

        self.log_cmd("任务已手动停止", 'error')

        self.log_message("任务已停止", 'warning')

        self._set_status("已停止", COLORS['accent_red'])



    # ================================================================

    # 设备操作 - 真实实现

    # ================================================================



    def _schedule_device_scan(self):

        threading.Thread(target=self._do_initial_scan, daemon=True).start()



    def _do_initial_scan(self):

        try:

            # 直接同步扫描，不嵌套线程

            self.device_manager.refresh_devices()

            self.root.after(0, self._update_device_combo)

        except Exception:

            pass



    def _update_device_combo(self):

        devices = self.device_manager.connected_devices

        if self.device_combo is None:

            return



        device_names = []

        for d in devices:

            model = d.get('model', 'Unknown')

            dev_id = d.get('id', '')

            device_names.append(f"{dev_id} ({model})")



        self.device_combo.configure(values=device_names)



        if device_names:

            saved = self.config_manager.selected_device_id.get()

            matched = False

            if saved:

                for i, name in enumerate(device_names):

                    if saved in name:

                        self.device_combo.set(name)

                        self.device_list_var.set(name)

                        self.device_manager.selected_device_id.set(name)

                        matched = True

                        break

            if not matched:

                self.device_combo.set(device_names[0])

                self.device_list_var.set(device_names[0])

                self.device_manager.selected_device_id.set(device_names[0])



            self._set_status("设备已连接", COLORS['accent_green'])

            self.log_message(f'检测到 {len(devices)} 台设备', 'success')

        else:

            self.device_combo.set('')

            self.device_list_var.set('')

            self._set_status("未连接", COLORS['text_muted'])

            self.log_message('未检测到设备，请连接设备后刷新', 'warning')



    def refresh_devices(self):

        self.log_message('正在扫描设备...', 'info')

        self.device_combo.set('扫描中...')



        def do_scan():

            try:

                self.device_manager.refresh_devices()

                self.root.after(0, self._update_device_combo)

            except Exception:

                self.root.after(0, lambda: self.log_message('扫描设备失败', 'error'))



        threading.Thread(target=do_scan, daemon=True).start()



    def connect_device(self):

        """连接远程设备"""

        dialog = ctk.CTkToplevel(self.root)

        dialog.title("连接远程设备")

        dialog.geometry("380x220")

        dialog.configure(fg_color=COLORS['bg_card'])

        dialog.transient(self.root)

        dialog.grab_set()



        dialog.update_idletasks()

        x = self.root.winfo_x() + (self.root.winfo_width() - 380) // 2

        y = self.root.winfo_y() + (self.root.winfo_height() - 220) // 2

        dialog.geometry(f"+{x}+{y}")



        ctk.CTkLabel(dialog, text="远程设备连接", font=FONTS['heading'],

                     text_color=COLORS['text_primary']).pack(pady=(20, 10))



        form = ctk.CTkFrame(dialog, fg_color='transparent')

        form.pack(padx=30, fill='x')

        form.grid_columnconfigure(1, weight=1)



        ctk.CTkLabel(form, text="IP 地址:", font=FONTS['small'],

                     text_color=COLORS['text_secondary']).grid(row=0, column=0, sticky='w', pady=4)

        ip_var = tk.StringVar(value=self.config_manager.last_remote_connection.get('ip', '192.168.1.100'))

        ip_entry = ctk.CTkEntry(form, textvariable=ip_var, font=FONTS['body'],

                                 fg_color=COLORS['bg_input'], border_color=COLORS['border_color'],

                                 corner_radius=SIZES['radius_sm'])

        ip_entry.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=4)



        ctk.CTkLabel(form, text="端口号:", font=FONTS['small'],

                     text_color=COLORS['text_secondary']).grid(row=1, column=0, sticky='w', pady=4)

        port_var = tk.StringVar(value=self.config_manager.last_remote_connection.get('port', '5555'))

        port_entry = ctk.CTkEntry(form, textvariable=port_var, font=FONTS['body'],

                                   fg_color=COLORS['bg_input'], border_color=COLORS['border_color'],

                                   corner_radius=SIZES['radius_sm'])

        port_entry.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=4)



        btn_frame = ctk.CTkFrame(dialog, fg_color='transparent')

        btn_frame.pack(pady=20)



        def do_connect():

            ip = ip_var.get().strip()

            port = port_var.get().strip()

            if not ip:

                messagebox.showwarning("提示", "请输入IP地址", parent=dialog)

                return

            dialog.destroy()

            self.log_message(f'正在连接 {ip}:{port}...', 'info')



            def bg_connect():

                success, msg = self.device_manager.connect_remote_device(ip, port)

                if success:

                    self.root.after(0, lambda: self.log_message(f'连接成功: {msg}', 'success'))

                    self.root.after(0, self._update_device_combo)

                else:

                    self.root.after(0, lambda: self.log_message(f'连接失败: {msg}', 'error'))



            threading.Thread(target=bg_connect, daemon=True).start()



        ctk.CTkButton(btn_frame, text="连接", font=FONTS['body'],

                       fg_color=COLORS['accent_primary'],

                       hover_color=COLORS['accent_primary_hover'],

                       corner_radius=SIZES['radius_sm'],

                       width=80, height=32,

                       command=do_connect).pack(side='left', padx=8)



        ctk.CTkButton(btn_frame, text="取消", font=FONTS['body'],

                       fg_color=COLORS['bg_input'],

                       hover_color=COLORS['bg_card_hover'],

                       text_color=COLORS['text_secondary'],

                       border_color=COLORS['border_color'],

                       border_width=1,

                       corner_radius=SIZES['radius_sm'],

                       width=80, height=32,

                       command=dialog.destroy).pack(side='left', padx=8)



    def device_details(self):

        device_id = self.device_manager.get_selected_device()

        if not device_id:

            self.log_message('请先选择设备', 'warning')

            return



        def do_details():

            try:

                creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

                prefix = ['adb', '-s', device_id]



                def run_shell(cmd):

                    r = subprocess.run(prefix + ['shell'] + cmd,

                                     capture_output=True, text=True, timeout=5,

                                     creationflags=creationflags)

                    return r.stdout.strip()



                model = run_shell(['getprop', 'ro.product.model'])

                brand = run_shell(['getprop', 'ro.product.brand'])

                android_ver = run_shell(['getprop', 'ro.build.version.release'])

                sdk = run_shell(['getprop', 'ro.build.version.sdk'])

                resolution = run_shell(['wm', 'size'])



                info = (f"设备: {device_id}\n"

                        f"品牌: {brand}\n"

                        f"型号: {model}\n"

                        f"Android: {android_ver} (SDK {sdk})\n"

                        f"分辨率: {resolution}")

                self.root.after(0, lambda: self.log_message(info, 'info'))

            except Exception as e:

                self.root.after(0, lambda: self.log_message(f'获取设备信息失败: {e}', 'error'))



        threading.Thread(target=do_details, daemon=True).start()



    def install_keyboard(self):

        device_id = self.device_manager.get_selected_device()

        if not device_id:

            self.log_message('请先选择设备', 'warning')

            return



        apk_path = get_resource_path('tools/ADBKeyboard.apk')

        if not os.path.exists(apk_path):

            self.log_message(f'APK 文件不存在: {apk_path}', 'error')

            return



        self.log_message(f'正在安装 ADB 键盘到 {device_id}...', 'info')



        def do_install():

            try:

                creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

                result = subprocess.run(

                    ['adb', '-s', device_id, 'install', '-r', apk_path],

                    capture_output=True, text=True, timeout=30,

                    creationflags=creationflags

                )

                if result.returncode == 0 and 'Success' in result.stdout:

                    self.root.after(0, lambda: self.log_message('ADB 键盘安装成功', 'success'))

                else:

                    self.root.after(0, lambda: self.log_message(

                        f'安装失败: {result.stdout}{result.stderr}', 'error'))

            except Exception as e:

                self.root.after(0, lambda: self.log_message(f'安装异常: {e}', 'error'))



        threading.Thread(target=do_install, daemon=True).start()



    def remote_desktop(self):

        device_id = self.device_manager.get_selected_device()

        if not device_id:

            self.log_message('请先选择设备', 'warning')

            return



        self.log_message('正在启动远程桌面 (scrcpy)...', 'info')



        def do_scrcpy():

            try:

                creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

                # 优先使用 tools 目录下的 scrcpy

                tools_dir = get_resource_path('tools')

                scrcpy_exe = os.path.join(tools_dir, 'scrcpy.exe')

                scrcpy_server = os.path.join(tools_dir, 'scrcpy-server')



                # 构建环境变量，设置 SCRCPY_SERVER_PATH 和 ADB 路径

                env = os.environ.copy()

                if os.path.isfile(scrcpy_server):

                    env['SCRCPY_SERVER_PATH'] = scrcpy_server

                adb_exe = os.path.join(tools_dir, 'adb.exe')

                if os.path.isfile(adb_exe):

                    env['ADB'] = adb_exe



                # 决定 scrcpy 可执行文件路径

                if os.path.isfile(scrcpy_exe):

                    cmd = [scrcpy_exe]

                else:

                    # fallback 到系统 PATH 中的 scrcpy

                    cmd = ['scrcpy']



                cmd.extend(['-s', device_id])



                subprocess.Popen(cmd, creationflags=creationflags, env=env)

                self.root.after(0, lambda: self.log_message('scrcpy 已启动', 'success'))

            except FileNotFoundError:

                self.root.after(0, lambda: self.log_message(

                    '未找到 scrcpy！tools 目录下缺少 scrcpy.exe，或系统 PATH 中未安装 scrcpy', 'error'))

            except Exception as e:

                self.root.after(0, lambda: self.log_message(f'scrcpy 启动失败: {e}', 'error'))



        threading.Thread(target=do_scrcpy, daemon=True).start()



    def screenshot(self):

        device_id = self.device_manager.get_selected_device()

        if not device_id:

            self.log_message('请先选择设备', 'warning')

            return



        self.log_message('正在截取设备屏幕...', 'info')



        def do_screenshot():

            try:

                from phone_agent.device_factory import get_device_factory

                screenshot = get_device_factory().get_screenshot(device_id)



                import base64

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

                filename = f"screenshot_{timestamp}.png"

                with open(filename, 'wb') as f:

                    f.write(base64.b64decode(screenshot.base64_data))



                self.root.after(0, lambda: self.log_message(f'截图已保存: {filename}', 'success'))

            except Exception as e:

                self.root.after(0, lambda: self.log_message(f'截图失败: {e}', 'error'))



        threading.Thread(target=do_screenshot, daemon=True).start()



    def wake_device(self):

        device_id = self.device_manager.get_selected_device()

        if not device_id:

            self.log_message('请先选择设备', 'warning')

            return



        self.log_message('正在唤醒设备...', 'info')



        def do_wake():

            try:

                creationflags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

                subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'keyevent', '224'],

                             capture_output=True, timeout=5, creationflags=creationflags)

                time.sleep(0.5)

                subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'keyevent', '82'],

                             capture_output=True, timeout=5, creationflags=creationflags)

                time.sleep(0.5)



                lock_password = os.environ.get('PHONE_AGENT_LOCK_PASSWORD', '')

                if lock_password:

                    esc = lock_password.replace(' ', '%s')

                    subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'text', esc],

                                 capture_output=True, timeout=5, creationflags=creationflags)

                    time.sleep(0.3)

                    subprocess.run(['adb', '-s', device_id, 'shell', 'input', 'keyevent', '66'],

                                 capture_output=True, timeout=5, creationflags=creationflags)



                self.root.after(0, lambda: self.log_message('设备已唤醒', 'success'))

            except Exception as e:

                self.root.after(0, lambda: self.log_message(f'唤醒失败: {e}', 'error'))



        threading.Thread(target=do_wake, daemon=True).start()



    # ================================================================

    # 配置管理

    # ================================================================



    def save_config(self):

        self._sync_ui_to_config()

        self.config_manager.save_config()

        self.log_message('配置已保存', 'success')



    def load_config(self):

        self.config_manager.load_config_async()

        self.log_message('正在加载配置...', 'info')

        self.root.after(1500, self._sync_config_to_ui)



    def _sync_ui_to_config(self):

        try:

            self.config_manager.temperature.set(f"{self.temperature_var.get():.1f}")

        except Exception:

            pass



    def _sync_config_to_ui(self):

        try:

            temp = float(self.config_manager.temperature.get() or 0.0)

            self.temperature_var.set(temp)



            # 恢复平台选择

            platform = self.config_manager.platform.get()

            if platform:

                self.platform_var.set(platform)



            # 恢复操作勾选状态

            self.op_like_var.set(self.config_manager.operation_checkpoint.get())

            self.op_comment_var.set(self.config_manager.operation_comment.get())

            self.op_collect_var.set(self.config_manager.operation_collect.get())

            self.op_follow_var.set(self.config_manager.operation_follow.get())



            # 检查是否有保存的任务，如果有则恢复；否则根据勾选生成

            saved_task = self.config_manager.task.get()

            if saved_task and saved_task.strip() and saved_task != '输入你想要执行的任务':

                # 恢复保存的任务

                if self.task_view:

                    self.task_view.delete('1.0', tk.END)

                    self.task_view.insert('1.0', saved_task)

            else:

                # 根据当前勾选状态生成任务

                self._on_operation_change()



            self.log_message('配置已加载', 'success')

        except Exception as e:

            self.log_message(f'配置加载异常: {e}', 'error')



    # ================================================================

    # 设备选择回调

    # ================================================================



    def _on_device_type_change(self, event=None):

        self.device_manager.device_type.set(self.device_type_var.get())

        self.device_manager.on_device_type_change()

        self.log_message(f'设备类型切换为: {self.device_type_var.get()}', 'info')

        self.root.after(500, self._update_device_combo)



    def _on_device_selected(self, event=None):

        selected = self.device_list_var.get()

        if selected:

            self.device_manager.selected_device_id.set(selected)

            self.config_manager.selected_device_id.set(selected)

            device_id = selected.split(' ')[0]

            self.log_message(f'已选择设备: {device_id}', 'info')



    # ================================================================

    # 其他功能

    # ================================================================



    def ai_polish(self):

        task = self.task_view.get('1.0', tk.END).strip()

        if not task or task == "输入你想要执行的任务...":

            messagebox.showwarning("提示", "请先输入任务描述")

            return



        self.log_message('AI 正在润色任务描述...', 'info')



        def do_polish():

            try:

                from task_simplifier import TaskSimplifier, AIProvider

                simplifier = TaskSimplifier()

                result = simplifier.simplify_task(task, AIProvider.DEEPSEEK)

                if result.get('success') and result.get('simplified_task'):

                    simplified = result['simplified_task']

                    self.root.after(0, lambda: self.task_view.delete('1.0', tk.END))

                    self.root.after(0, lambda: self.task_view.insert('1.0', simplified))

                    self.root.after(0, lambda: self.task_var.set(simplified.strip()))

                    provider = result.get('provider', 'unknown')

                    self.root.after(0, lambda: self.log_message(

                        f'AI 润色完成 (via {provider})', 'success'))

                else:

                    error = result.get('error', '未知错误')

                    self.root.after(0, lambda: self.log_message(

                        f'AI 润色失败: {error}', 'error'))

            except Exception as e:

                self.root.after(0, lambda: self.log_message(f'AI 润色异常: {e}', 'error'))



        threading.Thread(target=do_polish, daemon=True).start()



    def show_history(self):

        records = self.task_history.get_all()

        if not records:

            self.log_message('暂无任务历史', 'info')

            return



        self.log_message('--- 任务历史 ---', 'info')

        for i, r in enumerate(records[:10]):

            ts = r.get('timestamp', '')

            platform = r.get('platform', '')

            task_preview = r.get('task', '')[:40]

            self.log_message(f'  {ts} | {platform} | {task_preview}...', 'info')



    def show_templates(self):

        templates = [

            ("小红书自动互动",

             "1. 打开小红书应用，等待首页加载完成。\n"

             "2. 进入发现页面，下拉刷新并等待新内容加载。\n"

             "3. 在帖子列表中随机选择一个未操作过的帖子，点击进入详情页。\n"

             "4. 阅读帖子内容，总结核心意思。\n"

             "5. 点击评论区入口，浏览现有评论。\n"

             "6. 点击底部评论输入框，撰写包含文字和至少1个表情的评论。\n"

             "7. 点击发送按钮，等待发送成功提示。\n"

             "8. 返回发现页面，重复步骤2-7，共完成20次操作。"),



            ("抖音自动刷视频",

             "1. 打开抖音APP，等待推荐页加载。\n"

             "2. 浏览当前视频内容5-10秒。\n"

             "3. 双击屏幕点赞（如适用）。\n"

             "4. 上滑切换到下一个视频。\n"

             "5. 重复步骤2-4，共浏览30个视频。"),



            ("微信朋友圈互动",

             "1. 打开微信，进入朋友圈页面。\n"

             "2. 浏览朋友圈动态，随机选择一条未操作过的动态。\n"

             "3. 点击点赞按钮。\n"

             "4. 继续向下浏览，重复点赞操作。\n"

             "5. 共完成15条动态的点赞。"),



            ("微博自动转发",

             "1. 打开微博APP，进入首页推荐页面。\n"

             "2. 浏览微博列表，选择一条感兴趣的微博。\n"

             "3. 点击转发按钮，添加转发评论。\n"

             "4. 确认转发。\n"

             "5. 返回首页，重复操作，共完成10次转发。"),

        ]



        dialog = ctk.CTkToplevel(self.root)

        dialog.title("任务模板")

        dialog.geometry("500x400")

        dialog.configure(fg_color=COLORS['bg_card'])

        dialog.transient(self.root)

        dialog.grab_set()



        dialog.update_idletasks()

        x = self.root.winfo_x() + (self.root.winfo_width() - 500) // 2

        y = self.root.winfo_y() + (self.root.winfo_height() - 400) // 2

        dialog.geometry(f"+{x}+{y}")



        ctk.CTkLabel(dialog, text="选择任务模板", font=FONTS['heading'],

                     text_color=COLORS['text_primary']).pack(pady=(16, 12))



        for name, content in templates:

            ctk.CTkButton(dialog, text=name, font=FONTS['body'],

                           fg_color=COLORS['bg_input'],

                           hover_color=COLORS['bg_card_hover'],

                           text_color=COLORS['text_secondary'],

                           border_color=COLORS['border_color'],

                           border_width=1,

                           corner_radius=SIZES['radius_sm'],

                           anchor='w', height=40,

                           command=lambda c=content, d=dialog: self._apply_template(c, d)

                           ).pack(padx=20, pady=4, fill='x')



    def _apply_template(self, content, dialog):

        self.task_view.delete('1.0', tk.END)

        self.task_view.insert('1.0', content)

        self.task_var.set(content.strip())

        dialog.destroy()

        self.log_message('已加载任务模板', 'success')



    def _set_status(self, text, color):

        """更新状态徽章"""

        self.status_label.configure(text=text, text_color=color)

        try:

            self.status_dot_canvas.delete('all')

            self.status_dot_canvas.create_oval(0, 0, 7, 7, fill=color, outline='')

        except Exception:

            pass



    # ================================================================

    # 退出

    # ================================================================



    def on_closing(self):

        try:

            self._sync_ui_to_config()

            self.config_manager.save_config_silent()

        except Exception:

            pass



        if self.is_running:

            if messagebox.askyesno("确认", "任务正在执行，确定要退出吗？"):

                self.stop_run()

                self.root.destroy()

        else:

            self.root.destroy()



    # ================================================================

    # 操作预设

    # ================================================================



    def _load_operation_presets(self):
        """加载操作预设配置"""
        try:
            # 使用 get_resource_path 获取配置文件路径
            from gui.core.config import get_resource_path
            preset_file = get_resource_path('config/operation_presets.json')
            if os.path.exists(preset_file):
                with open(preset_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载操作预设失败: {e}")
        return {}

    def _load_platform_operations(self):
        """加载平台操作配置"""
        try:
            from gui.core.config import get_resource_path
            config_file = get_resource_path('config/platform_operations.json')
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载平台操作配置失败: {e}")
        return {}



    def _update_operation_checkboxes(self, platform):

        """根据平台更新操作勾选框"""

        # 清除现有勾选框

        for widget in self.operation_checks_frame.winfo_children():

            widget.destroy()

        self.operation_checkboxes.clear()



        # 获取该平台的操作列表

        if platform in self.platform_operations:

            operations = self.platform_operations[platform].get('operations', [])

        else:

            operations = ['点赞', '评论', '收藏', '关注']



        # 确保当前选中的操作在可用操作列表中

        current_op = self.selected_operation.get()

        if current_op not in operations:

            self.selected_operation.set(operations[0] if operations else "点赞")



        # 创建单选按钮

        for op in operations:

            icon = self.op_icons.get(op, "•")



            rb = ctk.CTkRadioButton(self.operation_checks_frame, text=f"{icon} {op}",

                                     variable=self.selected_operation, value=op,

                                     font=FONTS['body'],

                                     fg_color=COLORS['accent_primary'],

                                     hover_color=COLORS['accent_primary_hover'],

                                     text_color=COLORS['text_secondary'],

                                     border_color=COLORS['border_color'],

                                     corner_radius=50,

                                     border_width_unchecked=2,

                                     border_width_checked=2,

                                     command=self._on_operation_change)

            rb.pack(side='left', padx=(0, 16))

            self.operation_checkboxes[op] = rb



    def _generate_task_from_selection(self):

        """根据平台和操作选择生成任务内容"""

        platform = self.platform_var.get()

        operation = self.selected_operation.get()



        if not operation:

            return ""



        # 获取预设内容

        if platform in self.operation_presets:

            preset = self.operation_presets[platform]

            if operation in preset:

                task_lines = [f"【{operation}操作】"]

                task_lines.extend(preset[operation])

                return "\n".join(task_lines)



        return ""



    def _on_operation_change(self):

        """操作勾选变更时更新任务内容"""

        task_content = self._generate_task_from_selection()

        if task_content:

            # 更新任务文本框

            self.task_view.delete('1.0', tk.END)

            self.task_view.insert('1.0', task_content)

            self.task_var.set(task_content)



    def _on_platform_change(self, event=None):

        """平台切换时更新操作勾选框和任务内容"""

        platform = self.platform_var.get()

        # 更新操作勾选框

        self._update_operation_checkboxes(platform)

        # 更新任务内容

        self._on_operation_change()

        self.log_message(f'平台切换为: {platform}', 'info')



    def _save_current_task(self):

        """保存当前任务和配置"""

        try:

            # 保存当前任务内容

            task = self.task_view.get('1.0', tk.END).strip()

            self.config_manager.task.set(task)



            # 保存平台和操作勾选状态

            self.config_manager.platform.set(self.platform_var.get())

            self.config_manager.operation_checkpoint.set(self.op_like_var.get())

            self.config_manager.operation_comment.set(self.op_comment_var.get())

            self.config_manager.operation_collect.set(self.op_collect_var.get())

            self.config_manager.operation_follow.set(self.op_follow_var.get())



            # 静默保存配置

            self.config_manager.save_config_silent()

        except Exception as e:

            print(f"保存任务配置失败: {e}")

