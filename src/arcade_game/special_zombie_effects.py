"""
特殊僵尸效果系统 - 为特殊僵尸提供独特的视觉效果

包括：
- 撑杆僵尸的跳跃效果
- 舞王僵尸的召唤效果
- 气球僵尸的漂浮效果
- 巨人僵尸的砸地和投掷效果
- 矿工僵尸的挖掘效果
"""

import math
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
import arcade


class SpecialEffectType(Enum):
    """特殊效果类型"""
    POLE_VAULT_JUMP = auto()    # 撑杆跳跃
    DANCER_SUMMON = auto()      # 舞王召唤
    BALLOON_FLOAT = auto()      # 气球漂浮
    GARGANTUAR_SMASH = auto()   # 巨人砸地
    GARGANTUAR_THROW = auto()   # 巨人投掷
    MINER_DIG = auto()          # 矿工挖掘
    BUNGEE_DROP = auto()        # 蹦极下降
    POGO_BOUNCE = auto()        # 跳跳杆弹跳


@dataclass
class PoleVaultState:
    """撑杆僵尸跳跃状态"""
    is_jumping: bool = False
    jump_progress: float = 0.0
    start_x: float = 0.0
    target_x: float = 0.0
    start_y: float = 0.0
    jump_height: float = 80.0
    jump_duration: float = 0.6
    
    def start_jump(self, start_x: float, target_x: float, start_y: float) -> None:
        """开始跳跃"""
        self.is_jumping = True
        self.jump_progress = 0.0
        self.start_x = start_x
        self.target_x = target_x
        self.start_y = start_y
    
    def update(self, dt: float) -> Tuple[float, float, bool]:
        """
        更新跳跃状态
        
        Returns:
            (当前x, 当前y, 是否完成)
        """
        if not self.is_jumping:
            return self.start_x, self.start_y, True
        
        self.jump_progress += dt / self.jump_duration
        
        if self.jump_progress >= 1.0:
            self.is_jumping = False
            self.jump_progress = 1.0
            return self.target_x, self.start_y, True
        
        # 抛物线运动
        t = self.jump_progress
        x = self.start_x + (self.target_x - self.start_x) * t
        
        # 高度使用正弦曲线（抛物线近似）
        height = math.sin(t * math.pi) * self.jump_height
        y = self.start_y + height
        
        return x, y, False
    
    def render_pole(self, x: float, y: float, is_flipped: bool = True) -> None:
        """渲染撑杆"""
        pole_length = 60
        pole_angle = -30 if is_flipped else 30
        
        # 根据跳跃进度调整杆子角度
        if self.is_jumping:
            # 跳跃时杆子逐渐放平
            pole_angle = -30 + self.jump_progress * 60
        
        rad = math.radians(pole_angle)
        end_x = x + math.cos(rad) * pole_length
        end_y = y + math.sin(rad) * pole_length
        
        # 绘制撑杆（棕色）
        arcade.draw_line(x, y, end_x, end_y, (139, 69, 19), 4)


@dataclass
class DancerSummonEffect:
    """舞王僵尸召唤效果"""
    is_summoning: bool = False
    summon_progress: float = 0.0
    summon_duration: float = 1.0
    flash_intensity: float = 0.0
    
    def start_summon(self) -> None:
        """开始召唤"""
        self.is_summoning = True
        self.summon_progress = 0.0
        self.flash_intensity = 1.0
    
    def update(self, dt: float) -> bool:
        """更新召唤效果，返回是否完成"""
        if not self.is_summoning:
            return True
        
        self.summon_progress += dt / self.summon_duration
        self.flash_intensity = max(0, 1.0 - self.summon_progress)
        
        if self.summon_progress >= 1.0:
            self.is_summoning = False
            return True
        return False
    
    def render(self, x: float, y: float) -> None:
        """渲染召唤效果"""
        if not self.is_summoning:
            return
        
        # 闪光效果
        if self.flash_intensity > 0:
            flash_size = 50 + self.summon_progress * 100
            alpha = int(255 * self.flash_intensity * (1.0 - self.summon_progress))
            arcade.draw_circle_filled(x, y, flash_size, (255, 255, 100, alpha))
        
        # 迪斯科地板效果
        if self.summon_progress < 0.5:
            tile_size = 30
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
            
            for i in range(-2, 3):
                for j in range(-2, 3):
                    tile_x = x + i * tile_size
                    tile_y = y + j * tile_size
                    color_idx = (i + j + int(self.summon_progress * 20)) % 4
                    alpha = int(150 * (0.5 - self.summon_progress) * 2)
                    arcade.draw_rectangle_filled(
                        tile_x, tile_y, tile_size - 2, tile_size - 2,
                        (*colors[color_idx][:3], alpha)
                    )


