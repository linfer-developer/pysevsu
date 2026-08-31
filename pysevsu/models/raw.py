"""Ключи сырых данных источников."""

from enum import StrEnum

class WebsiteDataKey(StrEnum):
    """Ключи атрибутов контекста структуры веб-страницы расписания."""

    STUDY_FORM = "study_form"
    INSTITUTE = "institute"
    SEMESTER = "semester"
    DEGREE_COURSE = "degree_course"


class ExcelDataKey(StrEnum):
    """Ключи атрибутов элементов расписания из файлов Excel."""

    WEEK = "week"
    GROUP = "group"
    SUBGROUP = "subgroup"
    DAY = "day"
    DATE = "date"
    NUMBER = "number"
    START_TIME = "start_time"
    CLASS = "classname"
    TYPE = "type"
    CLASSROOM = "classroom"