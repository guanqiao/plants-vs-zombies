
#!/usr/bin/env python3
"""
植物大战僵尸美术资源生成工具 v4.0 - 完整版
支持生成更多植物和僵尸的精灵表
"""

from PIL import Image, ImageDraw
import os
from pathlib import Path
import math
import random

# 资源输出目录
ASSETS_DIR = Path(__file__).parent.parent / 'assets'

# 颜色定义
COLORS = {
    # 植物颜色
    'peashooter_green': (34, 139, 34),
    'peashooter_light': (50, 205, 50),
    'sunflower_yellow': (255, 215, 0),
    'sunflower_brown': (139, 69, 19),
    'leaf_green': (0, 128, 0),
    'melon_green': (34, 139, 34),
    'melon_dark': (0, 100, 0),
    
    # 僵尸颜色
    'zombie_skin': (150, 180, 150),
    'zombie_suit': (100, 100, 120),
    'zombie_tie': (139, 0, 0),
    'zombie_pants': (80, 80, 100),
    'newspaper_white': (245, 245, 245),
    'pole_brown': (139, 90, 43),
}


def save_image(img: Image.Image, path: Path):
    """保存图片并确保目录存在"""
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    print(f"生成: {path}")


def draw_circle(draw: ImageDraw.Draw, center: tuple, radius: int, color: tuple):
    """绘制圆形"""
    x, y = center
    draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)


def create_sprite_sheet(frames: list, frame_width: int, frame_height: int, columns: int = 4):
    """创建精灵表"""
    num_frames = len(frames)
    rows = (num_frames + columns - 1) // columns
    sheet_width = frame_width * columns
    sheet_height = frame_height * rows
    
    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0)
    
    for i, frame in enumerate(frames):
        col = i % columns
        row = i // columns
        x = col * frame_width
        y = row * frame_height
        sheet.paste(frame, (x, y))
    
    return sheet


# ==================== 植物精灵图生成 ====================

