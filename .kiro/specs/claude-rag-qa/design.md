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
| ベクトルDB | chromadb | latest | ローカル完結、SQLite + HNSW |
| Embedding | sentence-transformers + multilingual-e5-large | latest | 100言語対応・1024次元、クロスリンガル検索に強い（v3で `all-MiniLM-L6-v2` から変更） |
| LLM | google-generativeai | latest | Gemini API（gemini-2.5-flash） |
| スクレイピング | requests + beautifulsoup4 | latest | 軽量、標準的 |
| 設定管理 | python-dotenv | latest | .env読み込み |

### 依存関係（requirements.txt）
```
chromadb
google-generativeai
sentence-transformers
requests
beautifulsoup4
python-dotenv
pytest
```

### LLM選択について
当初は Claude API（Anthropic SDK）を採用する設計だったが、コスト・APIキー入手しやすさの観点から **Gemini API** に変更された。詳細は [decisions/0001-llm-choice.md](decisions/0001-llm-choice.md) を参照。

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
    top_k: int = 8                       # v3で5から拡大（取りこぼし防止）
    distance_threshold: float = 0.45     # v3で導入（無関係チャンクを除外）
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
    metadata: dict  # {"source_url": str, "chunk_index": int, "block_type": "text" | "table"}

def split_text(document: Document, chunk_size: int = 500, overlap: int = 100) -> list[Chunk]:
    """ドキュメントをチャンクに分割

    v7: 表認識チャンキング
    - Markdownの表（| で始まる連続行）を検出した場合、表全体を1チャンクとして保持する
    - 表の直前のセクション見出し（##）も同じチャンクに含める
    - 通常テキストは従来通り chunk_size でオーバーラップ付き分割
    """
    ...
```

**処理詳細**:
- テキストを「表ブロック」と「通常テキストブロック」に分解
- 表ブロック: chunk_sizeを無視して1チャンクにまとめる（行・列の対応関係を保持）
- 通常テキストブロック: 文字数ベースで chunk_size 文字ごとに分割し、隣接チャンク間に overlap 文字の重複を設ける
- 各チャンクに `source_url`、`chunk_index`、`block_type`（"text" or "table"）のメタデータを付与

### コンポーネント 4: vectorstore.py — ベクトルストア管理
**対応要件**: 3.1, 3.2, 3.3

```python
MODEL_NAME = "intfloat/multilingual-e5-large"

class E5EmbeddingFunction(EmbeddingFunction):
    """multilingual-e5-large 用のカスタムEmbedding関数。
    query/passage プレフィックスで検索精度を向上させる。"""
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self._mode = "passage"  # add_chunks時は passage、search時は query に切替

class VectorStore:
    def __init__(self, persist_dir: str = "./chroma_db", collection_name: str = "claude_docs"):
        """ChromaDB PersistentClientを初期化（E5EmbeddingFunctionを使用）"""
        ...

    def add_chunks(self, chunks: list[Chunk]) -> None:
        """チャンクをChromaDBに追加（multilingual-e5-largeでベクトル化）"""
        ...

    def search(self, query: str, top_k: int = 8) -> list[dict]:
        """クエリに類似するチャンクをtop_k件返す。各dictはtext, metadata, distanceを含む"""
        ...

    def reset(self) -> None:
        """コレクションをリセット（再インジェスト用）"""
        ...
```

**処理詳細**:
- `chromadb.PersistentClient(path=persist_dir)` で永続化
- カスタムEmbedding関数 `E5EmbeddingFunction` を使用（v3で導入）
- 検索時は `_mode = "query"`、保存時は `_mode = "passage"` を自動切替
- IDはURL+チャンクインデックスのSHA-256ハッシュで一意性を保証

### コンポーネント 5: rag.py — RAGパイプライン
**対応要件**: 4.1, 4.2, 4.3

```python
@dataclass
class RAGResponse:
    answer: str
    sources: list[str]  # ソースURLリスト

class RAGPipeline:
    def __init__(
        self,
        config: Config,
        vectorstore: VectorStore,
        translate_query: bool = False,
        distance_threshold: float | None = None,
    ):
        # gemini-2.5-flash を使用
        ...

    def ask(self, question: str) -> RAGResponse:
        """質問に対してRAGで回答を生成
        1. (オプション) クエリ翻訳
        2. ベクトルストア検索 (top_k件)
        3. 距離フィルタリング (distance_threshold以下のみ採用)
        4. プロンプト構築 + Gemini API呼び出し
        5. ソースURL重複除去
        """
        ...

    def _filter_by_distance(self, results: list[dict]) -> list[dict]:
        """距離が閾値以下のチャンクのみを残す（無関係チャンクを除外）"""
        ...

    def _build_prompt(self, question: str, contexts: list[dict]) -> str:
        """検索結果を含むプロンプトを構築（簡潔回答・推測禁止・論理的推論明示の指示）"""
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
