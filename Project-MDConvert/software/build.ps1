# MD转换神器 - PyInstaller 打包脚本 (PowerShell 版本)
# 使用方式: .\build.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MD转换神器 - PyInstaller 打包脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 设置打包参数
$SCRIPT_NAME = "app_flet.py"
$OUTPUT_NAME = "MD转换神器"
$ICON_PATH = "img\logo.ico"
$OUTPUT_DIR = "dist"

Write-Host "[步骤 1] 清理旧的打包文件..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Path "build" -Recurse -Force
}
if (Test-Path $OUTPUT_DIR) {
    Remove-Item -Path $OUTPUT_DIR -Recurse -Force
}
Write-Host "完成！" -ForegroundColor Green
Write-Host ""

Write-Host "[步骤 2] 使用 PyInstaller 打包..." -ForegroundColor Yellow
Write-Host ""

# 使用 PyInstaller 打包
$args = @(
    "--name", $OUTPUT_NAME,
    "--onefile",
    "--windowed",
    "--icon", $ICON_PATH,
    "--add-data", "img;img",
    "--hidden-import", "flet",
    "--hidden-import", "markitdown",
    "--hidden-import", "markitdown.convert",
    "--hidden-import", "magika",
    "--hidden-import", "openai",
    "--hidden-import", "tkinter",
    "--hidden-import", "tkinter.filedialog",
    "--hidden-import", "mammoth",
    "--hidden-import", "pdfplumber",
    "--hidden-import", "pdfminer",
    "--hidden-import", "pandas",
    "--collect-all", "markitdown",
    "--collect-all", "magika",
    $SCRIPT_NAME
)

& pyinstaller @args

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "打包失败！" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Write-Host ""
Write-Host "[步骤 3] 打包完成！" -ForegroundColor Yellow
Write-Host ""
Write-Host "输出文件: $OUTPUT_DIR\$OUTPUT_NAME.exe" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "打包成功！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Read-Host "按回车键退出"
