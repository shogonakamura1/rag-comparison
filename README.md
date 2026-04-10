# RAG Comparison: Claude Domain QA

Claude公式ドキュメントをソースに、自作RAGシステムと Google NotebookLM の応答を比較する実験プロジェクト。

## プロジェクトの目的
**「自分が作ったRAGシステムと NotebookLM の違いを観察する」**

両システムを同じソース文書・同じ質問セットで評価し、構造的な違いを定量的に明らかにすることが目的です。

## 主な発見
- **単純な事実抽出ではほぼ同等**（v4: RAG 94%、v5: RAG 100%）
- **RAGの構造的弱点は表データで露呈**（v6: RAG 80% vs NotebookLM 100%）
- **表認識チャンキングで部分的に改善**（v7: RAG 90%）
- 詳細は [`evaluation/results/`](evaluation/results/) と [`RAG_vs_NotebookLM_report.pptx`](RAG_vs_NotebookLM_report.pptx) を参照

---

## 技術スタック

| レイヤー | 技術 |
|---------|------|
| 言語 | Python 3.11+ |
| ベクトルDB | ChromaDB（ローカル永続化） |
| Embedding | sentence-transformers + multilingual-e5-large（1024次元、100言語対応） |
| LLM | Google Gemini API（gemini-2.5-flash） |
| 文書取得 | requests + BeautifulSoup4 / WebFetch（事前取得後ローカル保存） |
| 設定管理 | python-dotenv |
| 開発手法 | cc-sdd（Kiro-style 仕様駆動開発） |

LLM選択の理由は [`.kiro/specs/claude-rag-qa/decisions/0001-llm-choice.md`](.kiro/specs/claude-rag-qa/decisions/0001-llm-choice.md) を参照。

---

## セットアップ

### 1. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### 2. APIキーの設定
[Google AI Studio](https://aistudio.google.com/apikey) でGemini APIキーを取得し、`.env` ファイルを作成：

```bash
cp .env.example .env
# .env を編集して GEMINI_API_KEY を入力
```

### 3. ソース文書の確認
`data/sources.json` に10ファイル分のメタデータが定義されています。実体は `data/docs/` にMarkdownとして保存済み：

```
data/docs/
├── models_overview.md
├── tool_use.md
├── vision.md
├── streaming.md
├── structured_outputs.md
├── extended_thinking.md
├── prompt_engineering.md
├── batch_processing.md
├── pdf_support.md
└── pricing.md
```

---

## 使い方

### ① 文書の取り込み（インジェスト）
```bash
python main.py ingest
```

`data/docs/` の10ファイルを読み込み、チャンク分割して ChromaDB に保存します。
初回実行時は multilingual-e5-large モデル（約560MB）をダウンロードするため数分かかります。

実行例:
```
取り込み完了: 10件のドキュメント, 313件のチャンク
```

### ② 単一質問への回答
```bash
python main.py ask "Claude Haiku 4.5の入力料金は1MTokあたりいくらですか？"
```

実行例:
```
回答:
Claude Haiku 4.5の入力トークン100万トークン（1MTok）あたりの料金は$1です。

ソース:
  - https://platform.claude.com/docs/ja/about-claude/pricing
```

### ③ 評価バッチ実行（10問一括）
```bash
python main.py evaluate
```

`data/qa_pairs.json` の10問を順番にRAGに投げ、結果を `evaluation/results/rag_results.json` に保存します。

---

## 評価実験の流れ

| バージョン | 実装内容 | 結果 |
|-----------|---------|:---:|
| v1 | 初期構成（all-MiniLM-L6-v2） | 84% |
| v2 | クエリ翻訳実験 | 78% ↓ |
| v3 | 距離フィルタ + multilingual-e5-large | 88% |
| v4 | 単一ソース事実抽出（質問刷新） | 94% |
| v5 | 複数ソース・計算問題 | 100% |
| v6 | RAG弱点特化（カウント・表算術） | 80% ↓ |
| **v7** | **表認識チャンキング** | **90%** |
| NotebookLM | (v6と同じ質問で比較) | **100%** |

各バージョンの詳細レポート: [`evaluation/results/`](evaluation/results/)

---

## ディレクトリ構造

```
rag-comparison/
├── CLAUDE.md                    # AI開発ガイドライン
├── README.md                    # このファイル
├── pyproject.toml / requirements.txt
├── main.py                      # CLIエントリポイント (ingest/ask/evaluate)
├── .env.example                 # 環境変数テンプレート
├── .kiro/                       # cc-sdd 仕様駆動開発
│   ├── steering/                # プロジェクト方針
│   └── specs/claude-rag-qa/
│       ├── spec.json            # 仕様メタデータ
│       ├── requirements.md      # 要件定義
│       ├── design.md            # 技術設計
│       ├── tasks.md             # 実装タスク
│       ├── research.md          # 技術調査ログ
│       └── decisions/           # ADR (Architecture Decision Records)
│           └── 0001-llm-choice.md
├── src/
│   ├── config.py                # 設定管理
│   ├── loader.py                # ドキュメント取得
│   ├── chunker.py               # テキスト分割（v7で表認識追加）
│   ├── vectorstore.py           # ChromaDB + multilingual-e5-large
│   └── rag.py                   # RAGパイプライン
├── data/
│   ├── sources.json             # ソースURL一覧
│   ├── qa_pairs.json            # 評価用Q&A 10問
│   ├── notebooklm_answers.json  # NotebookLM側の回答
│   └── docs/                    # ローカルMarkdown 10ファイル
├── tests/                       # pytest（63テスト）
├── evaluation/
│   ├── evaluate.py              # 評価ロジック
│   ├── scoring_rubric.md        # 採点基準（v3まで進化）
│   └── results/                 # v1〜v7 の評価結果と分析レポート
├── scripts/
│   └── generate_report.py       # PowerPoint レポート生成
└── RAG_vs_NotebookLM_report.pptx  # 最終発表スライド（17ページ）
```

---

## テスト
```bash
python -m pytest tests/ -v
```

63テストが通過することを確認できます。

---

## ライセンス・免責
- 本リポジトリは学習目的の実験プロジェクトです
- ソース文書は Anthropic 公式ドキュメントの取得時点のスナップショット
- Gemini API の利用には Google AI Studio のAPIキーが必要です
