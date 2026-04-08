import json
from unittest.mock import MagicMock, patch, mock_open

import pytest

from src.loader import Document
from src.chunker import Chunk
from src.rag import RAGResponse


class TestIngestCommand:
    @patch("main.VectorStore")
    @patch("main.split_text")
    @patch("main.load_sources")
    @patch("main.load_config")
    def test_ingest_loads_and_stores_chunks(
        self, mock_load_config, mock_load_sources, mock_split_text, mock_vectorstore_cls, capsys
    ):
        from main import cmd_ingest

        mock_config = MagicMock()
        mock_config.chunk_size = 500
        mock_config.chunk_overlap = 100
        mock_config.chroma_persist_dir = "./chroma_db"
        mock_config.collection_name = "claude_docs"
        mock_load_config.return_value = mock_config

        doc1 = Document(url="https://example.com/1", title="Doc1", content="Hello world")
        doc2 = Document(url="https://example.com/2", title="Doc2", content="Foo bar")
        mock_load_sources.return_value = [doc1, doc2]

        chunk1 = Chunk(text="Hello", metadata={"source_url": "https://example.com/1", "chunk_index": 0})
        chunk2 = Chunk(text="world", metadata={"source_url": "https://example.com/1", "chunk_index": 1})
        chunk3 = Chunk(text="Foo bar", metadata={"source_url": "https://example.com/2", "chunk_index": 0})
        mock_split_text.side_effect = [[chunk1, chunk2], [chunk3]]

        mock_vs_instance = MagicMock()
        mock_vectorstore_cls.return_value = mock_vs_instance

        cmd_ingest()

        mock_load_sources.assert_called_once()
        assert mock_split_text.call_count == 2
        mock_vs_instance.add_chunks.assert_called_once()
        # Should have added all 3 chunks
        added_chunks = mock_vs_instance.add_chunks.call_args[0][0]
        assert len(added_chunks) == 3

        captured = capsys.readouterr()
        assert "2" in captured.out  # 2 docs
        assert "3" in captured.out  # 3 chunks

    @patch("main.VectorStore")
    @patch("main.split_text")
    @patch("main.load_sources")
    @patch("main.load_config")
    def test_ingest_handles_no_documents(
        self, mock_load_config, mock_load_sources, mock_split_text, mock_vectorstore_cls, capsys
    ):
        from main import cmd_ingest

        mock_config = MagicMock()
        mock_config.chunk_size = 500
        mock_config.chunk_overlap = 100
        mock_config.chroma_persist_dir = "./chroma_db"
        mock_config.collection_name = "claude_docs"
        mock_load_config.return_value = mock_config
        mock_load_sources.return_value = []

        mock_vs_instance = MagicMock()
        mock_vectorstore_cls.return_value = mock_vs_instance

        cmd_ingest()

        mock_split_text.assert_not_called()
        captured = capsys.readouterr()
        assert "0" in captured.out


class TestAskCommand:
    @patch("main.RAGPipeline")
    @patch("main.VectorStore")
    @patch("main.load_config")
    def test_ask_prints_answer_and_sources(
        self, mock_load_config, mock_vectorstore_cls, mock_pipeline_cls, capsys
    ):
        from main import cmd_ask

        mock_config = MagicMock()
        mock_config.chroma_persist_dir = "./chroma_db"
        mock_config.collection_name = "claude_docs"
        mock_load_config.return_value = mock_config

        mock_vs_instance = MagicMock()
        mock_vectorstore_cls.return_value = mock_vs_instance

        mock_pipeline = MagicMock()
        mock_pipeline.ask.return_value = RAGResponse(
            answer="Claudeは高性能なAIです。",
            sources=["https://example.com/claude", "https://example.com/models"],
        )
        mock_pipeline_cls.return_value = mock_pipeline

        cmd_ask("Claudeとは何ですか？")

        mock_pipeline.ask.assert_called_once_with("Claudeとは何ですか？")
        captured = capsys.readouterr()
        assert "Claudeは高性能なAIです。" in captured.out
        assert "https://example.com/claude" in captured.out
        assert "https://example.com/models" in captured.out

    @patch("main.RAGPipeline")
    @patch("main.VectorStore")
    @patch("main.load_config")
    def test_ask_no_sources(self, mock_load_config, mock_vectorstore_cls, mock_pipeline_cls, capsys):
        from main import cmd_ask

        mock_config = MagicMock()
        mock_config.chroma_persist_dir = "./chroma_db"
        mock_config.collection_name = "claude_docs"
        mock_load_config.return_value = mock_config

        mock_vs_instance = MagicMock()
        mock_vectorstore_cls.return_value = mock_vs_instance

        mock_pipeline = MagicMock()
        mock_pipeline.ask.return_value = RAGResponse(
            answer="関連情報が見つかりませんでした",
            sources=[],
        )
        mock_pipeline_cls.return_value = mock_pipeline

        cmd_ask("存在しない質問")

        captured = capsys.readouterr()
        assert "関連情報が見つかりませんでした" in captured.out


