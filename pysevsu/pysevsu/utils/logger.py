import logging
import functools
import time
from typing import Callable, Any

ENABLE_LOGGING = True
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s"
)


def logger(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not ENABLE_LOGGING:
            return func(*args, **kwargs)

        arg_str = f"args={args}, kwargs={kwargs}"
        logging.info(f"Вызов функции: {func.__name__} | {arg_str}")
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            duration = end_time - start_time
            logging.info(
                f"Завершена: {func.__name__} | Результат: {result} | "
                f"Время: {duration:.4f} сек."
            )
            return result
        except Exception as e:
            logging.error(f"Ошибка в {func.__name__}: {e}", exc_info=True)
            raise e

    return wrapper
