# ECS架构下，系统由System类统一管理
# 具体系统实现在ecs/systems/目录下
from src.ecs.system import System

__all__ = ['System']
