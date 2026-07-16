"""Schedule Web Scraper
____________________

This module provides asynchronous functions to fetch an HTML page containing
links to Excel schedule files and to download the Excel files themselves.
It parses the HTML using :class:`bs4.BeautifulSoup` to extract structured
metadata (study form, institute, semester, course, file URL) and yields only
those records that correspond to Excel files (i.e., not PDFs).

Constants ``TIMEOUT``, ``SCHEDULE_URL``, and ``URL`` are imported from
:mod:`core.website_config` and must be configured appropriately for the target
website.

Example usage::

    import aiohttp
    async with aiohttp.ClientSession() as session:
        html = await get_schedule_content(session)
        page = Page(html)
        for item in page.parse_only_excel_files():
            print(item)
            excel_bytes = await get_content_excel_link(session, item['file_url'])
            # process Excel bytes
"""

import aiohttp
from enum import Enum
from bs4 import BeautifulSoup, Tag
from typing import Dict, List, Iterator
from pysevsu.core.website_config import TIMEOUT, SCHEDULE_URL, URL
from pysevsu.models.enums import ScheduleSource
from pysevsu.models.types import WebsiteData


async def get_schedule_content(session: aiohttp.ClientSession) -> str:
    """Retrieve the HTML content of the main schedule page.

    :param session: An aiohttp client session to use for the request.
    :return: The raw HTML string of the schedule page.
    :raises aiohttp.ClientResponseError: If the response status is not 2xx.
    :raises asyncio.TimeoutError: If the request exceeds ``TIMEOUT``.
    """
    async with session.get(SCHEDULE_URL, timeout=TIMEOUT) as response:
        response.raise_for_status()
        return await response.text()


async def get_content_excel_link(session: aiohttp.ClientSession, end_url: str) -> bytes:
    """Download an Excel file given its relative URL suffix.

    The full URL is constructed as ``URL + end_url``.

    :param session: An aiohttp client session.
    :param end_url: The relative path (e.g., ``"/path/file.xlsx"``).
    :return: The binary content of the Excel file.
    :raises aiohttp.ClientResponseError: If the response status is not 2xx.
    :raises asyncio.TimeoutError: If the request exceeds ``TIMEOUT``.
    """
    url = URL + end_url
    async with session.get(url, timeout=TIMEOUT) as response:
        response.raise_for_status()
        return await response.read()


class _HTMLStructureConfig(str, Enum):
    """Internal enumeration of HTML class names and tag names used to locate
    relevant elements on the schedule page.

    Values:
        HEAD: CSS class for the study form header.
        LIST_TITLE: Tag name of the institute title (``h4``).
        INLIST_TITLE: CSS class for the semester indicator.
        FILENAME: CSS class for the course name (file description).
        FILE_URL: Tag name of the link element (``a``) containing the file URL.
        PDF_FILENAME: Prefix string that identifies PDF entries (to be excluded).
    """

    HEAD = "schedule-table__column-name"
    LIST_TITLE = "h4"
    INLIST_TITLE = "document-link__group-name"
    FILENAME = "document-link__name"
    FILE_URL = "a"
    PDF_FILENAME = "Распоряжение"


class Parser:
    """Parses the schedule HTML page and extracts structured records.

    The parser relies on the hierarchical order of elements in the HTML:
    study form (``HEAD``) is followed by institute (``LIST_TITLE``), then
    optionally by semester (``INLIST_TITLE``), course name (``FILENAME``), and
    a link (``FILE_URL``). It yields a dictionary for each complete file entry.

    .. note::

       The parsing logic uses :meth:`bs4.BeautifulSoup.descendants` for
       simplicity, but this may be fragile due to deeply nested ``div``
       elements. A future refactor should consider using :meth:`find` or
       :meth:`find_all` with more precise selectors.

    :param content: The raw HTML string of the schedule page.
    :ivar _bs4: Parsed BeautifulSoup tree.
    """

    def __init__(self, content: str) -> None:
        self._bs4: BeautifulSoup = BeautifulSoup(content, "html.parser")

    @staticmethod
    def _text(tag: Tag) -> str:
        """Extract and strip the textual content of a BeautifulSoup ``Tag``.

        :param tag: A BeautifulSoup element.
        :return: Cleaned text.
        """
        return tag.get_text().strip()

    def parse_all(self) -> Iterator[WebsiteData]:
        """Generator that yields all schedule entries found on the page,
        regardless of file type (Excel or PDF).

        The method walks the entire HTML tree using ``descendants`` and
        accumulates values in a dictionary. The fields are populated in the
        following order: HEAD, LIST_TITLE, FILE_URL, INLIST_TITLE, FILENAME.
        A dictionary is yielded as soon as a ``FILENAME`` element is
        encountered, representing a complete record.

        :yields: Dictionaries containing keys from :class:`DataFormat`.
        """
        data: WebsiteData = ScheduleSource.get_dict()

        # TODO: Rewrite the parser's logic
        # It seemed that `descendants` would be the best solution, since it is
        # a generator. The problem turned out to be the complete structural
        # rendering of the HTML page, including redundant nested `div` elements.
        # An implementation using `find` is proposed due to its lower-level
        # implementation, but this point requires further clarification.
        # The code is a working prototype, so this assumption has been made.
        for el in self._bs4.descendants:
            # The hierarchy is as follows: HEAD -> LIST_TITLE -> FILE_URL,
            # INLIST_TITLE -> FILENAME. HEAD and LIST_TITLE are always present,
            # whereas FILE_URL, INLIST_TITLE, and FILENAME may not exist in
            # the site’s HTML structure.
            if not hasattr(el, "get"):
                continue

            tag: str = el.name
            if _HTMLStructureConfig.LIST_TITLE == tag:
                data[ScheduleSource.LIST_TITLE] = self._text(el)
            elif _HTMLStructureConfig.FILE_URL == tag:
                data[ScheduleSource.FILE_URL] = el.get("href")

            classnames: List[str] = el.get("class")
            if not classnames:
                continue

            if _HTMLStructureConfig.HEAD in classnames:
                data[ScheduleSource.HEAD] = self._text(el)
            elif _HTMLStructureConfig.INLIST_TITLE in classnames:
                data[ScheduleSource.INLIST_TITLE] = self._text(el)
            elif _HTMLStructureConfig.FILENAME in classnames:
                # FILENAME exists only if the entire hierarchy leading up to it
                # is present. Elements that are not related to FILENAME cannot
                # appear in the dictionary, so the current conditional block
                # is structurally sound, even though it appears fragile.
                data[ScheduleSource.FILENAME] = self._text(el)
                yield data.copy()

    def parse_only_excel_files(self) -> Iterator[WebsiteData]:
        """Yield only those entries that represent Excel files (i.e., not PDFs).

        Entries whose ``FILENAME`` field starts with the string defined in
        :attr:`_HTMLStructureConfig.PDF_FILENAME` are skipped.

        :yields: Dictionaries of Excel schedule records.
        :rtype: Iterator[Dict[str, str]]

        .. warning::
           This method relies on the filename prefix to distinguish file types.
           If the website changes its naming convention, this filter may break.
        """
        # TODO: I strongly advise against trying such unreliable methods—unless you’re desperate ;)
        for data in self.parse_all():
            if not data[ScheduleSource.FILENAME].startswith(
                _HTMLStructureConfig.PDF_FILENAME
            ):
                yield data
