"""
僵尸动画渲染器 - 提供程序化的僵尸动画效果

包括：
- 行走时的身体摆动
- 手臂摆动动画
- 受击时的震动和闪烁
- 部位脱落效果
"""

import math
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import arcade


class ZombieBodyPart(Enum):
    """僵尸身体部位"""
    HEAD = auto()
    BODY = auto()
    ARM_LEFT = auto()
    ARM_RIGHT = auto()
    LEG_LEFT = auto()
    LEG_RIGHT = auto()


@dataclass
class BodyPartState:
    """身体部位状态"""
    attached: bool = True  # 是否还连接在身上
    offset_x: float = 0.0
    offset_y: float = 0.0
    rotation: float = 0.0
    scale: float = 1.0
    alpha: int = 255
    
    # 脱落后的物理状态
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    angular_velocity: float = 0.0


@dataclass
class ProceduralAnimationState:
    """程序化动画状态"""
    # 行走动画参数
    walk_cycle_time: float = 0.0
    walk_speed: float = 1.5  # 降低行走循环速度
    
    # 身体摆动
    body_bob_amount: float = 0.8  # 降低身体上下摆动幅度
    body_sway_amount: float = 0.5  # 降低身体左右摆动幅度
    
    # 手臂摆动
    arm_swing_amount: float = 5.0  # 降低手臂摆动角度
    
    # 当前变换
    body_offset_y: float = 0.0
    body_rotation: float = 0.0
    left_arm_angle: float = 0.0
    right_arm_angle: float = 0.0
    
    # 部位状态
    parts: Dict[ZombieBodyPart, BodyPartState] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化部位状态"""
        if not self.parts:
            for part in ZombieBodyPart:
                self.parts[part] = BodyPartState()


class ZombieAnimationRenderer:
    """
    僵尸动画渲染器
    
    使用程序化动画让僵尸更加生动，即使没有精灵图也能有好的视觉效果
    """
    
    def __init__(self):
        self._states: Dict[int, ProceduralAnimationState] = {}
        self._time: float = 0.0
    
    def update(self, dt: float, zombie_id: int, is_moving: bool = True,
               is_attacking: bool = False, is_hurt: bool = False) -> None:
        """
        更新僵尸动画状态
        
        Args:
            dt: 时间增量
            zombie_id: 僵尸实体ID
            is_moving: 是否在移动
            is_attacking: 是否在攻击
            is_hurt: 是否受击
        """
        self._time += dt
        
        state = self._get_or_create_state(zombie_id)
        
        # 更新行走循环
        if is_moving:
            state.walk_cycle_time += dt * state.walk_speed
        else:
            # 慢慢回到待机状态
            state.walk_cycle_time += dt * state.walk_speed * 0.3
        
        # 计算身体摆动
        walk_phase = state.walk_cycle_time % (2 * math.pi)
        
        # 身体上下摆动（正弦波）
        state.body_offset_y = math.sin(walk_phase) * state.body_bob_amount
        
        # 身体轻微左右摆动
        state.body_rotation = math.sin(walk_phase) * state.body_sway_amount * 0.3
        
        # 手臂摆动（与身体相反）
        if is_attacking:
            # 攻击时手臂前伸
            state.left_arm_angle = -30 + math.sin(self._time * 2.5) * 8
            state.right_arm_angle = -30 + math.sin(self._time * 2.5 + math.pi) * 8
        else:
            # 行走时手臂自然摆动
            swing = math.sin(walk_phase) * state.arm_swing_amount
            state.left_arm_angle = 20 + swing
            state.right_arm_angle = 20 - swing
        
        # 更新脱落的部位
        self._update_detached_parts(state, dt)
    
    def _update_detached_parts(self, state: ProceduralAnimationState, dt: float) -> None:
        """更新脱落部位的物理状态"""
        for part, part_state in state.parts.items():
            if not part_state.attached:
                # 应用重力
                part_state.velocity_y -= 200 * dt  # 重力加速度
                
                # 更新位置
                part_state.offset_x += part_state.velocity_x * dt
                part_state.offset_y += part_state.velocity_y * dt
                
                # 更新旋转
                part_state.rotation += part_state.angular_velocity * dt
                
                # 地面碰撞检测（简单处理）
                if part_state.offset_y < -50:
                    part_state.offset_y = -50
                    part_state.velocity_y *= -0.3  # 弹跳并减速
                    part_state.velocity_x *= 0.8  # 摩擦力
                    part_state.angular_velocity *= 0.8
    
    def render(self, zombie_id: int, x: float, y: float,
               base_color: Tuple[int, int, int],
               width: float, height: float,
               is_flipped_x: bool = False) -> None:
        """
        渲染僵尸（程序化动画版本）
        
        Args:
            zombie_id: 僵尸实体ID
            x: 中心X坐标
            y: 中心Y坐标
            base_color: 基础颜色
            width: 宽度
            height: 高度
            is_flipped_x: 是否水平翻转
        """
        state = self._get_or_create_state(zombie_id)
        
        # 计算翻转系数
        flip = -1 if is_flipped_x else 1
        
        # 身体中心位置（加上上下摆动）
        body_x = x
        body_y = y + state.body_offset_y
        
        # 渲染身体
        self._render_body(zombie_id, body_x, body_y, base_color, 
                         width, height, state.body_rotation, is_flipped_x)
        
        # 渲染头部
        head_state = state.parts[ZombieBodyPart.HEAD]
        if head_state.attached:
            head_x = body_x + head_state.offset_x
            head_y = body_y + height * 0.35 + head_state.offset_y
            self._render_head(head_x, head_y, base_color, width * 0.6, height * 0.4,
                            state.body_rotation * 0.5, is_flipped_x)
        else:
            # 渲染脱落的头部
            self._render_detached_part(zombie_id, ZombieBodyPart.HEAD, base_color)
        
        # 渲染手臂
        self._render_arms(zombie_id, body_x, body_y, base_color, 
                         width, height, flip, state)
    
    def _render_body(self, zombie_id: int, x: float, y: float,
                    color: Tuple[int, int, int], width: float, height: float,
                    rotation: float, is_flipped_x: bool) -> None:
        """渲染身体"""
        # 身体主体（矩形）
        body_width = width * 0.7
        body_height = height * 0.6
        
        # 计算旋转后的四个角
        cos_r = math.cos(math.radians(rotation))
        sin_r = math.sin(math.radians(rotation))
        
        half_w = body_width / 2
        half_h = body_height / 2
        
        # 身体颜色（比基础色稍深）
        body_color = (
            max(0, color[0] - 20),
            max(0, color[1] - 20),
            max(0, color[2] - 20)
        )
        
        # 绘制身体（使用椭圆更自然）
        arcade.draw_ellipse_filled(x, y, body_width, body_height, body_color)
        
        # 绘制衣服细节（领带/破烂衣服）
        tie_color = (139, 69, 19)  # 棕色领带
        arcade.draw_rect_filled(arcade.XYWH(x, y, body_width * 0.15, body_height * 0.5), tie_color)
        
        # 绘制破烂的边缘
        self._render_tattered_edges(x, y, body_width, body_height, body_color)
    
    def _render_head(self, x: float, y: float, color: Tuple[int, int, int],
                    width: float, height: float, rotation: float,
                    is_flipped_x: bool) -> None:
        """渲染头部"""
        # 头部颜色（比身体稍浅）
        head_color = (
            min(255, color[0] + 20),
            min(255, color[1] + 20),
            min(255, color[2] + 20)
        )
        
        # 绘制头部（圆形）
        head_radius = min(width, height) / 2
        arcade.draw_circle_filled(x, y, head_radius, head_color)
        
        # 绘制眼睛
        eye_offset_x = width * 0.15
        eye_offset_y = height * 0.05
        eye_size = width * 0.12
        
        # 左眼白
        left_eye_x = x - eye_offset_x
        left_eye_y = y + eye_offset_y
        arcade.draw_circle_filled(left_eye_x, left_eye_y, eye_size, (255, 255, 255))
        
        # 右眼白
        right_eye_x = x + eye_offset_x
        right_eye_y = y + eye_offset_y
        arcade.draw_circle_filled(right_eye_x, right_eye_y, eye_size, (255, 255, 255))
        
        # 瞳孔（看向左边，因为僵尸向左走）
        pupil_offset = -eye_size * 0.3
        pupil_size = eye_size * 0.5
        
        arcade.draw_circle_filled(
            left_eye_x + pupil_offset, left_eye_y, pupil_size, (0, 0, 0)
        )
        arcade.draw_circle_filled(
            right_eye_x + pupil_offset, right_eye_y, pupil_size, (0, 0, 0)
        )
        
        # 绘制嘴巴（简单的弧线）
        mouth_y = y - height * 0.15
        arcade.draw_arc_outline(
            x, mouth_y, width * 0.4, height * 0.2,
            (100, 50, 50), 180, 360, 2
        )
        
        # 绘制牙齿
        tooth_width = width * 0.06
        tooth_height = height * 0.08
        for i in range(-1, 2):
            tooth_x = x + i * tooth_width * 1.5
            arcade.draw_rect_filled(arcade.XYWH(tooth_x, mouth_y + tooth_height / 2, tooth_width * 0.8, tooth_height), (255, 255, 255)
            )
    
    def _render_arms(self, zombie_id: int, body_x: float, body_y: float,
                    color: Tuple[int, int, int], width: float, height: float,
                    flip: int, state: ProceduralAnimationState) -> None:
        """渲染手臂"""
        arm_width = width * 0.2
        arm_length = height * 0.45
        shoulder_y = body_y + height * 0.1
        
        # 左臂
        left_arm_state = state.parts[ZombieBodyPart.ARM_LEFT]
        if left_arm_state.attached:
            left_angle = state.left_arm_angle + state.body_rotation
            left_shoulder_x = body_x - width * 0.35
            self._render_arm(left_shoulder_x, shoulder_y, arm_width, arm_length,
                           left_angle, color, flip)
        
        # 右臂
        right_arm_state = state.parts[ZombieBodyPart.ARM_RIGHT]
        if right_arm_state.attached:
            right_angle = state.right_arm_angle + state.body_rotation
            right_shoulder_x = body_x + width * 0.35
            self._render_arm(right_shoulder_x, shoulder_y, arm_width, arm_length,
                           right_angle, color, flip)
    
    def _render_arm(self, shoulder_x: float, shoulder_y: float,
                   width: float, length: float, angle: float,
                   color: Tuple[int, int, int], flip: int) -> None:
        """渲染单条手臂"""
        # 手臂颜色
        arm_color = (
            max(0, color[0] - 10),
            max(0, color[1] - 10),
            max(0, color[2] - 10)
        )
        
        # 计算手臂末端位置
        rad = math.radians(angle * flip)
        end_x = shoulder_x + math.sin(rad) * length
        end_y = shoulder_y - math.cos(rad) * length
        
        # 绘制手臂（线段+圆形关节）
        arcade.draw_line(
            shoulder_x, shoulder_y, end_x, end_y,
            arm_color, width
        )
        
        # 肩膀关节
        arcade.draw_circle_filled(shoulder_x, shoulder_y, width * 0.6, arm_color)
        
        # 手部
        hand_color = (
            min(255, color[0] + 10),
            min(255, color[1] + 10),
            min(255, color[2] + 10)
        )
        arcade.draw_circle_filled(end_x, end_y, width * 0.7, hand_color)
    
    def _render_tattered_edges(self, x: float, y: float, 
                              width: float, height: float,
                              color: Tuple[int, int, int]) -> None:
        """渲染破烂衣服的边缘效果"""
        # 在衣服底部绘制锯齿状边缘
        edge_y = y - height / 2
        num_teeth = 5
        tooth_width = width / num_teeth
        
        for i in range(num_teeth):
            tooth_x = x - width / 2 + (i + 0.5) * tooth_width
            tooth_depth = random.uniform(3, 8)
            
            # 绘制三角形缺口
            arcade.draw_triangle_filled(
                tooth_x - tooth_width * 0.4, edge_y,
                tooth_x + tooth_width * 0.4, edge_y,
                tooth_x, edge_y - tooth_depth,
                (0, 0, 0, 0)  # 透明，形成缺口
            )
    
    def _render_detached_part(self, zombie_id: int, part: ZombieBodyPart,
                             color: Tuple[int, int, int]) -> None:
        """渲染脱落的部位"""
        state = self._states.get(zombie_id)
        if not state:
            return
        
        part_state = state.parts[part]
        if part_state.attached:
            return
        
        # 这里可以渲染脱落在地上的部位
        # 简化处理：绘制一个小标记
        x = part_state.offset_x
        y = part_state.offset_y
        
        if part == ZombieBodyPart.HEAD:
            arcade.draw_circle_filled(x, y, 15, color)
        elif part in (ZombieBodyPart.ARM_LEFT, ZombieBodyPart.ARM_RIGHT):
            arcade.draw_rect_filled(arcade.XYWH(x, y, 8, 20), color)
    
    def detach_part(self, zombie_id: int, part: ZombieBodyPart,
                   velocity_x: float = None, velocity_y: float = None) -> None:
        """
        使部位脱落
        
        Args:
            zombie_id: 僵尸实体ID
            part: 要脱落的部位
            velocity_x: 水平初速度（随机如果未指定）
            velocity_y: 垂直初速度（随机如果未指定）
        """
        state = self._get_or_create_state(zombie_id)
        part_state = state.parts[part]
        
        part_state.attached = False
        part_state.velocity_x = velocity_x if velocity_x is not None else random.uniform(-100, 100)
        part_state.velocity_y = velocity_y if velocity_y is not None else random.uniform(50, 150)
        part_state.angular_velocity = random.uniform(-360, 360)
    
    def reset(self, zombie_id: int) -> None:
        """重置僵尸动画状态"""
        if zombie_id in self._states:
            del self._states[zombie_id]
    
    def _get_or_create_state(self, zombie_id: int) -> ProceduralAnimationState:
        """获取或创建动画状态"""
        if zombie_id not in self._states:
            self._states[zombie_id] = ProceduralAnimationState()
        return self._states[zombie_id]
    
    def clear(self) -> None:
        """清除所有状态"""
        self._states.clear()
        self._time = 0.0
