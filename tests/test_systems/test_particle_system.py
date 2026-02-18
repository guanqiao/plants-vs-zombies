import pytest
from unittest.mock import MagicMock


class TestParticle:
    """粒子测试"""

    def test_particle_initialization(self):
        """测试粒子初始化"""
        from src.systems.particle_system import Particle
        
        particle = Particle(100, 200, (255, 0, 0))
        
        assert particle.x == 100
        assert particle.y == 200
        assert particle.color == (255, 0, 0)
        assert particle.is_alive == True

    def test_particle_update(self):
        """测试粒子更新"""
        from src.systems.particle_system import Particle
        
        particle = Particle(100, 200, (255, 0, 0), velocity=(10, -5), lifetime=2.0)
        
        particle.update(1.0)
        
        assert particle.x == 110
        assert particle.y == 195

    def test_particle_lifetime(self):
        """测试粒子生命周期"""
        from src.systems.particle_system import Particle
        
        particle = Particle(100, 200, (255, 0, 0), lifetime=1.0)
        
        particle.update(0.5)
        assert particle.is_alive == True
        
        particle.update(0.6)
        assert particle.is_alive == False

    def test_particle_gravity(self):
        """测试粒子重力"""
        from src.systems.particle_system import Particle
        
        particle = Particle(100, 200, (255, 0, 0), velocity=(0, 0), gravity=100, lifetime=2.0)
        
        particle.update(1.0)
        
        assert particle.vy == 100

    def test_particle_fade(self):
        """测试粒子淡出"""
        from src.systems.particle_system import Particle
        
        particle = Particle(100, 200, (255, 0, 0), lifetime=1.0, fade=True)
        
        particle.update(0.5)
        
        assert particle.alpha < 255


class TestParticleSystem:
    """粒子系统测试"""

    def test_particle_system_initialization(self):
        """测试粒子系统初始化"""
        from src.systems.particle_system import ParticleSystem
        
        system = ParticleSystem()
        assert len(system.particles) == 0

    def test_particle_system_emit(self):
        """测试发射粒子"""
        from src.systems.particle_system import ParticleSystem
        
        system = ParticleSystem()
        system.emit(100, 200, (255, 0, 0), count=5)
        
        assert len(system.particles) == 5

    def test_particle_system_update(self):
        """测试更新粒子系统"""
        from src.systems.particle_system import ParticleSystem
        
        system = ParticleSystem()
        system.emit(100, 200, (255, 0, 0), count=3, lifetime=0.1)
        
        system.update(0.2)
        
        assert len(system.particles) == 0

    def test_particle_system_explosion_effect(self):
        """测试爆炸效果"""
        from src.systems.particle_system import ParticleSystem
        
        system = ParticleSystem()
        system.create_explosion(300, 300)
        
        assert len(system.particles) > 0

    def test_particle_system_sun_collect_effect(self):
        """测试阳光收集效果"""
        from src.systems.particle_system import ParticleSystem
        
        system = ParticleSystem()
        system.create_sun_collect(100, 200)
        
        assert len(system.particles) > 0

    def test_particle_system_clear(self):
        """测试清除粒子"""
        from src.systems.particle_system import ParticleSystem
        
        system = ParticleSystem()
        system.emit(100, 200, (255, 0, 0), count=10)
        
        system.clear()
        
        assert len(system.particles) == 0
