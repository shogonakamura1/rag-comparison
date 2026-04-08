import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime


@dataclass
class EvaluationResult:
    question: str
    expected_answer: str
    rag_answer: str
    rag_sources: list[str]
    notebooklm_answer: str = ""
    scores: dict = field(default_factory=lambda: {"accuracy": 0, "coverage": 0, "citation": 0})


def run_evaluation(rag_pipeline, qa_path: str = "data/qa_pairs.json") -> list[EvaluationResult]:
    """Run all Q&A pairs through RAG pipeline, return results."""
    with open(qa_path, encoding="utf-8") as f:
        data = json.load(f)

    results: list[EvaluationResult] = []
    for pair in data["pairs"]:
        response = rag_pipeline.ask(pair["question"])
        result = EvaluationResult(
            question=pair["question"],
            expected_answer=pair["expected_answer"],
            rag_answer=response.answer,
            rag_sources=response.sources,
        )
        results.append(result)

    return results


def save_results(results: list[EvaluationResult], output_path: str = "evaluation/results/rag_results.json") -> None:
    """Save evaluation results as JSON."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    data = [asdict(r) for r in results]
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_report(results: list[EvaluationResult], output_dir: str = "evaluation/results/") -> str:
    """Generate Markdown comparison report. Returns the file path."""
    os.makedirs(output_dir, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"comparison_report_{today}.md"
    filepath = os.path.join(output_dir, filename)

    lines: list[str] = []
    lines.append(f"# RAG vs NotebookLM 比較レポート")
    lines.append(f"")
    lines.append(f"生成日: {today}")
    lines.append(f"")

    for i, result in enumerate(results, 1):
        lines.append(f"## Q{i}: {result.question}")
        lines.append(f"")
        lines.append(f"### 期待される回答")
        lines.append(f"")
        lines.append(result.expected_answer)
        lines.append(f"")
        lines.append(f"### RAG回答")
        lines.append(f"")
        lines.append(result.rag_answer)
        lines.append(f"")
        lines.append(f"**ソース:**")
        if result.rag_sources:
            for src in result.rag_sources:
                lines.append(f"- {src}")
        else:
            lines.append("- なし")
        lines.append(f"")
        lines.append(f"### NotebookLM回答")
        lines.append(f"")
        lines.append(result.notebooklm_answer if result.notebooklm_answer else "（未入力）")
        lines.append(f"")
        lines.append(f"### スコア")
        lines.append(f"")
        lines.append(f"| 評価軸 | スコア |")
        lines.append(f"|--------|--------|")
        lines.append(f"| 正確性 (accuracy) | {result.scores.get('accuracy', 0)} |")
        lines.append(f"| 網羅性 (coverage) | {result.scores.get('coverage', 0)} |")
        lines.append(f"| ソース引用 (citation) | {result.scores.get('citation', 0)} |")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

    # Summary table
    lines.append(f"## サマリー")
    lines.append(f"")
    lines.append(f"| # | 質問 | 正確性 | 網羅性 | ソース引用 |")
    lines.append(f"|---|------|--------|--------|------------|")
    for i, result in enumerate(results, 1):
        q_short = result.question[:30] + "..." if len(result.question) > 30 else result.question
        acc = result.scores.get("accuracy", 0)
        cov = result.scores.get("coverage", 0)
        cit = result.scores.get("citation", 0)
        lines.append(f"| {i} | {q_short} | {acc} | {cov} | {cit} |")
    lines.append(f"")

    total = len(results)
    if total > 0:
        avg_acc = sum(r.scores.get("accuracy", 0) for r in results) / total
        avg_cov = sum(r.scores.get("coverage", 0) for r in results) / total
        avg_cit = sum(r.scores.get("citation", 0) for r in results) / total
        lines.append(f"**平均スコア:** 正確性={avg_acc:.1f} / 網羅性={avg_cov:.1f} / ソース引用={avg_cit:.1f}")
        lines.append(f"")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath
