# 技術設計: claude-rag-qa

## アーキテクチャパターン & 境界マップ

### パターン: パイプライン + モジュール分離

```
┌─────────────┐    ┌─────────────┐    ┌──────────────────┐
│  loader.py  │───▶│ chunker.py  │───▶│ vectorstore.py   │
│  URL取得     │    │ テキスト分割  │    │ ChromaDB保存      │
└─────────────┘    └─────────────┘    └──────────────────┘
                                              │
                                              ▼
┌─────────────┐    ┌─────────────┐    ┌──────────────────┐
│  ユーザー質問  │───▶│   rag.py    │◀───│ vectorstore.py   │
│             │    │ 回答生成     │    │ ChromaDB検索      │
└─────────────┘    └─────────────┘    └──────────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ Gemini API  │
                   │ 回答生成     │
                   └─────────────┘
```

### 境界
- **外部境界**: URL取得（HTTP）、Gemini API（REST）
- **内部境界**: モジュール間はPython関数呼び出し
- **永続化境界**: ChromaDB（ローカルディスク）、JSONファイル（data/）

---

## 技術スタック & 整合性

| レイヤー | 技術 | バージョン | 根拠 |
|---------|------|----------|------|
| 言語 | Python | 3.11+ | ステアリング指定 |
| ベクトルDB | chromadb | latest | 内蔵Embedding付き、ローカル完結 |
| Embedding | all-MiniLM-L6-v2 | ChromaDB内蔵 | 無料、追加設定不要 |
| LLM | google-generativeai | latest | Gemini API（ユーザー指定） |
| スクレイピング | requests + beautifulsoup4 | latest | 軽量、標準的 |
| 設定管理 | python-dotenv | latest | .env読み込み |

### 依存関係（requirements.txt）
```
chromadb
google-generativeai
requests
beautifulsoup4
python-dotenv
```

---

## コンポーネント & インターフェース定義

### コンポーネント 1: config.py — 設定管理
**対応要件**: 7.1, 7.2, 7.3

```python
# 型定義
@dataclass
class Config:
    gemini_api_key: str
    chunk_size: int = 500
    chunk_overlap: int = 100
    top_k: int = 5
    chroma_persist_dir: str = "./chroma_db"
    collection_name: str = "claude_docs"

def load_config() -> Config:
    """環境変数と定数から設定を読み込む"""
    ...
```

### コンポーネント 2: loader.py — ドキュメント取得
**対応要件**: 1.1, 1.2, 1.3

```python
# 型定義
@dataclass
class Document:
    url: str
    title: str
    content: str

def fetch_url(url: str) -> Document | None:
    """単一URLからテキストを取得。失敗時はNoneを返しログ出力"""
    ...

def load_sources(sources_path: str = "data/sources.json") -> list[Document]:
    """sources.jsonから全URL取得し、Documentリストを返す"""
    ...
```

**処理詳細**:
- `requests.get(url, timeout=10)` でHTML取得
- `BeautifulSoup(html, 'html.parser')` でパース
- script, style, nav, footer, header タグを除去してからテキスト抽出
- 連続空白・改行を正規化

### コンポーネント 3: chunker.py — テキスト分割
**対応要件**: 2.1, 2.2, 2.3

```python
# 型定義
@dataclass
class Chunk:
    text: str
    metadata: dict  # {"source_url": str, "chunk_index": int}

def split_text(document: Document, chunk_size: int = 500, overlap: int = 100) -> list[Chunk]:
    """ドキュメントをオーバーラップ付きチャンクに分割"""
    ...
```

**処理詳細**:
- 文字数ベースの固定長分割（文境界を考慮）
- オーバーラップ: 前チャンクの末尾overlap文字を次チャンクの先頭に含める
- 各チャンクに`source_url`と`chunk_index`のメタデータを付与

### コンポーネント 4: vectorstore.py — ベクトルストア管理
**対応要件**: 3.1, 3.2, 3.3

```python
class VectorStore:
    def __init__(self, persist_dir: str = "./chroma_db", collection_name: str = "claude_docs"):
        """ChromaDB PersistentClientを初期化"""
        ...

    def add_chunks(self, chunks: list[Chunk]) -> None:
        """チャンクをChromaDBに追加（内蔵Embeddingで自動ベクトル化）"""
        ...

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """クエリに類似するチャンクをtop_k件返す。各dictはtext, metadata, distanceを含む"""
        ...

    def reset(self) -> None:
        """コレクションをリセット（再インジェスト用）"""
        ...
```

