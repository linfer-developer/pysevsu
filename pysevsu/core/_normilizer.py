from typing import Dict, Tuple, Any, List
from pysevsu.core.excel_file_handler import ClassAttribute
from pysevsu.core.website_structure_handler import ScheduleStructure
from pysevsu.models.schemas import *
from datetime import datetime, date, time
import re



def extract_course_number_and_degree(
    group: str,
) -> Tuple[int, Degree]:
    degree_mapping: Dict[str, str] = {
        "б": Degree.BACHELOR,
        "с": Degree.SPECIALIST,
        "м": Degree.MASTER,
        "а": Degree.POSTGRADUATE,
    }
    degree: Degree = degree_mapping.get(group.split("/")[1][0])
    course: int = int(group.split("-")[2])
    return degree, course


def get_the_associated_study_form(study_form: str) -> StudyForm:
    if not study_form:
        return None
    return StudyForm(study_form.strip())


def extract_groupname(raw_groupname: str) -> str:
    if not raw_groupname:
        raise ValueError("Parametr raw_groupname cannot be None.")
    groupname: str = raw_groupname.split(":")[-1].strip()
    return groupname


def extract_subgroup_number(subgroup: str) -> int:
    if not subgroup:
        return None
    subgroup_number: int = int(subgroup.split()[1])
    return subgroup_number


def get_the_associated_day(day: str) -> StudyWeekday:
    try:
        return StudyWeekday(day)
    except:
        return None


def create_date_object(raw_date: str) -> Tuple[date, int]:
    if isinstance(raw_date, date):
        return raw_date, raw_date.year
    match = re.search(r"(\d+)\D+(\d+)\D+(\d+)", raw_date)
    if match:
        day: str
        month: str
        year: str
        day, month, year = match.groups()
        date_object: date = datetime.strptime(
            f"{int(day):02d}.{int(month):02d}.{int(year):04d}", "%d.%m.%Y"
        )
        return date_object.date(), date_object.year


def extract_classname_and_teacher(raw_class: str) -> Tuple[str, str, int]:
    if not raw_class:
        raise ValueError("Parametr raw_class cannot be None.")

    class_info_splited: List[str] = raw_class.split(",")
    classname: str = None
    subgroup: int = None
    teacher: str = class_info_splited[-1].strip()

    if raw_class.startswith("подгр"):
        classname: str = ", ".join(class_info_splited[1:-1]).strip()
        match = re.search(r"\d+", raw_class)
        if match:
            subgroup = int(match.group())
    else:
        classname: str = ", ".join(class_info_splited[0:-1]).strip()

    return classname, teacher, subgroup


def create_time_object(raw_time: str) -> datetime.time:
    return datetime.strptime(raw_time, "%H:%M").time()


def extract_week_number(week: str) -> int:
    if not week:
        raise ValueError("Parametr week cannot be None.")
    match = re.search(r"\d+", week)
    if not match:
        raise ValueError("No numbers found in week string.")
    return int(match.group())


def normalize_a_unit_of_data(data: Dict[str, Any]) -> Class:
    degree: Degree
    course: int
    study_form: StudyForm
    groupname: str
    subgroup: int
    week_number: StudyWeekday
    date_object: date
    year: int
    classname: str
    teacher: str
    time_object: time
    day: StudyWeekday

    try:
        study_form = get_the_associated_study_form(data[ScheduleStructure.STUDY_FORM])
        groupname = extract_groupname(data[ClassAttribute.GROUP])
        degree, course = extract_course_number_and_degree(groupname)
        day = get_the_associated_day(data[ClassAttribute.DAY])
        week_number = extract_week_number(data[ClassAttribute.WEEK])
        date_object, year = create_date_object(data[ClassAttribute.DATE])
        time_object = create_time_object(data[ClassAttribute.START_TIME])
        classname, teacher_name, subgroup = extract_classname_and_teacher(
            data[ClassAttribute.CLASS]
        )
    except Exception as e:
        print(e, data)
        raise

    group: Group = None
    week: Week = None
    teacher: Teacher = None
    classroom: Classroom = None
    class_: Class = None

    if degree is None:
        group = Group(name=groupname, institute=data[ScheduleStructure.INSTITUTE])
    else:
        group = Group(
            name=groupname,
            institute=data[ScheduleStructure.INSTITUTE],
            course=course,
            degree=degree,
        )

    week = Week(
        number=week_number, year=year, semester=data[ScheduleStructure.SEMESTER]
    )

    if teacher_name:
        teacher = Teacher(fullname=teacher_name)

    if classname:
        classroom = Classroom(cipher=data[ClassAttribute.CLASSROOM])

    class_: Class = Class(
        number=int(data[ClassAttribute.NUMBER]),
        date=date_object,
        time=time_object,
        name=classname,
        study_form=study_form,
        day=day,
        group=group,
        week=week,
        teacher=teacher if teacher else None,
        room=classroom if classroom else None,
        type_=data[ClassAttribute.TYPE],
        subgroup=subgroup,
    )

    return class_
