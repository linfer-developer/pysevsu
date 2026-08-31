"""Обработка файлов электронных таблиц учебного расписания.

Предоставляет классы :class:`File` и :class:`Worksheet` для эффективного
потокового извлечения данных из рабочих листов. Результат является
последовательностью словарей с ключами :class:`DataKey` .
"""

import copy
from enum import StrEnum
from io import BytesIO
from typing import Any
from typing import Iterable
from typing import Iterator
from python_calamine import CalamineSheet
from python_calamine import CalamineWorkbook
from python_calamine import load_workbook
from ..core import CorruptedExcelFileError
from ..core import ExcelIterator
from ..models.raw import ExcelDataKey as DataKey


class _CLASSATTRS(StrEnum):
    WEEK = "уч.н."
    GROUP = "Группа"
    SUBGROUP = "подгруппа"
    DAY = "День"
    DATE = "Дата"
    NUMBER = "№занятия"
    START_TIME = "Время"
    CLASS = "Занятие"
    TYPE = "Тип"
    CLASSROOM = "Аудитория"


class File(ExcelIterator):
    """Контейнер документа электронной таблицы обеспечивает последовательную
    обработку рабочих листов. Предназначен для использования в качестве
    контекстного менеджера.

    В Excel-документе произвольное количество рабочих листов, именованных
    номерами учебных недель с приставки «уч.н.». Остальные (обычно один в
    начале) отражают справочную информацию и в обработку не включаются.
    """

    def __init__(self, content: BytesIO | bytes) -> None:
        """Инициализирует объект содержимым файла.

        :param content: Двоичные данные книги Excel.
        """
        self._workbook: CalamineWorkbook | None = None
        self._filters: dict[DataKey, Any] | None = None
        if isinstance(content, BytesIO):
            self._content = content
        else:
            self._content: BytesIO = BytesIO(content)

    def __enter__(self) -> "File":
        """Загружает книгу и подготавливает поток чтения."""
        try:
            self._content.seek(0)
            self._workbook = load_workbook(self._content)
            return self
        except Exception as error:
            raise CorruptedExcelFileError(
                "Excel file is corrupted: check the integrity of the file "
                "and its type."
            ) from error

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._workbook:
            self._workbook.close()

    def __iter__(self) -> Iterator[dict[DataKey, Any]]:
        """Запускает последовательную обработку рабочих листов книги.

        Временная сложность алгоритма составляет :math:`O(n \\cdot k)`,
        где :math:`n` — количество листов, :math:`k` — количество ячеек листа.

        .. code-block:: python

            with File(content) as excel_file:
                for data in excel_file:
                    if data.get(DataKey.CLASSROOM) == "I-422":
                        ...

        :yields: Словарь атрибутов записи расписания.
        """
        for worksheet in self.schedule_worksheets:
            if (
                not self._filters
                or self._filters.get(DataKey.WEEK) == worksheet.name
            ):
                yield from worksheet.with_filters(self._filters)

    @property
    def schedule_worksheets(self) -> Iterable["Worksheet"]:
        """Возвращает последовательность валидных рабочих листов книги."""
        if not self._workbook:
            raise AttributeError("")
        for sheetname in self._workbook.sheet_names:
            if sheetname.startswith(_CLASSATTRS.WEEK):
                yield Worksheet(
                    content=self._workbook.get_sheet_by_name(sheetname),
                    name=sheetname,
                )

    def with_filters(self, filters: dict[Any, Any] | None = None) -> "File":
        """Задает критерии отбора записей при итерации.

        :param filters: Словарь сопоставления ключей и их эталонных значений.
        :return: Текущий экземпляр класса.
        """
        self._filters = filters
        return self


