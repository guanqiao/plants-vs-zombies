# 植物大战僵尸 - 开发指南

> 版本: 1.0  
> 更新日期: 2026-02-21  
> 状态: 已完成

---

## 目录

1. [开发环境设置](#开发环境设置)
2. [项目结构](#项目结构)
3. [开发流程](#开发流程)
4. [调试技巧](#调试技巧)
5. [性能优化](#性能优化)
6. [常见问题](#常见问题)

---

## 开发环境设置

### 系统要求

- **Python**: 3.10+
- **操作系统**: Windows 10/11, macOS, Linux
- **内存**: 4GB+
- **显卡**: 支持OpenGL 3.3+

### 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd 植物大战僵尸

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 依赖列表

主要依赖包：

```
arcade>=2.6.0      # 游戏引擎
pytest>=7.0.0      # 测试框架
tomli>=2.0.0       # TOML解析（Python < 3.11）
```

---

## 项目结构

```
植物大战僵尸/
├── assets/                 # 游戏资源
│   ├── images/            # 图片资源
│   │   ├── plants/       # 植物图片
│   │   ├── zombies/      # 僵尸图片
│   │   ├── projectiles/  # 投射物图片
│   │   ├── effects/      # 特效图片
│   │   ├── ui/           # UI图片
│   │   └── backgrounds/  # 背景图片
│   ├── sounds/           # 音效资源
│   ├── sprites/          # 精灵图
│   └── animations/       # 动画配置
├── config/               # 配置文件
│   ├── game_config.toml  # 游戏配置
│   ├── zombies_config.toml # 僵尸配置
│   └── levels_config.toml # 关卡配置
├── docs/                 # 文档
│   ├── architecture.md   # 架构文档
│   ├── api_reference.md  # API参考
│   ├── development_guide.md # 开发指南（本文档）
│   ├── gap_analysis.md   # 差距分析
│   └── improvement_plan.md # 改进计划
├── src/                  # 源代码
│   ├── arcade_game/      # Arcade游戏实现
│   │   ├── entity_factory.py
│   │   ├── game_window.py
│   │   ├── save_system.py
│   │   ├── audio_manager.py
│   │   └── ...
│   ├── core/             # 核心模块
│   │   ├── config_manager.py
│   │   ├── event_bus.py
│   │   ├── game_state.py
│   │   ├── spatial_hash.py
│   │   └── ...
│   ├── ecs/              # ECS框架
│   │   ├── components/   # 组件定义
│   │   ├── systems/      # 系统实现
│   │   ├── entity.py
│   │   ├── component.py
│   │   ├── system.py
│   │   └── world.py
│   └── systems/          # 小游戏系统
│       └── mini_games/
├── tests/                # 测试代码
│   ├── test_core/        # 核心模块测试
│   ├── test_ecs/         # ECS测试
│   ├── test_arcade_game/ # 游戏测试
│   └── test_systems/     # 系统测试
├── tools/                # 工具脚本
├── main_arcade.py        # 游戏入口
├── requirements.txt      # 依赖列表
└── README.md            # 项目说明
```

---

## 开发流程

### 1. 功能开发流程

```
需求分析 → 设计 → 编码 → 测试 → 文档 → 提交
```

#### 步骤详解

1. **需求分析**
   - 理解功能需求
   - 查看相关文档（gap_analysis.md, improvement_plan.md）
   - 确定实现方案

2. **设计**
   - 确定是否需要新组件/系统
   - 设计数据结构和API
   - 考虑性能影响

3. **编码**
   - 遵循代码规范
   - 编写清晰的注释
   - 保持模块独立

4. **测试**
   - 编写单元测试
   - 运行测试确保通过
   - 测试边界情况

5. **文档**
   - 更新相关文档
   - 添加代码注释
   - 记录API变更

6. **提交**
   - 代码审查
   - 提交到Git
   - 更新改进计划

### 2. 代码规范

#### 命名规范

```python
# 类名: 大驼峰
class PlantBehaviorSystem:
    pass

# 函数名: 小写下划线
def update_plant_state():
    pass

# 常量: 大写下划线
MAX_HEALTH = 100
ATTACK_COOLDOWN = 1.5

# 私有属性: 下划线前缀
self._private_var = 0

# 保护属性: 单下划线前缀
self._protected_var = 0
```

#### 文档字符串规范

```python
def create_plant(self, plant_type: PlantType, x: float, y: float) -> Entity:
    """
    创建植物实体
    
    根据植物类型在指定位置创建植物实体，
    并添加所有必要的组件。
    
    Args:
        plant_type: 植物类型枚举
        x: X坐标（像素）
        y: Y坐标（像素）
        
    Returns:
        创建的植物实体
        
    Raises:
        ValueError: 如果植物类型无效
        
    Example:
        >>> plant = factory.create_plant(PlantType.PEASHOOTER, 100, 200)
        >>> print(plant.id)
        0
    """
    pass
```

#### 类型注解

```python
from typing import List, Dict, Optional, Tuple

def find_target(
    row: int,
    x: float,
    component_manager: ComponentManager
) -> Optional[int]:
    """
    查找目标僵尸
    
    Args:
        row: 所在行
        x: X坐标
        component_manager: 组件管理器
        
    Returns:
        目标僵尸实体ID，如果没有找到则返回None
    """
    pass
```

### 3. 测试规范

#### 测试文件命名

```
test_<模块名>.py

例如:
- test_game_state.py
- test_plant_config.py
- test_collision_system.py
```

#### 测试类命名

```python
class TestGameState:
    """测试游戏状态"""
    pass

class TestPlantConfigManager:
    """测试植物配置管理器"""
    pass
```

#### 测试方法命名

```python
def test_initial_state(self):
    """测试初始状态"""
    pass

def test_state_transition(self):
    """测试状态转换"""
    pass

def test_invalid_input_raises_error(self):
    """测试无效输入抛出异常"""
    pass
```

#### 测试示例

```python
import pytest
from src.ecs.components import HealthComponent

class TestHealthComponent:
    """生命值组件测试"""
    
    def test_initial_health(self):
        """测试初始生命值"""
        health = HealthComponent(current=100, max_health=100)
        assert health.current == 100
        assert health.max_health == 100
        assert not health.is_dead
    
    def test_take_damage(self):
        """测试受到伤害"""
        health = HealthComponent(current=100, max_health=100)
        health.take_damage(30)
        assert health.current == 70
    
    def test_death_detection(self):
        """测试死亡检测"""
        health = HealthComponent(current=100, max_health=100)
        health.take_damage(100)
        assert health.is_dead
        assert health.current == 0
    
    def test_heal(self):
        """测试恢复生命"""
        health = HealthComponent(current=50, max_health=100)
        health.heal(20)
        assert health.current == 70
    
    def test_heal_cannot_exceed_max(self):
        """测试恢复不能超过最大值"""
        health = HealthComponent(current=90, max_health=100)
        health.heal(20)
        assert health.current == 100
```

---

## 调试技巧

### 1. 日志调试

```python
from src.core.logger import get_module_logger

logger = get_module_logger(__name__)

# 不同级别的日志
logger.debug("调试信息")
logger.info("一般信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")

# 格式化日志
logger.info(f"植物 {plant_id} 在位置 ({x}, {y}) 被创建")
logger.debug("攻击冷却: %.2f秒", cooldown)
```

### 2. 性能监控

```python
from src.core.spatial_hash import PerformanceMonitor

monitor = PerformanceMonitor(history_size=60)

# 在游戏循环中更新
monitor.update(dt, entity_count, collision_checks)

# 获取统计
stats = monitor.get_stats()
print(f"平均FPS: {stats['avg_fps']:.1f}")
print(f"平均帧时间: {stats['avg_frame_time_ms']:.2f}ms")
print(f"实体数量: {stats['current_entity_count']}")
```

### 3. 可视化调试

```python
# 在渲染系统中添加调试绘制
class RenderSystem(System):
    def render(self, component_manager: ComponentManager):
        # 正常渲染
        ...
        
        # 调试：绘制碰撞盒
        if self.debug_mode:
            for entity_id in entities:
                collision = component_manager.get_component(entity_id, CollisionComponent)
                transform = component_manager.get_component(entity_id, TransformComponent)
                if collision and transform:
                    self._draw_collision_box(transform, collision)
```

### 4. 断点调试

使用VS Code进行调试：

1. 在代码中设置断点（点击行号左侧）
2. 按F5启动调试
3. 使用调试控制台检查变量

```python
# 在关键位置添加断点
def update(self, dt: float, component_manager: ComponentManager) -> None:
    entities = component_manager.query(PlantComponent)  # 在这里设置断点
    
    for entity_id in entities:
        plant = component_manager.get_component(entity_id, PlantComponent)
        # 检查plant属性
        pass
```

---

## 性能优化

### 1. 使用空间哈希优化碰撞检测

```python
# 创建空间哈希
spatial_hash = SpatialHash(cell_size=100.0)

# 每帧更新
spatial_hash.clear()
for entity_id in entities:
    aabb = calculate_aabb(entity_id)
    spatial_hash.insert(entity_id, aabb)

# 查询附近实体（O(1)复杂度）
nearby = spatial_hash.get_nearby_entities(entity_id, radius=100.0)
```

### 2. 使用对象池减少GC

```python
from src.core.spatial_hash import ObjectPool

# 创建投射物对象池
projectile_pool = ObjectPool(
    factory_func=lambda: Projectile(),
    reset_func=lambda p: p.reset(),
    initial_size=50
)

# 使用对象池
proj = projectile_pool.acquire()
# ... 使用投射物 ...
projectile_pool.release(proj)
```

### 3. 批量渲染

```python
# 收集所有需要渲染的精灵
sprites_to_render = []
for entity_id in entities:
    sprite = component_manager.get_component(entity_id, SpriteComponent)
    if sprite:
        sprites_to_render.append(sprite)

# 批量渲染
for sprite in sorted(sprites_to_render, key=lambda s: s.z_index):
    sprite.draw()
```

### 4. 组件查询缓存

```python
# 缓存查询结果
cached_entities = None
cache_dirty = True

def update(self, dt: float, component_manager: ComponentManager) -> None:
    global cached_entities, cache_dirty
    
    # 只在需要时重新查询
    if cache_dirty or cached_entities is None:
        cached_entities = component_manager.query(PlantComponent, TransformComponent)
        cache_dirty = False
    
    # 使用缓存的实体列表
    for entity_id in cached_entities:
        ...
```

---

## 常见问题

### Q1: 实体创建后没有显示？

**可能原因**:
1. 缺少SpriteComponent
2. 位置设置错误（在屏幕外）
3. 缺少TransformComponent

**解决方案**:
```python
# 检查组件是否齐全
entity = world.create_entity()
world.add_component(entity, TransformComponent(x=100, y=200))
world.add_component(entity, SpriteComponent(color=(0, 255, 0), width=60, height=80))

# 检查位置是否在屏幕内
assert 0 <= transform.x <= SCREEN_WIDTH
assert 0 <= transform.y <= SCREEN_HEIGHT
```

### Q2: 碰撞检测不工作？

**可能原因**:
1. 碰撞层设置错误
2. 碰撞盒大小为0
3. 缺少CollisionComponent

**解决方案**:
```python
# 确保碰撞层设置正确
collision = CollisionComponent(
    width=60,
    height=80,
    layer=CollisionSystem.LAYER_PLANT,
    collides_with={CollisionSystem.LAYER_ZOMBIE}  # 确保设置了可碰撞的层
)
```

### Q3: 系统更新顺序错误？

**解决方案**:
```python
# 设置正确的优先级（数字越小越早执行）
world.add_system(MovementSystem(priority=10))      # 先移动
world.add_system(CollisionSystem(priority=20))     # 再检测碰撞
world.add_system(HealthSystem(priority=60))        # 最后处理伤害
```

### Q4: 配置文件加载失败？

**解决方案**:
```python
import os

# 检查文件路径
config_path = os.path.join("config", "game_config.toml")
print(f"配置文件路径: {os.path.abspath(config_path)}")
print(f"文件存在: {os.path.exists(config_path)}")

# 确保使用正确的编码
with open(config_path, 'rb') as f:
    import tomllib
    data = tomllib.load(f)
```

### Q5: 测试失败但代码看起来正确？

**排查步骤**:
1. 检查测试是否正确导入模块
2. 检查是否有全局状态污染
3. 使用pytest的--tb=short查看详细错误

```bash
# 运行单个测试文件
python -m pytest tests/test_core/test_game_state.py -v

# 显示详细错误信息
python -m pytest tests/test_core/test_game_state.py -v --tb=long

# 使用pdb调试失败的测试
python -m pytest tests/test_core/test_game_state.py -v --pdb
```

---

## 最佳实践

### 1. 组件设计原则

- **单一职责**: 每个组件只负责一种数据
- **无逻辑**: 组件只包含数据，不包含方法（除简单getter/setter）
- **可序列化**: 组件应该可以被JSON序列化（用于存档）

### 2. 系统设计原则

- **独立**: 系统之间尽量减少依赖
- **优先级**: 合理设置系统执行顺序
- **批量处理**: 一次处理多个实体，减少函数调用开销

### 3. 性能优化原则

- **早优化是万恶之源**: 先实现功能，再优化性能
- **测量再优化**: 使用性能监控工具找出瓶颈
- **空间换时间**: 使用缓存减少重复计算

---

## 贡献指南

### 提交代码流程

1. **创建分支**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **提交更改**
   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   ```

3. **运行测试**
   ```bash
   python -m pytest tests/ -v
   ```

4. **推送分支**
   ```bash
   git push origin feature/new-feature
   ```

5. **创建Pull Request**

### 提交信息规范

```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 重构
test: 测试相关
chore: 构建过程或辅助工具的变动
```

示例：
```
feat: 添加樱桃炸弹爆炸效果
fix: 修复僵尸死亡后未清理的问题
docs: 更新API文档
```

---

*本文档将持续更新，记录开发经验和最佳实践*