@dataclass
class BalloonFloatState:
    """气球僵尸漂浮状态"""
    float_offset: float = 0.0
    float_speed: float = 3.0
    float_amplitude: float = 8.0
    balloon_popped: bool = False
    pop_progress: float = 0.0
    
    def update(self, dt: float, time: float) -> float:
        """
        更新漂浮状态
        
        Returns:
            Y轴偏移量
        """
        if self.balloon_popped:
            self.pop_progress += dt
            # 气球破裂后下落
            fall_distance = min(50, self.pop_progress * 100)
            return self.float_amplitude - fall_distance
        
        # 正常漂浮
        return math.sin(time * self.float_speed) * self.float_amplitude
    
    def pop_balloon(self) -> None:
        """气球被击破"""
        self.balloon_popped = True
        self.pop_progress = 0.0
    
    def render_balloon(self, x: float, y: float, zombie_height: float) -> None:
        """渲染气球"""
        if self.balloon_popped and self.pop_progress > 0.2:
            return
        
        balloon_x = x
        balloon_y = y + zombie_height * 0.6 + 40
        
        # 气球主体（红色）
        balloon_color = (255, 100, 100)
        if self.balloon_popped:
            # 破裂效果 - 缩小并变色
            scale = max(0, 1.0 - self.pop_progress * 5)
            balloon_color = (255, 150, 150)
        else:
            scale = 1.0
        
        # 绘制气球
        arcade.draw_circle_filled(balloon_x, balloon_y, 20 * scale, balloon_color)
        
        # 气球高光
        arcade.draw_circle_filled(
            balloon_x - 5, balloon_y + 5, 6 * scale,
            (255, 200, 200)
        )
        
        # 绳子
        if not self.balloon_popped:
            arcade.draw_line(
                balloon_x, balloon_y - 20,
                x, y + zombie_height * 0.3,
                (200, 200, 200), 2
            )


@dataclass
class GargantuarEffect:
    """巨人僵尸效果"""
    is_smashing: bool = False
    smash_progress: float = 0.0
    smash_duration: float = 0.5
    impact_shockwave: float = 0.0
    
    def start_smash(self) -> None:
        """开始砸地"""
        self.is_smashing = True
        self.smash_progress = 0.0
    
    def update(self, dt: float) -> bool:
        """更新砸地效果，返回是否完成"""
        if not self.is_smashing:
            return True
        
        self.smash_progress += dt / self.smash_duration
        
        # 冲击波在砸地瞬间产生
        if self.smash_progress >= 0.5 and self.impact_shockwave == 0:
            self.impact_shockwave = 1.0
        
        # 冲击波扩散
        if self.impact_shockwave > 0:
            self.impact_shockwave -= dt * 2
            if self.impact_shockwave < 0:
                self.impact_shockwave = 0
        
        if self.smash_progress >= 1.0:
            self.is_smashing = False
            self.smash_progress = 0.0
            return True
        return False
    
    def render_smash(self, x: float, y: float) -> None:
        """渲染砸地效果"""
        if not self.is_smashing:
            return
        
        # 举起电线的动画
        if self.smash_progress < 0.5:
            # 举起阶段
            raise_progress = self.smash_progress * 2
            wire_height = 60 + raise_progress * 40
        else:
            # 砸下阶段
            wire_height = 100 - (self.smash_progress - 0.5) * 2 * 80
        
        # 绘制电线（简化表示）
        arcade.draw_line(x, y + 40, x + 30, y + wire_height, (100, 100, 100), 6)
        arcade.draw_circle_filled(x + 30, y + wire_height, 8, (80, 80, 80))
        
        # 冲击波
        if self.impact_shockwave > 0:
            wave_radius = (1.0 - self.impact_shockwave) * 80
            alpha = int(255 * self.impact_shockwave)
            arcade.draw_circle_outline(
                x, y, wave_radius, (255, 255, 255, alpha), 3
            )


@dataclass
class MinerDigEffect:
    """矿工僵尸挖掘效果"""
    is_underground: bool = False
    dig_progress: float = 0.0
    tunnel_trail: List[Tuple[float, float]] = field(default_factory=list)
    max_trail_length: int = 20
    
    def start_dig(self, x: float, y: float) -> None:
        """开始挖掘"""
        self.is_underground = True
        self.dig_progress = 0.0
        self.tunnel_trail = [(x, y)]
    
    def update(self, dt: float, current_x: float, current_y: float) -> None:
        """更新挖掘效果"""
        if not self.is_underground:
            return
        
        # 记录隧道轨迹
        self.tunnel_trail.append((current_x, current_y))
        if len(self.tunnel_trail) > self.max_trail_length:
            self.tunnel_trail.pop(0)
    
    def emerge(self) -> None:
        """出土"""
        self.is_underground = False
        self.tunnel_trail.clear()
    
    def render_tunnel(self) -> None:
        """渲染隧道"""
        if len(self.tunnel_trail) < 2:
            return
        
        # 绘制隧道轨迹
        for i, (x, y) in enumerate(self.tunnel_trail):
            alpha = int(255 * (i / len(self.tunnel_trail)))
            size = 3 + (i / len(self.tunnel_trail)) * 5
            arcade.draw_circle_filled(x, y - 10, size, (139, 69, 19, alpha))