class Worksheet:
    """Обработчик отдельного рабочего листа книги.

    На рабочем листе существует множество объединений, в которых данные
    находятся в первой от всех слившихся ячеек. Из-за этого и многоуровневых
    заголовков выбрана стратегия накопления и мутирования информации в процессе
    парсинга. Шаблон внутреннего хранилища предопределен для повышения
    детерминизма (:class:`DataKey`).
    """

    def __init__(self, name: str, content: CalamineSheet) -> None:
        """Инициализирует рабочий лист.

        :param name: Наименование листа.
        :param content: Экземпляр листа библиотеки разбора.
        """
        self._name = name
        self._content = content
        self._filters: dict[DataKey, Any] | None = None

    def __iter__(self) -> Iterator[dict[DataKey, Any]]:
        """Выполняет обход ячеек и формирует поток структурированных записей.

        Временная сложность алгоритма составляет :math:`O(r*c*n)`,
        где :math:`r` — количество строк, :math:`c` — столбцов,
        :math:`n` — записей в ячейке.

        :yields: Словарь атрибутов записи расписания.
        """
        for cell_data in self._iter_content():
            for data in cell_data:
                data[DataKey.WEEK] = self.name
                if self._filters:
                    filter_keys: set = set(self._filters.keys())
                    data_keys: set = set(data.keys())
                    intersect_keys: set = filter_keys.intersection(data_keys)
                    if intersect_keys and any(
                        data[key] != self._filters[key]
                        for key in intersect_keys
                    ):
                        continue
                yield data

    @property
    def name(self) -> str:
        """Наименование рабочего листа."""
        return self._name

    def with_filters(
        self, filters: dict[DataKey, Any] | None = None
    ) -> "Worksheet":
        """Задает критерии отбора записей при итерации.

        :param filters: Словарь сопоставления ключей и их эталонных значений.
        :return: Текущий экземпляр класса.
        """
        self._filters = filters
        return self

    def _iter_rows(self) -> Iterator[tuple[int, int, Any]]:
        for row, values in enumerate(self._content.iter_rows()):
            for column, value in enumerate(values):
                if value is not None:
                    yield row, column, value

    def _iter_content(self) -> Iterator["_CellData"]:
        """Разбирает ячейки листа и формирует промежуточные структуры данных.

        Сопоставлена нумерация колонок ячеек и заголовки для
        отслеживания расположения элементов в структуре рабочего листа.
        Группы и номера занятий накрывают друг друга из-за чего были помещены в
        раздельные хранилища. При каждой новой итерации цикла текущее значение
        сопоставливается с собранной на предыдущих этапах разметкой.

        Для студенческой группы может существовать более одной
        подгруппы с различными или совместными занятиями. В последнем из них,
        предмет является объединенной ячейкой, содержимое которой находится в
        первой подгруппе, тогда как остальные свойства — в последней.
        """
        cell_data: _CellData = _CellData()
        _group_header: dict[int, str] = {}
        _class_header: dict[int, _CLASSATTRS] = {}

        for _, column, value in self._iter_rows():
            if isinstance(value, str) and value.startswith(_CLASSATTRS.GROUP):
                _group_header[column] = value
                continue

            if value not in {item.value for item in _CLASSATTRS}:
                groupname: str | None = _group_header.get(column)
                class_attribute: _CLASSATTRS | None = _class_header.get(column)

                if groupname:
                    yield cell_data.copy()
                    cell_data.reset_subject()
                    cell_data.add(DataKey.GROUP, groupname)

                if class_attribute == _CLASSATTRS.CLASS:
                    if cell_data.get(DataKey.CLASS) and value:
                        yield cell_data.copy()
                        cell_data.reset_subject()

                if class_attribute and value:
                    cell_data.add(DataKey[class_attribute.name], value)

            else:
                _class_header[column] = _CLASSATTRS(value)


class _CellData:
    """Внутреннее хранилище и преобразователь контекста ячейки."""

    def __init__(self) -> None:
        self._content: dict[DataKey, Any] = {
            item: None for item in DataKey
        }

    def __iter__(self) -> Iterator[dict[DataKey, Any]]:
        """Разбивает множественные записи ячейки на отдельные элементы.

        В ячейке может содержаться одно и более занятий, аудиторий и типов,
        которые записаны последовательно друг за другом и разделены переносом
        строки. Количество наименований предмета может не соответствовать другим
        атрибутам (аудитория и типам). Например, составитель расписания может
        определить несколько типов для одного занятия (дистанционное и зачет).
        """
        items: list[list[str]] = self._split_classes()
        subjects_length: int = len(items[0])
        types_length: int = len(items[1])
        classrooms_length: int = len(items[2])

        for index, subject in enumerate(items[0]):
            if subject:
                self.add(DataKey.CLASS, subject)

            if types_length > index:
                self.add(DataKey.TYPE, items[1][index])
                if subjects_length == index + 1:
                    self.add(DataKey.TYPE, ", ".join(items[1][index:]))

            if classrooms_length > index:
                self.add(DataKey.CLASSROOM, items[2][index])
                if subjects_length == index + 1:
                    self.add(
                        DataKey.CLASSROOM, ", ".join(items[2][index:])
                    )

            yield self.content

    @property
    def content(self) -> dict[DataKey, Any]:
        return self._content.copy()

    def add(self, key: DataKey, value: Any) -> None:
        if not isinstance(key, DataKey):
            raise TypeError("")
        self._content[key] = value

    def get(self, key: DataKey) -> None:
        return self._content.get(key)

    def copy(self) -> "_CellData":
        return copy.copy(self)

    def reset(self) -> None:
        self._content.update({item: None for item in DataKey})

    def reset_subject(self) -> None:
        self._content.update(
            {
                DataKey.CLASS: None,
                DataKey.TYPE: None,
                DataKey.CLASSROOM: None,
            }
        )

    def _split_classes(self) -> list[list[str]]:
        classes_items: list[list[str]] = [[], [], []]
        _merged_subject: str | None = self._content.get(DataKey.CLASS)
        _merged_classrooms: str | None = self._content.get(
            DataKey.CLASSROOM
        )
        _merged_types: str | None = self._content.get(DataKey.TYPE)

        if _merged_subject:
            classes: list[str] = _merged_subject.splitlines()
            classes_items[0] = classes

        if _merged_classrooms:
            classes: list[str] = _merged_classrooms.splitlines()
            classes_items[1] = classes

        if _merged_types:
            classes: list[str] = _merged_types.splitlines()
            classes_items[2] = classes

        return classes_items
