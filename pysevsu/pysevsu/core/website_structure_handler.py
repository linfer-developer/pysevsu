"""HTML parser module for extracting schedule metadata from university web pages.

This module provides functionality to parse HTML content from the university's
schedule system, extracting structured information about schedules including
institutes, study forms, semesters, and downloadable Excel file links.
"""

from typing import Iterator, Dict, Any
from enum import StrEnum
from lxml.html import fromstring


class ScheduleStructure(StrEnum):
    """Enumeration of CSS classes and HTML elements used in the schedule
    page structure.

    These values correspond to specific HTML elements and CSS classes that
    contain the schedule metadata and downloadable file links.
    """

    STUDY_FORM = "schedule-table__column-name"
    INSTITUTE = "h4"
    SEMESTER = "document-link__group-name"
    DEGREE_COURSE = "document-link__name"
    EXCEL_FILE = "a"


class Parser:
    """HTML parser for extracting schedule metadata and Excel file links.

    Parses the university schedule page HTML and extracts structured data
    about available schedules, including institute names, study forms,
    semesters, degree courses, and associated Excel file download URLs.
    """

    def __init__(self, content: str) -> None:
        self._tree: Any = fromstring(content)

    def iter_all(self) -> Iterator[Dict[ScheduleStructure, Any]]:
        """Iterate over all schedule entries found in the HTML.

        Parses the HTML tree and yields each schedule entry with its
        associated metadata and Excel file URL.

        Yields:
            Tuple of (excel_file_url, metadata_dict) where metadata_dict
            contains all ScheduleStructure attributes.
        """
        _xpath_expr: str = (
            f"//*[local-name()='{ScheduleStructure.INSTITUTE}' or "
            f"local-name()='{ScheduleStructure.EXCEL_FILE}' or "
            f"contains(@class, '{ScheduleStructure.STUDY_FORM}') or "
            f"contains(@class, '{ScheduleStructure.SEMESTER}') or "
            f"contains(@class, '{ScheduleStructure.DEGREE_COURSE}')]"
        )
        url: str = None
        data: Dict[ScheduleStructure, Any] = {item: None for item in ScheduleStructure}

        for element in self._tree.xpath(_xpath_expr):
            tag: Any = element.tag
            if tag == ScheduleStructure.INSTITUTE:
                data[ScheduleStructure.INSTITUTE] = element.text_content().strip()
            elif tag == ScheduleStructure.EXCEL_FILE:
                url = element.get("href")

            tag_classes: Any = element.get("class", "").split()
            if tag_classes:
                if ScheduleStructure.STUDY_FORM in tag_classes:
                    data[ScheduleStructure.STUDY_FORM] = element.text_content().strip()
                elif ScheduleStructure.SEMESTER in tag_classes:
                    data[ScheduleStructure.SEMESTER] = element.text_content().strip()
                elif ScheduleStructure.DEGREE_COURSE in tag_classes:
                    data[ScheduleStructure.DEGREE_COURSE] = (
                        element.text_content().strip()
                    )
                    yield url, data.copy()

    def iter_only_excel_files(self) -> Iterator[Dict[str, str]]:
        """Iterate over schedule entries that have Excel files.

        Filters out entries without Excel files and excludes administrative
        documents (those which starting with "Распоряжение").

        Yields:
            Tuple of (excel_file_url, metadata_dict) for valid schedule entries.
        """
        for url, data in self.iter_all():
            if (
                not data[ScheduleStructure.DEGREE_COURSE]
                .strip()
                .startswith("Распоряжение")
            ):
                yield url, data

    def iter(self, **kwargs) -> Iterator[Dict[str, str]]:
        """Iterate over Excel file entries with optional filtering.

        Provides filtering capability by metadata attributes. Only yields
        entries where all specified filter criteria match.

        Args:
            **kwargs: Filter criteria as key-value pairs where keys match
                     ScheduleStructure enum values (e.g., STUDY_FORM="Очная").

        Yields:
            Tuple of (excel_file_url, metadata_dict) that match all the filters.

        Example:
            >>> parser = Parser(html_content)
            >>> for url, data in parser.iter(STUDY_FORM="Очная", SEMESTER="1"):
            ...     print(f"Downloading: {url}")
        """
        for url, data in self.iter_only_excel_files():
            if kwargs:
                filter_keys: set = set(kwargs.keys())
                data_keys: set = set(data.keys())
                intersect_keys: set = filter_keys.intersection(data_keys)
                if intersect_keys and any(
                    data[key] != kwargs[key] for key in intersect_keys
                ):
                    continue
            yield url, data
