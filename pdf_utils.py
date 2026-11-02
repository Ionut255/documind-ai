
from io import BytesIO
from pypdf import PdfReader


def extract_pdf_pages(uploaded_file):
    """Extract text from each page of a PDF."""
    pdf_reader = PdfReader(
        BytesIO(uploaded_file.getvalue())
    )

    pages = []

    for page_number, page in enumerate(
        pdf_reader.pages, start=1
    ):
        text = page.extract_text() or ""

        pages.append({
            "page_number": page_number,
            "text": text
        })

    return pages


def split_text_into_chunks(
    pages,
    chunk_size=120,
    overlap=25
):
    """Split PDF pages into overlapping text chunks."""

    if chunk_size <= 0 or not 0 <= overlap < chunk_size:
        raise ValueError("Invalid chunk settings.")

    chunks = []
    step = chunk_size - overlap

    for page in pages:
        words = page["text"].split()

        for start in range(0, len(words), step):
            chunk_words = words[start:start + chunk_size]

            chunks.append({
                "page_number": page["page_number"],
                "text": " ".join(chunk_words)
            })

            if start + chunk_size >= len(words):
                break

    return chunks
