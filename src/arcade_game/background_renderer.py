"""
背景渲染器 - 绘制游戏背景和网格 - 增强版

包括：
- 草地背景（棋盘格效果）
- 网格线
- 装饰元素（花朵、石头、灌木）
- 动态效果（草地摇摆、光斑）
- 使用Material Design配色
"""

import arcade
import math
import random
from typing import Tuple, List, Optional
from dataclasses import dataclass

from ..core.theme_colors import GameColors, PRIMARY, PRIMARY_LIGHT, PRIMARY_DARK, SECONDARY, SECONDARY_LIGHT, WHITE, Color


@dataclass
class Decoration:
    """装饰元素"""
    x: float
    y: float
    decoration_type: str  # flower, rock, bush, grass
    size: float
    color_variant: int
    sway_offset: float = 0.0
    sway_speed: float = 1.0


@dataclass
class LightSpot:
    """光斑效果"""
    x: float
    y: float
    size: float
    alpha: float
    speed: float
    angle: float


@dataclass
class Cloud:
    """云朵装饰"""
    x: float
    y: float
    size: float
    speed: float
    opacity: float


@dataclass
class Mountain:
    """山脉装饰"""
    x: float
    height: float
    width: float
    color: Tuple[int, int, int]


class BackgroundRenderer:
    """
    背景渲染器 - 增强版
    
    负责绘制游戏背景、草坪网格和装饰元素
    使用Material Design配色方案
    """
    
    # 使用GameColors的配色
    GRASS_LIGHT = GameColors.GRASS_LIGHT
    GRASS_DARK = GameColors.GRASS_DARK
    GRASS_BORDER = GameColors.GRASS_BORDER
    PATH_COLOR = GameColors.DIRT
    GRID_LINE = Color(60, 100, 30)
    
    # 天空颜色渐变 - 更柔和的蓝色
    SKY_TOP = Color(100, 181, 246)      # Material Blue 300
    SKY_BOTTOM = Color(187, 222, 251)   # Material Blue 100
    
    # 装饰颜色 - 使用Material Design调色板
    FLOWER_COLORS = [
        Color(239, 83, 80),    # 红色
        Color(255, 167, 38),   # 橙色
        Color(253, 216, 53),   # 黄色
        Color(236, 64, 122),   # 粉色
        Color(171, 71, 188),   # 紫色
    ]
    ROCK_COLORS = [
        Color(158, 158, 158),
        Color(138, 138, 138),
        Color(118, 118, 118),
    ]
    BUSH_COLORS = [
        Color(67, 160, 71),    # Material Green 600
        Color(76, 175, 80),    # Material Green 500
        Color(56, 142, 60),    # Material Green 700
    ]
    
    # 山脉颜色
    MOUNTAIN_COLORS = [
        Color(120, 144, 156),  # Blue Grey
        Color(144, 164, 174),
        Color(176, 190, 197),
    ]
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 网格配置 - 与游戏窗口匹配
        self.rows = 5
        self.cols = 9
        self.cell_width = 80
        self.cell_height = 100
        # 调整起始位置，给顶部UI留出空间
        self.start_x = 100
        self.start_y = 80  # 增加底部边距，让网格在屏幕中间偏下
        
        # 时间累积（用于动画）
        self._time = 0.0
        
        # 装饰元素
        self.decorations: List[Decoration] = []
        self.light_spots: List[LightSpot] = []
        self.clouds: List[Cloud] = []
        self.mountains: List[Mountain] = []
        
        # 预计算网格位置
        self._calculate_grid_positions()
        
        # 初始化装饰元素和光斑
        self._init_decorations()
        
        # 生成光斑
        self._init_light_spots()
        
        # 初始化云朵
        self._init_clouds()
        
        # 初始化山脉
        self._init_mountains()
    
    def _calculate_grid_positions(self) -> None:
        """计算网格位置"""
        self.grid_cells: List[Tuple[float, float, float, float]] = []
        
        for row in range(self.rows):
            for col in range(self.cols):
                x = self.start_x + col * self.cell_width
                y = self.start_y + row * self.cell_height
                self.grid_cells.append((x, y, x + self.cell_width, y + self.cell_height))
    
    def _init_decorations(self) -> None:
        """初始化装饰元素"""
        # 在网格周围添加一些装饰性的花朵和石头
        for _ in range(12):
            # 在网格区域外随机生成装饰
            side = random.choice(['left', 'right', 'top', 'bottom'])
            if side == 'left':
                x = random.uniform(10, self.start_x - 10)
                y = random.uniform(0, self.screen_height)
            elif side == 'right':
                x = random.uniform(self.start_x + self.cols * self.cell_width + 10, self.screen_width - 10)
                y = random.uniform(0, self.screen_height)
            elif side == 'top':
                x = random.uniform(0, self.screen_width)
                y = random.uniform(self.start_y + self.rows * self.cell_height + 10, self.screen_height - 10)
            else:  # bottom
                x = random.uniform(0, self.screen_width)
                y = random.uniform(10, self.start_y - 10)
            
            decoration_type = random.choice(['flower', 'rock', 'bush'])
            size = random.uniform(5, 15)
            color_variant = random.randint(0, 4)
            
            decoration = Decoration(
                x=x, y=y,
                decoration_type=decoration_type,
                size=size,
                color_variant=color_variant,
                sway_offset=random.uniform(0, math.pi * 2),
                sway_speed=random.uniform(0.5, 2.0)
            )
            self.decorations.append(decoration)
    
    def _init_light_spots(self) -> None:
        """初始化光斑效果"""
        for _ in range(6):
            light_spot = LightSpot(
                x=random.uniform(self.start_x, self.start_x + self.cols * self.cell_width),
                y=random.uniform(self.start_y, self.start_y + self.rows * self.cell_height),
                size=random.uniform(25, 60),
                alpha=random.uniform(20, 50),
                speed=random.uniform(5, 15),
                angle=random.uniform(0, math.pi * 2)
            )
            self.light_spots.append(light_spot)
    
    def render(self) -> None:
        """渲染背景和网格"""
        # 绘制天空渐变
        self._draw_sky_gradient()
        
        # 绘制山脉
        self._draw_mountains()
        
        # 绘制云朵
        self._draw_clouds()
        
        # 绘制草地背景
        self._draw_grass_background()
        
        # 绘制网格
        self._draw_grid()
        
        # 绘制装饰元素
        self._draw_decorations()
    
    def _draw_grass_background(self) -> None:
        """绘制草地背景（棋盘格效果）- 增强版"""
        # 绘制整个游戏区域背景
        total_width = self.cols * self.cell_width
        total_height = self.rows * self.cell_height
        
        # 绘制外边框 - 带阴影效果
        arcade.draw_lrbt_rectangle_filled(
            self.start_x - 8, self.start_x + total_width + 8,
            self.start_y - 8, self.start_y + total_height + 8,
            (0, 0, 0, 80)
        )
        
        # 绘制主边框
        arcade.draw_lrbt_rectangle_filled(
            self.start_x - 5, self.start_x + total_width + 5,
            self.start_y - 5, self.start_y + total_height + 5,
            self.GRASS_BORDER.rgba
        )
        
        # 绘制棋盘格草地
        for row in range(self.rows):
            for col in range(self.cols):
                x = self.start_x + col * self.cell_width
                y = self.start_y + row * self.cell_height
                
                # 交替颜色
                if (row + col) % 2 == 0:
                    color = self.GRASS_LIGHT
                else:
                    color = self.GRASS_DARK
                
                # 绘制单元格背景
                arcade.draw_lrbt_rectangle_filled(
                    x, x + self.cell_width,
                    y, y + self.cell_height,
                    color.rgba
                )
                
                # 添加草地纹理效果
                self._draw_grass_texture(x, y, color)
                
                # 添加高光效果（每隔几个单元格）
                if (row + col) % 3 == 0:
                    highlight_alpha = 20
                    arcade.draw_lrbt_rectangle_filled(
                        x + 5, x + self.cell_width - 5,
                        y + self.cell_height - 10, y + self.cell_height - 5,
                        WHITE.with_alpha(highlight_alpha).rgba
                    )
    
    def _draw_grass_texture(self, cell_x: float, cell_y: float, base_color: Color) -> None:
        """绘制草地纹理"""
        # 使用固定的"随机"位置来绘制草地点，保持每帧一致
        random.seed(int(cell_x * 1000 + cell_y))  # 使用位置作为种子
        
        # 绘制一些深色的草地点
        for _ in range(5):
            dot_x = cell_x + random.uniform(5, self.cell_width - 5)
            dot_y = cell_y + random.uniform(5, self.cell_height - 5)
            dot_size = random.uniform(1, 3)
            
            # 深色点缀
            darker_color = base_color.darken(0.15)
            arcade.draw_circle_filled(dot_x, dot_y, dot_size, darker_color.rgba)
    
    def _draw_grid(self) -> None:
        """绘制网格线 - 增强版"""
        total_width = self.cols * self.cell_width
        total_height = self.rows * self.cell_height
        
        # 绘制垂直线 - 带阴影效果
        for col in range(self.cols + 1):
            x = self.start_x + col * self.cell_width
            # 阴影
            arcade.draw_line(
                x + 1, self.start_y,
                x + 1, self.start_y + total_height,
                (0, 0, 0, 60), 1
            )
            # 主线
            arcade.draw_line(
                x, self.start_y,
                x, self.start_y + total_height,
                self.GRID_LINE.rgba, 1
            )
        
        # 绘制水平线
        for row in range(self.rows + 1):
            y = self.start_y + row * self.cell_height
            # 阴影
            arcade.draw_line(
                self.start_x, y - 1,
                self.start_x + total_width, y - 1,
                (0, 0, 0, 60), 1
            )
            # 主线
            arcade.draw_line(
                self.start_x, y,
                self.start_x + total_width, y,
                self.GRID_LINE.rgba, 1
            )
    
    def _draw_decorations(self) -> None:
        """绘制装饰元素"""
        # 绘制光斑效果
        self._draw_light_spots()
        
        # 绘制装饰元素
        for deco in self.decorations:
            self._draw_decoration(deco)
        
        # 绘制行号标识 - 增强版
        for row in range(self.rows):
            y = self.start_y + row * self.cell_height + self.cell_height / 2
            # 阴影
            arcade.draw_text(
                str(row + 1),
                self.start_x - 23, y - 1,
                (0, 0, 0, 150), 14,
                anchor_x="center", anchor_y="center",
                font_name=("Arial", "Microsoft YaHei", "sans-serif")
            )
            # 主文字
            arcade.draw_text(
                str(row + 1),
                self.start_x - 25, y,
                WHITE.rgba, 14,
                anchor_x="center", anchor_y="center",
                font_name=("Arial", "Microsoft YaHei", "sans-serif")
            )
        
        # 绘制列号标识 - 增强版
        for col in range(self.cols):
            x = self.start_x + col * self.cell_width + self.cell_width / 2
            # 阴影
            arcade.draw_text(
                str(col + 1),
                x + 1, self.start_y + self.rows * self.cell_height + 9,
                (0, 0, 0, 150), 14,
                anchor_x="center",
                font_name=("Arial", "Microsoft YaHei", "sans-serif")
            )
            # 主文字
            arcade.draw_text(
                str(col + 1),
                x, self.start_y + self.rows * self.cell_height + 10,
                WHITE.rgba, 14,
                anchor_x="center",
                font_name=("Arial", "Microsoft YaHei", "sans-serif")
            )
    
    def _draw_decoration(self, deco: Decoration) -> None:
        """绘制单个装饰元素"""
        # 计算摇摆偏移
        sway = math.sin(self._time * deco.sway_speed + deco.sway_offset) * 3
        
        if deco.decoration_type == 'flower':
            self._draw_flower(deco.x + sway, deco.y, deco.size, deco.color_variant)
        elif deco.decoration_type == 'rock':
            self._draw_rock(deco.x, deco.y, deco.size, deco.color_variant)
        elif deco.decoration_type == 'bush':
            self._draw_bush(deco.x + sway * 0.5, deco.y, deco.size, deco.color_variant)
        elif deco.decoration_type == 'grass':
            self._draw_grass_blade(deco.x + sway, deco.y, deco.size)
    
    def _draw_flower(self, x: float, y: float, size: float, color_idx: int) -> None:
        """绘制花朵 - 增强版"""
        color = self.FLOWER_COLORS[color_idx % len(self.FLOWER_COLORS)]
        
        # 花茎
        arcade.draw_line(x, y, x, y + size * 1.5, PRIMARY_DARK.rgba, 2)
        
        # 花瓣 - 带高光效果
        petal_count = 5
        center_y = y + size * 1.5
        for i in range(petal_count):
            angle = (i / petal_count) * math.pi * 2 + self._time * 0.5
            px = x + math.cos(angle) * size * 0.6
            py = center_y + math.sin(angle) * size * 0.6
            
            # 花瓣阴影
            arcade.draw_circle_filled(px + 1, py - 1, size * 0.4, (0, 0, 0, 50))
            # 花瓣主体
            arcade.draw_circle_filled(px, py, size * 0.4, color.rgba)
            # 花瓣高光
            arcade.draw_circle_filled(px - size * 0.1, py + size * 0.1, size * 0.15, 
                                      color.lighten(0.3).rgba)
        
        # 花心 - 带渐变效果
        arcade.draw_circle_filled(x, center_y, size * 0.3, SECONDARY.rgba)
        arcade.draw_circle_filled(x - size * 0.05, center_y + size * 0.05, size * 0.15, 
                                  SECONDARY_LIGHT.rgba)
    
    def _draw_rock(self, x: float, y: float, size: float, color_idx: int) -> None:
        """绘制石头 - 增强版"""
        color = self.ROCK_COLORS[color_idx % len(self.ROCK_COLORS)]
        
        # 不规则多边形
        points = []
        vertices = 6
        for i in range(vertices):
            angle = (i / vertices) * math.pi * 2
            r = size * (0.7 + 0.3 * math.sin(angle * 3 + x))
            px = x + math.cos(angle) * r
            py = y + math.sin(angle) * r * 0.6
            points.append((px, py))
        
        # 阴影
        shadow_points = [(px + 2, py - 2) for px, py in points]
        arcade.draw_polygon_filled(shadow_points, (0, 0, 0, 80))
        
        # 主体
        arcade.draw_polygon_filled(points, color.rgba)
        
        # 高光
        arcade.draw_circle_filled(x - size * 0.2, y + size * 0.2, size * 0.2,
                                  color.lighten(0.25).rgba)
    
    def _draw_bush(self, x: float, y: float, size: float, color_idx: int) -> None:
        """绘制灌木 - 增强版"""
        color = self.BUSH_COLORS[color_idx % len(self.BUSH_COLORS)]
        
        # 阴影
        for i in range(3):
            offset_x = (i - 1) * size * 0.4
            offset_y = abs(i - 1) * size * 0.2
            arcade.draw_circle_filled(x + offset_x + 2, y + offset_y - 2, size * 0.7, (0, 0, 0, 60))
        
        # 多个重叠的圆
        for i in range(3):
            offset_x = (i - 1) * size * 0.4
            offset_y = abs(i - 1) * size * 0.2
            arcade.draw_circle_filled(x + offset_x, y + offset_y, size * 0.7, color.rgba)
        
        # 高光
        arcade.draw_circle_filled(x - size * 0.2, y + size * 0.3, size * 0.3,
                                  color.lighten(0.2).rgba)
    
    def _draw_grass_blade(self, x: float, y: float, size: float) -> None:
        """绘制草叶"""
        # 多根草叶
        for i in range(3):
            offset_x = (i - 1) * 3
            blade_height = size * (0.8 + 0.4 * (i % 2))
            
            # 弯曲的草叶
            points = [
                (x + offset_x, y),
                (x + offset_x - 2, y + blade_height * 0.5),
                (x + offset_x + 1, y + blade_height),
            ]
            
            arcade.draw_polygon_filled(points, PRIMARY.rgba)
    
    def _draw_light_spots(self) -> None:
        """绘制光斑效果 - 增强版"""
        for spot in self.light_spots:
            # 计算闪烁效果
            pulse = 0.5 + 0.5 * math.sin(self._time * spot.speed + spot.angle)
            current_alpha = int(spot.alpha * pulse)
            
            # 确保 alpha 值在有效范围内
            current_alpha = max(0, min(255, current_alpha))
            
            # 绘制多层光斑
            for i in range(3):
                size = spot.size * (1.0 + i * 0.3)
                alpha = int(current_alpha * (0.5 - i * 0.15))
                color = (255, 255, 200, alpha)
                arcade.draw_circle_filled(spot.x, spot.y, size, color)
    
    def update(self, dt: float) -> None:
        """更新背景动画"""
        self._time += dt
        
        # 更新云朵位置
        for cloud in self.clouds:
            cloud.x += cloud.speed * dt
            if cloud.x > self.screen_width + 100:
                cloud.x = -100
    
    def get_cell_center(self, row: int, col: int) -> Tuple[float, float]:
        """获取单元格中心坐标"""
        x = self.start_x + col * self.cell_width + self.cell_width / 2
        y = self.start_y + row * self.cell_height + self.cell_height / 2
        return (x, y)
    
    def get_cell_at_position(self, x: float, y: float) -> Tuple[int, int]:
        """根据屏幕坐标获取单元格行列"""
        col = int((x - self.start_x) // self.cell_width)
        row = int((y - self.start_y) // self.cell_height)
        
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return (row, col)
        return (-1, -1)
    
    def is_in_grid(self, x: float, y: float) -> bool:
        """检查坐标是否在网格内"""
        total_width = self.cols * self.cell_width
        total_height = self.rows * self.cell_height
        
        return (self.start_x <= x < self.start_x + total_width and
                self.start_y <= y < self.start_y + total_height)
    
    def get_grid_bounds(self) -> Tuple[float, float, float, float]:
        """获取网格边界"""
        total_width = self.cols * self.cell_width
        total_height = self.rows * self.cell_height
        return (
            self.start_x,
            self.start_x + total_width,
            self.start_y,
            self.start_y + total_height
        )
    
    def _init_clouds(self) -> None:
        """初始化云朵"""
        for i in range(5):
            cloud = Cloud(
                x=random.uniform(0, self.screen_width),
                y=random.uniform(self.screen_height * 0.6, self.screen_height - 50),
                size=random.uniform(40, 80),
                speed=random.uniform(10, 30),
                opacity=random.uniform(0.3, 0.6)
            )
            self.clouds.append(cloud)
    
    def _init_mountains(self) -> None:
        """初始化山脉"""
        mountain_positions = [
            (0, 120, 200),
            (150, 150, 250),
            (350, 100, 180),
            (500, 140, 220),
            (700, 110, 190),
            (850, 130, 210),
        ]
        
        for x, height, width in mountain_positions:
            color_idx = random.randint(0, len(self.MOUNTAIN_COLORS) - 1)
            mountain = Mountain(
                x=x,
                height=height,
                width=width,
                color=self.MOUNTAIN_COLORS[color_idx].rgba
            )
            self.mountains.append(mountain)
    
    def _draw_sky_gradient(self) -> None:
        """绘制天空渐变"""
        # 从上到下绘制渐变
        gradient_steps = 20
        for i in range(gradient_steps):
            y_bottom = self.screen_height - (i / gradient_steps) * self.screen_height
            y_top = self.screen_height - ((i + 1) / gradient_steps) * self.screen_height
            
            t = i / (gradient_steps - 1)
            r = int(self.SKY_TOP.r + (self.SKY_BOTTOM.r - self.SKY_TOP.r) * t)
            g = int(self.SKY_TOP.g + (self.SKY_BOTTOM.g - self.SKY_TOP.g) * t)
            b = int(self.SKY_TOP.b + (self.SKY_BOTTOM.b - self.SKY_TOP.b) * t)
            
            arcade.draw_lrbt_rectangle_filled(
                0, self.screen_width,
                y_top, y_bottom,
                (r, g, b)
            )
    
    def _draw_mountains(self) -> None:
        """绘制山脉"""
        for mountain in self.mountains:
            # 绘制三角形山脉
            points = [
                (mountain.x, self.start_y + self.rows * self.cell_height + 20),
                (mountain.x + mountain.width / 2, 
                 self.start_y + self.rows * self.cell_height + 20 + mountain.height),
                (mountain.x + mountain.width, 
                 self.start_y + self.rows * self.cell_height + 20),
            ]
            arcade.draw_polygon_filled(points, mountain.color)
            
            # 山顶积雪效果
            snow_points = [
                (mountain.x + mountain.width * 0.35, 
                 self.start_y + self.rows * self.cell_height + 20 + mountain.height * 0.7),
                (mountain.x + mountain.width / 2, 
                 self.start_y + self.rows * self.cell_height + 20 + mountain.height),
                (mountain.x + mountain.width * 0.65, 
                 self.start_y + self.rows * self.cell_height + 20 + mountain.height * 0.7),
            ]
            arcade.draw_polygon_filled(snow_points, WHITE.with_alpha(150).rgba)
    
    def _draw_clouds(self) -> None:
        """绘制云朵"""
        for cloud in self.clouds:
            alpha = int(255 * cloud.opacity)
            color = (255, 255, 255, alpha)
            
            # 绘制云朵（多个重叠的圆）
            offsets = [
                (0, 0),
                (-cloud.size * 0.4, -cloud.size * 0.2),
                (cloud.size * 0.4, -cloud.size * 0.2),
                (-cloud.size * 0.2, cloud.size * 0.2),
                (cloud.size * 0.2, cloud.size * 0.2),
            ]
            
            for ox, oy in offsets:
                arcade.draw_circle_filled(
                    cloud.x + ox, cloud.y + oy,
                    cloud.size * 0.5,
                    color
                )
