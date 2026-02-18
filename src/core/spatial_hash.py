"""
空间哈希系统 - 用于高效的碰撞检测

使用空间哈希网格来快速查找附近的实体
比四叉树更简单高效，适合2D游戏
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass


@dataclass
class AABB:
    """轴对齐包围盒"""
    x: float
    y: float
    width: float
    height: float
    
    @property
    def left(self) -> float:
        return self.x
    
    @property
    def right(self) -> float:
        return self.x + self.width
    
    @property
    def top(self) -> float:
        return self.y + self.height
    
    @property
    def bottom(self) -> float:
        return self.y
    
    def intersects(self, other: 'AABB') -> bool:
        """检查两个AABB是否相交"""
        return (self.left < other.right and
                self.right > other.left and
                self.bottom < other.top and
                self.top > other.bottom)
    
    def contains_point(self, x: float, y: float) -> bool:
        """检查点是否在AABB内"""
        return (self.left <= x <= self.right and
                self.bottom <= y <= self.top)


class SpatialHash:
    """
    空间哈希网格
    
    将世界划分为固定大小的网格单元，
    每个单元存储其中的实体，加速邻近查询
    """
    
    def __init__(self, cell_size: float = 100.0):
        """
        初始化空间哈希
        
        Args:
            cell_size: 网格单元大小（像素）
        """
        self.cell_size = cell_size
        self.grid: Dict[Tuple[int, int], Set[int]] = {}
        self.entity_cells: Dict[int, Set[Tuple[int, int]]] = {}
    
    def _get_cell_coords(self, x: float, y: float) -> Tuple[int, int]:
        """
        获取坐标所在的网格单元坐标
        
        Args:
            x: X坐标
            y: Y坐标
            
        Returns:
            网格单元坐标 (cell_x, cell_y)
        """
        return (int(x // self.cell_size), int(y // self.cell_size))
    
    def _get_cells_for_aabb(self, aabb: AABB) -> List[Tuple[int, int]]:
        """
        获取AABB覆盖的所有网格单元
        
        Args:
            aabb: 轴对齐包围盒
            
        Returns:
            网格单元坐标列表
        """
        cells = []
        
        min_cell = self._get_cell_coords(aabb.left, aabb.bottom)
        max_cell = self._get_cell_coords(aabb.right, aabb.top)
        
        for x in range(min_cell[0], max_cell[0] + 1):
            for y in range(min_cell[1], max_cell[1] + 1):
                cells.append((x, y))
        
        return cells
    
    def insert(self, entity_id: int, aabb: AABB) -> None:
        """
        插入实体到空间哈希
        
        Args:
            entity_id: 实体ID
            aabb: 实体的包围盒
        """
        # 获取实体覆盖的所有网格单元
        cells = self._get_cells_for_aabb(aabb)
        
        # 记录实体所在的单元
        self.entity_cells[entity_id] = set(cells)
        
        # 将实体添加到各个单元
        for cell in cells:
            if cell not in self.grid:
                self.grid[cell] = set()
            self.grid[cell].add(entity_id)
    
    def remove(self, entity_id: int) -> None:
        """
        从空间哈希中移除实体
        
        Args:
            entity_id: 实体ID
        """
        if entity_id not in self.entity_cells:
            return
        
        # 从所有单元中移除
        for cell in self.entity_cells[entity_id]:
            if cell in self.grid:
                self.grid[cell].discard(entity_id)
                # 清理空单元
                if not self.grid[cell]:
                    del self.grid[cell]
        
        # 移除实体记录
        del self.entity_cells[entity_id]
    
    def update(self, entity_id: int, aabb: AABB) -> None:
        """
        更新实体的位置
        
        Args:
            entity_id: 实体ID
            aabb: 新的包围盒
        """
        # 先移除再重新插入
        self.remove(entity_id)
        self.insert(entity_id, aabb)
    
    def query_point(self, x: float, y: float) -> List[int]:
        """
        查询点所在的网格单元中的所有实体
        
        Args:
            x: X坐标
            y: Y坐标
            
        Returns:
            实体ID列表
        """
        cell = self._get_cell_coords(x, y)
        
        if cell in self.grid:
            return list(self.grid[cell])
        
        return []
    
    def query_aabb(self, aabb: AABB) -> List[int]:
        """
        查询与AABB相交的所有网格单元中的实体
        
        Args:
            aabb: 查询的包围盒
            
        Returns:
            实体ID列表（去重）
        """
        cells = self._get_cells_for_aabb(aabb)
        entities: Set[int] = set()
        
        for cell in cells:
            if cell in self.grid:
                entities.update(self.grid[cell])
        
        return list(entities)
    
    def query_radius(self, x: float, y: float, radius: float) -> List[int]:
        """
        查询圆形范围内的所有实体
        
        Args:
            x: 圆心X坐标
            y: 圆心Y坐标
            radius: 半径
            
        Returns:
            实体ID列表
        """
        # 创建查询AABB
        query_aabb = AABB(
            x - radius,
            y - radius,
            radius * 2,
            radius * 2
        )
        
        return self.query_aabb(query_aabb)
    
    def get_nearby_entities(self, entity_id: int, radius: float) -> List[int]:
        """
        获取指定实体附近的其他实体
        
        Args:
            entity_id: 实体ID
            radius: 查询半径
            
        Returns:
            附近实体ID列表（不包含自身）
        """
        if entity_id not in self.entity_cells:
            return []
        
        # 获取实体所在的第一个单元（近似位置）
        cells = self.entity_cells[entity_id]
        if not cells:
            return []
        
        cell = next(iter(cells))
        cell_x, cell_y = cell
        
        # 计算查询范围（以单元为单位）
        cell_radius = int(radius / self.cell_size) + 1
        
        entities: Set[int] = set()
        
        # 查询周围单元
        for dx in range(-cell_radius, cell_radius + 1):
            for dy in range(-cell_radius, cell_radius + 1):
                check_cell = (cell_x + dx, cell_y + dy)
                if check_cell in self.grid:
                    entities.update(self.grid[check_cell])
        
        # 移除自身
        entities.discard(entity_id)
        
        return list(entities)
    
    def clear(self) -> None:
        """清空空间哈希"""
        self.grid.clear()
        self.entity_cells.clear()
    
    def get_stats(self) -> dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'cell_size': self.cell_size,
            'total_cells': len(self.grid),
            'total_entities': len(self.entity_cells),
            'avg_entities_per_cell': (
                sum(len(entities) for entities in self.grid.values()) / len(self.grid)
                if self.grid else 0
            )
        }


class ObjectPool:
    """
    对象池
    
    用于重用频繁创建和销毁的对象，减少内存分配
    """
    
    def __init__(self, factory_func, reset_func=None, initial_size: int = 10):
        """
        初始化对象池
        
        Args:
            factory_func: 创建新对象的工厂函数
            reset_func: 重置对象的函数
            initial_size: 初始池大小
        """
        self.factory_func = factory_func
        self.reset_func = reset_func
        self.available: List = []
        self.in_use: List = []
        
        # 预创建对象
        for _ in range(initial_size):
            obj = factory_func()
            self.available.append(obj)
    
    def acquire(self) -> object:
        """
        获取一个对象
        
        Returns:
            对象实例
        """
        if self.available:
            obj = self.available.pop()
        else:
            # 池为空，创建新对象
            obj = self.factory_func()
        
        self.in_use.append(obj)
        
        # 重置对象
        if self.reset_func:
            self.reset_func(obj)
        
        return obj
    
    def release(self, obj: object) -> None:
        """
        释放对象回池
        
        Args:
            obj: 要释放的对象
        """
        if obj in self.in_use:
            self.in_use.remove(obj)
            self.available.append(obj)
    
    def release_all(self) -> None:
        """释放所有正在使用的对象"""
        for obj in list(self.in_use):
            self.release(obj)
    
    def get_stats(self) -> dict:
        """
        获取统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'available': len(self.available),
            'in_use': len(self.in_use),
            'total': len(self.available) + len(self.in_use)
        }


