"""Excel Schedule Parser
_____________________

This module provides functionality to parse an Excel workbook containing
weekly lesson schedules. It expects sheets named with a specific prefix
(``уч.н.`` by default) and a particular column layout. The parser extracts
structured data about weeks and individual lessons, yielding them as
dictionaries.

Key components:

- :class:`WeekFields` and :class:`LessonFields` define the field names
  for the output dictionaries.
- :class:`ExcelFile` is a context manager that opens a workbook and yields
  parsed lesson data for all matching worksheets.
- :class:`Worksheet` wraps an individual sheet, mapping its columns to the
  semantic fields and handling multi-line cells (a single cell may contain
  several lessons separated by newlines).
- :class:`_DataFormatter` provides static helper methods to clean and split
  string values.

Usage example::

    with ExcelFile(file_bytes) as ef:
        for lesson in ef.parse():
            print(lesson)
"""

from itertools import zip_longest
from enum import Enum
from io import BytesIO
import python_calamine as calamine
from typing import Any, Dict, List, Optional, Iterator, Tuple, Union
from pysevsu.models.enums import WeekFields, LessonFields
from pysevsu.models.types import WeekData, LessonData

SHEETNAME_PREFIX: str = "уч.н."


class ExcelFile:
    """Context manager for parsing an Excel file containing lesson schedules.

    Opens the workbook in read-only mode, iterates over worksheets whose name
    starts with :data:`SHEETNAME_PREFIX`, and yields lesson dictionaries
    enriched with week-level information.

    :param file: Either a ``BytesIO`` object or raw bytes of an Excel file.
    :ivar workbook: The loaded ``openpyxl.Workbook`` instance (set after
                    entering the context).
    """

    def __init__(self, file: Union[BytesIO, bytes]) -> None:
        if isinstance(file, BytesIO):
            self.file = file
        else:
            self.file: BytesIO = BytesIO(file)
        self.workbook: calamine.CalamineWorkbook = None

    def __enter__(self) -> "ExcelFile":
        """Enter the runtime context. Opens the workbook in read-only mode.

        :return: The instance itself.
        """
        self.file.seek(0)
        self.workbook = calamine.load_workbook(self.file)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the runtime context. Closes the workbook.

        :param exc_type: Exception type (if any).
        :param exc_val: Exception value (if any).
        :param exc_tb: Traceback (if any).
        """
        ...

    @property
    def worksheets(self) -> Iterator[Tuple[str, "Worksheet"]]:
        """Yield tuples of ``(sheet_name, Worksheet instance)`` for every sheet
        whose name starts with :data:`SHEETNAME_PREFIX`.

        :yields: Pairs of sheet name and corresponding :class:`Worksheet`.
        """
        for sheetname in self.workbook.sheet_names:
            # Example: sheetname = "уч.н. 3"
            if sheetname.startswith(SHEETNAME_PREFIX):
                worksheet = Worksheet(self.workbook.get_sheet_by_name(sheetname))
                yield sheetname, worksheet

    def parse(self) -> Iterator[Dict[str, Any]]:
        """Main generator that extracts all lessons from the workbook.

        For each matching worksheet it retrieves week dates, then iterates over
        all lessons yielded by that sheet, enriching each lesson dictionary
        with the week-level data.

        :yields: Lesson dictionaries containing both lesson and week fields.
        """
        week_data: Dict[str, Any] = WeekFields.get_dict()

        for sheetname, worksheet in self.worksheets:
            # Example: sheetname = "уч.н. 3"
            week_data.update(
                {WeekFields.TITLE: sheetname, **worksheet.get_week_dates()}
            )

            for data in worksheet.parse_lessons():
                data.update(week_data)
                yield data


class _Column(str, Enum):
    """Internal enumeration mapping the expected header texts in the Excel sheet
    to their Russian counterparts. Used to build the column-to-field mapping.

    Values:
        GROUP: Column header for the group name.
        DAY: Column header for the day of the week.
        DATE: Column header for the date.
        NUMBER: Column header for the lesson number.
        START_TIME: Column header for the start time.
        LESSON: Column header for the lesson title.
        TYPE: Column header for the lesson type.
        CLASSROOM: Column header for the classroom.
    """

    GROUP = "Группа"
    DAY = "День"
    DATE = "Дата"
    NUMBER = "№занятия"
    START_TIME = "Время"
    LESSON = "Занятие"
    TYPE = "Тип"
    CLASSROOM = "Аудитория"


# Build a mapping from the Russian column headers (as they appear in the sheet)
# to the corresponding :class:`LessonFields` members.
mapping: Dict[_Column, LessonFields] = {
    _Column.GROUP: LessonFields.GROUPNAME,
    _Column.DAY: LessonFields.DAY,
    _Column.DATE: LessonFields.DATE,
    _Column.NUMBER: LessonFields.NUMBER,
    _Column.START_TIME: LessonFields.START_TIME,
    _Column.LESSON: LessonFields.TITLE,
    _Column.TYPE: LessonFields.TYPE,
    _Column.CLASSROOM: LessonFields.CLASSROOM,
}


class Worksheet:
    """Wraps an openpyxl worksheet and provides methods to extract structured
    lesson data based on a fixed column layout.

    :param content: An openpyxl worksheet object.
    """

    def __init__(self, content: calamine.CalamineSheet) -> None:
        self.content = content
        self._raw_data: List[List[Any]] = None

    def _iter_rows(self) -> Iterator[Tuple[int, int, Any]]:
        """Iterate over all non‑empty cells in the worksheet, yielding
        ``(cell, value)`` tuples for every cell that is not ``None``.

        :yields: Pairs of the openpyxl cell object and its value.
        """
        if self._raw_data is None:
            self._raw_data = self.content.to_python()

        for row, values in enumerate(self._raw_data):
            for column, value in enumerate(values):
                if value is not None:
                    yield row, column, value

    def iter_mapped_cells(
        self,
    ) -> Iterator[Tuple[int, int, Any, LessonFields]]:
        """Map raw cell values to :class:`LessonFields` fields.

        First scans the rows to detect column headers (using
        :func:`get_mapping`) and records their column indices. Then for every
        subsequent cell in a recognised column, yields a tuple of ``
        (LessonFields member, cell value, cell object)``.

        .. note::

           A cell whose value equals one of the header texts is treated as a
           header re‑definition and skipped.

        :yields: Triples of the semantic column identifier, the cell value, and
                 the cell object.
        """
        column_titles: Dict[int, str] = {}
        for row, column, value in self._iter_rows():
            if value in mapping:
                column_titles[column] = value  # Example: {1: "Дата"}
                continue

            column_title = column_titles.get(column)  # Example: "Дата"
            if column_title is None:
                continue

            yield row, column, value, mapping[column_title]

    def parse_lessons(self) -> Iterator[LessonData]:
        """Parse all lessons from the worksheet.

        The method accumulates lesson data in a dictionary. Whenever a new group
        is encountered (cell starting with :attr:`_Column.GROUP`), the group
        name is stored. Data from subsequent columns overwrites existing fields
        until the ``CLASSROOM`` column is reached, which signals the end of a
        lesson block. At that point the possibly multi‑line values are split and
        formatted by :meth:`_DataFormatter.format_`, yielding one or more
        complete lesson dictionaries.

        After processing, the lesson-specific fields are reset, leaving the
        group name intact.

        :yields: Complete lesson dictionaries.
        """
        data: LessonData = LessonFields.get_dict()

        for _, _, value, column_title in self.iter_mapped_cells():
            # Example: "Группа : ИТ/б-24-2-о"
            if isinstance(value, str) and value.startswith(_Column.GROUP):
                data[LessonFields.GROUPNAME] = value
                continue

            data[column_title] = value
            if column_title == LessonFields.CLASSROOM:
                # In an Excel worksheet, the class column is the last column
                # before the next class begins. However, the next class starts
                # with the class name, while the day of the week, class number,
                # and time remain in the very first columns all the way to the
                # end of the worksheet.
                yield from _DataFormatter.format_(
                    data
                )  # A single cell can contain multiple lessons
                self._reset_lesson(data)

    def get_week_dates(self) -> Dict[WeekData]:
        """Extract the year, start date, and end date for the week from the
        ``DATE`` column.

        The method reads all non‑empty dates (assumed to be the very first
        column entries, sorted chronologically) and returns a dictionary with
        keys ``year``, ``week_start_date``, and ``week_end_date``.

        .. note::

           Perhaps the method needs to be revised

        :return: A dictionary with week date fields, or an empty dict if no
                 dates are found.
        """
        # TODO: Not working
        dates: List[Any] = []
        data: WeekData = WeekFields.get_dict()

        for _, _, value, column_title in self.iter_mapped_cells():
            if column_title != LessonFields.DATE:
                continue
            if not isinstance(value, str) or not value.strip():
                break
            dates.append(value)

        if not dates:
            return {}

        data.update(
            {
                WeekFields.YEAR: dates[0].split(".")[-1],  # XX.XX.XXXX
                WeekFields.START_DATE: dates[0],
                WeekFields.END_DATE: dates[-1],
            }
        )
        return data

    @staticmethod
    def _reset_lesson(data: LessonData) -> None:
        """Clear the lesson‑specific fields (title, type, classroom) while
        keeping the group name and other persistent fields.

        :param data: The lesson data dictionary to modify in place.
        """
        data.update(
            {
                LessonFields.TITLE: None,
                LessonFields.TYPE: None,
                LessonFields.CLASSROOM: None,
            }
        )


class _DataFormatter:
    """Static helper methods for splitting and cleaning string values found in
    the schedule.

    These methods are used to handle multi‑line cells, to extract the teacher
    name from the lesson title, and to strip group name prefixes.
    """

    @staticmethod
    def split_title(raw: str) -> List[str]:
        """Split a combined title string into the lesson title and the teacher
        name.

        The teacher name is assumed to be the last comma‑separated part.
        Example:
        ``"Высшая математика, Попков"`` → ``{"title": "Высшая математика", "teacher": "Попков"}``.

        :param raw: The raw title string.
        :return: A dictionary with keys ``title`` and ``teacher``.
        """
        raw_list: List[str] = raw.split(",")
        return {
            LessonFields.TITLE: ", ".join(raw_list[0:-1]).strip(),
            LessonFields.TEACHER: raw_list[-1].strip(),
        }

    @staticmethod
    def splitlines_safe(raw: Optional[str]) -> List[str]:
        """Split a string into lines, or return an empty list if the input is
        ``None``.
        """
        return raw.splitlines() if raw else []

    @staticmethod
    def format_groupname(raw: str) -> str:
        """Extract the group identifier from a string that may contain a prefix
        followed by a colon. For example, ``"Группа : ИТ/б-24-2-о"`` becomes
        ``"ИТ/б-24-2-о"``.

        :param raw: The raw group string.
        :return: The trimmed group name.
        """
        if not raw:
            return ""
        return raw.split(":")[-1].strip()

    @staticmethod
    def format_(data: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Yield one or more formatted lesson dictionaries from a single
        accumulated data block.

        The ``title``, ``type``, and ``classroom`` fields may contain
        newline‑separated lists (multiple lessons in one cell). This method
        splits them and pairs corresponding elements. For each set it creates a
        copy of the data dictionary, updating it with the split values and the
        properly split teacher/title.

        :param data: Accumulated lesson data (may contain multi‑line strings).
        :yields: Fully formatted lesson dictionaries.
        """
        if not data[LessonFields.TITLE]:
            return

        titles: List[str] = _DataFormatter.splitlines_safe(data[LessonFields.TITLE])
        types: List[str] = _DataFormatter.splitlines_safe(data[LessonFields.TYPE])
        classrooms: List[str] = _DataFormatter.splitlines_safe(
            data[LessonFields.CLASSROOM]
        )

        for title, type_, classroom in zip_longest(
            titles, types, classrooms, fillvalue=""
        ):
            group: str = _DataFormatter.format_groupname(data[LessonFields.GROUPNAME])
            data.update(
                {
                    LessonFields.GROUPNAME: group,
                    **_DataFormatter.split_title(title),
                    LessonFields.TYPE: type_.strip(),
                    LessonFields.CLASSROOM: classroom.strip(),
                }
            )
            yield data.copy()
