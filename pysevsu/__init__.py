"""Библиотека предоставляет поток расписания из публичного источника
Севастопольского государственного университета. Система обеспечивает высокую
производительность, возможность регулировки параметров для контроля памяти и
нагрузки, механизмы ранней и поздней фильтрации.

Рекомендуемые импорты: 
:class:`CreatePipeline`,
:class:`ScheduleExcelParser`, 
:class:`ScheduleWebsiteParser`.
"""

from .factory import Pipeline as create_pipeline
from .sources.excel import File as ScheduleExcelParser
from .sources.website import Structure as ScheduleWebsiteParser

__all__ = ["create_pipeline", "ScheduleExcelParser", "ScheduleWebsiteParser"]
