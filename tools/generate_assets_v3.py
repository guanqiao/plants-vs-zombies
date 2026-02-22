
#!/usr/bin/env python3
"""
植物大战僵尸美术资源生成工具 v3.0 - 增强版
支持生成更多植物和僵尸的精灵表
"""

from PIL import Image, ImageDraw
import os
from pathlib import Path
import math

# 资源输出目录
ASSETS_DIR = Path(__file__).parent.parent / 'assets'

# 颜色定义
COLORS = {
    # 植物颜色
    'peashooter_green': (34, 139, 34),
    'peashooter_light': (50, 205, 50),
    'sunflower_yellow': (255, 215, 0),
    'sunflower_brown': (139, 69, 19),
    'wallnut_brown': (101, 67, 33),
    'wallnut_light': (160, 82, 45),
    'leaf_green': (0, 128, 0),
    'snow_blue': (135, 206, 250),
    'snow_light': (200, 230, 255),
    'cherry_red': (220, 20, 60),
    'cherry_dark': (139, 0, 0),
    'potato_brown': (210, 180, 140),
    'potato_dark': (160, 120, 80),
    
    # 僵尸颜色
    'zombie_skin': (150, 180, 150),
    'zombie_suit': (100, 100, 120),
    'zombie_tie': (139, 0, 0),
    'zombie_pants': (80, 80, 100),
    'cone_orange': (255, 140, 0),
    'bucket_gray': (128, 128, 128),
    'flag_red': (200, 0, 0),
    
    # 投射物
    'pea_green': (50, 205, 50),
    'frozen_blue': (135, 206, 250),
    
    # UI
    'ui_card': (139, 90, 43),
    'ui_card_border': (101, 67, 33),
    'sun_yellow': (255, 255, 0),
    'sun_orange': (255, 165, 0),
    
    # 背景
    'grass_dark': (34, 85, 51),
    'grass_light': (50, 120, 60),
    'dirt': (101, 67, 33),
    'sky': (135, 206, 235),
    'night_sky': (20, 30, 50),
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


def draw_rounded_rect(draw: ImageDraw.Draw, bbox: tuple, radius: int, color: tuple):
    """绘制圆角矩形"""
    x1, y1, x2, y2 = bbox
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=color)


def create_sprite_sheet(frames: list, frame_width: int, frame_height: int, columns: int = 4):
    """创建精灵表"""
    num_frames = len(frames)
    rows = (num_frames + columns - 1) // columns
    sheet_width = frame_width * columns
    sheet_height = frame_height * rows
    
    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
    
    for i, frame in enumerate(frames):
        col = i % columns
        row = i // columns
        x = col * frame_width
        y = row * frame_height
        sheet.paste(frame, (x, y))
    
    return sheet


# ==================== 植物精灵图生成 ====================

