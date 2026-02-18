"""
系统模块 - ECS架构中的逻辑处理器

系统包含处理特定类型组件的逻辑
系统批量处理拥有特定组件组合的实体
"""

from abc import ABC, abstractmethod
from typing import List, Type
from .component import ComponentManager


class System(ABC):
    """
    系统基类
    
    子类需要实现update方法来处理逻辑
    """
    
    def __init__(self, priority: int = 0):
        """
        初始化系统
        
        Args:
            priority: 系统执行优先级，数字越小优先级越高
        """
        self.priority = priority
        self.enabled = True
    
    @abstractmethod
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """
        更新系统逻辑
        
        Args:
            dt: 时间增量（秒）
            component_manager: 组件管理器，用于查询组件
        """
        pass
    
    def on_enable(self) -> None:
        """系统被启用时调用"""
        pass
    
    def on_disable(self) -> None:
        """系统被禁用时调用"""
        pass


class SystemManager:
    """
    系统管理器
    
    负责管理所有系统的注册、更新和执行顺序
    """
    
    def __init__(self):
        self._systems: List[System] = []
        self._component_manager: ComponentManager = None
    
    def set_component_manager(self, component_manager: ComponentManager) -> None:
        """设置组件管理器"""
        self._component_manager = component_manager
    
    def add_system(self, system: System) -> None:
        """添加系统"""
        self._systems.append(system)
        # 按优先级排序
        self._systems.sort(key=lambda s: s.priority)
        
        if system.enabled:
            system.on_enable()
    
    def remove_system(self, system: System) -> None:
        """移除系统"""
        if system in self._systems:
            system.on_disable()
            self._systems.remove(system)
    
    def update(self, dt: float) -> None:
        """更新所有启用的系统"""
        if self._component_manager is None:
            return
            
        for system in self._systems:
            if system.enabled:
                system.update(dt, self._component_manager)
    
    def get_systems(self) -> List[System]:
        """获取所有系统"""
        return self._systems.copy()
    
    def clear(self) -> None:
        """清空所有系统"""
        for system in self._systems:
            system.on_disable()
        self._systems.clear()