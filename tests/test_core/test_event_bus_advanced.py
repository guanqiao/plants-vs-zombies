"""
事件总线高级功能测试 - 事件队列和优先级
"""
import pytest
from unittest.mock import MagicMock


class TestEventBusPriority:
    """测试事件优先级功能"""

    def test_event_priority_order(self):
        """测试高优先级事件先被处理"""
        from src.core.event_bus import EventBus, Event, EventType
        
        event_bus = EventBus()
        results = []
        
        # 注册不同优先级的监听器
        def low_priority_handler(event):
            results.append('low')
        
        def high_priority_handler(event):
            results.append('high')
        
        def normal_priority_handler(event):
            results.append('normal')
        
        # 注册监听器（注意顺序：低、高、中）
        event_bus.subscribe(EventType.PLANT_PLANTED, low_priority_handler, priority=0)
        event_bus.subscribe(EventType.PLANT_PLANTED, high_priority_handler, priority=10)
        event_bus.subscribe(EventType.PLANT_PLANTED, normal_priority_handler, priority=5)
        
        # 发布事件
        event_bus.publish(Event(EventType.PLANT_PLANTED, {'plant': 'peashooter'}))
        
        # 验证处理顺序：高 -> 中 -> 低
        assert results == ['high', 'normal', 'low']

    def test_same_priority_fifo(self):
        """测试相同优先级按注册顺序处理"""
        from src.core.event_bus import EventBus, Event, EventType
        
        event_bus = EventBus()
        results = []
        
        def first_handler(event):
            results.append('first')
        
        def second_handler(event):
            results.append('second')
        
        # 相同优先级，按注册顺序
        event_bus.subscribe(EventType.ZOMBIE_SPAWNED, first_handler, priority=5)
        event_bus.subscribe(EventType.ZOMBIE_SPAWNED, second_handler, priority=5)
        
        event_bus.publish(Event(EventType.ZOMBIE_SPAWNED, {'zombie': 'normal'}))
        
        assert results == ['first', 'second']


class TestEventBusQueue:
    """测试事件队列功能"""

    def test_event_queue_basic(self):
        """测试基本事件队列功能"""
        from src.core.event_bus import EventBus, Event, EventType
        
        event_bus = EventBus()
        results = []
        
        def handler(event):
            results.append(event.data.get('value'))
        
        event_bus.subscribe(EventType.SUN_COLLECTED, handler)
        
        # 发布事件到队列（不立即处理）
        event_bus.publish(Event(EventType.SUN_COLLECTED, {'value': 1}), immediate=False)
        event_bus.publish(Event(EventType.SUN_COLLECTED, {'value': 2}), immediate=False)
        event_bus.publish(Event(EventType.SUN_COLLECTED, {'value': 3}), immediate=False)
        
        # 此时不应该有结果
        assert len(results) == 0
        
        # 处理队列
        event_bus.process_events()
        
        # 现在应该有结果
        assert results == [1, 2, 3]

    def test_event_queue_priority(self):
        """测试事件队列按优先级处理"""
        from src.core.event_bus import EventBus, Event, EventType
        
        event_bus = EventBus()
        results = []
        
        def handler(event):
            results.append(event.data.get('priority'))
        
        event_bus.subscribe(EventType.PLANT_PLANTED, handler)
        
        # 发布不同优先级的事件
        event_bus.publish(Event(EventType.PLANT_PLANTED, {'priority': 'low'}), 
                         priority=0, immediate=False)
        event_bus.publish(Event(EventType.PLANT_PLANTED, {'priority': 'high'}), 
                         priority=10, immediate=False)
        event_bus.publish(Event(EventType.PLANT_PLANTED, {'priority': 'normal'}), 
                         priority=5, immediate=False)
        
        # 处理队列
        event_bus.process_events()
        
        # 验证处理顺序
        assert results == ['high', 'normal', 'low']

    def test_mixed_immediate_and_queued(self):
        """测试混合立即处理和队列处理"""
        from src.core.event_bus import EventBus, Event, EventType
        
        event_bus = EventBus()
        results = []
        
        def handler(event):
            results.append(event.data.get('type'))
        
        event_bus.subscribe(EventType.ZOMBIE_SPAWNED, handler)
        
        # 立即处理
        event_bus.publish(Event(EventType.ZOMBIE_SPAWNED, {'type': 'immediate'}), 
                         immediate=True)
        
        # 队列处理
        event_bus.publish(Event(EventType.ZOMBIE_SPAWNED, {'type': 'queued'}), 
                         immediate=False)
        
        # 立即处理的应该已经执行
        assert 'immediate' in results
        assert 'queued' not in results
        
        # 处理队列
        event_bus.process_events()
        
        # 现在两个都应该执行了
        assert results == ['immediate', 'queued']


