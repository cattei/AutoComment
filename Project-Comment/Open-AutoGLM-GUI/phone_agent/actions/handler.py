"""Action handler for processing AI model outputs."""

import ast
import subprocess
import time
from dataclasses import dataclass
from typing import Any, Callable

from phone_agent.config.timing import TIMING_CONFIG
from phone_agent.device_factory import get_device_factory


@dataclass
class ActionResult:
    """Result of an action execution."""

    success: bool
    should_finish: bool
    message: str | None = None
    requires_confirmation: bool = False


class ActionHandler:
    """
    Handles execution of actions from AI model output.

    Args:
        device_id: Optional ADB device ID for multi-device setups.
        confirmation_callback: Optional callback for sensitive action confirmation.
            Should return True to proceed, False to cancel.
        takeover_callback: Optional callback for takeover requests (login, captcha).
    """

    # HarmonyOS HDC 按键码映射表：Android keycode -> HDC keycode
    HDC_KEYCODE_MAP = {
        "KEYCODE_ENTER": "2054",
        "66": "2054",
    }

    def __init__(
        self,
        device_id: str | None = None,
        confirmation_callback: Callable[[str], bool] | None = None,
        takeover_callback: Callable[[str], None] | None = None,
    ):
        self.device_id = device_id
        self.confirmation_callback = confirmation_callback or self._default_confirmation
        self.takeover_callback = takeover_callback or self._default_takeover

    def execute(
        self, action: dict[str, Any], screen_width: int, screen_height: int
    ) -> ActionResult:
        """
        Execute an action from the AI model.

        Args:
            action: The action dictionary from the model.
            screen_width: Current screen width in pixels.
            screen_height: Current screen height in pixels.

        Returns:
            ActionResult indicating success and whether to finish.
        """
        action_type = action.get("_metadata")

        if action_type == "finish":
            return ActionResult(
                success=True, should_finish=True, message=action.get("message")
            )

        if action_type != "do":
            return ActionResult(
                success=False,
                should_finish=True,
                message=f"Unknown action type: {action_type}",
            )

        action_name = action.get("action")
        handler_method = self._get_handler(action_name)

        if handler_method is None:
            return ActionResult(
                success=False,
                should_finish=False,
                message=f"Unknown action: {action_name}",
            )

        try:
            return handler_method(action, screen_width, screen_height)
        except Exception as e:
            return ActionResult(
                success=False, should_finish=False, message=f"Action failed: {e}"
            )

    def _get_handler(self, action_name: str) -> Callable | None:
        """Get the handler method for an action."""
        handlers = {
            "Launch": self._handle_launch,
            "Tap": self._handle_tap,
            "Type": self._handle_type,
            "Type_Name": self._handle_type,
            "Swipe": self._handle_swipe,
            "Back": self._handle_back,
            "Home": self._handle_home,
            "Double Tap": self._handle_double_tap,
            "Long Press": self._handle_long_press,
            "Wait": self._handle_wait,
            "Take_over": self._handle_takeover,
            "Note": self._handle_note,
            "Call_API": self._handle_call_api,
            "Interact": self._handle_interact,
        }
        return handlers.get(action_name)

    def _convert_relative_to_absolute(
        self, element: list[int], screen_width: int, screen_height: int
    ) -> tuple[int, int]:
        """Convert relative coordinates (0-1000) to absolute pixels."""
        x = int(element[0] / 1000 * screen_width)
        y = int(element[1] / 1000 * screen_height)
        return x, y

    def _handle_launch(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle app launch action."""
        app_name = action.get("app")
        if not app_name:
            return ActionResult(False, False, "No app name specified")

        device_factory = get_device_factory()
        success = device_factory.launch_app(app_name, self.device_id)
        if success:
            return ActionResult(True, False)
        return ActionResult(False, False, f"App not found: {app_name}")

    def _handle_tap(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle tap action."""
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_relative_to_absolute(element, width, height)

        # Check for sensitive operation
        if "message" in action:
            if not self.confirmation_callback(action["message"]):
                return ActionResult(
                    success=False,
                    should_finish=True,
                    message="User cancelled sensitive operation",
                )

        device_factory = get_device_factory()
        device_factory.tap(x, y, self.device_id)
        return ActionResult(True, False)

    def _handle_type(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle text input action."""
        text = action.get("text", "")

        device_factory = get_device_factory()

        # Switch to ADB keyboard
        original_ime = device_factory.detect_and_set_adb_keyboard(self.device_id)
        time.sleep(TIMING_CONFIG.action.keyboard_switch_delay)

        # Clear existing text and type new text
        device_factory.clear_text(self.device_id)
        time.sleep(TIMING_CONFIG.action.text_clear_delay)

        # Handle multiline text by splitting on newlines
        device_factory.type_text(text, self.device_id)
        time.sleep(TIMING_CONFIG.action.text_input_delay)

        # Restore original keyboard
        device_factory.restore_keyboard(original_ime, self.device_id)
        time.sleep(TIMING_CONFIG.action.keyboard_restore_delay)

        return ActionResult(True, False)

    def _handle_swipe(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle swipe action."""
        start = action.get("start")
        end = action.get("end")

        if not start or not end:
            return ActionResult(False, False, "Missing swipe coordinates")

        start_x, start_y = self._convert_relative_to_absolute(start, width, height)
        end_x, end_y = self._convert_relative_to_absolute(end, width, height)

        device_factory = get_device_factory()
        device_factory.swipe(start_x, start_y, end_x, end_y, device_id=self.device_id)
        return ActionResult(True, False)

    def _handle_back(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle back button action."""
        device_factory = get_device_factory()
        device_factory.back(self.device_id)
        return ActionResult(True, False)

    def _handle_home(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle home button action."""
        device_factory = get_device_factory()
        device_factory.home(self.device_id)
        return ActionResult(True, False)

    def _handle_double_tap(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle double tap action."""
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_relative_to_absolute(element, width, height)
        device_factory = get_device_factory()
        device_factory.double_tap(x, y, self.device_id)
        return ActionResult(True, False)

    def _handle_long_press(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle long press action."""
        element = action.get("element")
        if not element:
            return ActionResult(False, False, "No element coordinates")

        x, y = self._convert_relative_to_absolute(element, width, height)
        device_factory = get_device_factory()
        device_factory.long_press(x, y, device_id=self.device_id)
        return ActionResult(True, False)

    def _handle_wait(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle wait action."""
        duration_str = action.get("duration", "1 seconds")
        try:
            duration = float(duration_str.replace("seconds", "").strip())
        except ValueError:
            duration = 1.0

        time.sleep(duration)
        return ActionResult(True, False)

    def _handle_takeover(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle takeover request (login, captcha, etc.)."""
        message = action.get("message", "User intervention required")
        self.takeover_callback(message)
        return ActionResult(True, False)

    def _handle_note(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle note action (placeholder for content recording)."""
        # This action is typically used for recording page content
        # Implementation depends on specific requirements
        return ActionResult(True, False)

    def _handle_call_api(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle API call action (placeholder for summarization)."""
        # This action is typically used for content summarization
        # Implementation depends on specific requirements
        return ActionResult(True, False)

    def _handle_interact(self, action: dict, width: int, height: int) -> ActionResult:
        """Handle interaction request (user choice needed)."""
        # This action signals that user input is needed
        return ActionResult(True, False, message="User interaction required")

    def _send_keyevent(self, keycode: str) -> None:
        """
        向设备发送按键事件。

        根据设备类型自动选择 ADB 或 HDC 协议。
        """
        from phone_agent.device_factory import DeviceType, get_device_factory

        device_factory = get_device_factory()

        if device_factory.device_type != DeviceType.HDC:
            # ADB 设备：使用标准 input keyevent 命令
            self._send_adb_keyevent(keycode)
            return

        # HDC 设备：使用 HarmonyOS 特定的 uitest uiInput keyEvent 命令
        self._send_hdc_keyevent(keycode)

    def _send_adb_keyevent(self, keycode: str) -> None:
        """通过 ADB 发送按键事件。"""
        cmd_prefix = ["adb", "-s", self.device_id] if self.device_id else ["adb"]
        subprocess.run(
            cmd_prefix + ["shell", "input", "keyevent", keycode],
            capture_output=True,
            text=True,
        )

    def _send_hdc_keyevent(self, keycode: str) -> None:
        """
        通过 HDC 发送按键事件（HarmonyOS 专用）。

        HarmonyOS 使用 uitest uiInput keyEvent 命令，且按键码与 Android 不同。
        """
        hdc_prefix = ["hdc", "-t", self.device_id] if self.device_id else ["hdc"]

        # 尝试从映射表获取对应的 HDC 按键码
        hdc_code = self.HDC_KEYCODE_MAP.get(keycode)

        if hdc_code is None:
            # 映射表中不存在，尝试直接使用原始 keycode
            # 如果是 KEYCODE_XXX 格式但不含 ENTER，回退到 ADB 风格命令
            if keycode.startswith("KEYCODE_"):
                self._send_adb_keyevent(keycode)
                return
            hdc_code = str(keycode)

        # 发送 HDC 特定的按键命令
        subprocess.run(
            hdc_prefix + ["shell", "uitest", "uiInput", "keyEvent", hdc_code],
            capture_output=True,
            text=True,
        )

    @staticmethod
    def _default_confirmation(message: str) -> bool:
        """Default confirmation callback using console input."""
        response = input(f"Sensitive operation: {message}\nConfirm? (Y/N): ")
        return response.upper() == "Y"

    @staticmethod
    def _default_takeover(message: str) -> None:
        """Default takeover callback using console input."""
        input(f"{message}\nPress Enter after completing manual operation...")


def parse_action(response: str) -> dict[str, Any]:
    """
    Parse action from model response.

    Args:
        response: Raw response string from the model.

    Returns:
        Parsed action dictionary.

    Raises:
        ValueError: If the response cannot be parsed.
    """
    print(f"Parsing action: {response}")
    response = response.strip()

    # 处理 Type/Type_Name 动作
    if response.startswith('do(action="Type"') or response.startswith(
        'do(action="Type_Name"'
    ):
        text_part = response.split("text=", 1)
        if len(text_part) < 2:
            raise ValueError(f"Invalid Type action, missing text parameter: {response}")
        text = text_part[1][1:-2]  # 去除首尾引号
        return {"_metadata": "do", "action": "Type", "text": text}

    # 处理通用 do() 动作
    if response.startswith("do"):
        # 转义特殊字符以生成合法的 Python 语法
        response = response.replace('\n', '\\n')
        response = response.replace('\r', '\\r')
        response = response.replace('\t', '\\t')

        try:
            tree = ast.parse(response, mode="eval")
        except SyntaxError as e:
            raise ValueError(f"Failed to parse do() action (syntax error): {e}")

        if not isinstance(tree.body, ast.Call):
            raise ValueError("Expected a function call in do() action")

        call = tree.body
        action = {"_metadata": "do"}
        for keyword in call.keywords:
            key = keyword.arg
            try:
                value = ast.literal_eval(keyword.value)
            except (ValueError, SyntaxError) as e:
                raise ValueError(f"Failed to parse argument '{key}' in do() action: {e}")
            action[key] = value

        return action

    # 处理 finish 动作
    if response.startswith("finish"):
        # 安全提取 message 参数
        prefix = "finish(message="
        if not response.startswith(prefix):
            raise ValueError(f"Invalid finish action format: {response}")

        message_content = response[len(prefix):]
        # 验证格式：必须以 ")" 结尾且至少有一对引号包裹
        if not message_content.endswith(")"):
            raise ValueError(f"Finish action missing closing parenthesis: {response}")

        message_content = message_content[:-1]  # 去掉末尾的 ")"
        # 去除首尾的引号（单引号或双引号）
        if len(message_content) >= 2 and (
            (message_content[0] == '"' and message_content[-1] == '"') or
            (message_content[0] == "'" and message_content[-1] == "'")
        ):
            message_content = message_content[1:-1]

        return {"_metadata": "finish", "message": message_content}

    raise ValueError(f"Failed to parse action: {response}")


def do(**kwargs) -> dict[str, Any]:
    """Helper function for creating 'do' actions."""
    kwargs["_metadata"] = "do"
    return kwargs


def finish(**kwargs) -> dict[str, Any]:
    """Helper function for creating 'finish' actions."""
    kwargs["_metadata"] = "finish"
    return kwargs
