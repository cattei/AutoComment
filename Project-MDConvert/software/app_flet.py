# -*- coding: utf-8 -*-
"""
MD转换神器 - 修复版本
"""

import flet as ft
# 确保 flet_desktop 被正确导入
try:
    import flet_desktop
    import flet_desktop.version
except ImportError:
    pass
import threading
import asyncio
import sys
import os
import re
import hashlib
import zipfile
import shutil
import time
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from config import Config


def pick_folder() -> Optional[str]:
    """打开文件夹选择对话框"""
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory()
    root.destroy()
    return folder if folder else None


def _shorten_path(path: str, max_length: int = Config.PATH_DISPLAY_LIMIT) -> str:
    """缩短路径显示，超出部分用省略号代替"""
    if len(path) <= max_length:
        return path
    half = (max_length - 3) // 2
    return f"{path[:half]}...{path[-half:]}"


def _validate_directory(path: str) -> Tuple[bool, str]:
    """验证目录是否存在且有读写权限"""
    dir_path = Path(path)
    if not dir_path.exists():
        return False, "目录不存在"
    if not dir_path.is_dir():
        return False, "路径不是目录"
    try:
        test_file = dir_path / ".test_write_permission"
        test_file.touch()
        test_file.unlink()
    except Exception:
        return False, "目录没有读写权限"
    return True, ""