def generate_repeater():
    """生成双发射手精灵表"""
    base_img = Image.new('RGBA', (70, 90), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)
    
    # 身体（两个头）
    draw_circle(draw, (30, 35), 18, COLORS['peashooter_green'])
    draw_circle(draw, (25, 30), 4, COLORS['peashooter_light'])
    
    # 第二个头（稍微小一点）
    draw_circle(draw, (35, 25), 12, COLORS['peashooter_green'])
    draw_circle(draw, (33, 22), 3, COLORS['peashooter_light'])
    
    # 主炮管
    draw.rectangle([45, 30, 62, 42], fill=COLORS['peashooter_green'])
    draw.ellipse([59, 28, 68, 44], fill=COLORS['peashooter_green'])
    
    # 副炮管
    draw.rectangle([48, 20, 60, 28], fill=COLORS['peashooter_green'])
    draw.ellipse([57, 18, 66, 30], fill=COLORS['peashooter_green'])
    
    # 眼睛
    draw_circle(draw, (35, 33), 3, (255, 255, 255))
    draw_circle(draw, (36, 33), 1.5, (0, 0, 0))
    
    # 叶子底座
    draw.polygon([(15, 65), (30, 50), (45, 65)], fill=COLORS['leaf_green'])
    draw.polygon([(5, 75), (20, 60), (30, 75)], fill=COLORS['leaf_green'])
    draw.polygon([(40, 75), (50, 60), (55, 75)], fill=COLORS['leaf_green'])
    
    # 创建idle动画（4帧）
    idle_frames = []
    for i in range(4):
        frame = base_img.copy()
        idle_frames.append(frame)
    
    idle_sheet = create_sprite_sheet(idle_frames, 70, 90, 4)
    save_image(idle_sheet, ASSETS_DIR / 'images/plants/repeater_idle_sheet.png')
    
    # 创建attack动画（4帧）
    attack_frames = []
    for i in range(4):
        frame = base_img.copy()
        if i == 1:
            # 炮管伸长
            draw_frame = ImageDraw.Draw(frame)
            draw_frame.rectangle([45, 30, 68, 42], fill=COLORS['peashooter_green'])
            draw_frame.ellipse([65, 28, 75, 44], fill=COLORS['peashooter_green'])
        attack_frames.append(frame)
    
    attack_sheet = create_sprite_sheet(attack_frames, 70, 90, 4)
    save_image(attack_sheet, ASSETS_DIR / 'images/plants/repeater_attack_sheet.png')


