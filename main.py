import argparse
import json
import os

from src.config import load_config
from src.loader import load_sources
from src.chunker import split_text
from src.vectorstore import VectorStore
from src.rag import RAGPipeline


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="RAG比較システム CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("ingest", help="ソースURLからドキュメントを取り込み、ChromaDBに保存する")

    ask_parser = subparsers.add_parser("ask", help="質問に対してRAGパイプラインで回答する")
    ask_parser.add_argument("question", type=str, help="質問テキスト")

    subparsers.add_parser("evaluate", help="Q&Aペアを使ってRAGパイプラインを評価する")

    return parser


def cmd_ingest() -> None:
    config = load_config()
    print("ソースの読み込み中...")
    documents = load_sources()

    all_chunks = []
    for doc in documents:
        chunks = split_text(doc, chunk_size=config.chunk_size, overlap=config.chunk_overlap)
        all_chunks.extend(chunks)

    vs = VectorStore(persist_dir=config.chroma_persist_dir, collection_name=config.collection_name)
    if all_chunks:
        vs.add_chunks(all_chunks)

    print(f"取り込み完了: {len(documents)}件のドキュメント, {len(all_chunks)}件のチャンク")


def cmd_ask(question: str) -> None:
    config = load_config()
    vs = VectorStore(persist_dir=config.chroma_persist_dir, collection_name=config.collection_name)
    pipeline = RAGPipeline(config, vs, distance_threshold=config.distance_threshold)

    response = pipeline.ask(question)

    print(f"\n回答:\n{response.answer}")
    if response.sources:
        print("\nソース:")
        for url in response.sources:
            print(f"  - {url}")


def cmd_evaluate() -> None:
    config = load_config()
    vs = VectorStore(persist_dir=config.chroma_persist_dir, collection_name=config.collection_name)
    pipeline = RAGPipeline(config, vs, distance_threshold=config.distance_threshold)

    with open("data/qa_pairs.json") as f:
        qa_data = json.load(f)

    results = []
    for pair in qa_data["pairs"]:
        print(f"質問 {pair['id']}: {pair['question']}")
        response = pipeline.ask(pair["question"])
        results.append({
            "id": pair["id"],
            "question": pair["question"],
            "expected_answer": pair["expected_answer"],
            "rag_answer": response.answer,
            "sources": response.sources,
            "category": pair["category"],
        })

    os.makedirs("evaluation/results", exist_ok=True)
    output_path = "evaluation/results/rag_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"results": results}, f, ensure_ascii=False, indent=2)

    print(f"\n評価完了: {len(results)}件の質問を処理しました")
    print(f"結果を {output_path} に保存しました")


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "ingest":
        cmd_ingest()
    elif args.command == "ask":
        cmd_ask(args.question)
    elif args.command == "evaluate":
        cmd_evaluate()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
