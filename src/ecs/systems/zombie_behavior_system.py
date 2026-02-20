"""
僵尸行为系统 - 处理僵尸的移动和攻击
"""

from ..system import System
from ..component import ComponentManager
from ..components import (
    TransformComponent, VelocityComponent, ZombieComponent,
    GridPositionComponent, HealthComponent, PlantComponent
)


class ZombieBehaviorSystem(System):
    """
    僵尸行为系统
    
    处理僵尸的移动、攻击和特殊行为
    - 正常移动
    - 攻击植物
    - 特殊僵尸能力（跳跃、飞行等）
    """
    
    # 攻击距离阈值
    ATTACK_RANGE = 40.0
    
    def __init__(self, entity_factory=None, priority: int = 45):
        super().__init__(priority)
        self.entity_factory = entity_factory
        self.on_zombie_death_callbacks = []
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        """更新僵尸行为"""
        # 获取所有僵尸实体
        entities = component_manager.query(
            TransformComponent, VelocityComponent, ZombieComponent
        )
        
        zombies_to_remove = []
        
        for entity_id in entities:
            transform = component_manager.get_component(entity_id, TransformComponent)
            velocity = component_manager.get_component(entity_id, VelocityComponent)
            zombie = component_manager.get_component(entity_id, ZombieComponent)
            
            if not all([transform, velocity, zombie]):
                continue
            
            # 检查僵尸是否死亡
            health = component_manager.get_component(entity_id, HealthComponent)
            if health and health.is_dead:
                zombies_to_remove.append(entity_id)
                continue
            
            # 更新计时器
            zombie.update_timer(dt)
            
            # 检查是否可以攻击植物
            target_plant = self._find_target_plant(entity_id, transform, component_manager)
            
            if target_plant:
                # 停止移动并攻击
                velocity.vx = 0
                self._attack_plant(target_plant, zombie, component_manager, dt)
            else:
                # 继续移动
                velocity.vx = -1.0  # 向左移动
                velocity.apply_multiplier(zombie.slow_factor)
            
            # 处理特殊行为
            self._handle_special_behavior(entity_id, transform, zombie, component_manager, dt)
        
        # 处理死亡的僵尸
        for zombie_id in zombies_to_remove:
            self._handle_zombie_death(zombie_id, component_manager)
    
    def _find_target_plant(self, zombie_id: int, zombie_transform, 
                           component_manager: ComponentManager) -> int:
        """
        寻找攻击目标（同行最左侧的植物）
        
        Returns:
            目标植物实体ID，如果没有则返回None
        """
        zombie_grid = component_manager.get_component(zombie_id, GridPositionComponent)
        if not zombie_grid:
            return None
        
        # 获取同行的所有植物
        plants = component_manager.query(TransformComponent, PlantComponent, GridPositionComponent)
        
        closest_plant = None
        closest_distance = float('inf')
        
        for plant_id in plants:
            plant_grid = component_manager.get_component(plant_id, GridPositionComponent)
            if not plant_grid or plant_grid.row != zombie_grid.row:
                continue
            
            plant_transform = component_manager.get_component(plant_id, TransformComponent)
            if not plant_transform:
                continue
            
            # 计算距离（只考虑X轴）
            distance = zombie_transform.x - plant_transform.x
            
            # 植物必须在僵尸左侧且在攻击范围内
            if 0 < distance < self.ATTACK_RANGE:
                if distance < closest_distance:
                    closest_distance = distance
                    closest_plant = plant_id
        
        return closest_plant
    
    def _attack_plant(self, plant_id: int, zombie, 
                      component_manager: ComponentManager, dt: float) -> None:
        """攻击植物"""
        # 检查攻击冷却
        if zombie.attack_timer > 0:
            return
        
        # 获取植物生命值
        plant_health = component_manager.get_component(plant_id, HealthComponent)
        if not plant_health:
            return
        
        # 造成伤害
        plant_health.take_damage(zombie.damage)
        
        # 开始攻击冷却
        zombie.start_attack()
    
    def _handle_special_behavior(self, entity_id: int, transform, zombie, 
                                  component_manager: ComponentManager, dt: float) -> None:
        """处理特殊僵尸行为"""
        from ..components import ZombieType, ZombieTypeComponent
        
        zombie_type_comp = component_manager.get_component(entity_id, ZombieTypeComponent)
        if not zombie_type_comp:
            return
        
        zombie_type = zombie_type_comp.zombie_type
        
        # 撑杆僵尸跳跃
        if zombie.has_pole and not zombie.has_jumped:
            self._check_pole_vault(entity_id, transform, zombie, component_manager)
        
        # 舞王僵尸召唤伴舞
        if zombie_type == ZombieType.DANCER and not zombie.dancer_spawned:
            if transform.x < 800:
                self._spawn_backup_dancers(entity_id, transform, zombie, component_manager)
        
        # 矿工僵尸挖掘
        if zombie_type == ZombieType.MINER:
            if not zombie.has_dug and transform.x < 200:
                transform.x = 100
                zombie.has_dug = True
        
        # 气球僵尸飞行
        if zombie_type == ZombieType.BALLOON:
            if not zombie.is_flying:
                # 初始化为飞行状态
                zombie.is_flying = True
                # 设置飞行高度
                transform.y -= 50  # 向上偏移
            
            # 检查是否被仙人掌或香蒲击破气球
            if self._check_balloon_popped(entity_id, transform, zombie, component_manager):
                zombie.is_flying = False
                transform.y += 50  # 落回地面
        
        # 蹦极僵尸偷植物
        if zombie_type == ZombieType.BUNGEE:
            zombie.bungee_timer += dt
            if zombie.bungee_timer >= 3.0 and zombie.bungee_target is None:
                self._steal_plant(entity_id, transform, zombie, component_manager)
        
        # 巨人僵尸砸植物（造成大量伤害）
        if zombie_type == ZombieType.GARGANTUAR:
            self._gargantuar_smash(entity_id, transform, zombie, component_manager, dt)
        
        # 巨人僵尸投掷小鬼
        if zombie_type == ZombieType.GARGANTUAR and not zombie.imp_thrown:
            health = component_manager.get_component(entity_id, HealthComponent)
            if health and health.current < health.max_health * 0.5:
                self._throw_imp(entity_id, transform, zombie, component_manager)
    
    def _check_balloon_popped(self, entity_id: int, transform, zombie,
                               component_manager: ComponentManager) -> bool:
        """
        检查气球僵尸的气球是否被击破
        
        只有仙人掌或香蒲可以击破气球
        
        Returns:
            气球是否被击破
        """
        from ..components import PlantType, PlantTypeComponent
        
        # 获取僵尸所在行
        zombie_grid = component_manager.get_component(entity_id, GridPositionComponent)
        if not zombie_grid:
            return False
        
        # 检查同行是否有仙人掌或香蒲
        plants = component_manager.query(TransformComponent, PlantComponent, GridPositionComponent)
        
        for plant_id in plants:
            plant_grid = component_manager.get_component(plant_id, GridPositionComponent)
            if not plant_grid or plant_grid.row != zombie_grid.row:
                continue
            
            plant_transform = component_manager.get_component(plant_id, TransformComponent)
            if not plant_transform:
                continue
            
            # 检查距离
            distance = abs(transform.x - plant_transform.x)
            if distance > 100:  # 攻击范围
                continue
            
            # 检查植物类型
            plant_type_comp = component_manager.get_component(plant_id, PlantTypeComponent)
            if plant_type_comp:
                # 只有仙人掌和香蒲可以攻击飞行僵尸
                if plant_type_comp.plant_type in [PlantType.CACTUS, PlantType.CATTAIL]:
                    # 检查植物是否可以攻击
                    plant = component_manager.get_component(plant_id, PlantComponent)
                    if plant and plant.can_attack:
                        return True
        
        return False
    
    def _check_pole_vault(self, entity_id: int, transform, zombie, 
                          component_manager: ComponentManager) -> None:
        """检查撑杆僵尸是否应该跳跃"""
        # 检查前方是否有植物
        zombie_grid = component_manager.get_component(entity_id, GridPositionComponent)
        if not zombie_grid:
            return
        
        # 检查前方是否有植物
        plants = component_manager.query(TransformComponent, PlantComponent, GridPositionComponent)
        
        for plant_id in plants:
            plant_grid = component_manager.get_component(plant_id, GridPositionComponent)
            if not plant_grid or plant_grid.row != zombie_grid.row:
                continue
            
            plant_transform = component_manager.get_component(plant_id, TransformComponent)
            if not plant_transform:
                continue
            
            # 检查植物是否在跳跃范围内
            distance = plant_transform.x - transform.x
            if 0 < distance < 120:  # 跳跃范围
                # 检查是否是高坚果（不能跳过）
                from ..components import PlantType, PlantTypeComponent
                plant_type_comp = component_manager.get_component(plant_id, PlantTypeComponent)
                if plant_type_comp and plant_type_comp.plant_type == PlantType.TALL_NUT:
                    # 不能跳过高坚果，正常攻击
                    break
                
                # 跳跃过植物
                transform.x = plant_transform.x + 50
                zombie.has_jumped = True
                zombie.has_pole = False  # 失去撑杆
                zombie.speed = -30
                break
    
    def _spawn_backup_dancers(self, entity_id: int, transform, zombie,
                               component_manager: ComponentManager) -> None:
        """舞王僵尸召唤伴舞"""
        # 标记已召唤
        zombie.dancer_spawned = True
        
        # 召唤4个伴舞（上下左右）
        from ..components import ZombieType
        zombie_grid = component_manager.get_component(entity_id, GridPositionComponent)
        if not zombie_grid:
            return
        
        # 使用entity_factory创建伴舞
        if hasattr(self, 'entity_factory') and self.entity_factory:
            # 上方
            self.entity_factory.create_zombie(
                ZombieType.BACKUP_DANCER,
                transform.x,
                transform.y - 100,
                max(0, zombie_grid.row - 1)
            )
            # 下方
            self.entity_factory.create_zombie(
                ZombieType.BACKUP_DANCER,
                transform.x,
                transform.y + 100,
                min(4, zombie_grid.row + 1)
            )
            # 左侧
            self.entity_factory.create_zombie(
                ZombieType.BACKUP_DANCER,
                transform.x - 50,
                transform.y,
                zombie_grid.row
            )
            # 右侧
            self.entity_factory.create_zombie(
                ZombieType.BACKUP_DANCER,
                transform.x + 50,
                transform.y,
                zombie_grid.row
            )
    
    def _steal_plant(self, entity_id: int, transform, zombie,
                     component_manager: ComponentManager) -> None:
        """
        蹦极僵尸偷植物
        
        蹦极僵尸会从天而降，偷走一个植物，然后离开
        """
        from ..components import ZombieType, ZombieTypeComponent
        
        # 获取僵尸所在行
        zombie_grid = component_manager.get_component(entity_id, GridPositionComponent)
        if not zombie_grid:
            return
        
        # 寻找同行最右侧的植物（最靠近房子）
        plants = component_manager.query(TransformComponent, PlantComponent, GridPositionComponent)
        
        target_plant = None
        max_x = float('-inf')
        
        for plant_id in plants:
            plant_grid = component_manager.get_component(plant_id, GridPositionComponent)
            if not plant_grid or plant_grid.row != zombie_grid.row:
                continue
            
            plant_transform = component_manager.get_component(plant_id, TransformComponent)
            if not plant_transform:
                continue
            
            # 寻找最右侧的植物（X坐标最大）
            if plant_transform.x > max_x:
                max_x = plant_transform.x
                target_plant = plant_id
        
        if target_plant:
            # 记录目标
            zombie.bungee_target = target_plant
            
            # 移动到植物位置
            plant_transform = component_manager.get_component(target_plant, TransformComponent)
            if plant_transform:
                transform.x = plant_transform.x
                transform.y = plant_transform.y - 50  # 在植物上方
            
            # 偷取植物（直接销毁）
            self._destroy_plant(target_plant, component_manager)
            
            # 标记已偷取，开始离开
            zombie.bungee_has_stolen = True
            
            # 播放音效（如果有）
            # self._play_bungee_sound()
    
    def _destroy_plant(self, plant_id: int, component_manager: ComponentManager) -> None:
        """
        销毁植物
        
        Args:
            plant_id: 植物实体ID
            component_manager: 组件管理器
        """
        # 获取植物组件
        plant = component_manager.get_component(plant_id, PlantComponent)
        if plant:
            # 标记植物为死亡（实际销毁由HealthSystem处理）
            health = component_manager.get_component(plant_id, HealthComponent)
            if health:
                health.take_damage(health.max_health)  # 造成致命伤害
    
    def _gargantuar_smash(self, entity_id: int, transform, zombie,
                          component_manager: ComponentManager, dt: float) -> None:
        """巨人僵尸砸植物（造成大量伤害）"""
        # 检查攻击冷却
        if zombie.attack_timer > 0:
            return
        
        # 寻找目标植物
        target_plant = self._find_target_plant(entity_id, transform, component_manager)
        if not target_plant:
            return
        
        # 获取植物生命值
        plant_health = component_manager.get_component(target_plant, HealthComponent)
        if not plant_health:
            return
        
        # 造成大量伤害（秒杀大部分植物）
        plant_health.take_damage(1000)
        
        # 开始攻击冷却
        zombie.start_attack()
    
    def _throw_imp(self, entity_id: int, transform, zombie,
                   component_manager: ComponentManager) -> None:
        """巨人僵尸投掷小鬼"""
        zombie.imp_thrown = True
        
        # 使用entity_factory创建小鬼僵尸
        if hasattr(self, 'entity_factory') and self.entity_factory:
            from ..components import ZombieType
            zombie_grid = component_manager.get_component(entity_id, GridPositionComponent)
            if zombie_grid:
                # 在巨人前方创建小鬼僵尸
                self.entity_factory.create_zombie(
                    ZombieType.RUNNER,  # 使用RUNNER作为小鬼僵尸
                    transform.x + 100,
                    transform.y,
                    zombie_grid.row
                )
    
    def _handle_zombie_death(self, zombie_id: int, component_manager: ComponentManager) -> None:
        """处理僵尸死亡"""
        zombie = component_manager.get_component(zombie_id, ZombieComponent)
        if zombie:
            # 触发死亡回调
            for callback in self.on_zombie_death_callbacks:
                callback(zombie_id, zombie.score_value)
    
    def register_death_callback(self, callback) -> None:
        """注册僵尸死亡回调"""
        self.on_zombie_death_callbacks.append(callback)
    
    def unregister_death_callback(self, callback) -> None:
        """注销僵尸死亡回调"""
        if callback in self.on_zombie_death_callbacks:
            self.on_zombie_death_callbacks.remove(callback)