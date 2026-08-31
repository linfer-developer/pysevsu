# models

Пакет предоставляет модели организации выходных данных библиотеки.

## schemas

Модели схемы данных учебного расписания.

Модуль содержит структуры данных для представления ключевых доменных сущностей
расписания: академических групп ([`Group`](#pysevsu.models.schemas.Group)), учебных недель
([`Week`](#pysevsu.models.schemas.Week)), преподавателей ([`Teacher`](#pysevsu.models.schemas.Teacher)), аудиторий
([`Classroom`](#pysevsu.models.schemas.Classroom)) и учебных занятий ([`Class`](#pysevsu.models.schemas.Class)).

### *class* Group(name: str, institute: str, course: int | None = None, degree: [Degree](#pysevsu.models.enums.Degree) | None = None)

Базовые классы: `object`

Академическая группа.

#### name *: str*

#### institute *: str*

#### course *: int | None* *= None*

#### degree *: [Degree](#pysevsu.models.enums.Degree) | None* *= None*

### *class* Week(number: int, year: int, semester: str | None = None, start_date: str | None = None, end_date: str | None = None)

Базовые классы: `object`

Учебная неделя.

#### number *: int*

#### year *: int*

#### semester *: str | None* *= None*

#### start_date *: str | None* *= None*

#### end_date *: str | None* *= None*

### *class* Teacher(fullname: str)

Базовые классы: `object`

Преподаватель.

#### fullname *: str*

### *class* Classroom(cipher: str)

Базовые классы: `object`

Учебная аудитория.

#### cipher *: str*

### *class* Class(number: int, date: date, time: time, name: str, group: [Group](#pysevsu.models.schemas.Group), week: [Week](#pysevsu.models.schemas.Week), study_form: [StudyForm](#pysevsu.models.enums.StudyForm) | None = None, day: [StudyWeekday](#pysevsu.models.enums.StudyWeekday) | None = None, room: [Classroom](#pysevsu.models.schemas.Classroom) | None = None, teacher: [Teacher](#pysevsu.models.schemas.Teacher) | None = None, type_: str | None = None, subgroup: int | None = None)

Базовые классы: `object`

Учебное занятие.

Агрегирует сведения о времени и месте проведения занятия, преподавателе,
академической группе и дисциплине.

#### number *: int*

#### date *: date*

#### time *: time*

#### name *: str*

#### group *: [Group](#pysevsu.models.schemas.Group)*

#### week *: [Week](#pysevsu.models.schemas.Week)*

#### study_form *: [StudyForm](#pysevsu.models.enums.StudyForm) | None* *= None*

#### day *: [StudyWeekday](#pysevsu.models.enums.StudyWeekday) | None* *= None*

#### room *: [Classroom](#pysevsu.models.schemas.Classroom) | None* *= None*

#### teacher *: [Teacher](#pysevsu.models.schemas.Teacher) | None* *= None*

#### type_ *: str | None* *= None*

#### subgroup *: int | None* *= None*

## enums

Модуль предоставляет возможные варианты данных для некоторых полей
классов-участников схемы данных, основываясь на порядке проведения занятий
в Севастопольском государственном университете.

### *class* StudyForm(\*values)

Базовые классы: `StrEnum`

Перечисление отражает все возможные виды расписания с веб-ресурса
«Расписание» Севастопольского государственного университета.

#### FULL_TIME_CLASSES *= 'Расписание учебных занятий ОФО, ОЗФО'*

#### CORRESPONDENCE_CLASSES *= 'Расписание экзаменационной и установочной сессии ЗФО'*

#### FULL_TIME_CERTIFICATION *= 'Расписание промежуточной аттестации ОФО, ОЗФО'*

### *class* StudyWeekday(\*values)

Базовые классы: `StrEnum`

Перечисление отражает все учебные дни (6-ти дневная учебная неделя).

#### MONDAY *= 'Понедельник'*

#### TUESDAY *= 'Вторник'*

#### WEDNESDAY *= 'Среда'*

#### THURSDAY *= 'Четверг'*

#### FRIDAY *= 'Пятница'*

#### SATURDAY *= 'Суббота'*

### *class* Degree(\*values)

Базовые классы: `StrEnum`

Все ступени образования РФ, по которым могут обучаться студенты.

#### BACHELOR *= 'Бакалавриат'*

#### SPECIALIST *= 'Специалитет'*

#### MASTER *= 'Магистратура'*

#### POSTGRADUATE *= 'Аспирантура'*

## raw

Ключи сырых данных источников.

### *class* WebsiteDataKey(\*values)

Базовые классы: `StrEnum`

Ключи атрибутов контекста структуры веб-страницы расписания.

#### STUDY_FORM *= 'study_form'*

#### INSTITUTE *= 'institute'*

#### SEMESTER *= 'semester'*

#### DEGREE_COURSE *= 'degree_course'*

### *class* ExcelDataKey(\*values)

Базовые классы: `StrEnum`

Ключи атрибутов элементов расписания из файлов Excel.

#### WEEK *= 'week'*

#### GROUP *= 'group'*

#### SUBGROUP *= 'subgroup'*

#### DAY *= 'day'*

#### DATE *= 'date'*

#### NUMBER *= 'number'*

#### START_TIME *= 'start_time'*

#### CLASS *= 'classname'*

#### TYPE *= 'type'*

#### CLASSROOM *= 'classroom'*
