#!/usr/bin/env python3
"""
植物大战僵尸特效资源生成工具
生成各种游戏特效：阳光、击中、爆炸、状态等
"""

from PIL import Image, ImageDraw, ImageFilter
import math
from pathlib import Path
from typing import List, Tuple

ASSETS_DIR = Path(__file__).parent.parent / 'assets'


def save_image(img: Image.Image, path: Path):
    """保存图片"""
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    print(f"生成: {path}")


def save_sprite_sheet(frames: List[Image.Image], path: Path, frames_per_row: int = 4):
    """将多帧合并为精灵表"""
    if not frames:
        return
    
    frame_width = frames[0].width
    frame_height = frames[0].height
    num_frames = len(frames)
    
    cols = min(frames_per_row, num_frames)
    rows = (num_frames + cols - 1) // cols
    
    sheet_width = cols * frame_width
    sheet_height = rows * frame_height
    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
    
    for i, frame in enumerate(frames):
        col = i % cols
        row = i // cols
        x = col * frame_width
        y = row * frame_height
        sheet.paste(frame, (x, y))
    
    save_image(sheet, path)
    return sheet


# ==================== 阳光特效 ====================

def generate_sun_effects():
    """生成阳光特效"""
    frames_spin = []
    frames_glow = []
    
    # === 阳光旋转动画（8帧）===
    for frame in range(8):
        img = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x, center_y = 25, 25
        
        # 旋转的光芒
        for i in range(8):
            angle = math.radians(i * 45 + frame * 15)  # 每帧旋转15度
            # 光芒起点
            x1 = center_x + int(10 * math.cos(angle))
            y1 = center_y + int(10 * math.sin(angle))
            # 光芒终点
            x2 = center_x + int(22 * math.cos(angle))
            y2 = center_y + int(22 * math.sin(angle))
            
            # 光芒颜色渐变
            brightness = 200 + 55 * math.sin(frame * math.pi / 4 + i * math.pi / 4)
            color = (255, int(brightness), 0, 200)
            draw.line([x1, y1, x2, y2], fill=color, width=3)
        
        # 中心圆
        draw.ellipse([center_x-10, center_y-10, center_x+10, center_y+10],
                     fill=(255, 255, 100, 230), outline=(255, 200, 0, 255), width=2)
        
        # 中心高光
        draw.ellipse([center_x-5, center_y-5, center_x+2, center_y+2],
                     fill=(255, 255, 255, 200))
        
        frames_spin.append(img)
    
    save_sprite_sheet(frames_spin, ASSETS_DIR / 'images/effects/sun_spin_sheet.png')
    
    # === 阳光收集飞行动画（6帧）===
    for frame in range(6):
        img = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x, center_y = 20, 20
        scale = 1.0 - frame * 0.12  # 逐渐变小
        alpha = 255 - frame * 40  # 逐渐透明
        
        size = int(15 * scale)
        
        # 缩小并淡出的阳光
        draw.ellipse([center_x-size, center_y-size, center_x+size, center_y+size],
                     fill=(255, 255, 100, alpha), outline=(255, 200, 0, alpha), width=2)
        
        frames_glow.append(img)
    
    save_sprite_sheet(frames_glow, ASSETS_DIR / 'images/effects/sun_collect_sheet.png')
    return frames_spin, frames_glow


# ==================== 击中特效 ====================

