# 评论神器 — AI 驱动的手机自动化操作平台

> **当前版本**: v2.1.0  
> **核心能力**: 通过视觉语言模型理解手机屏幕内容，自动执行点赞、评论、收藏、关注等社交平台互动操作

---

##  项目简介

评论神器 是一个 AI 驱动的手机自动化操作平台，基于智谱 AutoGLM-Phone 视觉语言模型，能够"看懂"手机屏幕并自动执行操作。支持 Android（ADB）、HarmonyOS（HDC）、iOS（XCTest）三大设备协议，覆盖小红书、微信、抖音等 50+ 中文 APP。

**典型场景**: 社交平台自动互动 — 打开小红书 → 浏览帖子 → 阅读评论 → AI 生成评论 → 发送 → 循环 N 次

## ✨ 核心特性

- 🧠 **AI 看屏操作**：基于智谱 AutoGLM-Phone 视觉语言模型，截屏→推理→执行全闭环
- 🎯 **7 大平台通吃**：小红书、微信朋友圈、微信视频号、抖音、B站、快手、微博
- 💬 **AI 智能评论**：9 大 AI 平台润色（DeepSeek/豆包/元宝/OpenAI/文心/通义…），不是机器刷屏
-  **三端通吃**：Android（ADB）+ 鸿蒙（HDC）+ iOS（XCTest）
- 🔄 **批量执行**：设置任务，循环 1-100 次自动执行，运行统计实时看
- 🎨 **深色主题 GUI**：CustomTkinter 现代深色界面，专业美观
- ⚡ **独立 EXE**：PyInstaller 打包，复制到任何 Windows 电脑即可使用

---

## 🏗️ 系统架构

```
┌─────────────────────┐         ┌──────────────────────────────┐
│   客户端 (EXE)       │  HTTPS  │   服务端 (FastAPI)            │
│                     │◄───────►│                              │
│  ┌───────────────┐  │         │  ┌────────────┐  ────────┐ │
│  │ 评论神器 GUI  │  │         │  │ License 验证│  │ AI 代理 │ │
│  │ CustomTkinter │  │         │  │ 设备指纹绑定│  │ 请求转发│ │
│  └───────┬───────┘  │         │  └────────────┘  └───┬────┘ │
│          │          │         │        │               │      │
│  ┌───────▼───────┐  │         │  ┌─────▼──────┐  ┌────▼────┐ │
│  │ PhoneAgent    │  │         │  │  SQLite DB │  │ 智谱AI  │ │
│  │ 截屏→推理→执行│  │         │  │  Key + 用量│  │ DeepSeek│ │
│  └───────────────┘  │         │  └────────────┘  └─────────┘ │
└─────────────────────┘         └──────────────────────────────┘
```

**BS 架构设计**:
- **服务端**: 只做 Key 验证 + 设备指纹绑定 + AI 请求转发 + 计费，不存储业务数据
- **客户端**: 保持完整 PhoneAgent 引擎，`base_url` 指向代理，`api_key` 改为激活 Key
- **安全**: 真实 AI API Key 只存在服务端，客户端永远拿不到

---

##  目录结构

