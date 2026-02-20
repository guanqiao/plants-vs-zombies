"""
血条系统 - 显示实体生命值 - 增强版

包括：
- 渐变色彩血条
- 受伤闪烁效果
- 平滑血量变化动画
- 伤害数字飘字
"""

import arcade
import math
import random
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass, field
from ..core.theme_colors import StatusColors, UIColors, WHITE, Color


@dataclass
class HealthBar:
    """血条数据 - 增强版"""
    entity_id: int
    x: float
    y: float
    width: float
    height: float
    current_health: float
    max_health: float
    is_visible: bool = True
    
    # 动画状态
    display_health: float = field(default=0.0)
    damage_flash: float = field(default=0.0)
    heal_flash: float = field(default=0.0)
    pulse_phase: float = field(default=0.0)
    
    # 历史血量（用于检测变化）
    prev_health: float = field(default=0.0)
    
    def __post_init__(self):
        if self.display_health == 0.0:
            self.display_health = self.current_health
        if self.prev_health == 0.0:
            self.prev_health = self.current_health
    
    @property
    def health_percent(self) -> float:
        """获取血量百分比"""
        if self.max_health <= 0:
            return 0.0
        return max(0.0, min(1.0, self.current_health / self.max_health))
    
    @property
    def display_percent(self) -> float:
        """获取显示血量百分比"""
        if self.max_health <= 0:
            return 0.0
        return max(0.0, min(1.0, self.display_health / self.max_health))
    
    def update(self, dt: float) -> None:
        """更新血条动画"""
        # 平滑血量变化
        diff = self.current_health - self.display_health
        self.display_health += diff * 0.15
        
        # 检测受伤/治疗
        health_diff = self.current_health - self.prev_health
        if health_diff < 0:
            # 受伤
            self.damage_flash = 1.0
        elif health_diff > 0:
            # 治疗
            self.heal_flash = 1.0
        
        self.prev_health = self.current_health
        
        # 闪烁衰减
        self.damage_flash *= 0.9
        self.heal_flash *= 0.9
        
        # 低血量脉冲
        if self.health_percent <= 0.3:
            self.pulse_phase += dt * 5.0
        else:
            self.pulse_phase = 0.0
    
    def get_health_color(self, percent: float) -> Color:
        """根据血量获取颜色 - 渐变效果"""
        if percent > 0.6:
            return StatusColors.HEALTH_HIGH
        elif percent > 0.3:
            # 绿色到黄色的渐变
            t = (percent - 0.3) / 0.3
            return Color(
                int(StatusColors.HEALTH_LOW.r + (StatusColors.HEALTH_HIGH.r - StatusColors.HEALTH_LOW.r) * t),
                int(StatusColors.HEALTH_LOW.g + (StatusColors.HEALTH_HIGH.g - StatusColors.HEALTH_LOW.g) * t),
                int(StatusColors.HEALTH_LOW.b + (StatusColors.HEALTH_HIGH.b - StatusColors.HEALTH_LOW.b) * t)
            )
        else:
            # 黄色到红色的渐变
            t = percent / 0.3
            return Color(
                int(StatusColors.HEALTH_LOW.r + (StatusColors.HEALTH_MEDIUM.r - StatusColors.HEALTH_LOW.r) * t),
                int(StatusColors.HEALTH_LOW.g + (StatusColors.HEALTH_MEDIUM.g - StatusColors.HEALTH_LOW.g) * t),
                int(StatusColors.HEALTH_LOW.b + (StatusColors.HEALTH_MEDIUM.b - StatusColors.HEALTH_LOW.b) * t)
            )


@dataclass
class DamageNumber:
    """伤害数字"""
    x: float
    y: float
    value: int
    color: Color
    life: float = 1.0
    max_life: float = 1.0
    vy: float = -40.0
    vx: float = 0.0
    scale: float = 1.0
    is_crit: bool = False
    
    def update(self, dt: float) -> None:
        """更新动画"""
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # 弹跳效果
        if self.is_crit:
            self.scale = 1.0 + math.sin((1.0 - self.life / self.max_life) * math.pi) * 0.5
        else:
            self.scale = 1.0 + (1.0 - self.life / self.max_life) * 0.2
    
    @property
    def is_alive(self) -> bool:
        return self.life > 0
    
    @property
    def alpha(self) -> int:
        """获取透明度（带缓出效果）"""
        t = self.life / self.max_life
        return int(255 * t * t)


