import pytest
from unittest.mock import MagicMock


class TestAnimation:
    """动画组件测试"""

    def test_animation_initialization(self):
        """测试动画初始化"""
        from src.systems.animation import Animation
        
        frames = [MagicMock() for _ in range(4)]
        animation = Animation(frames, frame_duration=0.1)
        
        assert animation.frames == frames
        assert animation.frame_duration == 0.1
        assert animation.current_frame == 0
        assert animation.is_playing == True

    def test_animation_update(self):
        """测试动画更新"""
        from src.systems.animation import Animation
        
        frames = [MagicMock() for _ in range(4)]
        animation = Animation(frames, frame_duration=0.1)
        
        animation.update(0.15)
        assert animation.current_frame == 1

    def test_animation_loop(self):
        """测试动画循环"""
        from src.systems.animation import Animation
        
        frames = [MagicMock() for _ in range(4)]
        animation = Animation(frames, frame_duration=0.1, loop=True)
        
        for _ in range(4):
            animation.update(0.1)
        
        assert animation.current_frame == 0

    def test_animation_no_loop(self):
        """测试动画不循环"""
        from src.systems.animation import Animation
        
        frames = [MagicMock() for _ in range(4)]
        animation = Animation(frames, frame_duration=0.1, loop=False)
        
        for _ in range(5):
            animation.update(0.1)
        
        assert animation.current_frame == 3
        assert animation.is_playing == False

    def test_animation_get_current_frame(self):
        """测试获取当前帧"""
        from src.systems.animation import Animation
        
        frames = [MagicMock() for _ in range(4)]
        animation = Animation(frames, frame_duration=0.1)
        
        frame = animation.get_current_frame()
        assert frame == frames[0]

    def test_animation_reset(self):
        """测试动画重置"""
        from src.systems.animation import Animation
        
        frames = [MagicMock() for _ in range(4)]
        animation = Animation(frames, frame_duration=0.1)
        
        animation.update(0.3)
        animation.reset()
        
        assert animation.current_frame == 0
        assert animation.timer == 0.0

    def test_animation_pause_resume(self):
        """测试动画暂停和恢复"""
        from src.systems.animation import Animation
        
        frames = [MagicMock() for _ in range(4)]
        animation = Animation(frames, frame_duration=0.1)
        
        animation.pause()
        assert animation.is_playing == False
        
        animation.update(0.2)
        assert animation.current_frame == 0
        
        animation.resume()
        assert animation.is_playing == True


class TestAnimationManager:
    """动画管理器测试"""

    def test_animation_manager_initialization(self):
        """测试动画管理器初始化"""
        from src.systems.animation import AnimationManager
        
        manager = AnimationManager()
        assert manager.animations == {}

    def test_animation_manager_add_animation(self):
        """测试添加动画"""
        from src.systems.animation import AnimationManager, Animation
        
        manager = AnimationManager()
        frames = [MagicMock() for _ in range(4)]
        animation = Animation(frames, frame_duration=0.1)
        
        manager.add_animation('idle', animation)
        assert 'idle' in manager.animations

    def test_animation_manager_play(self):
        """测试播放动画"""
        from src.systems.animation import AnimationManager, Animation
        
        manager = AnimationManager()
        frames = [MagicMock() for _ in range(4)]
        animation = Animation(frames, frame_duration=0.1)
        animation.pause()
        
        manager.add_animation('idle', animation)
        manager.play('idle')
        
        assert manager.animations['idle'].is_playing == True

    def test_animation_manager_stop(self):
        """测试停止动画"""
        from src.systems.animation import AnimationManager, Animation
        
        manager = AnimationManager()
        frames = [MagicMock() for _ in range(4)]
        animation = Animation(frames, frame_duration=0.1)
        
        manager.add_animation('idle', animation)
        manager.stop('idle')
        
        assert manager.animations['idle'].is_playing == False

    def test_animation_manager_update_all(self):
        """测试更新所有动画"""
        from src.systems.animation import AnimationManager, Animation
        
        manager = AnimationManager()
        frames = [MagicMock() for _ in range(4)]
        
        anim1 = Animation(frames, frame_duration=0.1)
        anim2 = Animation(frames, frame_duration=0.1)
        
        manager.add_animation('idle', anim1)
        manager.add_animation('walk', anim2)
        
        manager.update_all(0.15)
        
        assert anim1.current_frame == 1
        assert anim2.current_frame == 1
