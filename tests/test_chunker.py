from src.chunker import Chunk, split_text
from src.loader import Document


def test_split_text_basic():
    doc = Document(url="https://example.com", title="Test", content="A" * 1000)
    chunks = split_text(doc, chunk_size=500, overlap=100)
    assert len(chunks) >= 2
    assert all(isinstance(c, Chunk) for c in chunks)


def test_split_text_metadata():
    doc = Document(url="https://example.com/page", title="Test", content="A" * 600)
    chunks = split_text(doc, chunk_size=500, overlap=100)
    for i, chunk in enumerate(chunks):
        assert chunk.metadata["source_url"] == "https://example.com/page"
        assert chunk.metadata["chunk_index"] == i


def test_split_text_overlap():
    doc = Document(url="https://example.com", title="Test", content="ABCDEFGHIJ" * 100)
    chunks = split_text(doc, chunk_size=500, overlap=100)
    if len(chunks) >= 2:
        tail_of_first = chunks[0].text[-100:]
        head_of_second = chunks[1].text[:100]
        assert tail_of_first == head_of_second


def test_split_text_short_document():
    doc = Document(url="https://example.com", title="Test", content="Short text")
    chunks = split_text(doc, chunk_size=500, overlap=100)
    assert len(chunks) == 1
    assert chunks[0].text == "Short text"


def test_split_text_empty():
    doc = Document(url="https://example.com", title="Test", content="")
    chunks = split_text(doc, chunk_size=500, overlap=100)
    assert len(chunks) == 0
