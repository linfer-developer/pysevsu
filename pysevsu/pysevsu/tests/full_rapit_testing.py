import time
import asyncio
from pysevsu.core import generate_objs


async def test():
    count: int = 0
    start_time = time.perf_counter()
    try:
        async for data in generate_objs():
            count += 1
    finally:
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        print(f"Обработано {count} элементов за {execution_time:.4f} секунд")

if __name__ == "__main__":
    asyncio.run(test())