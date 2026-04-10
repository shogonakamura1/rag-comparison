# ADR-0001: 回答生成LLMにGemini APIを採用

- **ステータス**: 承認済み
- **決定日**: 2026-04-08
- **決定者**: プロジェクトオーナー（中村）

## コンテキスト
本プロジェクト「claude-rag-qa」は **Claudeの公式ドキュメントをソースに、Google NotebookLMと比較する** RAGシステムを構築する実験である。当初の設計では、ドメインとの親和性を考慮して回答生成LLMに **Anthropic Claude API** を採用する予定だった。

しかし以下の制約・要件から再検討が必要になった：
1. **コスト**: 学生の個人プロジェクトのため、無料または低コストで使える選択肢が望ましい
2. **APIキー入手のしやすさ**: 当時 Anthropic API は支払い設定が必要だった
3. **NotebookLMとの構造的差異の観察が主目的**: ソースドメインがClaudeであっても、回答生成LLMがClaudeである必然性はない

## 決定
回答生成LLMに **Google Gemini API（gemini-2.5-flash）** を採用する。

## 採用理由
| 観点 | Claude API | **Gemini API** |
|------|:---:|:---:|
| 無料利用枠 | △（要支払い設定） | **◎（無料枠あり）** |
| APIキー入手 | やや手間 | **Google AI Studio で即時** |
| 日本語性能 | ◎ | **◎** |
| RAG用途の性能 | ◎ | **◎** |
| ソースとの一貫性 | ◎（Claudeドキュメント） | △ |

「ソースの一貫性」は失われるが、本実験の目的は **「RAGとNotebookLMの比較」** であり、回答生成LLMの選択は本質的な変数ではない（むしろ Gemini を採用することで、NotebookLMの裏側で動いているとされる Gemini 系モデルに条件を近づけることができ、フェアな比較になる）。

## 影響範囲
| ファイル | 内容 |
|---------|------|
| `src/rag.py` | `google.generativeai` を使用、`gemini-2.5-flash` モデル |
| `src/config.py` | `gemini_api_key` フィールド |
| `requirements.txt` | `google-generativeai` を追加 |
| `.env.example` | `GEMINI_API_KEY` を記載 |
| `.kiro/specs/claude-rag-qa/requirements.md` | 要件4.1 を「Gemini API」に統一 |
| `.kiro/specs/claude-rag-qa/design.md` | LLM選択について本ADRへの参照を追加 |

## 実験中に発生した補足事項
- **2026-04-09**: `gemini-2.0-flash` が新規ユーザーには利用不可になったため、`gemini-2.5-flash` に変更
- **2026-04-08〜09**: 無料枠のクォータ制限に当たることがあったが、評価実行は問題なく完了

## 結果
- 6世代（v1〜v7）の評価実験を全て Gemini API で完遂
- v6で NotebookLM との比較を実施し、構造的な違いを観察できた
- 「RAGとNotebookLMの違い」という本来の研究目的は達成された

## 関連
- [requirements.md - 要件4](../requirements.md)
- [design.md - 技術スタック](../design.md)
- [research.md - 技術調査ログ](../research.md)
