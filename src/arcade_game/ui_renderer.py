"""
UI渲染器 - 增强的游戏UI显示效果

包括：
- 阳光计数器（带图标、跳动动画、发光效果）
- 波次提示（警告动画、进度条、闪烁效果）
- 分数显示（带动画效果）
- 植物卡片（带真实精灵图片）
- 游戏结束界面（增强版）
"""

import math
import random
import os
from typing import Tuple, List, Optional
from dataclasses import dataclass, field
import arcade

from .sprite_manager import get_sprite_manager
from ..core.theme_colors import (
    Color, GameColors, StatusColors, UIColors, EffectColors,
    PRIMARY, SECONDARY, SECONDARY_DARK, ACCENT, WHITE, BLACK
)


@dataclass
class AnimatedValue:
    """动画数值"""
    current: float = 0.0
    target: float = 0.0
    velocity: float = 0.0
    
    def update(self, dt: float, spring: float = 0.3, damping: float = 0.7) -> None:
        """使用弹簧动画更新"""
        diff = self.target - self.current
        self.velocity += diff * spring
        self.velocity *= damping
        self.current += self.velocity
    
    def set_target(self, value: float) -> None:
        """设置目标值"""
        self.target = value


@dataclass
class SunCounterState:
    """阳光计数器状态"""
    sun_count: int = 0
    display_count: float = 0.0
    bounce_offset: float = 0.0
    glow_intensity: float = 0.0
    pulse_timer: float = 0.0
    prev_count: int = 0
    rotation: float = 0.0


@dataclass
class WaveIndicatorState:
    """波次指示器状态"""
    current_wave: int = 1
    total_waves: int = 10
    warning_timer: float = 0.0
    warning_active: bool = False
    flash_intensity: float = 0.0
    progress: float = 0.0
    pulse_phase: float = 0.0


@dataclass
class FloatingText:
    """浮动文字"""
    x: float
    y: float
    text: str
    color: Tuple[int, int, int, int]
    life: float
    max_life: float
    vy: float = -30.0
    scale: float = 1.0
    
    def update(self, dt: float) -> None:
        """更新浮动文字"""
        self.life -= dt
        self.y += self.vy * dt
        self.scale = 1.0 + (1.0 - self.life / self.max_life) * 0.3
    
    @property
    def is_alive(self) -> bool:
        return self.life > 0
    
    @property
    def alpha(self) -> int:
        return int(255 * (self.life / self.max_life))


