"""
动画组件 - 管理实体的动画状态
"""

from typing import Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from ..component import Component


class AnimationState(Enum):
    """动画状态枚举"""
    IDLE = auto()      # 空闲
    ATTACK = auto()    # 攻击
    WALK = auto()      # 行走/移动
    HURT = auto()      # 受击
    DEATH = auto()     # 死亡
    SPECIAL = auto()   # 特殊动作


@dataclass
class AnimationComponent(Component):
    """
    动画组件
    
    管理实体的动画状态和播放
    
    Attributes:
        animations: 动画字典 {状态: 动画对象}
        current_state: 当前动画状态
        default_state: 默认状态（动画结束后的回退状态）
        is_flipped_x: 是否水平翻转（用于面向不同方向）
        is_flipped_y: 是否垂直翻转
        scale: 缩放比例
        z_index: 渲染层级
    """
    animations: Dict[AnimationState, Any] = field(default_factory=dict)
    current_state: AnimationState = AnimationState.IDLE
    default_state: AnimationState = AnimationState.IDLE
    is_flipped_x: bool = False
    is_flipped_y: bool = False
    scale: float = 1.0
    z_index: int = 0
    
    def __post_init__(self):
        """初始化后自动播放默认动画（如果动画已存在）"""
        # 注意：此时 animations 可能还未添加，所以不自动播放
        # 动画应在添加到实体后由外部代码明确播放
        pass
    
    def add_animation(self, state: AnimationState, animation: Any) -> None:
        """
        添加动画
        
        Args:
            state: 动画状态
            animation: 动画对象
        """
        self.animations[state] = animation
    
    def play(self, state: AnimationState, force_restart: bool = False) -> bool:
        """
        播放指定状态的动画
        
        Args:
            state: 要播放的状态
            force_restart: 是否强制重新开始（即使已经在播放该状态）
            
        Returns:
            是否成功播放
        """
        if state not in self.animations:
            return False
        
        # 如果已经在播放该状态且不需要强制重启，则跳过
        if self.current_state == state and not force_restart:
            current_anim = self.animations[state]
            if current_anim.is_playing:
                return True
        
        # 停止当前动画
        self._stop_current_animation()
        
        # 切换到新状态
        self.current_state = state
        animation = self.animations[state]
        animation.play()
        
        return True
    
    def stop(self) -> None:
        """停止当前动画"""
        self._stop_current_animation()
    
    def _stop_current_animation(self) -> None:
        """停止当前播放的动画"""
        if self.current_state in self.animations:
            self.animations[self.current_state].stop()
    
    def update(self, dt: float) -> None:
        """
        更新动画
        
        Args:
            dt: 时间增量
        """
        if self.current_state in self.animations:
            animation = self.animations[self.current_state]
            animation.update(dt)
            
            # 如果动画结束且不是循环的，回到默认状态
            if not animation.is_playing and not animation.loop:
                if self.current_state != self.default_state:
                    self.play(self.default_state)
    
    def get_current_animation(self) -> Optional[Any]:
        """获取当前动画"""
        return self.animations.get(self.current_state)
    
    def get_current_texture(self):
        """获取当前帧的纹理"""
        animation = self.get_current_animation()
        if animation:
            return animation.get_current_texture()
        return None
    
    def set_flip_x(self, flipped: bool) -> None:
        """设置水平翻转"""
        self.is_flipped_x = flipped
    
    def set_flip_y(self, flipped: bool) -> None:
        """设置垂直翻转"""
        self.is_flipped_y = flipped
    
    def look_at(self, target_x: float, current_x: float) -> None:
        """
        面向目标位置
        
        Args:
            target_x: 目标X坐标
            current_x: 当前X坐标
        """
        self.is_flipped_x = target_x < current_x
    
    def is_playing(self, state: AnimationState = None) -> bool:
        """
        检查是否正在播放动画
        
        Args:
            state: 指定状态，None表示检查当前状态
            
        Returns:
            是否正在播放
        """
        if state is None:
            state = self.current_state
        
        if state in self.animations:
            return self.animations[state].is_playing
        return False
    
    def add_animation_event(self, state: AnimationState, frame_index: int, 
                           callback: Callable) -> bool:
        """
        为指定状态的动画添加帧事件
        
        Args:
            state: 动画状态
            frame_index: 帧索引
            callback: 回调函数
            
        Returns:
            是否成功添加
        """
        if state in self.animations:
            self.animations[state].add_frame_event(frame_index, callback)
            return True
        return False
