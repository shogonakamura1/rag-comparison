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


def test_split_text_table_kept_intact():
    """v7: Markdownの表は分割せず1チャンクに収まる。"""
    table_content = """前置きの文章。

## モデル比較

| 機能 | A | B | C |
|------|---|---|---|
| 料金 | $5 | $3 | $1 |
| 速度 | 中 | 速 | 最速 |
| サポート | はい | いいえ | いいえ |

後続の文章。
"""
    doc = Document(url="https://example.com", title="Test", content=table_content)
    chunks = split_text(doc, chunk_size=50, overlap=10)

    # 表全体が1チャンクとして保持されているチャンクが存在することを確認
    table_chunks = [c for c in chunks if c.metadata.get("block_type") == "table"]
    assert len(table_chunks) == 1, f"Expected 1 table chunk, got {len(table_chunks)}"

    table_text = table_chunks[0].text
    # 表全体（ヘッダー + 全データ行）が1チャンクに含まれている
    assert "| 機能 | A | B | C |" in table_text
    assert "| 料金 | $5 | $3 | $1 |" in table_text
    assert "| 速度 | 中 | 速 | 最速 |" in table_text
    assert "| サポート | はい | いいえ | いいえ |" in table_text
    # 直前のセクション見出しも含まれる
    assert "## モデル比較" in table_text


def test_split_text_table_with_text_around():
    """表と通常テキストが混在するときに、表は表チャンク、テキストはテキストチャンクになる。"""
    content = """これは通常テキストです。

| col1 | col2 |
|------|------|
| a    | b    |

通常テキストの続きです。
"""
    doc = Document(url="https://example.com", title="Test", content=content)
    chunks = split_text(doc, chunk_size=500, overlap=100)

    block_types = [c.metadata.get("block_type") for c in chunks]
    assert "table" in block_types
    assert "text" in block_types