class MDConverterApp:
    """MD转换神器主应用类"""

    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.page.title = "MD转换神器·孙永乐"
        self.page.window.width = Config.WINDOW_WIDTH
        self.page.window.height = Config.WINDOW_HEIGHT
        self.page.window.resizable = False
        self.page.update()
        self.page.theme_mode = ft.ThemeMode.LIGHT

        self.source_dir: str = ""
        self.target_dir: str = ""
        self.is_converting: bool = False
        self.failures: List[Tuple[str, str]] = []
        self.stats: Dict[str, str] = {
            "dirs": "0",
            "total": "0",
            "done": "0",
            "pending": "0"
        }
        self.all_files: List[Path] = []
        self._need_update: bool = False
        self._refresh_running: bool = True

        self._build_ui()
        self._start_ui_refresh()

    def _build_ui(self) -> None:
        """构建用户界面"""
        self.page.controls.clear()
        self.page.padding = 0
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        content = ft.Column(
            width=Config.CONVERT_BTN_WIDTH,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
            scroll=ft.ScrollMode.AUTO
        )

        content.controls.append(
            ft.Text("选择源目录，目标目录会自动生成，文件多的话会有点久，耐心等待 | DeepSeek-OCR已内置 | 图片OCR已启用", 
                    size=Config.TITLE_FONT_SIZE, weight=ft.FontWeight.BOLD, color="#667eea")
        )

        field_width = Config.CONVERT_BTN_WIDTH - Config.BUTTON_SOURCE_WIDTH - 10
        self.source_input = ft.TextField(
            hint_text="选择源目录...", width=field_width, read_only=True, height=Config.TEXT_FIELD_HEIGHT, text_vertical_align=ft.VerticalAlignment.CENTER        )
        source_row = ft.Row([
            self.source_input,
            ft.Button("📂 源目录", on_click=self._select_source, width=Config.BUTTON_SOURCE_WIDTH, height=Config.BUTTON_HEIGHT)
        ], width=Config.CONVERT_BTN_WIDTH)
        content.controls.append(source_row)

        self.target_input = ft.TextField(
            hint_text="选择目标目录...", width=field_width, read_only=True, height=Config.TEXT_FIELD_HEIGHT, text_vertical_align=ft.VerticalAlignment.CENTER        )
        target_row = ft.Row([
            self.target_input,
            ft.Button("📁 目标目录", on_click=self._select_target, width=Config.BUTTON_TARGET_WIDTH, height=Config.BUTTON_HEIGHT)
        ], width=Config.CONVERT_BTN_WIDTH)
        content.controls.append(target_row)

        self.convert_btn = ft.Button(
            "🚀 开始转换", on_click=self._start_convert, width=Config.CONVERT_BTN_WIDTH, height=Config.CONVERT_BTN_HEIGHT
        )
        content.controls.append(self.convert_btn)

        self.stat_dirs = ft.Text("📂 目录: 0", size=Config.STAT_FONT_SIZE, weight=ft.FontWeight.BOLD)
        self.stat_total = ft.Text("📄 文件: 0", size=Config.STAT_FONT_SIZE, weight=ft.FontWeight.BOLD)
        self.stat_done = ft.Text("✅ 已转换: 0", size=Config.STAT_FONT_SIZE, weight=ft.FontWeight.BOLD, color="#22c55e")
        self.stat_pending = ft.Text("⏳ 待转换: 0", size=Config.STAT_FONT_SIZE, weight=ft.FontWeight.BOLD, color="#f59e0b")

        content.controls.append(ft.Container(
            content=ft.Row(
                [
                    ft.Container(self.stat_dirs, width=Config.STAT_ITEM_WIDTH),
                    ft.Container(self.stat_total, width=Config.STAT_ITEM_WIDTH),
                    ft.Container(self.stat_done, width=Config.STAT_ITEM_WIDTH),
                    ft.Container(self.stat_pending, width=Config.STAT_ITEM_WIDTH),
                ],
                alignment=ft.MainAxisAlignment.CENTER, spacing=10
            ),
            bgcolor="#f3f4f6",
            padding=12,
            border_radius=10,
            margin=ft.Margin(0, 10, 0, 10),
            width=Config.STAT_CONTAINER_WIDTH
        ))



        self.progress_status = ft.Text("就绪", size=14, color="#333")
        self.progress_bar = ft.ProgressBar(
            width=Config.CONVERT_BTN_WIDTH, value=0, height=Config.PROGRESS_BAR_HEIGHT
        )
        content.controls.append(self.progress_status)
        content.controls.append(self.progress_bar)

        self.log_list = ft.ListView(height=Config.LOG_LIST_HEIGHT, spacing=3, reverse=True)
        content.controls.append(
            ft.Container(
                content=self.log_list,
                padding=8,
                border_radius=8,
                border=ft.Border(left=ft.BorderSide(3, "#667eea")),
                width=Config.CONVERT_BTN_WIDTH
            )
        )

        self.failures_list = ft.ListView(height=Config.FAILURES_LIST_HEIGHT, spacing=2)
        self.failures_section = ft.Column(
            [ft.Text("❌ 转换失败", size=14, weight=ft.FontWeight.BOLD, color="red"),
             self.failures_list]
        )
        self.failures_section.visible = False
        content.controls.append(self.failures_section)

        wechat_src = self._get_asset_path("img/wechat.jpg")
        wechat_qr = ft.Image(src=wechat_src, width=280, height=280, fit=ft.BoxFit.CONTAIN)
        self._qr_popup = ft.Container(
            content=wechat_qr,
            visible=False,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=10,
            border=ft.Border.all(1, "#ddd"),
            margin=ft.Margin(bottom=5),
        )
        def _on_hover(e):
            enter = str(e.data).lower() in ("true", "1")
            self._qr_popup.visible = enter
            self._request_update()
        def _on_click(e):
            import webbrowser
            webbrowser.open("https://github.com/cattei/ConvertoMD")
        tip_column = ft.Column(
            [
                self._qr_popup,
                ft.Text(
                    "请我喝一杯吧",
                    size=13,
                    color="#667eea",
                    weight=ft.FontWeight.BOLD,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
        )
        tip_container = ft.Container(
            content=tip_column,
            padding=ft.Padding(8, 4, 8, 4),
            on_hover=_on_hover,
            on_click=_on_click,
        )
        content.controls.append(tip_container)

        self.page.add(content)
        self._add_log("欢迎使用MD转换神器", "gray")

        self.current_dialog: Optional[ft.AlertDialog] = None

    def _request_update(self) -> None:
        self._need_update = True

    def _get_asset_path(self, relative_path: str) -> str:
        """获取资源文件路径，兼容打包和开发环境"""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = str(Path(__file__).parent)
        return str(Path(base_path) / relative_path)

    def _start_ui_refresh(self) -> None:
        async def _periodic_refresh():
            while self._refresh_running:
                await asyncio.sleep(0.5)
                if self._need_update:
                    self._need_update = False
                    self.page.update()
        self.page.run_task(_periodic_refresh)

    def _add_log(self, text: str, color: str = "black") -> None:
        """添加日志（线程安全）"""
        self.log_list.controls.insert(0, ft.Text(text, size=13, color=color))
        if len(self.log_list.controls) > Config.MAX_LOGS:
            self.log_list.controls.pop()
        self._request_update()

    def _update_all_stats(self) -> None:
        """更新所有统计信息（线程安全）"""
        self.stat_dirs.value = f"📂 目录: {self.stats['dirs']}"
        self.stat_total.value = f"📄 文件: {self.stats['total']}"
        self.stat_done.value = f"✅ 已转换: {self.stats['done']}"
        self.stat_pending.value = f"⏳ 待转换: {self.stats['pending']}"
        self._request_update()

    def _update_progress(self, value: float, status_text: str) -> None:
        """更新进度条和状态（线程安全）"""
        self.progress_bar.value = value
        self.progress_status.value = status_text
        self._request_update()

    def _select_source(self, e) -> None:
        """选择源目录"""
        folder = pick_folder()
        if not folder:
            return

        # 验证目录
        is_valid, error_msg = _validate_directory(folder)
        if not is_valid:
            self._show_error(f"源目录无效: {error_msg}")
            return

        self.source_dir = folder
        self.source_input.value = _shorten_path(folder)

        if not self.target_dir:
            self.target_dir = f"{folder}_md"
            self.target_input.value = _shorten_path(self.target_dir)

        self._update_stats()
        self.page.update()

    def _select_target(self, e) -> None:
        """选择目标目录"""
        folder = pick_folder()
        if not folder:
            return

        # 验证目录
        is_valid, error_msg = _validate_directory(folder)
        if not is_valid:
            self._show_error(f"目标目录无效: {error_msg}")
            return

        self.target_dir = folder
        self.target_input.value = _shorten_path(folder)
        self.page.update()

    def _update_stats(self) -> None:
        """更新文件统计"""
        if not self.source_dir:
            return

        files, dir_count = self._find_files(Path(self.source_dir))
        self.all_files = files

        self.stats["dirs"] = str(dir_count)
        self.stats["total"] = str(len(files))
        self.stats["done"] = "0"
        self.stats["pending"] = str(len(files))
        self._update_all_stats()

        if len(files) > 0:
            self._add_log(f"已扫描到 {len(files)} 个文件", "gray")

    def _show_error(self, msg: str) -> None:
        """显示错误对话框"""
        def close_dialog(e) -> None:
            if self.page.dialog:
                self.page.dialog.open = False
                self.page.update()

        self.current_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("提示", size=18),
            content=ft.Text(msg, size=14),
            actions=[ft.Button("确定", on_click=close_dialog)],
        )
        self.page.dialog = self.current_dialog
        self.current_dialog.open = True
        self.page.update()

    def _show_complete(self, msg: str) -> None:
        """显示完成对话框"""
        def close_dialog(e) -> None:
            if self.page.dialog:
                self.page.dialog.open = False
                self.page.update()

        self.current_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("转换完成", size=18),
            content=ft.Text(msg, size=14),
            actions=[ft.Button("确定", on_click=close_dialog)],
        )
        self.page.dialog = self.current_dialog
        self.current_dialog.open = True
        self.page.update()

    def _start_convert(self, e) -> None:
        """开始转换"""
        if self.is_converting:
            return
        if not self.source_dir:
            self._show_error("请选择源目录")
            return
        if not self.target_dir:
            self._show_error("请选择目标目录")
            return

        self.is_converting = True
        self.convert_btn.text = "⏳ 转换中..."
        self.convert_btn.disabled = True
        self.failures = []
        self.failures_section.visible = False
        self.failures_list.controls.clear()
        self.log_list.controls.clear()
        self.progress_bar.value = 0
        self.progress_status.value = "准备转换..."
        self._request_update()

        self.page.run_thread(self._convert_thread)

    def _convert_thread(self) -> None:
        """转换线程"""
        try:
            self._add_log("开始初始化转换器...", "#3b82f6")
            self._update_progress(0, "初始化转换器...")

            if not self.all_files:
                self._add_log("扫描文件...", "#3b82f6")
                self._update_progress(0, "扫描文件...")
                files, dir_count = self._find_files(Path(self.source_dir))
                self.all_files = files
            else:
                files = self.all_files
                dir_count = int(self.stats["dirs"])

            total = len(files)

            self.stats["dirs"] = str(dir_count)
            self.stats["total"] = str(total)
            self.stats["pending"] = str(total)
            self._update_all_stats()

            if total == 0:
                self._add_log("未找到可转换的文件", "#f59e0b")
                self._conversion_complete(0, 0, 0)
                return

            self._add_log(f"共 {total} 个文件待处理", "#3b82f6")
            self._update_progress(0, f"准备处理 {total} 个文件...")

            success_count = 0
            fail_count = 0
            skip_count = 0

            self._add_log("创建转换器实例...", "#3b82f6")
            self._update_progress(0, "创建转换器...")

            md = self._create_markitdown()
            self._add_log("转换器初始化完成", "#22c55e")
            self._update_progress(0, "开始转换...")

            for i, src_file in enumerate(files, 1):
                rel_path = src_file.relative_to(self.source_dir)

                if src_file.suffix.lower() == ".md":
                    out_path = Path(self.target_dir) / rel_path
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, out_path)
                    skip_count += 1
                    self.stats["done"] = str(success_count + skip_count)
                    self.stats["pending"] = str(total - i)
                    self._update_all_stats()
                    self._add_log(f"⏭️ 跳过: {rel_path.name}", "#f59e0b")
                else:
                    try:
                        self._add_log(f"🔄 转换: {rel_path.name}", "#3b82f6")
                        self._update_progress(i / total, f"转换: {rel_path.name}...")

                        self._convert_file(src_file, Path(self.target_dir) / rel_path.with_suffix(".md"), md)
                        success_count += 1
                        self.stats["done"] = str(success_count + skip_count)
                        self.stats["pending"] = str(total - i)
                        self._update_all_stats()
                        self._update_progress(i / total, f"转换完成: {rel_path.name}")
                        self._add_log(f"✅ 成功: {rel_path.name}", "#22c55e")
                    except Exception as ex:
                        fail_count += 1
                        self.failures.append((str(rel_path), str(ex)))
                        self._copy_failed(src_file, Path(self.target_dir) / rel_path)
                        self.stats["done"] = str(success_count + skip_count)
                        self.stats["pending"] = str(total - i)
                        self._update_all_stats()
                        self._add_log(f"❌ 失败: {rel_path.name} - {str(ex)}", "#ef4444")

                pct = int((i / total) * 100)
                self._update_progress(i / total, f"转换中 {i}/{total} ({pct}%)")

            self._conversion_complete(success_count, fail_count, skip_count)

        except Exception as ex:
            self._add_log(f"❌ 转换失败: {ex}", "#ef4444")
            import traceback
            traceback.print_exc()
            self.is_converting = False
            self._reset_btn()

    def _conversion_complete(self, success: int, fail: int, skip: int) -> None:
        """转换完成处理"""
        self._add_log(f"🏁 完成! 成功: {success} 失败: {fail} 跳过: {skip}", "#8b5cf6")
        self._update_progress(1, "转换完成")

        if fail > 0 and self.failures:
            self.failures_section.visible = True
            for path, reason in self.failures:
                self.failures_list.controls.append(ft.Text(f"{path}", size=12, color="red"))
            self._request_update()

        msg = f"转换完成!\n成功: {success} 失败: {fail} 跳过: {skip}"

        self._show_complete(msg)
        self.is_converting = False
        self._reset_btn()

    def _reset_btn(self) -> None:
        """重置转换按钮"""
        self.convert_btn.text = "🚀 开始转换"
        self.convert_btn.disabled = False
        self._request_update()

    def _find_files(self, source_dir: Path) -> Tuple[List[Path], int]:
        """查找所有支持的文件"""
        files = []
        dir_count = 0
        for root, dirs, filenames in os.walk(source_dir):
            dir_count += 1
            for filename in filenames:
                ext = os.path.splitext(filename)[1].lower()
                if ext in Config.SUPPORTED_EXTENSIONS:
                    files.append(Path(root) / filename)
        return sorted(files), dir_count

    def _convert_file(self, src_file: Path, out_path: Path, md) -> None:
        """转换单个文件"""
        out_path.parent.mkdir(parents=True, exist_ok=True)
        images_dir = out_path.parent / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        extracted_images = {}
        if src_file.suffix.lower() == ".docx":
            extracted_images = self._extract_docx_images(src_file, images_dir)

        result = md.convert(str(src_file), keep_data_uris=True)
        markdown_text = result.text_content

        if extracted_images:
            markdown_text = self._process_markdown_images(markdown_text, extracted_images)

        markdown_text = self._embed_ocr_as_comments(markdown_text)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)

    def _extract_docx_images(self, docx_path: Path, images_dir: Path) -> Dict[str, str]:
        """从DOCX文件中提取图片"""
        extracted = {}
        if not zipfile.is_zipfile(docx_path):
            return extracted

        try:
            with zipfile.ZipFile(docx_path, "r") as zf:
                for media_path in zf.namelist():
                    if not media_path.startswith("word/media/"):
                        continue
                    try:
                        data = zf.read(media_path)
                        if len(data) == 0:
                            continue

                        content_hash = hashlib.md5(data).hexdigest()[:8]
                        ext = os.path.splitext(media_path)[1].lower() or ".png"
                        safe_name = f"img_{content_hash}{ext}"

                        with open(images_dir / safe_name, "wb") as img_f:
                            img_f.write(data)

                        extracted[os.path.basename(media_path)] = safe_name
                    except (IOError, OSError, zipfile.BadZipFile):
                        continue
        except (zipfile.BadZipFile, IOError, OSError):
            pass

        return extracted

    def _process_markdown_images(self, text: str, images: Dict[str, str]) -> str:
        """处理Markdown中的图片引用"""
        img_pattern = re.compile(r"(!\[[^\]]*\]\()([^)]+)(\))")

        def replace(match):
            prefix = match.group(1)
            src = match.group(2)
            suffix = match.group(3)

            if not src.startswith("data:"):
                return match.group(0)

            for orig_name, safe_name in sorted(images.items(), key=lambda x: -len(x[0])):
                return f"{prefix}images/{safe_name}{suffix}"

            return match.group(0)

        return img_pattern.sub(replace, text)

    def _embed_ocr_as_comments(self, text: str) -> str:
        """将图片alt文字转为HTML注释，预览时隐藏，AI可读取"""
        img_pattern = re.compile(r"(!\[([^\]]*)\]\()([^)]+)(\))")

        def replace(match):
            full_match = match.group(0)
            alt_text = match.group(2).strip()
            if alt_text:
                cleaned = re.sub(r'\s+', ' ', alt_text).strip()
                if len(cleaned) > 2:
                    return f"{full_match}\n<!-- OCR: {cleaned} -->"
            return full_match

        return img_pattern.sub(replace, text)

    def _create_markitdown(self):
        """创建MarkItDown转换器实例"""
        from markitdown import MarkItDown
        from openai import OpenAI

        client = OpenAI(api_key=Config.API_KEY, base_url=Config.BASE_URL)
        return MarkItDown(llm_client=client, llm_model=Config.MODEL, llm_temperature=0.0)

    def _copy_failed(self, src: Path, dst: Path) -> None:
        """复制失败的文件"""
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(src, dst)
        except (IOError, OSError):
            pass


def main(page: ft.Page) -> None:
    """应用入口"""
    page.theme = ft.Theme(color_scheme_seed="#667eea", font_family="Microsoft YaHei")
    MDConverterApp(page)


if __name__ == "__main__":
    # 避免 flet 的自动安装检查
    import os
    os.environ['FLET_DISABLE_UPDATE_CHECK'] = '1'
    os.environ['FLET_NO_ANALYTICS'] = '1'
    ft.run(main, assets_dir=str(Config.get_img_dir()))
