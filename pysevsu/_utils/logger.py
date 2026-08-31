import logging
import functools
import time
from typing import Callable, Any

ENABLE_LOGGING = True
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s"
)


def logger(
    enabled: bool = True,
    ignore_result: bool = False,
    ignore_params: bool = False,
    signature: str | None = None,
) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not enabled:
                return func(*args, **kwargs)

            arg_str = f"args={args}, kwargs={kwargs}"
            if ignore_params:
                logging.info(
                    f"Вызов функции: {signature}{func.__name__}"
                )
            else:
                logging.info(
                    f"Вызов функции: {signature}{func.__name__} | {arg_str}"
                )
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                end_time = time.perf_counter()
                duration = end_time - start_time
                if ignore_result:
                    logging.info(
                        f"Завершена: {signature}{func.__name__} | "
                        f"Время: {duration:.4f} сек."
                    )
                else:
                    logging.info(
                        f"Завершена: {signature}{func.__name__} "
                        f"| Результат: {result} | "
                        f"Время: {duration:.4f} сек."
                    )
                return result
            except Exception as e:
                logging.error(
                    f"Ошибка в {signature}{func.__name__}: {e}", exc_info=True
                )
                raise e

        return wrapper

    return decorator