class PerformanceMonitor:
    """
    性能监控器
    
    用于监控游戏性能指标
    """
    
    def __init__(self, history_size: int = 60):
        """
        初始化性能监控器
        
        Args:
            history_size: 历史记录大小
        """
        self.history_size = history_size
        self.fps_history: List[float] = []
        self.frame_time_history: List[float] = []
        self.entity_count_history: List[int] = []
        self.collision_check_history: List[int] = []
    
    def update(self, dt: float, entity_count: int, collision_checks: int) -> None:
        """
        更新性能数据
        
        Args:
            dt: 帧时间
            entity_count: 实体数量
            collision_checks: 碰撞检测次数
        """
        fps = 1.0 / dt if dt > 0 else 0
        
        self.fps_history.append(fps)
        self.frame_time_history.append(dt * 1000)  # 转换为毫秒
        self.entity_count_history.append(entity_count)
        self.collision_check_history.append(collision_checks)
        
        # 限制历史记录大小
        if len(self.fps_history) > self.history_size:
            self.fps_history.pop(0)
            self.frame_time_history.pop(0)
            self.entity_count_history.pop(0)
            self.collision_check_history.pop(0)
    
    def get_average_fps(self) -> float:
        """获取平均FPS"""
        if not self.fps_history:
            return 0
        return sum(self.fps_history) / len(self.fps_history)
    
    def get_average_frame_time(self) -> float:
        """获取平均帧时间（毫秒）"""
        if not self.frame_time_history:
            return 0
        return sum(self.frame_time_history) / len(self.frame_time_history)
    
    def get_stats(self) -> dict:
        """
        获取性能统计
        
        Returns:
            性能统计字典
        """
        return {
            'avg_fps': self.get_average_fps(),
            'avg_frame_time_ms': self.get_average_frame_time(),
            'current_entity_count': self.entity_count_history[-1] if self.entity_count_history else 0,
            'avg_entity_count': (
                sum(self.entity_count_history) / len(self.entity_count_history)
                if self.entity_count_history else 0
            ),
            'avg_collision_checks': (
                sum(self.collision_check_history) / len(self.collision_check_history)
                if self.collision_check_history else 0
            )
        }
    
    def clear(self) -> None:
        """清空历史记录"""
        self.fps_history.clear()
        self.frame_time_history.clear()
        self.entity_count_history.clear()
        self.collision_check_history.clear()