def generate_hit_effects():
    """生成击中特效"""
    frames_normal = []
    frames_crit = []
    frames_frozen = []
    
    # === 普通击中（绿色飞溅）===
    for frame in range(5):
        img = Image.new('RGBA', (30, 30), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x, center_y = 15, 15
        
        # 飞溅粒子
        for i in range(6):
            angle = math.radians(i * 60 + frame * 10)
            distance = 5 + frame * 2
            px = center_x + int(distance * math.cos(angle))
            py = center_y + int(distance * math.sin(angle))
            size = 3 - frame * 0.5
            
            alpha = 255 - frame * 50
            draw.ellipse([px-size, py-size, px+size, py+size],
                        fill=(100, 255, 100, int(alpha)))
        
        # 中心闪光
        if frame < 2:
            flash_size = 8 - frame * 3
            draw.ellipse([center_x-flash_size, center_y-flash_size,
                         center_x+flash_size, center_y+flash_size],
                        fill=(255, 255, 255, 200))
        
        frames_normal.append(img)
    
    save_sprite_sheet(frames_normal, ASSETS_DIR / 'images/effects/hit_normal_sheet.png')
    
    # === 暴击星形闪光 ===
    for frame in range(6):
        img = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x, center_y = 20, 20
        
        # 星形光芒
        for i in range(8):
            angle = math.radians(i * 45)
            inner_r = 3
            outer_r = 12 + frame * 2 if frame < 3 else 18 - (frame - 3) * 3
            
            x1 = center_x + int(inner_r * math.cos(angle))
            y1 = center_y + int(inner_r * math.sin(angle))
            x2 = center_x + int(outer_r * math.cos(angle))
            y2 = center_y + int(outer_r * math.sin(angle))
            
            alpha = 255 - frame * 40
            draw.line([x1, y1, x2, y2], fill=(255, 255, 150, int(alpha)), width=3)
        
        # 中心星
        alpha = 255 - frame * 40
        draw.ellipse([center_x-6, center_y-6, center_x+6, center_y+6],
                     fill=(255, 255, 200, int(alpha)))
        
        frames_crit.append(img)
    
    save_sprite_sheet(frames_crit, ASSETS_DIR / 'images/effects/hit_crit_sheet.png')
    
    # === 冰冻击中（冰晶碎裂）===
    for frame in range(6):
        img = Image.new('RGBA', (35, 35), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x, center_y = 17, 17
        
        # 冰晶碎片
        for i in range(8):
            angle = math.radians(i * 45 + frame * 15)
            distance = frame * 2
            px = center_x + int(distance * math.cos(angle))
            py = center_y + int(distance * math.sin(angle))
            
            # 冰晶形状（菱形）
            size = 4 - frame * 0.5
            alpha = 255 - frame * 40
            
            points = [
                (px, py - size),
                (px + size, py),
                (px, py + size),
                (px - size, py)
            ]
            draw.polygon(points, fill=(200, 240, 255, int(alpha)),
                        outline=(150, 200, 255, int(alpha)))
        
        # 中心冰爆
        if frame < 3:
            burst_size = 10 - frame * 3
            alpha = 200 - frame * 60
            draw.ellipse([center_x-burst_size, center_y-burst_size,
                         center_x+burst_size, center_y+burst_size],
                        fill=(200, 240, 255, int(alpha)))
        
        frames_frozen.append(img)
    
    save_sprite_sheet(frames_frozen, ASSETS_DIR / 'images/effects/hit_frozen_sheet.png')
    return frames_normal, frames_crit, frames_frozen


# ==================== 爆炸特效 ====================

def generate_explosion_effects():
    """生成爆炸特效"""
    frames_explosion = []
    frames_smoke = []
    
    # === 爆炸扩散效果（8帧）===
    for frame in range(8):
        size = 60
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x, center_y = size // 2, size // 2
        
        # 爆炸进度
        progress = frame / 7.0
        
        # 外圈火球
        outer_radius = int(10 + progress * 25)
        alpha = int(255 * (1 - progress * 0.5))
        draw.ellipse([center_x-outer_radius, center_y-outer_radius,
                     center_x+outer_radius, center_y+outer_radius],
                    fill=(255, 100 + int(50 * progress), 0, alpha),
                    outline=(255, 150, 0, alpha), width=2)
        
        # 内圈核心
        inner_radius = int(5 + progress * 15)
        draw.ellipse([center_x-inner_radius, center_y-inner_radius,
                     center_x+inner_radius, center_y+inner_radius],
                    fill=(255, 255, 200, int(alpha * 0.8)))
        
        # 爆炸碎片
        if frame < 6:
            for i in range(12):
                angle = math.radians(i * 30 + frame * 5)
                distance = int(progress * 20)
                fx = center_x + int(distance * math.cos(angle))
                fy = center_y + int(distance * math.sin(angle))
                fsize = 3 - frame * 0.4
                
                fragment_alpha = int(255 * (1 - progress))
                draw.ellipse([fx-fsize, fy-fsize, fx+fsize, fy+fsize],
                            fill=(255, 150, 0, fragment_alpha))
        
        frames_explosion.append(img)
    
    save_sprite_sheet(frames_explosion, ASSETS_DIR / 'images/effects/explosion_sheet.png')
    
    # === 烟雾效果（6帧）===
    for frame in range(6):
        size = 50
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x, center_y = size // 2, size // 2
        
        # 烟雾团
        for i in range(3):
            offset_x = (i - 1) * 8
            offset_y = -frame * 3
            radius = 10 + frame * 2 + i * 3
            alpha = int(150 - frame * 25)
            
            draw.ellipse([center_x+offset_x-radius, center_y+offset_y-radius,
                         center_x+offset_x+radius, center_y+offset_y+radius],
                        fill=(80, 80, 80, alpha))
        
        frames_smoke.append(img)
    
    save_sprite_sheet(frames_smoke, ASSETS_DIR / 'images/effects/smoke_sheet.png')
    return frames_explosion, frames_smoke


# ==================== 状态特效 ====================

def generate_status_effects():
    """生成状态特效"""
    frames_frozen = []
    frames_slow = []
    
    # === 冰冻状态（蓝色覆盖+雪花）===
    for frame in range(8):
        img = Image.new('RGBA', (70, 90), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 蓝色覆盖层
        overlay = Image.new('RGBA', (70, 90), (100, 150, 255, 80))
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)
        
        # 飘落的雪花
        for i in range(5):
            sx = 10 + i * 12
            sy = (frame * 10 + i * 20) % 90
            
            # 雪花形状
            snow_color = (255, 255, 255, 200)
            draw.line([sx, sy-3, sx, sy+3], fill=snow_color, width=1)
            draw.line([sx-3, sy, sx+3, sy], fill=snow_color, width=1)
        
        # 冰晶装饰
        for i in range(4):
            angle = math.radians(i * 90 + frame * 10)
            cx = 35 + int(25 * math.cos(angle))
            cy = 45 + int(35 * math.sin(angle))
            
            ice_color = (200, 240, 255, 150)
            draw.polygon([(cx, cy-4), (cx+4, cy), (cx, cy+4), (cx-4, cy)],
                        fill=ice_color, outline=(150, 200, 255, 200))
        
        frames_frozen.append(img)
    
    save_sprite_sheet(frames_frozen, ASSETS_DIR / 'images/effects/status_frozen_sheet.png')
    
    # === 减速状态（蓝色光晕）===
    for frame in range(6):
        img = Image.new('RGBA', (70, 90), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 脉动光晕
        pulse = 1.0 + 0.2 * math.sin(frame * math.pi / 3)
        
        # 外圈光晕
        for r in range(30, 20, -2):
            alpha = int(30 * pulse * (30 - r) / 10)
            draw.ellipse([35-r, 45-int(r*1.2), 35+r, 45+int(r*1.2)],
                        outline=(100, 150, 255, alpha), width=1)
        
        # 减速符号
        draw.text((28, 38), "\\", fill=(150, 200, 255, 200))
        
        frames_slow.append(img)
    
    save_sprite_sheet(frames_slow, ASSETS_DIR / 'images/effects/status_slow_sheet.png')
    return frames_frozen, frames_slow


# ==================== 其他特效 ====================

def generate_other_effects():
    """生成其他特效"""
    frames_plant = []
    frames_death = []
    
    # === 植物种植破土效果（5帧）===
    for frame in range(5):
        img = Image.new('RGBA', (60, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 土壤飞溅
        for i in range(8):
            angle = math.radians(i * 45 + 180)  # 向上飞溅
            distance = frame * 3
            px = 30 + int(distance * math.cos(angle))
            py = 35 + int(distance * math.sin(angle))
            
            size = 3 - frame * 0.5
            alpha = 255 - frame * 50
            
            draw.ellipse([px-size, py-size, px+size, py+size],
                        fill=(139, 90, 43, int(alpha)))
        
        # 破土裂纹
        if frame > 2:
            draw.line([25, 38, 30, 35, 35, 38], fill=(100, 70, 40), width=2)
        
        frames_plant.append(img)
    
    save_sprite_sheet(frames_plant, ASSETS_DIR / 'images/effects/plant_ground_sheet.png')
    
    # === 僵尸死亡效果（6帧）===
    for frame in range(6):
        img = Image.new('RGBA', (70, 40), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 倒地身体（逐渐变灰）
        gray_value = 150 - frame * 20
        alpha = 255 - frame * 40
        
        # 身体轮廓（躺倒）
        body_y = 25 + frame * 2
        draw.ellipse([10, body_y-8, 60, body_y+8],
                    fill=(gray_value, gray_value + 10, gray_value, int(alpha)),
                    outline=(gray_value-20, gray_value-10, gray_value-20, int(alpha)),
                    width=2)
        
        # 消散粒子
        if frame > 2:
            for i in range(5):
                px = 15 + i * 10
                py = body_y - 10 - (frame - 2) * 3
                psize = 2
                palpha = int((255 - frame * 40) * 0.5)
                draw.ellipse([px-psize, py-psize, px+psize, py+psize],
                            fill=(gray_value, gray_value, gray_value, palpha))
        
        frames_death.append(img)
    
    save_sprite_sheet(frames_death, ASSETS_DIR / 'images/effects/zombie_death_sheet.png')
    return frames_plant, frames_death


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("=" * 60)
    print("植物大战僵尸特效资源生成工具")
    print("=" * 60)
    
    # 确保目录存在
    (ASSETS_DIR / 'images/effects').mkdir(parents=True, exist_ok=True)
    
    print("\n生成阳光特效...")
    print("-" * 40)
    generate_sun_effects()
    
    print("\n生成击中特效...")
    print("-" * 40)
    generate_hit_effects()
    
    print("\n生成爆炸特效...")
    print("-" * 40)
    generate_explosion_effects()
    
    print("\n生成状态特效...")
    print("-" * 40)
    generate_status_effects()
    
    print("\n生成其他特效...")
    print("-" * 40)
    generate_other_effects()
    
    print("\n" + "=" * 60)
    print("特效资源生成完成！")
    print("=" * 60)
    print("\n生成的特效资源:")
    print("  阳光特效:")
    print("    - sun_spin_sheet.png (8帧旋转)")
    print("    - sun_collect_sheet.png (6帧收集)")
    print("  击中特效:")
    print("    - hit_normal_sheet.png (5帧普通)")
    print("    - hit_crit_sheet.png (6帧暴击)")
    print("    - hit_frozen_sheet.png (6帧冰冻)")
    print("  爆炸特效:")
    print("    - explosion_sheet.png (8帧爆炸)")
    print("    - smoke_sheet.png (6帧烟雾)")
    print("  状态特效:")
    print("    - status_frozen_sheet.png (8帧冰冻)")
    print("    - status_slow_sheet.png (6帧减速)")
    print("  其他特效:")
    print("    - plant_ground_sheet.png (5帧种植)")
    print("    - zombie_death_sheet.png (6帧死亡)")


if __name__ == '__main__':
    main()
