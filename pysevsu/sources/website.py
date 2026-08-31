"""Модуль синтаксического анализа HTML-содержимого раздела расписания СевГУ.

Предоставляет класс :class:`Structure` для потоковой обработки веб-страницы,
извлечения ссылок на файлы документов и сопоставления их с метаданными.
"""

from enum import StrEnum
from typing import Any
from typing import Iterator
from lxml.html import fromstring
from pysevsu.core import WebsiteIterator
from ..models.raw import WebsiteDataKey as DataKey


class _HTML(StrEnum):
    """Сайт имеет иерархическое устройство: таблица с формами обучения содержит
    три колонки и включает блоки с институтами, где расположены Excel файлы
    разделенные названиями семестров.
    """

    STUDY_FORM = "schedule-table__column-name"
    INSTITUTE = "h4"
    SEMESTER = "document-link__group-name"
    DEGREE_COURSE = "document-link__name"
    EXCEL_FILE = "a"


class Structure(WebsiteIterator):
    """Итератор по иерархической структуре расписания.

    Осуществляет последовательный разбор DOM-дерева и формирует набор
    атрибутов контекста для каждой найденной ссылки на документ, который
    включает следующее:

    - заголовки формы обучения («Расписание учебных занятий ОФО, ОФЗО»,
      «Расписание установочной сессии ЗФО и др.);
    - заголовки наименований институтов («ВТШ СПИ Факультет информационных
      технологий», «Институт перспективных исследований» и др.);
    - заголовки Excel документов («1 курс Бакалавриат», «2 курс
      Специалитет», «ИТ/б-24-2-о, ИТ/б-24-3-о» и др.);
    - заголовки-разделители Excel файлов («I семестр» и «II семестр»).

    Такой комплект данных необходим для организации механизмов глубокой
    фильтрации и расширения информационного поля расписания.
    """

    def __init__(self, content: str) -> None:
        """Создает экземпляр обходчика на основе исходного кода страницы.

        :param content: Строковое HTML-содержимое веб-страницы.
        """
        self._tree: Any = fromstring(content)
        self._filters: dict[DataKey, Any] | None = None

    def __iter__(self) -> Iterator[tuple[str, dict[DataKey, Any]]]:
        """Запускает обход структуры элементов и возвращает ссылки с контекстом.

        Расположение элементов верстки позволяет накапливать данные за один
        цикл, отдавая при найденной ссылки. Временная сложность алгоритма
        составляет :math:`O(n)`, где :math:`n` — число обрабатываемых узлов
        DOM-дерева.

        Использование:
        .. code-block:: python
            for url, data in structure:
                if data.get(DataKey.SEMESTER) == "II семестр":
                    ...

        :yields: Кортеж из URL-адреса файла и словаря сопоставленных атрибутов.
        """
        for url, data in self._iter_only_excel_files():
            if self._filters:
                filter_keys: set = set(self._filters.keys())
                data_keys: set = set(data.keys())
                intersect_keys: set = filter_keys.intersection(data_keys)
                if intersect_keys and any(
                    data[key] != self._filters[key] for key in intersect_keys
                ):
                    continue
            yield url, data

    def with_filters(
        self, filters: dict[Any, Any] | None = None
    ) -> "Structure":
        """Задает критерии отбора записей при итерации.

        Ключи, отсутствующие в схеме атрибутов, игнорируются при фильтрации.

        :param filters: Словарь с эталонными значениями атрибутов.
        :return: Текущий экземпляр класса.
        """
        self._filters = filters
        return self

    def _iter_all(self) -> Iterator[tuple[str, dict[DataKey, Any]]]:
        """Обходит целевые узлы HTML-дерева в порядке их размещения."""
        _xpath_expr: str = (
            f"//*[local-name()='{_HTML.INSTITUTE}' or "
            f"local-name()='{_HTML.EXCEL_FILE}' or "
            f"contains(@class, '{_HTML.STUDY_FORM}') or "
            f"contains(@class, '{_HTML.SEMESTER}') or "
            f"contains(@class, '{_HTML.DEGREE_COURSE}')]"
        )
        url: str | None = None
        data: dict[DataKey, Any] = {item: None for item in DataKey}

        for element in self._tree.xpath(_xpath_expr):
            tag: Any = element.tag
            if tag == _HTML.INSTITUTE:
                data[DataKey.INSTITUTE] = element.text_content().strip()
            elif tag == _HTML.EXCEL_FILE:
                url = element.get("href")

            tag_classes: Any = element.get("class", "").split()
            if tag_classes:
                if _HTML.STUDY_FORM in tag_classes:
                    data[DataKey.STUDY_FORM] = element.text_content().strip()
                elif _HTML.SEMESTER in tag_classes:
                    data[DataKey.SEMESTER] = element.text_content().strip()
                elif _HTML.DEGREE_COURSE in tag_classes:
                    data[DataKey.DEGREE_COURSE] = element.text_content().strip()
                    if url:
                        yield url, data.copy()

    def _iter_only_excel_files(
        self,
    ) -> Iterator[tuple[str, dict[DataKey, Any]]]:
        """Исключает из результатов элементы, не относящиеся к расписанию."""
        for url, data in self._iter_all():
            if (
                not data[DataKey.DEGREE_COURSE]
                .strip()
                .startswith("Распоряжение")
            ):
                yield url, data
