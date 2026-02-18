from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Any


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


@dataclass
class Event:
    """事件数据类"""
    event_type: EventType
    data: Dict[str, Any] = field(default_factory=dict)


class EventBus:
    """事件总线 - 发布/订阅模式实现"""
    
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable[[Event], None]]] = {}
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """订阅事件"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """取消订阅事件"""
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(callback)
            except ValueError:
                pass
    
    def publish(self, event: Event):
        """发布事件"""
        if event.event_type in self._listeners:
            for callback in self._listeners[event.event_type][:]:
                callback(event)
    
    def clear(self):
        """清除所有监听器"""
        self._listeners.clear()
    
    def has_listeners(self, event_type: EventType) -> bool:
        """检查是否有指定类型的监听器"""
        return event_type in self._listeners and len(self._listeners[event_type]) > 0
