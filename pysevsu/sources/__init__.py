"""Отвечает за парсинг и создание потока информации из HTML-структуры сайта
(URL-адресов с контекстом) и файлов электронных таблиц Excel (занятий
расписания). Определяющим требованием к реализации выступает наличие
механизмов фильтрации, за счет которых движок обеспечивает повышение
производительности на пользовательской выборке.

Рекомендуемые импорты:
:class:`ExcelFileIterator`
:class:`WebsiteStructureIterator`.
"""

from .excel import File as ExcelFileIterator
from .website import Structure as WebsiteStructureIterator

__all__ = [
    "ExcelFileIterator",
    "WebsiteStructureIterator",
]
