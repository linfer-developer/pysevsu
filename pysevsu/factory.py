"""Фабричный модуль асинхронного конвейера обработки расписания.

Объединяет сетевое взаимодействие, разбор HTML-структуры, многопоточную
обработку книг Excel и формирование объектов моделей в рамках единого
асинхронного менеджера контекста.
"""

from asyncio import Queue as AsyncQueue
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from typing import AsyncIterator
from aiohttp import ClientSession
from janus import Queue as MixedQueue
from ._map import create_objects
from .models import Class
from .models import ExcelDataKey
from .models import WebsiteDataKey
from .sources import ExcelFileIterator
from .sources import WebsiteStructureIterator
from .core import Engine
from .core import NetworkClient
from .core import create_engine
from .core import create_network_client


class Pipeline:
    """Асинхронный менеджер контекста для управления конвейером обработки.

    Управляет жизненным циклом сетевых соединений, пула рабочих потоков
    и промежуточных очередей передачи данных.
    """

    def __init__(
        self,
        base_url: str = "https://www.sevsu.ru",
        request_timeout: int = 30,
        requests_limit: int = 15,
        requests_delay: int = 0,
        requests_queue_size: int = 0,
        thread_queue_size: int = 0,
        max_workers: int = 4,
        excel_processor_chunk_size: int = 50,
    ) -> None:
        """Инициализирует настройки выполнения и емкость буферов конвейера.

        :param base_url: Базовый адрес веб-ресурса.
        :param request_timeout: Предельное время ожидания ответа в секундах.
        :param requests_limit: Ограничение на количество одновременных запросов.
        :param requests_delay: Интервал задержки перед отправкой запроса в
                               секундах.
        :param requests_queue_size: Емкость асинхронной очереди загрузки.
        :param thread_queue_size: Емкость очереди связывания потоков.
        :param max_workers: Количество рабочих потоков исполнителя.
        :param excel_processor_chunk_size: Размер пакета обработанных записей.
        """
        self.base_url = base_url
        self.request_timeout = request_timeout
        self.requests_limit = requests_limit
        self.request_delay = requests_delay
        self.requests_queue_size = requests_queue_size
        self.thread_queue_size = thread_queue_size
        self.max_workers = max_workers
        self.excel_processor_chunk_size = excel_processor_chunk_size
        self._client: NetworkClient | None = None
        self._executor: ThreadPoolExecutor | None = None
        self._network_queue: AsyncQueue | None = None
        self._thread_queue: MixedQueue | None = None

    async def __aenter__(self) -> "Pipeline":
        """Инициализирует сетевые соединения, пул потоков и очереди."""
        self._client = create_network_client(
            base_url=self.base_url,
            session=ClientSession(),
            request_limit=self.requests_limit,
            request_timeout=self.request_timeout,
            request_delay=self.request_delay,
        )
        self._executor = ThreadPoolExecutor(self.max_workers)
        self._network_queue = AsyncQueue(self.requests_queue_size)
        self._thread_queue = MixedQueue(self.thread_queue_size)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Завершает сетевой сеанс и останавливает пул рабочих потоков."""
        if not self._executor or not self._client:
            raise AttributeError(
                """Невозможно закрыть контекстный менеджер: ошибка инициализации
                пула потоков или сетевого клиента."""
            )

        await self._client.session.close()
        self._executor.shutdown(wait=True, cancel_futures=False)

    async def run(
        self,
        return_objects: bool = True,
        filters: dict[WebsiteDataKey | ExcelDataKey, Any] | None = None,
    ) -> AsyncIterator[Class | dict[WebsiteDataKey | ExcelDataKey, Any]]:
        """Запускает полный цикл обработки расписания и предоставляет поток
        результатов.

        :param return_objects: Флаг преобразования словарей данных в объекты
                               моделей.
        :param filters: Критерии фильтрации записей.

        :yields: Элементы расписания в виде моделей или исходных словарей.
        """
        if (
            not self._client
            or not self._executor
            or not self._thread_queue
            or not self._network_queue
        ):
            raise AttributeError("Вызов вне контекстного менеджера невозможен.")

        _website_html: str | bytes | None = await self._client.request(
            end_url="/univers/shedule/",
            return_="text",
            number_network_exceptions=1,
            reset_network_exception_counter=True,
        )
        if not _website_html or not isinstance(_website_html, str):
            raise RuntimeError(f"Ожидался тип str, а не {type(_website_html)}.")
        
        _engine: Engine = create_engine(
            client=self._client,
            web_iterator=WebsiteStructureIterator(_website_html),
            downloader_queue=self._network_queue,
            executor=self._executor,
            processor_queue=self._thread_queue,
            excel_iterator_model=ExcelFileIterator,
            processor_chunk_size=self.excel_processor_chunk_size,
            filters=filters,
        )

        async for data in _engine.start():
            if return_objects:
                yield create_objects(data)
                continue
            yield data