class TestEvaluateCommand:
    @patch("builtins.open", new_callable=mock_open)
    @patch("main.json")
    @patch("main.RAGPipeline")
    @patch("main.VectorStore")
    @patch("main.load_config")
    def test_evaluate_processes_all_pairs_and_saves(
        self, mock_load_config, mock_vectorstore_cls, mock_pipeline_cls, mock_json, mock_file, capsys
    ):
        from main import cmd_evaluate

        mock_config = MagicMock()
        mock_config.chroma_persist_dir = "./chroma_db"
        mock_config.collection_name = "claude_docs"
        mock_load_config.return_value = mock_config

        mock_vs_instance = MagicMock()
        mock_vectorstore_cls.return_value = mock_vs_instance

        mock_pipeline = MagicMock()
        mock_pipeline.ask.return_value = RAGResponse(
            answer="テスト回答",
            sources=["https://example.com"],
        )
        mock_pipeline_cls.return_value = mock_pipeline

        qa_data = {
            "pairs": [
                {"id": 1, "question": "質問1", "expected_answer": "期待回答1", "category": "カテゴリ1"},
                {"id": 2, "question": "質問2", "expected_answer": "期待回答2", "category": "カテゴリ2"},
            ]
        }
        mock_json.load.return_value = qa_data

        cmd_evaluate()

        assert mock_pipeline.ask.call_count == 2
        mock_json.dump.assert_called_once()
        saved_data = mock_json.dump.call_args[0][0]
        assert len(saved_data["results"]) == 2
        assert saved_data["results"][0]["question"] == "質問1"
        assert saved_data["results"][0]["rag_answer"] == "テスト回答"
        assert saved_data["results"][0]["sources"] == ["https://example.com"]

        captured = capsys.readouterr()
        assert "2" in captured.out

    @patch("builtins.open", new_callable=mock_open)
    @patch("main.json")
    @patch("main.RAGPipeline")
    @patch("main.VectorStore")
    @patch("main.load_config")
    def test_evaluate_creates_output_directory(
        self, mock_load_config, mock_vectorstore_cls, mock_pipeline_cls, mock_json, mock_file, capsys
    ):
        from main import cmd_evaluate

        mock_config = MagicMock()
        mock_config.chroma_persist_dir = "./chroma_db"
        mock_config.collection_name = "claude_docs"
        mock_load_config.return_value = mock_config

        mock_vs_instance = MagicMock()
        mock_vectorstore_cls.return_value = mock_vs_instance

        mock_pipeline = MagicMock()
        mock_pipeline_cls.return_value = mock_pipeline

        mock_json.load.return_value = {"pairs": []}

        with patch("main.os.makedirs") as mock_makedirs:
            cmd_evaluate()
            mock_makedirs.assert_called_once_with("evaluation/results", exist_ok=True)


class TestArgparse:
    def test_ingest_subcommand(self):
        from main import create_parser

        parser = create_parser()
        args = parser.parse_args(["ingest"])
        assert args.command == "ingest"

    def test_ask_subcommand(self):
        from main import create_parser

        parser = create_parser()
        args = parser.parse_args(["ask", "テスト質問"])
        assert args.command == "ask"
        assert args.question == "テスト質問"

    def test_evaluate_subcommand(self):
        from main import create_parser

        parser = create_parser()
        args = parser.parse_args(["evaluate"])
        assert args.command == "evaluate"

    def test_no_subcommand_shows_help(self):
        from main import create_parser

        parser = create_parser()
        args = parser.parse_args([])
        assert args.command is None
