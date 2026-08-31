"""Модуль вспомогательных функций парсинга и преобразования данных расписания.

Предоставляет утилиты для извлечения курсов, групп, дисциплин, подгрупп,
преподавателей, а также для преобразования строк в объекты дат и времени.
"""

import re
from datetime import date
from datetime import datetime
from datetime import time
from ..models.enums import Degree
from ..models.enums import StudyForm
from ..models.enums import StudyWeekday


def extract_course_number_and_degree(
    group: str,
) -> tuple[int, Degree]:
    """Извлекает номер курса и уровень образования из наименования группы.

    :param group: Шифр академической группы.
    :return: Кортеж из номера курса и уровня образования.
    """
    _degree_mapping: dict[str, Degree] = {
        "б": Degree.BACHELOR,
        "с": Degree.SPECIALIST,
        "м": Degree.MASTER,
        "а": Degree.POSTGRADUATE,
    }
    key: str = group.split("/")[1][0]
    degree: Degree = _degree_mapping[key]
    course: int = int(group.split("-")[2])
    return course, degree


def get_the_associated_study_form(study_form: str) -> StudyForm | None:
    """Сопоставляет текстовое описание формы обучения с перечислением.

    :param study_form: Строковое наименование формы обучения.
    :return: Элемент перечисления формы обучения или None.
    """
    if not study_form:
        return None
    return StudyForm(study_form.strip())


def extract_groupname(raw_groupname: str) -> str:
    """Извлекает очищенное наименование группы из сырой строки.

    :param raw_groupname: Исходная строка с названием группы.
    :return: Наименование академической группы.
    :raises ValueError: Если входная строка не передана.
    """
    if not raw_groupname:
        raise ValueError("Параметр raw_groupname не может быть пустым.")
    return raw_groupname.split(":")[-1].strip()


def extract_subgroup_number(subgroup: str) -> int | None:
    """Извлекает номер подгруппы из текстового описания.

    :param subgroup: Строковое представление подгруппы.
    :return: Номер подгруппы или None.
    """
    if not subgroup:
        return None
    return int(subgroup.split()[1])


def get_the_associated_day(day: str) -> StudyWeekday | None:
    """Возвращает элемент перечисления дня недели по его названию.

    :param day: Наименование дня недели.
    :return: Элемент перечисления дня недели или None.
    """
    try:
        return StudyWeekday(day)
    except ValueError:
        return None


def create_date_object(raw_date: str | date) -> tuple[date, int]:
    """Формирует объект даты и возвращает его вместе с годом.

    :param raw_date: Строка с датой или существующий объект даты.
    :return: Кортеж из объекта даты и соответствующего года.
    :raises AttributeError: Если не удалось разобрать формат даты.
    """
    if isinstance(raw_date, date):
        return raw_date, raw_date.year

    match = re.search(r"(\d+)\D+(\d+)\D+(\d+)", raw_date)
    if match:
        day, month, year = match.groups()
        date_object: datetime = datetime.strptime(
            f"{int(day):02d}.{int(month):02d}.{int(year):04d}", "%d.%m.%Y"
        )
        return date_object.date(), date_object.year

    raise AttributeError(
        "Неверный формат данных, невозможно создать объект datetime."
    )


def extract_classname_and_teacher(
    raw_class: str,
) -> tuple[str, str, int | None]:
    """Извлекает название предмета, имя преподавателя и номер подгруппы.

    :param raw_class: Сырая строка с информацией о занятии.
    :return: Кортеж из названия предмета, ФИО преподавателя и номера подгруппы.
    :raises ValueError: Если входная строка не передана.
    """
    if not raw_class:
        raise ValueError("Параметр raw_class не может быть пустым.")

    class_info_splited: list[str] = raw_class.split(",")
    teacher: str = class_info_splited[-1].strip()
    subgroup: int | None = None

    if raw_class.startswith("подгр"):
        classname: str = ", ".join(class_info_splited[1:-1]).strip()
        match = re.search(r"\d+", raw_class)
        if match:
            subgroup = int(match.group())
    else:
        classname = ", ".join(class_info_splited[0:-1]).strip()

    return classname, teacher, subgroup


def create_time_object(raw_time: str) -> time:
    """Преобразует строковое представление времени в объект time.

    :param raw_time: Строка со временем в формате "ЧЧ:ММ".
    :return: Объект времени.
    """
    return datetime.strptime(raw_time, "%H:%M").time()


def extract_week_number(week: str) -> int:
    """Извлекает номер учебной недели из текстовой строки.

    :param week: Строка с указанием недели.
    :return: Численный номер недели.
    :raises ValueError: Если строка пуста или номер недели не найден.
    """
    if not week:
        raise ValueError("Параметр week не может быть пустым.")

    match = re.search(r"\d+", week)
    if not match:
        raise ValueError("Номер недели не найден в переданной строке.")

    return int(match.group())
