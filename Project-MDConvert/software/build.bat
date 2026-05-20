@echo off
chcp 65001 >nul
echo ========================================
echo MD转换神器 - PyInstaller 打包脚本
echo ========================================
echo.

REM 设置打包参数
set SCRIPT_NAME=app_flet.py
set OUTPUT_NAME=MD转换神器
set ICON_PATH=img\logo.ico
set OUTPUT_DIR=dist

echo [步骤 1] 清理旧的打包文件...
if exist build rmdir /s /q build
if exist %OUTPUT_DIR% rmdir /s /q %OUTPUT_DIR%
echo 完成！
echo.

echo [步骤 2] 使用 PyInstaller 打包...
echo.

REM 使用 PyInstaller 打包
pyinstaller --name "%OUTPUT_NAME%" ^
    --onefile ^
    --windowed ^
    --icon "%ICON_PATH%" ^
    --add-data "img;img" ^
    --hidden-import flet ^
    --hidden-import markitdown ^
    --hidden-import markitdown.convert ^
    --hidden-import magika ^
    --hidden-import openai ^
    --hidden-import tkinter ^
    --hidden-import tkinter.filedialog ^
    --hidden-import mammoth ^
    --hidden-import pdfplumber ^
    --hidden-import pdfminer ^
    --hidden-import pandas ^
    --collect-all markitdown ^
    --collect-all magika ^
    "%SCRIPT_NAME%"

if errorlevel 1 (
    echo.
    echo 打包失败！
    pause
    exit /b 1
)

echo.
echo [步骤 3] 打包完成！
echo.
echo 输出文件: %OUTPUT_DIR%\%OUTPUT_NAME%.exe
echo.
echo ========================================
echo 打包成功！
echo ========================================
echo.

pause
