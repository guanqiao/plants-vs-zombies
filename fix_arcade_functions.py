#!/usr/bin/env python3
"""修复 Arcade 3.0+ 函数名"""

import re

files_to_fix = [
    'src/arcade_game/zombie_animation_renderer.py',
    'src/arcade_game/visual_effects_enhanced.py',
    'src/arcade_game/special_zombie_effects.py',
    'src/ui/menu_system.py',
    'src/systems/mini_games/beghouled.py',
]

replacements = [
    ('draw_rectangle_filled', 'draw_rect_filled'),
    ('draw_rectangle_outline', 'draw_rect_outline'),
]

for filepath in files_to_fix:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old, new in replacements:
            content = content.replace(old, new)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed: {filepath}")
        else:
            print(f"- No changes: {filepath}")
    except Exception as e:
        print(f"✗ Error: {filepath} - {e}")

print("\nDone!")
