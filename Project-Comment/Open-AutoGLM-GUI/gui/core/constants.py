"""
常量定义模块
"""

# 窗口配置
WINDOW_TITLE = "私域新势力"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750
WINDOW_MIN_WIDTH = 1100
WINDOW_MIN_HEIGHT = 650

# 默认配置
DEFAULT_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"
DEFAULT_MODEL = "autoglm-phone"
DEFAULT_API_KEY = "your-bigmodel-api-key"
DEFAULT_TASK = "输入你想要执行的任务，例如：打开美团搜索附近的火锅店"
DEFAULT_MAX_STEPS = "200"
DEFAULT_TEMPERATURE = "0.0"
DEFAULT_DEVICE_TYPE = "安卓"
DEFAULT_PLATFORM = "小红书"

# 配置文件
GUI_CONFIG_FILE = "config/gui_config.json"
TASK_HISTORY_FILE = "config/task_history.json"
AI_CONFIG_FILE = "config/ai_config.json"

# 设备类型映射
DEVICE_TYPE_MAP = {
    "安卓": "adb",
    "iOS": "ios",
    "鸿蒙": "hdc"
}

DEVICE_TYPE_REVERSE_MAP = {
    "adb": "安卓",
    "ios": "iOS",
    "hdc": "鸿蒙"
}

# 平台配置
PLATFORM_CONFIGS = {
    "小红书": {
        "buttons": {
            "发布": "bottom_center",
            "拍照": "center",
            "分享": "top_right"
        },
        "pages": {
            "首页": "发现页面，显示推荐内容",
            "个人中心": "我的页面，显示个人信息和作品"
        }
    },
    "微信朋友圈": {
        "buttons": {
            "发布": "top_right",
            "相机": "center",
            "评论": "bottom"
        },
        "pages": {
            "朋友圈": "显示好友发布的动态",
            "个人主页": "显示个人信息和发布的内容"
        }
    },
    "微信视频号": {
        "buttons": {
            "发布": "top_right",
            "点赞": "bottom_left",
            "评论": "bottom_center"
        },
        "pages": {
            "推荐": "显示推荐视频",
            "关注": "显示关注的创作者"
        }
    }
}

# ADB命令
ADB_WAKEUP = "224"  # KEYCODE_WAKEUP
ADB_MENU = "82"     # KEYCODE_MENU
ADB_POWER = "26"    # KEYCODE_POWER
ADB_ENTER = "66"    # KEYCODE_ENTER

# 超时设置
ADB_TIMEOUT = 5
DEVICE_SCAN_TIMEOUT = 10
CONNECTION_TIMEOUT = 30

# 输出缓冲
OUTPUT_BUFFER_SIZE = 1000
OUTPUT_FLUSH_INTERVAL = 0.1