**処理詳細**:
- `chromadb.PersistentClient(path=persist_dir)` で永続化
- `collection.add(documents=..., metadatas=..., ids=...)` でチャンク追加
- `collection.query(query_texts=[query], n_results=top_k)` で検索
- IDはURL+チャンクインデックスのハッシュで一意性を保証

### コンポーネント 5: rag.py — RAGパイプライン
**対応要件**: 4.1, 4.2, 4.3

```python
@dataclass
class RAGResponse:
    answer: str
    sources: list[str]  # ソースURLリスト

class RAGPipeline:
    def __init__(self, config: Config, vectorstore: VectorStore):
        ...

    def ask(self, question: str) -> RAGResponse:
        """質問に対してRAGで回答を生成"""
        ...

    def _build_prompt(self, question: str, contexts: list[dict]) -> str:
        """検索結果を含むプロンプトを構築"""
        ...
```

**プロンプトテンプレート**:
```
以下のコンテキスト情報を使って質問に回答してください。
コンテキストに含まれない情報については「情報が見つかりませんでした」と回答してください。

コンテキスト:
{contexts}

質問: {question}
```

### コンポーネント 6: evaluate.py — 比較評価
**対応要件**: 6.1, 6.2, 6.3

```python
@dataclass
class EvaluationResult:
    question: str
    expected_answer: str
    rag_answer: str
    notebooklm_answer: str  # 手動入力
    scores: dict  # {"accuracy": int, "coverage": int, "citation": int}

def run_evaluation(qa_path: str = "data/qa_pairs.json") -> list[EvaluationResult]:
    """全Q&Aペアに対してRAG回答を生成"""
    ...

def generate_report(results: list[EvaluationResult], output_dir: str = "evaluation/results/") -> str:
    """Markdownレポートを生成"""
    ...
```

---

## データフロー

### インジェストフロー（文書取り込み）
```
data/sources.json → loader.load_sources() → [Document]
    → chunker.split_text() → [Chunk]
    → vectorstore.add_chunks() → ChromaDB永続化
```

### クエリフロー（質問応答）
```
質問(str) → vectorstore.search() → [関連チャンク]
    → rag._build_prompt() → プロンプト構築
    → Gemini API → 回答生成
    → RAGResponse(answer, sources)
```

### 評価フロー
```
data/qa_pairs.json → evaluate.run_evaluation()
    → 各質問をRAGPipeline.ask()で処理
    → NotebookLM回答を手動追加
    → evaluate.generate_report() → Markdownレポート
```

---

## データ形式

### data/sources.json
```json
{
  "sources": [
    {"url": "https://...", "name": "Claude概要"}
  ]
}
```

### data/qa_pairs.json
```json
{
  "pairs": [
    {
      "id": 1,
      "question": "Claudeのコンテキストウィンドウの最大サイズは？",
      "expected_answer": "...",
      "category": "基本仕様"
    }
  ]
}
```

---

## エントリポイント

### main.py（CLIインターフェース）
```python
def main():
    """サブコマンド: ingest, ask, evaluate"""
    ...

# 使用例:
# python main.py ingest          — 文書取り込み
# python main.py ask "質問"      — 単一質問
# python main.py evaluate        — 全Q&A評価実行
```

---

## 要件トレーサビリティ

| 要件ID | コンポーネント | 検証方法 |
|--------|-------------|---------|
| 1.1, 1.2, 1.3 | loader.py | URL取得・エラーハンドリング動作確認 |
| 2.1, 2.2, 2.3 | chunker.py | チャンクサイズ・オーバーラップ・メタデータ確認 |
| 3.1, 3.2, 3.3 | vectorstore.py | ChromaDB保存・検索・永続化確認 |
| 4.1, 4.2, 4.3 | rag.py | 回答生成・ソース引用・フォールバック確認 |
| 5.1, 5.2, 5.3 | qa_pairs.json + evaluate.py | Q&Aペア構造・回答生成確認 |
| 6.1, 6.2, 6.3 | evaluate.py | レポート出力・評価軸確認 |
| 7.1, 7.2, 7.3 | config.py + .env | 設定管理・セキュリティ確認 |
