
"""
3D效果渲染器 - 为2D精灵添加伪3D视觉效果

包括：
- 阴影效果（柔和的底部阴影）
- 高光效果（顶部高光增加立体感）
- 透视缩放（根据Y位置调整大小）
- 浮动动画效果
- 边缘高亮
"""

import math
from typing import Tuple, Optional
import arcade


class ThreeDEffects:
    """
    3D效果渲染器
    
    为精灵添加多种伪3D视觉效果
    """
    
    def __init__(self):
        self._time = 0.0
        self._float_amplitude = 3.0
        self._float_speed = 2.0
        self._shadow_offset = (0, -8)
        self._shadow_scale = 0.9
        self._shadow_alpha = 120
        self._highlight_alpha = 80
        self._edge_highlight_alpha = 60
    
    def update(self, dt: float):
        self._time += dt
    
    def get_float_offset(self, entity_id: int, base_y: float) -> float:
        phase = (entity_id * 0.1234) % (2 * math.pi)
        return math.sin(self._time * self._float_speed + phase) * self._float_amplitude
    
    def get_perspective_scale(self, y: float, screen_height: float = 600) -> float:
        normalized_y = y / screen_height
        return 0.95 + normalized_y * 0.1
    
    def draw_shadow(self, x: float, y: float, width: float, height: float, 
                   alpha: Optional[int] = None):
        shadow_alpha = alpha if alpha is not None else self._shadow_alpha
        shadow_x = x + self._shadow_offset[0]
        shadow_y = y + self._shadow_offset[1]
        shadow_width = width * self._shadow_scale
        shadow_height = height * 0.4
        
        self._draw_soft_ellipse(
            shadow_x, shadow_y,
            shadow_width, shadow_height,
            (0, 0, 0, shadow_alpha)
        )
    
    def _draw_soft_ellipse(self, x: float, y: float, width: float, height: float,
                           color: Tuple[int, int, int, int]):
        r, g, b, a = color
        
        for i in range(3):
            scale = 1.0 + i * 0.2
            alpha = max(0, a - i * 30)
            if alpha <= 0:
                continue
            
            arcade.draw_ellipse_filled(
                x, y,
                width * scale, height * scale,
                (r, g, b, alpha)
            )
    
    def draw_highlight(self, x: float, y: float, width: float, height: float,
                      alpha: Optional[int] = None):
        highlight_alpha = alpha if alpha is not None else self._highlight_alpha
        highlight_y = y + height * 0.25
        highlight_width = width * 0.6
        highlight_height = height * 0.3
        
        arcade.draw_ellipse_filled(
            x, highlight_y,
            highlight_width, highlight_height,
            (255, 255, 255, highlight_alpha)
        )
    
    def draw_edge_highlight(self, x: float, y: float, width: float, height: float,
                           alpha: Optional[int] = None):
        edge_alpha = alpha if alpha is not None else self._edge_highlight_alpha
        
        half_width = width / 2
        half_height = height / 2
        
        points = [
            (x - half_width, y + half_height),
            (x - half_width + 3, y + half_height - 3),
            (x - half_width + 3, y - half_height + 3),
            (x - half_width, y - half_height),
        ]
        arcade.draw_polygon_filled(points, (255, 255, 255, edge_alpha))
        
        points = [
            (x - half_width, y + half_height),
            (x + half_width, y + half_height),
            (x + half_width - 3, y + half_height - 3),
            (x - half_width + 3, y + half_height - 3),
        ]
        arcade.draw_polygon_filled(points, (255, 255, 255, edge_alpha // 2))
    
    def draw_3d_effects(self, entity_id: int, x: float, y: float, 
                        width: float, height: float,
                        screen_height: float = 600,
                        enable_shadow: bool = True,
                        enable_highlight: bool = True,
                        enable_edge: bool = False,
                        enable_float: bool = True) -> Tuple[float, float, float]:
        float_offset = self.get_float_offset(entity_id, y) if enable_float else 0.0
        scale = self.get_perspective_scale(y, screen_height)
        
        adjusted_y = y + float_offset
        adjusted_width = width * scale
        adjusted_height = height * scale
        
        if enable_shadow:
            self.draw_shadow(x, adjusted_y, adjusted_width, adjusted_height)
        
        return (x, adjusted_y, scale)
    
    def apply_post_effects(self, entity_id: int, x: float, y: float,
                          width: float, height: float,
                          enable_highlight: bool = True,
                          enable_edge: bool = False):
        if enable_highlight:
            self.draw_highlight(x, y, width, height)
        
        if enable_edge:
            self.draw_edge_highlight(x, y, width, height)
