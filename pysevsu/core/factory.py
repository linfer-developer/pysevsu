"""Main pipeline module for processing educational schedule data.

This module orchestrates the entire data processing workflow, from fetching
schedule metadata from the university website to parsing Excel files and
optionally normalizing the extracted data into structured class objects.

The pipeline handles resource management, thread pooling, and provides
flexible configuration for different processing needs.
"""

import asyncio
import os
import aiohttp
from typing import Any, Coroutine, Dict, Optional, AsyncIterator
from concurrent.futures import ThreadPoolExecutor
from pysevsu.models.schemas import Class
from pysevsu.pysevsu.core._normalizer import normalize_a_unit_of_data
from pysevsu.core._engine import Producer, consumer


class Pipeline:
    """Main processing pipeline for educational schedule data.

    Orchestrates the complete workflow:
    1. Fetches schedule metadata from the university website
    2. Downloads Excel files with rate limiting
    3. Parses Excel content
    4. Optionally normalizes data into structured Class objects

    The pipeline uses async/await for I/O operations and ThreadPoolExecutor
    for CPU-bound parsing tasks, providing efficient concurrent processing.

    Example:
        >>> pipeline = Pipeline(request_limit=10)
        >>> async for data in pipeline.run(normalization=True, STUDY_FORM="Очная"):
        ...     print(data.week, data.group)
    """

    def __init__(
        self,
        request_limit: int = 20,
        request_timeout: int = 15,
        request_delay: int = 0,
        broken_requests_size: int = 20,
        max_workers: Optional[int] = None,
        queue_size: Optional[int] = None,
    ) -> None:
        """Initialize the pipeline with configuration parameters.

        Args:
            request_limit: Maximum number of concurrent HTTP requests.
            request_timeout: HTTP request timeout in seconds.
            request_delay: Delay between initiating requests (seconds).
            broken_requests_size: Maximum consecutive failures before aborting.
            max_workers: Maximum number of thread pool workers for parsing.
                Defaults to CPU count if not specified.
            queue_size: Maximum size of the internal async queue.
                If 0 or None, queue is unbounded.
        """
        self.request_limit = request_limit
        self.request_timeout = request_timeout
        self.request_delay = request_delay
        self.broken_requests_size = broken_requests_size
        self.max_workers = max_workers if max_workers else os.cpu_count()
        self.queue_size = queue_size
        self.connection_errors: Optional[Dict[str, Exception]] = None

    async def _run_without_normalization(
        self, **kwargs: Any
    ) -> AsyncIterator[Dict[object, Any]]:
        """Run the pipeline without data normalization.

        This internal method handles the core processing workflow, yielding
        raw dictionary data from the Excel files.

        Args:
            **kwargs: Filter criteria passed to the producer.

        Yields:
            Raw dictionary data from parsed Excel files.
        """
        queue = asyncio.Queue(maxsize=self.queue_size or 0)

        async with aiohttp.ClientSession() as aiohttp_session:
            with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
                producer: Producer = Producer(
                    aiohttp_session=aiohttp_session,
                    request_limit=self.request_limit,
                    request_timeout=self.request_timeout,
                    thread_pool=pool,
                    queue=queue,
                )
                producer_task: Coroutine = asyncio.create_task(producer.start(**kwargs))

                async for data in consumer(queue):
                    yield data

                await producer_task
                await queue.join()

                self.connection_errors = producer.connection_errors

    async def run(
        self, normalization: bool = True, **kwargs: Any
    ) -> AsyncIterator[Dict[object, Any] | Class]:
        """Run the pipeline with optional data normalization.

        Args:
            normalization: If True, normalize raw data into Class objects.
                If False, yield raw dictionary data.
            **kwargs: Filter criteria for schedule entries.
                Common filters include:
                - STUDY_FORM: "Очная", "Заочная", etc.
                - SEMESTER: "1", "2", etc.
                - INSTITUTE: Institute name

        Yields:
            If normalization=True: Class objects with structured attributes.
            If normalization=False: Raw dictionary data from Excel files.

        Example:
            >>> # Process only full-time students
            >>> async for class_obj in pipeline.run(STUDY_FORM="Очная"):
            ...     process_class(class_obj)
        """
        if not normalization:
            async for data in self._run_without_normalization(**kwargs):
                yield data
        else:
            async for data in self._run_without_normalization(**kwargs):
                yield normalize_a_unit_of_data(data)
