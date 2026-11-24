from pathlib import Path

try:
    from weasyprint import HTML
except (ImportError, OSError) as exc:
    msg = "PDF output is required, but WeasyPrint or its dependencies could not be loaded."
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
