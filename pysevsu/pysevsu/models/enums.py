"""enums"""

from enum import StrEnum
from typing import Any, Dict


class WeekFields(StrEnum):
    """Enumeration of keys used to describe a week in the output dictionary.

    Values:
        YEAR: The year of the week (e.g., ``"2026"``).
        TITLE: The title of the week (the sheet name).
        START_DATE: The first date of the week (string).
        END_DATE: The last date of the week (string).

    Provides :meth:`get_dict` to obtain a template dictionary with ``None``
    values.
    """

    YEAR = "year"
    TITLE = "week_title"
    START_DATE = "week_start_date"
    END_DATE = "week_end_date"

    @classmethod
    def get_dict(cls) -> Dict[str, Any]:
        """Return a dictionary with all week-level fields set to ``None``.

        :return: A template dictionary, e.g.,
                 ``{"year": None, "week_title": None, ...}``
        """
        return {str(item): None for item in cls}


class LessonFields(StrEnum):
    """Enumeration of keys used to describe a single lesson in the output
    dictionary.

    Values:
        GROUPNAME: The group identifier (e.g., ``"ИТ/б-24-2-о"``).
        DAY: The day of the week (e.g., ``"Понедельник"``).
        DATE: The exact date of the lesson (string).
        NUMBER: The lesson number within the day.
        START_TIME: The start time (string).
        TITLE: The title of the lesson.
        TEACHER: The teacher's name (extracted from the title).
        TYPE: The type of lesson (e.g., lecture, practice).
        CLASSROOM: The classroom number or name.

    Provides :meth:`get_dict` to obtain a template dictionary with ``None``
    values.
    """

    GROUPNAME = "group"
    DAY = "day"
    DATE = "date"
    NUMBER = "number"
    START_TIME = "start_time"
    TITLE = "title"
    TEACHER = "teacher"
    TYPE = "type"
    CLASSROOM = "classroom"

    @classmethod
    def get_dict(cls) -> Dict[str, Any]:
        """Return a dictionary with all lesson-level fields set to ``None``.

        :return: A template dictionary, e.g.,
                 ``{"group": None, "day": None, ...}``
        """
        return {str(item): None for item in cls}


class ScheduleSource(StrEnum):
    """Enumeration of keys used in the output dictionary for each schedule entry.

    Values:
        HEAD: Study form (e.g., ``"Очная"``).
        LIST_TITLE: Institute name.
        INLIST_TITLE: Semester description.
        FILENAME: Course name or file description.
        FILE_URL: Relative URL to the Excel file.

    Provides :meth:`get_dict` to create a template dictionary with all values
    set to ``None``.
    """

    HEAD = "study_form"
    LIST_TITLE = "institute"
    INLIST_TITLE = "semester"
    FILENAME = "course"
    FILE_URL = "file_url"

    @classmethod
    def get_dict(cls) -> Dict[str, None]:
        """Provides :meth:`get_dict` to create a template dictionary with all
        values set to ``None``.
        """
        return {str(item): None for item in cls}
