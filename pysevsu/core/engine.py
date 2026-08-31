"""Асинхронный и многопоточный механизм конвейерной обработки расписания.

Модуль реализует архитектуру «Производитель — Потребитель», разделенную на два
этапа выполнения:

1. Загрузка данных :class:`Downloader`: Асинхронное получение файлов
   по сети с ограничением интенсивности запросов.
2. Обработка данных :class:`Processor`: Разбор документов и извлечение
   записей в пуле вычислительных потоков.
3. Координация :class:`Runner`: Связывание этапов загрузки и разбора
   через очереди данных с предоставлением итогового потока записей.
"""

from asyncio import Semaphore
from asyncio import Task
from asyncio import create_task
from asyncio import gather
from typing import Any
from typing import AsyncIterator
from concurrent.futures import Executor
from concurrent.futures import Future
from .interfaces import AsyncQueue
from .interfaces import ExcelIteratorProtocol
from .interfaces import MixedQueue
from .interfaces import ScheduleStructureIteratorProtocol
from .interfaces import _ClientProtocol
from .interfaces import _DownloaderProtocol
from .interfaces import _ProcessorProtocol
from .interfaces import _RunnerProtocol
from .._utils.logger import logger

_STOP = object()  # Единое остановочное значение для очередей


class Downloader(_DownloaderProtocol):
    """Асинхронный компонент загрузки Excel файлов расписания из сети.

    Планирует одновременные HTTP-запросы на основе элементов структуры сайта,
    ограничивая их количество семафором.

    Использует шаблон «Производитель — Потребитель» с общей асинхронной очередью
    для скачивания файлов на странице. Сетевой клиент получает содержимое
    ресурса с активацией итеративного парсера веб-ресурса. Для каждого
    полученного URL-адреса документов выполняется GET-запрос с последующим
    размещением байтов в очереди с контекстом их расположения. Потребитель
    перебирает все имеющиеся данные, генеративно возвращая информацию
    фиксированными единицами.
    """

    def __init__(
        self,
        client: _ClientProtocol,
        iterator: ScheduleStructureIteratorProtocol,
        queue: AsyncQueue,
        filters: dict[Any, Any] | None = None,
    ) -> None:
        """Инициализирует параметры загрузчика.

        :param client: Сетевой клиент для выполнения запросов.
        :param iterator: Итератор структуры ресурсов веб-сайта.
        :param queue: Асинхронная очередь для полученных файлов.
        :param filters: Критерии ранней фильтрации.
        """
        self.client = client
        self.iterator = iterator
        self.queue = queue
        self.filters = filters

    @logger(enabled=False, signature="Downloader.", ignore_result=True)
    async def run(
        self,
    ) -> AsyncIterator[tuple[bytes, dict[Any, Any]]]:
        """Предоставляет асинхронный поток загруженных файлов.

        :yields: Кортеж из двоичных данных файла и словаря метаданных.
        """
        _downloader_background: Task = create_task(self._run_background())
        try:
            async for excel, data in self._stream():
                yield excel, data
        finally:
            await _downloader_background

    async def _stream(self) -> AsyncIterator[Any]:
        """Извлекает элементы из очереди до получения маркера завершения."""
        while True:
            item = await self.queue.get()
            try:
                if item is _STOP:
                    return
                yield item
            finally:
                self.queue.task_done()

    async def _done(self) -> None:
        """Отправляет сигнал завершения обработки в очередь результатов."""
        await self.queue.put(_STOP)

    async def _add_file_to_queue(
        self,
        end_url: str,
        raw_website_data: dict[Any, Any],
        semaphore: Semaphore,
    ) -> None:
        """Загрузка отдельного файла и размещение его в очередь.

        :param end_url: Относительный или абсолютный адрес файла.
        :param raw_website_data: Метаданные контекста ресурса.
        :param semaphore: Средство ограничения количества одновременных запросов.
        """
        async with semaphore:
            file_content: str | bytes | None = await self.client.request(
                end_url=end_url,
                return_="bytes",
                number_network_exceptions=0,
                reset_network_exception_counter=False,
            )

        if file_content:
            await self.queue.put((file_content, raw_website_data))

    async def _run_background(self) -> None:
        """Запуск одновременной загрузки целевых файлов."""
        semaphore: Semaphore = Semaphore(self.client.request_policy.limit)

        tasks: list[Task] = [
            create_task(
                self._add_file_to_queue(
                    end_url=url,
                    raw_website_data=data,
                    semaphore=semaphore,
                )
            )
            for url, data in self.iterator.with_filters(self.filters)
        ]

        try:
            await gather(*tasks)
        finally:
            await self._done()


