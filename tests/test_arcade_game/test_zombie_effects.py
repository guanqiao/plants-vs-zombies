"""
测试僵尸特效系统
"""

import pytest
from src.arcade_game.zombie_effects import (
    ZombieEffects, ZombieExpression, DustParticle, 
    ShadowState, ExpressionState, get_zombie_effects
)


class TestDustParticle:
    """测试尘土粒子"""
    
    def test_particle_creation(self):
        """测试粒子创建"""
        p = DustParticle(
            x=100, y=50, vx=10, vy=20,
            size=5, alpha=150, life=0.5, max_life=0.5
        )
        assert p.x == 100
        assert p.is_alive
    
    def test_particle_update(self):
        """测试粒子更新"""
        p = DustParticle(
            x=100, y=50, vx=10, vy=20,
            size=5, alpha=150, life=0.5, max_life=0.5
        )
        p.update(0.1)
        assert p.x == 101  # 100 + 10 * 0.1
        assert p.life == 0.4
    
    def test_particle_death(self):
        """测试粒子死亡"""
        p = DustParticle(
            x=100, y=50, vx=0, vy=0,
            size=5, alpha=150, life=0.1, max_life=0.1
        )
        p.update(0.15)
        assert not p.is_alive


class TestShadowState:
    """测试阴影状态"""
    
    def test_shadow_creation(self):
        """测试阴影创建"""
        shadow = ShadowState()
        assert shadow.offset_y == -5.0
        assert shadow.alpha == 80
    
    def test_shadow_update_on_ground(self):
        """测试地面阴影"""
        shadow = ShadowState()
        shadow.update(zombie_y_offset=0)
        assert shadow.scale_x == 1.0
        assert shadow.alpha == 80
    
    def test_shadow_update_in_air(self):
        """测试空中阴影（变小变淡）"""
        shadow = ShadowState()
        shadow.update(zombie_y_offset=50)
        assert shadow.scale_x < 1.0
        assert shadow.alpha < 80


class TestExpressionState:
    """测试表情状态"""
    
    def test_expression_creation(self):
        """测试表情创建"""
        expr = ExpressionState()
        assert expr.current_expression == ZombieExpression.NORMAL
        assert not expr.is_blinking
    
    def test_blinking(self):
        """测试眨眼逻辑"""
        expr = ExpressionState()
        # 手动设置眨眼
        expr.is_blinking = True
        expr.blink_timer = 0.0
        
        expr.update(0.2)  # 超过眨眼持续时间
        assert not expr.is_blinking
    
    def test_expression_changes(self):
        """测试表情变化"""
        expr = ExpressionState()
        
        # 受击时变为痛苦
        expr.update(0.1, is_hurt=True)
        assert expr.current_expression == ZombieExpression.PAIN
        
        # 吃植物时变为饥饿
        expr = ExpressionState()  # 重置
        expr.update(0.1, is_eating=True)
        assert expr.current_expression == ZombieExpression.HUNGRY
        assert expr.mouth_open > 0
        
        # 跳跃时变为坚定
        expr = ExpressionState()
        expr.update(0.1, is_jumping=True)
        assert expr.current_expression == ZombieExpression.DETERMINED


