import json
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from evaluation.evaluate import EvaluationResult, generate_report, run_evaluation, save_results


@pytest.fixture
def sample_qa_pairs():
    return {
        "pairs": [
            {
                "id": 1,
                "question": "Claudeとは何ですか？",
                "expected_answer": "ClaudeはAnthropicが開発したAIアシスタントです。",
                "category": "基本仕様",
            },
            {
                "id": 2,
                "question": "Claude 3.5 Sonnetの特徴は？",
                "expected_answer": "高速かつ高性能なモデルです。",
                "category": "モデル比較",
            },
        ]
    }


@pytest.fixture
def mock_rag_pipeline():
    from src.rag import RAGResponse

    pipeline = MagicMock()
    pipeline.ask.side_effect = [
        RAGResponse(answer="Claudeは高性能なAIです。", sources=["https://example.com/claude"]),
        RAGResponse(answer="Sonnetは高速モデルです。", sources=["https://example.com/models"]),
    ]
    return pipeline


@pytest.fixture
def sample_results():
    return [
        EvaluationResult(
            question="Claudeとは何ですか？",
            expected_answer="ClaudeはAnthropicが開発したAIアシスタントです。",
            rag_answer="Claudeは高性能なAIです。",
            rag_sources=["https://example.com/claude"],
        ),
        EvaluationResult(
            question="Claude 3.5 Sonnetの特徴は？",
            expected_answer="高速かつ高性能なモデルです。",
            rag_answer="Sonnetは高速モデルです。",
            rag_sources=["https://example.com/models"],
        ),
    ]


class TestEvaluationResult:
    def test_dataclass_fields(self):
        result = EvaluationResult(
            question="Q",
            expected_answer="A",
            rag_answer="RA",
            rag_sources=["src1"],
        )
        assert result.question == "Q"
        assert result.expected_answer == "A"
        assert result.rag_answer == "RA"
        assert result.rag_sources == ["src1"]
        assert result.notebooklm_answer == ""
        assert result.scores == {"accuracy": 0, "coverage": 0, "citation": 0}

    def test_custom_scores(self):
        result = EvaluationResult(
            question="Q",
            expected_answer="A",
            rag_answer="RA",
            rag_sources=[],
            scores={"accuracy": 5, "coverage": 4, "citation": 3},
        )
        assert result.scores["accuracy"] == 5
        assert result.scores["coverage"] == 4
        assert result.scores["citation"] == 3


class TestRunEvaluation:
    def test_returns_evaluation_results(self, tmp_path, mock_rag_pipeline, sample_qa_pairs):
        qa_path = tmp_path / "qa_pairs.json"
        qa_path.write_text(json.dumps(sample_qa_pairs, ensure_ascii=False), encoding="utf-8")

        results = run_evaluation(mock_rag_pipeline, qa_path=str(qa_path))

        assert len(results) == 2
        assert all(isinstance(r, EvaluationResult) for r in results)

    def test_first_result_matches_qa_pair(self, tmp_path, mock_rag_pipeline, sample_qa_pairs):
        qa_path = tmp_path / "qa_pairs.json"
        qa_path.write_text(json.dumps(sample_qa_pairs, ensure_ascii=False), encoding="utf-8")

        results = run_evaluation(mock_rag_pipeline, qa_path=str(qa_path))

        assert results[0].question == "Claudeとは何ですか？"
        assert results[0].expected_answer == "ClaudeはAnthropicが開発したAIアシスタントです。"
        assert results[0].rag_answer == "Claudeは高性能なAIです。"
        assert results[0].rag_sources == ["https://example.com/claude"]

    def test_calls_rag_pipeline_for_each_question(self, tmp_path, mock_rag_pipeline, sample_qa_pairs):
        qa_path = tmp_path / "qa_pairs.json"
        qa_path.write_text(json.dumps(sample_qa_pairs, ensure_ascii=False), encoding="utf-8")

        run_evaluation(mock_rag_pipeline, qa_path=str(qa_path))

        assert mock_rag_pipeline.ask.call_count == 2
        mock_rag_pipeline.ask.assert_any_call("Claudeとは何ですか？")
        mock_rag_pipeline.ask.assert_any_call("Claude 3.5 Sonnetの特徴は？")


