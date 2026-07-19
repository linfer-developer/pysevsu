"""Core package for schedule processing.

Provides parsers for Excel schedules and the website scraper,
as well as the asynchronous processing pipeline.
"""

__version__ = "0.1.0"
__author__ = "Mayorov O. Yu."

from pysevsu.core.excel_file_handler import File
from pysevsu.core.website_structure_handler import Parser
from pysevsu.core.network import get_schedule_content, get_content_excel_link
from pysevsu.core.factory import Pipeline

__all__ = [
    "File",
    "Parser",
    "get_schedule_content",
    "get_content_excel_link",
    "Pipeline"
]
