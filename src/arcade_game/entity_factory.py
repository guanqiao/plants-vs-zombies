"""
实体工厂 - 创建游戏实体的工厂类
"""

import os
from pathlib import Path
from ..ecs import World, Entity
from ..core.logger import get_module_logger


logger = get_module_logger(__name__)
from ..ecs.components import (
    TransformComponent, SpriteComponent, HealthComponent,
    VelocityComponent, CollisionComponent, GridPositionComponent,
    PlantComponent, PlantTypeComponent, PlantType, PLANT_CONFIGS,
    ZombieComponent, ZombieTypeComponent, ZombieType, ZOMBIE_CONFIGS,
    ProjectileComponent, ProjectileTypeComponent, ProjectileType, PROJECTILE_CONFIGS,
    SunProducerComponent, AnimationComponent, AnimationState
)
from ..ecs.systems import CollisionSystem
from .sprite_manager import get_sprite_manager, Animation, AnimationFrame


class EntityFactory:
    """
    实体工厂
    
    提供创建各种游戏实体的便捷方法
    """
    
    def __init__(self, world: World):
        self.world = world
        self.sprite_manager = get_sprite_manager()
        self._load_real_sprites()
        self._init_placeholder_animations()
    
    def _load_real_sprites(self) -> None:
        """尝试加载真实的精灵图资源"""
        plants_dir = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", "plants")
        zombies_dir = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", "zombies")
        projectiles_dir = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", "projectiles")
        
        plant_sprites = {
            PlantType.PEASHOOTER: ("peashooter.png", (124, 252, 0)),
            PlantType.SUNFLOWER: ("sunflower.png", (255, 215, 0)),
            PlantType.CHERRY_BOMB: ("cherry_bomb.png", (220, 20, 60)),
            PlantType.WALLNUT: ("wallnut.png", (210, 180, 140)),
            PlantType.SNOW_PEA: ("snow_pea.png", (135, 206, 250)),
            PlantType.REPEATER: ("repeater.png", (124, 252, 0)),
        }
        
        for plant_type, (filename, fallback_color) in plant_sprites.items():
            sprite_path = os.path.join(plants_dir, filename)
            if os.path.exists(sprite_path):
                try:
                    texture = self.sprite_manager.load_texture(f"plant_{plant_type.name}", sprite_path)
                    if texture:
                        continue
                except Exception:
                    pass
        
        # 动态获取所有僵尸类型
        zombie_sprites = {}
        for zombie_type in ZombieType:
            # 根据类型名称生成文件名
            filename = f"{zombie_type.name.lower()}.png"
            # 默认颜色映射
            color_map = {
                ZombieType.NORMAL: (144, 164, 144),
                ZombieType.CONEHEAD: (255, 140, 0),
                ZombieType.BUCKETHEAD: (128, 128, 128),
            }
            fallback_color = color_map.get(zombie_type, (128, 128, 128))
            zombie_sprites[zombie_type] = (filename, fallback_color)
        
        for zombie_type, (filename, fallback_color) in zombie_sprites.items():
            sprite_path = os.path.join(zombies_dir, filename)
            if os.path.exists(sprite_path):
                try:
                    texture = self.sprite_manager.load_texture(f"zombie_{zombie_type.name}", sprite_path)
                    if texture:
                        continue
                except Exception:
                    pass
        
        projectile_sprites = {
            ProjectileType.PEA: ("pea.png", (124, 252, 0)),
            ProjectileType.FROZEN_PEA: ("frozen_pea.png", (135, 206, 250)),
        }
        
        for proj_type, (filename, fallback_color) in projectile_sprites.items():
            sprite_path = os.path.join(projectiles_dir, filename)
            if os.path.exists(sprite_path):
                try:
                    texture = self.sprite_manager.load_texture(f"projectile_{proj_type.name}", sprite_path)
                    if texture:
                        continue
                except Exception:
                    pass
    
    def _load_sprite_sheet_config(self) -> dict:
        """加载精灵表配置文件"""
        import json
        from pathlib import Path
        
        config_path = Path(__file__).parent.parent.parent / 'assets' / 'animations' / 'sprite_sheets.json'
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载精灵表配置失败: {e}")
        return {}
    
    def _load_sprite_sheet_animation(self, sheet_config: dict, assets_dir: Path) -> list:
        """从精灵表加载动画帧"""
        import arcade
        
        frames = []
        sheet_path = assets_dir / sheet_config['sheet_path']
        
        if not sheet_path.exists():
            return frames
        
        try:
            # 加载精灵表
            sheet_texture = arcade.load_texture(str(sheet_path))
            
            frame_width = sheet_config['frame_width']
            frame_height = sheet_config['frame_height']
            num_frames = sheet_config['frames']
            columns = sheet_config.get('columns', 4)
            fps = sheet_config.get('fps', 10)
            frame_duration = 1.0 / fps
            
            # 提取每一帧
            for i in range(num_frames):
                col = i % columns
                row = i // columns
                
                x = col * frame_width
                y = row * frame_height
                
                # 从精灵表裁剪单帧
                frame_texture = arcade.Texture(
                    name=f"{sheet_path.stem}_frame_{i}",
                    image=sheet_texture.image.crop((
                        x, y,
                        x + frame_width,
                        y + frame_height
                    ))
                )
                frames.append(AnimationFrame(frame_texture, frame_duration))
                
        except Exception as e:
            logger.warning(f"加载精灵表失败 {sheet_path}: {e}")
        
        return frames
    
    def _init_placeholder_animations(self) -> None:
        """初始化动画（优先使用精灵表，其次使用单图，最后使用占位符）"""
        import arcade
        from pathlib import Path
        
        # 资源路径
        assets_dir = Path(__file__).parent.parent.parent / 'assets'
        images_dir = assets_dir / 'images'
        
        # 加载精灵表配置
        sprite_sheet_config = self._load_sprite_sheet_config()
        sprite_sheets = sprite_sheet_config.get('sprite_sheets', {})
        
        # 植物图片映射（单图，作为后备）
        plant_image_map = {
            PlantType.PEASHOOTER: {
                'idle': ['plants/peashooter.png'],
                'attack': ['plants/peashooter_shoot.png', 'plants/peashooter.png']
            },
            PlantType.SUNFLOWER: {
                'idle': ['plants/sunflower.png'],
                'attack': ['plants/sunflower.png']
            },
            PlantType.WALLNUT: {
                'idle': ['plants/wallnut.png'],
                'attack': ['plants/wallnut.png']
            }
        }
        
        # 僵尸图片映射（单图，作为后备）
        zombie_image_map = {
            ZombieType.NORMAL: {
                'walk': ['zombies/zombie_normal.png'],
                'attack': ['zombies/zombie_normal.png']
            }
        }
        
        # 投射物图片映射
        projectile_image_map = {
            ProjectileType.PEA: 'projectiles/pea.png',
            ProjectileType.FROZEN_PEA: 'projectiles/frozen_pea.png'
        }
        
        # 为每种植物类型创建动画
        for plant_type in PlantType:
            config = PLANT_CONFIGS.get(plant_type, {})
            color = config.get('color', (0, 200, 0))
            width = config.get('width', 60)
            height = config.get('height', 80)
            
            # 获取精灵表配置
            plant_sheet_config = sprite_sheets.get(plant_type.name.lower(), {})
            
            # 获取单图配置（作为后备）
            image_config = plant_image_map.get(plant_type, {})
            
            # 创建空闲动画（优先使用精灵表）
            idle_frames = []
            
            # 尝试从精灵表加载
            if 'idle' in plant_sheet_config:
                idle_frames = self._load_sprite_sheet_animation(
                    plant_sheet_config['idle'], assets_dir
                )
            
            # 如果精灵表加载失败，尝试单图
            if not idle_frames:
                idle_images = image_config.get('idle', [])
                if idle_images:
                    for img_path in idle_images:
                        full_path = images_dir / img_path
                        if full_path.exists():
                            texture = arcade.load_texture(str(full_path))
                            idle_frames.append(AnimationFrame(texture, 0.3))
            
            # 如果没有图片，使用占位符
            if not idle_frames:
                for i in range(4):
                    scale = 1.0 + 0.05 * (i if i < 2 else 4 - i)
                    texture_name = f"plant_{plant_type.name}_idle_{i}"
                    texture = self.sprite_manager.create_placeholder_texture(
                        texture_name, int(width * scale), height, color
                    )
                    idle_frames.append(AnimationFrame(texture, 0.2))
            
            anim = Animation(f"plant_{plant_type.name}_idle", idle_frames, loop=True)
            self.sprite_manager.register_animation(f"plant_{plant_type.name}_idle", anim)
            
            # 创建攻击动画（优先使用精灵表）
            attack_frames = []
            
            # 尝试从精灵表加载
            if 'attack' in plant_sheet_config:
                attack_frames = self._load_sprite_sheet_animation(
                    plant_sheet_config['attack'], assets_dir
                )
            
            # 如果精灵表加载失败，尝试单图
            if not attack_frames:
                attack_images = image_config.get('attack', [])
                if attack_images:
                    for img_path in attack_images:
                        full_path = images_dir / img_path
                        if full_path.exists():
                            texture = arcade.load_texture(str(full_path))
                            attack_frames.append(AnimationFrame(texture, 0.15))
            
            if not attack_frames:
                for i in range(3):
                    texture_name = f"plant_{plant_type.name}_attack_{i}"
                    texture = self.sprite_manager.create_placeholder_texture(
                        texture_name, width, height, color
                    )
                    attack_frames.append(AnimationFrame(texture, 0.1))
            
            attack_anim = Animation(f"plant_{plant_type.name}_attack", attack_frames, loop=False)
            self.sprite_manager.register_animation(f"plant_{plant_type.name}_attack", attack_anim)
        
        # 为每种僵尸类型创建动画
        for zombie_type in ZombieType:
            config = ZOMBIE_CONFIGS.get(zombie_type, {})
            color = config.get('color', (128, 128, 128))
            width = config.get('width', 50)
            height = config.get('height', 80)
            
            # 获取精灵表配置
            zombie_sheet_config = sprite_sheets.get(f"zombie_{zombie_type.name.lower()}", {})
            
            # 获取单图配置（作为后备）
            image_config = zombie_image_map.get(zombie_type, {})
            
            # 创建行走动画（优先使用精灵表）
            walk_frames = []
            
            # 尝试从精灵表加载
            if 'walk' in zombie_sheet_config:
                walk_frames = self._load_sprite_sheet_animation(
                    zombie_sheet_config['walk'], assets_dir
                )
            
            # 如果精灵表加载失败，尝试单图
            if not walk_frames:
                walk_images = image_config.get('walk', [])
                if walk_images:
                    for img_path in walk_images:
                        full_path = images_dir / img_path
                        if full_path.exists():
                            texture = arcade.load_texture(str(full_path))
                            walk_frames.append(AnimationFrame(texture, 0.2))
            
            if not walk_frames:
                for i in range(4):
                    texture_name = f"zombie_{zombie_type.name}_walk_{i}"
                    texture = self.sprite_manager.create_placeholder_texture(
                        texture_name, width, height, color
                    )
                    walk_frames.append(AnimationFrame(texture, 0.15))
            
            anim = Animation(f"zombie_{zombie_type.name}_walk", walk_frames, loop=True)
            self.sprite_manager.register_animation(f"zombie_{zombie_type.name}_walk", anim)
            
            # 创建攻击动画（优先使用精灵表）
            attack_frames = []
            
            # 尝试从精灵表加载
            if 'attack' in zombie_sheet_config:
                attack_frames = self._load_sprite_sheet_animation(
                    zombie_sheet_config['attack'], assets_dir
                )
            
            # 如果精灵表加载失败，尝试单图
            if not attack_frames:
                attack_images = image_config.get('attack', [])
                if attack_images:
                    for img_path in attack_images:
                        full_path = images_dir / img_path
                        if full_path.exists():
                            texture = arcade.load_texture(str(full_path))
                            attack_frames.append(AnimationFrame(texture, 0.2))
            
            if not attack_frames:
                for i in range(3):
                    texture_name = f"zombie_{zombie_type.name}_attack_{i}"
                    texture = self.sprite_manager.create_placeholder_texture(
                        texture_name, width, height, color
                    )
                    attack_frames.append(AnimationFrame(texture, 0.15))
            
            attack_anim = Animation(f"zombie_{zombie_type.name}_attack", attack_frames, loop=True)
            self.sprite_manager.register_animation(f"zombie_{zombie_type.name}_attack", attack_anim)
        
        # 为投射物创建纹理
        for proj_type in ProjectileType:
            config = PROJECTILE_CONFIGS.get(proj_type, {})
            color = config.get('color', (0, 255, 0))
            width = config.get('width', 15)
            height = config.get('height', 15)
            
            texture_name = f"projectile_{proj_type.name}"
            image_path = projectile_image_map.get(proj_type)
            
            if image_path:
                full_path = assets_dir / image_path
                if full_path.exists():
                    texture = arcade.load_texture(str(full_path))
                    self.sprite_manager._textures[texture_name] = texture
                    continue
            
            # 使用占位符
            self.sprite_manager.create_colored_circle_texture(texture_name, width // 2, color)
    
    def create_plant(self, plant_type: PlantType, x: float, y: float, 
                     row: int, col: int) -> Entity:
        """
        创建植物实体
        
        Args:
            plant_type: 植物类型
            x: X坐标
            y: Y坐标
            row: 网格行
            col: 网格列
            
        Returns:
            创建的实体
        """
        entity = self.world.create_entity()
        config = PLANT_CONFIGS.get(plant_type, {})
        
        # 变换组件
        transform = TransformComponent(x=x, y=y)
        self.world.add_component(entity, transform)
        
        # 精灵组件
        sprite = SpriteComponent(
            color=config.get('color', (0, 200, 0)),
            width=config.get('width', 60),
            height=config.get('height', 80)
        )
        self.world.add_component(entity, sprite)
        
        # 动画组件
        anim_comp = AnimationComponent(
            current_state=AnimationState.IDLE,
            default_state=AnimationState.IDLE,
            z_index=20  # 植物层级
        )
        
        # 添加动画
        idle_anim = self.sprite_manager.get_animation(f"plant_{plant_type.name}_idle")
        if idle_anim:
            anim_comp.add_animation(AnimationState.IDLE, idle_anim)
            # 明确播放待机动画
            anim_comp.play(AnimationState.IDLE)
        
        attack_anim = self.sprite_manager.get_animation(f"plant_{plant_type.name}_attack")
        if attack_anim:
            anim_comp.add_animation(AnimationState.ATTACK, attack_anim)
        
        self.world.add_component(entity, anim_comp)
        
        # 生命值组件
        health = HealthComponent(
            current=config.get('health', 100),
            max_health=config.get('health', 100)
        )
        self.world.add_component(entity, health)
        
        # 碰撞组件
        collision = CollisionComponent(
            width=config.get('width', 60),
            height=config.get('height', 80),
            layer=CollisionSystem.LAYER_PLANT,
            collides_with={CollisionSystem.LAYER_ZOMBIE}
        )
        self.world.add_component(entity, collision)
        
        # 网格位置组件
        grid_pos = GridPositionComponent(row=row, col=col, is_occupied=True)
        self.world.add_component(entity, grid_pos)
        
        # 植物类型组件
        plant_type_comp = PlantTypeComponent(plant_type=plant_type)
        self.world.add_component(entity, plant_type_comp)
        
        # 植物组件
        plant = PlantComponent(
            cost=config.get('cost', 100),
            attack_cooldown=config.get('attack_cooldown', 1.5),
            attack_damage=config.get('attack_damage', 20),
            is_armed=config.get('is_armed', True),
            is_ready=True,  # 新放置的植物应该可以立即攻击
            attack_range=config.get('attack_range', 800.0)
        )
        self.world.add_component(entity, plant)
        
        # 阳光生产组件（仅向日葵）
        if plant_type == PlantType.SUNFLOWER:
            sun_producer = SunProducerComponent(
                production_amount=25,
                production_interval=5.0,
                is_auto=True
            )
            self.world.add_component(entity, sun_producer)
        
        return entity
    
    def create_zombie(self, zombie_type: ZombieType, x: float, y: float,
                      row: int, 
                      speed_multiplier: float = 1.0,
                      health_multiplier: float = 1.0) -> Entity:
        """
        创建僵尸实体
        
        Args:
            zombie_type: 僵尸类型
            x: X坐标
            y: Y坐标
            row: 所在行
            speed_multiplier: 速度倍率
            health_multiplier: 生命值倍率
            
        Returns:
            创建的实体
        """
        entity = self.world.create_entity()
        config = ZOMBIE_CONFIGS.get(zombie_type, {})
        
        # 变换组件
        transform = TransformComponent(x=x, y=y)
        self.world.add_component(entity, transform)
        
        # 精灵组件
        sprite = SpriteComponent(
            color=config.get('color', (128, 128, 128)),
            width=config.get('width', 50),
            height=config.get('height', 80)
        )
        self.world.add_component(entity, sprite)
        
        # 动画组件
        anim_comp = AnimationComponent(
            current_state=AnimationState.WALK,
            default_state=AnimationState.WALK,
            z_index=30  # 僵尸层级（在植物之上）
        )
        
        # 添加动画
        walk_anim = self.sprite_manager.get_animation(f"zombie_{zombie_type.name}_walk")
        if walk_anim:
            anim_comp.add_animation(AnimationState.WALK, walk_anim)
        
        attack_anim = self.sprite_manager.get_animation(f"zombie_{zombie_type.name}_attack")
        if attack_anim:
            anim_comp.add_animation(AnimationState.ATTACK, attack_anim)
        
        # 僵尸面向左边（从右向左走）
        anim_comp.is_flipped_x = True
        
        self.world.add_component(entity, anim_comp)
        
        # 生命值组件（应用难度倍率）
        base_health = config.get('health', 100)
        scaled_health = int(base_health * health_multiplier)
        health = HealthComponent(
            current=scaled_health,
            max_health=scaled_health
        )
        self.world.add_component(entity, health)
        
        # 速度组件（应用难度倍率）
        base_speed = abs(config.get('speed', 30))
        scaled_speed = base_speed * speed_multiplier
        velocity = VelocityComponent(
            vx=-1.0,  # 向左移动
            vy=0.0,
            base_speed=scaled_speed
        )
        self.world.add_component(entity, velocity)
        
        # 碰撞组件
        collision = CollisionComponent(
            width=config.get('width', 50),
            height=config.get('height', 80),
            layer=CollisionSystem.LAYER_ZOMBIE,
            collides_with={CollisionSystem.LAYER_PLANT, CollisionSystem.LAYER_PROJECTILE}
        )
        self.world.add_component(entity, collision)
        
        # 网格位置组件
        grid_pos = GridPositionComponent(row=row, col=-1)
        self.world.add_component(entity, grid_pos)
        
        # 僵尸类型组件
        zombie_type_comp = ZombieTypeComponent(zombie_type=zombie_type)
        self.world.add_component(entity, zombie_type_comp)
        
        # 僵尸组件
        zombie = ZombieComponent(
            damage=config.get('damage', 20),
            score_value=config.get('score_value', 10),
            has_armor=config.get('has_armor', False),
            armor_health=config.get('armor_health', 0),
            has_pole=config.get('has_pole', False),
            is_flying=config.get('is_flying', False),
            is_pogoing=config.get('is_pogoing', False)
        )
        self.world.add_component(entity, zombie)
        
        return entity
    
    def create_projectile(self, projectile_type: ProjectileType, 
                          x: float, y: float, row: int) -> Entity:
        """
        创建投射物实体
        
        Args:
            projectile_type: 投射物类型
            x: X坐标
            y: Y坐标
            row: 所在行
            
        Returns:
            创建的实体
        """
        entity = self.world.create_entity()
        config = PROJECTILE_CONFIGS.get(projectile_type, {})
        
        # 变换组件
        transform = TransformComponent(x=x, y=y)
        self.world.add_component(entity, transform)
        
        # 精灵组件
        sprite = SpriteComponent(
            color=config.get('color', (0, 255, 0)),
            width=config.get('width', 15),
            height=config.get('height', 15)
        )
        self.world.add_component(entity, sprite)
        
        # 动画组件（用于旋转效果）
        anim_comp = AnimationComponent(
            current_state=AnimationState.IDLE,
            default_state=AnimationState.IDLE,
            z_index=40  # 投射物层级
        )
        self.world.add_component(entity, anim_comp)
        
        # 速度组件
        velocity = VelocityComponent(
            vx=1.0,  # 向右移动
            vy=0.0,
            base_speed=config.get('speed', 300.0)
        )
        self.world.add_component(entity, velocity)
        
        # 碰撞组件
        collision = CollisionComponent(
            width=config.get('width', 15),
            height=config.get('height', 15),
            layer=CollisionSystem.LAYER_PROJECTILE,
            collides_with={CollisionSystem.LAYER_ZOMBIE},
            is_trigger=True
        )
        self.world.add_component(entity, collision)
        
        # 网格位置组件
        grid_pos = GridPositionComponent(row=row, col=-1)
        self.world.add_component(entity, grid_pos)
        
        # 投射物类型组件
        projectile_type_comp = ProjectileTypeComponent(projectile_type=projectile_type)
        self.world.add_component(entity, projectile_type_comp)
        
        # 投射物组件
        projectile = ProjectileComponent(
            damage=config.get('damage', 20),
            speed=config.get('speed', 300.0),
            is_splash=config.get('is_splash', False),
            splash_radius=config.get('splash_radius', 50.0),
            applies_slow=config.get('applies_slow', False),
            slow_factor=config.get('slow_factor', 0.5),
            slow_duration=config.get('slow_duration', 3.0),
            lifetime=config.get('lifetime', 5.0)
        )
        self.world.add_component(entity, projectile)
        
        return entity
    
    def create_sun(self, x: float, y: float, amount: int = 25,
                   is_auto: bool = False) -> Entity:
        """
        创建阳光实体
        
        Args:
            x: X坐标
            y: Y坐标
            amount: 阳光数量
            is_auto: 是否自动产生
            
        Returns:
            创建的实体
        """
        entity = self.world.create_entity()
        
        # 变换组件
        transform = TransformComponent(x=x, y=y)
        self.world.add_component(entity, transform)
        
        # 精灵组件（黄色圆形）
        sprite = SpriteComponent(
            color=(255, 255, 0),
            width=40,
            height=40
        )
        self.world.add_component(entity, sprite)
        
        # 动画组件（闪烁效果）
        anim_comp = AnimationComponent(
            current_state=AnimationState.IDLE,
            default_state=AnimationState.IDLE,
            z_index=50  # 特效层级
        )
        
        # 创建闪烁动画
        frames = []
        for i in range(4):
            scale = 1.0 + 0.1 * (i if i < 2 else 4 - i)
            texture_name = f"sun_glow_{i}"
            texture = self.sprite_manager.create_colored_circle_texture(
                texture_name, int(20 * scale), (255, 255, 0)
            )
            frames.append(AnimationFrame(texture, 0.15))
        
        sun_anim = Animation("sun_idle", frames, loop=True)
        anim_comp.add_animation(AnimationState.IDLE, sun_anim)
        self.world.add_component(entity, anim_comp)
        
        # 碰撞组件
        collision = CollisionComponent(
            width=40,
            height=40,
            layer=CollisionSystem.LAYER_SUN,
            is_trigger=True
        )
        self.world.add_component(entity, collision)
        
        # 阳光生产组件
        sun_producer = SunProducerComponent(
            production_amount=amount,
            is_auto=is_auto,
            is_collectable=True
        )
        self.world.add_component(entity, sun_producer)
        
        # 速度组件（下落）
        if not is_auto:
            velocity = VelocityComponent(
                vx=0.0,
                vy=-1.0,
                base_speed=50.0
            )
            self.world.add_component(entity, velocity)
        
        return entity
