"""
测试僵尸动画系统
"""

import pytest
import arcade
from src.arcade_game.zombie_animation_renderer import (
    ZombieAnimationRenderer, ZombieBodyPart, ProceduralAnimationState
)
from src.arcade_game.zombie_visual_system import (
    ZombieVisualSystem, ZombieVisualState, DeathType
)
from src.arcade_game.special_zombie_effects import (
    SpecialZombieEffects, PoleVaultState, BalloonFloatState
)


class TestZombieAnimationRenderer:
    """测试僵尸动画渲染器"""
    
    def test_renderer_creation(self):
        """测试渲染器创建"""
        renderer = ZombieAnimationRenderer()
        assert renderer is not None
    
    def test_animation_state_creation(self):
        """测试动画状态创建"""
        state = ProceduralAnimationState()
        assert state.walk_cycle_time == 0.0
        assert state.body_offset_y == 0.0
        assert len(state.parts) == 6  # 6个身体部位
    
    def test_body_part_enum(self):
        """测试身体部位枚举"""
        assert ZombieBodyPart.HEAD is not None
        assert ZombieBodyPart.BODY is not None
        assert ZombieBodyPart.ARM_LEFT is not None
        assert ZombieBodyPart.ARM_RIGHT is not None
    
    def test_update_walking(self):
        """测试行走动画更新"""
        renderer = ZombieAnimationRenderer()
        renderer.update(0.1, 1, is_moving=True, is_attacking=False, is_hurt=False)
        
        state = renderer._get_or_create_state(1)
        assert state.walk_cycle_time > 0
    
    def test_detach_part(self):
        """测试部位脱落"""
        renderer = ZombieAnimationRenderer()
        renderer.detach_part(1, ZombieBodyPart.ARM_LEFT)
        
        state = renderer._get_or_create_state(1)
        assert not state.parts[ZombieBodyPart.ARM_LEFT].attached
    
    def test_reset(self):
        """测试重置状态"""
        renderer = ZombieAnimationRenderer()
        renderer.update(0.1, 1, is_moving=True)
        renderer.reset(1)
        
        assert 1 not in renderer._states


class TestZombieVisualSystem:
    """测试僵尸视觉效果系统"""
    
    def test_visual_system_creation(self):
        """测试视觉效果系统创建"""
        system = ZombieVisualSystem()
        assert system is not None
    
    def test_trigger_hit(self):
        """测试触发受击效果"""
        system = ZombieVisualSystem()
        system.trigger_hit(1, damage=20)
        
        state = system.get_or_create_state(1)
        assert state.hit_flash == 1.0
        assert state.hit_pulse == 1.0
        assert len(state.blood_particles) > 0
    
    def test_trigger_armor_break(self):
        """测试触发护甲破碎"""
        system = ZombieVisualSystem()
        system.trigger_armor_break(1)
        
        state = system.get_or_create_state(1)
        assert state.armor_broken
        assert state.armor_flying
    
    def test_detach_part(self):
        """测试部位脱落"""
        system = ZombieVisualSystem()
        system.detach_part(1, 'left_arm')
        
        state = system.get_or_create_state(1)
        assert not state.has_left_arm
    
    def test_death_types(self):
        """测试死亡类型"""
        assert DeathType.NORMAL is not None
        assert DeathType.EXPLOSION is not None
        assert DeathType.FROZEN is not None
        assert DeathType.ELECTRIC is not None
        assert DeathType.BURNED is not None
    
    def test_apply_hit_flash_to_color(self):
        """测试受击闪烁应用到颜色"""
        system = ZombieVisualSystem()
        system.trigger_hit(1)
        
        base_color = (128, 128, 128)
        result_color = system.apply_hit_flash_to_color(1, base_color)
        
        # 受击后颜色应该更亮（向白色靠近）
        assert result_color[0] >= base_color[0]
        assert result_color[1] >= base_color[1]
        assert result_color[2] >= base_color[2]


class TestSpecialZombieEffects:
    """测试特殊僵尸效果"""
    
    def test_effects_creation(self):
        """测试效果系统创建"""
        effects = SpecialZombieEffects()
        assert effects is not None
    
    def test_pole_vault_state(self):
        """测试撑杆跳跃状态"""
        state = PoleVaultState()
        assert not state.is_jumping
        
        state.start_jump(100, 200, 50)
        assert state.is_jumping
        
        x, y, completed = state.update(0.1)
        assert not completed
        assert x > 100  # 应该向前移动
    
    def test_balloon_float(self):
        """测试气球漂浮"""
        state = BalloonFloatState()
        offset = state.update(0.1, 0.0)
        assert -10 <= offset <= 10  # 漂浮范围
    
    def test_balloon_pop(self):
        """测试气球破裂"""
        state = BalloonFloatState()
        state.pop_balloon()
        assert state.balloon_popped
    
    def test_special_effects_manager(self):
        """测试特殊效果管理器"""
        effects = SpecialZombieEffects()
        
        # 测试撑杆跳跃
        effects.start_pole_vault(1, 100, 200, 50)
        assert effects.is_pole_vaulting(1)
        
        # 测试舞王召唤
        effects.start_dancer_summon(2)
        assert effects.is_dancer_summoning(2)
        
        # 测试巨人砸地
        effects.start_gargantuar_smash(3)
        assert effects.is_gargantuar_smashing(3)
    
    def test_remove_zombie(self):
        """测试移除僵尸效果"""
        effects = SpecialZombieEffects()
        effects.start_pole_vault(1, 100, 200, 50)
        effects.remove_zombie(1)
        
        assert not effects.is_pole_vaulting(1)


class TestIntegration:
    """集成测试"""
    
    def test_full_hit_sequence(self):
        """测试完整的受击序列"""
        # 创建所有系统
        anim_renderer = ZombieAnimationRenderer()
        visual_system = ZombieVisualSystem()
        
        zombie_id = 1
        
        # 触发受击
        visual_system.trigger_hit(zombie_id, damage=30)
        
        # 更新动画
        for _ in range(10):
            anim_renderer.update(0.05, zombie_id, is_moving=True, is_attacking=False, is_hurt=True)
            visual_system.update(0.05)
        
        # 验证状态
        state = visual_system.get_or_create_state(zombie_id)
        assert state.hit_flash < 1.0  # 闪烁应该衰减
        
        # 验证动画状态
        anim_state = anim_renderer._get_or_create_state(zombie_id)
        assert anim_state.walk_cycle_time > 0
    
    def test_part_detachment_sequence(self):
        """测试部位脱落序列"""
        anim_renderer = ZombieAnimationRenderer()
        visual_system = ZombieVisualSystem()
        
        zombie_id = 1
        
        # 脱落左臂
        visual_system.detach_part(zombie_id, 'left_arm')
        anim_renderer.detach_part(zombie_id, ZombieBodyPart.ARM_LEFT)
        
        # 验证状态
        visual_state = visual_system.get_or_create_state(zombie_id)
        assert not visual_state.has_left_arm
        
        anim_state = anim_renderer._get_or_create_state(zombie_id)
        assert not anim_state.parts[ZombieBodyPart.ARM_LEFT].attached


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
