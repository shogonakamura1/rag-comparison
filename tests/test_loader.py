from unittest.mock import patch, Mock
from src.loader import Document, fetch_url, load_local_file, load_sources


def test_fetch_url_success():
    html = "<html><head><script>js</script></head><body><p>Hello World</p></body></html>"
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.text = html
    mock_resp.raise_for_status = Mock()

    with patch("src.loader.requests.get", return_value=mock_resp):
        doc = fetch_url("https://example.com")

    assert doc is not None
    assert doc.url == "https://example.com"
    assert "Hello World" in doc.content
    assert "js" not in doc.content


def test_fetch_url_removes_nav_footer():
    html = "<html><body><nav>Nav</nav><main>Main Content</main><footer>Footer</footer></body></html>"
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.text = html
    mock_resp.raise_for_status = Mock()

    with patch("src.loader.requests.get", return_value=mock_resp):
        doc = fetch_url("https://example.com")

    assert doc is not None
    assert "Main Content" in doc.content
    assert "Nav" not in doc.content
    assert "Footer" not in doc.content


def test_fetch_url_failure():
    with patch("src.loader.requests.get", side_effect=Exception("Connection error")):
        doc = fetch_url("https://bad-url.com")

    assert doc is None


def test_load_sources(tmp_path):
    import json
    sources_file = tmp_path / "sources.json"
    sources_file.write_text(json.dumps({
        "sources": [
            {"url": "https://example.com/1", "name": "Doc1"},
            {"url": "https://example.com/2", "name": "Doc2"},
        ]
    }))

    html = "<html><body><p>Content</p></body></html>"
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.text = html
    mock_resp.raise_for_status = Mock()

    with patch("src.loader.requests.get", return_value=mock_resp):
        docs = load_sources(str(sources_file))

    assert len(docs) == 2


def test_load_sources_skips_failed_urls(tmp_path):
    import json
    sources_file = tmp_path / "sources.json"
    sources_file.write_text(json.dumps({
        "sources": [
            {"url": "https://bad.com", "name": "Bad"},
            {"url": "https://good.com", "name": "Good"},
        ]
    }))

    def side_effect(url, **kwargs):
        if "bad" in url:
            raise Exception("Fail")
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.text = "<html><body><p>OK</p></body></html>"
        mock_resp.raise_for_status = Mock()
        return mock_resp

    with patch("src.loader.requests.get", side_effect=side_effect):
        docs = load_sources(str(sources_file))

    assert len(docs) == 1
    assert docs[0].url == "https://good.com"


def test_load_local_file(tmp_path):
    md_file = tmp_path / "test.md"
    md_file.write_text("# Test Title\n\nSome content here.")
    doc = load_local_file(str(md_file), source_url="https://example.com")
    assert doc is not None
    assert doc.url == "https://example.com"
    assert doc.title == "Test Title"
    assert "Some content here." in doc.content


def test_load_local_file_missing():
    doc = load_local_file("/nonexistent/path.md")
    assert doc is None


def test_load_sources_with_local_path(tmp_path):
    import json
    md_file = tmp_path / "doc.md"
    md_file.write_text("# Local Doc\n\nLocal content.")
    sources_file = tmp_path / "sources.json"
    sources_file.write_text(json.dumps({
        "sources": [
            {"url": "https://example.com", "name": "Doc", "local_path": str(md_file)}
        ]
    }))
    docs = load_sources(str(sources_file))
    assert len(docs) == 1
    assert docs[0].url == "https://example.com"
    assert "Local content." in docs[0].content
