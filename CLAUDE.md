# AI-DLC と 仕様駆動開発

AI-DLC（AI Development Life Cycle）上で実装する Kiro スタイルの仕様駆動開発（Spec-Driven Development）

## プロジェクトコンテキスト

### パス
- ステアリング: `.kiro/steering/`
- 仕様（Spec）: `.kiro/specs/`

### ステアリングと仕様の違い

**ステアリング**（`.kiro/steering/`）- プロジェクト全体のルールやコンテキストで AI を導く
**仕様**（`.kiro/specs/`）- 個別機能ごとの開発プロセスを形式化する

### アクティブな仕様
- アクティブな仕様は `.kiro/specs/` を確認する
- 進捗確認には `/kiro:spec-status [feature-name]` を使用する

## 開発ガイドライン
- 思考は英語で行い、応答は日本語で生成すること。プロジェクトファイルに書き込む Markdown コンテンツ（例: requirements.md, design.md, tasks.md, research.md, バリデーションレポート）は、該当仕様に設定された言語（`spec.json.language` を参照）で必ず記述すること。

## 最小ワークフロー
- Phase 0（任意）: `/kiro:steering`, `/kiro:steering-custom`
- Phase 1（仕様策定）:
  - `/kiro:spec-init "description"`
  - `/kiro:spec-requirements {feature}`
  - `/kiro:validate-gap {feature}`（任意: 既存コードベース向け）
  - `/kiro:spec-design {feature} [-y]`
  - `/kiro:validate-design {feature}`（任意: 設計レビュー）
  - `/kiro:spec-tasks {feature} [-y]`
- Phase 2（実装）: `/kiro:spec-impl {feature} [tasks]`
  - `/kiro:validate-impl {feature}`（任意: 実装後の検証）
- 進捗確認: `/kiro:spec-status {feature}`（いつでも使用可能）

## 開発ルール
- 3 段階の承認ワークフロー: 要件定義 → 設計 → タスク → 実装
- 各フェーズで人によるレビューが必須。`-y` は意図的なファストトラック時のみ使用すること
- ステアリングは常に最新に保ち、`/kiro:spec-status` で整合性を確認すること
- ユーザーの指示には忠実に従い、その範囲内では自律的に行動すること。必要なコンテキストを収集し、依頼された作業をこの実行内でエンドツーエンドに完遂する。質問は、不可欠な情報が欠けている場合や指示が致命的に曖昧な場合のみ行うこと。
- 指示通りに開発を終え、適切なタイミングでGitにコミットし、リモートにプッシュを行うこと。

## ステアリング設定
- `.kiro/steering/` 全体をプロジェクトメモリとしてロードする
- デフォルトファイル: `product.md`, `tech.md`, `structure.md`
- カスタムファイルもサポート（`/kiro:steering-custom` で管理）