```
Open-AutoGLM-GUI/
├── gui/                    # GUI 界面模块（CustomTkinter 深色主题）
│   ├── app.py              #   评论神器 v2.0 主界面
│   ├── core/config.py      #   ConfigManager 配置管理
│   ├── device/             #   DeviceManager 设备管理（ADB 扫描/连接/截图）
│   └── task/               #   TaskExecutor + TaskHistory
├── phone_agent/            # 核心自动化引擎
│   ├── agent.py            #   PhoneAgent 核心循环：截屏 → AI 推理 → 解析动作 → 执行
│   ├── model/client.py     #   OpenAI 兼容 API 流式调用 + MessageBuilder
│   ├── actions/handler.py  #   动作解析与执行（Launch/Tap/Type/Swipe/Back/Home 等）
│   ├── device_factory.py   #   设备工厂模式（全局单例）
│   ├── adb/                #   ADB 连接/截图/输入/设备控制
│   ├── hdc/                #   HDC（鸿蒙）对应实现
│   └── xctest/             #   iOS XCTest/WebDriverAgent 实现
├── server/                 # License 服务端
│   ├── main.py             #   FastAPI 入口（3 核心 API + 管理接口）
│   ├── config.py           #   服务端配置（环境变量注入）
│   ├── auth.py             #   License 激活 + 设备指纹验证
│   ├── proxy.py            #   AI 请求代理转发
│   ├── database.py         #   SQLite 数据库操作
│   ├── admin.py            #   管理接口路由
│   ├── keygen.py           #   Key 生成 CLI 工具
│   ├── Dockerfile          #   Docker 部署
│   └── requirements.txt    #   服务端依赖
├── client/                 # 客户端辅助模块
│   ├── device_fingerprint.py  # 设备指纹采集（SHA256(MAC+磁盘序列号)）
│   └── license.py          #   License 激活管理（请求/缓存/Header 注入）
├── config/                 # 配置文件目录
│   ── gui_config.json     #   GUI 运行配置
├── assets/                 # 图标资源
│   ├── icons/              #   app.ico / app.icns 应用图标
│   └── images/             #   comment-shenqi-logo.png / wechat.jpg 收款码
├── tools/                  # ADB/SCrcpy 等外部工具
├── build_exe.py            # PyInstaller 打包脚本
├── gui.py                  # GUI 入口
├── main.py                 # CLI 入口
├── task_simplifier.py      # 多平台 AI 任务精简器（9 平台）
└── requirements.txt        # 客户端依赖
```

---

## 🚀 快速开始

### 使用方法

1. 双击运行 `评论神器.exe`
2. 在左侧"自动化流程配置"中编写操作步骤
3. 在右侧"平台设置"中选择平台和参数（最大步数、执行次数、温度值）
4. 选择"操作类型"（点赞/评论/收藏/关注）
5. 在右侧"ADB 设备管理"中连接手机设备
6. 点击底部"运行"按钮，开始自动执行
7. 运行统计面板实时显示点赞/评论/收藏/关注次数

### 界面说明

| 区域 | 功能 |
|------|------|
| **自动化流程配置** | 编写操作步骤，支持步骤/命令/日志三种视图 |
| **平台设置** | 选择平台、配置最大步数/执行次数/温度值、选择操作类型 |
| **ADB 设备管理** | 刷新设备、连接设备、安装键盘、远程桌面、截图 |
| **运行统计** | 实时显示点赞次数/评论次数/收藏次数/关注次数 |
| **底部工具栏** | 唤醒设备、保存/加载配置、AI 润色评论、查看历史 |

### 环境要求

- Python 3.10+
- Android 设备（需开启 USB 调试）/ 鸿蒙设备 / iOS 设备
- ADB 已安装并加入 PATH（Android）/ HDC（鸿蒙）/ WebDriverAgent（iOS）

### 安装

```bash
# 克隆项目
git clone https://github.com/your-org/Open-AutoGLM-GUI.git
cd Open-AutoGLM-GUI

# 安装客户端依赖
pip install -r requirements.txt
```

### 运行

```bash
# 方式一：GUI 模式（推荐）
python gui.py

# 方式二：CLI 模式
python main.py
```

### 打包为 EXE

```bash
python build_exe.py
# 输出：dist/PhoneAgentGUI.exe
```

---

## 🖥️ 服务端部署

### 方式一：Docker 部署（推荐）

```bash
cd server
docker build -t autoflow-license-server .

docker run -d \
  -p 9000:9000 \
  -e AF_ADMIN_SECRET=your-admin-secret \
  -e AF_AUTOGLM_API_KEY=your-autoglm-key \
  -e AF_HMAC_KEY=your-hmac-key \
  -e AF_DEEPSEEK_API_KEY=your-deepseek-key \
  autoflow-license-server
```

