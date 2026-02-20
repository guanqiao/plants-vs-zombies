"""
主题色彩系统 - Material Design 风格的游戏配色

提供统一的色彩管理，支持亮色/暗色主题
"""

from dataclasses import dataclass
from typing import Tuple, Dict


@dataclass(frozen=True)
class Color:
    """颜色定义"""
    r: int
    g: int
    b: int
    a: int = 255
    
    @property
    def rgba(self) -> Tuple[int, int, int, int]:
        """获取RGBA元组"""
        return (self.r, self.g, self.b, self.a)
    
    @property
    def rgb(self) -> Tuple[int, int, int]:
        """获取RGB元组"""
        return (self.r, self.g, self.b)
    
    def with_alpha(self, alpha: int) -> "Color":
        """创建带有指定透明度的颜色副本"""
        return Color(self.r, self.g, self.b, alpha)
    
    def lighten(self, amount: float = 0.2) -> "Color":
        """变亮"""
        return Color(
            min(255, int(self.r + (255 - self.r) * amount)),
            min(255, int(self.g + (255 - self.g) * amount)),
            min(255, int(self.b + (255 - self.b) * amount)),
            self.a
        )
    
    def darken(self, amount: float = 0.2) -> "Color":
        """变暗"""
        return Color(
            max(0, int(self.r * (1 - amount))),
            max(0, int(self.g * (1 - amount))),
            max(0, int(self.b * (1 - amount))),
            self.a
        )


# ==================== Material Design 基础色板 ====================

# 主色调 - 绿色系（草地主题）
PRIMARY = Color(76, 175, 80)          # Material Green 500
PRIMARY_LIGHT = Color(129, 199, 132)  # Material Green 300
PRIMARY_DARK = Color(46, 125, 50)     # Material Green 700

# 辅助色 - 橙黄色系（阳光主题）
SECONDARY = Color(255, 193, 7)        # Material Amber 500
SECONDARY_LIGHT = Color(255, 224, 130) # Material Amber 200
SECONDARY_DARK = Color(255, 160, 0)   # Material Amber 700

# 强调色
ACCENT = Color(255, 87, 34)           # Material Deep Orange 500
ACCENT_LIGHT = Color(255, 138, 101)   # Material Deep Orange 300

# ==================== UI 专用颜色 ====================

class UIColors:
    """UI颜色集合"""
    
    # 背景色
    BG_DARK = Color(30, 30, 30)
    BG_MEDIUM = Color(45, 45, 45)
    BG_LIGHT = Color(60, 60, 60)
    BG_TRANSPARENT = Color(30, 30, 30, 180)
    
    # 表面色
    SURFACE = Color(50, 50, 50)
    SURFACE_ELEVATED = Color(66, 66, 66)
    
    # 边框色
    BORDER = Color(100, 100, 100)
    BORDER_HIGHLIGHT = Color(150, 150, 150)
    BORDER_SELECTED = Color(255, 220, 100)
    
    # 文字色
    TEXT_PRIMARY = Color(255, 255, 255)
    TEXT_SECONDARY = Color(200, 200, 200)
    TEXT_DISABLED = Color(150, 150, 150)
    TEXT_HINT = Color(120, 120, 120)


# ==================== 游戏专用颜色 ====================

class GameColors:
    """游戏元素颜色"""
    
    # 阳光系统
    SUN_CORE = Color(255, 235, 59)      # 亮黄核心
    SUN_GLOW = Color(255, 193, 7)       # 金色光晕
    SUN_RAY = Color(255, 248, 225)      # 光芒
    SUN_TEXT = Color(255, 241, 118)     # 阳光文字
    
    # 草地系统
    GRASS_LIGHT = Color(124, 179, 66)   # 浅草地
    GRASS_DARK = Color(104, 159, 56)    # 深草地
    GRASS_BORDER = Color(85, 139, 47)   # 草地边缘
    DIRT = Color(121, 85, 72)           # 土壤
    
    # 植物颜色
    PLANT_PEASHOOTER = Color(76, 175, 80)
    PLANT_SUNFLOWER = Color(255, 193, 7)
    PLANT_WALLNUT = Color(141, 110, 99)
    PLANT_CHERRY = Color(244, 67, 54)
    PLANT_SNOWPEA = Color(100, 181, 246)
    PLANT_REPEATER = Color(67, 160, 71)
    PLANT_CHOMPER = Color(156, 39, 176)
    PLANT_POTATO = Color(161, 136, 127)
    
    # 僵尸颜色
    ZOMBIE_SKIN = Color(129, 199, 132)
    ZOMBIE_SHIRT = Color(96, 125, 139)
    ZOMBIE_TIE = Color(183, 28, 28)
    
    # 投射物
    PEA_NORMAL = Color(76, 175, 80)
    PEA_FROZEN = Color(100, 181, 246)
    PEA_FIRE = Color(255, 87, 34)


