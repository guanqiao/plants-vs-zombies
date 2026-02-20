"""
植物大战僵尸 - Arcade ECS版本主入口

使用Arcade游戏引擎和ECS架构的实现
"""

import arcade
from src.core.logger import get_logger
from src.arcade_game import GameWindow


def main():
    """游戏主入口"""
    # 初始化日志系统
    logger = get_logger()
    logger.setup(logs_dir="logs")
    logger.setup_exception_hook()
    
    logger.info("=" * 50)
    logger.info("游戏启动")
    logger.info("=" * 50)
    
    try:
        window = GameWindow()
        arcade.run()
    except Exception as e:
        logger.critical(f"游戏运行时发生致命错误: {e}")
        raise
    finally:
        logger.info("=" * 50)
        logger.info("游戏结束")
        logger.info("=" * 50)


if __name__ == "__main__":
    main()
