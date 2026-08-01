import io


class TextExtractionError(RuntimeError):
    pass


def _extract_pdf(data: bytes) -> str:
    from pypdf import PdfReader

    try:
        reader = PdfReader(io.BytesIO(data))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:  # noqa: BLE001 — surfaced as a clean extraction error
        raise TextExtractionError(f"Could not read PDF file: {exc}") from exc
    return "\n".join(pages).strip()


def _extract_docx(data: bytes) -> str:
    import docx

    try:
        document = docx.Document(io.BytesIO(data))
        paragraphs = [p.text for p in document.paragraphs]
    except Exception as exc:  # noqa: BLE001 — surfaced as a clean extraction error
        raise TextExtractionError(f"Could not read DOCX file: {exc}") from exc
    return "\n".join(paragraphs).strip()


def extract_text(data: bytes, filename: str) -> str:
    if not data:
        raise TextExtractionError("The uploaded file is empty.")

    lower_name = (filename or "").lower()

    if lower_name.endswith(".pdf"):
        text = _extract_pdf(data)
    elif lower_name.endswith(".docx"):
        text = _extract_docx(data)
    elif lower_name.endswith(".txt"):
        try:
            text = data.decode("utf-8", errors="ignore").strip()
        except Exception as exc:  # noqa: BLE001
            raise TextExtractionError(f"Could not read text file: {exc}") from exc
    else:
        raise TextExtractionError("Unsupported file type. Please upload a .pdf, .docx, or .txt file.")

    if not text:
        raise TextExtractionError("No readable text could be extracted from this file.")

    return text
