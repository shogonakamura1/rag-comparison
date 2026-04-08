"""v3 A/B test: compare with and without query translation, both with distance filtering."""
import json

from src.config import load_config
from src.rag import RAGPipeline, DEFAULT_DISTANCE_THRESHOLD
from src.vectorstore import VectorStore


def run_variant(name: str, translate: bool, output_path: str):
    config = load_config()
    vs = VectorStore(persist_dir=config.chroma_persist_dir, collection_name=config.collection_name)
    pipeline = RAGPipeline(
        config,
        vs,
        translate_query=translate,
        distance_threshold=DEFAULT_DISTANCE_THRESHOLD,
    )

    with open("data/qa_pairs.json") as f:
        qa_data = json.load(f)

    results = []
    for pair in qa_data["pairs"]:
        print(f"  [{name}] Q{pair['id']}: {pair['question'][:40]}...")
        response = pipeline.ask(pair["question"])
        results.append({
            "id": pair["id"],
            "question": pair["question"],
            "expected_answer": pair["expected_answer"],
            "rag_answer": response.answer,
            "sources": response.sources,
            "category": pair["category"],
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"results": results}, f, ensure_ascii=False, indent=2)

    print(f"  [{name}] Saved to {output_path}")


if __name__ == "__main__":
    print("=== v3a: No translation + distance filtering ===")
    run_variant("v3a", translate=False, output_path="evaluation/results/v3a_no_translate_rag_results.json")

    print()
    print("=== v3b: Translation + distance filtering ===")
    run_variant("v3b", translate=True, output_path="evaluation/results/v3b_translate_rag_results.json")

    print("\nDone! Compare results in evaluation/results/")