class HealthBarSystem:
    """
    血条系统 - 增强版
    
    管理并渲染所有实体的血条，包含动画效果
    """
    
    def __init__(self):
        self.health_bars: Dict[int, HealthBar] = {}
        self.damage_numbers: List[DamageNumber] = []
        self.bar_width = 50
        self.bar_height = 8
        self.offset_y = 55  # 血条在实体上方的偏移
        
        # 颜色配置
        self.bg_color = UIColors.BG_DARK.with_alpha(200)
        self.border_color = UIColors.BORDER
        self.damage_flash_color = StatusColors.ERROR
        self.heal_flash_color = StatusColors.HEALTH_HIGH
    
    def add_health_bar(self, entity_id: int, x: float, y: float,
                      current_health: float, max_health: float,
                      width: float = None, height: float = None) -> None:
        """
        添加血条
        
        Args:
            entity_id: 实体ID
            x: X坐标
            y: Y坐标
            current_health: 当前生命值
            max_health: 最大生命值
            width: 血条宽度（默认50）
            height: 血条高度（默认8）
        """
        bar = HealthBar(
            entity_id=entity_id,
            x=x,
            y=y + self.offset_y,
            width=width or self.bar_width,
            height=height or self.bar_height,
            current_health=current_health,
            max_health=max_health,
            display_health=current_health,
            prev_health=current_health
        )
        self.health_bars[entity_id] = bar
    
    def remove_health_bar(self, entity_id: int) -> None:
        """移除血条"""
        if entity_id in self.health_bars:
            del self.health_bars[entity_id]
    
    def update_health_bar(self, entity_id: int, 
                         current_health: float, max_health: float = None,
                         x: float = None, y: float = None) -> None:
        """更新血条数据"""
        if entity_id not in self.health_bars:
            return
        
        bar = self.health_bars[entity_id]
        bar.current_health = current_health
        
        if max_health is not None:
            bar.max_health = max_health
        
        if x is not None:
            bar.x = x
        
        if y is not None:
            bar.y = y + self.offset_y
    
    def set_visibility(self, entity_id: int, visible: bool) -> None:
        """设置血条可见性"""
        if entity_id in self.health_bars:
            self.health_bars[entity_id].is_visible = visible
    
    def add_damage_number(self, x: float, y: float, damage: int, 
                         is_crit: bool = False, is_heal: bool = False) -> None:
        """
        添加伤害数字
        
        Args:
            x: X坐标
            y: Y坐标
            damage: 伤害值
            is_crit: 是否暴击
            is_heal: 是否治疗
        """
        if is_heal:
            color = StatusColors.HEALTH_HIGH
            vx = 0.0
        elif is_crit:
            color = StatusColors.ERROR.lighten(0.2)
            vx = random.uniform(-20, 20)
        else:
            color = WHITE
            vx = random.uniform(-10, 10)
        
        self.damage_numbers.append(DamageNumber(
            x=x, y=y, value=damage, color=color,
            vx=vx, is_crit=is_crit
        ))
    
    def update(self, dt: float) -> None:
        """更新所有血条和伤害数字"""
        # 更新血条
        for bar in self.health_bars.values():
            bar.update(dt)
        
        # 更新伤害数字
        for num in self.damage_numbers:
            num.update(dt)
        
        # 清理死亡的伤害数字
        self.damage_numbers = [n for n in self.damage_numbers if n.is_alive]
    
    def render(self) -> None:
        """渲染所有血条和伤害数字"""
        # 渲染血条
        for bar in self.health_bars.values():
            if bar.is_visible and bar.max_health > 0:
                self._draw_health_bar(bar)
        
        # 渲染伤害数字
        for num in self.damage_numbers:
            self._draw_damage_number(num)
    
    def _draw_health_bar(self, bar: HealthBar) -> None:
        """绘制单个血条 - 增强版"""
        # 计算位置
        half_width = bar.width / 2
        half_height = bar.height / 2
        left = bar.x - half_width
        right = bar.x + half_width
        bottom = bar.y - half_height
        top = bar.y + half_height
        
        # 低血量脉冲效果
        pulse_scale = 1.0
        if bar.health_percent <= 0.3:
            pulse = 0.5 + 0.5 * math.sin(bar.pulse_phase)
            pulse_scale = 1.0 + pulse * 0.1
            
            # 绘制警告光晕
            glow_alpha = int(50 * pulse)
            arcade.draw_circle_filled(
                bar.x, bar.y, half_width * 1.5,
                StatusColors.ERROR.with_alpha(glow_alpha).rgba
            )
        
        # 应用脉冲缩放
        if pulse_scale != 1.0:
            center_x = (left + right) / 2
            center_y = (bottom + top) / 2
            w = (right - left) * pulse_scale / 2
            h = (top - bottom) * pulse_scale / 2
            left = center_x - w
            right = center_x + w
            bottom = center_y - h
            top = center_y + h
        
        # 绘制阴影
        arcade.draw_lrbt_rectangle_filled(
            left + 2, right + 2, bottom - 2, top - 2,
            (0, 0, 0, 100)
        )
        
        # 绘制背景
        arcade.draw_lrbt_rectangle_filled(
            left, right, bottom, top,
            self.bg_color.rgba
        )
        
        # 绘制血量背景（显示血量变化）
        display_width = bar.width * bar.display_percent
        if display_width > 0 and abs(bar.display_health - bar.current_health) > 1:
            # 延迟血量条（白色）
            arcade.draw_lrbt_rectangle_filled(
                left, left + display_width, bottom + 1, top - 1,
                WHITE.with_alpha(100).rgba
            )
        
        # 绘制实际血量
        health_width = bar.width * bar.health_percent
        if health_width > 0:
            health_color = bar.get_health_color(bar.health_percent)
            
            # 受伤闪烁效果
            if bar.damage_flash > 0.1:
                flash_intensity = bar.damage_flash
                health_color = Color(
                    int(health_color.r + (255 - health_color.r) * flash_intensity * 0.5),
                    int(health_color.g * (1 - flash_intensity * 0.3)),
                    int(health_color.b * (1 - flash_intensity * 0.3))
                )
            
            # 治疗闪烁效果
            if bar.heal_flash > 0.1:
                flash_intensity = bar.heal_flash
                health_color = health_color.lighten(flash_intensity * 0.3)
            
            arcade.draw_lrbt_rectangle_filled(
                left, left + health_width, bottom + 1, top - 1,
                health_color.rgba
            )
            
            # 绘制血量高光
            highlight_height = (top - bottom - 2) * 0.4
            arcade.draw_lrbt_rectangle_filled(
                left, left + health_width,
                top - 1 - highlight_height, top - 1,
                WHITE.with_alpha(60).rgba
            )
        
        # 绘制边框
        border_color = self.border_color
        if bar.damage_flash > 0.1:
            # 受伤时边框变红
            border_color = self.damage_flash_color.with_alpha(int(150 + bar.damage_flash * 105))
        elif bar.heal_flash > 0.1:
            # 治疗时边框变绿
            border_color = self.heal_flash_color.with_alpha(int(150 + bar.heal_flash * 105))
        
        arcade.draw_lrbt_rectangle_outline(
            left, right, bottom, top,
            border_color.rgba, 2 if bar.damage_flash > 0.1 else 1
        )
    
    def _draw_damage_number(self, num: DamageNumber) -> None:
        """绘制伤害数字"""
        alpha = num.alpha
        color = num.color.with_alpha(alpha)
        
        text = str(num.value)
        if num.is_crit:
            text = f"{text}!"
        
        font_size = int(16 * num.scale) if not num.is_crit else int(20 * num.scale)
        
        # 绘制发光效果（暴击时）
        if num.is_crit:
            for i in range(3):
                glow_alpha = int(alpha * (0.3 - i * 0.1))
                arcade.draw_text(
                    text, num.x, num.y,
                    num.color.with_alpha(glow_alpha).rgba,
                    font_size + i * 2,
                    anchor_x="center",
                    font_name=("Arial", "Microsoft YaHei", "sans-serif"),
                    bold=True
                )
        
        # 绘制阴影
        arcade.draw_text(
            text, num.x + 2, num.y - 2,
            (0, 0, 0, alpha // 2),
            font_size,
            anchor_x="center",
            font_name=("Arial", "Microsoft YaHei", "sans-serif"),
            bold=num.is_crit
        )
        
        # 绘制主文字
        arcade.draw_text(
            text, num.x, num.y,
            color.rgba,
            font_size,
            anchor_x="center",
            font_name=("Arial", "Microsoft YaHei", "sans-serif"),
            bold=num.is_crit
        )
    
    def clear(self) -> None:
        """清除所有血条和伤害数字"""
        self.health_bars.clear()
        self.damage_numbers.clear()
    
    def get_health_bar(self, entity_id: int) -> Optional[HealthBar]:
        """获取血条"""
        return self.health_bars.get(entity_id)
