"""Schedule Pipeline
_________________________

This module implements an asynchronous producer-consumer pipeline that:

1. Fetches an HTML schedule page.
2. Extracts links to Excel files.
3. Downloads each Excel file (with a concurrency limit).
4. Parses Excel content into structured dictionaries using a process pool to
   avoid blocking the event loop.
5. Yields the resulting records via an async generator.

The pipeline exposes a single public entry point, :func:`generate`, which is
designed to be used as an async iterator. A :class:`_Producer` manages
downloading and parsing, feeding results into an :class:`asyncio.Queue`. The
:func:`_consumer` function turns queue items into an async generator that
drives the iteration.

Constants and imports from sibling modules:

- :data:`core.website_config.TIMEOUT`, :data:`SCHEDULE_URL`, :data:`URL`
- :mod:`core.website_parser` provides HTML parsing and download helpers.
- :mod:`core.excel_file_parser` provides :class:`ExcelFile` for parsing Excel
  workbooks.

.. note::

   The ``core.logger`` import is reserved for future logging.

Usage example::

    async for record in generate(request_limit=5):
        # Each record is a dictionary combining website metadata and
        # lesson data from the Excel file.
        print(record)
"""

import asyncio
import aiohttp
import os
from typing import Any, Coroutine, Dict, List, Optional, AsyncGenerator, Tuple
from concurrent.futures import ThreadPoolExecutor
from pysevsu.core.website_parser import Parser, get_schedule_content, get_content_excel_link
from pysevsu.core.excel_parser import ExcelFile
from pysevsu.models.enums import ScheduleSource, WeekFields, LessonFields
from pysevsu.models.schedule import Week, Group, Lesson

_STOP = object()  # Sentinel value used to signal the end of the queue to the consumer


def _parse_excel(content: bytes) -> List[Dict[str, Any]]:
    """Parse a raw Excel file into a list of lesson dictionaries.

    This function is defined at module level so it can be pickled and
    executed in a :class:`~concurrent.futures.ThreadPoolExecutor`.

    :param content: The binary content of the Excel file.
    :return: A list of structured lesson dictionaries as produced by
             :meth:`ExcelFile.parse`.
    """
    excel_file: ExcelFile = ExcelFile(content)
    with excel_file:
        return list(excel_file.parse())


class _Producer:
    """Orchestrates fetching and parsing of Excel schedule files.

    Downloads files concurrently (respecting ``request_limit``) and offloads
    CPU‑intensive parsing to a :class:`~concurrent.futures.ThreadPoolExecutor`.

    :param aiohttp_session: The aiohttp session to use for HTTP requests.
    :param queue: The asyncio queue into which parsed records are placed.
    :param request_limit: Maximum number of concurrent HTTP requests.
    :param max_workers: Number of worker processes for the pool. Defaults to
                        ``os.cpu_count()``.
    :ivar connection_errors: Dictionary mapping failed file URLs to the
                             exception that occurred during download.
    :vartype connection_errors: Dict[str, Exception]
    """

    def __init__(
        self,
        aiohttp_session: aiohttp.ClientSession,
        queue: asyncio.Queue,
        request_limit: int = 5,
        max_workers: Optional[int] = None,
    ) -> None:
        self.request_limit = request_limit
        self.max_workers = max_workers if max_workers else os.cpu_count()
        self.connection_errors: Dict[str, Exception] = {}
        self._session = aiohttp_session
        self._queue = queue
        self._thread_pool = None

    async def start(self) -> None:
        """Start the producer.

        Creates a :class:`~concurrent.futures.ThreadPoolExecutor`, triggers
        the download and parsing pipeline, and finally pushes the :data:`_STOP`
        sentinel into the queue to signal completion.
        """
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            self._thread_pool = pool
            try:
                await self.parse_files_to_website()
            finally:
                await self._queue.put(_STOP)

    async def parse_files_to_website(self) -> None:
        """Fetch the schedule page, extract Excel file links, and create tasks to
        download and parse each file.

        Each task is limited by an :class:`asyncio.Semaphore` to control
        concurrency.
        """
        semaphore = asyncio.Semaphore(self.request_limit)
        website_content: str = await get_schedule_content(self._session)
        parser = Parser(website_content)
        tasks: List[Coroutine] = []

        for data in parser.parse_only_excel_files():
            task: Coroutine = asyncio.create_task(
                self.handle_excel_file(
                    data=data.copy(),
                    excel_file_url=data[ScheduleSource.FILE_URL],
                    semaphore=semaphore,
                )
            )
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def handle_excel_file(
        self,
        data: Dict[str, Any],
        excel_file_url: str,
        semaphore: asyncio.Semaphore,
    ) -> None:
        """Download an Excel file and parse its content in a process pool.

        :param data: The metadata dictionary from the website (will be
                     enriched with lesson data from the Excel file).
        :param excel_file_url: Relative URL of the Excel file.
        :param semaphore: Semaphore to limit concurrent downloads.
        """
        async with semaphore:
            try:
                file_content: bytes = await get_content_excel_link(
                    session=self._session, end_url=excel_file_url
                )
                if not file_content:
                    return
            except aiohttp.client_exceptions.ClientPayloadError as error:
                self.connection_errors[excel_file_url] = error
                return
            except aiohttp.client_exceptions.ClientOSError as error:
                self.connection_errors[excel_file_url] = error
                return

        loop = asyncio.get_running_loop()
        parsed_list: List[Dict[str, Any]] = await loop.run_in_executor(
            self._thread_pool,
            _parse_excel,
            file_content,
        )

        for excel_file_data in parsed_list:
            data.update(excel_file_data)
            await self._queue.put(data.copy())


