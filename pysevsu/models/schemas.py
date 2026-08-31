"""Модели схемы данных учебного расписания.

Модуль содержит структуры данных для представления ключевых доменных сущностей
расписания: академических групп (:class:`Group`), учебных недель 
(:class:`Week`), преподавателей (:class:`Teacher`), аудиторий 
(:class:`Classroom`) и учебных занятий (:class:`Class`).
"""

from dataclasses import dataclass
from datetime import date
from datetime import time
from pysevsu.models.enums import Degree
from pysevsu.models.enums import StudyForm
from pysevsu.models.enums import StudyWeekday


@dataclass(frozen=False)
class Group:
    """Академическая группа."""

    name: str
    institute: str
    course: int | None = None
    degree: Degree | None = None


@dataclass(frozen=False)
class Week:
    """Учебная неделя."""

    number: int
    year: int
    semester: str | None = None
    start_date: str | None = None
    end_date: str | None = None


@dataclass(frozen=False)
class Teacher:
    """Преподаватель."""

    fullname: str


@dataclass(frozen=False)
class Classroom:
    """Учебная аудитория."""

    cipher: str


@dataclass(frozen=False)
class Class:
    """Учебное занятие.

    Агрегирует сведения о времени и месте проведения занятия, преподавателе,
    академической группе и дисциплине.
    """

    number: int
    date: date
    time: time
    name: str
    group: Group
    week: Week
    study_form: StudyForm | None = None
    day: StudyWeekday | None = None
    room: Classroom | None = None
    teacher: Teacher | None = None
    type_: str | None = None
    subgroup: int | None = None