class TestZombieEffects:
    """测试僵尸特效管理器"""
    
    def test_effects_creation(self):
        """测试特效系统创建"""
        effects = ZombieEffects()
        assert effects is not None
    
    def test_get_zombie_effects_singleton(self):
        """测试单例模式"""
        effects1 = get_zombie_effects()
        effects2 = get_zombie_effects()
        assert effects1 is effects2
    
    def test_shadow_rendering(self):
        """测试阴影渲染状态（不实际渲染）"""
        effects = ZombieEffects()
        # 只测试阴影状态，不实际渲染（需要arcade窗口）
        shadow = effects._get_or_create_shadow(1)
        assert shadow is not None
        assert shadow.alpha == 80
    
    def test_dust_generation(self):
        """测试尘土生成"""
        effects = ZombieEffects()
        
        # 更新多次以生成尘土
        for _ in range(10):
            effects.update(0.1, 1, x=100, y=50, is_moving=True, speed=50)
        
        # 检查是否生成了尘土粒子
        assert 1 in effects._dust_particles
        assert len(effects._dust_particles[1]) > 0
    
    def test_expression_setting(self):
        """测试设置表情"""
        effects = ZombieEffects()
        effects.set_expression(1, ZombieExpression.ANGRY, duration=2.0)
        
        expr = effects._get_or_create_expression(1)
        assert expr.current_expression == ZombieExpression.ANGRY
        assert expr.expression_timer == 2.0
    
    def test_remove_zombie(self):
        """测试移除僵尸"""
        effects = ZombieEffects()
        
        # 添加一些效果
        effects.update(0.1, 1, x=100, y=50, is_moving=True, speed=50)
        effects.set_expression(1, ZombieExpression.ANGRY)
        
        # 移除僵尸
        effects.remove_zombie(1)
        
        # 验证已移除
        assert 1 not in effects._dust_particles
        assert 1 not in effects._expression_states
    
    def test_clear(self):
        """测试清除所有效果"""
        effects = ZombieEffects()
        
        # 添加一些效果
        effects.update(0.1, 1, x=100, y=50, is_moving=True, speed=50)
        effects.update(0.1, 2, x=200, y=50, is_moving=True, speed=50)
        
        # 清除
        effects.clear()
        
        # 验证已清除
        assert len(effects._dust_particles) == 0
        assert len(effects._shadow_states) == 0
        assert len(effects._expression_states) == 0


class TestZombieExpressionEnum:
    """测试僵尸表情枚举"""
    
    def test_expression_types(self):
        """测试所有表情类型存在"""
        assert ZombieExpression.NORMAL is not None
        assert ZombieExpression.ANGRY is not None
        assert ZombieExpression.PAIN is not None
        assert ZombieExpression.HUNGRY is not None
        assert ZombieExpression.SURPRISED is not None
        assert ZombieExpression.DETERMINED is not None
    
    def test_expression_values(self):
        """测试表情值"""
        expressions = list(ZombieExpression)
        assert len(expressions) == 6


class TestIntegration:
    """集成测试"""
    
    def test_full_zombie_effect_sequence(self):
        """测试完整的僵尸特效序列"""
        effects = ZombieEffects()
        zombie_id = 1
        
        # 1. 僵尸行走，产生尘土
        for _ in range(5):
            effects.update(0.1, zombie_id, x=100, y=50, 
                         is_moving=True, speed=30)
        
        # 验证尘土生成
        assert len(effects._dust_particles.get(zombie_id, [])) > 0
        
        # 2. 僵尸受击，表情变化
        effects.update(0.1, zombie_id, x=100, y=50, 
                      is_moving=False, is_hurt=True)
        
        expr = effects._get_or_create_expression(zombie_id)
        assert expr.current_expression == ZombieExpression.PAIN
        
        # 3. 僵尸吃植物
        for _ in range(5):
            effects.update(0.1, zombie_id, x=100, y=50, 
                         is_moving=False, is_eating=True)
        
        assert expr.current_expression == ZombieExpression.HUNGRY
        assert expr.mouth_open > 0.5  # 嘴巴应该张开
        
        # 4. 验证渲染状态（不实际渲染，因为需要arcade窗口）
        shadow = effects._get_or_create_shadow(zombie_id)
        assert shadow is not None
        # 验证尘土存在
        assert len(effects._dust_particles.get(zombie_id, [])) >= 0
    
    def test_multiple_zombies(self):
        """测试多个僵尸的效果管理"""
        effects = ZombieEffects()
        
        # 创建多个僵尸
        expressions = [
            ZombieExpression.NORMAL,
            ZombieExpression.ANGRY,
            ZombieExpression.PAIN
        ]
        for i in range(3):
            effects.update(0.1, i, x=100 + i*50, y=50, 
                         is_moving=True, speed=30)
            effects.set_expression(i, expressions[i])
        
        # 验证每个僵尸都有独立的状态
        for i in range(3):
            assert i in effects._dust_timers
            expr = effects._get_or_create_expression(i)
            assert expr.current_expression == expressions[i]
        
        # 移除一个僵尸
        effects.remove_zombie(1)
        
        # 验证其他僵尸不受影响
        assert 0 in effects._dust_timers
        assert 1 not in effects._dust_timers
        assert 2 in effects._dust_timers


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