@dataclass
class PogoBounceState:
    """跳跳杆僵尸弹跳状态"""
    bounce_offset: float = 0.0
    bounce_speed: float = 8.0
    bounce_height: float = 20.0
    compression: float = 0.0  # 杆子压缩程度
    
    def update(self, dt: float, time: float) -> Tuple[float, float]:
        """
        更新弹跳状态
        
        Returns:
            (Y轴偏移, 杆子压缩比例)
        """
        # 弹跳周期
        phase = (time * self.bounce_speed) % (2 * math.pi)
        
        # 高度使用绝对正弦（只向上）
        height = abs(math.sin(phase)) * self.bounce_height
        
        # 杆子压缩（在最低点时压缩最大）
        cos_phase = math.cos(phase)
        self.compression = max(0, -cos_phase) * 0.3
        
        return height, self.compression
    
    def render_pogo(self, x: float, y: float, zombie_height: float) -> None:
        """渲染跳跳杆"""
        pogo_x = x
        pogo_bottom = y - zombie_height * 0.4
        pogo_top = y - zombie_height * 0.1
        
        # 杆子（考虑压缩）
        actual_height = (pogo_top - pogo_bottom) * (1.0 - self.compression)
        
        # 杆子主体
        arcade.draw_line(
            pogo_x, pogo_bottom,
            pogo_x, pogo_bottom + actual_height,
            (200, 100, 50), 4
        )
        
        # 脚踏板
        arcade.draw_rectangle_filled(
            pogo_x, pogo_bottom + actual_height,
            20, 4, (100, 100, 100)
        )
        
        # 底部弹簧
        spring_coils = 5
        spring_width = 12
        spring_height = actual_height * 0.4
        spring_bottom = pogo_bottom
        
        for i in range(spring_coils):
            t = i / (spring_coils - 1)
            coil_y = spring_bottom + t * spring_height
            width = spring_width * (0.8 + 0.2 * math.sin(t * math.pi * 4))
            arcade.draw_rectangle_filled(
                pogo_x, coil_y, width, 3, (150, 150, 150)
            )


