#!/usr/bin/env python3
"""
植物大战僵尸美术资源生成工具
使用PIL生成像素风格的游戏资源
"""

from PIL import Image, ImageDraw
import os
from pathlib import Path

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
    
    # 僵尸颜色
    'zombie_skin': (150, 180, 150),
    'zombie_suit': (100, 100, 120),
    'zombie_tie': (139, 0, 0),
    'zombie_pants': (80, 80, 100),
    
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


# ==================== 植物精灵图生成 ====================

def generate_peashooter():
    """生成豌豆射手精灵图"""
    # 创建60x80的图像
    img = Image.new('RGBA', (60, 80), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 身体（圆形头部）
    draw_circle(draw, (30, 35), 20, COLORS['peashooter_green'])
    # 头部高光
    draw_circle(draw, (25, 30), 5, COLORS['peashooter_light'])
    
    # 炮管
    draw.rectangle([45, 30, 58, 42], fill=COLORS['peashooter_green'])
    # 炮口
    draw.ellipse([55, 28, 62, 44], fill=COLORS['peashooter_green'])
    
    # 眼睛
    draw_circle(draw, (35, 30), 4, (255, 255, 255))
    draw_circle(draw, (36, 30), 2, (0, 0, 0))
    
    # 眉毛
    draw.line([32, 25, 38, 27], fill=(0, 0, 0), width=2)
    
    # 叶子底座
    draw.polygon([(15, 65), (30, 50), (45, 65)], fill=COLORS['leaf_green'])
    draw.polygon([(5, 75), (20, 60), (30, 75)], fill=COLORS['leaf_green'])
    draw.polygon([(40, 75), (50, 60), (55, 75)], fill=COLORS['leaf_green'])
    
    save_image(img, ASSETS_DIR / 'images/plants/peashooter.png')
    
    # 生成射击版本（炮管伸长）
    img2 = Image.new('RGBA', (70, 80), (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(img2)
    
    draw_circle(draw2, (30, 35), 20, COLORS['peashooter_green'])
    draw_circle(draw2, (25, 30), 5, COLORS['peashooter_light'])
    draw2.rectangle([45, 30, 65, 42], fill=COLORS['peashooter_green'])
    draw2.ellipse([62, 28, 72, 44], fill=COLORS['peashooter_green'])
    draw_circle(draw2, (35, 30), 4, (255, 255, 255))
    draw_circle(draw2, (36, 30), 2, (0, 0, 0))
    draw2.line([32, 25, 38, 27], fill=(0, 0, 0), width=2)
    draw2.polygon([(15, 65), (30, 50), (45, 65)], fill=COLORS['leaf_green'])
    draw2.polygon([(5, 75), (20, 60), (30, 75)], fill=COLORS['leaf_green'])
    draw2.polygon([(40, 75), (50, 60), (55, 75)], fill=COLORS['leaf_green'])
    
    save_image(img2, ASSETS_DIR / 'images/plants/peashooter_shoot.png')


def generate_sunflower():
    """生成向日葵精灵图"""
    img = Image.new('RGBA', (60, 80), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 花瓣
    petal_color = COLORS['sunflower_yellow']
    center_x, center_y = 30, 35
    for angle in range(0, 360, 30):
        import math
        rad = math.radians(angle)
        px = center_x + int(18 * math.cos(rad))
        py = center_y + int(18 * math.sin(rad))
        draw_circle(draw, (px, py), 8, petal_color)
    
    # 花盘
    draw_circle(draw, (center_x, center_y), 12, COLORS['sunflower_brown'])
    
    # 眼睛
    draw_circle(draw, (26, 33), 3, (255, 255, 255))
    draw_circle(draw, (26, 33), 1, (0, 0, 0))
    draw_circle(draw, (34, 33), 3, (255, 255, 255))
    draw_circle(draw, (34, 33), 1, (0, 0, 0))
    
    # 微笑
    draw.arc([24, 36, 36, 42], start=0, end=180, fill=(0, 0, 0), width=2)
    
    # 茎
    draw.rectangle([27, 47, 33, 65], fill=COLORS['leaf_green'])
    
    # 叶子
    draw.polygon([(10, 60), (27, 55), (27, 65)], fill=COLORS['leaf_green'])
    draw.polygon([(33, 58), (50, 55), (33, 68)], fill=COLORS['leaf_green'])
    
    save_image(img, ASSETS_DIR / 'images/plants/sunflower.png')


def generate_wallnut():
    """生成坚果墙精灵图"""
    img = Image.new('RGBA', (60, 80), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 坚果主体（椭圆）
    draw.ellipse([10, 20, 50, 70], fill=COLORS['wallnut_brown'])
    
    # 高光
    draw.ellipse([15, 25, 30, 40], fill=COLORS['wallnut_light'])
    
    # 眼睛（受伤表情）
    draw.line([22, 40, 28, 45], fill=(0, 0, 0), width=2)
    draw.line([28, 40, 22, 45], fill=(0, 0, 0), width=2)
    draw.line([32, 40, 38, 45], fill=(0, 0, 0), width=2)
    draw.line([38, 40, 32, 45], fill=(0, 0, 0), width=2)
    
    # 嘴巴（波浪形表示紧张）
    draw.line([25, 55, 30, 50, 35, 55], fill=(0, 0, 0), width=2)
    
    # 底部阴影
    draw.ellipse([15, 68, 45, 75], fill=(80, 50, 30))
    
    save_image(img, ASSETS_DIR / 'images/plants/wallnut.png')


# ==================== 僵尸精灵图生成 ====================

def generate_zombie_normal():
    """生成普通僵尸精灵图"""
    img = Image.new('RGBA', (50, 80), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 头部
    draw.ellipse([15, 10, 35, 35], fill=COLORS['zombie_skin'])
    
    # 眼睛（空洞）
    draw_circle(draw, (22, 22), 4, (255, 255, 255))
    draw_circle(draw, (22, 22), 2, (0, 0, 0))
    draw_circle(draw, (28, 22), 4, (255, 255, 255))
    draw_circle(draw, (28, 22), 2, (0, 0, 0))
    
    # 嘴巴（张开）
    draw.ellipse([20, 28, 30, 33], fill=(100, 50, 50))
    # 牙齿
    draw.rectangle([22, 28, 24, 30], fill=(255, 255, 255))
    draw.rectangle([26, 28, 28, 30], fill=(255, 255, 255))
    
    # 西装
    draw.rectangle([12, 35, 38, 65], fill=COLORS['zombie_suit'])
    # 领带
    draw.polygon([(23, 35), (27, 35), (25, 50)], fill=COLORS['zombie_tie'])
    
    # 手臂（向前伸）
    draw.rectangle([35, 40, 48, 48], fill=COLORS['zombie_suit'])
    draw_circle(draw, (50, 44), 5, COLORS['zombie_skin'])
    
    # 裤子
    draw.rectangle([15, 65, 24, 78], fill=COLORS['zombie_pants'])
    draw.rectangle([26, 65, 35, 78], fill=COLORS['zombie_pants'])
    
    # 鞋子
    draw.ellipse([12, 75, 24, 82], fill=(50, 50, 50))
    draw.ellipse([26, 75, 38, 82], fill=(50, 50, 50))
    
    save_image(img, ASSETS_DIR / 'images/zombies/zombie_normal.png')


# ==================== 投射物生成 ====================

def generate_projectiles():
    """生成投射物精灵图"""
    # 豌豆
    img = Image.new('RGBA', (20, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_circle(draw, (10, 10), 8, COLORS['pea_green'])
    draw_circle(draw, (7, 7), 3, (100, 255, 100))
    save_image(img, ASSETS_DIR / 'images/projectiles/pea.png')
    
    # 寒冰豌豆
    img = Image.new('RGBA', (20, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_circle(draw, (10, 10), 8, COLORS['frozen_blue'])
    # 冰晶效果
    for i in range(4):
        import math
        angle = i * 90
        rad = math.radians(angle)
        x = 10 + int(6 * math.cos(rad))
        y = 10 + int(6 * math.sin(rad))
        draw.line([10, 10, x, y], fill=(200, 230, 255), width=2)
    save_image(img, ASSETS_DIR / 'images/projectiles/frozen_pea.png')


# ==================== UI资源生成 ====================

def generate_ui():
    """生成UI资源"""
    # 植物卡片
    img = Image.new('RGBA', (60, 80), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # 卡片背景
    draw_rounded_rect(draw, [2, 2, 58, 78], 5, COLORS['ui_card'])
    # 边框
    draw_rounded_rect(draw, [2, 2, 58, 78], 5, COLORS['ui_card_border'])
    draw_rounded_rect(draw, [4, 4, 56, 76], 3, COLORS['ui_card'])
    save_image(img, ASSETS_DIR / 'images/ui/card_slot.png')
    
    # 阳光图标
    img = Image.new('RGBA', (30, 30), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # 外圈
    draw_circle(draw, (15, 15), 12, COLORS['sun_orange'])
    # 内圈
    draw_circle(draw, (15, 15), 9, COLORS['sun_yellow'])
    # 光芒
    for angle in range(0, 360, 45):
        import math
        rad = math.radians(angle)
        x1 = 15 + int(10 * math.cos(rad))
        y1 = 15 + int(10 * math.sin(rad))
        x2 = 15 + int(14 * math.cos(rad))
        y2 = 15 + int(14 * math.sin(rad))
        draw.line([x1, y1, x2, y2], fill=COLORS['sun_orange'], width=2)
    save_image(img, ASSETS_DIR / 'images/ui/sun_icon.png')


# ==================== 背景生成 ====================

def generate_backgrounds():
    """生成背景图"""
    # 草地格子
    img = Image.new('RGBA', (80, 100), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # 交替颜色
    draw.rectangle([0, 0, 80, 100], fill=COLORS['grass_light'])
    # 草地纹理
    for i in range(0, 80, 10):
        for j in range(0, 100, 10):
            if (i + j) % 20 == 0:
                draw.rectangle([i, j, i+5, j+5], fill=COLORS['grass_dark'])
    save_image(img, ASSETS_DIR / 'images/backgrounds/grass_tile.png')
    
    # 主背景
    img = Image.new('RGBA', (900, 600), COLORS['sky'])
    draw = ImageDraw.Draw(img)
    # 草地
    draw.rectangle([0, 100, 900, 600], fill=COLORS['grass_dark'])
    # 草地行
    for row in range(5):
        y = 150 + row * 80
        color = COLORS['grass_light'] if row % 2 == 0 else COLORS['grass_dark']
        draw.rectangle([0, y, 900, y + 80], fill=color)
        # 添加一些纹理
        for x in range(0, 900, 40):
            draw.rectangle([x, y + 10, x + 20, y + 30], 
                          fill=COLORS['grass_dark'] if color == COLORS['grass_light'] else COLORS['grass_light'])
    save_image(img, ASSETS_DIR / 'images/backgrounds/lawn_day.png')


def main():
    """主函数"""
    print("=" * 50)
    print("植物大战僵尸美术资源生成工具")
    print("=" * 50)
    
    # 确保目录存在
    (ASSETS_DIR / 'images/plants').mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / 'images/zombies').mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / 'images/projectiles').mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / 'images/ui').mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / 'images/backgrounds').mkdir(parents=True, exist_ok=True)
    
    print("\n生成植物资源...")
    generate_peashooter()
    generate_sunflower()
    generate_wallnut()
    
    print("\n生成僵尸资源...")
    generate_zombie_normal()
    
    print("\n生成投射物...")
    generate_projectiles()
    
    print("\n生成UI资源...")
    generate_ui()
    
    print("\n生成背景...")
    generate_backgrounds()
    
    print("\n" + "=" * 50)
    print("资源生成完成！")
    print(f"输出目录: {ASSETS_DIR}")
    print("=" * 50)


if __name__ == '__main__':
    main()
