import tempfile
import os

import pytest

from src.chunker import Chunk
from src.vectorstore import VectorStore


@pytest.fixture
def tmp_persist_dir(tmp_path):
    """Provide a temporary directory for ChromaDB persistence."""
    return str(tmp_path / "chroma_test_db")


@pytest.fixture
def store(tmp_persist_dir):
    """Create a VectorStore instance with a temporary directory."""
    return VectorStore(persist_dir=tmp_persist_dir, collection_name="test_collection")


@pytest.fixture
def sample_chunks():
    """Create sample chunks for testing."""
    return [
        Chunk(text="Python is a programming language.", metadata={"source_url": "https://example.com/python", "chunk_index": 0}),
        Chunk(text="JavaScript runs in the browser.", metadata={"source_url": "https://example.com/js", "chunk_index": 0}),
        Chunk(text="Python is great for data science and machine learning.", metadata={"source_url": "https://example.com/python", "chunk_index": 1}),
    ]


class TestAddChunks:
    def test_add_chunks_stores_documents(self, store, sample_chunks):
        store.add_chunks(sample_chunks)
        count = store.collection.count()
        assert count == len(sample_chunks)

    def test_add_chunks_empty_list(self, store):
        store.add_chunks([])
        assert store.collection.count() == 0

    def test_add_chunks_deduplication(self, store, sample_chunks):
        """Adding the same chunks twice should not duplicate them (upsert behavior)."""
        store.add_chunks(sample_chunks)
        store.add_chunks(sample_chunks)
        assert store.collection.count() == len(sample_chunks)


class TestSearch:
    def test_search_returns_relevant_results(self, store, sample_chunks):
        store.add_chunks(sample_chunks)
        results = store.search("Python programming", top_k=2)
        assert len(results) == 2
        # The Python-related chunks should be ranked higher
        texts = [r["text"] for r in results]
        assert any("Python" in t for t in texts)

    def test_search_result_structure(self, store, sample_chunks):
        store.add_chunks(sample_chunks)
        results = store.search("Python", top_k=1)
        assert len(results) == 1
        result = results[0]
        assert "text" in result
        assert "metadata" in result
        assert "distance" in result

    def test_search_top_k(self, store, sample_chunks):
        store.add_chunks(sample_chunks)
        results = store.search("programming", top_k=1)
        assert len(results) == 1

    def test_search_empty_collection(self, store):
        results = store.search("anything")
        assert results == []


class TestReset:
    def test_reset_clears_collection(self, store, sample_chunks):
        store.add_chunks(sample_chunks)
        assert store.collection.count() == len(sample_chunks)
        store.reset()
        assert store.collection.count() == 0

    def test_reset_allows_re_adding(self, store, sample_chunks):
        store.add_chunks(sample_chunks)
        store.reset()
        store.add_chunks(sample_chunks[:1])
        assert store.collection.count() == 1
