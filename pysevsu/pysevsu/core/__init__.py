"""Core package for schedule processing.

Provides parsers for Excel schedules and the website scraper,
as well as the asynchronous processing pipeline.
"""

__version__ = "0.1.0"
__author__ = "Mayorov O. Yu."

from pysevsu.core.excel_parser import ExcelFile
from pysevsu.core.website_parser import Parser, get_schedule_content, get_content_excel_link
from pysevsu.core.pipeline import generate, generate_objs

__all__ = [
    "ExcelFile",
    "Parser",
    "get_schedule_content",
    "get_content_excel_link",
    "generate",
]
