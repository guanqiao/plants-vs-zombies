#!/usr/bin/env python3
"""
植物大战僵尸美术资源生成工具 V2
对标原版PVZ风格，支持多帧动画、轮廓线、高光阴影
"""

from PIL import Image, ImageDraw, ImageFilter
import os
import json
import math
from pathlib import Path
from typing import List, Tuple, Dict

# 资源输出目录
ASSETS_DIR = Path(__file__).parent.parent / 'assets'

# 优化后的调色板 - 对标原版PVZ
COLORS = {
    # 植物颜色 - 更高饱和度
    'peashooter_primary': (34, 139, 34),      # 森林绿
    'peashooter_light': (50, 205, 50),        # 鲜绿高光
    'peashooter_dark': (20, 100, 20),         # 深绿阴影
    'peashooter_outline': (10, 60, 10),       # 轮廓线
    
    'sunflower_petal': (255, 215, 0),         # 金黄花瓣
    'sunflower_petal_light': (255, 255, 100), # 亮黄高光
    'sunflower_center': (139, 69, 19),        # 棕色花盘
    'sunflower_center_dark': (100, 50, 10),   # 花盘阴影
    
    'wallnut_primary': (139, 90, 43),         # 坚果棕
    'wallnut_light': (180, 130, 70),          # 高光
    'wallnut_dark': (100, 60, 30),            # 阴影
    
    'snowpea_primary': (70, 130, 180),        # 寒冰蓝绿
    'snowpea_light': (135, 206, 250),         # 冰蓝高光
    'snowpea_dark': (40, 80, 120),            # 深蓝阴影
    
    'cherry_primary': (220, 20, 60),          # 樱桃红
    'cherry_dark': (139, 0, 0),               # 深红阴影
    'cherry_stem': (34, 85, 51),              # 樱桃梗
    
    'potato_primary': (160, 82, 45),          # 土豆棕
    'potato_dark': (120, 60, 30),             # 土豆阴影
    
    # 僵尸颜色
    'zombie_skin': (150, 180, 150),           # 僵尸绿
    'zombie_skin_dark': (120, 150, 120),      # 皮肤阴影
    'zombie_suit': (80, 80, 100),             # 西装灰
    'zombie_suit_dark': (60, 60, 80),         # 西装暗部
    'zombie_tie': (180, 30, 30),              # 红领带
    'zombie_pants': (60, 60, 80),             # 裤子
    'zombie_outline': (40, 50, 40),           # 僵尸轮廓
    
    # 路障/铁桶
    'cone_orange': (255, 140, 0),             # 路障橙
    'bucket_silver': (192, 192, 192),         # 铁桶银
    'bucket_dark': (128, 128, 128),           # 铁桶暗部
    
    # 通用
    'leaf_green': (34, 139, 34),
    'leaf_dark': (20, 100, 20),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'outline': (20, 20, 20),                  # 通用轮廓色
    
    # 投射物
    'pea_green': (50, 205, 50),
    'pea_highlight': (150, 255, 150),
    'frozen_blue': (135, 206, 250),
    'frozen_highlight': (200, 240, 255),
    
    # UI
    'ui_card_bg': (160, 120, 80),
    'ui_card_border': (100, 70, 40),
    'sun_yellow': (255, 255, 0),
    'sun_orange': (255, 180, 0),
    
    # 背景
    'grass_dark': (34, 85, 51),
    'grass_light': (50, 120, 60),
    'grass_highlight': (70, 150, 80),
    'sky': (135, 206, 235),
}


def save_image(img: Image.Image, path: Path):
    """保存图片并确保目录存在"""
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
    
    # 计算行列数
    cols = min(frames_per_row, num_frames)
    rows = (num_frames + cols - 1) // cols
    
    # 创建精灵表
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


def draw_circle_with_outline(draw: ImageDraw.Draw, center: tuple, radius: int, 
                              fill_color: tuple, outline_color: tuple = None, 
                              outline_width: int = 2):
    """绘制带轮廓的圆形"""
    x, y = center
    if outline_color and outline_width > 0:
        draw.ellipse([x-radius-outline_width, y-radius-outline_width, 
                      x+radius+outline_width, y+radius+outline_width], 
                     fill=outline_color)
    draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=fill_color)


def draw_ellipse_with_outline(draw: ImageDraw.Draw, bbox: tuple, 
                               fill_color: tuple, outline_color: tuple = None,
                               outline_width: int = 2):
    """绘制带轮廓的椭圆"""
    if outline_color and outline_width > 0:
        x1, y1, x2, y2 = bbox
        draw.ellipse([x1-outline_width, y1-outline_width, 
                      x2+outline_width, y2+outline_width], fill=outline_color)
    draw.ellipse(bbox, fill=fill_color)


def draw_rect_with_outline(draw: ImageDraw.Draw, bbox: tuple,
                            fill_color: tuple, outline_color: tuple = None,
                            outline_width: int = 2):
    """绘制带轮廓的矩形"""
    if outline_color and outline_width > 0:
        x1, y1, x2, y2 = bbox
        draw.rectangle([x1-outline_width, y1-outline_width,
                        x2+outline_width, y2+outline_width], fill=outline_color)
    draw.rectangle(bbox, fill=fill_color)


def draw_polygon_with_outline(draw: ImageDraw.Draw, points: List[tuple],
                               fill_color: tuple, outline_color: tuple = None,
                               outline_width: int = 2):
    """绘制带轮廓的多边形"""
    if outline_color and outline_width > 0:
        # 简单偏移轮廓
        offset_points = [(p[0]+outline_width, p[1]+outline_width) for p in points]
        draw.polygon(offset_points, fill=outline_color)
    draw.polygon(points, fill=fill_color)


# ==================== 豌豆射手 - 多帧动画 ====================

