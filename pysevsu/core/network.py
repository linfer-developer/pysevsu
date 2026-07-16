"""Async HTTP client module for fetching educational schedule data.

This module provides asynchronous HTTP client functionality for retrieving
schedule information and Excel files from the university's schedule system.
It handles the base URL configuration and provides type-safe HTTP operations
with proper error handling.
"""

from typing import Final
from aiohttp import ClientSession

# Base URL configuration for the university's schedule system
URL: Final[str] = "https://www.sevsu.ru"
SCHEDULE_URL: Final[str] = f"{URL}/univers/shedule/"


async def get_schedule_content(timeout: int, session: ClientSession) -> str:
    """Fetch the main schedule page content.

    Retrieves the HTML content of the schedule page, which typically contains
    links to downloadable Excel schedule files.

    Args:
        timeout: HTTP request timeout in seconds.
        session: Active aiohttp client session for making the request.

    Returns:
        HTML content of the schedule page as a string.

    Raises:
        aiohttp.ClientError: If the HTTP request fails.
        aiohttp.ClientResponseError: If the response status is not 2xx.
    """
    async with session.get(SCHEDULE_URL, timeout=timeout) as response:
        response.raise_for_status()
        return await response.text()


async def get_content_excel_link(
    timeout: int, session: ClientSession, end_url: str
) -> bytes:
    """Fetch an Excel file from the schedule system.

    Downloads a binary Excel file using the provided endpoint URL suffix.
    The complete URL is constructed by concatenating the base URL with
    the provided endpoint.

    Args:
        timeout: HTTP request timeout in seconds.
        session: Active aiohttp client session for making the request.
        end_url: URL suffix/path for the Excel file endpoint.

    Returns:
        Binary content of the Excel file as bytes.

    Raises:
        aiohttp.ClientError: If the HTTP request fails.
        aiohttp.ClientResponseError: If the response status is not 2xx.
    """
    url: str = URL + end_url
    async with session.get(url, timeout=timeout) as response:
        response.raise_for_status()
        return await response.read()