class TestSaveResults:
    def test_writes_json_file(self, tmp_path, sample_results):
        output_path = str(tmp_path / "results.json")
        save_results(sample_results, output_path=output_path)

        assert (tmp_path / "results.json").exists()

    def test_json_contains_all_results(self, tmp_path, sample_results):
        output_path = str(tmp_path / "results.json")
        save_results(sample_results, output_path=output_path)

        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 2
        assert data[0]["question"] == "Claudeとは何ですか？"
        assert data[1]["question"] == "Claude 3.5 Sonnetの特徴は？"

    def test_json_has_correct_structure(self, tmp_path, sample_results):
        output_path = str(tmp_path / "results.json")
        save_results(sample_results, output_path=output_path)

        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)

        entry = data[0]
        assert "question" in entry
        assert "expected_answer" in entry
        assert "rag_answer" in entry
        assert "rag_sources" in entry
        assert "notebooklm_answer" in entry
        assert "scores" in entry

    def test_creates_parent_directories(self, tmp_path, sample_results):
        output_path = str(tmp_path / "nested" / "dir" / "results.json")
        save_results(sample_results, output_path=output_path)

        assert (tmp_path / "nested" / "dir" / "results.json").exists()


class TestGenerateReport:
    def test_creates_markdown_file(self, tmp_path, sample_results):
        path = generate_report(sample_results, output_dir=str(tmp_path))
        assert path.endswith(".md")
        assert (tmp_path / path.split("/")[-1]).exists()

    def test_report_contains_header_with_date(self, tmp_path, sample_results):
        path = generate_report(sample_results, output_dir=str(tmp_path))
        with open(path, encoding="utf-8") as f:
            content = f.read()

        today = datetime.now().strftime("%Y-%m-%d")
        assert today in content
        assert "# " in content

    def test_report_contains_all_questions(self, tmp_path, sample_results):
        path = generate_report(sample_results, output_dir=str(tmp_path))
        with open(path, encoding="utf-8") as f:
            content = f.read()

        assert "Claudeとは何ですか？" in content
        assert "Claude 3.5 Sonnetの特徴は？" in content

    def test_report_contains_expected_answers(self, tmp_path, sample_results):
        path = generate_report(sample_results, output_dir=str(tmp_path))
        with open(path, encoding="utf-8") as f:
            content = f.read()

        assert "ClaudeはAnthropicが開発したAIアシスタントです。" in content
        assert "高速かつ高性能なモデルです。" in content

    def test_report_contains_rag_answers(self, tmp_path, sample_results):
        path = generate_report(sample_results, output_dir=str(tmp_path))
        with open(path, encoding="utf-8") as f:
            content = f.read()

        assert "Claudeは高性能なAIです。" in content
        assert "Sonnetは高速モデルです。" in content

    def test_report_contains_sources(self, tmp_path, sample_results):
        path = generate_report(sample_results, output_dir=str(tmp_path))
        with open(path, encoding="utf-8") as f:
            content = f.read()

        assert "https://example.com/claude" in content
        assert "https://example.com/models" in content

    def test_report_contains_notebooklm_placeholder(self, tmp_path, sample_results):
        path = generate_report(sample_results, output_dir=str(tmp_path))
        with open(path, encoding="utf-8") as f:
            content = f.read()

        assert "NotebookLM" in content

    def test_report_contains_score_table(self, tmp_path, sample_results):
        path = generate_report(sample_results, output_dir=str(tmp_path))
        with open(path, encoding="utf-8") as f:
            content = f.read()

        assert "accuracy" in content.lower() or "正確性" in content
        assert "coverage" in content.lower() or "網羅性" in content
        assert "citation" in content.lower() or "ソース引用" in content

    def test_report_contains_summary_table(self, tmp_path, sample_results):
        path = generate_report(sample_results, output_dir=str(tmp_path))
        with open(path, encoding="utf-8") as f:
            content = f.read()

        # Summary section should exist
        assert "サマリー" in content or "Summary" in content or "summary" in content or "まとめ" in content
