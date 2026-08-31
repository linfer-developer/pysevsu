"""Пакет предоставляет модели организации выходных данных библиотеки."""

from .schemas import Class
from .schemas import Classroom
from .schemas import Group
from .schemas import Teacher
from .schemas import Week
from .enums import StudyForm
from .enums import StudyWeekday
from .enums import Degree
from .raw import WebsiteDataKey
from .raw import ExcelDataKey

__all__ = [
    "Class",
    "Classroom",
    "Group",
    "Teacher",
    "Week",
    "WebsiteDataKey",
    "ExcelDataKey",
    "StudyForm",
    "StudyWeekday",
    "Degree"
]
