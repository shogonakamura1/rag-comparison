# Tech Stack

## 言語
- Python 3.11+

## 主要ライブラリ
- **ChromaDB**: ローカルベクトルデータベース（類似検索）+ 内蔵Embedding（all-MiniLM-L6-v2）
- **Google Generative AI SDK**: Gemini APIによるLLM回答生成
- **BeautifulSoup4 + requests**: Webページからのテキスト抽出

## 方針
- フレームワーク（LangChain等）は使わず、手動でRAGパイプラインを構築する
- 各コンポーネントを自前で実装し、仕組みを理解する

## アーキテクチャ
```
URL → requests+BS4 → テキスト分割(手動) → ChromaDB(内蔵Embedding)
                                                                    ↓
質問 → ChromaDB検索(内蔵Embedding) → 関連チャンク取得 → Gemini API → 回答
```

## 開発ツール
- Git: バージョン管理
- uv/pip: パッケージ管理