async def _consumer(queue: asyncio.Queue) -> AsyncGenerator[Any, None]:
    """Async generator that yields items from the queue until the :data:`_STOP`
    sentinel is received.

    :param queue: The queue from which to consume items.
    :yields: Queued data items (excluding the sentinel).
    """
    while True:
        data: Optional[Any] = await queue.get()
        if data == _STOP:
            queue.task_done()
            break
        yield data
        queue.task_done()



def _create_objects_from_dict(raw_data: Dict[str, Any]) -> Tuple[Week, Group, Lesson]:
    return (
        Week(
            number=raw_data[WeekFields.TITLE],
            year=raw_data[WeekFields.YEAR],
            semester=raw_data[ScheduleSource.INLIST_TITLE],
            start_date=raw_data[WeekFields.START_DATE],
            end_date=raw_data[WeekFields.END_DATE],
        ),
        Group(
            name=raw_data[LessonFields.GROUPNAME],
            course=raw_data[ScheduleSource.FILENAME],
            education_step=...,
        ),
        Lesson(
            study_form=raw_data[ScheduleSource.LIST_TITLE],
            date=raw_data[LessonFields.DATE],
            day=raw_data[LessonFields.DAY],
            number=raw_data[LessonFields.NUMBER],
            start_time=raw_data[LessonFields.START_TIME],
            title=raw_data[LessonFields.TITLE],
            teacher=raw_data[LessonFields.TEACHER],
            type_=raw_data[LessonFields.TYPE],
            classroom=raw_data[LessonFields.CLASSROOM],
        )
    )



async def generate(
    request_limit: int = 20,
    max_workers: Optional[int] = None,
    queue_size: Optional[int] = None,
) -> AsyncGenerator[Any, None]:
    """Entry point for the schedule pipeline.

    Yields parsed lesson records (dictionaries) one by one. After all records
    have been yielded, the final item is the ``connection_errors`` dictionary
    from the producer, which maps URLs that failed to download to their
    respective exceptions.

    :param request_limit: Maximum number of simultaneous HTTP requests.
    :param max_workers: Number of worker processes for CPU‑intensive parsing.
                        Passed to :class:`_Producer`.
    :param queue_size: Maximum size of the internal queue. ``0`` (default) means
                       unlimited.
    :yields: Either a lesson dictionary or, at the end, the
             ``connection_errors`` dictionary.
    """
    queue = asyncio.Queue(maxsize=queue_size or 0)

    async with aiohttp.ClientSession() as aiohttp_session:
        producer = _Producer(aiohttp_session, queue, request_limit, max_workers)
        producer_task = asyncio.create_task(producer.start())

        async for data in _consumer(queue):
            yield data

        await producer_task
        await queue.join()

        # TODO: It's better to think of another way
        yield producer.connection_errors


async def generate_objs(
    request_limit: int = 20,
    max_workers: Optional[int] = None,
    queue_size: Optional[int] = None,
) -> AsyncGenerator[Any, None]:
    """Entry point for the schedule pipeline.

    Yields parsed lesson records (dictionaries) one by one. After all records
    have been yielded, the final item is the ``connection_errors`` dictionary
    from the producer, which maps URLs that failed to download to their
    respective exceptions.

    :param request_limit: Maximum number of simultaneous HTTP requests.
    :param max_workers: Number of worker processes for CPU‑intensive parsing.
                        Passed to :class:`_Producer`.
    :param queue_size: Maximum size of the internal queue. ``0`` (default) means
                       unlimited.
    :yields: Either a lesson dictionary or, at the end, the
             ``connection_errors`` dictionary.
    """
    queue = asyncio.Queue(maxsize=queue_size or 0)

    async with aiohttp.ClientSession() as aiohttp_session:
        producer = _Producer(aiohttp_session, queue, request_limit, max_workers)
        producer_task = asyncio.create_task(producer.start())

        async for data in _consumer(queue):
            yield _create_objects_from_dict(data)

        await producer_task
        await queue.join()
