# MD转换神器

基于微软的 [markitdown](https://github.com/microsoft/markitdown)，使用 **Python + Flet** 开发的桌面应用程序，可将各种文档格式批量转换为 Markdown 格式，支持图片提取与 DeepSeek-OCR 文字识别。

## ✨ 核心特性

- 📄 **多格式支持**：DOCX, DOC, XLSX, XLS, PPTX, PPT, PDF, HTML, TXT, CSV, XML, JSON, MD, RST, RTF 等
- 🖼️ **图片提取**：自动从 DOCX 文件中提取图片
- 🤖 **DeepSeek-OCR**：内置 DeepSeek-OCR 模型，自动识别图片中的文字
- 📁 **目录保持**：转换后自动保持原有目录结构
- ⚡ **批量转换**：支持批量处理大量文件
- 🎨 **独立运行**：单个 exe 文件，复制到任何 Windows 电脑即可使用
- 🔒 **安全配置**：支持环境变量配置 API Key

## 🚀 快速开始

### 使用方法

1. 双击运行 `MD转换神器.exe`
2. 点击「选择目录」按钮，选择要转换的源文档目录
3. 选择或创建目标目录（Markdown 输出目录）
4. 点击「开始转换」按钮
5. 等待转换完成，查看统计信息

### 界面说明

- **统计面板**：显示目录数、总文件数、已转换数、待转换数
- **进度条**：实时显示转换进度
- **日志区域**：显示详细转换日志
- **失败列表**：转换失败的文件会显示在此处

### 转换结果

- ✅ **成功转换**：生成 Markdown 文件
- ⏭️ **跳过（MD文件）**：直接复制到目标目录
- ❌ **转换失败**：自动复制原文件到目标目录
- 📝 **完成提示**：弹窗显示统计信息

## 🏗️ 技术架构

```
┌─────────────────────────────────────┐
│      MD转换神器.exe (PyInstaller)   │
│  ┌─────────────────────────────────┐ │
│  │   Python 3.11 完整环境           │ │
│  ├─────────────────────────────────┤ │
│  │   Flet UI 界面                  │ │
│  ├─────────────────────────────────┤ │
│  │   markitdown 文档转换            │ │
│  ├─────────────────────────────────┤ │
│  │   DeepSeek-OCR 文字识别          │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

### 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 桌面框架 | Flet | Flutter + Python |
| GUI | Flet 原生控件 | Material Design |
| 文档转换 | Python + markitdown | 核心转换逻辑 |
| OCR | DeepSeek-OCR (SiliconFlow API) | 图片文字识别 |
| 打包 | PyInstaller | 独立 exe |

## 📁 项目结构

```
software/
├── app_flet.py          # 主程序（Flet 应用）
├── config.py            # 配置管理模块
├── .env.example         # 环境变量模板
├── .gitignore           # Git 忽略文件配置
├── build.bat            # PyInstaller 打包脚本
├── convert_icon.py      # 图标转换工具
├── img/                 # 界面图片资源
│   ├── logo.ico
│   ├── logo.jpg
│   └── wechat.jpg
├── docs/                # 文档资源
│   ├── logo.jpg
│   └── 微信收款码.jpg
├── test/                # 测试文件目录
│   ├── test_units.py    # 单元测试用例
│   ├── code_review.py   # 代码审查测试
│   ├── verify_fixes.py  # 修复验证脚本
│   └── ...              # 其他测试文件
├── .trae/               # Trae 项目文档
│   └── documents/
│       └── md_converter_improvement_plan.md
└── README.md            # 项目说明文档
```

## 🔧 开发说明

### 环境要求

- Python 3.11+
- Flet
- markitdown
- openai
- PyInstaller (用于打包)

### 开发调试

```bash
# 1. 安装依赖
pip install flet markitdown openai python-dotenv

# 2. 配置环境变量（可选）
# 复制 .env.example 为 .env 并填入你的 API Key

# 3. 运行开发模式
python app_flet.py

# 4. 运行测试
cd test
python verify_fixes.py
python test_units.py

# 5. 打包应用（使用 build.bat）
build.bat
```

### API Key 配置

方式1：使用环境变量（推荐）
```bash
# 在 .env 文件中配置
SILICONFLOW_API_KEY=your_api_key_here
SILICONFLOW_MODEL=deepseek-ai/DeepSeek-OCR
SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
```

方式2：直接修改 config.py（不推荐用于生产环境）

## 🔒 安全说明

### API Key 管理

本应用使用 SiliconFlow API Key 用于 DeepSeek-OCR 功能：

- API Key 配置在 [config.py](config.py)
- 支持通过环境变量 `.env` 文件覆盖配置
- 为了方便使用，API Key 已预置在代码中，仅供个人/内部使用
- 仅用于图片 OCR 识别，文档内的图片也能转换
- API 调用受 SiliconFlow 账户限制

**注意事项：**
- 建议使用环境变量配置 API Key
- `.env` 文件已添加到 `.gitignore`，不会被提交到 Git
- 如需商业部署，请联系开发者获取正式授权

### 文件安全

- 转换过程在本地执行，不上传文件到服务器
- 仅图片数据会发送到 SiliconFlow API 进行 OCR 识别
- 临时文件在转换完成后自动清理

## ⚠️ 限制与注意事项

1. **API 限制**：DeepSeek-OCR 使用 SiliconFlow API，有调用频率和额度限制
2. **文件大小**：大文件转换可能需要较长时间
3. **图片格式**：EMF/WMF 格式图片不支持 OCR 识别
4. **Python 环境**：打包后的 exe 不需要安装 Python
5. **线程安全**：UI 更新已使用 `page.run_task()` 保证线程安全

## 📝 更新日志

### v2.0 (2026-05-15)
- 🔒 新增 config.py 统一配置管理
- 🔒 支持环境变量配置 API Key
- 🐛 修复线程安全问题，使用 page.run_task()
- 🐛 改进异常处理，使用具体异常类型
- ✨ 新增目录验证功能
- ✨ 新增路径自动缩短显示
- 📦 代码重构，提取公共函数
- 🧪 完善单元测试用例
- 📁 整理项目结构，test 目录规范化

### v1.0
- 初始版本发布
- 基础文档转换功能
- DOCX 图片提取
- DeepSeek-OCR 集成

## 💰 打赏支持

如果这个工具对你有帮助，欢迎打赏支持！

<div align="center">
  <img src="docs/微信收款码.jpg" alt="微信收款码" width="250" />
</div>

## 📝 许可证

MIT License

## 🤝 联系方式

如有问题或建议，请联系开发者：
- 邮箱：12777894@qq.com
- 微信号：cattei