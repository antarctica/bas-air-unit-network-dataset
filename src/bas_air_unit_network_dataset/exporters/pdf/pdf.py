from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

try:
    from weasyprint import HTML
except (ImportError, OSError) as exc:
    msg = "Cannot load WeasyPrint or its dependencies for PDF outputs."
    raise RuntimeError(msg) from exc


class PdfReport:
    """
    PDF report.

    Simple exporter for saving pre-generated HTML content as a PDF report.
    """

    def __init__(self, content: str) -> None:
        self._content = content

    def dump(self, path: Path) -> None:
        """Write report contents."""
        pdf = HTML(string=self._content)
        with path.open(mode="wb") as file:
            pdf.write_pdf(file)
