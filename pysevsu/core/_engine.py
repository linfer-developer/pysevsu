"""Asynchronous producer-consumer pipeline for processing educational
schedule data.

This module implements a concurrent data processing pipeline that:
1. Fetches schedule metadata from the university website
2. Downloads Excel files in parallel with rate limiting
3. Parses Excel files using a thread pool
4. Yields structured schedule data through a consumer interface

The architecture uses async/await for I/O operations and ThreadPoolExecutor
for CPU-bound Excel parsing to achieve optimal performance.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Coroutine, Dict, List, AsyncIterator, Optional, Union
import aiohttp
from pysevsu.core.website_structure_handler import Parser
from pysevsu.core.network import get_content_excel_link, get_schedule_content
from pysevsu.core.excel_file_handler import File

_STOP = object()  # Sentinel object to signal queue completion


def _parse_excel(
    content: bytes, filters: Optional[Dict[Any, Any]] = None
) -> List[Dict[str, Any]]:
    """Parse Excel file content in a separate thread.

    This function is designed to be run in a ThreadPoolExecutor to avoid
    blocking the asyncio event loop with CPU-bound parsing operations.

    Args:
        content: Binary content of the Excel file.
        filters: Optional filters to apply during parsing.

    Returns:
        List of dictionaries containing parsed schedule entries.
    """
    excel_file: File = File(content)
    with excel_file:
        return list(excel_file.iter(**filters))


class Producer:
    """Producer component that fetches and processes schedule data.

    Manages concurrent HTTP requests, Excel parsing, and queues results
    for consumer processing. Handles rate limiting, request delays, and
    error recovery for network-related issues.
    """

    def __init__(
        self,
        aiohttp_session: aiohttp.ClientSession,
        thread_pool: ThreadPoolExecutor,
        queue: asyncio.Queue,
        request_limit: int = 30,
        request_timeout: int = 15,
        request_delay: int = 0,
        broken_requests_size=20,
    ) -> None:
        """Initialize the producer with configuration parameters.

        Args:
            aiohttp_session: Shared aiohttp session for HTTP requests.
            thread_pool: Thread pool for Excel parsing operations.
            queue: Asyncio queue for passing data to consumer.
            request_limit: Maximum number of concurrent HTTP requests.
            request_timeout: HTTP request timeout in seconds.
            request_delay: Delay between initiating requests (seconds).
            broken_requests_size: Maximum consecutive failures before aborting.
        """
        self.connection_errors: Dict[str, Exception] = {}
        self.request_limit = request_limit
        self.request_timeout = request_timeout
        self.request_delay = request_delay
        self.broken_requests_size = broken_requests_size
        self._session = aiohttp_session
        self._queue = queue
        self._thread_pool = thread_pool

    async def start(self, **kwargs: Any) -> None:
        """Start the producer processing pipeline.

        Fetches the main schedule page, extracts Excel file links, downloads
        them with rate limiting, parses their content, and queues the results.

        Args:
            **kwargs: Filter criteria passed to the parser (e.g., STUDY_FORM="Очная").
        """
        try:
            await self._handle_website_files(**kwargs)
        finally:
            await self._queue.put(_STOP)

    async def _handle_website_files(self, **kwargs: Any) -> None:
        """Process all Excel files from the website.

        Fetches the schedule page, extracts Excel file metadata, and initiates
        concurrent downloads and parsing tasks.

        Args:
            **kwargs: Filter criteria for schedule entries.
        """
        semaphore: asyncio.Semaphore = asyncio.Semaphore(self.request_limit)
        website_content: str = await get_schedule_content(
            self.request_timeout, self._session
        )
        parser: Parser = Parser(website_content)
        tasks: List[Coroutine] = []

        for url, data in parser.iter(**kwargs):
            task: Coroutine = asyncio.create_task(
                self._request_a_file(data, url, semaphore, **kwargs)
            )
            tasks.append(task)

        await asyncio.gather(*tasks)

    async def _request_a_file(
        self,
        data: Dict[Any, Any],
        end_url: str,
        semaphore: asyncio.Semaphore,
        **kwargs: Any,
    ) -> None:
        """Download a single Excel file with concurrency control.

        Args:
            data: Metadata for the schedule entry.
            end_url: URL suffix for the Excel file.
            semaphore: Semaphore for controlling concurrent requests.
            **kwargs: Filter criteria for Excel parsing.

        Raises:
            RuntimeError: If too many consecutive network errors occur.
        """
        async with semaphore:
            try:
                file_content: Optional[bytes] = await get_content_excel_link(
                    timeout=self.request_timeout,
                    session=self._session,
                    end_url=end_url,
                )
                await asyncio.sleep(self.request_delay)
            except (aiohttp.ClientError, asyncio.TimeoutError) as error:
                self.connection_errors[end_url] = error
                if len(self.connection_errors) >= self.broken_requests_size:
                    raise RuntimeError(
                        "Unstable network connection: Check access to the web "
                        "resource or network settings."
                    ) from error
                print(f"Warning: query error in engine (line 76): {error}")
                return

        if file_content:
            await self._handle_excel_file(file_content, data, **kwargs)

    async def _handle_excel_file(
        self,
        file_content: Optional[bytes],
        data: Dict[str, Any],
        **kwargs: Any,
    ) -> None:
        """Parse Excel file and queue the results.

        Offloads Excel parsing to a thread pool to avoid blocking the
        event loop, then enqueues each parsed entry for consumer processing.

        Args:
            file_content: Binary content of the Excel file.
            data: Metadata associated with this schedule file.
            **kwargs: Filter criteria for Excel parsing.
        """

        loop: asyncio.AbstractEventLoop = asyncio.get_running_loop()
        excel_files_data: List[Dict[str, Any]] = await loop.run_in_executor(
            self._thread_pool, _parse_excel, file_content, kwargs
        )
        for excel_file_data in excel_files_data:
            data.update(excel_file_data)
            await self._queue.put(data.copy())


async def consumer(queue: asyncio.Queue) -> AsyncIterator[Dict[Any, Any] | object]:
    """Consumer parsed schedule data from the queue.

    Async generator that yields items from the queue until the sentinel
    object is received, indicating no more data is available.

    Args:
        queue: Asyncio queue containing parsed schedule entries.

    Yields:
        Dictionary containing schedule data or the sentinel object.

    Example:
        >>> async for data in consumer(queue):
        ...     if data == _STOP:
        ...         break
        ...     process_schedule_entry(data)
    """
    while True:
        data: Union[Dict[Any, Any], object] = await queue.get()
        if data == _STOP:
            queue.task_done()
            break
        yield data
        queue.task_done()
