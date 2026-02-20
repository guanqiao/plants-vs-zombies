"""
僵尸特效系统 - 为僵尸添加各种视觉效果

包括：
- 行走尘土效果
- 僵尸阴影
- 表情变化
- 环境互动效果
"""

import math
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import arcade


class ZombieExpression(Enum):
    """僵尸表情类型"""
    NORMAL = auto()      # 正常
    ANGRY = auto()       # 愤怒
    PAIN = auto()        # 痛苦
    HUNGRY = auto()      # 饥饿（吃植物时）
    SURPRISED = auto()   # 惊讶
    DETERMINED = auto()  # 坚定（撑杆跳时）


@dataclass
class DustParticle:
    """尘土粒子"""
    x: float
    y: float
    vx: float
    vy: float
    size: float
    alpha: int
    life: float
    max_life: float
    
    def update(self, dt: float) -> None:
        """更新粒子"""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy -= 20 * dt  # 轻微重力
        self.life -= dt
        # 淡出
        life_ratio = self.life / self.max_life
        self.alpha = int(150 * life_ratio)
    
    @property
    def is_alive(self) -> bool:
        return self.life > 0


@dataclass
class ShadowState:
    """阴影状态"""
    offset_x: float = 0.0
    offset_y: float = -5.0  # 阴影在脚下
    scale_x: float = 1.0
    scale_y: float = 0.3    # 压扁的椭圆
    alpha: int = 80
    
    def update(self, zombie_y_offset: float = 0.0) -> None:
        """
        更新阴影
        
        Args:
            zombie_y_offset: 僵尸的Y轴偏移（如跳跃时）
        """
        # 当僵尸跳起时，阴影变小变淡
        if zombie_y_offset > 0:
            height_factor = max(0.3, 1.0 - zombie_y_offset / 100)
            self.scale_x = height_factor
            self.scale_y = 0.3 * height_factor
            self.alpha = int(80 * height_factor)
        else:
            self.scale_x = 1.0
            self.scale_y = 0.3
            self.alpha = 80


@dataclass
class ExpressionState:
    """表情状态"""
    current_expression: ZombieExpression = ZombieExpression.NORMAL
    expression_timer: float = 0.0
    blink_timer: float = 0.0
    is_blinking: bool = False
    mouth_open: float = 0.0  # 嘴巴张开程度 (0-1)
    
    def update(self, dt: float, is_eating: bool = False, 
               is_hurt: bool = False, is_jumping: bool = False) -> None:
        """更新表情状态"""
        # 眨眼逻辑
        self.blink_timer += dt
        if self.is_blinking:
            if self.blink_timer > 0.15:  # 眨眼持续0.15秒
                self.is_blinking = False
                self.blink_timer = 0.0
        else:
            if self.blink_timer > random.uniform(2.0, 5.0):  # 随机眨眼间隔
                self.is_blinking = True
                self.blink_timer = 0.0
        
        # 根据状态改变表情
        if is_hurt:
            self.current_expression = ZombieExpression.PAIN
            self.expression_timer = 0.5
        elif is_eating:
            self.current_expression = ZombieExpression.HUNGRY
            self.mouth_open = min(1.0, self.mouth_open + dt * 5)
        elif is_jumping:
            self.current_expression = ZombieExpression.DETERMINED
        else:
            self.mouth_open = max(0.0, self.mouth_open - dt * 3)
            if self.expression_timer > 0:
                self.expression_timer -= dt
            else:
                self.current_expression = ZombieExpression.NORMAL


@dataclass
class GrassInteraction:
    """草地互动效果"""
    x: float
    y: float
    intensity: float = 0.0  # 摆动强度
    phase: float = 0.0      # 摆动相位
    
    def update(self, dt: float, zombie_x: float, zombie_y: float,
               zombie_speed: float) -> None:
        """更新草地互动"""
        # 计算与僵尸的距离
        dx = self.x - zombie_x
        dy = self.y - zombie_y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # 如果在僵尸附近，增加摆动
        if distance < 40 and zombie_speed > 0:
            self.intensity = min(1.0, self.intensity + dt * 5)
            self.phase += dt * 10
        else:
            self.intensity = max(0.0, self.intensity - dt * 2)