# ==================== 状态颜色 ====================

class StatusColors:
    """状态指示颜色"""
    
    # 生命值
    HEALTH_HIGH = Color(76, 175, 80)    # 绿色 - 健康
    HEALTH_MEDIUM = Color(255, 193, 7)  # 黄色 - 警告
    HEALTH_LOW = Color(244, 67, 54)     # 红色 - 危险
    
    # 游戏状态
    SUCCESS = Color(76, 175, 80)        # 成功
    WARNING = Color(255, 152, 0)        # 警告
    ERROR = Color(244, 67, 54)          # 错误
    INFO = Color(33, 150, 243)          # 信息
    
    # 波次状态
    WAVE_NORMAL = Color(255, 255, 255)
    WAVE_WARNING = Color(255, 87, 34)
    WAVE_DANGER = Color(244, 67, 54)
    WAVE_PROGRESS = Color(76, 175, 80)


# ==================== 特效颜色 ====================

class EffectColors:
    """特效颜色"""
    
    # 爆炸
    EXPLOSION_CORE = Color(255, 87, 34)
    EXPLOSION_OUTER = Color(255, 152, 0)
    EXPLOSION_SMOKE = Color(97, 97, 97)
    
    # 冰冻
    ICE_CORE = Color(187, 222, 251)
    ICE_OUTER = Color(100, 181, 246)
    ICE_SPARKLE = Color(255, 255, 255)
    
    # 火焰
    FIRE_CORE = Color(255, 87, 34)
    FIRE_MIDDLE = Color(255, 152, 0)
    FIRE_OUTER = Color(255, 235, 59)
    
    # 收集
    COLLECT_GOLD = Color(255, 215, 0)
    COLLECT_SPARKLE = Color(255, 255, 200)


# ==================== 渐变定义 ====================

def get_gradient_colors(start: Color, end: Color, steps: int) -> list:
    """
    生成渐变颜色列表
    
    Args:
        start: 起始颜色
        end: 结束颜色
        steps: 渐变步数
        
    Returns:
        颜色列表
    """
    colors = []
    for i in range(steps):
        t = i / (steps - 1) if steps > 1 else 0
        r = int(start.r + (end.r - start.r) * t)
        g = int(start.g + (end.g - start.g) * t)
        b = int(start.b + (end.b - start.b) * t)
        a = int(start.a + (end.a - start.a) * t)
        colors.append(Color(r, g, b, a))
    return colors


# 预定义渐变
GRADIENT_HEALTH = get_gradient_colors(StatusColors.HEALTH_LOW, StatusColors.HEALTH_HIGH, 10)
GRADIENT_SUN = get_gradient_colors(GameColors.SUN_GLOW, GameColors.SUN_CORE, 5)
GRADIENT_GRASS = get_gradient_colors(GameColors.GRASS_DARK, GameColors.GRASS_LIGHT, 5)


# ==================== 导出便捷访问 ====================

# 便捷函数
def hex_to_color(hex_str: str, alpha: int = 255) -> Color:
    """从十六进制字符串创建颜色"""
    hex_str = hex_str.lstrip('#')
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return Color(r, g, b, alpha)


# 常用颜色快捷访问
WHITE = Color(255, 255, 255)
BLACK = Color(0, 0, 0)
TRANSPARENT = Color(0, 0, 0, 0)

# 导出所有颜色类
__all__ = [
    'Color',
    'PRIMARY', 'PRIMARY_LIGHT', 'PRIMARY_DARK',
    'SECONDARY', 'SECONDARY_LIGHT', 'SECONDARY_DARK',
    'ACCENT', 'ACCENT_LIGHT',
    'UIColors',
    'GameColors',
    'StatusColors',
    'EffectColors',
    'get_gradient_colors',
    'GRADIENT_HEALTH', 'GRADIENT_SUN', 'GRADIENT_GRASS',
    'hex_to_color',
    'WHITE', 'BLACK', 'TRANSPARENT',
]