def generate_chomper():
    """生成大嘴花精灵表"""
    base_img = Image.new('RGBA', (70, 90), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)
    
    # 身体（绿色）
    draw.ellipse([15, 30, 55, 70], fill=COLORS['peashooter_green'])
    
    # 头（大嘴巴）
    draw.ellipse([10, 15, 60, 45], fill=COLORS['peashooter_green'])
    
    # 嘴巴（闭合）
    draw.ellipse([20, 25, 50, 40], fill=(100, 50, 50))
    
    # 眼睛
    draw_circle(draw, (25, 20), 4, (255, 255, 255))
    draw_circle(draw, (25, 20), 2, (0, 0, 0))
    draw_circle(draw, (45, 20), 4, (255, 255, 255))
    draw_circle(draw, (45, 20), 2, (0, 0, 0))
    
    # 茎
    draw.rectangle([30, 70, 40, 85], fill=COLORS['leaf_green'])
    
    # 创建idle动画（4帧）
    idle_frames = []
    for i in range(4):
        frame = base_img.copy()
        idle_frames.append(frame)
    
    idle_sheet = create_sprite_sheet(idle_frames, 70, 90, 4)
    save_image(idle_sheet, ASSETS_DIR / 'images/plants/chomper_idle_sheet.png')
    
    # 创建attack动画（6帧 - 嘴巴张开）
    attack_frames = []
    for i in range(6):
        frame = Image.new('RGBA', (70, 90), (0, 0, 0, 0))
        draw_frame = ImageDraw.Draw(frame)
        
        # 身体
        draw_frame.ellipse([15, 30, 55, 70], fill=COLORS['peashooter_green'])
        
        # 头
        draw_frame.ellipse([10, 15, 60, 45], fill=COLORS['peashooter_green'])
        
        # 嘴巴（逐渐张开）
        mouth_open = min(30, i * 6)
        draw_frame.ellipse([20, 25 - mouth_open//2, 50, 40 + mouth_open//2], fill=(100, 50, 50))
        
        # 眼睛
        draw_circle(draw_frame, (25, 20 - mouth_open//4), 4, (255, 255, 255))
        draw_circle(draw_frame, (25, 20 - mouth_open//4), 2, (0, 0, 0))
        draw_circle(draw_frame, (45, 20 - mouth_open//4), 4, (255, 255, 255))
        draw_circle(draw_frame, (45, 20 - mouth_open//4), 2, (0, 0, 0))
        
        # 茎
        draw_frame.rectangle([30, 70, 40, 85], fill=COLORS['leaf_green'])
        
        attack_frames.append(frame)
    
    attack_sheet = create_sprite_sheet(attack_frames, 70, 90, 4)
    save_image(attack_sheet, ASSETS_DIR / 'images/plants/chomper_attack_sheet.png')


def generate_threepeater():
    """生成三线射手精灵表"""
    base_img = Image.new('RGBA', (80, 90), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)
    
    # 主身体
    draw_circle(draw, (40, 45), 20, COLORS['peashooter_green'])
    draw_circle(draw, (35, 40), 5, COLORS['peashooter_light'])
    
    # 三个头
    positions = [(40, 30), (40, 45), (40, 60)]
    for i, (x, y) in enumerate(positions):
        # 头
        draw_circle(draw, (x, y), 12, COLORS['peashooter_green'])
        # 炮管
        draw.rectangle([x+10, y-5, x+28, y+5], fill=COLORS['peashooter_green'])
        draw.ellipse([x+25, y-7, x+35, y+7], fill=COLORS['peashooter_green'])
    
    # 眼睛
    draw_circle(draw, (45, 43), 3, (255, 255, 255))
    draw_circle(draw, (46, 43), 1.5, (0, 0, 0))
    
    # 叶子底座
    draw.polygon([(20, 75), (40, 60), (60, 75)], fill=COLORS['leaf_green'])
    draw.polygon([(10, 85), (25, 70), (40, 85)], fill=COLORS['leaf_green'])
    draw.polygon([(55, 85), (65, 70), (70, 85)], fill=COLORS['leaf_green'])
    
    # 创建idle动画（4帧）
    idle_frames = []
    for i in range(4):
        frame = base_img.copy()
        idle_frames.append(frame)
    
    idle_sheet = create_sprite_sheet(idle_frames, 80, 90, 4)
    save_image(idle_sheet, ASSETS_DIR / 'images/plants/threepeater_idle_sheet.png')
    
    # 创建attack动画（6帧）
    attack_frames = []
    for i in range(6):
        frame = base_img.copy()
        if i in [1, 3, 5]:
            # 炮管伸长
            draw_frame = ImageDraw.Draw(frame)
            positions = [(40, 30), (40, 45), (40, 60)]
            for x, y in positions:
                draw_frame.rectangle([x+10, y-5, x+35, y+5], fill=COLORS['peashooter_green'])
                draw_frame.ellipse([x+32, y-7, x+42, y+7], fill=COLORS['peashooter_green'])
        attack_frames.append(frame)
    
    attack_sheet = create_sprite_sheet(attack_frames, 80, 90, 4)
    save_image(attack_sheet, ASSETS_DIR / 'images/plants/threepeater_attack_sheet.png')


# ==================== 僵尸精灵图生成 ====================

def generate_zombie_flag():
    """生成旗帜僵尸精灵表"""
    base_img = Image.new('RGBA', (70, 100), (0, 0, 0, 0))
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
    
    # 手臂（举旗帜）
    draw.rectangle([45, 30, 55, 55], fill=COLORS['zombie_suit'])
    draw_circle(draw, (57, 32), 5, COLORS['zombie_skin'])
    
    # 旗帜杆
    draw.rectangle([55, 10, 58, 55], fill=(100, 80, 60))
    
    # 旗帜
    draw.polygon([(58, 10), (70, 15), (58, 25)], fill=COLORS['flag_red'])
    
    # 裤子
    draw.rectangle([18, 65, 27, 90], fill=COLORS['zombie_pants'])
    draw.rectangle([29, 65, 38, 90], fill=COLORS['zombie_pants'])
    
    # 鞋子
    draw.ellipse([15, 87, 27, 95], fill=(50, 50, 50))
    draw.ellipse([29, 87, 41, 95], fill=(50, 50, 50))
    
    # 创建walk动画（6帧）
    walk_frames = []
    for i in range(6):
        frame = base_img.copy()
        walk_frames.append(frame)
    
    walk_sheet = create_sprite_sheet(walk_frames, 70, 100, 4)
    save_image(walk_sheet, ASSETS_DIR / 'images/zombies/zombie_flag_walk_sheet.png')
    
    # 创建attack动画（4帧）
    attack_frames = []
    for i in range(4):
        frame = base_img.copy()
        attack_frames.append(frame)
    
    attack_sheet = create_sprite_sheet(attack_frames, 70, 100, 4)
    save_image(attack_sheet, ASSETS_DIR / 'images/zombies/zombie_flag_attack_sheet.png')


def generate_zombie_football():
    """生成橄榄球僵尸精灵表"""
    base_img = Image.new('RGBA', (70, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base_img)
    
    # 橄榄球头盔
    draw.ellipse([15, 8, 50, 30], fill=(150, 50, 50))
    draw.ellipse([20, 12, 45, 26], fill=(180, 60, 60))
    
    # 面罩
    draw.rectangle([22, 18, 43, 28], fill=(100, 100, 100))
    
    # 身体（橄榄球服）
    draw.rectangle([12, 30, 53, 68], fill=(150, 50, 50))
    
    # 肩膀护垫
    draw.ellipse([8, 30, 57, 40], fill=(100, 30, 30))
    
    # 手臂（向前伸）
    draw.rectangle([50, 40, 65, 50], fill=(150, 50, 50))
    draw_circle(draw, (67, 45), 5, COLORS['zombie_skin'])
    
    # 裤子
    draw.rectangle([15, 68, 26, 92], fill=(100, 30, 30))
    draw.rectangle([30, 68, 41, 92], fill=(100, 30, 30))
    
    # 鞋子
    draw.ellipse([12, 89, 26, 97], fill=(50, 50, 50))
    draw.ellipse([30, 89, 44, 97], fill=(50, 50, 50))
    
    # 创建walk动画（6帧）
    walk_frames = []
    for i in range(6):
        frame = base_img.copy()
        walk_frames.append(frame)
    
    walk_sheet = create_sprite_sheet(walk_frames, 70, 100, 4)
    save_image(walk_sheet, ASSETS_DIR / 'images/zombies/zombie_football_walk_sheet.png')
    
    # 创建attack动画（4帧）
    attack_frames = []
    for i in range(4):
        frame = base_img.copy()
        attack_frames.append(frame)
    
    attack_sheet = create_sprite_sheet(attack_frames, 70, 100, 4)
    save_image(attack_sheet, ASSETS_DIR / 'images/zombies/zombie_football_attack_sheet.png')


# ==================== 场景生成 ====================

def generate_lawn_night():
    """生成黑夜场景背景"""
    img = Image.new('RGBA', (900, 600), COLORS['night_sky'])
    draw = ImageDraw.Draw(img)
    
    # 星星
    for _ in range(50):
        x = int(random.random() * 900)
        y = int(random.random() * 120)
        size = int(random.random() * 3) + 1
        draw_circle(draw, (x, y), size, (255, 255, 255))
    
    # 月亮
    draw_circle(draw, (800, 60), 40, (255, 255, 220))
    draw_circle(draw, (790, 55), 35, COLORS['night_sky'])
    
    # 草地（深色）
    draw.rectangle([0, 100, 900, 600], fill=(20, 50, 30))
    
    # 草地行
    for row in range(5):
        y = 150 + row * 80
        color = (30, 60, 35) if row % 2 == 0 else (25, 55, 30)
        draw.rectangle([0, y, 900, y + 80], fill=color)
    
    save_image(img, ASSETS_DIR / 'images/backgrounds/lawn_night.png')


# ==================== 工具函数 ====================

import random


def update_sprite_sheets_config():
    """更新精灵表配置文件"""
    import json
    
    config_path = ASSETS_DIR / 'animations/sprite_sheets.json'
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {
            "version": "3.0",
            "description": "精灵表配置文件 - 增强版",
            "sprite_sheets": {},
            "legacy_fallback": {
                "enabled": True,
                "paths": {}
            }
        }
    
    # 添加新植物配置
    new_plants = {
        "repeater": {
            "idle": {
                "sheet_path": "images/plants/repeater_idle_sheet.png",
                "frames": 4,
                "frame_width": 70,
                "frame_height": 90,
                "fps": 10,
                "loop": True,
                "columns": 4
            },
            "attack": {
                "sheet_path": "images/plants/repeater_attack_sheet.png",
                "frames": 4,
                "frame_width": 70,
                "frame_height": 90,
                "fps": 12,
                "loop": False,
                "columns": 4,
                "event_frame": 1
            }
        },
        "chomper": {
            "idle": {
                "sheet_path": "images/plants/chomper_idle_sheet.png",
                "frames": 4,
                "frame_width": 70,
                "frame_height": 90,
                "fps": 8,
                "loop": True,
                "columns": 4
            },
            "attack": {
                "sheet_path": "images/plants/chomper_attack_sheet.png",
                "frames": 6,
                "frame_width": 70,
                "frame_height": 90,
                "fps": 10,
                "loop": False,
                "columns": 4
            }
        },
        "threepeater": {
            "idle": {
                "sheet_path": "images/plants/threepeater_idle_sheet.png",
                "frames": 4,
                "frame_width": 80,
                "frame_height": 90,
                "fps": 10,
                "loop": True,
                "columns": 4
            },
            "attack": {
                "sheet_path": "images/plants/threepeater_attack_sheet.png",
                "frames": 6,
                "frame_width": 80,
                "frame_height": 90,
                "fps": 12,
                "loop": False,
                "columns": 4
            }
        }
    }
    
    # 添加新僵尸配置
    new_zombies = {
        "zombie_flag": {
            "walk": {
                "sheet_path": "images/zombies/zombie_flag_walk_sheet.png",
                "frames": 6,
                "frame_width": 70,
                "frame_height": 100,
                "fps": 12,
                "loop": True,
                "columns": 4
            },
            "attack": {
                "sheet_path": "images/zombies/zombie_flag_attack_sheet.png",
                "frames": 4,
                "frame_width": 70,
                "frame_height": 100,
                "fps": 10,
                "loop": True,
                "columns": 4
            }
        },
        "zombie_football": {
            "walk": {
                "sheet_path": "images/zombies/zombie_football_walk_sheet.png",
                "frames": 6,
                "frame_width": 70,
                "frame_height": 100,
                "fps": 14,
                "loop": True,
                "columns": 4
            },
            "attack": {
                "sheet_path": "images/zombies/zombie_football_attack_sheet.png",
                "frames": 4,
                "frame_width": 70,
                "frame_height": 100,
                "fps": 12,
                "loop": True,
                "columns": 4
            }
        }
    }
    
    config["sprite_sheets"].update(new_plants)
    config["sprite_sheets"].update(new_zombies)
    
    # 保存配置
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"更新配置: {config_path}")


def main():
    """主函数"""
    print("=" * 60)
    print("植物大战僵尸美术资源生成工具 v3.0 - 增强版")
    print("=" * 60)
    
    # 确保目录存在
    (ASSETS_DIR / 'images/plants').mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / 'images/zombies').mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / 'images/backgrounds').mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / 'animations').mkdir(parents=True, exist_ok=True)
    
    print("\n生成植物资源（新增）...")
    generate_repeater()
    generate_chomper()
    generate_threepeater()
    
    print("\n生成僵尸资源（新增）...")
    generate_zombie_flag()
    generate_zombie_football()
    
    print("\n生成场景资源（新增）...")
    generate_lawn_night()
    
    print("\n更新精灵表配置...")
    update_sprite_sheets_config()
    
    print("\n" + "=" * 60)
    print("增强版资源生成完成！")
    print(f"输出目录: {ASSETS_DIR}")
    print("\n提示：本工具生成的是占位资源")
    print("建议使用专业美术软件替换为高质量像素画")
    print("=" * 60)


if __name__ == '__main__':
    main()