class ZombieEffects:
    """
    僵尸特效管理器
    
    管理僵尸的各种视觉效果
    """
    
    def __init__(self):
        self._dust_particles: Dict[int, List[DustParticle]] = {}
        self._shadow_states: Dict[int, ShadowState] = {}
        self._expression_states: Dict[int, ExpressionState] = {}
        self._grass_interactions: Dict[int, GrassInteraction] = {}
        self._time: float = 0.0
        
        # 尘土生成计时器
        self._dust_timers: Dict[int, float] = {}
    
    def update(self, dt: float, zombie_id: int, x: float, y: float,
               is_moving: bool = False, is_eating: bool = False,
               is_hurt: bool = False, is_jumping: bool = False,
               speed: float = 0.0) -> None:
        """
        更新僵尸特效
        
        Args:
            dt: 时间增量
            zombie_id: 僵尸实体ID
            x: X坐标
            y: Y坐标
            is_moving: 是否在移动
            is_eating: 是否在吃植物
            is_hurt: 是否受击
            is_jumping: 是否在跳跃
            speed: 移动速度
        """
        self._time += dt
        
        # 更新阴影
        shadow = self._get_or_create_shadow(zombie_id)
        y_offset = 0.0 if not is_jumping else 50.0  # 简化处理
        shadow.update(y_offset)
        
        # 更新表情
        expression = self._get_or_create_expression(zombie_id)
        expression.update(dt, is_eating, is_hurt, is_jumping)
        
        # 生成行走尘土
        if is_moving and speed > 0 and not is_jumping:
            self._update_dust(dt, zombie_id, x, y, speed)
        
        # 更新尘土粒子
        self._update_dust_particles(dt, zombie_id)
    
    def _update_dust(self, dt: float, zombie_id: int, x: float, 
                    y: float, speed: float) -> None:
        """更新行走尘土生成"""
        if zombie_id not in self._dust_timers:
            self._dust_timers[zombie_id] = 0.0
        
        self._dust_timers[zombie_id] += dt
        
        # 根据速度决定生成频率
        dust_interval = max(0.1, 0.5 - speed / 200)
        
        if self._dust_timers[zombie_id] >= dust_interval:
            self._dust_timers[zombie_id] = 0.0
            self._spawn_dust(zombie_id, x, y - 35)  # 在脚下生成
    
    def _spawn_dust(self, zombie_id: int, x: float, y: float) -> None:
        """生成尘土粒子"""
        if zombie_id not in self._dust_particles:
            self._dust_particles[zombie_id] = []
        
        # 生成2-4个尘土粒子
        for _ in range(random.randint(2, 4)):
            particle = DustParticle(
                x=x + random.uniform(-10, 10),
                y=y + random.uniform(-5, 5),
                vx=random.uniform(-20, 20),
                vy=random.uniform(10, 30),
                size=random.uniform(3, 8),
                alpha=150,
                life=random.uniform(0.3, 0.6),
                max_life=0.6
            )
            self._dust_particles[zombie_id].append(particle)
    
    def _update_dust_particles(self, dt: float, zombie_id: int) -> None:
        """更新尘土粒子"""
        if zombie_id not in self._dust_particles:
            return
        
        particles = self._dust_particles[zombie_id]
        for p in particles[:]:
            p.update(dt)
            if not p.is_alive:
                particles.remove(p)
    
    def render_shadow(self, zombie_id: int, x: float, y: float,
                     zombie_width: float) -> None:
        """渲染僵尸阴影"""
        shadow = self._get_or_create_shadow(zombie_id)
        
        shadow_x = x + shadow.offset_x
        shadow_y = y + shadow.offset_y
        
        # 绘制椭圆阴影
        arcade.draw_ellipse_filled(
            shadow_x, shadow_y,
            zombie_width * shadow.scale_x,
            zombie_width * shadow.scale_y * 0.5,
            (0, 0, 0, shadow.alpha)
        )
    
    def render_dust(self, zombie_id: int) -> None:
        """渲染尘土粒子"""
        if zombie_id not in self._dust_particles:
            return
        
        for p in self._dust_particles[zombie_id]:
            if p.is_alive:
                # 使用棕灰色绘制尘土
                color = (160, 140, 120, p.alpha)
                arcade.draw_circle_filled(p.x, p.y, p.size, color)
    
    def render_expression(self, zombie_id: int, x: float, y: float,
                         head_width: float, head_height: float,
                         is_flipped: bool = True) -> None:
        """
        渲染僵尸表情
        
        Args:
            zombie_id: 僵尸实体ID
            x: 头部中心X
            y: 头部中心Y
            head_width: 头部宽度
            head_height: 头部高度
            is_flipped: 是否水平翻转
        """
        expression = self._get_or_create_expression(zombie_id)
        
        # 计算眼睛位置
        eye_offset_x = head_width * 0.2
        eye_offset_y = head_height * 0.1
        eye_size = head_width * 0.15
        
        left_eye_x = x - eye_offset_x
        right_eye_x = x + eye_offset_x
        eye_y = y + eye_offset_y
        
        # 根据表情绘制不同的眼睛
        if expression.is_blinking:
            # 闭眼 - 绘制弧线
            self._draw_closed_eye(left_eye_x, eye_y, eye_size)
            self._draw_closed_eye(right_eye_x, eye_y, eye_size)
        else:
            # 睁眼
            self._draw_expression_eyes(
                expression.current_expression,
                left_eye_x, right_eye_x, eye_y,
                eye_size, is_flipped
            )
        
        # 绘制嘴巴
        self._draw_mouth(
            expression.current_expression,
            x, y - head_height * 0.15,
            head_width * 0.4, head_height * 0.2,
            expression.mouth_open
        )
    
    def _draw_closed_eye(self, x: float, y: float, size: float) -> None:
        """绘制闭着的眼睛"""
        arcade.draw_arc_outline(
            x, y, size * 1.5, size,
            (100, 50, 50), 0, 180, 2
        )
    
    def _draw_expression_eyes(self, expression: ZombieExpression,
                             left_x: float, right_x: float, y: float,
                             size: float, is_flipped: bool) -> None:
        """根据表情绘制眼睛"""
        # 眼白
        arcade.draw_circle_filled(left_x, y, size, (255, 255, 255))
        arcade.draw_circle_filled(right_x, y, size, (255, 255, 255))
        
        # 瞳孔方向和大小根据表情变化
        if expression == ZombieExpression.ANGRY:
            # 愤怒 - 瞳孔变小，向下看
            pupil_size = size * 0.4
            pupil_offset_y = -size * 0.2
        elif expression == ZombieExpression.PAIN:
            # 痛苦 - 瞳孔收缩
            pupil_size = size * 0.3
            pupil_offset_y = 0
        elif expression == ZombieExpression.SURPRISED:
            # 惊讶 - 瞳孔放大
            pupil_size = size * 0.7
            pupil_offset_y = 0
        elif expression == ZombieExpression.DETERMINED:
            # 坚定 - 正常瞳孔，向前看
            pupil_size = size * 0.5
            pupil_offset_y = 0
        else:
            # 正常/饥饿 - 向左看（朝向房子）
            pupil_size = size * 0.5
            pupil_offset_y = 0
        
        # 瞳孔偏移（僵尸向左走）
        pupil_offset_x = -size * 0.2 if is_flipped else size * 0.2
        
        # 绘制瞳孔
        arcade.draw_circle_filled(
            left_x + pupil_offset_x, y + pupil_offset_y,
            pupil_size, (0, 0, 0)
        )
        arcade.draw_circle_filled(
            right_x + pupil_offset_x, y + pupil_offset_y,
            pupil_size, (0, 0, 0)
        )
        
        # 愤怒时添加眉毛
        if expression == ZombieExpression.ANGRY:
            brow_y = y + size * 0.8
            # 左眉（向下倾斜）
            arcade.draw_line(
                left_x - size, brow_y + size * 0.3,
                left_x + size, brow_y - size * 0.3,
                (80, 40, 40), 3
            )
            # 右眉
            arcade.draw_line(
                right_x - size, brow_y - size * 0.3,
                right_x + size, brow_y + size * 0.3,
                (80, 40, 40), 3
            )
    
    def _draw_mouth(self, expression: ZombieExpression, x: float, y: float,
                   width: float, height: float, open_amount: float) -> None:
        """绘制嘴巴"""
        if expression == ZombieExpression.HUNGRY or open_amount > 0.1:
            # 张嘴（吃植物或饥饿）
            open_height = height * open_amount
            
            # 口腔（深色）
            arcade.draw_ellipse_filled(
                x, y - open_height / 2,
                width * 0.8, open_height,
                (80, 30, 30)
            )
            
            # 牙齿
            if open_amount > 0.3:
                tooth_width = width * 0.15
                tooth_height = height * 0.15
                for i in range(-1, 2):
                    tooth_x = x + i * tooth_width * 1.5
                    # 上牙
                    arcade.draw_rectangle_filled(
                        tooth_x, y + open_height / 2 - tooth_height / 2,
                        tooth_width * 0.8, tooth_height,
                        (240, 240, 240)
                    )
        elif expression == ZombieExpression.PAIN:
            # 痛苦 - 扭曲的嘴
            arcade.draw_arc_outline(
                x, y, width, height * 0.5,
                (100, 50, 50), 180, 360, 2
            )
            # 添加痛苦线条
            arcade.draw_line(x - width/2, y, x - width/2 - 5, y + 5, (100, 50, 50), 1)
            arcade.draw_line(x + width/2, y, x + width/2 + 5, y + 5, (100, 50, 50), 1)
        elif expression == ZombieExpression.ANGRY:
            # 愤怒 - 紧咬的嘴
            arcade.draw_line(
                x - width/2, y,
                x + width/2, y,
                (80, 40, 40), 3
            )
        else:
            # 正常 - 简单弧线
            arcade.draw_arc_outline(
                x, y, width, height * 0.4,
                (100, 50, 50), 180, 360, 2
            )
    
    def render_grass_interaction(self, zombie_id: int, x: float, y: float) -> None:
        """渲染草地互动效果"""
        if zombie_id not in self._grass_interactions:
            return
        
        interaction = self._grass_interactions[zombie_id]
        if interaction.intensity <= 0:
            return
        
        # 绘制被压弯的草
        grass_height = 8 * interaction.intensity
        grass_bend = 5 * interaction.intensity * math.sin(interaction.phase)
        
        # 左右两侧的草
        for offset in [-15, 15]:
            grass_x = x + offset
            grass_y = y - 40  # 脚下
            
            # 草叶（简化为线条）
            arcade.draw_line(
                grass_x, grass_y,
                grass_x + grass_bend + offset * 0.2, grass_y + grass_height,
                (100, 160, 80, int(200 * interaction.intensity)),
                2
            )
    
    def set_expression(self, zombie_id: int, expression: ZombieExpression,
                      duration: float = 1.0) -> None:
        """
        设置僵尸表情
        
        Args:
            zombie_id: 僵尸实体ID
            expression: 表情类型
            duration: 持续时间
        """
        expr_state = self._get_or_create_expression(zombie_id)
        expr_state.current_expression = expression
        expr_state.expression_timer = duration
    
    def _get_or_create_shadow(self, zombie_id: int) -> ShadowState:
        """获取或创建阴影状态"""
        if zombie_id not in self._shadow_states:
            self._shadow_states[zombie_id] = ShadowState()
        return self._shadow_states[zombie_id]
    
    def _get_or_create_expression(self, zombie_id: int) -> ExpressionState:
        """获取或创建表情状态"""
        if zombie_id not in self._expression_states:
            self._expression_states[zombie_id] = ExpressionState()
        return self._expression_states[zombie_id]
    
    def remove_zombie(self, zombie_id: int) -> None:
        """移除僵尸的所有效果"""
        self._dust_particles.pop(zombie_id, None)
        self._shadow_states.pop(zombie_id, None)
        self._expression_states.pop(zombie_id, None)
        self._grass_interactions.pop(zombie_id, None)
        self._dust_timers.pop(zombie_id, None)
    
    def clear(self) -> None:
        """清除所有效果"""
        self._dust_particles.clear()
        self._shadow_states.clear()
        self._expression_states.clear()
        self._grass_interactions.clear()
        self._dust_timers.clear()
        self._time = 0.0


# 全局特效实例
_zombie_effects: Optional[ZombieEffects] = None


def get_zombie_effects() -> ZombieEffects:
    """获取僵尸特效管理器实例"""
    global _zombie_effects
    if _zombie_effects is None:
        _zombie_effects = ZombieEffects()
    return _zombie_effects
