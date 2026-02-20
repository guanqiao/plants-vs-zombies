"""
植物行为系统 - 处理植物的攻击和特殊行为
"""

from ..system import System
from ..component import ComponentManager
from ..components import (
    TransformComponent, PlantComponent, GridPositionComponent,
    ProjectileType, PlantTypeComponent, PlantType, HealthComponent,
    AnimationComponent, AnimationState
)
from ...core.event_bus import EventBus, Event, EventType


class PlantBehaviorSystem(System):
    """
    植物行为系统
    
    处理植物的攻击逻辑和特殊行为
    - 豌豆射手：发射豌豆
    - 向日葵：产生阳光
    - 樱桃炸弹：爆炸
    - 土豆雷：埋设后爆炸
    - 大嘴花：吞噬僵尸
    等
    """
    
    # 射手类植物类型（单行射击）
    SHOOTER_PLANTS = {
        PlantType.PEASHOOTER,
        PlantType.SNOW_PEA,
        PlantType.REPEATER,
        # 注意：THREEPEATER 不在此列表中，因为它需要特殊处理（三行射击）
    }
    
    # 爆炸类植物配置
    CHERRY_EXPLOSION_RADIUS = 150  # 樱桃炸弹爆炸半径
    CHERRY_EXPLOSION_DAMAGE = 500  # 樱桃炸弹伤害
    POTATO_EXPLOSION_RADIUS = 40   # 土豆雷爆炸半径
    POTATO_EXPLOSION_DAMAGE = 500  # 土豆雷伤害
    POTATO_ARM_TIME = 15.0         # 土豆雷武装时间（秒）
    
    # 大嘴花配置
    CHOMPER_RANGE = 50             # 大嘴花攻击范围
    CHOMPER_DAMAGE = 1000          # 大嘴花伤害（秒杀）
    CHOMPER_CHEW_TIME = 42.0       # 大嘴花咀嚼时间（秒）
    
    def __init__(self, entity_factory, event_bus: EventBus = None, priority: int = 40):
        super().__init__(priority)
        self.entity_factory = entity_factory
        self.event_bus = event_bus
        
        self._potato_mine_states = {}
        self._chomper_states = {}
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """更新植物行为"""
        # 获取所有植物实体
        entities = component_manager.query(
            TransformComponent, PlantComponent, GridPositionComponent
        )
        
        # 清理已销毁实体的状态（防止内存泄漏）
        self._cleanup_states(entities)
        
        for entity_id in entities:
            transform = component_manager.get_component(entity_id, TransformComponent)
            plant = component_manager.get_component(entity_id, PlantComponent)
            grid_pos = component_manager.get_component(entity_id, GridPositionComponent)
            
            if not all([transform, plant, grid_pos]):
                continue
            
            # 更新攻击计时器
            plant.update_timer(dt)
            
            # 处理特殊植物状态更新
            self._update_special_plants(entity_id, dt, component_manager)
            
            # 获取植物类型
            plant_type_comp = component_manager.get_component(entity_id, PlantTypeComponent)
            if not plant_type_comp:
                continue
            
            plant_type = plant_type_comp.plant_type
            
            # 土豆雷需要特殊处理（不依赖can_attack）
            if plant_type == PlantType.POTATO_MINE:
                self._check_potato_mine(entity_id, transform, grid_pos, component_manager)
                continue
            
            # 处理攻击逻辑
            if plant.can_attack():
                self._handle_attack(entity_id, transform, plant, grid_pos, component_manager, dt)
    
    def _cleanup_states(self, active_entities: list) -> None:
        """
        清理已销毁实体的状态
        
        防止内存泄漏，只保留仍然存在的实体的状态
        """
        active_set = set(active_entities)
        
        # 清理土豆雷状态
        self._potato_mine_states = {
            k: v for k, v in self._potato_mine_states.items() 
            if k in active_set
        }
        
        # 清理大嘴花状态
        self._chomper_states = {
            k: v for k, v in self._chomper_states.items() 
            if k in active_set
        }
    
    def _update_special_plants(self, entity_id: int, dt: float, 
                               component_manager: ComponentManager) -> None:
        """更新特殊植物状态"""
        # 更新土豆雷武装计时器
        if entity_id in self._potato_mine_states:
            state = self._potato_mine_states[entity_id]
            if not state['armed']:
                state['timer'] += dt
                if state['timer'] >= self.POTATO_ARM_TIME:
                    state['armed'] = True
        
        # 更新大嘴花咀嚼计时器
        if entity_id in self._chomper_states:
            state = self._chomper_states[entity_id]
            if state['chewing']:
                state['timer'] -= dt
                if state['timer'] <= 0:
                    state['chewing'] = False
    
    def _handle_attack(self, entity_id: int, transform, plant, grid_pos, 
                       component_manager: ComponentManager, dt: float) -> None:
        """处理植物攻击"""
        plant_type_comp = component_manager.get_component(entity_id, PlantTypeComponent)
        if not plant_type_comp:
            return
        
        plant_type = plant_type_comp.plant_type
        
        # 根据植物类型处理不同攻击方式
        if plant_type in self.SHOOTER_PLANTS:
            # 检查同行是否有僵尸
            if self._has_zombie_in_row(grid_pos.row, component_manager):
                # 发射投射物
                self._shoot_projectile(entity_id, transform, grid_pos, plant_type, component_manager)
                plant.start_cooldown()
        
        # 特殊植物处理
        elif plant_type == PlantType.SUNFLOWER:
            # 向日葵不产生投射物，而是产生阳光
            # 这个逻辑在SunSystem中处理
            pass
        
        elif plant_type == PlantType.CHERRY_BOMB:
            # 樱桃炸弹：立即爆炸
            self._explode_cherry_bomb(entity_id, transform, component_manager)
        
        elif plant_type == PlantType.POTATO_MINE:
            # 土豆雷：检查是否武装并触发
            self._check_potato_mine(entity_id, transform, grid_pos, component_manager)
        
        elif plant_type == PlantType.CHOMPER:
            # 大嘴花：吞噬僵尸
            self._chomper_eat(entity_id, transform, grid_pos, component_manager)
        
        elif plant_type == PlantType.THREEPEATER:
            # 三线射手：检查三行是否有僵尸
            if self._has_zombie_in_three_rows(grid_pos.row, component_manager):
                # 发射三行投射物
                self._shoot_three_projectiles(transform, grid_pos)
                plant.start_cooldown()
        
        elif plant_type in (PlantType.MELON_PULT, PlantType.WINTER_MELON):
            # 西瓜投手：抛物线攻击
            if self._has_zombie_in_row(grid_pos.row, component_manager):
                self._shoot_melon(transform, grid_pos, plant_type)
                plant.start_cooldown()
        
        elif plant_type == PlantType.SPIKEWEED:
            # 地刺：接触伤害
            self._spikeweed_damage(entity_id, transform, grid_pos, component_manager)
        
        elif plant_type == PlantType.MAGNET_SHROOM:
            # 磁力菇：吸走金属防具
            self._magnet_shroom_effect(entity_id, transform, grid_pos, component_manager)
    
    def _has_zombie_in_row(self, row: int, component_manager: ComponentManager) -> bool:
        """
        检查指定行是否有僵尸
        
        Args:
            row: 行索引
            component_manager: 组件管理器
            
        Returns:
            是否有僵尸在该行
        """
        from ..components import ZombieComponent
        
        # 获取所有僵尸
        zombies = component_manager.query(TransformComponent, ZombieComponent, GridPositionComponent)
        
        for zombie_id in zombies:
            zombie_grid = component_manager.get_component(zombie_id, GridPositionComponent)
            if zombie_grid and zombie_grid.row == row:
                return True
        
        return False
    
    def _shoot_projectile(self, entity_id: int, transform, grid_pos, plant_type, 
                         component_manager: ComponentManager) -> None:
        """发射投射物"""
        # 播放攻击动画
        anim_comp = component_manager.get_component(entity_id, AnimationComponent)
        if anim_comp:
            anim_comp.play(AnimationState.ATTACK)
        
        # 确定投射物类型
        if plant_type == PlantType.SNOW_PEA:
            projectile_type = ProjectileType.FROZEN_PEA
        else:
            projectile_type = ProjectileType.PEA
        
        # 创建投射物
        self.entity_factory.create_projectile(
            projectile_type,
            transform.x + 30,  # 从植物右侧发射
            transform.y,
            grid_pos.row
        )
    
    def _shoot_three_projectiles(self, transform, grid_pos) -> None:
        """
        三线射手发射三行投射物
        
        Args:
            transform: 植物变换组件
            grid_pos: 网格位置组件
        """
        # 发射到当前行和上下两行
        for row_offset in [-1, 0, 1]:
            target_row = grid_pos.row + row_offset
            if 0 <= target_row < 5:  # 确保在有效范围内
                self.entity_factory.create_projectile(
                    ProjectileType.PEA,
                    transform.x + 30,
                    transform.y + row_offset * 100,  # 调整Y坐标到对应行
                    target_row
                )
    
    def _explode_cherry_bomb(self, entity_id: int, transform, 
                             component_manager: ComponentManager) -> None:
        """
        樱桃炸弹爆炸
        
        对爆炸范围内的所有僵尸造成伤害并销毁自己
        """
        from ..components import ZombieComponent
        zombies = component_manager.query(TransformComponent, ZombieComponent)
        
        damaged_zombies = []
        
        for zombie_id in zombies:
            zombie_transform = component_manager.get_component(zombie_id, TransformComponent)
            if not zombie_transform:
                continue
            
            dx = zombie_transform.x - transform.x
            dy = zombie_transform.y - transform.y
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= self.CHERRY_EXPLOSION_RADIUS:
                zombie_health = component_manager.get_component(zombie_id, HealthComponent)
                if zombie_health:
                    zombie_health.take_damage(self.CHERRY_EXPLOSION_DAMAGE)
                    damaged_zombies.append((zombie_id, zombie_transform))
        
        if self.event_bus:
            self.event_bus.publish(Event(
                EventType.EXPLOSION,
                {
                    'x': transform.x,
                    'y': transform.y,
                    'radius': self.CHERRY_EXPLOSION_RADIUS,
                    'damage': self.CHERRY_EXPLOSION_DAMAGE,
                    'explosion_type': 'cherry_bomb'
                }
            ))
            
            for zombie_id, zombie_transform in damaged_zombies:
                self.event_bus.publish(Event(
                    EventType.DAMAGE_DEALT,
                    {
                        'x': zombie_transform.x,
                        'y': zombie_transform.y,
                        'damage': self.CHERRY_EXPLOSION_DAMAGE,
                        'damage_type': 'fire',
                        'target_id': zombie_id
                    }
                ))
        
        plant_health = component_manager.get_component(entity_id, HealthComponent)
        if plant_health:
            plant_health.take_damage(plant_health.current)
    
    def _check_potato_mine(self, entity_id: int, transform, grid_pos,
                           component_manager: ComponentManager) -> None:
        """
        检查土豆雷状态
        
        - 如果未武装，开始武装计时
        - 如果已武装，检查是否有僵尸触发
        """
        from ..components import ZombieComponent
        
        # 初始化状态
        if entity_id not in self._potato_mine_states:
            self._potato_mine_states[entity_id] = {'armed': False, 'timer': 0.0}
        
        state = self._potato_mine_states[entity_id]
        
        # 如果已武装，检查触发
        if state['armed']:
            # 检查范围内是否有僵尸
            zombies = component_manager.query(TransformComponent, ZombieComponent)
            
            for zombie_id in zombies:
                zombie_transform = component_manager.get_component(zombie_id, TransformComponent)
                zombie_grid = component_manager.get_component(zombie_id, GridPositionComponent)
                
                if not zombie_transform or not zombie_grid:
                    continue
                
                # 检查是否在同一行且距离足够近
                if zombie_grid.row == grid_pos.row:
                    dx = zombie_transform.x - transform.x
                    if abs(dx) <= self.POTATO_EXPLOSION_RADIUS:
                        # 触发爆炸
                        self._explode_potato_mine(entity_id, transform, component_manager)
                        return
    
    def _explode_potato_mine(self, entity_id: int, transform,
                             component_manager: ComponentManager) -> None:
        """土豆雷爆炸"""
        from ..components import ZombieComponent
        
        zombies = component_manager.query(TransformComponent, ZombieComponent, GridPositionComponent)
        grid_pos = component_manager.get_component(entity_id, GridPositionComponent)
        
        damaged_zombies = []
        
        for zombie_id in zombies:
            zombie_transform = component_manager.get_component(zombie_id, TransformComponent)
            zombie_grid = component_manager.get_component(zombie_id, GridPositionComponent)
            
            if not zombie_transform or not zombie_grid:
                continue
            
            if zombie_grid.row == grid_pos.row:
                dx = zombie_transform.x - transform.x
                if abs(dx) <= self.POTATO_EXPLOSION_RADIUS:
                    zombie_health = component_manager.get_component(zombie_id, HealthComponent)
                    if zombie_health:
                        zombie_health.take_damage(self.POTATO_EXPLOSION_DAMAGE)
                        damaged_zombies.append((zombie_id, zombie_transform))
        
        if self.event_bus:
            self.event_bus.publish(Event(
                EventType.EXPLOSION,
                {
                    'x': transform.x,
                    'y': transform.y,
                    'radius': self.POTATO_EXPLOSION_RADIUS,
                    'damage': self.POTATO_EXPLOSION_DAMAGE,
                    'explosion_type': 'potato_mine'
                }
            ))
            
            for zombie_id, zombie_transform in damaged_zombies:
                self.event_bus.publish(Event(
                    EventType.DAMAGE_DEALT,
                    {
                        'x': zombie_transform.x,
                        'y': zombie_transform.y,
                        'damage': self.POTATO_EXPLOSION_DAMAGE,
                        'damage_type': 'fire',
                        'target_id': zombie_id
                    }
                ))
        
        plant_health = component_manager.get_component(entity_id, HealthComponent)
        if plant_health:
            plant_health.take_damage(plant_health.current)
        
        if entity_id in self._potato_mine_states:
            del self._potato_mine_states[entity_id]
    
    def _chomper_eat(self, entity_id: int, transform, grid_pos,
                     component_manager: ComponentManager) -> None:
        """
        大嘴花吞噬僵尸
        
        - 如果正在咀嚼，不能攻击
        - 吞噬范围内的僵尸（秒杀）
        - 进入咀嚼状态
        """
        from ..components import ZombieComponent
        
        # 初始化状态
        if entity_id not in self._chomper_states:
            self._chomper_states[entity_id] = {'chewing': False, 'timer': 0.0}
        
        state = self._chomper_states[entity_id]
        
        # 如果正在咀嚼，不能攻击
        if state['chewing']:
            return
        
        # 查找范围内的僵尸
        zombies = component_manager.query(TransformComponent, ZombieComponent, GridPositionComponent)
        
        for zombie_id in zombies:
            zombie_transform = component_manager.get_component(zombie_id, TransformComponent)
            zombie_grid = component_manager.get_component(zombie_id, GridPositionComponent)
            
            if not zombie_transform or not zombie_grid:
                continue
            
            # 检查是否在同一行且在攻击范围内
            if zombie_grid.row == grid_pos.row:
                dx = zombie_transform.x - transform.x
                # 僵尸必须在植物前方（右侧）且在范围内
                if 0 < dx <= self.CHOMPER_RANGE:
                    # 吞噬僵尸（造成大量伤害）
                    zombie_health = component_manager.get_component(zombie_id, HealthComponent)
                    if zombie_health:
                        zombie_health.take_damage(self.CHOMPER_DAMAGE)
                    
                    # 进入咀嚼状态
                    state['chewing'] = True
                    state['timer'] = self.CHOMPER_CHEW_TIME
                    break
    
    def _has_zombie_in_three_rows(self, row: int, component_manager: ComponentManager) -> bool:
        """
        检查三行（当前行和上下行）是否有僵尸
        
        Args:
            row: 中心行索引
            component_manager: 组件管理器
            
        Returns:
            是否有僵尸在这三行中的任意一行
        """
        from ..components import ZombieComponent
        
        # 检查三行
        for row_offset in [-1, 0, 1]:
            target_row = row + row_offset
            if 0 <= target_row < 5:  # 确保在有效范围内
                if self._has_zombie_in_row(target_row, component_manager):
                    return True
        
        return False
    
    def _shoot_melon(self, transform, grid_pos, plant_type) -> None:
        """
        发射西瓜投射物
        
        Args:
            transform: 植物变换组件
            grid_pos: 网格位置组件
            plant_type: 植物类型（MELON_PULT或WINTER_MELON）
        """
        # 确定投射物类型
        if plant_type == PlantType.WINTER_MELON:
            projectile_type = ProjectileType.WINTER_MELON
        else:
            projectile_type = ProjectileType.MELON
        
        # 创建投射物
        self.entity_factory.create_projectile(
            projectile_type,
            transform.x + 30,
            transform.y,
            grid_pos.row
        )
    
    def _spikeweed_damage(self, entity_id: int, transform, grid_pos,
                          component_manager: ComponentManager) -> None:
        """
        地刺伤害
        
        对站在地刺上的僵尸造成持续伤害
        """
        from ..components import ZombieComponent
        
        # 获取同行僵尸
        zombies = component_manager.query(TransformComponent, ZombieComponent, GridPositionComponent)
        
        for zombie_id in zombies:
            zombie_transform = component_manager.get_component(zombie_id, TransformComponent)
            zombie_grid = component_manager.get_component(zombie_id, GridPositionComponent)
            
            if not zombie_transform or not zombie_grid:
                continue
            
            # 检查是否在同一行且位置重叠
            if zombie_grid.row == grid_pos.row:
                dx = abs(zombie_transform.x - transform.x)
                if dx <= 20:  # 接触范围
                    zombie_health = component_manager.get_component(zombie_id, HealthComponent)
                    if zombie_health:
                        zombie_health.take_damage(20)  # 地刺伤害
    
    def _magnet_shroom_effect(self, entity_id: int, transform, grid_pos,
                              component_manager: ComponentManager) -> None:
        """
        磁力菇效果
        
        吸走范围内僵尸的金属防具
        """
        from ..components import ZombieComponent
        
        # 获取所有僵尸
        zombies = component_manager.query(TransformComponent, ZombieComponent, GridPositionComponent)
        
        for zombie_id in zombies:
            zombie_comp = component_manager.get_component(zombie_id, ZombieComponent)
            zombie_grid = component_manager.get_component(zombie_id, GridPositionComponent)
            
            if not zombie_comp or not zombie_grid:
                continue
            
            # 检查是否有金属防具
            if zombie_comp.has_armor and zombie_comp.armor_health > 0:
                # 移除防具
                zombie_comp.has_armor = False
                zombie_comp.armor_health = 0
