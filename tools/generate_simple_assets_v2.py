
#!/usr/bin/env python3
"""
简化版资源生成脚本 v2 - 生成更多占位资源
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
    print("简化版资源生成脚本 v2")
    print("=" * 60)
    
    # 高坚果
    print("\n生成高坚果资源...")
    tallnut_color = (101, 67, 33)
    tallnut_idle = create_simple_sheet(70, 120, tallnut_color, 3)
    save_sheet(tallnut_idle, ASSETS_DIR / 'images/plants/tall_nut_idle_sheet.png')
    tallnut_hurt = create_simple_sheet(70, 120, (160, 82, 45), 4)
    save_sheet(tallnut_hurt, ASSETS_DIR / 'images/plants/tall_nut_hurt_sheet.png')
    
    # 地刺
    print("\n生成地刺资源...")
    spikeweed_color = (46, 139, 87)
    spikeweed_idle = create_simple_sheet(70, 90, spikeweed_color, 4)
    save_sheet(spikeweed_idle, ASSETS_DIR / 'images/plants/spikeweed_idle_sheet.png')
    spikeweed_attack = create_simple_sheet(70, 90, spikeweed_color, 3)
    save_sheet(spikeweed_attack, ASSETS_DIR / 'images/plants/spikeweed_attack_sheet.png')
    
    # 舞王僵尸
    print("\n生成舞王僵尸资源...")
    dancing_color = (150, 180, 150)
    dancing_walk = create_simple_sheet(70, 100, dancing_color, 6)
    save_sheet(dancing_walk, ASSETS_DIR / 'images/zombies/zombie_dancing_walk_sheet.png')
    dancing_summon = create_simple_sheet(70, 100, (255, 0, 200), 8)
    save_sheet(dancing_summon, ASSETS_DIR / 'images/zombies/zombie_dancing_summon_sheet.png')
    dancing_attack = create_simple_sheet(70, 100, dancing_color, 4)
    save_sheet(dancing_attack, ASSETS_DIR / 'images/zombies/zombie_dancing_attack_sheet.png')
    
    # 伴舞僵尸
    print("\n生成伴舞僵尸资源...")
    backup_color = (150, 180, 150)
    backup_walk = create_simple_sheet(70, 100, backup_color, 6)
    save_sheet(backup_walk, ASSETS_DIR / 'images/zombies/zombie_backup_walk_sheet.png')
    backup_attack = create_simple_sheet(70, 100, backup_color, 4)
    save_sheet(backup_attack, ASSETS_DIR / 'images/zombies/zombie_backup_attack_sheet.png')
    
    # 潜水僵尸
    print("\n生成潜水僵尸资源...")
    snorkel_color = (150, 180, 150)
    snorkel_swim = create_simple_sheet(70, 100, (0, 100, 200), 6)
    save_sheet(snorkel_swim, ASSETS_DIR / 'images/zombies/zombie_snorkel_swim_sheet.png')
    snorkel_walk = create_simple_sheet(70, 100, snorkel_color, 6)
    save_sheet(snorkel_walk, ASSETS_DIR / 'images/zombies/zombie_snorkel_walk_sheet.png')
    snorkel_attack = create_simple_sheet(70, 100, snorkel_color, 4)
    save_sheet(snorkel_attack, ASSETS_DIR / 'images/zombies/zombie_snorkel_attack_sheet.png')
    
    print("\n" + "=" * 60)
    print("资源生成完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()

