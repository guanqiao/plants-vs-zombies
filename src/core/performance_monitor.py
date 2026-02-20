"""
性能监控工具 - 实时监控游戏性能指标

包括：
- 帧率(FPS)监控
- 绘制调用计数
- 实体数量统计
- 粒子数量统计
- 内存使用追踪
"""

import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from collections import deque
import arcade


@dataclass
class PerformanceMetrics:
    """性能指标数据"""
    fps: float = 0.0
    frame_time: float = 0.0
    draw_calls: int = 0
    entity_count: int = 0
    particle_count: int = 0
    memory_usage_mb: float = 0.0
    
    # 历史数据（用于图表显示）
    fps_history: deque = field(default_factory=lambda: deque(maxlen=60))
    frame_time_history: deque = field(default_factory=lambda: deque(maxlen=60))


class PerformanceMonitor:
    """
    性能监控器
    
    单例模式，全局性能监控
    """
    _instance: Optional['PerformanceMonitor'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.metrics = PerformanceMetrics()
        
        # 帧率计算
        self._frame_count = 0
        self._last_fps_update = time.time()
        self._frame_start_time = 0.0
        
        # 绘制调用计数
        self._draw_calls = 0
        self._draw_call_loggers: List[Callable] = []
        
        # 是否显示调试信息
        self._show_debug = False
        self._show_detailed = False
        
        # 统计文本对象（缓存）
        self._text_objects: Dict[str, arcade.Text] = {}
        self._init_text_objects()
    
    def _init_text_objects(self) -> None:
        """初始化文本对象（缓存）"""
        # 使用 arcade.Text 对象缓存，避免每帧重新创建
        self._text_objects['fps'] = arcade.Text(
            "FPS: 0", 10, 570,
            arcade.color.YELLOW, 14,
            font_name=("Arial", "Microsoft YaHei")
        )
        self._text_objects['entities'] = arcade.Text(
            "Entities: 0", 10, 550,
            arcade.color.WHITE, 12,
            font_name=("Arial", "Microsoft YaHei")
        )
        self._text_objects['particles'] = arcade.Text(
            "Particles: 0", 10, 535,
            arcade.color.WHITE, 12,
            font_name=("Arial", "Microsoft YaHei")
        )
        self._text_objects['draw_calls'] = arcade.Text(
            "Draw Calls: 0", 10, 520,
            arcade.color.WHITE, 12,
            font_name=("Arial", "Microsoft YaHei")
        )
        self._text_objects['frame_time'] = arcade.Text(
            "Frame Time: 0ms", 10, 505,
            arcade.color.WHITE, 12,
            font_name=("Arial", "Microsoft YaHei")
        )
        self._text_objects['memory'] = arcade.Text(
            "Memory: 0MB", 10, 490,
            arcade.color.WHITE, 12,
            font_name=("Arial", "Microsoft YaHei")
        )
    
    def begin_frame(self) -> None:
        """开始一帧的计时"""
        self._frame_start_time = time.perf_counter()
        self._draw_calls = 0  # 重置绘制调用计数
    
    def end_frame(self) -> None:
        """结束一帧的计时"""
        frame_end_time = time.perf_counter()
        frame_time = (frame_end_time - self._frame_start_time) * 1000  # 转换为毫秒
        
        self._frame_count += 1
        self.metrics.frame_time = frame_time
        self.metrics.frame_time_history.append(frame_time)
        
        # 每秒更新一次FPS
        current_time = time.time()
        if current_time - self._last_fps_update >= 1.0:
            self.metrics.fps = self._frame_count
            self.metrics.fps_history.append(float(self._frame_count))
            self._frame_count = 0
            self._last_fps_update = current_time
            
            # 更新内存使用
            self._update_memory_usage()
        
        # 更新绘制调用数
        self.metrics.draw_calls = self._draw_calls
    
    def log_draw_call(self, count: int = 1) -> None:
        """记录绘制调用"""
        self._draw_calls += count
    
    def set_entity_count(self, count: int) -> None:
        """设置实体数量"""
        self.metrics.entity_count = count
    
    def set_particle_count(self, count: int) -> None:
        """设置粒子数量"""
        self.metrics.particle_count = count
    
    def _update_memory_usage(self) -> None:
        """更新内存使用统计"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            self.metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
        except ImportError:
            self.metrics.memory_usage_mb = 0.0
    
    def toggle_debug(self) -> None:
        """切换调试信息显示"""
        self._show_debug = not self._show_debug
    
    def toggle_detailed(self) -> None:
        """切换详细模式"""
        self._show_detailed = not self._show_detailed
    
    def render(self) -> None:
        """渲染性能监控信息"""
        if not self._show_debug:
            return
        
        # 更新文本内容
        self._text_objects['fps'].text = f"FPS: {self.metrics.fps:.0f}"
        self._text_objects['entities'].text = f"Entities: {self.metrics.entity_count}"
        self._text_objects['particles'].text = f"Particles: {self.metrics.particle_count}"
        self._text_objects['draw_calls'].text = f"Draw Calls: {self.metrics.draw_calls}"
        self._text_objects['frame_time'].text = f"Frame Time: {self.metrics.frame_time:.2f}ms"
        self._text_objects['memory'].text = f"Memory: {self.metrics.memory_usage_mb:.1f}MB"
        
        # 根据FPS设置颜色
        if self.metrics.fps >= 55:
            self._text_objects['fps'].color = arcade.color.GREEN
        elif self.metrics.fps >= 30:
            self._text_objects['fps'].color = arcade.color.YELLOW
        else:
            self._text_objects['fps'].color = arcade.color.RED
        
        # 绘制背景面板
        panel_width = 150
        panel_height = 100 if not self._show_detailed else 200
        arcade.draw_lrbt_rectangle_filled(
            5, 5 + panel_width,
            480, 480 + panel_height,
            (0, 0, 0, 150)
        )
        
        # 绘制所有文本
        self._text_objects['fps'].draw()
        
        if self._show_detailed:
            self._text_objects['entities'].draw()
            self._text_objects['particles'].draw()
            self._text_objects['draw_calls'].draw()
            self._text_objects['frame_time'].draw()
            self._text_objects['memory'].draw()
            
            # 绘制FPS历史图表
            self._render_fps_graph(5, 430, 150, 50)
    
    def _render_fps_graph(self, x: float, y: float, width: float, height: float) -> None:
        """渲染FPS历史图表"""
        if len(self.metrics.fps_history) < 2:
            return
        
        # 绘制背景
        arcade.draw_lrbt_rectangle_filled(
            x, x + width,
            y, y + height,
            (0, 0, 0, 100)
        )
        
        # 绘制FPS曲线
        history = list(self.metrics.fps_history)
        if len(history) < 2:
            return
        
        max_fps = max(history) if history else 60
        min_fps = min(history) if history else 0
        fps_range = max(1, max_fps - min_fps)
        
        points = []
        for i, fps in enumerate(history):
            px = x + (i / (len(history) - 1)) * width
            py = y + ((fps - min_fps) / fps_range) * height
            points.append((px, py))
        
        if len(points) >= 2:
            arcade.draw_line_strip(points, arcade.color.GREEN, 2)
    
    def get_metrics(self) -> PerformanceMetrics:
        """获取性能指标"""
        return self.metrics
    
    def reset(self) -> None:
        """重置监控器"""
        self.metrics = PerformanceMetrics()
        self._frame_count = 0
        self._draw_calls = 0
        self._last_fps_update = time.time()


# 全局性能监控器实例
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """获取性能监控器单例"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


# 便捷函数
def begin_frame() -> None:
    """开始一帧"""
    get_performance_monitor().begin_frame()


def end_frame() -> None:
    """结束一帧"""
    get_performance_monitor().end_frame()


def log_draw_call(count: int = 1) -> None:
    """记录绘制调用"""
    get_performance_monitor().log_draw_call(count)


def set_entity_count(count: int) -> None:
    """设置实体数量"""
    get_performance_monitor().set_entity_count(count)


def set_particle_count(count: int) -> None:
    """设置粒子数量"""
    get_performance_monitor().set_particle_count(count)


def toggle_debug() -> None:
    """切换调试显示"""
    get_performance_monitor().toggle_debug()


def render_debug_info() -> None:
    """渲染调试信息"""
    get_performance_monitor().render()
