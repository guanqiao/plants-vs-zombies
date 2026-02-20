# 植物大战僵尸 - Python Arcade版

一个使用Python和Arcade库实现的植物大战僵尸游戏，采用ECS（Entity-Component-System）架构。

## 项目特点

- **ECS架构**：使用Entity-Component-System架构，代码清晰、易于扩展
- **高性能**：使用空间哈希优化碰撞检测，性能提升10-100倍
- **模块化设计**：植物系统、僵尸系统、小游戏系统等模块独立
- **设计模式**：应用策略模式、单例模式、工厂模式等
- **完整测试**：包含196+个单元测试
- **类型安全**：完整的类型提示

## 项目结构

```
植物大战僵尸/
├── src/
│   ├── core/                    # 核心系统
│   │   ├── game_constants.py    # 游戏常量
│   │   ├── plant_config.py      # 植物配置
│   │   ├── spatial_hash.py      # 空间哈希
│   │   └── config_manager.py    # 配置管理
│   ├── ecs/                     # ECS架构
│   │   ├── components/          # 组件定义
│   │   ├── systems/             # 系统实现
│   │   │   └── plants/          # 植物系统
│   │   ├── entity.py            # 实体
│   │   ├── component.py         # 组件管理
│   │   └── system.py            # 系统基类
│   ├── systems/                 # 游戏系统
│   │   └── mini_games/          # 小游戏
│   ├── arcade_game/             # Arcade游戏
│   │   ├── game_window.py       # 游戏窗口
│   │   ├── planting_system.py   # 种植系统
│   │   ├── zombie_spawner.py    # 僵尸生成器
│   │   └── ...
│   └── ui/                      # UI模块
├── tests/                       # 测试
├── config/                      # 配置文件
└── assets/                      # 资源文件
```

## 安装和运行

### 环境要求

- Python 3.10+
- Arcade 2.6+
- Pytest 7.0+（测试）

### 安装依赖

```bash
pip install arcade pytest
```

### 运行游戏

```bash
python main_arcade.py
```

### 运行测试

```bash
python -m pytest tests/ -v
```

## 游戏功能

### 核心玩法

- **种植植物**：在草坪上种植各种植物对抗僵尸
- **收集阳光**：点击掉落的阳光收集资源
- **防御僵尸**：阻止僵尸到达房子

### 植物类型

- **射手类**：豌豆射手、寒冰射手、双发射手、三线射手
- **爆炸类**：樱桃炸弹、土豆雷
- **近战类**：大嘴花、地刺
- **投手类**：西瓜投手、冰西瓜
- **辅助类**：磁力菇、向日葵

### 小游戏

- **僵尸水族馆**：喂养僵尸收集金币
- **宝石迷阵**：匹配消除游戏
- **坚果保龄球**：滚动坚果击倒僵尸

## 架构设计

### ECS架构

```
Entity（实体）
  └── Component（组件）
        └── System（系统）
```

### 植物系统架构

```
BasePlantSystem（基类）
  ├── ShooterPlantSystem（射手）
  ├── ExplosivePlantSystem（爆炸）
  ├── MeleePlantSystem（近战）
  ├── LobberPlantSystem（投手）
  └── SupportPlantSystem（辅助）
```

### 攻击策略模式

```python
# 使用策略模式消除if-elif链
strategy = AttackStrategyRegistry.get_strategy(plant_type)
strategy.execute(...)
```

## 性能优化

- **空间哈希**：O(n²)碰撞检测优化到O(n)
- **对象池**：减少内存分配
- **批量渲染**：使用Arcade的批处理

## 重构历史

1. **集成空间哈希**：碰撞检测性能提升10-100倍
2. **统一配置数据源**：消除硬编码配置
3. **拆分PlantBehaviorSystem**：6个专门的植物系统
4. **拆分mini_games**：模块化小游戏
5. **策略模式重构**：消除复杂if-elif链
6. **提取魔法数字**：集中管理常量

## 测试覆盖

```
总测试数：196+
覆盖率：85%+
```

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 致谢

- 原版游戏：PopCap Games
- Arcade库：Python游戏开发框架
- ECS架构参考：游戏开发最佳实践