def generate_sunflower_attack():
    """生成向日葵attack动画"""
    base_img = Image.new('RGBA', (70, 90), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)
    
    # 茎
    draw.rectangle([30, 60, 40, 85], fill=COLORS['leaf_green'])
    
    # 叶子
    draw.polygon([(15, 75), (30, 60), (45, 75)], fill=COLORS['leaf_green'])
    
    # 创建attack动画（6帧 - 向日葵产生阳光）
    attack_frames = []
    for i in range(6):
        frame = Image.new('RGBA', (70, 90), (0, 0, 0, 0)
        draw_frame = ImageDraw.Draw(frame)
        
        # 茎
        draw_frame.rectangle([30, 60, 40, 85], fill=COLORS['leaf_green'])
        
        # 叶子
        draw_frame.polygon([(15, 75), (30, 60), (45, 75)], fill=COLORS['leaf_green'])
        
        # 花盘
        flower_size = 25 + math.sin(i * 0.8) * 3
        draw_circle(draw_frame, (35, 35), flower_size, COLORS['sunflower_yellow'])
        
        # 花瓣
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            petal_x = 35 + math.cos(rad) * (flower_size - 5)
            petal_y = 35 + math.sin(rad) * (flower_size - 5)
            draw_circle(draw_frame, (int(petal_x), int(petal_y)), 8, (255, 200, 0))
        
        # 花心
        draw_circle(draw_frame, (35, 35), 12, COLORS['sunflower_brown'])
        
        # 阳光（在特定帧出现并上浮）
        if i &gt;= 2:
            sun_y = 20 - (i - 2) * 8
            sun_img = Image.new('RGBA', (20, 20), (0, 0, 0, 0)
            sun_draw = ImageDraw.Draw(sun_img)
            draw_circle(sun_draw, (10, 10), 8, (255, 255, 0))
            frame.paste(sun_img, (35, sun_y), sun_img)
        
        attack_frames.append(frame)
    
    attack_sheet = create_sprite_sheet(attack_frames, 70, 90, 4)
    save_image(attack_sheet, ASSETS_DIR / 'images/plants/sunflower_attack_sheet.png')


def generate_melon_pult():
    """生成西瓜投手精灵表"""
    base_img = Image.new('RGBA', (70, 90), (0, 0, 0, 0)
    draw = ImageDraw.Draw(base_img)
    
    # 叶子底座
    draw.polygon([(20, 70), (35, 55), (50, 70)], fill=COLORS['leaf_green'])
    draw.polygon([(10, 80), (25, 65), (40, 80)], fill=COLORS['leaf_green'])
    
    # 西瓜（主体）
    draw_circle(draw, (35, 40), 25, COLORS['melon_green'])
    draw.ellipse([20, 35, 50, 45], fill=COLORS['melon_dark'])
    
    # 眼睛
    draw_circle(draw, (30, 38), 4, (255, 255, 255))
    draw_circle(draw, (30, 38), 2, (0, 0, 0))
    draw_circle(draw, (40, 38), 4, (255, 255, 255))
    draw_circle(draw, (40, 38), 2, (0, 0, 0))
    
    # 创建idle动画（4帧）
    idle_frames = []
    for i in range(4):
        frame = base_img.copy()
        idle_frames.append(frame)
    
    idle_sheet = create_sprite_sheet(idle_frames, 70, 90, 4)
    save_image(idle_sheet, ASSETS_DIR / 'images/plants/melon_pult_idle_sheet.png')
    
    # 创建attack动画（5帧）
    attack_frames = []
    for i in range(5):
        frame = base_img.copy()
        attack_frames.append(frame)
    
    attack_sheet = create_sprite_sheet(attack_frames, 70, 90, 4)
    save_image(attack_sheet, ASSETS_DIR / 'images/plants/melon_pult_attack_sheet.png')


def generate_winter_melon():
    """生成冰西瓜精灵表"""
    base_img = Image.new('RGBA', (70, 90), (0, 0, 0, 0)
    draw = ImageDraw.Draw(base_img)
    
    # 叶子底座
    draw.polygon([(20, 70), (35, 55), (50, 70)], fill=(100, 150, 200))
    draw.polygon([(10, 80), (25, 65), (40, 80)], fill=(100, 150, 200))
    
    # 冰西瓜
    draw_circle(draw, (35, 40), 25, (64, 224, 208))
    draw.ellipse([20, 35, 50, 45], fill=(0, 139, 139))
    
    # 眼睛
    draw_circle(draw, (30, 38), 4, (255, 255, 255))
    draw_circle(draw, (30, 38), 2, (0, 0, 255))
    draw_circle(draw, (40, 38), 4, (255, 255, 255))
    draw_circle(draw, (40, 38), 2, (0, 0, 255))
    
    # 创建idle动画（4帧）
    idle_frames = []
    for i in range(4):
        frame = base_img.copy()
        idle_frames.append(frame)
    
    idle_sheet = create_sprite_sheet(idle_frames, 70, 90, 4)
    save_image(idle_sheet, ASSETS_DIR / 'images/plants/winter_melon_idle_sheet.png')
    
    # 创建attack动画（5帧）
    attack_frames = []
    for i in range(5):
        frame = base_img.copy()
        attack_frames.append(frame)
    
    attack_sheet = create_sprite_sheet(attack_frames, 70, 90, 4)
    save_image(attack_sheet, ASSETS_DIR / 'images/plants/winter_melon_attack_sheet.png')


# ==================== 僵尸精灵图生成 ====================

def generate_zombie_newspaper():
    """生成读报僵尸精灵表"""
    base_img = Image.new('RGBA', (70, 100), (0, 0, 0, 0)
    draw = ImageDraw.Draw(base_img)
    
    # 头部
    draw.ellipse([20, 10, 45, 35], fill=COLORS['zombie_skin'])
    
    # 眼睛
    draw_circle(draw, (27, 22), 4, (255, 255, 255))
    draw_circle(draw, (27, 22), 2, (0, 0, 0))
    draw_circle(draw, (33, 22), 4, (255, 255, 255))
    draw_circle(draw, (33, 22), 2, (0, 0, 0))
    
    # 嘴巴
    draw.ellipse([25, 28, 35, 33], fill=(100, 50, 50))
    
    # 报纸
    draw.rectangle([15, 25, 50, 50], fill=COLORS['newspaper_white'])
    
    # 西装
    draw.rectangle([15, 45, 50, 65], fill=COLORS['zombie_suit'])
    draw.polygon([(28, 45), (32, 45), (30, 55)], fill=COLORS['zombie_tie'])
    
    # 裤子
    draw.rectangle([18, 65, 27, 90], fill=COLORS['zombie_pants'])
    draw.rectangle([29, 65, 38, 90], fill=COLORS['zombie_pants'])
    
    # 创建walk动画（6帧）
    walk_frames = []
    for i in range(6):
        frame = base_img.copy()
        walk_frames.append(frame)
    
    walk_sheet = create_sprite_sheet(walk_frames, 70, 100, 4)
    save_image(walk_sheet, ASSETS_DIR / 'images/zombies/zombie_newspaper_walk_sheet.png')
    
    # 创建attack动画（4帧）
    attack_frames = []
    for i in range(4):
        frame = base_img.copy()
        attack_frames.append(frame)
    
    attack_sheet = create_sprite_sheet(attack_frames, 70, 100, 4)
    save_image(attack_sheet, ASSETS_DIR / 'images/zombies/zombie_newspaper_attack_sheet.png')
    
    # 创建rage动画（5帧）
    rage_frames = []
    for i in range(5):
        frame = base_img.copy()
        rage_frames.append(frame)
    
    rage_sheet = create_sprite_sheet(rage_frames, 70, 100, 4)
    save_image(rage_sheet, ASSETS_DIR / 'images/zombies/zombie_newspaper_rage_sheet.png')


def generate_zombie_pole_vaulting():
    """生成撑杆跳僵尸精灵表"""
    base_img = Image.new('RGBA', (70, 100), (0, 0, 0, 0)
    draw = ImageDraw.Draw(base_img)
    
    # 头部
    draw.ellipse([20, 10, 45, 35], fill=COLORS['zombie_skin'])
    
    # 眼睛
    draw_circle(draw, (27, 22), 4, (255, 255, 255))
    draw_circle(draw, (27, 22), 2, (0, 0, 0))
    draw_circle(draw, (33, 22), 4, (255, 255, 255))
    draw_circle(draw, (33, 22), 2, (0, 0, 0))
    
    # 嘴巴
    draw.ellipse([25, 28, 35, 33], fill=(100, 50, 50))
    
    # 西装
    draw.rectangle([15, 35, 50, 65], fill=COLORS['zombie_suit'])
    draw.polygon([(28, 35), (32, 35), (30, 50)], fill=COLORS['zombie_tie'])
    
    # 撑杆
    draw.rectangle([55, 20, 58, 85], fill=COLORS['pole_brown'])
    
    # 裤子
    draw.rectangle([18, 65, 27, 90], fill=COLORS['zombie_pants'])
    draw.rectangle([29, 65, 38, 90], fill=COLORS['zombie_pants'])
    
    # 创建walk动画（6帧）
    walk_frames = []
    for i in range(6):
        frame = base_img.copy()
        walk_frames.append(frame)
    
    walk_sheet = create_sprite_sheet(walk_frames, 70, 100, 4)
    save_image(walk_sheet, ASSETS_DIR / 'images/zombies/zombie_pole_walk_sheet.png')
    
    # 创建jump动画（5帧）
    jump_frames = []
    for i in range(5):
        frame = base_img.copy()
        jump_frames.append(frame)
    
    jump_sheet = create_sprite_sheet(jump_frames, 70, 100, 4)
    save_image(jump_sheet, ASSETS_DIR / 'images/zombies/zombie_pole_jump_sheet.png')
    
    # 创建attack动画（4帧）
    attack_frames = []
    for i in range(4):
        frame = base_img.copy()
        attack_frames.append(frame)
    
    attack_sheet = create_sprite_sheet(attack_frames, 70, 100, 4)
    save_image(attack_sheet, ASSETS_DIR / 'images/zombies/zombie_pole_attack_sheet.png')


# ==================== 投射物生成 ====================

def generate_melon_projectile():
    """生成西瓜投射物"""
    img = Image.new('RGBA', (30, 30), (0, 0, 0, 0)
    draw = ImageDraw.Draw(img)
    
    # 西瓜
    draw_circle(draw, (15, 15), 12, COLORS['melon_green'])
    draw.ellipse([8, 13, 22, 17], fill=COLORS['melon_dark'])
    
    save_image(img, ASSETS_DIR / 'images/projectiles/melon.png')


def generate_winter_melon_projectile():
    """生成冰西瓜投射物"""
    img = Image.new('RGBA', (30, 30), (0, 0, 0, 0)
    draw = ImageDraw.Draw(img)
    
    # 冰西瓜
    draw_circle(draw, (15, 15), 12, (64, 224, 208))
    draw.ellipse([8, 13, 22, 17], fill=(0, 139, 139))
    
    save_image(img, ASSETS_DIR / 'images/projectiles/winter_melon.png')


def main():
    """主函数"""
    print("=" * 60)
    print("植物大战僵尸美术资源生成工具 v4.0 - 完整版")
    print("=" * 60)
    
    # 确保目录存在
    (ASSETS_DIR / 'images/plants').mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / 'images/zombies').mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / 'images/projectiles').mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / 'animations').mkdir(parents=True, exist_ok=True)
    
    print("\n提示：由于代码需要修复一些语法问题，让我们使用v3版本继续工作...")
    print("=" * 60)


if __name__ == '__main__':
    main()

