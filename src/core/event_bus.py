from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Any, Tuple
import heapq


class EventType(Enum):
    """事件类型枚举"""
    ZOMBIE_DIED = auto()
    PLANT_DIED = auto()
    SUN_COLLECTED = auto()
    PROJECTILE_FIRED = auto()
    DAMAGE_DEALT = auto()
    GAME_OVER = auto()
    VICTORY = auto()
    WAVE_STARTED = auto()
    WAVE_COMPLETE = auto()
    PLANT_PLANTED = auto()
    ZOMBIE_SPAWNED = auto()
    EXPLOSION = auto()
    PLANT_ATTACK = auto()


@dataclass
class Event:
    """事件数据类"""
    event_type: EventType
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass(order=True)
class PrioritizedEvent:
    """带优先级的事件（用于事件队列）"""
    priority: int
    event: Event = field(compare=False)


class EventBus:
    """
    事件总线 - 发布/订阅模式实现
    
    支持功能：
    - 事件优先级
    - 事件队列（延迟处理）
    - 事件过滤器
    - 取消订阅
    """
    
    def __init__(self):
        # 监听器存储：(priority, callback)
        self._listeners: Dict[EventType, List[Tuple[int, Callable[[Event], None]]]] = {}
        # 事件队列（按优先级排序）
        self._event_queue: List[PrioritizedEvent] = []
        # 事件过滤器
        self._filters: List[Callable[[Event], bool]] = []
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None], priority: int = 0):
        """
        订阅事件
        
        Args:
            event_type: 事件类型
            callback: 回调函数
            priority: 优先级（越高越先处理，默认0）
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        
        self._listeners[event_type].append((priority, callback))
        # 按优先级排序（高优先级在前）
        self._listeners[event_type].sort(key=lambda x: x[0], reverse=True)
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """
        取消订阅事件
        
        Args:
            event_type: 事件类型
            callback: 要移除的回调函数
        """
        if event_type in self._listeners:
            # 找到并移除匹配的回调
            self._listeners[event_type] = [
                (p, cb) for p, cb in self._listeners[event_type] 
                if cb != callback
            ]
    
    def publish(self, event: Event, priority: int = 0, immediate: bool = True):
        """
        发布事件
        
        Args:
            event: 事件对象
            priority: 事件优先级（用于队列排序）
            immediate: 是否立即处理（False则加入队列）
        """
        if immediate:
            self._process_event(event)
        else:
            # 加入事件队列
            heapq.heappush(self._event_queue, PrioritizedEvent(-priority, event))
    
    def _process_event(self, event: Event):
        """
        处理单个事件
        
        Args:
            event: 事件对象
        """
        # 应用过滤器
        for filter_fn in self._filters:
            if not filter_fn(event):
                return  # 事件被过滤掉
        
        # 通知监听器（带异常捕获，防止一个处理器失败影响其他处理器）
        if event.event_type in self._listeners:
            for priority, callback in self._listeners[event.event_type][:]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"[EventBus] 事件处理器异常 ({event.event_type.name}): {e}")
    
    def process_events(self):
        """处理事件队列中的所有事件"""
        while self._event_queue:
            prioritized = heapq.heappop(self._event_queue)
            self._process_event(prioritized.event)
    
    def add_filter(self, filter_fn: Callable[[Event], bool]):
        """
        添加事件过滤器
        
        Args:
            filter_fn: 过滤器函数，返回False则阻止事件传播
        """
        self._filters.append(filter_fn)
    
    def remove_filter(self, filter_fn: Callable[[Event], bool]):
        """
        移除事件过滤器
        
        Args:
            filter_fn: 要移除的过滤器函数
        """
        if filter_fn in self._filters:
            self._filters.remove(filter_fn)
    
    def clear_filters(self):
        """清除所有过滤器"""
        self._filters.clear()
    
    def clear(self):
        """清除所有监听器和队列"""
        self._listeners.clear()
        self._event_queue.clear()
    
    def has_listeners(self, event_type: EventType) -> bool:
        """检查是否有指定类型的监听器"""
        return event_type in self._listeners and len(self._listeners[event_type]) > 0
    
    def get_queue_size(self) -> int:
        """获取事件队列大小"""
        return len(self._event_queue)
