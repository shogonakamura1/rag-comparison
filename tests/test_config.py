import os
from src.config import Config, load_config


def test_config_defaults():
    config = Config(gemini_api_key="test-key")
    assert config.gemini_api_key == "test-key"
    assert config.chunk_size == 500
    assert config.chunk_overlap == 100
    assert config.top_k == 8
    assert config.chroma_persist_dir == "./chroma_db"
    assert config.collection_name == "claude_docs"


def test_load_config_from_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "env-test-key")
    config = load_config()
    assert config.gemini_api_key == "env-test-key"


def test_load_config_missing_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr("src.config.load_dotenv", lambda: None)
    try:
        load_config()
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "GEMINI_API_KEY" in str(e)