def generate_peashooter_enhanced():
    """生成增强版豌豆射手（带多帧动画）"""
    frames_idle = []
    frames_attack = []
    
    # 基础颜色
    primary = COLORS['peashooter_primary']
    light = COLORS['peashooter_light']
    dark = COLORS['peashooter_dark']
    outline = COLORS['peashooter_outline']
    
    # === 待机动画（4帧摇摆）===
    for frame in range(4):
        img = Image.new('RGBA', (70, 90), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 摇摆角度
        sway = math.sin(frame * math.pi / 2) * 3  # -3到3度的摇摆
        
        # 身体（圆形头部）带高光
        head_x, head_y = 35, 40
        head_radius = 22
        
        # 轮廓
        draw_circle_with_outline(draw, (head_x, head_y), head_radius, 
                                  primary, outline, 3)
        
        # 高光（左上方）
        highlight_x = head_x - 8 + int(sway)
        highlight_y = head_y - 8
        draw_circle_with_outline(draw, (highlight_x, highlight_y), 6, 
                                  light, None, 0)
        
        # 阴影（右下方）
        shadow_x = head_x + 8 + int(sway)
        shadow_y = head_y + 8
        draw.ellipse([shadow_x-5, shadow_y-5, shadow_x+5, shadow_y+5], 
                     fill=dark)
        
        # 炮管（随摇摆移动）
        barrel_x = head_x + head_radius - 5 + int(sway * 0.5)
        draw_rect_with_outline(draw, [barrel_x, head_y-8, barrel_x+20, head_y+8],
                               primary, outline, 2)
        # 炮口
        draw.ellipse([barrel_x+18, head_y-10, barrel_x+28, head_y+10], 
                     fill=primary, outline=outline, width=2)
        
        # 眼睛（大而圆，PVZ风格）
        eye_x = head_x + 5 + int(sway * 0.3)
        eye_y = head_y - 5
        # 眼白
        draw_circle_with_outline(draw, (eye_x, eye_y), 7, 
                                  COLORS['white'], outline, 1)
        # 瞳孔（看向右边）
        draw_circle_with_outline(draw, (eye_x+2, eye_y), 3, 
                                  COLORS['black'], None, 0)
        
        # 眉毛（愤怒/专注表情）
        brow_x1, brow_y1 = eye_x-5, eye_y-8
        brow_x2, brow_y2 = eye_x+5, eye_y-6
        draw.line([brow_x1, brow_y1, brow_x2, brow_y2], 
                  fill=outline, width=3)
        
        # 叶子底座（3片叶子，带摇摆）
        leaf_y = 75
        leaf_sway = int(sway * 0.5)
        
        # 中间叶子
        draw_polygon_with_outline(draw, 
            [(35+leaf_sway, 55), (25+leaf_sway, leaf_y), (45+leaf_sway, leaf_y)],
            COLORS['leaf_green'], outline, 2)
        
        # 左叶子
        draw_polygon_with_outline(draw,
            [(20+leaf_sway, 65), (5+leaf_sway, 80), (25+leaf_sway, 75)],
            COLORS['leaf_green'], outline, 2)
        
        # 右叶子
        draw_polygon_with_outline(draw,
            [(50+leaf_sway, 65), (65+leaf_sway, 80), (45+leaf_sway, 75)],
            COLORS['leaf_green'], outline, 2)
        
        frames_idle.append(img)
    
    # === 攻击动画（4帧：准备-发射-后坐力-恢复）===
    attack_phases = [
        {'barrel_extend': 0, 'recoil': 0},      # 准备
        {'barrel_extend': 15, 'recoil': -3},    # 发射（炮管伸长）
        {'barrel_extend': 5, 'recoil': 5},      # 后坐力（头部后仰）
        {'barrel_extend': 0, 'recoil': 0},      # 恢复
    ]
    
    for phase in attack_phases:
        img = Image.new('RGBA', (90, 90), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        head_x, head_y = 35, 40 + phase['recoil']
        head_radius = 22
        
        # 身体
        draw_circle_with_outline(draw, (head_x, head_y), head_radius,
                                  primary, outline, 3)
        
        # 高光
        draw_circle_with_outline(draw, (head_x-8, head_y-8), 6,
                                  light, None, 0)
        
        # 阴影
        draw.ellipse([head_x+3, head_y+3, head_x+13, head_y+13], fill=dark)
        
        # 炮管（伸长状态）
        barrel_x = head_x + head_radius - 5
        barrel_length = 20 + phase['barrel_extend']
        draw_rect_with_outline(draw, 
                               [barrel_x, head_y-8, barrel_x+barrel_length, head_y+8],
                               primary, outline, 2)
        
        # 炮口（发射时更大）
        muzzle_x = barrel_x + barrel_length
        muzzle_size = 10 if phase['barrel_extend'] > 10 else 8
        draw.ellipse([muzzle_x-2, head_y-muzzle_size, muzzle_x+muzzle_size, head_y+muzzle_size],
                     fill=primary, outline=outline, width=2)
        
        # 眼睛（发射时眯起）
        eye_x = head_x + 5
        eye_y = head_y - 5
        if phase['barrel_extend'] > 10:
            # 眯眼
            draw.line([eye_x-5, eye_y, eye_x+5, eye_y], fill=outline, width=3)
        else:
            # 正常眼睛
            draw_circle_with_outline(draw, (eye_x, eye_y), 7,
                                      COLORS['white'], outline, 1)
            draw_circle_with_outline(draw, (eye_x+2, eye_y), 3,
                                      COLORS['black'], None, 0)
        
        # 眉毛
        draw.line([eye_x-5, eye_y-8, eye_x+5, eye_y-6], fill=outline, width=3)
        
        # 叶子
        leaf_y = 75
        draw_polygon_with_outline(draw,
            [(35, 55), (25, leaf_y), (45, leaf_y)],
            COLORS['leaf_green'], outline, 2)
        draw_polygon_with_outline(draw,
            [(20, 65), (5, 80), (25, 75)],
            COLORS['leaf_green'], outline, 2)
        draw_polygon_with_outline(draw,
            [(50, 65), (65, 80), (45, 75)],
            COLORS['leaf_green'], outline, 2)
        
        frames_attack.append(img)
    
    # 保存精灵表
    save_sprite_sheet(frames_idle, ASSETS_DIR / 'images/plants/peashooter_idle_sheet.png')
    save_sprite_sheet(frames_attack, ASSETS_DIR / 'images/plants/peashooter_attack_sheet.png')
    
    return frames_idle, frames_attack


# ==================== 向日葵 - 多帧动画 ====================

def generate_sunflower_enhanced():
    """生成增强版向日葵（带多帧动画）"""
    frames_idle = []
    
    petal_color = COLORS['sunflower_petal']
    petal_light = COLORS['sunflower_petal_light']
    center_color = COLORS['sunflower_center']
    center_dark = COLORS['sunflower_center_dark']
    outline = COLORS['outline']
    
    # === 待机动画（4帧周期性摇摆）===
    for frame in range(4):
        img = Image.new('RGBA', (70, 90), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 整体摇摆
        sway = math.sin(frame * math.pi / 2) * 2
        center_x, center_y = 35 + int(sway), 35
        
        # 花瓣（12片，双层）
        for layer in range(2):
            radius = 20 - layer * 5
            color = petal_light if layer == 0 else petal_color
            for i in range(12):
                angle = math.radians(i * 30 + frame * 5)  # 轻微旋转
                px = center_x + int(radius * math.cos(angle))
                py = center_y + int(radius * math.sin(angle))
                petal_size = 10 - layer * 2
                draw_circle_with_outline(draw, (px, py), petal_size,
                                          color, outline, 1)
        
        # 花盘（带纹理）
        draw_circle_with_outline(draw, (center_x, center_y), 14,
                                  center_color, outline, 2)
        
        # 花盘纹理（小点）
        for i in range(8):
            angle = math.radians(i * 45)
            tx = center_x + int(8 * math.cos(angle))
            ty = center_y + int(8 * math.sin(angle))
            draw_circle_with_outline(draw, (tx, ty), 2, center_dark, None, 0)
        
        # 眼睛（大而可爱）
        eye_y = center_y + 2
        eye_spacing = 8
        for eye_x in [center_x - eye_spacing, center_x + eye_spacing]:
            # 眼白
            draw_circle_with_outline(draw, (eye_x, eye_y), 6,
                                      COLORS['white'], outline, 1)
            # 瞳孔（看向玩家）
            draw_circle_with_outline(draw, (eye_x, eye_y+1), 3,
                                      COLORS['black'], None, 0)
            # 高光
            draw_circle_with_outline(draw, (eye_x-1, eye_y-1), 1,
                                      COLORS['white'], None, 0)
        
        # 微笑
        smile_y = center_y + 8
        draw.arc([center_x-8, smile_y-4, center_x+8, smile_y+4],
                 start=0, end=180, fill=outline, width=2)
        
        # 茎（带弯曲）
        stem_top = center_y + 14
        stem_bottom = 75
        stem_sway = int(sway * 0.5)
        draw_polygon_with_outline(draw,
            [(center_x-3, stem_top), (center_x+3, stem_top),
             (center_x+3+stem_sway, stem_bottom), (center_x-3+stem_sway, stem_bottom)],
            COLORS['leaf_green'], outline, 1)
        
        # 叶子（2片，不对称）
        leaf_y = 60
        # 左叶子
        draw_polygon_with_outline(draw,
            [(center_x-3+stem_sway, leaf_y), (center_x-20+stem_sway, leaf_y+10),
             (center_x-3+stem_sway, leaf_y+15)],
            COLORS['leaf_green'], outline, 1)
        # 右叶子
        draw_polygon_with_outline(draw,
            [(center_x+3+stem_sway, leaf_y+5), (center_x+20+stem_sway, leaf_y+15),
             (center_x+3+stem_sway, leaf_y+20)],
            COLORS['leaf_green'], outline, 1)
        
        frames_idle.append(img)
    
    save_sprite_sheet(frames_idle, ASSETS_DIR / 'images/plants/sunflower_idle_sheet.png')
    return frames_idle


# ==================== 普通僵尸 - 多帧动画 ====================

def generate_zombie_normal_enhanced():
    """生成增强版普通僵尸（带多帧动画）"""
    frames_walk = []
    frames_attack = []
    
    skin = COLORS['zombie_skin']
    skin_dark = COLORS['zombie_skin_dark']
    suit = COLORS['zombie_suit']
    suit_dark = COLORS['zombie_suit_dark']
    tie = COLORS['zombie_tie']
    pants = COLORS['zombie_pants']
    outline = COLORS['zombie_outline']
    
    # === 行走动画（6帧蹒跚步态）===
    walk_cycle = [
        {'body_y': 0, 'arm_angle': -20, 'leg_offset': 0},
        {'body_y': -2, 'arm_angle': -10, 'leg_offset': 3},
        {'body_y': -1, 'arm_angle': 0, 'leg_offset': 5},
        {'body_y': 0, 'arm_angle': 10, 'leg_offset': 3},
        {'body_y': -2, 'arm_angle': 20, 'leg_offset': 0},
        {'body_y': -1, 'arm_angle': 10, 'leg_offset': -3},
    ]
    
    for phase in walk_cycle:
        img = Image.new('RGBA', (70, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        body_y = 40 + phase['body_y']
        
        # 头部（椭圆，略带不规则）
        head_x, head_y = 35, body_y - 25
        draw_ellipse_with_outline(draw, [head_x-12, head_y-15, head_x+12, head_y+15],
                                   skin, outline, 2)
        
        # 头发（凌乱几缕）
        for i in range(3):
            hx = head_x - 8 + i * 8
            hy = head_y - 12
            draw.line([hx, hy, hx-2, hy-5], fill=outline, width=2)
        
        # 眼睛（空洞，眼白多）
        eye_y = head_y - 3
        for eye_x in [head_x - 5, head_x + 5]:
            # 眼白（大）
            draw_circle_with_outline(draw, (eye_x, eye_y), 5,
                                      COLORS['white'], outline, 1)
            # 瞳孔（小，居中）
            draw_circle_with_outline(draw, (eye_x, eye_y), 2,
                                      COLORS['black'], None, 0)
        
        # 黑眼圈
        draw.ellipse([head_x-10, eye_y-2, head_x-2, eye_y+6], 
                     fill=(100, 120, 100, 100))
        draw.ellipse([head_x+2, eye_y-2, head_x+10, eye_y+6],
                     fill=(100, 120, 100, 100))
        
        # 嘴巴（张开，露齿）
        mouth_y = head_y + 8
        draw.ellipse([head_x-8, mouth_y-3, head_x+8, mouth_y+5],
                     fill=(80, 40, 40), outline=outline, width=1)
        # 牙齿
        for i in range(3):
            tx = head_x - 4 + i * 4
            draw.rectangle([tx, mouth_y-2, tx+2, mouth_y+1], 
                          fill=COLORS['white'])
        
        # 西装躯干
        torso_y = body_y + 5
        draw_rect_with_outline(draw, [head_x-15, torso_y, head_x+15, torso_y+30],
                               suit, outline, 2)
        
        # 领带
        tie_points = [(head_x, torso_y), (head_x-3, torso_y+20), 
                      (head_x+3, torso_y+20)]
        draw_polygon_with_outline(draw, tie_points, tie, None, 0)
        
        # 手臂（向前伸，随步态摆动）
        arm_angle = math.radians(phase['arm_angle'])
        arm_x = head_x + 15 + int(10 * math.cos(arm_angle))
        arm_y = torso_y + 5 + int(5 * math.sin(arm_angle))
        
        # 袖子
        draw_rect_with_outline(draw, [head_x+12, torso_y+3, arm_x, arm_y+8],
                               suit, outline, 1)
        # 手
        draw_circle_with_outline(draw, (arm_x+5, arm_y+4), 6,
                                  skin, outline, 1)
        
        # 裤子
        pants_y = torso_y + 30
        draw_rect_with_outline(draw, [head_x-12, pants_y, head_x-2, pants_y+20],
                               pants, outline, 1)
        draw_rect_with_outline(draw, [head_x+2, pants_y, head_x+12, pants_y+20],
                               pants, outline, 1)
        
        # 鞋子
        shoe_y = pants_y + 20
        draw.ellipse([head_x-15, shoe_y, head_x-2, shoe_y+8],
                     fill=(40, 40, 40), outline=outline, width=1)
        draw.ellipse([head_x+2, shoe_y, head_x+15, shoe_y+8],
                     fill=(40, 40, 40), outline=outline, width=1)
        
        frames_walk.append(img)
    
    # === 攻击动画（4帧前扑）===
    attack_phases = [
        {'lean': 0, 'arm_extend': 0},
        {'lean': 5, 'arm_extend': 10},
        {'lean': 10, 'arm_extend': 20},
        {'lean': 5, 'arm_extend': 10},
    ]
    
    for phase in attack_phases:
        img = Image.new('RGBA', (80, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        body_y = 40
        lean = phase['lean']
        
        # 头部（前倾）
        head_x, head_y = 35 + lean, body_y - 20
        draw_ellipse_with_outline(draw, [head_x-12, head_y-15, head_x+12, head_y+15],
                                   skin, outline, 2)
        
        # 眼睛（愤怒/饥饿）
        eye_y = head_y - 3
        for eye_x in [head_x - 5, head_x + 5]:
            draw_circle_with_outline(draw, (eye_x, eye_y), 5,
                                      COLORS['white'], outline, 1)
            draw_circle_with_outline(draw, (eye_x, eye_y), 2,
                                      COLORS['black'], None, 0)
        
        # 嘴巴（大张）
        mouth_y = head_y + 8
        draw.ellipse([head_x-10, mouth_y-4, head_x+10, mouth_y+6],
                     fill=(100, 50, 50), outline=outline, width=1)
        # 更多牙齿
        for i in range(4):
            tx = head_x - 6 + i * 4
            draw.rectangle([tx, mouth_y-3, tx+2, mouth_y+2],
                          fill=COLORS['white'])
        
        # 躯干
        torso_y = body_y + 5
        draw_rect_with_outline(draw, [head_x-15, torso_y, head_x+15, torso_y+30],
                               suit, outline, 2)
        
        # 手臂（大幅前伸）
        arm_extend = phase['arm_extend']
        draw_rect_with_outline(draw, 
                               [head_x+12, torso_y+3, head_x+35+arm_extend, torso_y+11],
                               suit, outline, 1)
        # 手（张开）
        hand_x = head_x + 40 + arm_extend
        draw_circle_with_outline(draw, (hand_x, torso_y+7), 8,
                                  skin, outline, 1)
        # 手指
        for i in range(3):
            fx = hand_x + 3 + i * 3
            draw.line([fx, torso_y+5, fx+2, torso_y-3], fill=outline, width=2)
        
        # 裤子
        pants_y = torso_y + 30
        draw_rect_with_outline(draw, [head_x-12, pants_y, head_x-2, pants_y+20],
                               pants, outline, 1)
        draw_rect_with_outline(draw, [head_x+2, pants_y, head_x+12, pants_y+20],
                               pants, outline, 1)
        
        # 鞋子
        shoe_y = pants_y + 20
        draw.ellipse([head_x-15, shoe_y, head_x-2, shoe_y+8],
                     fill=(40, 40, 40), outline=outline, width=1)
        draw.ellipse([head_x+2, shoe_y, head_x+15, shoe_y+8],
                     fill=(40, 40, 40), outline=outline, width=1)
        
        frames_attack.append(img)
    
    save_sprite_sheet(frames_walk, ASSETS_DIR / 'images/zombies/zombie_normal_walk_sheet.png')
    save_sprite_sheet(frames_attack, ASSETS_DIR / 'images/zombies/zombie_normal_attack_sheet.png')
    
    return frames_walk, frames_attack


# ==================== 寒冰射手 - 多帧动画 ====================

def generate_snowpea_enhanced():
    """生成增强版寒冰射手（带多帧动画）"""
    frames_idle = []
    frames_attack = []
    
    primary = COLORS['snowpea_primary']
    light = COLORS['snowpea_light']
    dark = COLORS['snowpea_dark']
    outline = COLORS['peashooter_outline']
    
    # === 待机动画（4帧摇摆+冰晶闪烁）===
    for frame in range(4):
        img = Image.new('RGBA', (70, 90), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        sway = math.sin(frame * math.pi / 2) * 3
        head_x, head_y = 35, 40
        head_radius = 22
        
        # 身体（带冰蓝色调）
        draw_circle_with_outline(draw, (head_x, head_y), head_radius,
                                  primary, outline, 3)
        
        # 冰晶高光
        highlight_x = head_x - 8 + int(sway)
        highlight_y = head_y - 8
        draw_circle_with_outline(draw, (highlight_x, highlight_y), 6,
                                  light, None, 0)
        
        # 冰晶装饰（闪烁效果）
        for i in range(4):
            angle = math.radians(i * 90 + frame * 15)
            cx = head_x + int(15 * math.cos(angle))
            cy = head_y + int(15 * math.sin(angle))
            size = 2 if frame % 2 == 0 else 3
            draw_circle_with_outline(draw, (cx, cy), size,
                                      (200, 240, 255), None, 0)
        
        # 炮管
        barrel_x = head_x + head_radius - 5 + int(sway * 0.5)
        draw_rect_with_outline(draw, [barrel_x, head_y-8, barrel_x+20, head_y+8],
                               primary, outline, 2)
        draw.ellipse([barrel_x+18, head_y-10, barrel_x+28, head_y+10],
                     fill=primary, outline=outline, width=2)
        
        # 眼睛（冷峻蓝色）
        eye_x = head_x + 5 + int(sway * 0.3)
        eye_y = head_y - 5
        draw_circle_with_outline(draw, (eye_x, eye_y), 7,
                                  COLORS['white'], outline, 1)
        draw_circle_with_outline(draw, (eye_x+2, eye_y), 3,
                                  (100, 150, 200), None, 0)  # 蓝色瞳孔
        
        # 眉毛（冷酷表情）
        draw.line([eye_x-5, eye_y-8, eye_x+5, eye_y-8], fill=outline, width=3)
        
        # 叶子（带冰霜）
        leaf_y = 75
        leaf_sway = int(sway * 0.5)
        
        # 中间叶子
        draw_polygon_with_outline(draw,
            [(35+leaf_sway, 55), (25+leaf_sway, leaf_y), (45+leaf_sway, leaf_y)],
            COLORS['leaf_green'], outline, 2)
        # 冰霜覆盖
        draw.ellipse([30+leaf_sway, 60, 40+leaf_sway, 70],
                     fill=(200, 230, 255, 150))
        
        # 左叶子
        draw_polygon_with_outline(draw,
            [(20+leaf_sway, 65), (5+leaf_sway, 80), (25+leaf_sway, 75)],
            COLORS['leaf_green'], outline, 2)
        
        # 右叶子
        draw_polygon_with_outline(draw,
            [(50+leaf_sway, 65), (65+leaf_sway, 80), (45+leaf_sway, 75)],
            COLORS['leaf_green'], outline, 2)
        
        frames_idle.append(img)
    
    # === 攻击动画（4帧）===
    attack_phases = [
        {'barrel_extend': 0, 'recoil': 0, 'ice_glow': 100},
        {'barrel_extend': 15, 'recoil': -3, 'ice_glow': 255},
        {'barrel_extend': 5, 'recoil': 5, 'ice_glow': 200},
        {'barrel_extend': 0, 'recoil': 0, 'ice_glow': 150},
    ]
    
    for phase in attack_phases:
        img = Image.new('RGBA', (90, 90), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        head_x, head_y = 35, 40 + phase['recoil']
        head_radius = 22
        
        # 身体
        draw_circle_with_outline(draw, (head_x, head_y), head_radius,
                                  primary, outline, 3)
        
        # 冰晶高光（发光效果）
        glow = phase['ice_glow']
        highlight_color = (200, 240, 255, glow)
        draw_circle_with_outline(draw, (head_x-8, head_y-8), 8,
                                  highlight_color, None, 0)
        
        # 炮管
        barrel_x = head_x + head_radius - 5
        barrel_length = 20 + phase['barrel_extend']
        draw_rect_with_outline(draw,
                               [barrel_x, head_y-8, barrel_x+barrel_length, head_y+8],
                               primary, outline, 2)
        
        # 炮口（冰晶效果）
        muzzle_x = barrel_x + barrel_length
        muzzle_size = 10 if phase['barrel_extend'] > 10 else 8
        draw.ellipse([muzzle_x-2, head_y-muzzle_size, muzzle_x+muzzle_size, head_y+muzzle_size],
                     fill=(150, 200, 255), outline=outline, width=2)
        
        # 眼睛
        eye_x = head_x + 5
        eye_y = head_y - 5
        draw_circle_with_outline(draw, (eye_x, eye_y), 7,
                                  COLORS['white'], outline, 1)
        draw_circle_with_outline(draw, (eye_x+2, eye_y), 3,
                                  (100, 150, 200), None, 0)
        
        # 眉毛
        draw.line([eye_x-5, eye_y-8, eye_x+5, eye_y-8], fill=outline, width=3)
        
        # 叶子
        leaf_y = 75
        draw_polygon_with_outline(draw,
            [(35, 55), (25, leaf_y), (45, leaf_y)],
            COLORS['leaf_green'], outline, 2)
        draw_polygon_with_outline(draw,
            [(20, 65), (5, 80), (25, 75)],
            COLORS['leaf_green'], outline, 2)
        draw_polygon_with_outline(draw,
            [(50, 65), (65, 80), (45, 75)],
            COLORS['leaf_green'], outline, 2)
        
        frames_attack.append(img)
    
    save_sprite_sheet(frames_idle, ASSETS_DIR / 'images/plants/snowpea_idle_sheet.png')
    save_sprite_sheet(frames_attack, ASSETS_DIR / 'images/plants/snowpea_attack_sheet.png')
    return frames_idle, frames_attack


# ==================== 樱桃炸弹 - 多帧动画 ====================

def generate_cherry_bomb_enhanced():
    """生成增强版樱桃炸弹（带多帧动画）"""
    frames_idle = []
    frames_explode = []
    
    cherry_red = COLORS['cherry_primary']
    cherry_dark = COLORS['cherry_dark']
    stem_green = COLORS['cherry_stem']
    outline = COLORS['outline']
    
    # === 待机动画（4帧闪烁）===
    for frame in range(4):
        img = Image.new('RGBA', (80, 90), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 闪烁效果
        glow_intensity = 1.0 + 0.2 * math.sin(frame * math.pi / 2)
        
        # 左樱桃
        left_x, left_y = 25, 50
        left_radius = int(18 * glow_intensity)
        draw_circle_with_outline(draw, (left_x, left_y), left_radius,
                                  cherry_red, outline, 3)
        # 高光
        draw_circle_with_outline(draw, (left_x-5, left_y-5), 5,
                                  (255, 100, 100), None, 0)
        
        # 右樱桃
        right_x, right_y = 55, 50
        right_radius = int(18 * glow_intensity)
        draw_circle_with_outline(draw, (right_x, right_y), right_radius,
                                  cherry_red, outline, 3)
        # 高光
        draw_circle_with_outline(draw, (right_x-5, right_y-5), 5,
                                  (255, 100, 100), None, 0)
        
        # 梗（连接两个樱桃）
        draw.line([(left_x, left_y-15), (40, 20), (right_x, right_y-15)],
                  fill=stem_green, width=4)
        
        # 叶子
        draw_polygon_with_outline(draw,
            [(40, 20), (30, 10), (50, 10)],
            COLORS['leaf_green'], outline, 1)
        
        # 眼睛（愤怒）
        for eye_x in [left_x, right_x]:
            # 愤怒的眼睛（斜线）
            draw.line([eye_x-5, 45, eye_x-2, 48], fill=outline, width=2)
            draw.line([eye_x+2, 45, eye_x+5, 48], fill=outline, width=2)
        
        # 嘴巴（咬牙切齿）
        draw.line([35, 60, 45, 60], fill=outline, width=3)
        
        frames_idle.append(img)
    
    # === 爆炸动画（6帧）===
    explode_phases = [
        {'scale': 1.0, 'glow': 0},
        {'scale': 1.2, 'glow': 50},
        {'scale': 1.5, 'glow': 150},
        {'scale': 2.0, 'glow': 255},  # 最大爆炸
        {'scale': 2.5, 'glow': 200},
        {'scale': 3.0, 'glow': 100},  # 消散
    ]
    
    for phase in explode_phases:
        img = Image.new('RGBA', (120, 120), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x, center_y = 60, 60
        scale = phase['scale']
        glow = phase['glow']
        
        # 爆炸核心
        core_radius = int(20 * scale)
        draw_circle_with_outline(draw, (center_x, center_y), core_radius,
                                  (255, 100, 0), None, 0)
        
        # 爆炸光晕
        glow_radius = int(30 * scale)
        glow_color = (255, 200, 0, glow)
        draw_circle_with_outline(draw, (center_x, center_y), glow_radius,
                                  glow_color, None, 0)
        
        # 爆炸碎片
        for i in range(8):
            angle = math.radians(i * 45)
            distance = int(25 * scale)
            fx = center_x + int(distance * math.cos(angle))
            fy = center_y + int(distance * math.sin(angle))
            fragment_size = int(5 * scale)
            draw_circle_with_outline(draw, (fx, fy), fragment_size,
                                      (255, 150, 0), None, 0)
        
        frames_explode.append(img)
    
    save_sprite_sheet(frames_idle, ASSETS_DIR / 'images/plants/cherry_bomb_idle_sheet.png')
    save_sprite_sheet(frames_explode, ASSETS_DIR / 'images/plants/cherry_bomb_explode_sheet.png')
    return frames_idle, frames_explode


# ==================== 土豆雷 - 多帧动画 ====================

def generate_potato_mine_enhanced():
    """生成增强版土豆雷（带多帧动画）"""
    frames_buried = []
    frames_armed = []
    frames_explode = []
    
    potato_color = COLORS['potato_primary']
    potato_dark = COLORS['potato_dark']
    outline = COLORS['outline']
    
    # === 埋藏状态（4帧）===
    for frame in range(4):
        img = Image.new('RGBA', (60, 50), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 只露出顶部
        head_x, head_y = 30, 35
        
        # 土豆顶部（半圆）
        draw_ellipse_with_outline(draw, [head_x-20, head_y-10, head_x+20, head_y+15],
                                   potato_color, outline, 2)
        
        # 眼睛（眯起，隐藏中）
        draw.line([head_x-10, head_y, head_x-5, head_y], fill=outline, width=2)
        draw.line([head_x+5, head_y, head_x+10, head_y], fill=outline, width=2)
        
        # 闪烁的指示灯
        if frame % 2 == 0:
            draw_circle_with_outline(draw, (head_x, head_y-8), 3,
                                      (255, 0, 0), None, 0)  # 红灯闪烁
        
        frames_buried.append(img)
    
    # === 激活状态（4帧）===
    for frame in range(4):
        img = Image.new('RGBA', (60, 70), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 整个身体露出
        body_x, body_y = 30, 40
        
        # 土豆身体（不规则椭圆）
        draw_ellipse_with_outline(draw, [body_x-22, body_y-15, body_x+22, body_y+20],
                                   potato_color, outline, 3)
        
        # 高光
        draw.ellipse([body_x-15, body_y-10, body_x-5, body_y], fill=potato_dark)
        
        # 眼睛（睁开，警觉）
        eye_y = body_y - 5
        for eye_x in [body_x - 8, body_x + 8]:
            draw_circle_with_outline(draw, (eye_x, eye_y), 5,
                                      COLORS['white'], outline, 1)
            draw_circle_with_outline(draw, (eye_x+1, eye_y), 2,
                                      COLORS['black'], None, 0)
        
        # 嘴巴（O型，惊讶/准备爆炸）
        draw.ellipse([body_x-5, body_y+5, body_x+5, body_y+15],
                     fill=(100, 50, 50), outline=outline, width=1)
        
        # 闪烁的指示灯（更快）
        if frame % 2 == 0:
            draw_circle_with_outline(draw, (body_x, body_y-18), 4,
                                      (255, 0, 0), outline, 1)
        
        frames_armed.append(img)
    
    save_sprite_sheet(frames_buried, ASSETS_DIR / 'images/plants/potato_mine_buried_sheet.png')
    save_sprite_sheet(frames_armed, ASSETS_DIR / 'images/plants/potato_mine_armed_sheet.png')
    return frames_buried, frames_armed


# ==================== 路障僵尸 - 多帧动画 ====================

def generate_zombie_cone_enhanced():
    """生成增强版路障僵尸（带多帧动画）"""
    frames_walk = []
    frames_attack = []
    
    skin = COLORS['zombie_skin']
    skin_dark = COLORS['zombie_skin_dark']
    suit = COLORS['zombie_suit']
    tie = COLORS['zombie_tie']
    pants = COLORS['zombie_pants']
    cone_orange = COLORS['cone_orange']
    outline = COLORS['zombie_outline']
    
    # === 行走动画（6帧）===
    walk_cycle = [
        {'body_y': 0, 'arm_angle': -20},
        {'body_y': -2, 'arm_angle': -10},
        {'body_y': -1, 'arm_angle': 0},
        {'body_y': 0, 'arm_angle': 10},
        {'body_y': -2, 'arm_angle': 20},
        {'body_y': -1, 'arm_angle': 10},
    ]
    
    for phase in walk_cycle:
        img = Image.new('RGBA', (70, 110), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        body_y = 45 + phase['body_y']
        
        # 头部
        head_x, head_y = 35, body_y - 25
        draw_ellipse_with_outline(draw, [head_x-12, head_y-15, head_x+12, head_y+15],
                                   skin, outline, 2)
        
        # 路障（戴在头上）
        cone_points = [
            (head_x, head_y-35),  # 顶点
            (head_x-18, head_y-10),  # 左下
            (head_x+18, head_y-10),  # 右下
        ]
        draw_polygon_with_outline(draw, cone_points, cone_orange, outline, 2)
        # 路障条纹
        draw.line([head_x, head_y-30, head_x, head_y-15], fill=(255, 255, 255), width=2)
        draw.line([head_x-8, head_y-22, head_x-5, head_y-12], fill=(255, 255, 255), width=2)
        draw.line([head_x+8, head_y-22, head_x+5, head_y-12], fill=(255, 255, 255), width=2)
        
        # 眼睛
        eye_y = head_y - 3
        for eye_x in [head_x - 5, head_x + 5]:
            draw_circle_with_outline(draw, (eye_x, eye_y), 5,
                                      COLORS['white'], outline, 1)
            draw_circle_with_outline(draw, (eye_x, eye_y), 2,
                                      COLORS['black'], None, 0)
        
        # 嘴巴
        mouth_y = head_y + 8
        draw.ellipse([head_x-8, mouth_y-3, head_x+8, mouth_y+5],
                     fill=(80, 40, 40), outline=outline, width=1)
        for i in range(3):
            tx = head_x - 4 + i * 4
            draw.rectangle([tx, mouth_y-2, tx+2, mouth_y+1],
                          fill=COLORS['white'])
        
        # 西装
        torso_y = body_y + 5
        draw_rect_with_outline(draw, [head_x-15, torso_y, head_x+15, torso_y+30],
                               suit, outline, 2)
        
        # 领带
        tie_points = [(head_x, torso_y), (head_x-3, torso_y+20),
                      (head_x+3, torso_y+20)]
        draw_polygon_with_outline(draw, tie_points, tie, None, 0)
        
        # 手臂
        arm_angle = math.radians(phase['arm_angle'])
        arm_x = head_x + 15 + int(10 * math.cos(arm_angle))
        arm_y = torso_y + 5 + int(5 * math.sin(arm_angle))
        draw_rect_with_outline(draw, [head_x+12, torso_y+3, arm_x, arm_y+8],
                               suit, outline, 1)
        draw_circle_with_outline(draw, (arm_x+5, arm_y+4), 6,
                                  skin, outline, 1)
        
        # 裤子
        pants_y = torso_y + 30
        draw_rect_with_outline(draw, [head_x-12, pants_y, head_x-2, pants_y+20],
                               pants, outline, 1)
        draw_rect_with_outline(draw, [head_x+2, pants_y, head_x+12, pants_y+20],
                               pants, outline, 1)
        
        # 鞋子
        shoe_y = pants_y + 20
        draw.ellipse([head_x-15, shoe_y, head_x-2, shoe_y+8],
                     fill=(40, 40, 40), outline=outline, width=1)
        draw.ellipse([head_x+2, shoe_y, head_x+15, shoe_y+8],
                     fill=(40, 40, 40), outline=outline, width=1)
        
        frames_walk.append(img)
    
    # === 攻击动画（4帧）===
    for i in range(4):
        img = Image.new('RGBA', (80, 110), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        body_y = 45
        lean = i * 3
        
        # 头部（前倾）
        head_x, head_y = 35 + lean, body_y - 20
        draw_ellipse_with_outline(draw, [head_x-12, head_y-15, head_x+12, head_y+15],
                                   skin, outline, 2)
        
        # 路障
        cone_points = [
            (head_x, head_y-35),
            (head_x-18, head_y-10),
            (head_x+18, head_y-10),
        ]
        draw_polygon_with_outline(draw, cone_points, cone_orange, outline, 2)
        
        # 眼睛
        eye_y = head_y - 3
        for eye_x in [head_x - 5, head_x + 5]:
            draw_circle_with_outline(draw, (eye_x, eye_y), 5,
                                      COLORS['white'], outline, 1)
            draw_circle_with_outline(draw, (eye_x, eye_y), 2,
                                      COLORS['black'], None, 0)
        
        # 嘴巴（大张）
        mouth_y = head_y + 8
        draw.ellipse([head_x-10, mouth_y-4, head_x+10, mouth_y+6],
                     fill=(100, 50, 50), outline=outline, width=1)
        for i in range(4):
            tx = head_x - 6 + i * 4
            draw.rectangle([tx, mouth_y-3, tx+2, mouth_y+2],
                          fill=COLORS['white'])
        
        # 躯干
        torso_y = body_y + 5
        draw_rect_with_outline(draw, [head_x-15, torso_y, head_x+15, torso_y+30],
                               suit, outline, 2)
        
        # 手臂（前伸）
        arm_extend = i * 8
        draw_rect_with_outline(draw,
                               [head_x+12, torso_y+3, head_x+35+arm_extend, torso_y+11],
                               suit, outline, 1)
        hand_x = head_x + 40 + arm_extend
        draw_circle_with_outline(draw, (hand_x, torso_y+7), 8,
                                  skin, outline, 1)
        
        # 裤子
        pants_y = torso_y + 30
        draw_rect_with_outline(draw, [head_x-12, pants_y, head_x-2, pants_y+20],
                               pants, outline, 1)
        draw_rect_with_outline(draw, [head_x+2, pants_y, head_x+12, pants_y+20],
                               pants, outline, 1)
        
        # 鞋子
        shoe_y = pants_y + 20
        draw.ellipse([head_x-15, shoe_y, head_x-2, shoe_y+8],
                     fill=(40, 40, 40), outline=outline, width=1)
        draw.ellipse([head_x+2, shoe_y, head_x+15, shoe_y+8],
                     fill=(40, 40, 40), outline=outline, width=1)
        
        frames_attack.append(img)
    
    save_sprite_sheet(frames_walk, ASSETS_DIR / 'images/zombies/zombie_cone_walk_sheet.png')
    save_sprite_sheet(frames_attack, ASSETS_DIR / 'images/zombies/zombie_cone_attack_sheet.png')
    return frames_walk, frames_attack


# ==================== 铁桶僵尸 - 多帧动画 ====================

def generate_zombie_bucket_enhanced():
    """生成增强版铁桶僵尸（带多帧动画）"""
    frames_walk = []
    frames_attack = []
    
    skin = COLORS['zombie_skin']
    suit = COLORS['zombie_suit']
    tie = COLORS['zombie_tie']
    pants = COLORS['zombie_pants']
    bucket_silver = COLORS['bucket_silver']
    bucket_dark = COLORS['bucket_dark']
    outline = COLORS['zombie_outline']
    
    # === 行走动画（6帧）===
    walk_cycle = [
        {'body_y': 0, 'arm_angle': -20},
        {'body_y': -2, 'arm_angle': -10},
        {'body_y': -1, 'arm_angle': 0},
        {'body_y': 0, 'arm_angle': 10},
        {'body_y': -2, 'arm_angle': 20},
        {'body_y': -1, 'arm_angle': 10},
    ]
    
    for phase in walk_cycle:
        img = Image.new('RGBA', (70, 110), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        body_y = 45 + phase['body_y']
        
        # 头部（大部分被铁桶遮住）
        head_x, head_y = 35, body_y - 20
        
        # 铁桶（圆柱形）
        # 桶身
        draw_rect_with_outline(draw, [head_x-15, head_y-40, head_x+15, head_y],
                               bucket_silver, outline, 2)
        # 桶底
        draw.ellipse([head_x-15, head_y-5, head_x+15, head_y+5],
                     fill=bucket_dark, outline=outline, width=2)
        # 桶顶
        draw.ellipse([head_x-15, head_y-45, head_x+15, head_y-35],
                     fill=bucket_silver, outline=outline, width=2)
        # 桶的高光
        draw.rectangle([head_x-10, head_y-35, head_x-5, head_y-10],
                       fill=(220, 220, 220))
        
        # 露出的脸部（底部）
        draw_ellipse_with_outline(draw, [head_x-12, head_y-5, head_x+12, head_y+15],
                                   skin, outline, 2)
        
        # 眼睛（从桶下露出）
        eye_y = head_y + 5
        for eye_x in [head_x - 5, head_x + 5]:
            draw_circle_with_outline(draw, (eye_x, eye_y), 4,
                                      COLORS['white'], outline, 1)
            draw_circle_with_outline(draw, (eye_x, eye_y), 2,
                                      COLORS['black'], None, 0)
        
        # 嘴巴
        mouth_y = head_y + 12
        draw.ellipse([head_x-6, mouth_y-2, head_x+6, mouth_y+4],
                     fill=(80, 40, 40), outline=outline, width=1)
        
        # 西装
        torso_y = body_y + 5
        draw_rect_with_outline(draw, [head_x-15, torso_y, head_x+15, torso_y+30],
                               suit, outline, 2)
        
        # 领带
        tie_points = [(head_x, torso_y), (head_x-3, torso_y+20),
                      (head_x+3, torso_y+20)]
        draw_polygon_with_outline(draw, tie_points, tie, None, 0)
        
        # 手臂
        arm_angle = math.radians(phase['arm_angle'])
        arm_x = head_x + 15 + int(10 * math.cos(arm_angle))
        arm_y = torso_y + 5 + int(5 * math.sin(arm_angle))
        draw_rect_with_outline(draw, [head_x+12, torso_y+3, arm_x, arm_y+8],
                               suit, outline, 1)
        draw_circle_with_outline(draw, (arm_x+5, arm_y+4), 6,
                                  skin, outline, 1)
        
        # 裤子
        pants_y = torso_y + 30
        draw_rect_with_outline(draw, [head_x-12, pants_y, head_x-2, pants_y+20],
                               pants, outline, 1)
        draw_rect_with_outline(draw, [head_x+2, pants_y, head_x+12, pants_y+20],
                               pants, outline, 1)
        
        # 鞋子
        shoe_y = pants_y + 20
        draw.ellipse([head_x-15, shoe_y, head_x-2, shoe_y+8],
                     fill=(40, 40, 40), outline=outline, width=1)
        draw.ellipse([head_x+2, shoe_y, head_x+15, shoe_y+8],
                     fill=(40, 40, 40), outline=outline, width=1)
        
        frames_walk.append(img)
    
    # === 攻击动画（4帧）===
    for i in range(4):
        img = Image.new('RGBA', (80, 110), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        body_y = 45
        lean = i * 3
        
        # 头部
        head_x, head_y = 35 + lean, body_y - 20
        
        # 铁桶
        draw_rect_with_outline(draw, [head_x-15, head_y-40, head_x+15, head_y],
                               bucket_silver, outline, 2)
        draw.ellipse([head_x-15, head_y-5, head_x+15, head_y+5],
                     fill=bucket_dark, outline=outline, width=2)
        draw.ellipse([head_x-15, head_y-45, head_x+15, head_y-35],
                     fill=bucket_silver, outline=outline, width=2)
        draw.rectangle([head_x-10, head_y-35, head_x-5, head_y-10],
                       fill=(220, 220, 220))
        
        # 露出的脸
        draw_ellipse_with_outline(draw, [head_x-12, head_y-5, head_x+12, head_y+15],
                                   skin, outline, 2)
        
        # 眼睛
        eye_y = head_y + 5
        for eye_x in [head_x - 5, head_x + 5]:
            draw_circle_with_outline(draw, (eye_x, eye_y), 4,
                                      COLORS['white'], outline, 1)
            draw_circle_with_outline(draw, (eye_x, eye_y), 2,
                                      COLORS['black'], None, 0)
        
        # 嘴巴（大张）
        mouth_y = head_y + 12
        draw.ellipse([head_x-8, mouth_y-3, head_x+8, mouth_y+6],
                     fill=(100, 50, 50), outline=outline, width=1)
        
        # 躯干
        torso_y = body_y + 5
        draw_rect_with_outline(draw, [head_x-15, torso_y, head_x+15, torso_y+30],
                               suit, outline, 2)
        
        # 手臂（前伸）
        arm_extend = i * 8
        draw_rect_with_outline(draw,
                               [head_x+12, torso_y+3, head_x+35+arm_extend, torso_y+11],
                               suit, outline, 1)
        hand_x = head_x + 40 + arm_extend
        draw_circle_with_outline(draw, (hand_x, torso_y+7), 8,
                                  skin, outline, 1)
        
        # 裤子
        pants_y = torso_y + 30
        draw_rect_with_outline(draw, [head_x-12, pants_y, head_x-2, pants_y+20],
                               pants, outline, 1)
        draw_rect_with_outline(draw, [head_x+2, pants_y, head_x+12, pants_y+20],
                               pants, outline, 1)
        
        # 鞋子
        shoe_y = pants_y + 20
        draw.ellipse([head_x-15, shoe_y, head_x-2, shoe_y+8],
                     fill=(40, 40, 40), outline=outline, width=1)
        draw.ellipse([head_x+2, shoe_y, head_x+15, shoe_y+8],
                     fill=(40, 40, 40), outline=outline, width=1)
        
        frames_attack.append(img)
    
    save_sprite_sheet(frames_walk, ASSETS_DIR / 'images/zombies/zombie_bucket_walk_sheet.png')
    save_sprite_sheet(frames_attack, ASSETS_DIR / 'images/zombies/zombie_bucket_attack_sheet.png')
    return frames_walk, frames_attack


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("=" * 60)
    print("植物大战僵尸美术资源生成工具 V2")
    print("对标原版PVZ风格 - 支持多帧动画")
    print("=" * 60)
    
    # 确保目录存在
    (ASSETS_DIR / 'images/plants').mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / 'images/zombies').mkdir(parents=True, exist_ok=True)
    
    print("\n生成增强版植物资源...")
    print("-" * 40)
    generate_peashooter_enhanced()
    generate_sunflower_enhanced()
    generate_snowpea_enhanced()
    generate_cherry_bomb_enhanced()
    generate_potato_mine_enhanced()
    
    print("\n生成增强版僵尸资源...")
    print("-" * 40)
    generate_zombie_normal_enhanced()
    generate_zombie_cone_enhanced()
    generate_zombie_bucket_enhanced()
    
    print("\n" + "=" * 60)
    print("资源生成完成！")
    print("=" * 60)
    print("\n生成的植物资源:")
    print("  - peashooter_idle_sheet.png (4帧待机动画)")
    print("  - peashooter_attack_sheet.png (4帧攻击动画)")
    print("  - sunflower_idle_sheet.png (4帧待机动画)")
    print("  - snowpea_idle_sheet.png (4帧待机动画)")
    print("  - snowpea_attack_sheet.png (4帧攻击动画)")
    print("  - cherry_bomb_idle_sheet.png (4帧待机动画)")
    print("  - cherry_bomb_explode_sheet.png (6帧爆炸动画)")
    print("  - potato_mine_buried_sheet.png (4帧埋藏动画)")
    print("  - potato_mine_armed_sheet.png (4帧激活动画)")
    print("\n生成的僵尸资源:")
    print("  - zombie_normal_walk_sheet.png (6帧行走动画)")
    print("  - zombie_normal_attack_sheet.png (4帧攻击动画)")
    print("  - zombie_cone_walk_sheet.png (6帧行走动画)")
    print("  - zombie_cone_attack_sheet.png (4帧攻击动画)")
    print("  - zombie_bucket_walk_sheet.png (6帧行走动画)")
    print("  - zombie_bucket_attack_sheet.png (4帧攻击动画)")


if __name__ == '__main__':
    main()