class Processor(_ProcessorProtocol):
    """Многопоточный компонент анализа файлов Excel.

    Делегирует задачи разбора документов пулу потоков для исключения
    блокировки цикла событий.

    Проводит итеративный парсинг файлов ЭТ в новых независимых потоках,
    насыщая очередь :class:`MixedQueue` информацией с соединением контекста
    расположения и расписания. Когда исходные данные заканчиваются, дается
    команда на остановку очереди.
    """

    def __init__(
        self,
        executor: Executor,
        queue: MixedQueue,
        iterator_model: type[ExcelIteratorProtocol],
        chunk_size: int = 50,
        filters: dict[Any, Any] | None = None,
    ) -> None:
        """Инициализирует параметры обработчика документов.

        :param executor: Исполнитель задач в отдельном пуле потоков.
        :param queue: Потокобезопасная очередь результатов.
        :param iterator_model: Класс итератора разбора Excel-файлов.
        :param chunk_size: Размер пакета отправляемых записей.
        :param filters: Критерии фильтрации элементов расписания.
        """
        self.executor = executor
        self.queue = queue
        self.chunk_size = chunk_size
        self.filters = filters

        self._create_iterator = iterator_model
        self._website_data: dict[Any, Any] | None = None
        self._futures: list[Future] = []

    @logger(enabled=False, signature="Processor.", ignore_params=True)
    def run(
        self, file: bytes, website_data: dict[Any, Any] | None = None
    ) -> None:
        """Передает задачу разбора файла на выполнение в пул потоков.

        :param file: Двоичные данные файла Excel.
        :param website_data: Метаданные контекста файла.
        """
        excel: ExcelIteratorProtocol = self._create_iterator(file)
        if website_data:
            future: Future = self.executor.submit(
                self._add_data_to_queue,
                excel,
                website_data,
            )
        else:
            future: Future = self.executor.submit(
                self._add_data_to_queue,
                excel,
            )
        self._futures.append(future)

    @logger(enabled=False, signature="Processor.")
    def get_errors(self) -> None:
        """Проверяет результаты выполнения задач в потоках и транслирует исключения.

        :raises Exception: Возникает при сбое обработки внутри любого из потоков.
        """
        for future in self._futures:
            future.result()

    @logger(enabled=False, signature="Processor.")
    def done(self) -> None:
        """Отправляет сигнал завершения обработки в очередь результатов."""
        self.queue.sync_q.put(_STOP)

    @logger(enabled=False, signature="Processor.", ignore_result=True)
    async def stream(
        self,
    ) -> AsyncIterator[dict[Any, Any]]:
        """Извлекает элементы из очереди до получения маркера завершения."""
        while True:
            item = await self.queue.async_q.get()
            try:
                if item is _STOP:
                    break
                for excel_data in item:
                    yield excel_data
            finally:
                self.queue.async_q.task_done()

    def _add_data_to_queue(
        self,
        excel: ExcelIteratorProtocol,
        website_data: dict[Any, Any] | None = None,
    ) -> None:
        """Выполняет разбор файла в рабочем потоке и формирует пакеты данных.

        :param excel: Экземпляр итератора файла Excel.
        :param website_data: Метаданные контекста документа.
        """
        chunk: list[dict[Any, Any]] = []
        with excel as iterator:
            for excel_data in iterator.with_filters(self.filters):
                if website_data:
                    chunk.append(excel_data | website_data)
                else:
                    chunk.append(excel_data)

                if len(chunk) >= self.chunk_size:
                    self.queue.sync_q.put(chunk)
                    chunk = []

        if chunk:
            self.queue.sync_q.put(chunk)


class Runner(_RunnerProtocol):
    """Координатор процессов загрузки и обработки расписания.

    Начинает фоновое скачивание Excel-документов с помощью загрузчика и
    запускает обработчик для независимого сбора и слияния информации.
    Количество воркеров фиксировано, поэтому при полной загрузке новые
    файлы электронных таблиц ожидают освобождения ресурсов. Одновременно
    с процессом наполнения очереди запускается ее итерация с возвратом данных
    вызываемому компоненту.
    """

    def __init__(
        self,
        processor: _ProcessorProtocol,
        downloader: _DownloaderProtocol,
    ) -> None:
        """Инициализирует компоненты и очереди конвейера.

        :param processor: Компонент многопоточной обработки файлов.
        :param downloader: Компонент асинхронной загрузки.
        """
        self.processor = processor
        self.downloader = downloader

    @logger(enabled=False, signature="Runner.")
    async def _hande_files(self) -> None:
        try:
            async for excel_file, website_data in self.downloader.run():
                self.processor.run(file=excel_file, website_data=website_data)
        finally:
            self.processor.done()
            self.processor.get_errors()

    @logger(enabled=False, signature="Runner.")
    async def start(
        self,
    ) -> AsyncIterator[dict[Any, Any]]:
        """Запускает полный цикл и предоставляет поток итоговых записей.

        :yields: Объединенный словарь метаданных и полей записи расписания.
        """
        task: Task = create_task(self._hande_files())
        async for data in self.processor.stream():
            yield data
        await task