### 方式二：手动部署

```bash
cd server
pip install -r requirements.txt

# 创建 .env 文件（参考 .env.example）
cp .env.example .env
# 编辑 .env 填入真实配置

# 启动
python main.py
```

---

##  设备支持

| 平台 | 协议 | 功能 |
|------|------|------|
| Android | ADB | 截图、点击、滑动、输入、安装输入法、SCrcpy 投屏 |
| HarmonyOS | HDC | 截图、点击、滑动、输入 |
| iOS | XCTest/WebDriverAgent | 截图、点击、滑动、输入 |

### 连接方式

- **USB 连接**（推荐，低延迟）
- **WiFi 连接**（ADB TCP/IP / HDC 无线）
- **无线配对**（Android 11+）

---

## 🔐 环境变量说明

### 服务端（server/.env）

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `AF_ADMIN_SECRET` | ✅ | - | 管理员密钥（Key 生成/解绑等） |
| `AF_AUTOGLM_API_KEY` | ✅ | - | 智谱 AutoGLM API Key |
| `AF_HMAC_KEY` | ✅ | - | 设备指纹 HMAC 签名密钥 |
| `AF_HOST` | ❌ | `0.0.0.0` | 监听地址 |
| `AF_PORT` | ❌ | `9000` | 监听端口 |
| `AF_RATE_LIMIT` | ❌ | `30` | 每分钟请求限制/Key |
| `AF_MAX_BODY_SIZE` |  | `10485760` | 请求体最大字节数（10MB） |
| `AF_DEEPSEEK_API_KEY` | ❌ | - | DeepSeek API Key（备用模型） |
| `AF_DEFAULT_PROVIDER` | ❌ | `autoglm-phone` | 默认 AI 提供商 |
| `AF_DATABASE_URL` | ❌ | `sqlite+aiosqlite:///./autoflow_license.db` | 数据库连接 |

---

## 🛠️ 开发指南

### 项目依赖

**客户端核心依赖**: `openai`, `Pillow`, `aiohttp`, `phone-agent`, `customtkinter>=5.2.0`, `httpx`

**服务端核心依赖**: `fastapi`, `uvicorn`, `aiosqlite`, `httpx`, `pydantic`

### AI 模型支持

| 提供商 | 模型 | 说明 |
|--------|------|------|
| 智谱 | AutoGLM-Phone | 默认，视觉理解+操作推理 |
| DeepSeek | deepseek-chat | 备用 |
| 豆包 | - | 可扩展 |
| 元宝 | - | 可扩展 |
| OpenAI | - | 可扩展 |

### 动作类型

PhoneAgent 支持以下动作（由 AI 推理输出，自动解析执行）：

| 动作 | 说明 |
|------|------|
| `Launch(app)` | 启动应用 |
| `Tap(x, y)` | 点击坐标 |
| `Type(text)` | 输入文字 |
| `Swipe(x1, y1, x2, y2)` | 滑动 |
| `Back()` | 返回 |
| `Home()` | 回到桌面 |
| `Finish(reason)` | 任务完成 |

### 已知限制

- PhoneAgent 无内置中断机制，停止只能等当前步骤完成
- iOS 连接需提前配置 WebDriverAgent 环境
- 鸿蒙 HDC 需安装 DevEco Studio 或 HDC 工具

---

## 💰 打赏支持

如果这个工具对你有帮助，欢迎打赏支持！

<div align="center">
  <img src="assets/images/wechat.jpg" alt="微信收款码" width="250" />
</div>

---

## 📝 许可证

MIT License

本项目仅限非商业用途。如需商用，请联系作者获取授权。

## 🤝 联系方式

如有问题或建议，请联系开发者：
- 邮箱：12777894@qq.com
- 微信号：cattei
