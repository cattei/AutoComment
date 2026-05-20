"""
UI样式定义 - 基于 CustomTkinter + ui.html设计
深色主题现代化UI - 严格对齐设计图
延迟初始化字体（CTkFont 需要先创建 root）
"""

import customtkinter as ctk

# ===== 颜色定义 (严格对齐 ui.html :root) =====
COLORS = {
    # 背景色
    'bg_primary': '#0f1117',
    'bg_secondary': '#1a1d27',
    'bg_card': '#1e2130',
    'bg_card_hover': '#252839',
    'bg_input': '#161923',
    'bg_console': '#0a0c12',

    # 边框色
    'border_color': '#2a2d3e',
    'border_focus': '#6366f1',

    # 文字色
    'text_primary': '#e4e6f0',
    'text_secondary': '#8b8fa7',
    'text_muted': '#5c6078',

    # 强调色
    'accent_primary': '#6366f1',
    'accent_primary_hover': '#7577f5',
    'accent_primary_glow': '#1a1d3a',
    'accent_green': '#22c55e',
    'accent_green_hover': '#16a34a',
    'accent_green_glow': '#0d2d1a',
    'accent_red': '#ef4444',
    'accent_red_hover': '#dc2626',
    'accent_amber': '#f59e0b',
    'accent_amber_glow': '#2d2510',
    'accent_cyan': '#06b6d4',
    'accent_cyan_glow': '#0d2d33',

    # 渐变色
    'gradient_start': '#6366f1',
    'gradient_end': '#a855f7',
}

# ===== CustomTkinter 主题配置 =====
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# ===== 字体定义 (延迟初始化) =====
FONTS = {}

# ===== 字体规格 (用于延迟创建 CTkFont) =====
_FONT_SPECS = {
    'title': ('Microsoft YaHei', 18, 'bold'),
    'subtitle': ('Microsoft YaHei', 11, 'normal'),
    'heading': ('Microsoft YaHei', 14, 'bold'),
    'body': ('Microsoft YaHei', 13, 'normal'),
    'small': ('Microsoft YaHei', 12, 'normal'),
    'tiny': ('Microsoft YaHei', 11, 'normal'),
    'console': ('Consolas', 12, 'normal'),
    'mono': ('Consolas', 11, 'normal'),
    'stat_value': ('Microsoft YaHei', 22, 'bold'),
    'logo': ('Microsoft YaHei', 18, 'bold'),
}

def _init_fonts():
    """延迟初始化字体（必须在 root 创建之后调用）"""
    if FONTS:  # 已初始化
        return
    for key, (family, size, weight) in _FONT_SPECS.items():
        FONTS[key] = ctk.CTkFont(family=family, size=size, weight=weight)

# ===== 尺寸定义 =====
SIZES = {
    'radius_sm': 6,
    'radius_md': 10,
    'radius_lg': 14,
    'radius_pill': 20,

    'padding_sm': 6,
    'padding_md': 12,
    'padding_lg': 18,

    'gap_sm': 8,
    'gap_md': 12,
    'gap_lg': 16,
}

# ===== 布局定义 =====
LAYOUT = {
    'header_height': 60,
    'toolbar_height': 50,
    'right_panel_width': 380,
    'main_padding': 16,
    'card_padding': 18,
}


def setup_styles(root):
    """设置样式 - 初始化字体和主题"""
    _init_fonts()
