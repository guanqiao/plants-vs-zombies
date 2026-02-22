# 植物大战僵尸 - API参考文档

> 版本: 1.0  
> 更新日期: 2026-02-21  
> 状态: 已完成

---

## 目录

1. [ECS核心API](#ecs核心api)
2. [组件API](#组件api)
3. [系统API](#系统api)
4. [核心模块API](#核心模块api)
5. [游戏系统API](#游戏系统api)

---

## ECS核心API

### World 世界管理器

**文件**: `src/ecs/world.py`

ECS架构的入口点，统一管理实体、组件和系统。

```python
from src.ecs import World

# 创建世界
world = World()
```

#### 实体操作

```python
# 创建实体
entity = world.create_entity()  # 返回 Entity 对象

# 销毁实体
world.destroy_entity(entity)

# 获取实体
entity = world.get_entity(entity_id)
```

#### 组件操作

```python
from src.ecs.components import TransformComponent, HealthComponent

# 添加组件
world.add_component(entity, TransformComponent(x=100, y=200))
world.add_component(entity, HealthComponent(current=100, max_health=100))

# 移除组件
world.remove_component(entity, TransformComponent)

# 获取组件
transform = world.get_component(entity, TransformComponent)

# 检查是否有组件
has_health = world.has_component(entity, HealthComponent)
```

#### 查询操作

```python
# 查询拥有指定组件的所有实体
entities = world.query_entities(TransformComponent, HealthComponent)
# 返回: List[int] - 实体ID列表

# 查询所有指定类型的组件
components = world.query_components(TransformComponent)
# 返回: Dict[int, TransformComponent] - {entity_id: component}
```

#### 系统操作

```python
from src.ecs.systems import MovementSystem

# 添加系统
world.add_system(MovementSystem(priority=10))

# 移除系统
world.remove_system(movement_system)
```

#### 世界更新

```python
# 更新世界（在游戏循环中调用）
dt = 1/60  # 时间增量（秒）
world.update(dt)
```

---

## 组件API

### TransformComponent 变换组件

**文件**: `src/ecs/components/transform.py`

```python
from src.ecs.components import TransformComponent

# 创建
transform = TransformComponent(
    x=100.0,        # X坐标
    y=200.0,        # Y坐标
    rotation=0.0,   # 旋转角度（度）
    scale=1.0       # 缩放比例
)

# 属性访问
print(transform.x, transform.y)
print(transform.rotation)
print(transform.scale)

# 方法
transform.translate(10, -5)  # 相对移动
transform.set_position(100, 200)  # 绝对设置
```

### HealthComponent 生命值组件

**文件**: `src/ecs/components/health.py`

```python
from src.ecs.components import HealthComponent

# 创建
health = HealthComponent(
    current=100,    # 当前生命值
    max_health=100  # 最大生命值
)

# 属性
print(health.current)      # 当前生命值
print(health.max_health)   # 最大生命值
print(health.is_dead)      # 是否死亡
print(health.is_full)      # 是否满血
print(health.percent)      # 生命百分比 (0.0 - 1.0)

# 方法
health.take_damage(20)     # 受到伤害
health.heal(10)            # 恢复生命
health.reset()             # 重置为满血
```

### VelocityComponent 速度组件

**文件**: `src/ecs/components/velocity.py`

```python
from src.ecs.components import VelocityComponent

# 创建
velocity = VelocityComponent(
    vx=0.0,     # X方向速度
    vy=0.0,     # Y方向速度
    speed=100.0 # 基础速度
)

# 方法
velocity.set_velocity(50, 0)        # 设置速度
velocity.apply_multiplier(0.5)      # 应用速度倍率（如减速效果）
velocity.reset_multiplier()          # 重置速度倍率
```

### PlantComponent 植物组件

**文件**: `src/ecs/components/plant.py`

```python
from src.ecs.components import PlantComponent, PlantType

# 创建
plant = PlantComponent(
    cost=100,               # 阳光成本
    attack_cooldown=1.5,    # 攻击冷却时间（秒）
    attack_damage=20,       # 攻击力
    attack_range=800.0,     # 攻击范围（像素）
    is_ready=True,          # 是否准备好攻击
    is_armed=True           # 是否已激活
)

# 方法
plant.update_timer(dt)      # 更新攻击计时器
plant.start_cooldown()      # 开始攻击冷却
plant.can_attack()          # 检查是否可以攻击 -> bool
```

### ZombieComponent 僵尸组件

**文件**: `src/ecs/components/zombie.py`

```python
from src.ecs.components import ZombieComponent, ZombieType

# 创建
zombie = ZombieComponent(
    damage=20,              # 攻击力
    attack_cooldown=1.0,    # 攻击冷却时间（秒）
    score_value=10,         # 击杀得分
    slow_factor=1.0,        # 速度倍率（1.0为正常）
    slow_duration=0.0       # 减速持续时间
)

# 方法
zombie.update_timer(dt)              # 更新计时器
zombie.start_attack()                # 开始攻击
zombie.apply_slow(0.5, 5.0)          # 应用减速（倍率，持续时间）
zombie.take_armor_damage(50)         # 对护甲造成伤害
```

### CollisionComponent 碰撞组件

**文件**: `src/ecs/components/collision.py`

```python
from src.ecs.components import CollisionComponent
from src.ecs.systems import CollisionSystem

# 创建
collision = CollisionComponent(
    width=60.0,     # 碰撞盒宽度
    height=80.0,    # 碰撞盒高度
    layer=CollisionSystem.LAYER_PLANT,  # 碰撞层
    collides_with={CollisionSystem.LAYER_ZOMBIE}  # 可碰撞的层
)

# 方法
collision.set_size(60, 80)           # 设置碰撞盒大小
collision.can_collide_with(layer)    # 检查是否可以与某层碰撞 -> bool
collision.intersects(other, x1, y1, x2, y2)  # 检查两个碰撞盒是否相交 -> bool
```

---

## 系统API

### System 系统基类

**文件**: `src/ecs/system.py`

```python
from src.ecs.system import System
from src.ecs.component import ComponentManager

class MySystem(System):
    def __init__(self, priority: int = 50):
        super().__init__(priority)
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        # 实现系统逻辑
        pass
```

### MovementSystem 移动系统

**文件**: `src/ecs/systems/movement_system.py`

```python
from src.ecs.systems import MovementSystem

# 创建
movement_system = MovementSystem(priority=10)

# 添加到世界
world.add_system(movement_system)
```

### CollisionSystem 碰撞系统

**文件**: `src/ecs/systems/collision_system.py`

```python
from src.ecs.systems import CollisionSystem

# 创建
collision_system = CollisionSystem(priority=20)

# 注册碰撞回调
def on_collision(entity1: int, entity2: int) -> None:
    print(f"碰撞: {entity1} 和 {entity2}")

collision_system.register_collision_callback(on_collision)

# 获取统计信息
stats = collision_system.get_stats()
# 返回: {'spatial_hash': {...}, 'checked_pairs': int, 'callbacks': int}
```

**碰撞层常量**:

```python
CollisionSystem.LAYER_PLANT      # 植物层
CollisionSystem.LAYER_ZOMBIE     # 僵尸层
CollisionSystem.LAYER_PROJECTILE # 投射物层
CollisionSystem.LAYER_SUN        # 阳光层
```

### HealthSystem 生命值系统

**文件**: `src/ecs/systems/health_system.py`

```python
from src.ecs.systems import HealthSystem

# 创建
health_system = HealthSystem(priority=60)

# 注册死亡回调
def on_death(entity_id: int) -> None:
    print(f"实体 {entity_id} 死亡")

health_system.register_death_callback(on_death)
```

### PlantBehaviorSystem 植物行为系统

**文件**: `src/ecs/systems/plant_behavior_system.py`

```python
from src.ecs.systems import PlantBehaviorSystem
from src.arcade_game.entity_factory import EntityFactory

# 创建
entity_factory = EntityFactory(world)
plant_system = PlantBehaviorSystem(entity_factory, priority=40)
```

### ZombieBehaviorSystem 僵尸行为系统

**文件**: `src/ecs/systems/zombie_behavior_system.py`

```python
from src.ecs.systems import ZombieBehaviorSystem

# 创建
zombie_system = ZombieBehaviorSystem(entity_factory, priority=45)

# 注册死亡回调
def on_zombie_death(zombie_id: int, score: int) -> None:
    print(f"僵尸 {zombie_id} 死亡，得分: {score}")

zombie_system.register_death_callback(on_zombie_death)
```

---

## 核心模块API

### ConfigManager 配置管理器

**文件**: `src/core/config_manager.py`

```python
from src.core.config_manager import ConfigManager

# 获取单例实例
config = ConfigManager()

# 获取植物配置
plant_config = config.get_plant_config("peashooter")
# 返回: Dict[str, Any]

# 获取僵尸配置
zombie_config = config.get_zombie_config("normal")

# 获取游戏配置
game_config = config.get_game_config()

# 获取关卡配置
level_config = config.get_level_config(1)

# 重新加载配置
config.reload()
```

### PlantConfigManager 植物配置管理器

**文件**: `src/core/plant_config.py`

```python
from src.core.plant_config import PlantConfigManager, get_plant_config
from src.ecs.components import PlantType

# 获取单例实例
manager = PlantConfigManager()

# 获取配置
config = manager.get_config(PlantType.PEASHOOTER)
# 返回: PlantConfig 对象

# 便捷函数
config = get_plant_config(PlantType.PEASHOOTER)

# 属性访问
print(config.name)           # 植物名称
print(config.cost)           # 阳光成本
print(config.health)         # 生命值
print(config.fire_rate)      # 射击间隔
print(config.is_shooter)     # 是否是射手
print(config.is_explosive)   # 是否是爆炸类
print(config.is_sun_producer) # 是否产生阳光
```

### EventBus 事件总线

**文件**: `src/core/event_bus.py`

```python
from src.core.event_bus import EventBus, Event, EventType

# 获取单例实例
event_bus = EventBus()

# 定义事件处理器
def on_plant_placed(event: Event) -> None:
    plant_id = event.data.get("plant_id")
    print(f"植物放置: {plant_id}")

# 订阅事件
event_bus.subscribe(EventType.PLANT_PLACED, on_plant_placed)

# 发布事件
event = Event(
    event_type=EventType.PLANT_PLACED,
    data={"plant_id": 123, "position": (100, 200)}
)
event_bus.publish(event)

# 取消订阅
event_bus.unsubscribe(EventType.PLANT_PLACED, on_plant_placed)

# 清除所有监听器
event_bus.clear()
```

**事件类型**:

```python
EventType.PLANT_PLACED      # 植物放置
EventType.ZOMBIE_SPAWNED    # 僵尸生成
EventType.ZOMBIE_DIED       # 僵尸死亡
EventType.SUN_COLLECTED     # 阳光收集
EventType.GAME_OVER         # 游戏结束
EventType.LEVEL_COMPLETE    # 关卡完成
```

### SaveSystem 存档系统

**文件**: `src/arcade_game/save_system.py`

```python
from src.arcade_game.save_system import SaveSystem, GameSaveData, get_save_system

# 获取单例实例
save_system = get_save_system(save_dir="saves")

# 创建存档数据
save_data = GameSaveData(
    version="1.0",
    save_name="关卡1-1",
    current_level=1,
    sun_count=150,
    score=1000,
    play_time=3600.0
)

# 保存游戏
success = save_system.save_game(slot=1, data=save_data)

# 加载游戏
loaded_data = save_system.load_game(slot=1)
# 返回: GameSaveData 或 None

# 删除存档
success = save_system.delete_save(slot=1)

# 获取存档信息
info = save_system.get_save_info(slot=1)
# 返回: Dict[str, Any] 或 None

# 获取所有存档
saves = save_system.get_all_saves()
# 返回: List[Dict[str, Any]]

# 检查存档是否存在
exists = save_system.has_save(slot=1)

# 导出存档
success = save_system.export_save(slot=1, export_path="backup/save1.json")

# 导入存档
success = save_system.import_save(import_path="backup/save1.json", slot=2)
```

### SpatialHash 空间哈希

**文件**: `src/core/spatial_hash.py`

```python
from src.core.spatial_hash import SpatialHash, AABB

# 创建空间哈希
spatial_hash = SpatialHash(cell_size=100.0)

# 创建AABB（轴对齐包围盒）
aabb = AABB(x=100, y=200, width=60, height=80)

# 插入实体
spatial_hash.insert(entity_id=1, aabb=aabb)

# 更新实体位置
spatial_hash.update(entity_id=1, aabb=new_aabb)

# 移除实体
spatial_hash.remove(entity_id=1)

# 点查询
entities = spatial_hash.query_point(x=150, y=250)
# 返回: List[int]

# AABB查询
entities = spatial_hash.query_aabb(query_aabb)
# 返回: List[int]

# 半径查询
entities = spatial_hash.query_radius(x=150, y=250, radius=100.0)
# 返回: List[int]

# 获取附近实体
entities = spatial_hash.get_nearby_entities(entity_id=1, radius=100.0)
# 返回: List[int]（不包含自身）

# 清空
spatial_hash.clear()

# 获取统计
stats = spatial_hash.get_stats()
# 返回: {'cell_size': float, 'total_cells': int, 'total_entities': int, 'avg_entities_per_cell': float}
```

### ObjectPool 对象池

**文件**: `src/core/spatial_hash.py`

```python
from src.core.spatial_hash import ObjectPool

# 创建对象池
def create_projectile():
    return Projectile()

def reset_projectile(proj):
    proj.reset()

pool = ObjectPool(
    factory_func=create_projectile,
    reset_func=reset_projectile,
    initial_size=10
)

# 获取对象
proj = pool.acquire()

# 释放对象
pool.release(proj)

# 释放所有
pool.release_all()

# 获取统计
stats = pool.get_stats()
# 返回: {'available': int, 'in_use': int, 'total': int}
```

---

## 游戏系统API

### EntityFactory 实体工厂

**文件**: `src/arcade_game/entity_factory.py`

```python
from src.arcade_game.entity_factory import EntityFactory
from src.ecs import World
from src.ecs.components import PlantType, ZombieType, ProjectileType

# 创建工厂
world = World()
factory = EntityFactory(world)

# 创建植物
plant = factory.create_plant(
    plant_type=PlantType.PEASHOOTER,
    x=200.0,
    y=300.0,
    row=2,
    col=3
)

# 创建僵尸
zombie = factory.create_zombie(
    zombie_type=ZombieType.NORMAL,
    x=900.0,
    y=300.0,
    row=2,
    speed_multiplier=1.0,
    health_multiplier=1.0
)

# 创建投射物
projectile = factory.create_projectile(
    proj_type=ProjectileType.PEA,
    x=250.0,
    y=300.0,
    row=2
)

# 创建阳光
sun = factory.create_sun(
    x=300.0,
    y=100.0,
    amount=25,
    is_falling=True
)
```

### GameStateManager 游戏状态管理器

**文件**: `src/core/game_state.py`

```python
from src.core.game_state import GameStateManager, ExtendedGameState

# 创建管理器
state_manager = GameStateManager()

# 开始游戏
state_manager.start_game(level=1, difficulty="normal")

# 暂停游戏
state_manager.pause_game()

# 继续游戏
state_manager.resume_game()

# 重新开始
state_manager.restart_game()

# 游戏结束
state_manager.game_over(score=1000)

# 游戏胜利
state_manager.victory(score=2000)

# 状态检查
is_playing = state_manager.is_playing()
is_paused = state_manager.is_paused()
is_game_over = state_manager.is_game_over()
is_victory = state_manager.is_victory()
is_in_menu = state_manager.is_in_menu()

# 导航
state_manager.go_to_main_menu()
state_manager.go_to_level_select()
state_manager.go_to_settings()

# 下一关
state_manager.next_level()

# 获取状态名称
name = state_manager.get_state_name()  # 返回: "游戏中" 等

# 设置回调
def on_state_change(old_state, new_state):
    print(f"状态变更: {old_state} -> {new_state}")

state_manager.on_state_change = on_state_change
```

### AudioManager 音频管理器

**文件**: `src/arcade_game/audio_manager.py`

```python
from src.arcade_game.audio_manager import AudioManager, SoundType

# 获取单例实例
audio = AudioManager()

# 播放音效
audio.play_sound(SoundType.PLANT_PLACE)
audio.play_sound(SoundType.SHOOT)
audio.play_sound(SoundType.ZOMBIE_DIE)

# 播放背景音乐
audio.play_music("background")

# 停止音乐
audio.stop_music()

# 音量控制
audio.set_master_volume(0.8)      # 主音量 (0.0 - 1.0)
audio.set_music_volume(0.5)       # 音乐音量
audio.set_sfx_volume(0.7)         # 音效音量

# 静音
audio.mute()
audio.unmute()
audio.toggle_mute()
is_muted = audio.is_muted()
```

**音效类型**:

```python
SoundType.PLANT_PLACE     # 种植
SoundType.SHOOT           # 射击
SoundType.HIT             # 击中
SoundType.ZOMBIE_DIE      # 僵尸死亡
SoundType.SUN_COLLECT     # 收集阳光
SoundType.EXPLOSION       # 爆炸
SoundType.GAME_OVER       # 游戏结束
SoundType.VICTORY         # 胜利
SoundType.BUTTON_CLICK    # 按钮点击
SoundType.PAUSE           # 暂停
SoundType.RESUME          # 继续
```

---

## 常量参考

### 游戏常量

**文件**: `src/core/game_constants.py`

```python
# 屏幕尺寸
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60

# 网格设置
GRID_ROWS = 5
GRID_COLS = 9
CELL_WIDTH = 80
CELL_HEIGHT = 100
GRID_START_X = 80
GRID_START_Y = 80

# 游戏数值
INITIAL_SUN = 50
MAX_SUN = 9990
SUN_DROP_INTERVAL = 10.0
```

### 植物类型

**文件**: `src/ecs/components/plant.py`

```python
class PlantType(Enum):
    SUNFLOWER = auto()      # 向日葵
    PEASHOOTER = auto()     # 豌豆射手
    WALLNUT = auto()        # 坚果墙
    SNOW_PEA = auto()       # 寒冰射手
    CHERRY_BOMB = auto()    # 樱桃炸弹
    POTATO_MINE = auto()    # 土豆雷
    REPEATER = auto()       # 双发射手
    CHOMPER = auto()        # 大嘴花
    THREEPEATER = auto()    # 三线射手
    MELON_PULT = auto()     # 西瓜投手
    WINTER_MELON = auto()   # 冰西瓜
    TALL_NUT = auto()       # 高坚果
    SPIKEWEED = auto()      # 地刺
    MAGNET_SHROOM = auto()  # 磁力菇
    PUMPKIN = auto()        # 南瓜头
```

### 僵尸类型

**文件**: `src/ecs/components/zombie.py`

```python
class ZombieType(Enum):
    NORMAL = auto()         # 普通僵尸
    CONEHEAD = auto()       # 路障僵尸
    BUCKETHEAD = auto()     # 铁桶僵尸
    RUNNER = auto()         # 跑步僵尸
    GARGANTUAR = auto()     # 巨人僵尸
    POLE_VAULTER = auto()   # 撑杆跳僵尸
    SCREEN_DOOR = auto()    # 铁栅门僵尸
    FOOTBALL = auto()       # 橄榄球僵尸
    DANCER = auto()         # 舞王僵尸
    BACKUP_DANCER = auto()  # 伴舞僵尸
    BALLOON = auto()        # 气球僵尸
    MINER = auto()          # 矿工僵尸
    POGO = auto()           # 跳跳僵尸
    BUNGEE = auto()         # 蹦极僵尸
```

### 投射物类型

**文件**: `src/ecs/components/projectile.py`

```python
class ProjectileType(Enum):
    PEA = auto()            # 豌豆
    FROZEN_PEA = auto()     # 冰豌豆
    MELON = auto()          # 西瓜
    WINTER_MELON = auto()   # 冰西瓜
    CABBAGE = auto()        # 卷心菜
    KERNEL = auto()         # 玉米粒
    BUTTER = auto()         # 黄油
```

---

## 错误处理

所有API都遵循以下错误处理模式：

1. **返回None**: 查询类操作在找不到时返回None
2. **返回False**: 操作失败时返回False
3. **抛出异常**: 严重错误时抛出异常
4. **日志记录**: 使用logger记录警告和错误

示例：

```python
# 返回None的示例
data = save_system.load_game(slot=99)  # 不存在的槽位
if data is None:
    print("存档不存在")

# 返回False的示例
success = save_system.save_game(slot=1, data=save_data)
if not success:
    print("保存失败")

# 异常处理
try:
    entity = world.get_entity(99999)  # 不存在的实体
except KeyError:
    print("实体不存在")
```

---

*本文档将持续更新，记录API变更*
