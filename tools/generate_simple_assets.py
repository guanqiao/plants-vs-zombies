
#!/usr/bin/env python3
"""
简化版资源生成脚本 - 生成占位资源
"""

from PIL import Image, ImageDraw
from pathlib import Path

ASSETS_DIR = Path(__file__).parent.parent / 'assets'


def draw_circle(draw, center, radius, color):
    x, y = center
    draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)


def create_simple_sheet(width, height, color, num_frames=4):
    """创建简单的精灵表"""
    frames = []
    for i in range(num_frames):
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # 绘制一个简单的形状
        draw_circle(draw, (width//2, height//2), min(width, height)//3, color)
        frames.append(img)
    
    # 创建精灵表
    sheet_width = width * 4
    sheet_height = height * ((num_frames + 3) // 4)
    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
    
    for i, frame in enumerate(frames):
        col = i % 4
        row = i // 4
        x = col * width
        y = row * height
        sheet.paste(frame, (x, y))
    
    return sheet


def save_sheet(img, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    print(f"生成: {path}")


def main():
    print("=" * 60)
    print("简化版资源生成脚本")
    print("=" * 60)
    
    # 向日葵attack
    print("\n生成向日葵资源...")
    sunflower_color = (255, 215, 0)
    sunflower_attack = create_simple_sheet(70, 90, sunflower_color, 6)
    save_sheet(sunflower_attack, ASSETS_DIR / 'images/plants/sunflower_attack_sheet.png')
    
    # 西瓜投手
    print("\n生成西瓜投手资源...")
    melon_color = (34, 139, 34)
    melon_idle = create_simple_sheet(70, 90, melon_color, 4)
    save_sheet(melon_idle, ASSETS_DIR / 'images/plants/melon_pult_idle_sheet.png')
    melon_attack = create_simple_sheet(70, 90, melon_color, 5)
    save_sheet(melon_attack, ASSETS_DIR / 'images/plants/melon_pult_attack_sheet.png')
    
    # 冰西瓜
    print("\n生成冰西瓜资源...")
    winter_color = (64, 224, 208)
    winter_idle = create_simple_sheet(70, 90, winter_color, 4)
    save_sheet(winter_idle, ASSETS_DIR / 'images/plants/winter_melon_idle_sheet.png')
    winter_attack = create_simple_sheet(70, 90, winter_color, 5)
    save_sheet(winter_attack, ASSETS_DIR / 'images/plants/winter_melon_attack_sheet.png')
    
    # 读报僵尸
    print("\n生成读报僵尸资源...")
    newspaper_color = (150, 180, 150)
    newspaper_walk = create_simple_sheet(70, 100, newspaper_color, 6)
    save_sheet(newspaper_walk, ASSETS_DIR / 'images/zombies/zombie_newspaper_walk_sheet.png')
    newspaper_attack = create_simple_sheet(70, 100, newspaper_color, 4)
    save_sheet(newspaper_attack, ASSETS_DIR / 'images/zombies/zombie_newspaper_attack_sheet.png')
    newspaper_rage = create_simple_sheet(70, 100, (255, 0, 0), 5)
    save_sheet(newspaper_rage, ASSETS_DIR / 'images/zombies/zombie_newspaper_rage_sheet.png')
    
    # 撑杆跳僵尸
    print("\n生成撑杆跳僵尸资源...")
    pole_color = (150, 180, 150)
    pole_walk = create_simple_sheet(70, 100, pole_color, 6)
    save_sheet(pole_walk, ASSETS_DIR / 'images/zombies/zombie_pole_walk_sheet.png')
    pole_jump = create_simple_sheet(70, 100, pole_color, 5)
    save_sheet(pole_jump, ASSETS_DIR / 'images/zombies/zombie_pole_jump_sheet.png')
    pole_attack = create_simple_sheet(70, 100, pole_color, 4)
    save_sheet(pole_attack, ASSETS_DIR / 'images/zombies/zombie_pole_attack_sheet.png')
    
    # 投射物
    print("\n生成投射物资源...")
    melon_proj = create_simple_sheet(30, 30, melon_color, 1)
    save_sheet(melon_proj, ASSETS_DIR / 'images/projectiles/melon.png')
    winter_proj = create_simple_sheet(30, 30, winter_color, 1)
    save_sheet(winter_proj, ASSETS_DIR / 'images/projectiles/winter_melon.png')
    
    print("\n" + "=" * 60)
    print("资源生成完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()