class SpecialZombieEffects:
    """
    特殊僵尸效果管理器
    
    管理所有特殊僵尸的独特视觉效果
    """
    
    def __init__(self):
        self._pole_vault_states: Dict[int, PoleVaultState] = {}
        self._dancer_effects: Dict[int, DancerSummonEffect] = {}
        self._balloon_states: Dict[int, BalloonFloatState] = {}
        self._gargantuar_effects: Dict[int, GargantuarEffect] = {}
        self._miner_effects: Dict[int, MinerDigEffect] = {}
        self._pogo_states: Dict[int, PogoBounceState] = {}
        self._time = 0.0
    
    def update(self, dt: float) -> None:
        """更新所有效果"""
        self._time += dt
        
        # 更新舞王召唤效果
        for effect in self._dancer_effects.values():
            effect.update(dt)
        
        # 更新巨人砸地效果
        for effect in self._gargantuar_effects.values():
            effect.update(dt)
    
    # ========== 撑杆僵尸 ==========
    def start_pole_vault(self, zombie_id: int, start_x: float, target_x: float, start_y: float) -> None:
        """开始撑杆跳跃"""
        if zombie_id not in self._pole_vault_states:
            self._pole_vault_states[zombie_id] = PoleVaultState()
        self._pole_vault_states[zombie_id].start_jump(start_x, target_x, start_y)
    
    def update_pole_vault(self, zombie_id: int, dt: float) -> Tuple[float, float, bool]:
        """更新撑杆跳跃，返回(新x, 新y, 是否完成)"""
        if zombie_id not in self._pole_vault_states:
            return 0, 0, True
        return self._pole_vault_states[zombie_id].update(dt)
    
    def render_pole(self, zombie_id: int, x: float, y: float, is_flipped: bool = True) -> None:
        """渲染撑杆"""
        if zombie_id in self._pole_vault_states:
            self._pole_vault_states[zombie_id].render_pole(x, y, is_flipped)
    
    def is_pole_vaulting(self, zombie_id: int) -> bool:
        """是否正在撑杆跳跃"""
        if zombie_id in self._pole_vault_states:
            return self._pole_vault_states[zombie_id].is_jumping
        return False
    
    # ========== 舞王僵尸 ==========
    def start_dancer_summon(self, zombie_id: int) -> None:
        """开始舞王召唤"""
        if zombie_id not in self._dancer_effects:
            self._dancer_effects[zombie_id] = DancerSummonEffect()
        self._dancer_effects[zombie_id].start_summon()
    
    def render_dancer_effect(self, zombie_id: int, x: float, y: float) -> None:
        """渲染舞王召唤效果"""
        if zombie_id in self._dancer_effects:
            self._dancer_effects[zombie_id].render(x, y)
    
    def is_dancer_summoning(self, zombie_id: int) -> bool:
        """是否正在召唤"""
        if zombie_id in self._dancer_effects:
            return self._dancer_effects[zombie_id].is_summoning
        return False
    
    # ========== 气球僵尸 ==========
    def get_balloon_offset(self, zombie_id: int, dt: float) -> float:
        """获取气球漂浮偏移"""
        if zombie_id not in self._balloon_states:
            self._balloon_states[zombie_id] = BalloonFloatState()
        return self._balloon_states[zombie_id].update(dt, self._time)
    
    def pop_balloon(self, zombie_id: int) -> None:
        """击破气球"""
        if zombie_id in self._balloon_states:
            self._balloon_states[zombie_id].pop_balloon()
    
    def render_balloon(self, zombie_id: int, x: float, y: float, zombie_height: float) -> None:
        """渲染气球"""
        if zombie_id in self._balloon_states:
            self._balloon_states[zombie_id].render_balloon(x, y, zombie_height)
    
    # ========== 巨人僵尸 ==========
    def start_gargantuar_smash(self, zombie_id: int) -> None:
        """开始巨人砸地"""
        if zombie_id not in self._gargantuar_effects:
            self._gargantuar_effects[zombie_id] = GargantuarEffect()
        self._gargantuar_effects[zombie_id].start_smash()
    
    def render_gargantuar_smash(self, zombie_id: int, x: float, y: float) -> None:
        """渲染巨人砸地效果"""
        if zombie_id in self._gargantuar_effects:
            self._gargantuar_effects[zombie_id].render_smash(x, y)
    
    def is_gargantuar_smashing(self, zombie_id: int) -> bool:
        """是否正在砸地"""
        if zombie_id in self._gargantuar_effects:
            return self._gargantuar_effects[zombie_id].is_smashing
        return False
    
    # ========== 矿工僵尸 ==========
    def start_miner_dig(self, zombie_id: int, x: float, y: float) -> None:
        """开始矿工挖掘"""
        if zombie_id not in self._miner_effects:
            self._miner_effects[zombie_id] = MinerDigEffect()
        self._miner_effects[zombie_id].start_dig(x, y)
    
    def update_miner_dig(self, zombie_id: int, dt: float, x: float, y: float) -> None:
        """更新矿工挖掘"""
        if zombie_id in self._miner_effects:
            self._miner_effects[zombie_id].update(dt, x, y)
    
    def miner_emerge(self, zombie_id: int) -> None:
        """矿工出土"""
        if zombie_id in self._miner_effects:
            self._miner_effects[zombie_id].emerge()
    
    def render_miner_tunnel(self, zombie_id: int) -> None:
        """渲染矿工隧道"""
        if zombie_id in self._miner_effects:
            self._miner_effects[zombie_id].render_tunnel()
    
    def is_miner_underground(self, zombie_id: int) -> bool:
        """矿工是否在地下"""
        if zombie_id in self._miner_effects:
            return self._miner_effects[zombie_id].is_underground
        return False
    
    # ========== 跳跳僵尸 ==========
    def get_pogo_offset(self, zombie_id: int, dt: float) -> Tuple[float, float]:
        """获取跳跳杆偏移和压缩，返回(Y偏移, 压缩比例)"""
        if zombie_id not in self._pogo_states:
            self._pogo_states[zombie_id] = PogoBounceState()
        return self._pogo_states[zombie_id].update(dt, self._time)
    
    def render_pogo(self, zombie_id: int, x: float, y: float, zombie_height: float) -> None:
        """渲染跳跳杆"""
        if zombie_id in self._pogo_states:
            self._pogo_states[zombie_id].render_pogo(x, y, zombie_height)
    
    # ========== 清理 ==========
    def remove_zombie(self, zombie_id: int) -> None:
        """移除僵尸的所有效果"""
        self._pole_vault_states.pop(zombie_id, None)
        self._dancer_effects.pop(zombie_id, None)
        self._balloon_states.pop(zombie_id, None)
        self._gargantuar_effects.pop(zombie_id, None)
        self._miner_effects.pop(zombie_id, None)
        self._pogo_states.pop(zombie_id, None)
    
    def clear(self) -> None:
        """清除所有效果"""
        self._pole_vault_states.clear()
        self._dancer_effects.clear()
        self._balloon_states.clear()
        self._gargantuar_effects.clear()
        self._miner_effects.clear()
        self._pogo_states.clear()
        self._time = 0.0
