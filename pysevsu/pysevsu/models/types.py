from typing import Dict, Any, Optional
from pysevsu.models.enums import ScheduleSource, WeekFields, LessonFields


WebsiteData = Dict[ScheduleSource, Optional[Any]]
WeekData = Dict[WeekFields, Optional[Any]]
LessonData = Dict[LessonFields, Optional[Any]]
