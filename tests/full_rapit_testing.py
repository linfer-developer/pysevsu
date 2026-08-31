import time
import asyncio
from pysevsu import Pipeline


async def test():
    count: int = 0
    start_time = time.perf_counter()
    async with Pipeline(
        requests_limit=20,
        request_timeout=15,
        max_workers=8,
    ) as pipeline:
        try:
            async for class_ in pipeline.run(return_objects=True):
                if class_.group.name == "ИС/б-24-1-о" and (class_.subgroup == 1 or not class_.subgroup):
                    print(class_.date, class_.number, class_.name, class_.teacher.fullname)
        finally:
            end_time = time.perf_counter()
            execution_time = end_time - start_time
            print(
                f"Обработано {count} элементов за {execution_time:.4f} секунд"
            )


if __name__ == "__main__":
    asyncio.run(test())
