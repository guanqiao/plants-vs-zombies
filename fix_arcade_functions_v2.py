#!/usr/bin/env python3
"""修复 Arcade 3.0+ 函数名 - 版本2，处理参数变化"""

import re

files_to_fix = [
    'src/arcade_game/zombie_animation_renderer.py',
    'src/arcade_game/visual_effects_enhanced.py',
    'src/arcade_game/special_zombie_effects.py',
    'src/ui/menu_system.py',
    'src/systems/mini_games/beghouled.py',
]

# 替换模式：将 draw_rect_filled(x, y, width, height, color) 改为 draw_rect_filled(arcade.XYWH(x, y, width, height), color)
# 将 draw_rect_outline(x, y, width, height, color, line_width) 改为 draw_rect_outline(arcade.XYWH(x, y, width, height), color, line_width)

def fix_draw_rect_filled(content):
    """修复 draw_rect_filled 调用"""
    # 匹配 draw_rect_filled(x, y, width, height, color)
    pattern = r'arcade\.draw_rect_filled\(\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^)]+)\)'
    replacement = r'arcade.draw_rect_filled(arcade.XYWH(\1, \2, \3, \4), \5)'
    return re.sub(pattern, replacement, content)

def fix_draw_rect_outline(content):
    """修复 draw_rect_outline 调用"""
    # 匹配 draw_rect_outline(x, y, width, height, color, line_width)
    pattern = r'arcade\.draw_rect_outline\(\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^)]+)\)'
    replacement = r'arcade.draw_rect_outline(arcade.XYWH(\1, \2, \3, \4), \5, \6)'
    return re.sub(pattern, replacement, content)

for filepath in files_to_fix:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        content = fix_draw_rect_filled(content)
        content = fix_draw_rect_outline(content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed: {filepath}")
        else:
            print(f"- No changes: {filepath}")
    except Exception as e:
        print(f"✗ Error: {filepath} - {e}")

print("\nDone!")
