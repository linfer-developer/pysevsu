from dataclasses import dataclass
from datetime import datetime


@dataclass
class Week:
    number: int = None
    year: datetime.year = None
    semester: str = None
    start_date: datetime.date = None
    end_date: datetime.date = None


@dataclass
class Group:
    name: str = None
    course: int = None
    education_step: str = None


@dataclass
class Lesson:
    study_form: str = None
    date: datetime.date = None
    day: str = None
    number: str = None
    start_time: datetime.time = None
    title: str = None
    teacher: str = None
    type_: str = None
    classroom: str = None
