import time
import asyncio
from pysevsu.core import Pipeline
from pysevsu.core.excel_file_handler import ClassAttribute
from pysevsu.core.website_structure_handler import ScheduleStructure


async def test():
    count: int = 0
    start_time = time.perf_counter()
    pipeline = Pipeline(max_workers=8, request_limit=5, request_delay=0.2)
    try:
        async for class_ in pipeline.run(
            normalization=True,
            # **{
            #     ScheduleStructure.STUDY_FORM: "Расписание промежуточной аттестации ОФО, ОЗФО",
            #     ScheduleStructure.INSTITUTE: "ВТШ «СПИ». Факультет информационных технологий",
            #     ScheduleStructure.DEGREE_COURSE: "2 курс Бакалавриат",
            #     ScheduleStructure.SEMESTER: "II семестр",
            #     ClassAttribute.WEEK: "уч.н. 43",
            # }
        ):
            print(class_.number, class_.date, class_.name, class_.type_)
            count += 1
    finally:
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"Обработано {count} элементов за {execution_time:.4f} секунд")
        print(pipeline.connection_errors)


if __name__ == "__main__":
    asyncio.run(test())
