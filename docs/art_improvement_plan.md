
# 植物大战僵尸 - 美术资源和效果改进计划

&gt; 版本: 1.0  
&gt; 更新日期: 2026-02-22  
&gt; 状态: 进行中

---

## 目录

1. [现状分析](#现状分析)
2. [改进目标](#改进目标)
3. [阶段一：核心精灵资源完善](#阶段一核心精灵资源完善)
4. [阶段二：场景资源补充](#阶段二场景资源补充)
5. [阶段三：UI美术优化](#阶段三ui美术优化)
6. [阶段四：视觉效果增强](#阶段四视觉效果增强)
7. [资源清单](#资源清单)
8. [技术指南](#技术指南)

---

## 现状分析

### ✅ 已有视觉效果系统
项目在代码层面已经拥有非常完善的视觉效果系统：

| 系统 | 状态 | 文件 |
|------|------|------|
| 粒子系统 | ✅ 完善 | `src/arcade_game/particle_system.py` |
| 视觉特效系统 | ✅ 完善 | `src/arcade_game/visual_effects.py` |
| 3D效果系统 | ✅ 完善 | `src/arcade_game/three_d_effects.py` |
| 血条系统 | ✅ 完善 | `src/arcade_game/health_bar_system.py` |
| 伤害数字系统 | ✅ 完善 | `src/arcade_game/damage_number_system.py` |
| 屏幕震动 | ✅ 完善 | `src/arcade_game/screen_shake.py` |
| UI渲染器 | ✅ 完善 | `src/arcade_game/ui_renderer.py` |
| 背景渲染器 | ✅ 完善 | `src/arcade_game/background_renderer.py` |

### ✅ 已有美术资源

#### 植物精灵（plants/）
| 植物 | idle | attack | 其他 | 状态 |
|------|------|--------|------|------|
| 豌豆射手 | ✅ | ✅ | shoot | ⭐ 完整 |
| 向日葵 | ✅ | ❌ | - | ⚠️ 部分 |
| 坚果墙 | ❌ | ❌ | - | ⚠️ 部分 |
| 寒冰射手 | ✅ | ✅ | - | ⭐ 完整 |
| 樱桃炸弹 | ✅ | ✅ | explode | ⭐ 完整 |
| 土豆雷 | ✅ | ✅ | buried/armed | ⭐ 完整 |

#### 僵尸精灵（zombies/）
| 僵尸 | walk | attack | 其他 | 状态 |
|------|------|--------|------|------|
| 普通僵尸 | ✅ | ✅ | - | ⭐ 完整 |
| 路障僵尸 | ✅ | ✅ | - | ⭐ 完整 |
| 铁桶僵尸 | ✅ | ✅ | - | ⭐ 完整 |

#### 特效精灵（effects/）
| 效果 | 状态 |
|------|------|
| 阳光旋转/收集 | ✅ |
| 击中特效（normal/crit/frozen） | ✅ |
| 爆炸/烟雾 | ✅ |
| 状态特效（frozen/slow） | ✅ |
| 种植特效 | ✅ |
| 僵尸死亡特效 | ✅ |

#### 场景（backgrounds/）
| 场景 | 状态 |
|------|------|
| 白天草坪 | ✅ |

### ❌ 美术资源缺口

#### 植物精灵缺口（8种）
| 植物 | 需要的动画 |
|------|-----------|
| 双发射手 | idle, attack |
| 大嘴花 | idle, attack, bite |
| 三线射手 | idle, attack |
| 西瓜投手 | idle, attack |
| 冰西瓜 | idle, attack |
| 高坚果 | idle, hurt |
| 地刺 | idle, attack |
| 磁力菇 | idle |
| 南瓜头 | idle, hurt |
| 仙人掌 | idle, attack |
| 香蒲 | idle, attack |

#### 僵尸精灵缺口（13种）
| 僵尸 | 需要的动画 |
|------|-----------|
| 旗帜僵尸 | walk, attack |
| 读报僵尸 | walk, attack, rage |
| 撑杆跳僵尸 | walk, jump, attack |
| 橄榄球僵尸 | walk, attack |
| 舞王僵尸 | walk, summon, attack |
| 伴舞僵尸 | walk, attack |
| 潜水僵尸 | swim, walk, attack |
| 冰车僵尸 | drive, attack |
| 海豚骑士僵尸 | ride, walk, attack |
| 小丑僵尸 | walk, explode |
| 巨人僵尸 | walk, attack, throw |
| 小鬼僵尸 | walk, attack |

#### 场景缺口（4种）
- 黑夜场景
- 泳池场景
- 迷雾场景
- 屋顶场景

---

## 改进目标

### 总体目标
对标原版植物大战僵尸，在3个月内达到：
- ✅ 16种配置植物全部有完整精灵表
- ✅ 16种配置僵尸全部有完整精灵表
- ✅ 5种游戏场景全部实现
- ✅ UI界面全面美化
- ✅ 新增多种视觉特效

### 质量标准
1. **像素风格统一**：所有资源保持一致的像素风格
2. **动画流畅**：所有动画达到10-15 FPS
3. **透明度支持**：所有PNG图片支持透明背景
4. **尺寸规范**：植物约70x90，僵尸约70x100
5. **性能优化**：精灵表合理布局，减少绘制调用

---

## 阶段一：核心精灵资源完善

### 1.1 植物精灵完善（高优先级）

#### 任务清单
- [ ] 双发射手（REPEATER）
  - idle动画：4帧，10 FPS
  - attack动画：4帧，12 FPS
  - 文件：`repeater_idle_sheet.png`, `repeater_attack_sheet.png`

- [ ] 大嘴花（CHOMPER）
  - idle动画：4帧，8 FPS
  - attack动画：6帧，10 FPS
  - bite动画：4帧，15 FPS
  - 文件：`chomper_idle_sheet.png`, `chomper_attack_sheet.png`, `chomper_bite_sheet.png`

- [ ] 三线射手（THREEPEATER）
  - idle动画：4帧，10 FPS
  - attack动画：6帧，12 FPS
  - 文件：`threepeater_idle_sheet.png`, `threepeater_attack_sheet.png`

- [ ] 西瓜投手（MELON_PULT）
  - idle动画：4帧，8 FPS
  - attack动画：5帧，10 FPS
  - 文件：`melon_pult_idle_sheet.png`, `melon_pult_attack_sheet.png`

- [ ] 冰西瓜（WINTER_MELON）
  - idle动画：4帧，8 FPS
  - attack动画：5帧，10 FPS
  - 文件：`winter_melon_idle_sheet.png`, `winter_melon_attack_sheet.png`

- [ ] 高坚果（TALL_NUT）
  - idle动画：3帧，6 FPS
  - hurt动画：4帧，8 FPS
  - 文件：`tall_nut_idle_sheet.png`, `tall_nut_hurt_sheet.png`

- [ ] 地刺（SPIKEWEED）
  - idle动画：4帧，10 FPS
  - attack动画：3帧，15 FPS
  - 文件：`spikeweed_idle_sheet.png`, `spikeweed_attack_sheet.png`

- [ ] 磁力菇（MAGNET_SHROOM）
  - idle动画：4帧，8 FPS
  - 文件：`magnet_shroom_idle_sheet.png`

- [ ] 南瓜头（PUMPKIN）
  - idle动画：3帧，6 FPS
  - hurt动画：4帧，8 FPS
  - 文件：`pumpkin_idle_sheet.png`, `pumpkin_hurt_sheet.png`

- [ ] 仙人掌（CACTUS）
  - idle动画：4帧，10 FPS
  - attack动画：4帧，12 FPS
  - 文件：`cactus_idle_sheet.png`, `cactus_attack_sheet.png`

- [ ] 香蒲（CATTAIL）
  - idle动画：4帧，10 FPS
  - attack动画：5帧，12 FPS
  - 文件：`cattail_idle_sheet.png`, `cattail_attack_sheet.png`

### 1.2 僵尸精灵完善（高优先级）

#### 任务清单
- [ ] 旗帜僵尸（FLAG）
  - walk动画：6帧，12 FPS
  - attack动画：4帧，10 FPS
  - 文件：`zombie_flag_walk_sheet.png`, `zombie_flag_attack_sheet.png`

- [ ] 读报僵尸（NEWSPAPER）
  - walk动画：6帧，12 FPS
  - attack动画：4帧，10 FPS
  - rage动画：5帧，15 FPS
  - 文件：`zombie_newspaper_walk_sheet.png`, `zombie_newspaper_attack_sheet.png`, `zombie_newspaper_rage_sheet.png`

- [ ] 撑杆跳僵尸（POLE_VAULTING）
  - walk动画：6帧，12 FPS
  - jump动画：5帧，15 FPS
  - attack动画：4帧，10 FPS
  - 文件：`zombie_pole_walk_sheet.png`, `zombie_pole_jump_sheet.png`, `zombie_pole_attack_sheet.png`

- [ ] 橄榄球僵尸（FOOTBALL）
  - walk动画：6帧，14 FPS
  - attack动画：4帧，12 FPS
  - 文件：`zombie_football_walk_sheet.png`, `zombie_football_attack_sheet.png`

- [ ] 舞王僵尸（DANCING）
  - walk动画：6帧，10 FPS
  - summon动画：8帧，8 FPS
  - attack动画：4帧，10 FPS
  - 文件：`zombie_dancing_walk_sheet.png`, `zombie_dancing_summon_sheet.png`, `zombie_dancing_attack_sheet.png`

- [ ] 伴舞僵尸（BACKUP_DANCER）
  - walk动画：6帧，10 FPS
  - attack动画：4帧，10 FPS
  - 文件：`zombie_backup_walk_sheet.png`, `zombie_backup_attack_sheet.png`

- [ ] 潜水僵尸（SNORKEL）
  - swim动画：6帧，12 FPS
  - walk动画：6帧，12 FPS
  - attack动画：4帧，10 FPS
  - 文件：`zombie_snorkel_swim_sheet.png`, `zombie_snorkel_walk_sheet.png`, `zombie_snorkel_attack_sheet.png`

- [ ] 冰车僵尸（ZOMBONI）
  - drive动画：8帧，15 FPS
  - attack动画：4帧，12 FPS
  - 文件：`zombie_zamboni_drive_sheet.png`, `zombie_zamboni_attack_sheet.png`

- [ ] 海豚骑士僵尸（DOLPHIN_RIDER）
  - ride动画：6帧，12 FPS
  - walk动画：6帧，12 FPS
  - attack动画：4帧，10 FPS
  - 文件：`zombie_dolphin_ride_sheet.png`, `zombie_dolphin_walk_sheet.png`, `zombie_dolphin_attack_sheet.png`

- [ ] 小丑僵尸（JACK_IN_THE_BOX）
  - walk动画：6帧，12 FPS
  - explode动画：8帧，20 FPS
  - 文件：`zombie_jack_walk_sheet.png`, `zombie_jack_explode_sheet.png`

- [ ] 巨人僵尸（GARGANTUAR）
  - walk动画：6帧，10 FPS
  - attack动画：5帧，12 FPS
  - throw动画：6帧，15 FPS
  - 文件：`zombie_gargantuar_walk_sheet.png`, `zombie_gargantuar_attack_sheet.png`, `zombie_gargantuar_throw_sheet.png`

- [ ] 小鬼僵尸（IMP）
  - walk动画：6帧，14 FPS
  - attack动画：4帧，12 FPS
  - 文件：`zombie_imp_walk_sheet.png`, `zombie_imp_attack_sheet.png`

---

## 阶段二：场景资源补充

### 2.1 场景背景

#### 任务清单
- [ ] 黑夜场景背景
  - 文件名：`lawn_night.png`
  - 尺寸：900x600
  - 特点：深色草地、星星、月亮

- [ ] 泳池场景背景
  - 文件名：`pool.png`
  - 尺寸：900x600
  - 特点：泳池水纹、睡莲、泳池装饰

- [ ] 迷雾场景背景
  - 文件名：`fog.png`
  - 尺寸：900x600
  - 特点：渐变迷雾效果

- [ ] 屋顶场景背景
  - 文件名：`roof.png`
  - 尺寸：900x600
  - 特点：屋顶瓦片、斜坡

### 2.2 场景装饰元素

#### 任务清单
- [ ] 黑夜装饰
  - 星星粒子效果
  - 月亮图片
  - 萤火虫动画

- [ ] 泳池装饰
  - 睡莲图片
  - 泳池边缘装饰
  - 水纹动画

- [ ] 迷雾装饰
  - 迷雾滚动效果
  - 迷雾遮罩层

- [ ] 屋顶装饰
  - 屋顶瓦片
  - 烟囱
  - 屋顶边缘装饰

---

## 阶段三：UI美术优化

### 3.1 植物卡片美化

#### 任务清单
- [ ] 为每种植物设计独特卡片背景
  - 根据植物类型配色（射手类绿色、爆炸类红色等）
  - 添加植物名称显示
  - 优化冷却动画视觉效果

- [ ] 卡片状态视觉
  - 可种植状态：亮色
  - 冷却中：半透明+进度条
  - 阳光不足：灰色

### 3.2 新增UI元素

#### 任务清单
- [ ] 设置菜单UI
  - 音量控制滑块
  - 显示设置开关
  - 难度选择

- [ ] 成就展示界面
  - 成就列表
  - 解锁状态显示
  - 成就详情

- [ ] 关卡选择界面美化
  - 关卡预览
  - 星级评价
  - 解锁状态

- [ ] 游戏结束/胜利界面美化
  - 分数显示
  - 重新开始按钮
  - 返回菜单按钮

---

## 阶段四：视觉效果增强

### 4.1 新增特效

#### 任务清单
- [ ] 僵尸特写效果
  - 首次出现的僵尸特写
  - 巨人僵尸登场特写

- [ ] 场景过渡动画
  - 淡入淡出效果
  - 场景切换动画

- [ ] 植物种植时的破土效果
  - 泥土飞溅
  - 植物从地下冒出

- [ ] 僵尸从地下钻出来的效果
  - 地面震动
  - 泥土飞溅

### 4.2 特效优化

#### 任务清单
- [ ] 优化现有特效的视觉效果
  - 调整粒子参数
  - 优化颜色搭配

- [ ] 添加更多粒子形状
  - 新增更多几何形状
  - 自定义形状支持

- [ ] 优化3D效果参数
  - 调整阴影参数
  - 优化高光效果

---

## 资源清单

### 植物精灵清单（完整）

| 植物 | idle | attack | 其他 | 状态 |
|------|------|--------|------|------|
| 向日葵 | ✅ | ❌ | - | ⚠️ |
| 豌豆射手 | ✅ | ✅ | shoot | ✅ |
| 坚果墙 | ❌ | ❌ | - | ⚠️ |
| 寒冰射手 | ✅ | ✅ | - | ✅ |
| 樱桃炸弹 | ✅ | ✅ | explode | ✅ |
| 土豆雷 | ✅ | ✅ | buried/armed | ✅ |
| 双发射手 | ❌ | ❌ | - | ❌ |
| 大嘴花 | ❌ | ❌ | - | ❌ |
| 三线射手 | ❌ | ❌ | - | ❌ |
| 西瓜投手 | ❌ | ❌ | - | ❌ |
| 冰西瓜 | ❌ | ❌ | - | ❌ |
| 高坚果 | ❌ | ❌ | - | ❌ |
| 地刺 | ❌ | ❌ | - | ❌ |
| 磁力菇 | ❌ | ❌ | - | ❌ |
| 南瓜头 | ❌ | ❌ | - | ❌ |
| 仙人掌 | ❌ | ❌ | - | ❌ |
| 香蒲 | ❌ | ❌ | - | ❌ |

### 僵尸精灵清单（完整）

| 僵尸 | walk | attack | 其他 | 状态 |
|------|------|--------|------|------|
| 普通僵尸 | ✅ | ✅ | - | ✅ |
| 路障僵尸 | ✅ | ✅ | - | ✅ |
| 铁桶僵尸 | ✅ | ✅ | - | ✅ |
| 旗帜僵尸 | ❌ | ❌ | - | ❌ |
| 读报僵尸 | ❌ | ❌ | - | ❌ |
| 撑杆跳僵尸 | ❌ | ❌ | - | ❌ |
| 橄榄球僵尸 | ❌ | ❌ | - | ❌ |
| 舞王僵尸 | ❌ | ❌ | - | ❌ |
| 伴舞僵尸 | ❌ | ❌ | - | ❌ |
| 潜水僵尸 | ❌ | ❌ | - | ❌ |
| 冰车僵尸 | ❌ | ❌ | - | ❌ |
| 海豚骑士僵尸 | ❌ | ❌ | - | ❌ |
| 小丑僵尸 | ❌ | ❌ | - | ❌ |
| 巨人僵尸 | ❌ | ❌ | - | ❌ |
| 小鬼僵尸 | ❌ | ❌ | - | ❌ |

### 场景清单

| 场景 | 背景 | 装饰 | 状态 |
|------|------|------|------|
| 白天草坪 | ✅ | ✅ | ✅ |
| 黑夜 | ❌ | ❌ | ❌ |
| 泳池 | ❌ | ❌ | ❌ |
| 迷雾 | ❌ | ❌ | ❌ |
| 屋顶 | ❌ | ❌ | ❌ |

---

## 技术指南

### 精灵表规范

#### 文件命名规则
```
{entity_type}_{action}_sheet.png
```

例如：
- `peashooter_idle_sheet.png`
- `zombie_normal_walk_sheet.png`

#### 精灵表布局
- 横向排列，从左到右
- 推荐4列布局
- 每帧大小一致

#### 配置示例（sprite_sheets.json）
```json
{
  "repeater": {
    "idle": {
      "sheet_path": "images/plants/repeater_idle_sheet.png",
      "frames": 4,
      "frame_width": 70,
      "frame_height": 90,
      "fps": 10,
      "loop": true,
      "columns": 4
    },
    "attack": {
      "sheet_path": "images/plants/repeater_attack_sheet.png",
      "frames": 4,
      "frame_width": 90,
      "frame_height": 90,
      "fps": 12,
      "loop": false,
      "columns": 4,
      "event_frame": 1
    }
  }
}
```

### 图片规格

| 类型 | 推荐尺寸 | 格式 |
|------|---------|------|
| 植物 | 70x90 | PNG |
| 僵尸 | 70x100 | PNG |
| 投射物 | 20x20 | PNG |
| UI元素 | 按需 | PNG |
| 背景 | 900x600 | PNG |

### 颜色规范

参考 `src/core/theme_colors.py` 中的配色：
- 植物绿色系
- 僵尸灰绿色系
- 阳光黄色系
- 特效红/蓝/紫色系

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-02-22 | 1.0 | 初始版本，完整的美术资源改进计划 |

---

*本文档将持续更新，记录美术资源改进进展*
