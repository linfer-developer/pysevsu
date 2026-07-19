"""Data models for educational schedule information.

This module defines dataclasses that represent the core data structures
for educational schedule information, including groups, weeks, teachers,
classrooms, and individual class entries. These models provide a type-safe
way to handle schedule data throughout the application.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from pysevsu.models.enums import Degree, StudyWeekday, StudyForm


@dataclass(frozen=False)
class Group:
    """Represents a student group with its academic attributes.

    Attributes:
        name: Full group name (e.g., "ИВТ-б-о-201")
        institute: Name of the institute/department
        course: Course year (1-6 typically), optional
        degree: Academic degree level, optional
    """

    name: str
    institute: str
    course: Optional[int] = None
    degree: Optional[Degree] = None


@dataclass(frozen=False)
class Week:
    """Represents an academic week with its temporal metadata.

    Attributes:
        number: Week number within the semester (1-18 typically)
        year: Calendar year of the week
        semester: Semester identifier (e.g., "1", "2"), optional
        start_date: Week start date as string, optional
        end_date: Week end date as string, optional
    """

    number: int
    year: datetime.year
    semester: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@dataclass(frozen=False)
class Teacher:
    """Represents a teacher/instructor.

    Attributes:
        fullname: Teacher's full name (surname, initials typically)
    """

    fullname: str


@dataclass(frozen=False)
class Classroom:
    """Represents a classroom or lecture hall.

    Attributes:
        cipher: Room identifier (e.g., "A-301", "Main Hall")
    """

    cipher: str


@dataclass(frozen=False)
class Class:
    """Represents a single class/session in the schedule.

    This is the primary data model containing all information about a
    specific class session including timing, location, and participants.

    Attributes:
        number: Sequential class number within the schedule
        date: Calendar date of the class
        time: Start time of the class
        name: Subject/course name
        group: Student group attending the class
        week: Academic week information
        study_form: Study form (full-time, correspondence, etc.), optional
        day: Day of the week, optional
        room: Classroom where the class takes place, optional
        teacher: Instructor for this class, optional
        type_: Type of class (lecture, lab, seminar, etc.), optional
        subgroup: Subgroup number for split groups, optional
    """

    number: int
    date: datetime.date
    time: datetime.time
    name: str
    group: Group
    week: Week
    study_form: Optional[StudyForm] = None
    day: Optional[StudyWeekday] = None
    room: Optional[Classroom] = None
    teacher: Optional[Teacher] = None
    type_: Optional[str] = None
    subgroup: Optional[int] = None
