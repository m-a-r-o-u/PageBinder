# PageBinder

PageBinder is a command-line utility that takes a list of web pages and compiles them into a single PDF document while preserving layout, backgrounds, and links. This is ideal for preparing presentation PDFs that match the look of the original pages.

## Features

- Uses the Chromium browser via [Playwright](https://playwright.dev/python/) to accurately capture each page.
- Preserves links and styling, including backgrounds.
- Accepts a text file containing one URL per line.
- Produces a single combined PDF in the order provided.

## Installation

PageBinder requires Python 3.10 or newer.

```bash
pip install .
playwright install chromium
```

The second command downloads the Chromium browser that Playwright uses for rendering.

## Usage

Create a text file (e.g. `pages.txt`) with one URL per line. Lines beginning with `#` are treated as comments and ignored.

```
https://doku.lrz.de/ai-systems-11484278.html
https://doku.lrz.de/1-access-10746642.html
https://doku.lrz.de/2-compute-10746641.html
https://doku.lrz.de/3-storage-10746646.html
```

Then run PageBinder, passing the list file and the desired output PDF path:

```bash
pagebinder pages.txt presentation.pdf
```

Optional flags:

- `--wait-until {load,domcontentloaded,networkidle}`: Choose when a page is considered fully loaded (default: `networkidle`).
- `--timeout SECONDS`: Maximum seconds to wait for each page load (default: 60).
- `--verbose`: Enable detailed logging output.

The resulting `presentation.pdf` will contain each page in order with live hyperlinks intact.

## Development

To install dependencies in editable mode:

```bash
pip install -e .
playwright install chromium
```

## License

This project is released under the MIT License.
