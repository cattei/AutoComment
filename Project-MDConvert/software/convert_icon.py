# -*- coding: utf-8 -*-
"""
图标转换脚本 - 将 JPG 转换为 ICO
"""

from PIL import Image
import os

def convert_jpg_to_ico(jpg_path, ico_path, sizes=[16, 32, 48, 64, 128, 256]):
    """将 JPG 图片转换为 ICO 格式"""
    try:
        img = Image.open(jpg_path)
        
        # 转换为 RGBA 模式
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # 调整图片大小以适应 ICO
        icons = []
        for size in sizes:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            icons.append(resized)
        
        # 保存为 ICO
        icons[0].save(
            ico_path,
            format='ICO',
            sizes=[(s, s) for s in sizes]
        )
        
        print(f"✅ 成功转换: {jpg_path} -> {ico_path}")
        return True
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return False

if __name__ == "__main__":
    jpg_path = "img/logo.jpg"
    ico_path = "img/logo.ico"
    
    if os.path.exists(jpg_path):
        convert_jpg_to_ico(jpg_path, ico_path)
    else:
        print(f"❌ 文件不存在: {jpg_path}")
