"""Command line interface for PageBinder."""

from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path
from typing import Iterable

from .render import compile_urls_to_pdf


LOGGER = logging.getLogger(__name__)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a list of web pages into a single PDF while preserving layout and links.",
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to a text file containing one URL per line.",
    )
    parser.add_argument(
        "output_file",
        type=Path,
        help="Path where the combined PDF will be written.",
    )
    parser.add_argument(
        "--wait-until",
        choices=["load", "domcontentloaded", "networkidle"],
        default="networkidle",
        help="Event to wait for before capturing each page. Defaults to 'networkidle'.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="Maximum number of seconds to wait for each page to load. Defaults to 60 seconds.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging output.",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def load_urls(input_path: Path) -> list[str]:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file {input_path} does not exist")

    urls: list[str] = []
    for line in input_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        urls.append(stripped)

    if not urls:
        raise ValueError("The input file does not contain any URLs")

    return urls


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(message)s")

    urls = load_urls(args.input_file)
    LOGGER.info("Rendering %s pages...", len(urls))

    try:
        asyncio.run(
            compile_urls_to_pdf(
                urls=urls,
                output_path=args.output_file,
                wait_until=args.wait_until,
                timeout=args.timeout,
            )
        )
    except Exception as exc:  # pragma: no cover - defensive top-level guard
        LOGGER.error("Failed to render pages: %s", exc)
        return 1

    LOGGER.info("PDF written to %s", args.output_file)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
