"""
伤害数字系统 - 显示伤害飘字效果
"""

import arcade
from typing import List, Tuple
from dataclasses import dataclass
import random


@dataclass
class DamageNumber:
    """伤害数字"""
    x: float
    y: float
    value: int
    color: Tuple[int, int, int]
    scale: float
    velocity_x: float
    velocity_y: float
    life: float
    max_life: float
    alpha: int = 255
    
    @property
    def is_alive(self) -> bool:
        """检查是否存活"""
        return self.life > 0
    
    def update(self, dt: float) -> None:
        """更新状态"""
        # 更新位置
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # 更新生命周期
        self.life -= dt
        
        # 更新透明度（渐隐）
        life_ratio = max(0, self.life / self.max_life)
        self.alpha = int(255 * life_ratio)


class DamageNumberSystem:
    """
    伤害数字系统
    
    管理并渲染伤害飘字效果
    """
    
    # 颜色定义
    COLOR_NORMAL = (255, 255, 255)   # 白色 - 普通伤害
    COLOR_CRIT = (255, 215, 0)       # 金色 - 暴击
    COLOR_HEAL = (0, 255, 0)         # 绿色 - 治疗
    COLOR_POISON = (128, 0, 128)     # 紫色 - 毒伤害
    COLOR_FIRE = (255, 69, 0)        # 橙红色 - 火焰伤害
    COLOR_ICE = (135, 206, 250)      # 浅蓝色 - 冰冻伤害
    
    def __init__(self):
        self.damage_numbers: List[DamageNumber] = []
        self.default_life = 1.0  # 默认存活时间（秒）
        self.default_scale = 1.0
        self.crit_scale = 1.5
    
    def add_damage_number(self, x: float, y: float, value: int,
                         damage_type: str = "normal", is_crit: bool = False) -> None:
        """
        添加伤害数字
        
        Args:
            x: X坐标
            y: Y坐标
            value: 伤害值
            damage_type: 伤害类型（normal, heal, poison, fire, ice）
            is_crit: 是否暴击
        """
        # 根据伤害类型选择颜色
        color = self._get_color(damage_type)
        
        # 暴击使用更大的字体
        scale = self.crit_scale if is_crit else self.default_scale
        
        # 添加上飘的随机偏移
        velocity_x = random.uniform(-20, 20)
        velocity_y = random.uniform(50, 100)  # 向上飘
        
        damage_num = DamageNumber(
            x=x,
            y=y,
            value=value,
            color=color,
            scale=scale,
            velocity_x=velocity_x,
            velocity_y=velocity_y,
            life=self.default_life,
            max_life=self.default_life
        )
        
        self.damage_numbers.append(damage_num)
    
    def _get_color(self, damage_type: str) -> Tuple[int, int, int]:
        """
        根据伤害类型获取颜色
        
        Args:
            damage_type: 伤害类型
            
        Returns:
            RGB颜色元组
        """
        color_map = {
            "normal": self.COLOR_NORMAL,
            "heal": self.COLOR_HEAL,
            "poison": self.COLOR_POISON,
            "fire": self.COLOR_FIRE,
            "ice": self.COLOR_ICE,
        }
        return color_map.get(damage_type, self.COLOR_NORMAL)
    
    def update(self, dt: float) -> None:
        """
        更新所有伤害数字
        
        Args:
            dt: 时间增量
        """
        # 更新所有数字
        for num in self.damage_numbers:
            num.update(dt)
        
        # 移除已消失的数字
        self.damage_numbers = [n for n in self.damage_numbers if n.is_alive]
    
    def render(self) -> None:
        """渲染所有伤害数字"""
        for num in self.damage_numbers:
            self._draw_damage_number(num)
    
    def _draw_damage_number(self, num: DamageNumber) -> None:
        """
        绘制单个伤害数字
        
        Args:
            num: 伤害数字数据
        """
        # 添加alpha通道到颜色
        color_with_alpha = (*num.color, num.alpha)
        
        # 计算字体大小
        font_size = int(16 * num.scale)
        
        # 绘制文字
        arcade.draw_text(
            str(num.value),
            num.x, num.y,
            color_with_alpha,
            font_size,
            anchor_x="center",
            anchor_y="center",
            bold=True
        )
    
    def clear(self) -> None:
        """清除所有伤害数字"""
        self.damage_numbers.clear()
    
    def get_active_count(self) -> int:
        """获取当前活跃的伤害数字数量"""
        return len(self.damage_numbers)
