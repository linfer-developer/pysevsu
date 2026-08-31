"""Предоставляет публичные интерфейсы для реализации итеративных парсеров
веб-ресурса и документов электронных таблиц Microsoft Excel, организует
взаимосвязь сетевого клиента со сбором данных из источников в модуле
module:`engine` .

Рекомендуемые импорты:
:class:`CorruptedExcelFileError`,
:class:`UnstableNetworkConnection`,
:class:`WebsiteIterator`,
:class:`ExcelIterator`,
:func:`create_network_client`,
:func:`create_engine`,
"""

from typing import Any as Any
from .exceptions import CorruptedExcelFileError as CorruptedExcelFileError
from .exceptions import UnstableNetworkConnection as UnstableNetworkConnection
from .interfaces import RequestPolicy as RequestPolicy
from .interfaces import AsyncQueue as AsyncQueue
from .interfaces import MixedQueue as MixedQueue
from .interfaces import ScheduleStructureIteratorProtocol as WebsiteIterator
from .interfaces import ExcelIteratorProtocol as ExcelIterator
from .engine import Executor as Executor
from .engine import Downloader as ExcelFileDownloader
from .engine import Processor as ExcelFileProcessor
from .engine import Runner as Engine
from .network import Client as NetworkClient


def create_network_client(
    base_url: str,
    session: Any,
    request_limit: int,
    request_timeout: int,
    request_delay: int,
) -> NetworkClient:
    """Создает асинхронный сетевой клиент системы."""
    return NetworkClient(
        base_url=base_url,
        session=session,
        request_policy=RequestPolicy(
            limit=request_limit,
            timeout=request_timeout,
            delay=request_delay,
        ),
    )


def create_engine(
    client: NetworkClient,
    web_iterator: WebsiteIterator,
    downloader_queue: AsyncQueue,
    executor: Executor,
    excel_iterator_model: type[ExcelIterator],
    processor_chunk_size: int,
    processor_queue: MixedQueue,
    filters: dict[Any, Any] | None = None,
) -> Engine:
    """Создает движок системы."""
    return Engine(
        processor=ExcelFileProcessor(
            executor=executor,
            queue=processor_queue,
            iterator_model=excel_iterator_model,
            chunk_size=processor_chunk_size,
            filters=filters,
        ),
        downloader=ExcelFileDownloader(
            client=client,
            iterator=web_iterator,
            queue=downloader_queue,
            filters=filters,
        ),
    )


__all__ = [
    "ExcelFileDownloader",
    "ExcelFileProcessor",
    "CorruptedExcelFileError",
    "UnstableNetworkConnection",
    "WebsiteIterator",
    "ExcelIterator",
    "create_engine",
    "create_network_client"
]
