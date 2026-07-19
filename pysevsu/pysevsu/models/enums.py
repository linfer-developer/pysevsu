"""Enumerations for educational schedule data classification.

This module defines standard enums used throughout the application for
categorizing educational data, including study forms, weekdays, and
academic degrees. These enums ensure type safety and consistent
naming across the codebase.
"""

from enum import StrEnum


class StudyForm(StrEnum):
    """Study form categories in the educational institution.

    Defines the different modes of study and examination types
    used in the schedule system.

    Values correspond to the actual labels used in the schedule pages:
    - Full-time classes (ОФО, ОЗФО) - regular classes
    - Correspondence/external classes (ЗФО) - distance learning
    - Certification sessions for full-time students
    """

    FULL_TIME_CLASSES = "Расписание учебных занятий ОФО, ОЗФО"
    CORRESPONDENCE_CLASSES = "Расписание экзаменационной и установочной сессии ЗФО"
    FULL_TIME_CERTIFICATION = "Расписание промежуточной аттестации ОФО, ОЗФО"


class StudyWeekday(StrEnum):
    """Weekday names in Russian.

    Used for classifying schedule entries by day of the week.
    Values are in Russian as they appear in the source data.
    """

    MONDAY = "Понедельник"
    TUESDAY = "Вторник"
    WEDNESDAY = "Среда"
    THURSDAY = "Четверг"
    FRIDAY = "Пятница"
    SATURDAY = "Суббота"


class Degree(StrEnum):
    """Academic degree levels offered by the institution.

    Defines the standard degree levels in the Russian education system:
    - Bachelor's (Бакалавриат) - 4-year undergraduate
    - Specialist (Специалитет) - 5-year professional
    - Master's (Магистратура) - 2-year postgraduate
    - Postgraduate (Аспирантура) - 3-year doctoral preparation
    """

    BACHELOR = "Бакалавриат"
    SPECIALIST = "Специалитет"
    MASTER = "Магистратура"
    POSTGRADUATE = "Аспирантура"
