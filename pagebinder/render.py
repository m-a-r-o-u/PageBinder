"""Utilities for rendering web pages to PDF using Playwright."""

from __future__ import annotations
import logging
from io import BytesIO
from pathlib import Path
from typing import Iterable

from playwright.async_api import Browser, Error, async_playwright
from pypdf import PdfMerger

LOGGER = logging.getLogger(__name__)

DEFAULT_MARGIN = {
    "top": "0.5in",
    "bottom": "0.5in",
    "left": "0.5in",
    "right": "0.5in",
}


async def _render_single_page(
    browser: Browser,
    url: str,
    *,
    wait_until: str,
    timeout: float,
) -> bytes:
    LOGGER.info("Fetching %s", url)
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until=wait_until, timeout=timeout * 1000)
        pdf_bytes = await page.pdf(
            print_background=True,
            display_header_footer=False,
            margin=DEFAULT_MARGIN,
        )
        LOGGER.debug("Rendered %s (%s bytes)", url, len(pdf_bytes))
        return pdf_bytes
    finally:
        await page.close()


async def compile_urls_to_pdf(
    *,
    urls: Iterable[str],
    output_path: Path,
    wait_until: str = "networkidle",
    timeout: float = 60.0,
) -> None:
    """Render each URL to PDF and combine them into ``output_path``.

    Parameters
    ----------
    urls:
        Iterable of URL strings to fetch.
    output_path:
        Path to the resulting PDF file.
    wait_until:
        Playwright navigation option that determines when a page is considered loaded.
    timeout:
        Maximum number of seconds to wait for each page load.
    """

    pdf_merger = PdfMerger()
    output_path = Path(output_path)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        try:
            for url in urls:
                try:
                    pdf_bytes = await _render_single_page(
                        browser,
                        url,
                        wait_until=wait_until,
                        timeout=timeout,
                    )
                except Error as playwright_error:
                    raise RuntimeError(f"Playwright failed to render {url}: {playwright_error}") from playwright_error

                with BytesIO(pdf_bytes) as buffer:
                    pdf_merger.append(buffer)
        finally:
            await browser.close()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as output_file:
        pdf_merger.write(output_file)
    pdf_merger.close()

    LOGGER.info("Created %s", output_path)
