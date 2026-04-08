# リサーチログ: claude-rag-qa

## サマリ
グリーンフィールドRAGシステムの設計に必要な技術調査。フレームワーク不使用、ChromaDB内蔵Embedding、Gemini APIの組み合わせ。

## リサーチログ

### トピック 1: ChromaDB内蔵Embedding
- **ソース**: ChromaDB公式ドキュメント
- **発見**: ChromaDBはデフォルトで`all-MiniLM-L6-v2`（sentence-transformers）を使用。`chromadb.Client()`作成時に自動ダウンロードされる。明示的なEmbedding関数指定不要。
- **影響**: OpenAI SDK不要。初回実行時にモデルダウンロードが発生する点をユーザーに通知する必要あり。

### トピック 2: ChromaDB永続化
- **ソース**: ChromaDB公式ドキュメント
- **発見**: `chromadb.PersistentClient(path="./chroma_db")`でローカルディスク永続化。SQLite + Parquet形式で保存。
- **影響**: `chroma_db/`ディレクトリを`.gitignore`に追加する必要あり。

### トピック 3: Gemini API (google-generativeai)
- **ソース**: Google AI公式ドキュメント
- **発見**: `google-generativeai` パッケージで `gemini-2.0-flash` モデルを使用。`genai.GenerativeModel('gemini-2.0-flash')` でインスタンス化。`generate_content()` メソッドで回答生成。
- **影響**: システムプロンプトにRAGコンテキスト注入のテンプレートが必要。

### トピック 4: BeautifulSoup4によるWebスクレイピング
- **ソース**: BS4公式ドキュメント
- **発見**: `requests.get()` + `BeautifulSoup(html, 'html.parser')` でHTML取得・パース。`soup.get_text()` でテキスト抽出。不要なタグ（script, style, nav, footer）は事前に除去。
- **影響**: Webページの構造によって抽出品質が変わるため、前処理の工夫が必要。

## アーキテクチャパターン評価
- **パイプラインパターン**: 取得→分割→保存→検索→生成の線形パイプライン。シンプルで理解しやすい。
- **モジュール分離**: 各ステップを独立したモジュール（loader, chunker, vectorstore, rag）に分離し、テスト容易性を確保。

## 設計判断
1. フレームワーク不使用 → 各コンポーネント手動実装（ユーザー要件）
2. ChromaDB内蔵Embedding → OpenAI SDK不要でコスト削減
3. Gemini API → 回答生成に使用（ユーザー指定）

## リスク
- ChromaDB内蔵Embeddingモデル（all-MiniLM-L6-v2）は英語に最適化されているため、日本語テキストの検索精度に影響する可能性がある
- Webスクレイピングはサイト構造の変更に脆弱
