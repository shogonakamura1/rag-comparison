# メッセージのストリーミング

---

メッセージを作成する際に、`"stream": true`を設定することで、[サーバー送信イベント](https://developer.mozilla.org/en-US/Web/API/Server-sent_events/Using_server-sent_events)（SSE）を使用してレスポンスをインクリメンタルにストリーミングできます。

## SDKを使用したストリーミング

[Python](https://github.com/anthropics/anthropic-sdk-python)および[TypeScript](https://github.com/anthropics/anthropic-sdk-typescript) SDKは、複数のストリーミング方法を提供しています。Python SDKは同期ストリームと非同期ストリームの両方をサポートしています。詳細は各SDKのドキュメントを参照してください。

## イベント処理なしで最終メッセージを取得する

テキストが到着するたびに処理する必要がない場合、SDKはストリーミングを内部で使用しながら、`.create()`が返すものと同一の完全な`Message`オブジェクトを返す方法を提供します。これは、`max_tokens`の値が大きいリクエストで特に便利で、SDKがHTTPタイムアウトを回避するためにストリーミングを必要とする場合に役立ちます。

`.stream()`呼び出しはサーバー送信イベントでHTTP接続を維持し、`.get_final_message()`（Python）または`.finalMessage()`（TypeScript）がすべてのイベントを蓄積して完全な`Message`オブジェクトを返します。イベント処理コードは不要です。

## イベントタイプ

各サーバー送信イベントには、名前付きイベントタイプと関連するJSONデータが含まれます。各イベントはSSEイベント名（例: `event: message_stop`）を使用し、データ内に一致するイベント`type`を含みます。

各ストリームは以下のイベントフローを使用します:

1. `message_start`: 空の`content`を持つ`Message`オブジェクトを含みます。
2. 一連のコンテンツブロック。各ブロックには`content_block_start`、1つ以上の`content_block_delta`イベント、および`content_block_stop`イベントがあります。各コンテンツブロックには、最終的なMessageの`content`配列内のインデックスに対応する`index`があります。
3. 1つ以上の`message_delta`イベント。最終的な`Message`オブジェクトのトップレベルの変更を示します。
4. 最終的な`message_stop`イベント。

`message_delta`イベントの`usage`フィールドに表示されるトークン数は*累積*です。

### Pingイベント

イベントストリームには、任意の数の`ping`イベントが含まれる場合があります。

### エラーイベント

イベントストリーム内で[エラー](/docs/ja/api/errors)が送信されることがあります。例えば、高負荷時には`overloaded_error`を受信する場合があり、これは非ストリーミングコンテキストではHTTP 529に対応します。

### その他のイベント

[バージョニングポリシー](/docs/ja/api/versioning)に従い、新しいイベントタイプを追加する場合があります。コードは未知のイベントタイプを適切に処理する必要があります。

## コンテンツブロックデルタタイプ

各`content_block_delta`イベントには、指定された`index`の`content`ブロックを更新するタイプの`delta`が含まれます。

### テキストデルタ

`text`コンテンツブロックデルタはテキストインクリメントを含みます。

### 入力JSONデルタ

`tool_use`コンテンツブロックのデルタは、ブロックの`input`フィールドの更新に対応します。最大の粒度をサポートするため、デルタは*部分的なJSON文字列*ですが、最終的な`tool_use.input`は常に*オブジェクト*です。

文字列デルタを蓄積し、`content_block_stop`イベントを受信した後にJSONを解析できます。[Pydantic](https://docs.pydantic.dev/latest/concepts/json/#partial-json-parsing)のようなライブラリを使用して部分的なJSON解析を行うか、解析済みのインクリメンタル値にアクセスするヘルパーを提供する[SDK](/docs/ja/api/client-sdks)を使用できます。

現在のモデルは、`input`から一度に1つの完全なキーと値のプロパティのみを出力することをサポートしています。そのため、ツールを使用する場合、モデルが処理中にストリーミングイベント間に遅延が発生する場合があります。`input`のキーと値が蓄積されると、チャンク化された部分的なJSONを含む複数の`content_block_delta`イベントとして出力されるため、将来のモデルでより細かい粒度を自動的にサポートできる形式になっています。

### 思考デルタ

ストリーミングを有効にした[拡張思考](/docs/ja/build-with-claude/extended-thinking#streaming-thinking)を使用する場合、`thinking_delta`イベントを通じて思考コンテンツを受信します。これらのデルタは、`thinking`コンテンツブロックの`thinking`フィールドに対応します。

思考コンテンツの場合、`content_block_stop`イベントの直前に特別な`signature_delta`イベントが送信されます。この署名は、思考ブロックの整合性を検証するために使用されます。

## 完全なHTTPストリームレスポンス

ストリーミングモードを使用する場合は、[クライアントSDK](/docs/ja/api/client-sdks)の使用を強くお勧めします。ただし、直接APIインテグレーションを構築する場合は、これらのイベントを自分で処理する必要があります。

ストリームレスポンスは以下で構成されます:

1. `message_start`イベント
2. 複数のコンテンツブロック（各ブロックには以下が含まれます）:
    - `content_block_start`イベント
    - 複数の`content_block_delta`イベント（可能性あり）
    - `content_block_stop`イベント
3. `message_delta`イベント
4. `message_stop`イベント

レスポンス全体を通じて`ping`イベントが散在する場合もあります。形式の詳細については[イベントタイプ](#event-types)を参照してください。

### 基本的なストリーミングリクエスト

基本的なストリーミングリクエストは、`message_start`、`content_block_start`、`content_block_delta`（テキスト増分を含む）、`content_block_stop`、`message_delta`、`message_stop`イベントのシーケンスを返します。

### ツール使用を伴うストリーミングリクエスト

ツール使用は、パラメータ値の[きめ細かいストリーミング](/docs/ja/agents-and-tools/tool-use/fine-grained-tool-streaming)をサポートしています。`eager_input_streaming`でツールごとに有効にできます。

ツール使用をストリーミングする場合、レスポンスには最初にテキストコンテンツブロックが含まれ、その後に`tool_use`コンテンツブロックが続き、`input_json_delta`イベントとして部分的なJSON文字列がストリーミングされます。

### 拡張思考を伴うストリーミングリクエスト

ストリーミングで拡張思考を有効にすると、Claudeのステップバイステップの推論を確認できます。レスポンスには最初に`thinking`コンテンツブロックが含まれ、`thinking_delta`イベントと最終的な`signature_delta`イベントが続き、その後にテキストコンテンツブロックが続きます。

### Web検索ツール使用を伴うストリーミングリクエスト

Web検索を有効にすると、レスポンスにはテキストブロック、`server_tool_use`ブロック（検索クエリを含む）、`web_search_tool_result`ブロック（検索結果を含む）、そしてレスポンスを含む最終的なテキストブロックが含まれます。

## エラーリカバリ

### Claude 4.5以前

Claude 4.5モデル以前の場合、ネットワークの問題、タイムアウト、またはその他のエラーにより中断されたストリーミングリクエストを、ストリームが中断された箇所から再開することでリカバリできます。このアプローチにより、レスポンス全体を再処理する必要がなくなります。

基本的なリカバリ戦略は以下の通りです:

1. **部分的なレスポンスをキャプチャする**: エラーが発生する前に正常に受信されたすべてのコンテンツを保存します
2. **継続リクエストを構築する**: 部分的なアシスタントレスポンスを新しいアシスタントメッセージの先頭として含む新しいAPIリクエストを作成します
3. **ストリーミングを再開する**: 中断された箇所からレスポンスの残りの受信を続けます

### Claude 4.6

Claude 4.6モデルの場合、中断された箇所から続行するようモデルに指示するユーザーメッセージを追加する必要があります。例えば:

```
Your previous response was interrupted and ended with [previous_response]. Continue from where you left off.
```

### エラーリカバリのベストプラクティス

1. **SDK機能を使用する**: SDKの組み込みメッセージ蓄積およびエラー処理機能を活用します
2. **コンテンツタイプを処理する**: メッセージには複数のコンテンツブロック（`text`、`tool_use`、`thinking`）が含まれる場合があることに注意してください。ツール使用と拡張思考ブロックは部分的にリカバリできません。最新のテキストブロックからストリーミングを再開できます。
