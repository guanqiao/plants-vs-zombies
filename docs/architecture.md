# 植物大战僵尸 - 架构文档

> 版本: 1.0  
> 更新日期: 2026-02-21  
> 状态: 已完成

---

## 目录

1. [架构概览](#架构概览)
2. [ECS架构详解](#ecs架构详解)
3. [核心系统](#核心系统)
4. [数据流](#数据流)
5. [模块说明](#模块说明)
6. [扩展指南](#扩展指南)

---

## 架构概览

本项目采用 **ECS (Entity-Component-System)** 架构，这是一种数据驱动的设计模式，特别适合游戏开发。

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                      GameWindow (Arcade)                    │
│                      游戏主窗口层                            │
├─────────────────────────────────────────────────────────────┤
│                      GameStateManager                        │
│                      游戏状态管理层                          │
├─────────────────────────────────────────────────────────────┤
│                         ECS World                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Entity     │  │  Component   │  │   System     │      │
│  │   Manager    │  │   Manager    │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
├─────────────────────────────────────────────────────────────┤
│  Systems: Render | Movement | Collision | Health | AI ...   │
├─────────────────────────────────────────────────────────────┤
│  Components: Transform | Sprite | Health | Velocity ...     │
├─────────────────────────────────────────────────────────────┤
│  Core: Config | Resource | Event | Save | Audio ...         │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

- **游戏引擎**: Python Arcade
- **架构模式**: ECS (Entity-Component-System)
- **配置文件**: TOML
- **日志系统**: 自定义Logger
- **测试框架**: pytest

---

## ECS架构详解

### 核心概念

#### 1. Entity (实体)
实体是游戏对象的唯一标识符，本身不包含任何数据，只是一个整数ID。

```python
# 创建实体
entity = world.create_entity()  # 返回实体ID，如 0, 1, 2...
```

**特点**:
- 轻量级，只是一个整数ID
- 通过组件组合定义行为
- 运行时动态添加/移除组件

#### 2. Component (组件)
组件是纯数据容器，不包含任何逻辑。

```python
@dataclass
class TransformComponent(Component):
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0
    scale: float = 1.0
```

**已有组件类型** (13种):

| 组件 | 用途 | 关键属性 |
|------|------|----------|
| TransformComponent | 位置变换 | x, y, rotation, scale |
| SpriteComponent | 视觉表现 | color, width, height, texture |
| HealthComponent | 生命值 | current, max_health |
| VelocityComponent | 移动速度 | vx, vy, speed_multiplier |
| GridPositionComponent | 网格位置 | row, col, is_occupied |
| PlantComponent | 植物属性 | cost, attack_cooldown, attack_damage |
| ZombieComponent | 僵尸属性 | damage, attack_cooldown, slow_factor |
| ProjectileComponent | 投射物 | damage, speed, is_splash |
| CollisionComponent | 碰撞检测 | width, height, layer, collides_with |
| AnimationComponent | 动画控制 | current_state, animations |
| SunProducerComponent | 阳光生产 | production_amount, production_interval |
| CooldownComponent | 冷却计时 | duration, remaining, callback |
| AttackComponent | 攻击属性 | damage, range, cooldown |

#### 3. System (系统)
系统包含处理逻辑，操作具有特定组件的实体。

```python
class MovementSystem(System):
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        # 查询所有有Transform和Velocity组件的实体
        entities = component_manager.query(TransformComponent, VelocityComponent)
        
        for entity_id in entities:
            transform = component_manager.get_component(entity_id, TransformComponent)
            velocity = component_manager.get_component(entity_id, VelocityComponent)
            
            # 更新位置
            transform.x += velocity.vx * dt
            transform.y += velocity.vy * dt
```

**核心系统** (8个):

| 系统 | 优先级 | 功能 |
|------|--------|------|
| MovementSystem | 10 | 处理实体移动 |
| CollisionSystem | 20 | 碰撞检测（使用空间哈希优化） |
| CooldownSystem | 30 | 管理各种冷却计时器 |
| PlantBehaviorSystem | 40 | 植物行为协调 |
| ZombieBehaviorSystem | 45 | 僵尸AI和行为 |
| ProjectileSystem | 50 | 投射物飞行和碰撞 |
| HealthSystem | 60 | 生命值管理和死亡检测 |
| SunSystem | 70 | 阳光生成和收集 |
| RenderSystem | 100 | 渲染所有实体 |

**专门植物系统** (5个):

| 系统 | 功能 |
|------|------|
| ShooterPlantSystem | 射手类植物（豌豆射手等） |
| ExplosivePlantSystem | 爆炸类植物（樱桃炸弹、土豆雷） |
| MeleePlantSystem | 近战类植物（大嘴花、地刺） |
| LobberPlantSystem | 投手类植物（西瓜投手） |
| SupportPlantSystem | 辅助类植物（磁力菇） |

### ECS优势

1. **组合优于继承**: 通过组件组合创建复杂对象，避免深层继承链
2. **数据局部性**: 同类型组件连续存储，提高CPU缓存命中率
3. **并行友好**: 系统之间无依赖时可并行执行
4. **易于扩展**: 添加新功能只需添加组件和系统
5. **测试友好**: 组件是纯数据，系统逻辑独立，易于单元测试

---

## 核心系统

### 1. 配置系统

**文件**: `src/core/config_manager.py`, `src/core/plant_config.py`

使用TOML配置文件管理游戏数据：

```toml
[plants.peashooter]
name = "豌豆射手"
cost = 100
health = 100
fire_rate = 1.5
projectile_damage = 20
```

**特点**:
- 类型安全的配置访问
- 热重载支持
- 单例模式管理

### 2. 资源管理系统

**文件**: `src/core/resource_manager.py`, `src/arcade_game/sprite_manager.py`

管理游戏资源（图片、音效、动画）：

```python
# 加载图片（带缓存）
texture = resource_manager.load_image("plant_peashooter", "path/to/image.png")

# 加载动画
animation = sprite_manager.get_animation("plant_peashooter_idle")
```

### 3. 事件总线

**文件**: `src/core/event_bus.py`

实现发布-订阅模式，解耦系统间通信：

```python
# 订阅事件
event_bus.subscribe(EventType.PLANT_PLACED, on_plant_placed)

# 发布事件
event_bus.publish(Event(EventType.PLANT_PLACED, {"plant_id": entity_id}))
```

### 4. 存档系统

**文件**: `src/arcade_game/save_system.py`

支持多槽位存档：

```python
# 保存游戏
save_data = GameSaveData(
    current_level=1,
    sun_count=150,
    plants=[...],
    zombies=[...]
)
save_system.save_game(slot=1, data=save_data)

# 加载游戏
data = save_system.load_game(slot=1)
```

### 5. 空间哈希系统

**文件**: `src/core/spatial_hash.py`

优化碰撞检测性能：

```python
spatial_hash = SpatialHash(cell_size=100.0)
spatial_hash.insert(entity_id, aabb)

# 查询附近实体
nearby = spatial_hash.get_nearby_entities(entity_id, radius=100.0)
```

**性能提升**: 从O(n²)优化到O(n)

---

## 数据流

### 游戏循环数据流

```
┌─────────────────────────────────────────────────────────────┐
│                        游戏循环                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  1. 处理输入 (Input Handling)                                │
│     - 鼠标点击                                               │
│     - 键盘输入                                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  2. 更新系统 (System Update)                                 │
│     - MovementSystem: 更新位置                               │
│     - CollisionSystem: 检测碰撞                              │
│     - PlantBehaviorSystem: 植物攻击                          │
│     - ZombieBehaviorSystem: 僵尸AI                           │
│     - ProjectileSystem: 投射物移动                           │
│     - HealthSystem: 生命检测                                 │
│     - SunSystem: 阳光生成                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  3. 渲染 (Rendering)                                         │
│     - RenderSystem: 渲染所有实体                             │
│     - UIRenderer: 渲染UI元素                                 │
│     - ParticleSystem: 渲染粒子效果                           │
└─────────────────────────────────────────────────────────────┘
```

### 事件流示例：植物攻击僵尸

```
PlantBehaviorSystem
       │
       │ 1. 检测僵尸在范围内
       ▼
ProjectileSystem
       │
       │ 2. 创建投射物实体
       ▼
CollisionSystem
       │
       │ 3. 检测投射物与僵尸碰撞
       ▼
HealthSystem
       │
       │ 4. 对僵尸造成伤害
       ▼
ZombieBehaviorSystem
       │
       │ 5. 检测僵尸死亡
       ▼
EventBus
       │
       │ 6. 发布僵尸死亡事件
       ▼
GameWindow
       │ 7. 更新分数、播放音效
```

---

## 模块说明

### 目录结构

```
src/
├── arcade_game/          # Arcade游戏实现
│   ├── entity_factory.py    # 实体工厂
│   ├── game_window.py       # 游戏主窗口
│   ├── save_system.py       # 存档系统
│   ├── audio_manager.py     # 音频管理
│   ├── ui_renderer.py       # UI渲染器
│   └── ...
├── core/                 # 核心模块
│   ├── config_manager.py    # 配置管理
│   ├── event_bus.py         # 事件总线
│   ├── game_state.py        # 游戏状态
│   ├── spatial_hash.py      # 空间哈希
│   └── ...
├── ecs/                  # ECS框架
│   ├── components/          # 组件定义
│   ├── systems/             # 系统实现
│   ├── entity.py            # 实体管理
│   ├── component.py         # 组件管理
│   ├── system.py            # 系统基类
│   └── world.py             # 世界管理
└── systems/              # 小游戏系统
    └── mini_games/          # 小游戏实现
```

### 关键文件说明

| 文件 | 用途 |
|------|------|
| `src/ecs/world.py` | ECS世界，架构入口 |
| `src/ecs/component.py` | 组件管理器 |
| `src/ecs/system.py` | 系统基类和系统管理器 |
| `src/arcade_game/entity_factory.py` | 创建游戏实体的工厂 |
| `src/arcade_game/game_window.py` | 游戏主循环和渲染 |
| `config/game_config.toml` | 游戏配置 |
| `config/zombies_config.toml` | 僵尸配置 |

---

## 扩展指南

### 如何添加新植物

1. **在配置文件中添加植物数据** (`config/game_config.toml`):

```toml
[plants.new_plant]
name = "新植物"
cost = 150
health = 100
fire_rate = 2.0
projectile_damage = 30
```

2. **在枚举中添加植物类型** (`src/ecs/components/plant.py`):

```python
class PlantType(Enum):
    # ... 已有类型
    NEW_PLANT = auto()
```

3. **在配置管理器中添加映射** (`src/core/plant_config.py`):

```python
type_mapping = {
    # ... 已有映射
    'new_plant': PlantType.NEW_PLANT,
}
```

4. **在实体工厂中添加精灵** (`src/arcade_game/entity_factory.py`):

```python
plant_sprites = {
    # ... 已有映射
    PlantType.NEW_PLANT: ("new_plant.png", (255, 0, 0)),
}
```

5. **创建植物系统**（如果需要特殊逻辑）:

```python
class NewPlantSystem(BasePlantSystem):
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        plants = self._get_plants_of_type([PlantType.NEW_PLANT], component_manager)
        # 实现植物逻辑
```

### 如何添加新僵尸

步骤与添加植物类似：

1. 在 `config/zombies_config.toml` 添加配置
2. 在 `src/ecs/components/zombie.py` 添加枚举
3. 在 `src/arcade_game/entity_factory.py` 添加精灵
4. 在 `src/ecs/systems/zombie_behavior_system.py` 添加特殊行为

### 如何添加新系统

1. **继承System基类**:

```python
class NewSystem(System):
    def __init__(self, priority: int = 50):
        super().__init__(priority)
    
    def update(self, dt: float, component_manager: ComponentManager) -> None:
        # 查询实体
        entities = component_manager.query(ComponentA, ComponentB)
        
        # 处理逻辑
        for entity_id in entities:
            # 获取组件并处理
            pass
```

2. **注册到世界**:

```python
world.add_system(NewSystem())
```

### 如何添加小游戏

1. **继承BaseMiniGame** (`src/systems/mini_games/base_game.py`):

```python
class MyMiniGame(BaseMiniGame):
    def __init__(self):
        super().__init__(MiniGameType.MY_GAME)
    
    def initialize(self, level: int) -> None:
        super().initialize(level)
        # 初始化游戏状态
    
    def update(self, dt: float) -> None:
        # 更新游戏逻辑
        pass
    
    def render(self) -> None:
        # 渲染游戏画面
        pass
```

2. **注册到小游戏管理器**:

```python
mini_game_manager.register_game(MiniGameType.MY_GAME, MyMiniGame)
```

---

## 性能优化建议

### 已实现的优化

1. **空间哈希**: 碰撞检测O(n²) → O(n)
2. **对象池**: 重用实体ID，减少GC
3. **组件缓存**: 缓存查询结果
4. **批量渲染**: 减少绘制调用

### 建议的进一步优化

1. **组件存储优化**: 使用连续数组存储组件
2. **多线程**: 无依赖系统并行更新
3. **LOD系统**: 远距离对象简化渲染
4. **纹理图集**: 减少纹理切换

---

## 调试工具

### 已提供的调试功能

1. **性能监控**: `src/core/performance_monitor.py`
2. **日志系统**: `src/core/logger.py`
3. **统计信息**: 各系统的get_stats()方法

### 使用示例

```python
# 获取碰撞系统统计
collision_stats = collision_system.get_stats()
print(f"碰撞检测对数: {collision_stats['checked_pairs']}")

# 获取空间哈希统计
spatial_stats = spatial_hash.get_stats()
print(f"实体数量: {spatial_stats['total_entities']}")
```

---

## 总结

本项目采用ECS架构，具有清晰的模块划分和良好的扩展性：

- **13种组件** 定义游戏对象属性
- **13个系统** 处理游戏逻辑
- **空间哈希** 优化碰撞检测
- **配置驱动** 易于调整游戏平衡
- **高测试覆盖** 保证代码质量

架构设计考虑了性能、可维护性和扩展性，为后续功能开发提供了坚实基础。

---

*本文档将持续更新，记录架构变更和最佳实践*
