#!/usr/bin/env python3
"""
测试生成的资源是否可以正常加载
"""

import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_image_loading():
    """测试图片资源加载"""
    print("=" * 50)
    print("测试图片资源加载")
    print("=" * 50)
    
    assets_dir = Path(__file__).parent.parent / 'assets' / 'images'
    
    # 测试所有生成的图片
    test_images = [
        'plants/peashooter.png',
        'plants/peashooter_shoot.png',
        'plants/sunflower.png',
        'plants/wallnut.png',
        'zombies/zombie_normal.png',
        'projectiles/pea.png',
        'projectiles/frozen_pea.png',
        'ui/card_slot.png',
        'ui/sun_icon.png',
        'backgrounds/grass_tile.png',
        'backgrounds/lawn_day.png',
    ]
    
    all_passed = True
    for img_path in test_images:
        full_path = assets_dir / img_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✓ {img_path} ({size} bytes)")
        else:
            print(f"✗ {img_path} - 不存在!")
            all_passed = False
    
    return all_passed


def test_arcade_loading():
    """测试Arcade库加载"""
    print("\n" + "=" * 50)
    print("测试Arcade库加载")
    print("=" * 50)
    
    try:
        import arcade
        print("✓ Arcade库已安装")
        
        assets_dir = Path(__file__).parent.parent / 'assets' / 'images'
        
        # 测试加载几个关键资源
        test_files = [
            'plants/peashooter.png',
            'zombies/zombie_normal.png',
            'projectiles/pea.png',
        ]
        
        for file_path in test_files:
            full_path = assets_dir / file_path
            try:
                texture = arcade.load_texture(str(full_path))
                print(f"✓ {file_path} - 加载成功 ({texture.width}x{texture.height})")
            except Exception as e:
                print(f"✗ {file_path} - 加载失败: {e}")
                return False
        
        return True
    except ImportError:
        print("✗ Arcade库未安装")
        return False


def test_entity_factory():
    """测试实体工厂初始化"""
    print("\n" + "=" * 50)
    print("测试实体工厂初始化")
    print("=" * 50)
    
    try:
        import arcade
        from arcade_game.entity_factory import EntityFactory
        from ecs import World
        
        # 初始化Arcade（需要窗口，但我们可以测试导入）
        print("✓ 模块导入成功")
        
        # 检查资源映射配置
        from arcade_game.entity_factory import PlantType, ZombieType, ProjectileType
        
        print(f"✓ 植物类型数量: {len(list(PlantType))}")
        print(f"✓ 僵尸类型数量: {len(list(ZombieType))}")
        print(f"✓ 投射物类型数量: {len(list(ProjectileType))}")
        
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "=" * 50)
    print("植物大战僵尸美术资源测试")
    print("=" * 50 + "\n")
    
    results = []
    
    # 测试1: 图片文件存在性
    results.append(("图片文件存在性", test_image_loading()))
    
    # 测试2: Arcade加载
    results.append(("Arcade库加载", test_arcade_loading()))
    
    # 测试3: 实体工厂
    results.append(("实体工厂初始化", test_entity_factory()))
    
    # 汇总
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "=" * 50)
    if all_passed:
        print("所有测试通过！资源已准备就绪。")
    else:
        print("部分测试失败，请检查错误信息。")
    print("=" * 50)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