class UIRenderer:
    """
    增强的UI渲染器
    
    提供类似原游戏的UI效果，使用Material Design配色
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # 阳光计数器状态
        self.sun_state = SunCounterState()
        
        # 波次指示器状态
        self.wave_state = WaveIndicatorState()
        
        # 浮动文字列表
        self.floating_texts: List[FloatingText] = []
        
        # 动画数值
        self.score_display = AnimatedValue()
        
        # 时间累积
        self._time_accumulator = 0.0
        
        # 文字缓存 - 使用 arcade.Text 对象避免每帧重新创建
        self._init_text_cache()
    
    def update(self, dt: float) -> None:
        """更新UI状态"""
        self._time_accumulator += dt
        
        # 更新阳光计数器动画
        self._update_sun_counter(dt)
        
        # 更新波次指示器
        self._update_wave_indicator(dt)
        
        # 更新浮动文字
        self._update_floating_texts(dt)
        
        # 更新分数显示
        self.score_display.update(dt)
    
    def _update_sun_counter(self, dt: float) -> None:
        """更新阳光计数器动画"""
        state = self.sun_state
        
        # 数字跳动动画
        if state.sun_count != state.prev_count:
            state.bounce_offset = 15.0
            state.glow_intensity = 1.0
            state.prev_count = state.sun_count
        
        # 弹跳衰减
        state.bounce_offset *= 0.85
        if state.bounce_offset < 0.1:
            state.bounce_offset = 0.0
        
        # 发光衰减
        state.glow_intensity *= 0.92
        if state.glow_intensity < 0.01:
            state.glow_intensity = 0.0
        
        # 脉冲动画
        state.pulse_timer += dt * 3.0
        
        # 旋转动画
        state.rotation += dt * 30.0
        
        # 显示数值平滑过渡
        diff = state.sun_count - state.display_count
        state.display_count += diff * 0.15
    
    def _update_wave_indicator(self, dt: float) -> None:
        """更新波次指示器动画"""
        state = self.wave_state
        
        state.pulse_phase += dt * 2.0
        
        if state.warning_active:
            state.warning_timer += dt
            state.flash_intensity = 0.5 + 0.5 * math.sin(state.warning_timer * 10)
        else:
            state.flash_intensity *= 0.9
    
    def _update_floating_texts(self, dt: float) -> None:
        """更新浮动文字"""
        for text in self.floating_texts:
            text.update(dt)
        
        self.floating_texts = [t for t in self.floating_texts if t.is_alive]
    
    def _init_text_cache(self) -> None:
        """初始化文字缓存对象"""
        # 阳光数量文字
        self._sun_text = arcade.Text(
            "0", 0, 0,
            GameColors.SUN_TEXT.rgba, 22,
            font_name=("Arial", "Microsoft YaHei", "sans-serif"),
            bold=True
        )
        
        # 波次文字
        self._wave_text = arcade.Text(
            "", 0, 0,
            StatusColors.WAVE_NORMAL.rgba, 20,
            font_name=("Arial", "Microsoft YaHei", "sans-serif")
        )
        
        # 分数文字
        self._score_text = arcade.Text(
            "", 0, 0,
            WHITE.rgba, 18,
            font_name=("Arial", "Microsoft YaHei", "sans-serif")
        )
        
        # 游戏结束文字
        self._game_over_title = arcade.Text(
            "", 0, 0,
            SECONDARY.rgba, 48,
            anchor_x="center",
            font_name=("Arial", "Microsoft YaHei", "sans-serif"),
            bold=True
        )
        
        self._game_over_hint = arcade.Text(
            "", 0, 0,
            WHITE.rgba, 20,
            anchor_x="center",
            font_name=("Arial", "Microsoft YaHei", "sans-serif")
        )
    
    def set_sun_count(self, count: int) -> None:
        """设置阳光数量"""
        self.sun_state.sun_count = count
    
    def set_wave_info(self, current: int, total: int, progress: float = 0.0) -> None:
        """设置波次信息"""
        self.wave_state.current_wave = current
        self.wave_state.total_waves = total
        self.wave_state.progress = progress
    
    def trigger_wave_warning(self) -> None:
        """触发波次警告"""
        self.wave_state.warning_active = True
        self.wave_state.warning_timer = 0.0
    
    def stop_wave_warning(self) -> None:
        """停止波次警告"""
        self.wave_state.warning_active = False
    
    def add_floating_text(self, x: float, y: float, text: str, 
                         color: Tuple[int, int, int] = (255, 255, 255),
                         life: float = 1.5) -> None:
        """添加浮动文字"""
        self.floating_texts.append(FloatingText(
            x=x, y=y, text=text,
            color=(*color, 255),
            life=life, max_life=life
        ))
    
    def set_score(self, score: int) -> None:
        """设置分数"""
        self.score_display.set_target(float(score))
    
    def render(self) -> None:
        """渲染所有UI"""
        self._render_sun_counter()
        self._render_wave_indicator()
        self._render_score()
        self._render_floating_texts()
    
    def _render_sun_counter(self) -> None:
        """渲染阳光计数器 - 增强版"""
        state = self.sun_state
        base_x = 20
        base_y = self.screen_height - 55
        
        # 计算动画偏移
        bounce = state.bounce_offset
        pulse = math.sin(state.pulse_timer) * 3.0
        
        # 绘制多层发光效果
        if state.glow_intensity > 0:
            # 外层光晕
            for i in range(4):
                radius = 40 + i * 8 + state.glow_intensity * 10
                alpha = int((40 - i * 8) * state.glow_intensity)
                if alpha > 0:
                    arcade.draw_circle_filled(
                        base_x + 30, base_y + 10,
                        radius, GameColors.SUN_GLOW.with_alpha(alpha).rgba
                    )
        
        # 绘制阳光图标外圈
        arcade.draw_circle_filled(
            base_x + 30, base_y + 10 + bounce * 0.3,
            32, GameColors.SUN_GLOW.darken(0.3).rgba
        )
        
        # 绘制阳光图标主体
        arcade.draw_circle_filled(
            base_x + 30, base_y + 10 + bounce * 0.3,
            28, GameColors.SUN_CORE.rgba
        )
        
        # 绘制内部高光
        arcade.draw_circle_filled(
            base_x + 25, base_y + 15 + bounce * 0.3,
            15, GameColors.SUN_RAY.with_alpha(200).rgba
        )
        
        # 绘制旋转光芒
        self._draw_sun_rays(
            base_x + 30, base_y + 10 + bounce * 0.3, 
            28 + pulse * 0.5, state.rotation
        )
        
        # 绘制阳光数量背景 - 圆角矩形效果
        bg_width = 110
        bg_height = 36
        bg_x = base_x + 65
        bg_y = base_y - 8
        
        # 背景阴影
        arcade.draw_lrbt_rectangle_filled(
            bg_x + 3, bg_x + bg_width + 3,
            bg_y - 3, bg_y + bg_height - 3,
            (0, 0, 0, 60)
        )
        
        # 主背景
        arcade.draw_lrbt_rectangle_filled(
            bg_x, bg_x + bg_width,
            bg_y, bg_y + bg_height,
            UIColors.BG_DARK.with_alpha(200).rgba
        )
        
        # 渐变边框效果
        arcade.draw_lrbt_rectangle_outline(
            bg_x, bg_x + bg_width,
            bg_y, bg_y + bg_height,
            GameColors.SUN_GLOW.with_alpha(150).rgba, 2
        )
        
        # 内部高光边框
        arcade.draw_lrbt_rectangle_outline(
            bg_x + 2, bg_x + bg_width - 2,
            bg_y + 2, bg_y + bg_height - 2,
            GameColors.SUN_RAY.with_alpha(50).rgba, 1
        )
        
        # 绘制阳光数量（带跳动效果）
        display_count = int(state.display_count)
        scale = 1.0 + bounce * 0.015
        text_y = base_y + 10 + bounce * 0.5
        
        # 使用缓存的Text对象（性能优化）
        self._sun_text.text = str(display_count)
        self._sun_text.font_size = int(22 * scale)
        self._sun_text.x = bg_x + 10
        self._sun_text.y = text_y
        
        # 文字阴影（简化，只绘制主文字以提高性能）
        self._sun_text.draw()
    
    def _draw_sun_rays(self, x: float, y: float, radius: float, rotation: float) -> None:
        """绘制阳光光芒"""
        ray_count = 12
        for i in range(ray_count):
            angle = math.radians(i * (360 / ray_count) + rotation)
            
            inner_r = radius * 1.1
            outer_r = radius * 1.6
            
            x1 = x + math.cos(angle) * inner_r
            y1 = y + math.sin(angle) * inner_r
            x2 = x + math.cos(angle) * outer_r
            y2 = y + math.sin(angle) * outer_r
            
            # 光芒渐变效果
            arcade.draw_line(x1, y1, x2, y2, GameColors.SUN_RAY.with_alpha(200).rgba, 3)
            arcade.draw_line(x1, y1, (x1+x2)/2, (y1+y2)/2, GameColors.SUN_CORE.with_alpha(255).rgba, 4)
    
    def _render_wave_indicator(self) -> None:
        """渲染波次指示器 - 增强版"""
        state = self.wave_state
        base_x = self.screen_width - 200
        base_y = self.screen_height - 45
        
        # 确定颜色
        if state.warning_active:
            color = self._interpolate_color(
                StatusColors.WAVE_NORMAL.rgba, 
                StatusColors.WAVE_WARNING.rgba, 
                state.flash_intensity
            )
            bg_color = StatusColors.ERROR.with_alpha(40).rgba
        else:
            color = StatusColors.WAVE_NORMAL.rgba
            bg_color = UIColors.BG_DARK.with_alpha(180).rgba
        
        # 绘制背景
        bg_width = 190
        bg_height = 60
        
        # 背景阴影
        arcade.draw_lrbt_rectangle_filled(
            base_x + 3, base_x + bg_width + 3,
            base_y - 28, base_y + bg_height - 28,
            (0, 0, 0, 60)
        )
        
        # 主背景
        arcade.draw_lrbt_rectangle_filled(
            base_x - 5, base_x + bg_width,
            base_y - 25, base_y + bg_height - 25,
            bg_color
        )
        
        # 绘制边框（警告时闪烁）
        if state.warning_active:
            border_color = StatusColors.WARNING.rgba
            border_width = 3
            # 脉冲效果
            pulse = 0.5 + 0.5 * math.sin(state.pulse_phase * 3)
            glow_alpha = int(100 * pulse)
            arcade.draw_lrbt_rectangle_filled(
                base_x - 8, base_x + bg_width + 3,
                base_y - 28, base_y + bg_height - 22,
                StatusColors.WARNING.with_alpha(glow_alpha).rgba
            )
        else:
            border_color = UIColors.BORDER.rgba
            border_width = 2
        
        arcade.draw_lrbt_rectangle_outline(
            base_x - 5, base_x + bg_width,
            base_y - 25, base_y + bg_height - 25,
            border_color, border_width
        )
        
        # 绘制波次文字
        wave_text = f"波次: {state.current_wave}/{state.total_waves}"
        
        # 文字阴影
        arcade.draw_text(
            wave_text, base_x + 2, base_y + 2,
            (0, 0, 0, 150), 20,
            font_name=("Arial", "Microsoft YaHei", "sans-serif"),
            bold=state.warning_active
        )
        
        # 主文字
        arcade.draw_text(
            wave_text, base_x, base_y,
            color, 20,
            font_name=("Arial", "Microsoft YaHei", "sans-serif"),
            bold=state.warning_active
        )
        
        # 绘制进度条 - 增强版
        progress_width = 170
        progress_height = 10
        progress_x = base_x + 5
        progress_y = base_y - 22
        
        # 进度条背景（带圆角效果）
        arcade.draw_lrbt_rectangle_filled(
            progress_x, progress_x + progress_width,
            progress_y, progress_y + progress_height,
            UIColors.BG_MEDIUM.with_alpha(200).rgba
        )
        
        # 进度条前景 - 渐变效果
        if state.progress > 0:
            fg_width = progress_width * state.progress
            
            # 进度颜色根据完成度变化
            if state.progress < 0.3:
                progress_color = StatusColors.HEALTH_HIGH.rgba
            elif state.progress < 0.7:
                progress_color = StatusColors.HEALTH_MEDIUM.rgba
            else:
                progress_color = StatusColors.WARNING.rgba
            
            arcade.draw_lrbt_rectangle_filled(
                progress_x, progress_x + fg_width,
                progress_y, progress_y + progress_height,
                progress_color
            )
            
            # 进度条高光
            arcade.draw_lrbt_rectangle_filled(
                progress_x, progress_x + fg_width,
                progress_y + progress_height - 3, progress_y + progress_height,
                WHITE.with_alpha(100).rgba
            )
        
        # 进度条边框
        arcade.draw_lrbt_rectangle_outline(
            progress_x, progress_x + progress_width,
            progress_y, progress_y + progress_height,
            UIColors.BORDER.rgba, 1
        )
        
        # 警告时绘制警告图标
        if state.warning_active:
            self._draw_warning_icon(base_x + bg_width - 25, base_y + 5, state.flash_intensity)
    
    def _draw_warning_icon(self, x: float, y: float, intensity: float) -> None:
        """绘制警告图标 - 增强版"""
        size = 14 + intensity * 4
        
        # 外发光
        glow_size = size + 5
        arcade.draw_circle_filled(x, y, glow_size, StatusColors.WARNING.with_alpha(int(100 * intensity)).rgba)
        
        # 三角形警告图标
        points = [
            (x, y + size),
            (x - size * 0.85, y - size * 0.5),
            (x + size * 0.85, y - size * 0.5),
        ]
        
        arcade.draw_polygon_filled(points, StatusColors.WARNING.rgba)
        
        # 内部高光
        inner_points = [
            (x, y + size * 0.7),
            (x - size * 0.5, y - size * 0.3),
            (x + size * 0.5, y - size * 0.3),
        ]
        arcade.draw_polygon_filled(inner_points, StatusColors.WARNING.lighten(0.3).rgba)
        
        # 感叹号
        arcade.draw_text("!", x - 3, y - 6, BLACK.rgba, 16, bold=True)
    
    def _render_score(self) -> None:
        """渲染分数 - 增强版"""
        base_x = 20
        base_y = self.screen_height - 100
        
        # 分数图标背景
        arcade.draw_circle_filled(base_x + 15, base_y + 12, 16, SECONDARY_DARK.rgba)
        
        # 绘制星星图标
        self._draw_star(base_x + 15, base_y + 12, 12, SECONDARY.rgba)
        
        # 分数文字阴影
        display_score = int(self.score_display.current)
        arcade.draw_text(
            f"分数: {display_score}",
            base_x + 37, base_y + 2,
            (0, 0, 0, 150), 18,
            font_name=("Arial", "Microsoft YaHei", "sans-serif")
        )
        
        # 分数文字
        arcade.draw_text(
            f"分数: {display_score}",
            base_x + 35, base_y,
            WHITE.rgba, 18,
            font_name=("Arial", "Microsoft YaHei", "sans-serif")
        )
    
    def _draw_star(self, x: float, y: float, size: float, color: Tuple[int, ...]) -> None:
        """绘制星星"""
        points = []
        rotation = self._time_accumulator * 30
        for i in range(5):
            # 外顶点
            angle = math.radians(i * 72 - 90 + rotation)
            points.append((
                x + math.cos(angle) * size,
                y + math.sin(angle) * size
            ))
            # 内顶点
            angle = math.radians(i * 72 + 36 - 90 + rotation)
            points.append((
                x + math.cos(angle) * size * 0.4,
                y + math.sin(angle) * size * 0.4
            ))
        
        arcade.draw_polygon_filled(points, color)
    
    def _render_floating_texts(self) -> None:
        """渲染浮动文字 - 增强版"""
        for text in self.floating_texts:
            alpha = text.alpha
            color = (text.color[0], text.color[1], text.color[2], alpha)
            
            # 绘制发光效果
            if text.scale > 1.1:
                glow_alpha = int((text.scale - 1.0) * 200)
                arcade.draw_text(
                    text.text, text.x, text.y,
                    (text.color[0], text.color[1], text.color[2], glow_alpha),
                    int(16 * text.scale * 1.2),
                    font_name=("Arial", "Microsoft YaHei", "sans-serif"),
                    bold=True
                )
            
            # 绘制阴影
            arcade.draw_text(
                text.text, text.x + 2, text.y - 2,
                (0, 0, 0, alpha // 2),
                int(16 * text.scale),
                font_name=("Arial", "Microsoft YaHei", "sans-serif"),
                bold=True
            )
            
            # 绘制文字
            arcade.draw_text(
                text.text, text.x, text.y,
                color,
                int(16 * text.scale),
                font_name=("Arial", "Microsoft YaHei", "sans-serif"),
                bold=True
            )
    
    def _interpolate_color(self, color1: Tuple[int, ...], color2: Tuple[int, ...], t: float) -> Tuple[int, ...]:
        """插值颜色"""
        return tuple(int(c1 + (c2 - c1) * t) for c1, c2 in zip(color1, color2))


class PlantCardRenderer:
    """
    植物卡片渲染器 - 增强版
    
    提供类似原游戏的植物卡片效果
    """
    
    # 卡片尺寸
    CARD_WIDTH = 55
    CARD_HEIGHT = 75
    
    def __init__(self):
        self.hover_card: Optional[str] = None
        self.card_animations: dict = {}
        self.sprite_manager = get_sprite_manager()
        self._load_plant_card_textures()
    
    def _load_plant_card_textures(self) -> None:
        """加载植物卡片纹理"""
        # 植物类型到文件名的映射
        plant_files = {
            'peashooter': 'peashooter.png',
            'sunflower': 'sunflower.png',
            'wallnut': 'wallnut.png',
            'cherrybomb': 'cherry_bomb.png',
            'snowpea': 'snow_pea.png',
            'repeater': 'repeater.png',
            'chomper': 'chomper.png',
            'potatomine': 'potato_mine.png',
        }
        
        # 获取植物精灵图目录
        plants_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'assets', 'sprites', 'plants'
        )
        
        # 加载每个植物的纹理
        for plant_type, filename in plant_files.items():
            texture_path = os.path.join(plants_dir, filename)
            if os.path.exists(texture_path):
                try:
                    self.sprite_manager.load_texture(f"card_{plant_type}", texture_path)
                except Exception as e:
                    print(f"加载植物卡片纹理失败 {plant_type}: {e}")
    
    def update(self, dt: float) -> None:
        """更新卡片动画"""
        for card_id, anim in list(self.card_animations.items()):
            if 'scale' in anim:
                anim['scale'] = max(1.0, anim['scale'] - dt * 2)
            if 'glow' in anim:
                anim['glow'] = max(0, anim['glow'] - dt * 3)
    
    def set_hover(self, card_id: Optional[str]) -> None:
        """设置悬停卡片"""
        self.hover_card = card_id
    
    def trigger_plant_animation(self, card_id: str) -> None:
        """触发种植动画"""
        self.card_animations[card_id] = {
            'scale': 1.3,
            'glow': 1.0
        }
    
    def render_card(self, x: float, y: float, plant_type: str,
                   sun_cost: int, cooldown_progress: float,
                   is_affordable: bool, is_selected: bool = False) -> None:
        """
        渲染单个植物卡片 - 增强版
        """
        # 获取动画状态
        anim = self.card_animations.get(plant_type, {})
        scale = anim.get('scale', 1.0)
        glow = anim.get('glow', 0.0)
        
        is_hover = self.hover_card == plant_type
        
        # 计算卡片尺寸
        width = self.CARD_WIDTH * scale
        height = self.CARD_HEIGHT * scale
        offset_x = (width - self.CARD_WIDTH) / 2
        offset_y = (height - self.CARD_HEIGHT) / 2
        
        card_x = x - offset_x
        card_y = y - offset_y
        
        # 绘制发光效果
        if glow > 0 or is_selected:
            glow_intensity = max(glow, 0.5 if is_selected else 0)
            glow_color = SECONDARY_LIGHT.with_alpha(int(100 * glow_intensity))
            arcade.draw_lrbt_rectangle_filled(
                card_x - 6, card_x + width + 6,
                card_y - 6, card_y + height + 6,
                glow_color.rgba
            )
        
        # 确定背景颜色
        if not is_affordable:
            bg_color = UIColors.BG_DARK.with_alpha(180)
        elif is_hover or is_selected:
            bg_color = UIColors.SURFACE_ELEVATED
        else:
            bg_color = UIColors.SURFACE
        
        # 绘制卡片背景 - 带阴影
        arcade.draw_lrbt_rectangle_filled(
            card_x + 2, card_x + width + 2,
            card_y - 2, card_y + height - 2,
            (0, 0, 0, 60)
        )
        
        # 主背景
        arcade.draw_lrbt_rectangle_filled(
            card_x, card_x + width,
            card_y, card_y + height,
            bg_color.rgba
        )
        
        # 绘制边框
        if is_selected:
            border_color = SECONDARY
            border_width = 3
            # 选中时添加外发光
            arcade.draw_lrbt_rectangle_filled(
                card_x - 3, card_x + width + 3,
                card_y - 3, card_y + height + 3,
                SECONDARY.with_alpha(80).rgba
            )
        elif is_hover:
            border_color = UIColors.BORDER_HIGHLIGHT
            border_width = 2
        else:
            border_color = UIColors.BORDER
            border_width = 1
        
        arcade.draw_lrbt_rectangle_outline(
            card_x, card_x + width,
            card_y, card_y + height,
            border_color.rgba, border_width
        )
        
        # 绘制植物图标区域
        icon_y = card_y + height * 0.45
        self._draw_plant_icon(card_x + width / 2, icon_y, plant_type, scale)
        
        # 绘制阳光消耗背景
        cost_bg_height = 18
        arcade.draw_lrbt_rectangle_filled(
            card_x + 2, card_x + width - 2,
            card_y + 2, card_y + cost_bg_height,
            UIColors.BG_DARK.with_alpha(150).rgba
        )
        
        # 绘制阳光消耗
        cost_y = card_y + 6
        cost_color = GameColors.SUN_CORE if is_affordable else UIColors.TEXT_DISABLED
        
        # 小太阳图标
        arcade.draw_circle_filled(
            card_x + 10, cost_y + 4, 4, GameColors.SUN_GLOW.rgba
        )
        
        # 消耗数值
        arcade.draw_text(
            str(sun_cost),
            card_x + 18, cost_y,
            cost_color.rgba,
            int(11 * scale),
            font_name=("Arial", "Microsoft YaHei", "sans-serif"),
            bold=True
        )
        
        # 绘制冷却遮罩
        if cooldown_progress < 1.0:
            mask_height = (height - cost_bg_height - 4) * (1.0 - cooldown_progress)
            arcade.draw_lrbt_rectangle_filled(
                card_x, card_x + width,
                card_y + height - mask_height - cost_bg_height - 2, card_y + height - cost_bg_height - 2,
                (0, 0, 0, 180)
            )
            
            # 绘制冷却进度条
            progress_width = (width - 4) * cooldown_progress
            arcade.draw_lrbt_rectangle_filled(
                card_x + 2, card_x + 2 + progress_width,
                card_y + cost_bg_height + 1, card_y + cost_bg_height + 4,
                StatusColors.HEALTH_HIGH.rgba
            )
    
    def _draw_plant_icon(self, x: float, y: float, plant_type: str, scale: float) -> None:
        """绘制植物图标（优先使用真实精灵图片）"""
        # 尝试获取真实纹理
        # 首先尝试使用具体的植物名称
        texture = self.sprite_manager.get_texture(f"{plant_type}_idle")
        if not texture:
            # 如果没有找到特定的idle纹理，则尝试其他可能的命名
            texture = self.sprite_manager.get_texture(f"{plant_type}_idle_sheet")
        if not texture:
            texture = self.sprite_manager.get_texture(f"{plant_type}")
        if not texture:
            # 尝试使用card_前缀（原有逻辑）
            texture = self.sprite_manager.get_texture(f"card_{plant_type}")
        
        if texture:
            # 使用真实精灵图片
            size = 40 * scale  # 卡片内图标大小
            rect = arcade.XYWH(x, y, size, size)
            arcade.draw_texture_rect(texture, rect)
        else:
            # 回退到彩色圆形（纹理加载失败时）
            size = 18 * scale
            
            # 根据植物类型绘制不同颜色的图标
            colors = {
                'peashooter': GameColors.PLANT_PEASHOOTER,
                'sunflower': GameColors.PLANT_SUNFLOWER,
                'wallnut': GameColors.PLANT_WALLNUT,
                'cherrybomb': GameColors.PLANT_CHERRY,
                'snowpea': GameColors.PLANT_SNOWPEA,
                'repeater': GameColors.PLANT_REPEATER,
                'chomper': GameColors.PLANT_CHOMPER,
                'potatomine': GameColors.PLANT_POTATO,
            }
            
            color = colors.get(plant_type, PRIMARY)
            
            # 绘制简化的植物形状
            arcade.draw_circle_filled(x, y, size, color.rgba)
            
            # 添加高光
            arcade.draw_circle_filled(
                x - size * 0.3, y + size * 0.3, size * 0.3, 
                color.lighten(0.4).rgba
            )


class GameOverRenderer:
    """
    游戏结束界面渲染器 - 增强版
    
    提供美观的游戏结束/胜利界面
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.animation_time = 0.0
        self.is_victory = False
        self.final_score = 0
        self.waves_completed = 0
    
    def show(self, is_victory: bool, score: int = 0, waves: int = 0) -> None:
        """显示游戏结束界面"""
        self.is_victory = is_victory
        self.final_score = score
        self.waves_completed = waves
        self.animation_time = 0.0
    
    def update(self, dt: float) -> None:
        """更新动画"""
        self.animation_time += dt
    
    def render(self) -> None:
        """渲染游戏结束界面"""
        t = min(1.0, self.animation_time * 2.0)  # 入场动画进度
        
        # 背景遮罩 - 渐变出现
        overlay_alpha = int(180 * t)
        arcade.draw_lrbt_rectangle_filled(
            0, self.screen_width,
            0, self.screen_height,
            (0, 0, 0, overlay_alpha)
        )
        
        center_x = self.screen_width / 2
        center_y = self.screen_height / 2
        
        # 主面板 - 从上方滑入
        panel_offset = (1.0 - t) * 100
        panel_y = center_y + panel_offset
        
        panel_width = 400
        panel_height = 300
        panel_x = center_x - panel_width / 2
        panel_bottom = panel_y - panel_height / 2
        
        # 面板阴影
        arcade.draw_lrbt_rectangle_filled(
            panel_x + 8, panel_x + panel_width + 8,
            panel_bottom - 8, panel_bottom + panel_height - 8,
            (0, 0, 0, 100)
        )
        
        # 面板背景 - 根据胜负改变颜色
        if self.is_victory:
            bg_color = PRIMARY_DARK.with_alpha(240)
            accent_color = SECONDARY
        else:
            bg_color = Color(60, 30, 30, 240)
            accent_color = StatusColors.ERROR
        
        arcade.draw_lrbt_rectangle_filled(
            panel_x, panel_x + panel_width,
            panel_bottom, panel_bottom + panel_height,
            bg_color.rgba
        )
        
        # 面板边框
        arcade.draw_lrbt_rectangle_outline(
            panel_x, panel_x + panel_width,
            panel_bottom, panel_bottom + panel_height,
            accent_color.rgba, 3
        )
        
        # 内部装饰线
        arcade.draw_lrbt_rectangle_outline(
            panel_x + 10, panel_x + panel_width - 10,
            panel_bottom + 10, panel_bottom + panel_height - 10,
            accent_color.with_alpha(100).rgba, 1
        )
        
        # 标题文字 - 带发光效果
        title_text = "胜利!" if self.is_victory else "游戏结束"
        title_color = SECONDARY if self.is_victory else StatusColors.ERROR
        
        # 标题发光
        for i in range(3):
            glow_alpha = int(50 * (3 - i) * t)
            arcade.draw_text(
                title_text,
                center_x, panel_bottom + panel_height - 70 + i * 2,
                title_color.with_alpha(glow_alpha).rgba,
                int(48 + i * 4),
                anchor_x="center",
                font_name=("Arial", "Microsoft YaHei", "sans-serif"),
                bold=True
            )
        
        # 主标题
        title_scale = 1.0 + math.sin(self.animation_time * 3.0) * 0.02
        arcade.draw_text(
            title_text,
            center_x, panel_bottom + panel_height - 70,
            title_color.rgba,
            int(48 * title_scale),
            anchor_x="center",
            font_name=("Arial", "Microsoft YaHei", "sans-serif"),
            bold=True
        )
        
        # 统计信息
        info_y = panel_bottom + panel_height - 130
        
        # 分数
        arcade.draw_text(
            f"最终分数: {self.final_score}",
            center_x, info_y,
            WHITE.rgba, 24,
            anchor_x="center",
            font_name=("Arial", "Microsoft YaHei", "sans-serif")
        )
        
        # 波次
        arcade.draw_text(
            f"完成波次: {self.waves_completed}",
            center_x, info_y - 40,
            WHITE.rgba, 20,
            anchor_x="center",
            font_name=("Arial", "Microsoft YaHei", "sans-serif")
        )
        
        # 提示文字 - 闪烁效果
        blink = 0.7 + 0.3 * math.sin(self.animation_time * 4.0)
        hint_alpha = int(255 * blink)
        
        arcade.draw_text(
            "按 R 返回菜单",
            center_x, panel_bottom + 50,
            WHITE.with_alpha(hint_alpha).rgba,
            20,
            anchor_x="center",
            font_name=("Arial", "Microsoft YaHei", "sans-serif")
        )
        
        # 装饰性粒子效果
        if self.is_victory:
            self._render_victory_particles(center_x, panel_bottom + panel_height)
    
    def _render_victory_particles(self, x: float, y: float) -> None:
        """渲染胜利粒子效果"""
        import random
        random.seed(int(self.animation_time * 10))
        
        for i in range(20):
            px = x + random.uniform(-200, 200)
            py = y + random.uniform(-50, 50)
            size = random.uniform(2, 6)
            alpha = int(random.uniform(50, 150) * (0.5 + 0.5 * math.sin(self.animation_time * 2 + i)))
            
            colors = [SECONDARY, SECONDARY_LIGHT, WHITE]
            color = random.choice(colors).with_alpha(alpha)
            
            arcade.draw_circle_filled(px, py, size, color.rgba)
