"""Форматирует и преобразует исходные материалы из источников в Python-объекты,
используя схему данных из schemas как правила для трансформации.
"""

from .transformer import create as create_objects

__all__ = ["create_objects"]
