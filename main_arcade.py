"""
植物大战僵尸 - Arcade ECS版本主入口

使用Arcade游戏引擎和ECS架构的实现
"""

import arcade
from src.arcade_game import GameWindow


def main():
    """游戏主入口"""
    window = GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()