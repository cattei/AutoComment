
# 简单的测试脚本，验证 flet 和相关模块是否能正确导入
print("Testing imports...")

try:
    import flet
    print("✓ flet imported successfully")
except Exception as e:
    print(f"✗ flet import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    import flet_desktop
    print("✓ flet_desktop imported successfully")
except Exception as e:
    print(f"✗ flet_desktop import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    import flet_desktop.version
    print("✓ flet_desktop.version imported successfully")
except Exception as e:
    print(f"✗ flet_desktop.version import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    import markitdown
    print("✓ markitdown imported successfully")
except Exception as e:
    print(f"✗ markitdown import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    import config
    print("✓ config imported successfully")
except Exception as e:
    print(f"✗ config import failed: {e}")
    import traceback
    traceback.print_exc()

print("\nImport test complete!")
