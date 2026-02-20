"""
精灵图资源生成器

使用PIL程序化生成简化的游戏精灵图
"""

import os
from PIL import Image, ImageDraw, ImageFilter
from typing import Tuple, List

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "sprites")


def ensure_dir(path: str):
    """确保目录存在"""
    os.makedirs(path, exist_ok=True)


def create_rounded_rect(draw: ImageDraw, x: int, y: int, w: int, h: int, 
                        radius: int, fill: Tuple[int, int, int, int], 
                        outline: Tuple[int, int, int, int] = None, width: int = 2):
    """绘制圆角矩形"""
    draw.rounded_rectangle([x, y, x + w, y + h], radius=radius, fill=fill, outline=outline, width=width)


def create_plant_sprite(width: int, height: int, color: Tuple[int, int, int], 
                        name: str, has_face: bool = True) -> Image:
    """创建植物精灵图"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    stem_color = (34, 139, 34, 255)
    leaf_color = (50, 205, 50, 255)
    
    stem_width = width // 6
    stem_x = (width - stem_width) // 2
    draw.rectangle([stem_x, height // 2, stem_x + stem_width, height - 5], fill=stem_color)
    
    head_width = int(width * 0.8)
    head_height = int(height * 0.6)
    head_x = (width - head_width) // 2
    head_y = 5
    
    draw.ellipse([head_x, head_y, head_x + head_width, head_y + head_height], fill=(*color, 255))
    
    if has_face:
        eye_size = max(4, head_width // 8)
        left_eye_x = head_x + head_width // 3 - eye_size // 2
        right_eye_x = head_x + 2 * head_width // 3 - eye_size // 2
        eye_y = head_y + head_height // 3
        
        draw.ellipse([left_eye_x, eye_y, left_eye_x + eye_size, eye_y + eye_size], fill=(0, 0, 0, 255))
        draw.ellipse([right_eye_x, eye_y, right_eye_x + eye_size, eye_y + eye_size], fill=(0, 0, 0, 255))
        
        mouth_y = head_y + head_height // 2
        mouth_width = head_width // 4
        mouth_x = (width - mouth_width) // 2
        draw.arc([mouth_x, mouth_y, mouth_x + mouth_width, mouth_y + mouth_width // 2], 
                 0, 180, fill=(0, 0, 0, 255), width=2)
    
    leaf_y = height // 2
    leaf_size = width // 4
    
    draw.ellipse([stem_x - leaf_size, leaf_y, stem_x, leaf_y + leaf_size], fill=leaf_color)
    draw.ellipse([stem_x + stem_width, leaf_y, stem_x + stem_width + leaf_size, leaf_y + leaf_size], fill=leaf_color)
    
    return img


def create_peashooter_sprite(width: int, height: int) -> Image:
    """创建豌豆射手精灵图"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    stem_color = (34, 139, 34, 255)
    head_color = (124, 252, 0, 255)
    
    stem_width = width // 5
    stem_x = width // 3
    draw.rectangle([stem_x, height // 2, stem_x + stem_width, height - 5], fill=stem_color)
    
    head_radius = int(min(width, height) * 0.35)
    head_x = width // 2
    head_y = height // 3
    draw.ellipse([head_x - head_radius, head_y - head_radius, 
                  head_x + head_radius, head_y + head_radius], fill=head_color)
    
    mouth_x = head_x + head_radius // 2
    mouth_y = head_y
    mouth_radius = head_radius // 2
    draw.ellipse([mouth_x - mouth_radius, mouth_y - mouth_radius,
                  mouth_x + mouth_radius, mouth_y + mouth_radius], fill=(50, 50, 50, 255))
    
    eye_size = head_radius // 3
    left_eye_x = head_x - head_radius // 2
    right_eye_x = head_x
    eye_y = head_y - head_radius // 3
    draw.ellipse([left_eye_x, eye_y, left_eye_x + eye_size, eye_y + eye_size], fill=(255, 255, 255, 255))
    draw.ellipse([right_eye_x, eye_y, right_eye_x + eye_size, eye_y + eye_size], fill=(255, 255, 255, 255))
    
    pupil_size = eye_size // 2
    draw.ellipse([left_eye_x + eye_size // 4, eye_y + eye_size // 4,
                  left_eye_x + eye_size // 4 + pupil_size, eye_y + eye_size // 4 + pupil_size], fill=(0, 0, 0, 255))
    draw.ellipse([right_eye_x + eye_size // 4, eye_y + eye_size // 4,
                  right_eye_x + eye_size // 4 + pupil_size, eye_y + eye_size // 4 + pupil_size], fill=(0, 0, 0, 255))
    
    leaf_y = height // 2
    leaf_size = width // 4
    draw.ellipse([stem_x - leaf_size, leaf_y, stem_x, leaf_y + leaf_size], fill=(50, 205, 50, 255))
    
    return img


def create_sunflower_sprite(width: int, height: int) -> Image:
    """创建向日葵精灵图"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    stem_color = (34, 139, 34, 255)
    petal_color = (255, 215, 0, 255)
    center_color = (139, 69, 19, 255)
    
    stem_width = width // 6
    stem_x = (width - stem_width) // 2
    draw.rectangle([stem_x, height // 2, stem_x + stem_width, height - 5], fill=stem_color)
    
    center_x = width // 2
    center_y = height // 3
    center_radius = int(min(width, height) * 0.2)
    
    petal_count = 12
    petal_length = center_radius + center_radius // 2
    petal_width = center_radius // 2
    
    import math
    for i in range(petal_count):
        angle = (2 * math.pi * i) / petal_count
        px = center_x + int(center_radius * 0.8 * math.cos(angle))
        py = center_y + int(center_radius * 0.8 * math.sin(angle))
        
        petal_img = Image.new('RGBA', (petal_length * 2, petal_width * 2), (0, 0, 0, 0))
        petal_draw = ImageDraw.Draw(petal_img)
        petal_draw.ellipse([0, petal_width // 2, petal_length, petal_width + petal_width // 2], fill=petal_color)
        
        rotated = petal_img.rotate(-math.degrees(angle) - 90, expand=True)
        img.paste(rotated, (px - rotated.width // 2, py - rotated.height // 2), rotated)
    
    draw.ellipse([center_x - center_radius, center_y - center_radius,
                  center_x + center_radius, center_y + center_radius], fill=center_color)
    
    eye_size = center_radius // 3
    left_eye_x = center_x - center_radius // 2
    right_eye_x = center_x + center_radius // 4
    eye_y = center_y - center_radius // 4
    
    draw.ellipse([left_eye_x, eye_y, left_eye_x + eye_size, eye_y + eye_size], fill=(0, 0, 0, 255))
    draw.ellipse([right_eye_x, eye_y, right_eye_x + eye_size, eye_y + eye_size], fill=(0, 0, 0, 255))
    
    smile_y = center_y + center_radius // 4
    smile_width = center_radius
    draw.arc([center_x - smile_width // 2, smile_y, center_x + smile_width // 2, smile_y + smile_width // 2],
             0, 180, fill=(0, 0, 0, 255), width=2)
    
    return img


def create_cherry_bomb_sprite(width: int, height: int) -> Image:
    """创建樱桃炸弹精灵图"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cherry_color = (220, 20, 60, 255)
    stem_color = (34, 139, 34, 255)
    
    cherry_radius = int(min(width, height) * 0.3)
    
    left_cherry_x = width // 3
    right_cherry_x = 2 * width // 3
    cherry_y = height // 2 + cherry_radius // 2
    
    draw.ellipse([left_cherry_x - cherry_radius, cherry_y - cherry_radius,
                  left_cherry_x + cherry_radius, cherry_y + cherry_radius], fill=cherry_color)
    draw.ellipse([right_cherry_x - cherry_radius, cherry_y - cherry_radius,
                  right_cherry_x + cherry_radius, cherry_y + cherry_radius], fill=cherry_color)
    
    highlight_radius = cherry_radius // 4
    draw.ellipse([left_cherry_x - cherry_radius // 2, cherry_y - cherry_radius // 2,
                  left_cherry_x - cherry_radius // 2 + highlight_radius, 
                  cherry_y - cherry_radius // 2 + highlight_radius], fill=(255, 255, 255, 180))
    draw.ellipse([right_cherry_x - cherry_radius // 2, cherry_y - cherry_radius // 2,
                  right_cherry_x - cherry_radius // 2 + highlight_radius,
                  cherry_y - cherry_radius // 2 + highlight_radius], fill=(255, 255, 255, 180))
    
    stem_start_y = cherry_y - cherry_radius
    stem_end_y = height // 6
    
    draw.line([left_cherry_x, stem_start_y, width // 2, stem_end_y], fill=stem_color, width=3)
    draw.line([right_cherry_x, stem_start_y, width // 2, stem_end_y], fill=stem_color, width=3)
    
    eye_size = cherry_radius // 4
    for cx in [left_cherry_x, right_cherry_x]:
        draw.ellipse([cx - eye_size, cherry_y - eye_size, cx + eye_size, cherry_y + eye_size], fill=(255, 255, 255, 255))
        pupil_size = eye_size // 2
        draw.ellipse([cx - pupil_size // 2, cherry_y - pupil_size // 2, 
                      cx + pupil_size // 2, cherry_y + pupil_size // 2], fill=(0, 0, 0, 255))
    
    angry_y = cherry_y - cherry_radius // 2
    draw.line([left_cherry_x - cherry_radius // 3, angry_y, 
               left_cherry_x + cherry_radius // 4, angry_y + cherry_radius // 4], fill=(0, 0, 0, 255), width=2)
    draw.line([right_cherry_x + cherry_radius // 3, angry_y,
               right_cherry_x - cherry_radius // 4, angry_y + cherry_radius // 4], fill=(0, 0, 0, 255), width=2)
    
    return img


def create_zombie_sprite(width: int, height: int, color: Tuple[int, int, int]) -> Image:
    """创建僵尸精灵图"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    skin_color = color
    shirt_color = (128, 0, 0, 255)
    pants_color = (70, 70, 70, 255)
    
    head_width = int(width * 0.5)
    head_height = int(height * 0.25)
    head_x = (width - head_width) // 2
    head_y = 5
    
    draw.ellipse([head_x, head_y, head_x + head_width, head_y + head_height], fill=(*skin_color, 255))
    
    eye_size = head_width // 5
    left_eye_x = head_x + head_width // 4
    right_eye_x = head_x + 3 * head_width // 4 - eye_size
    eye_y = head_y + head_height // 3
    
    draw.ellipse([left_eye_x, eye_y, left_eye_x + eye_size, eye_y + eye_size], fill=(255, 0, 0, 200))
    draw.ellipse([right_eye_x, eye_y, right_eye_x + eye_size, eye_y + eye_size], fill=(255, 0, 0, 200))
    
    body_width = int(width * 0.4)
    body_height = int(height * 0.3)
    body_x = (width - body_width) // 2
    body_y = head_y + head_height - 5
    
    draw.rectangle([body_x, body_y, body_x + body_width, body_y + body_height], fill=shirt_color)
    
    arm_width = body_width // 3
    arm_height = body_height
    left_arm_x = body_x - arm_width + 5
    right_arm_x = body_x + body_width - 5
    
    draw.rectangle([left_arm_x, body_y, left_arm_x + arm_width, body_y + arm_height], fill=(*skin_color, 255))
    draw.rectangle([right_arm_x, body_y, right_arm_x + arm_width, body_y + arm_height], fill=(*skin_color, 255))
    
    leg_width = body_width // 3
    leg_height = int(height * 0.25)
    leg_y = body_y + body_height
    left_leg_x = body_x + 2
    right_leg_x = body_x + body_width - leg_width - 2
    
    draw.rectangle([left_leg_x, leg_y, left_leg_x + leg_width, leg_y + leg_height], fill=pants_color)
    draw.rectangle([right_leg_x, leg_y, right_leg_x + leg_width, leg_y + leg_height], fill=pants_color)
    
    return img


def create_projectile_sprite(width: int, height: int, color: Tuple[int, int, int]) -> Image:
    """创建投射物精灵图"""
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    radius = min(width, height) // 2
    
    draw.ellipse([width // 2 - radius, height // 2 - radius,
                  width // 2 + radius, height // 2 + radius], fill=(*color, 255))
    
    highlight_radius = radius // 3
    draw.ellipse([width // 2 - radius // 2, height // 2 - radius // 2,
                  width // 2 - radius // 2 + highlight_radius,
                  height // 2 - radius // 2 + highlight_radius], fill=(255, 255, 255, 180))
    
    return img


def create_pea_sprite(width: int, height: int) -> Image:
    """创建豌豆精灵图"""
    return create_projectile_sprite(width, height, (124, 252, 0))


def create_frozen_pea_sprite(width: int, height: int) -> Image:
    """创建冰冻豌豆精灵图"""
    return create_projectile_sprite(width, height, (135, 206, 250))


def generate_all_sprites():
    """生成所有精灵图"""
    plants_dir = os.path.join(ASSETS_DIR, "plants")
    zombies_dir = os.path.join(ASSETS_DIR, "zombies")
    projectiles_dir = os.path.join(ASSETS_DIR, "projectiles")
    
    ensure_dir(plants_dir)
    ensure_dir(zombies_dir)
    ensure_dir(projectiles_dir)
    
    print("生成植物精灵图...")
    
    peashooter = create_peashooter_sprite(60, 80)
    peashooter.save(os.path.join(plants_dir, "peashooter.png"))
    
    sunflower = create_sunflower_sprite(60, 80)
    sunflower.save(os.path.join(plants_dir, "sunflower.png"))
    
    cherry_bomb = create_cherry_bomb_sprite(60, 80)
    cherry_bomb.save(os.path.join(plants_dir, "cherry_bomb.png"))
    
    wallnut = create_plant_sprite(60, 80, (210, 180, 140), "wallnut", has_face=True)
    wallnut.save(os.path.join(plants_dir, "wallnut.png"))
    
    snow_pea = create_peashooter_sprite(60, 80)
    snow_pea.save(os.path.join(plants_dir, "snow_pea.png"))
    
    repeater = create_peashooter_sprite(60, 80)
    repeater.save(os.path.join(plants_dir, "repeater.png"))
    
    print("生成僵尸精灵图...")
    
    normal_zombie = create_zombie_sprite(50, 80, (144, 164, 144))
    normal_zombie.save(os.path.join(zombies_dir, "normal.png"))
    
    cone_zombie = create_zombie_sprite(50, 80, (144, 164, 144))
    cone_zombie.save(os.path.join(zombies_dir, "cone.png"))
    
    bucket_zombie = create_zombie_sprite(50, 80, (144, 164, 144))
    bucket_zombie.save(os.path.join(zombies_dir, "bucket.png"))
    
    print("生成投射物精灵图...")
    
    pea = create_pea_sprite(15, 15)
    pea.save(os.path.join(projectiles_dir, "pea.png"))
    
    frozen_pea = create_frozen_pea_sprite(15, 15)
    frozen_pea.save(os.path.join(projectiles_dir, "frozen_pea.png"))
    
    print("精灵图生成完成！")
    print(f"资源目录: {ASSETS_DIR}")


if __name__ == "__main__":
    generate_all_sprites()
