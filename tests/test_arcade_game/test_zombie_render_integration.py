"""
测试僵尸渲染集成系统
"""

import pytest
from unittest.mock import MagicMock, Mock
from src.arcade_game.zombie_render_integration import (
    ZombieRenderIntegration, get_zombie_render_integration
)
from src.arcade_game.zombie_visual_system import DeathType
from src.arcade_game.zombie_effects import ZombieExpression


class TestZombieRenderIntegration:
    """测试僵尸渲染集成"""
    
    def test_integration_creation(self):
        """测试集成系统创建"""
        integration = ZombieRenderIntegration()
        assert integration is not None
        assert integration._time == 0.0
    
    def test_get_integration_singleton(self):
        """测试单例模式"""
        integration1 = get_zombie_render_integration()
        integration2 = get_zombie_render_integration()
        assert integration1 is integration2
    
    def test_trigger_hit(self):
        """测试触发受击效果"""
        integration = ZombieRenderIntegration()
        zombie_id = 1
        
        integration.trigger_hit(zombie_id, damage=20)
        
        # 验证受击效果已触发
        assert integration._visual_system.get_hit_flash_intensity(zombie_id) > 0
    
    def test_trigger_armor_break(self):
        """测试触发护甲破碎"""
        integration = ZombieRenderIntegration()
        zombie_id = 1
        
        integration.trigger_armor_break(zombie_id)
        
        state = integration._visual_system.get_or_create_state(zombie_id)
        assert state.armor_broken
    
    def test_detach_part(self):
        """测试部位脱落"""
        integration = ZombieRenderIntegration()
        zombie_id = 1
        
        integration.detach_part(zombie_id, 'left_arm')
        
        # 验证部位已脱落
        visual_state = integration._visual_system.get_or_create_state(zombie_id)
        assert not visual_state.has_left_arm
    
    def test_start_death_animation(self):
        """测试开始死亡动画"""
        integration = ZombieRenderIntegration()
        zombie_id = 1
        
        integration.start_death_animation(
            zombie_id, x=100, y=50, 
            zombie_type='normal', 
            death_type=DeathType.EXPLOSION
        )
        
        # 验证死亡动画已添加
        assert integration._visual_system.get_active_death_count() > 0
    
    def test_start_pole_vault(self):
        """测试开始撑杆跳跃"""
        integration = ZombieRenderIntegration()
        zombie_id = 1
        
        integration.start_pole_vault(zombie_id, 100, 200, 50)
        
        # 验证跳跃已开始
        assert integration._special_effects.is_pole_vaulting(zombie_id)
    
    def test_start_dancer_summon(self):
        """测试开始舞王召唤"""
        integration = ZombieRenderIntegration()
        zombie_id = 1
        
        integration.start_dancer_summon(zombie_id)
        
        # 验证召唤已开始
        assert integration._special_effects.is_dancer_summoning(zombie_id)
    
    def test_start_gargantuar_smash(self):
        """测试开始巨人砸地"""
        integration = ZombieRenderIntegration()
        zombie_id = 1
        
        integration.start_gargantuar_smash(zombie_id)
        
        # 验证砸地已开始
        assert integration._special_effects.is_gargantuar_smashing(zombie_id)
    
    def test_pop_balloon(self):
        """测试击破气球"""
        integration = ZombieRenderIntegration()
        zombie_id = 1
        
        integration.pop_balloon(zombie_id)
        
        # 验证表情已变为惊讶
        expr_state = integration._effects._get_or_create_expression(zombie_id)
        assert expr_state.current_expression == ZombieExpression.SURPRISED
    
    def test_remove_zombie(self):
        """测试移除僵尸"""
        integration = ZombieRenderIntegration()
        zombie_id = 1
        
        # 添加一些效果
        integration.trigger_hit(zombie_id)
        integration.detach_part(zombie_id, 'left_arm')
        
        # 移除僵尸
        integration.remove_zombie(zombie_id)
        
        # 验证状态已清除
        assert zombie_id not in integration._visual_system.zombie_states
        assert zombie_id not in integration._anim_renderer._states
    
    def test_clear(self):
        """测试清除所有效果"""
        integration = ZombieRenderIntegration()
        
        # 添加多个僵尸的效果
        for i in range(3):
            integration.trigger_hit(i)
        
        # 清除
        integration.clear()
        
        # 验证所有状态已清除
        assert len(integration._visual_system.zombie_states) == 0
        assert len(integration._anim_renderer._states) == 0
        assert integration._time == 0.0


class TestIntegrationWithMockComponents:
    """使用Mock组件测试集成"""
    
    def test_update_with_mock_components(self):
        """测试使用Mock组件更新"""
        integration = ZombieRenderIntegration()
        
        # 创建Mock组件管理器
        mock_manager = MagicMock()
        
        # 创建Mock僵尸实体
        mock_transform = MagicMock()
        mock_transform.x = 100
        mock_transform.y = 50
        
        mock_zombie = MagicMock()
        mock_zombie.is_attacking = False
        
        mock_sprite = MagicMock()
        mock_sprite.color = (128, 128, 128)
        mock_sprite.width = 50
        mock_sprite.height = 80
        
        mock_anim = MagicMock()
        mock_anim.is_flipped_x = True
        
        # 设置Mock返回值
        mock_manager.query.return_value = [1]
        mock_manager.get_component.side_effect = lambda eid, comp_type: {
            'TransformComponent': mock_transform,
            'ZombieComponent': mock_zombie,
            'SpriteComponent': mock_sprite,
            'AnimationComponent': mock_anim,
            'ZombieTypeComponent': None,
        }.get(comp_type.__name__, None)
        
        # 执行更新（不应抛出异常）
        try:
            integration.update(0.1, mock_manager)
        except Exception as e:
            pytest.fail(f"更新不应抛出异常: {e}")


class TestEventTriggers:
    """测试事件触发"""
    
    def test_hit_triggers_expression_change(self):
        """测试受击触发表情变化"""
        integration = ZombieRenderIntegration()
        zombie_id = 1
        
        integration.trigger_hit(zombie_id, damage=10)
        
        # 验证表情已变为痛苦
        expr_state = integration._effects._get_or_create_expression(zombie_id)
        assert expr_state.current_expression == ZombieExpression.PAIN
    
    def test_pole_vault_triggers_determined_expression(self):
        """测试撑杆跳跃触发坚定表情"""
        integration = ZombieRenderIntegration()
        zombie_id = 1
        
        integration.start_pole_vault(zombie_id, 100, 200, 50)
        
        # 验证表情已变为坚定
        expr_state = integration._effects._get_or_create_expression(zombie_id)
        assert expr_state.current_expression == ZombieExpression.DETERMINED


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
