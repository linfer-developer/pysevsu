"""Интерфейсы и базовые типы данных системы обработки расписания.

Модуль определяет публичные протоколы взаимодействия компонентов
очередей (:class:`AsyncQueue`, :class:`ThreadSafeQueue`, :class:`MixedQueue`) и
итераторов источников данных (:class:`ExcelIteratorProtocol`, 
:class:`ScheduleStructureIteratorProtocol`) .
"""

from io import BytesIO
from dataclasses import dataclass
from typing import Any
from typing import AsyncIterator
from typing import Iterator
from typing import Protocol
from typing import TypeVar
from typing import AsyncGenerator


@dataclass
class RequestPolicy:
    """Параметры ограничения сетевых запросов.

    :param limit: Предельное количество одновременных запросов.
    :param timeout: Время ожидания ответа в секундах.
    :param delay: Задержка между повторными запросами в секундах.
    """

    limit: int = 30
    timeout: int = 15
    delay: int = 0

    def __post_init__(self) -> None:
        if self.limit < 1 or self.timeout < 0 or self.delay < 0:
            raise ValueError


T = TypeVar("T")


class AsyncQueue[T](Protocol):
    async def put(self, item: T) -> None: ...
    async def get(self) -> T: ...
    async def join(self) -> None: ...
    def task_done(self) -> None: ...


class ThreadSafeQueue[T](Protocol):
    def put(
        self, item: T, block: bool = True, timeout: float | None = None
    ) -> None: ...
    def get(self, block: bool = True, timeout: float | None = None) -> T: ...
    def join(self) -> None: ...
    def task_done(self) -> None: ...


class MixedQueue[T](Protocol):
    @property
    def async_q(self) -> AsyncQueue[T]: ...
    @property
    def sync_q(self) -> ThreadSafeQueue[T]: ...


class ExcelIteratorProtocol(Protocol):
    def __init__(self, content: bytes | BytesIO) -> None: ...
    def __enter__(self) -> "ExcelIteratorProtocol": ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...
    def __iter__(self) -> Iterator[dict[Any, Any]]: ...

    def with_filters(
        self, filters: dict[Any, Any] | None = None
    ) -> "ExcelIteratorProtocol": ...


class ScheduleStructureIteratorProtocol(Protocol):
    def __init__(self, content: str) -> None: ...
    def __iter__(self) -> Iterator[tuple[str, dict[Any, Any]]]: ...

    def with_filters(
        self, filters: dict[Any, Any] | None = None
    ) -> "ScheduleStructureIteratorProtocol": ...


class _ClientProtocol(Protocol):
    request_policy: RequestPolicy

    async def request(
        self,
        end_url: str | None,
        return_: str,
        number_network_exceptions: int,
        reset_network_exception_counter: bool,
    ) -> str | bytes | None: ...


class _DownloaderProtocol(Protocol):
    async def run(
        self,
    ) -> AsyncIterator[tuple[bytes, dict[Any, Any]]]:
        yield bytes(1), {1: None}


class _ProcessorProtocol(Protocol):
    async def stream(
        self,
    ) -> AsyncGenerator[dict[Any | Any, Any]]:
        yield {1: None}

    def run(
        self, file: bytes, website_data: dict[Any, Any]
    ) -> None: ...
    def get_errors(self) -> None: ...
    def done(self) -> None: ...


class _RunnerProtocol(Protocol):
    async def start(
        self,
    ) -> AsyncIterator[dict[Any, Any]]: ...
