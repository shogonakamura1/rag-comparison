# Project Structure

```
rag-comparison/
├── CLAUDE.md                 # AI開発ガイドライン
├── README.md                 # プロジェクト説明
├── .kiro/
│   ├── steering/             # プロジェクト方針
│   │   ├── product.md
│   │   ├── tech.md
│   │   └── structure.md
│   └── specs/                # 機能仕様
├── src/
│   ├── __init__.py
│   ├── loader.py             # URL文書の取得・パース
│   ├── chunker.py            # テキスト分割
│   ├── vectorstore.py        # ChromaDB操作
│   ├── rag.py                # RAGパイプライン
│   └── config.py             # 設定管理
├── data/
│   ├── sources.json          # ソースURL一覧
│   └── qa_pairs.json         # Q&Aペア
├── evaluation/
│   ├── evaluate.py           # 評価スクリプト
│   └── results/              # 比較結果
├── requirements.txt
├── pyproject.toml
└── .env.example              # API キー設定例
```
