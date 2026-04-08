from dataclasses import dataclass

import google.generativeai as genai

from src.config import Config
from src.vectorstore import VectorStore

DEFAULT_DISTANCE_THRESHOLD = 0.45


@dataclass
class RAGResponse:
    answer: str
    sources: list[str]


class RAGPipeline:
    def __init__(
        self,
        config: Config,
        vectorstore: VectorStore,
        translate_query: bool = False,
        distance_threshold: float | None = None,
    ):
        genai.configure(api_key=config.gemini_api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.vectorstore = vectorstore
        self.top_k = config.top_k
        self.translate_query_enabled = translate_query
        self.distance_threshold = distance_threshold

    def _translate_query(self, question: str) -> str:
        response = self.model.generate_content(
            "Translate the following question to English. "
            "Output ONLY the translated text, nothing else.\n\n"
            f"{question}"
        )
        return response.text.strip()

    def _filter_by_distance(self, results: list[dict]) -> list[dict]:
        if self.distance_threshold is None:
            return results
        return [r for r in results if r["distance"] <= self.distance_threshold]

    def ask(self, question: str) -> RAGResponse:
        search_query = question
        if self.translate_query_enabled:
            search_query = self._translate_query(question)

        results = self.vectorstore.search(search_query, top_k=self.top_k)
        results = self._filter_by_distance(results)

        if not results:
            return RAGResponse(answer="関連情報が見つかりませんでした", sources=[])

        prompt = self._build_prompt(question, results)
        response = self.model.generate_content(prompt)

        seen: set[str] = set()
        sources: list[str] = []
        for r in results:
            url = r["metadata"]["source_url"]
            if url not in seen:
                seen.add(url)
                sources.append(url)

        return RAGResponse(answer=response.text, sources=sources)

    def _build_prompt(self, question: str, contexts: list[dict]) -> str:
        context_parts = []
        for ctx in contexts:
            source_url = ctx["metadata"]["source_url"]
            context_parts.append(f"ソース: {source_url}\n{ctx['text']}")

        contexts_text = "\n\n".join(context_parts)

        return (
            "あなたはドキュメントに基づいて質問に回答するアシスタントです。\n"
            "以下のコンテキスト情報を注意深く読み、質問に対して回答してください。\n"
            "コンテキストにはMarkdown形式の表が含まれることがあります。表の中の情報も活用してください。\n"
            "コンテキストに関連する情報が少しでもあれば、それを基に回答してください。\n"
            "コンテキストに全く関連する情報がない場合のみ「情報が見つかりませんでした」と回答してください。\n\n"
            f"コンテキスト:\n{contexts_text}\n\n"
            f"質問: {question}"
        )
