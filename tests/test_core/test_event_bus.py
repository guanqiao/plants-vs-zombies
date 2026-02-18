import pytest
from dataclasses import is_dataclass


class TestEventType:
    """事件类型枚举测试"""

    def test_event_type_enum_exists(self):
        """测试事件类型枚举存在"""
        from src.core.event_bus import EventType
        
        assert hasattr(EventType, 'ZOMBIE_DIED')
        assert hasattr(EventType, 'PLANT_DIED')
        assert hasattr(EventType, 'SUN_COLLECTED')
        assert hasattr(EventType, 'PROJECTILE_FIRED')
        assert hasattr(EventType, 'DAMAGE_DEALT')
        assert hasattr(EventType, 'GAME_OVER')
        assert hasattr(EventType, 'VICTORY')


class TestEvent:
    """事件数据类测试"""

    def test_event_is_dataclass(self):
        """测试Event是数据类"""
        from src.core.event_bus import Event
        
        assert is_dataclass(Event)

    def test_event_initialization(self):
        """测试事件初始化"""
        from src.core.event_bus import Event, EventType
        
        event = Event(EventType.ZOMBIE_DIED, {'x': 100, 'y': 200, 'score': 50})
        
        assert event.event_type == EventType.ZOMBIE_DIED
        assert event.data['x'] == 100
        assert event.data['y'] == 200
        assert event.data['score'] == 50

    def test_event_default_data(self):
        """测试事件默认数据为空字典"""
        from src.core.event_bus import Event, EventType
        
        event = Event(EventType.SUN_COLLECTED)
        
        assert event.data == {}


class TestEventBus:
    """事件总线测试"""

    def test_event_bus_initialization(self):
        """测试事件总线初始化"""
        from src.core.event_bus import EventBus
        
        bus = EventBus()
        
        assert bus is not None
        assert hasattr(bus, '_listeners')

    def test_subscribe_single_listener(self):
        """测试订阅单个监听器"""
        from src.core.event_bus import EventBus, Event, EventType
        
        bus = EventBus()
        call_count = {'count': 0}
        
        def callback(event: Event):
            call_count['count'] += 1
        
        bus.subscribe(EventType.ZOMBIE_DIED, callback)
        bus.publish(Event(EventType.ZOMBIE_DIED, {'score': 100}))
        
        assert call_count['count'] == 1

    def test_subscribe_multiple_listeners(self):
        """测试订阅多个监听器"""
        from src.core.event_bus import EventBus, Event, EventType
        
        bus = EventBus()
        results = []
        
        def callback1(event: Event):
            results.append('callback1')
        
        def callback2(event: Event):
            results.append('callback2')
        
        bus.subscribe(EventType.ZOMBIE_DIED, callback1)
        bus.subscribe(EventType.ZOMBIE_DIED, callback2)
        bus.publish(Event(EventType.ZOMBIE_DIED))
        
        assert len(results) == 2
        assert 'callback1' in results
        assert 'callback2' in results

    def test_publish_no_listeners(self):
        """测试发布事件时没有监听器"""
        from src.core.event_bus import EventBus, Event, EventType
        
        bus = EventBus()
        
        bus.publish(Event(EventType.ZOMBIE_DIED))
        
        assert True

    def test_unsubscribe(self):
        """测试取消订阅"""
        from src.core.event_bus import EventBus, Event, EventType
        
        bus = EventBus()
        call_count = {'count': 0}
        
        def callback(event: Event):
            call_count['count'] += 1
        
        bus.subscribe(EventType.ZOMBIE_DIED, callback)
        bus.unsubscribe(EventType.ZOMBIE_DIED, callback)
        bus.publish(Event(EventType.ZOMBIE_DIED))
        
        assert call_count['count'] == 0

    def test_unsubscribe_nonexistent(self):
        """测试取消不存在的订阅"""
        from src.core.event_bus import EventBus, Event, EventType
        
        bus = EventBus()
        
        def callback(event: Event):
            pass
        
        bus.unsubscribe(EventType.ZOMBIE_DIED, callback)
        
        assert True

    def test_different_event_types_isolated(self):
        """测试不同事件类型隔离"""
        from src.core.event_bus import EventBus, Event, EventType
        
        bus = EventBus()
        zombie_calls = []
        sun_calls = []
        
        def zombie_callback(event: Event):
            zombie_calls.append(1)
        
        def sun_callback(event: Event):
            sun_calls.append(1)
        
        bus.subscribe(EventType.ZOMBIE_DIED, zombie_callback)
        bus.subscribe(EventType.SUN_COLLECTED, sun_callback)
        
        bus.publish(Event(EventType.ZOMBIE_DIED))
        
        assert len(zombie_calls) == 1
        assert len(sun_calls) == 0

    def test_event_data_passed_to_callback(self):
        """测试事件数据传递给回调"""
        from src.core.event_bus import EventBus, Event, EventType
        
        bus = EventBus()
        received_data = {}
        
        def callback(event: Event):
            received_data.update(event.data)
        
        bus.subscribe(EventType.DAMAGE_DEALT, callback)
        bus.publish(Event(EventType.DAMAGE_DEALT, {'damage': 50, 'target': 'zombie'}))
        
        assert received_data['damage'] == 50
        assert received_data['target'] == 'zombie'

    def test_clear_all_listeners(self):
        """测试清除所有监听器"""
        from src.core.event_bus import EventBus, Event, EventType
        
        bus = EventBus()
        call_count = {'count': 0}
        
        def callback(event: Event):
            call_count['count'] += 1
        
        bus.subscribe(EventType.ZOMBIE_DIED, callback)
        bus.subscribe(EventType.SUN_COLLECTED, callback)
        bus.clear()
        
        bus.publish(Event(EventType.ZOMBIE_DIED))
        bus.publish(Event(EventType.SUN_COLLECTED))
        
        assert call_count['count'] == 0

    def test_has_listeners(self):
        """测试检查是否有监听器"""
        from src.core.event_bus import EventBus, EventType
        
        bus = EventBus()
        
        assert not bus.has_listeners(EventType.ZOMBIE_DIED)
        
        bus.subscribe(EventType.ZOMBIE_DIED, lambda e: None)
        
        assert bus.has_listeners(EventType.ZOMBIE_DIED)
