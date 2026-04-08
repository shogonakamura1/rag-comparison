from unittest.mock import MagicMock, patch

import pytest

from src.config import Config
from src.rag import RAGPipeline, RAGResponse


@pytest.fixture
def mock_config():
    return Config(gemini_api_key="test-api-key", top_k=3)


@pytest.fixture
def mock_vectorstore():
    return MagicMock()


@pytest.fixture
def sample_search_results():
    return [
        {
            "text": "Claudeは高性能なAIアシスタントです。",
            "metadata": {"source_url": "https://example.com/claude", "chunk_index": 0},
            "distance": 0.1,
        },
        {
            "text": "Claude 3.5 Sonnetは最新モデルです。",
            "metadata": {"source_url": "https://example.com/models", "chunk_index": 0},
            "distance": 0.2,
        },
    ]


class TestRAGResponse:
    def test_dataclass_fields(self):
        response = RAGResponse(answer="テスト回答", sources=["https://example.com"])
        assert response.answer == "テスト回答"
        assert response.sources == ["https://example.com"]


class TestAsk:
    @patch("src.rag.genai")
    def test_ask_returns_rag_response(self, mock_genai, mock_config, mock_vectorstore, sample_search_results):
        mock_vectorstore.search.return_value = sample_search_results

        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = MagicMock(text="Claudeは高性能なAIです。")
        mock_genai.GenerativeModel.return_value = mock_model_instance

        pipeline = RAGPipeline(mock_config, mock_vectorstore)
        response = pipeline.ask("Claudeとは何ですか？")

        assert isinstance(response, RAGResponse)
        assert response.answer == "Claudeは高性能なAIです。"
        assert "https://example.com/claude" in response.sources
        assert "https://example.com/models" in response.sources
        mock_vectorstore.search.assert_called_once_with("Claudeとは何ですか？", top_k=3)

    @patch("src.rag.genai")
    def test_ask_no_results_returns_fallback(self, mock_genai, mock_config, mock_vectorstore):
        mock_vectorstore.search.return_value = []

        mock_genai.GenerativeModel.return_value = MagicMock()

        pipeline = RAGPipeline(mock_config, mock_vectorstore)
        response = pipeline.ask("存在しない質問")

        assert isinstance(response, RAGResponse)
        assert response.answer == "関連情報が見つかりませんでした"
        assert response.sources == []

    @patch("src.rag.genai")
    def test_ask_deduplicates_source_urls(self, mock_genai, mock_config, mock_vectorstore):
        """Same URL from different chunks should appear only once in sources."""
        mock_vectorstore.search.return_value = [
            {
                "text": "チャンク1",
                "metadata": {"source_url": "https://example.com/same", "chunk_index": 0},
                "distance": 0.1,
            },
            {
                "text": "チャンク2",
                "metadata": {"source_url": "https://example.com/same", "chunk_index": 1},
                "distance": 0.2,
            },
        ]

        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = MagicMock(text="回答")
        mock_genai.GenerativeModel.return_value = mock_model_instance

        pipeline = RAGPipeline(mock_config, mock_vectorstore)
        response = pipeline.ask("質問")

        assert response.sources == ["https://example.com/same"]


class TestBuildPrompt:
    @patch("src.rag.genai")
    def test_build_prompt_contains_question(self, mock_genai, mock_config, mock_vectorstore, sample_search_results):
        pipeline = RAGPipeline(mock_config, mock_vectorstore)
        prompt = pipeline._build_prompt("Claudeとは？", sample_search_results)
        assert "Claudeとは？" in prompt

    @patch("src.rag.genai")
    def test_build_prompt_contains_contexts(self, mock_genai, mock_config, mock_vectorstore, sample_search_results):
        pipeline = RAGPipeline(mock_config, mock_vectorstore)
        prompt = pipeline._build_prompt("質問", sample_search_results)
        assert "Claudeは高性能なAIアシスタントです。" in prompt
        assert "Claude 3.5 Sonnetは最新モデルです。" in prompt

    @patch("src.rag.genai")
    def test_build_prompt_contains_source_urls(self, mock_genai, mock_config, mock_vectorstore, sample_search_results):
        pipeline = RAGPipeline(mock_config, mock_vectorstore)
        prompt = pipeline._build_prompt("質問", sample_search_results)
        assert "https://example.com/claude" in prompt
        assert "https://example.com/models" in prompt

    @patch("src.rag.genai")
    def test_build_prompt_contains_instructions(self, mock_genai, mock_config, mock_vectorstore, sample_search_results):
        pipeline = RAGPipeline(mock_config, mock_vectorstore)
        prompt = pipeline._build_prompt("質問", sample_search_results)
        assert "質問に対して回答してください" in prompt
        assert "情報が見つかりませんでした" in prompt
