"""Модуль преобразования сырых данных расписания в доменные модели.

Содержит функцию маппинга словаря извлеченных метаданных сайта и строк Excel
в агрегированный объект занятия (:class:`~.models.schemas.Class`).
"""

from datetime import date, time
from typing import Any
from .formatter import create_date_object
from .formatter import create_time_object
from .formatter import extract_classname_and_teacher
from .formatter import extract_course_number_and_degree
from .formatter import extract_groupname
from .formatter import extract_week_number
from .formatter import get_the_associated_day
from .formatter import get_the_associated_study_form
from ..models import Degree
from ..models import StudyForm
from ..models import StudyWeekday
from ..models import ExcelDataKey
from ..models import WebsiteDataKey
from ..models import Class
from ..models import Classroom
from ..models import Group
from ..models import Teacher
from ..models import Week


def create(data: dict[WebsiteDataKey | ExcelDataKey, Any]) -> Class:
    """Создает экземпляр модели занятия на основе словаря сырых данных.

    :param data: Объединенный словарь метаданных сайта и данных файла Excel.
    :return: Сформированный объект доменной модели :class:`Class`.
    :raises ValueError: Если отсутствуют критически важные атрибуты занятия.
    """
    degree: Degree | None = None
    study_form: StudyForm | None = None
    day: StudyWeekday | None = None
    time_object: time | None = None
    date_object: date | None = None
    course: int | None = None
    subgroup: int | None = None
    week_number: int | None = None
    year: int | None = None
    groupname: str | None = None
    classname: str | None = None
    teacher: str | None = None
    institute: str | None = None
    semester: str | None = None
    type_: str | None = None
    classroom: str | None = None

    study_form = get_the_associated_study_form(data[WebsiteDataKey.STUDY_FORM])
    institute = data[WebsiteDataKey.INSTITUTE]
    semester = data[WebsiteDataKey.SEMESTER]
    number = int(data[ExcelDataKey.NUMBER])
    type_ = data[ExcelDataKey.TYPE]
    classroom_object = data[ExcelDataKey.CLASSROOM]
    groupname = extract_groupname(data[ExcelDataKey.GROUP])
    course, degree = extract_course_number_and_degree(groupname)
    day = get_the_associated_day(data[ExcelDataKey.DAY])
    week_number = extract_week_number(data[ExcelDataKey.WEEK])
    date_object, year = create_date_object(data[ExcelDataKey.DATE])
    time_object = create_time_object(data[ExcelDataKey.START_TIME])
    classname, teacher, subgroup = extract_classname_and_teacher(
        data[ExcelDataKey.CLASS]
    )

    group_object: Group | None = None
    week_object: Week | None = None
    teacher_object: Teacher | None = None
    classroom_object: Classroom | None = None
    class_object: Class | None = None

    if not institute:
        raise ValueError("Нарушение целостности данных: отсутствует институт.")

    if not groupname:
        raise ValueError(
            "Нарушение целостности данных: отсутствует шифр группы."
        )

    if not number:
        raise ValueError(
            "Нарушение целостности данных: отсутствует номер занятия."
        )

    if not week_number:
        raise ValueError(
            "Нарушение целостности данных: отсутствует номер учебной недели."
        )

    if not date_object:
        raise ValueError(
            "Нарушение целостности данных: отсутствует дата проведения занятия."
        )

    if not time_object:
        raise ValueError(
            "Нарушение целостности данных: отсутствует время проведения занятия."
        )

    if not classname:
        raise ValueError(
            "Нарушение целостности данных: отсутствует наименование занятия."
        )

    if teacher:
        teacher_object = Teacher(teacher)

    if classroom:
        classroom_object = Classroom(classroom)

    week_object = Week(number=week_number, year=year, semester=semester)
    group_object = Group(
        name=groupname,
        institute=institute,
        course=course if course else None,
        degree=degree if degree else None,
    )
    class_object = Class(
        number=number,
        date=date_object,
        time=time_object,
        name=classname,
        study_form=study_form,
        day=day,
        group=group_object,
        week=week_object,
        teacher=teacher_object if teacher_object else None,
        room=classroom_object if classroom_object else None,
        type_=type_,
        subgroup=subgroup,
    )
    return class_object
