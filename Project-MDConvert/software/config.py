# -*- coding: utf-8 -*-
"""
MD转换神器 - 配置管理模块
"""

import os
from pathlib import Path
from typing import Set

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    """应用配置类"""
    
    # API 配置 - 优先从环境变量加载，否则使用默认值（向后兼容）
    API_KEY: str = os.getenv(
        "SILICONFLOW_API_KEY",
        "sk-duohvgsidlebysltfcbozhhdfmririmmxalakbzdqwikxaqhq"
    )
    MODEL: str = os.getenv(
        "SILICONFLOW_MODEL",
        "deepseek-ai/DeepSeek-OCR"
    )
    BASE_URL: str = os.getenv(
        "SILICONFLOW_BASE_URL",
        "https://api.siliconflow.cn/v1"
    )
    
    # 支持的文件扩展名
    SUPPORTED_EXTENSIONS: Set[str] = {
        ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
        ".pdf", ".html", ".htm", ".txt", ".csv", ".tsv",
        ".xml", ".json", ".md", ".rst", ".rtf",
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp",
    }
    
    # UI 常量
    WINDOW_WIDTH: int = 600
    WINDOW_HEIGHT: int = 850
    PATH_DISPLAY_LIMIT: int = 60
    MAX_LOGS: int = 100
    PROGRESS_BAR_HEIGHT: int = 12
    
    # 控件尺寸
    TITLE_FONT_SIZE: int = 10
    TEXT_FIELD_WIDTH: int = 400
    TEXT_FIELD_HEIGHT: int = 45
    BUTTON_SOURCE_WIDTH: int = 140
    BUTTON_TARGET_WIDTH: int = 140
    BUTTON_HEIGHT: int = 40
    CONVERT_BTN_WIDTH: int = 560
    CONVERT_BTN_HEIGHT: int = 45
    STAT_ITEM_WIDTH: int = 130
    STAT_FONT_SIZE: int = 14
    PROGRESS_BAR_WIDTH: int = 560
    LOG_LIST_HEIGHT: int = 320
    FAILURES_LIST_HEIGHT: int = 80
    STAT_CONTAINER_WIDTH: int = 560
    
    # ICO 图标尺寸
    ICON_SIZES: list = [16, 32, 48, 64, 128, 256]
    
    @classmethod
    def get_project_root(cls) -> Path:
        """获取项目根目录"""
        return Path(__file__).parent
    
    @classmethod
    def get_img_dir(cls) -> Path:
        """获取图片资源目录"""
        return cls.get_project_root() / "img"