class TestEventBusFilters:
    """测试事件过滤器功能"""

    def test_event_filter_blocks_events(self):
        """测试事件过滤器阻止事件"""
        from src.core.event_bus import EventBus, Event, EventType
        
        event_bus = EventBus()
        results = []
        
        def handler(event):
            results.append(event.data.get('value'))
        
        # 添加过滤器（阻止value < 10的事件）
        def filter_low_values(event):
            return event.data.get('value', 0) >= 10
        
        event_bus.add_filter(filter_low_values)
        event_bus.subscribe(EventType.SUN_COLLECTED, handler)
        
        # 发布事件
        event_bus.publish(Event(EventType.SUN_COLLECTED, {'value': 5}))
        event_bus.publish(Event(EventType.SUN_COLLECTED, {'value': 15}))
        event_bus.publish(Event(EventType.SUN_COLLECTED, {'value': 8}))
        
        # 只有 >= 10 的事件被处理
        assert results == [15]

    def test_multiple_filters(self):
        """测试多个过滤器"""
        from src.core.event_bus import EventBus, Event, EventType
        
        event_bus = EventBus()
        results = []
        
        def handler(event):
            results.append(event.data.get('value'))
        
        # 添加多个过滤器
        def filter_positive(event):
            return event.data.get('value', 0) > 0
        
        def filter_even(event):
            return event.data.get('value', 0) % 2 == 0
        
        event_bus.add_filter(filter_positive)
        event_bus.add_filter(filter_even)
        event_bus.subscribe(EventType.SUN_COLLECTED, handler)
        
        # 发布事件
        event_bus.publish(Event(EventType.SUN_COLLECTED, {'value': -2}))  # 负数，被过滤
        event_bus.publish(Event(EventType.SUN_COLLECTED, {'value': 3}))   # 奇数，被过滤
        event_bus.publish(Event(EventType.SUN_COLLECTED, {'value': 4}))   # 正偶数，通过
        
        # 只有正偶数被处理
        assert results == [4]


class TestEventBusUnsubscribe:
    """测试取消订阅功能"""

    def test_unsubscribe_removes_listener(self):
        """测试取消订阅后监听器不再接收事件"""
        from src.core.event_bus import EventBus, Event, EventType
        
        event_bus = EventBus()
        results = []
        
        def handler(event):
            results.append(1)
        
        # 订阅
        event_bus.subscribe(EventType.PLANT_PLANTED, handler)
        
        # 发布事件
        event_bus.publish(Event(EventType.PLANT_PLANTED, {}))
        assert len(results) == 1
        
        # 取消订阅
        event_bus.unsubscribe(EventType.PLANT_PLANTED, handler)
        
        # 再次发布事件
        event_bus.publish(Event(EventType.PLANT_PLANTED, {}))
        assert len(results) == 1  # 不应该增加


class TestEventBusIntegration:
    """测试事件系统集成"""

    def test_event_bus_with_ecs(self):
        """测试事件系统与ECS集成"""
        from src.core.event_bus import EventBus, Event, EventType
        from src.ecs.world import World
        from src.arcade_game.entity_factory import EntityFactory
        from src.ecs.components.plant import PlantType
        
        event_bus = EventBus()
        world = World()
        factory = EntityFactory(world)
        
        events_received = []
        
        def on_plant_placed(event):
            events_received.append(event.data)
        
        event_bus.subscribe(EventType.PLANT_PLANTED, on_plant_placed)
        
        # 创建植物（触发事件）
        plant = factory.create_plant(PlantType.PEASHOOTER, x=100, y=100, row=0, col=0)
        
        # 手动发布事件（模拟种植系统）
        event_bus.publish(Event(EventType.PLANT_PLANTED, {
            'plant_type': PlantType.PEASHOOTER,
            'position': (100, 100),
            'entity_id': plant
        }))
        
        assert len(events_received) == 1
        assert events_received[0]['plant_type'] == PlantType.PEASHOOTER
