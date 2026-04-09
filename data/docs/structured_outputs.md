# 構造化出力

エージェントワークフローから検証済みのJSON結果を取得する

---

構造化出力は、Claudeの応答を特定のスキーマに従うよう制約し、ダウンストリーム処理のための有効でパース可能な出力を保証します。2つの補完的な機能が利用可能です：

- **JSON出力** (`output_config.format`)：特定のJSON形式でClaudeの応答を取得する
- **厳格なツール使用** (`strict: true`)：ツール名と入力のスキーマ検証を保証する

これらの機能は、同じリクエストで独立して、または組み合わせて使用できます。

<Note>
構造化出力は、Claude Opus 4.6、Claude Sonnet 4.6、Claude Sonnet 4.5、Claude Opus 4.5、およびClaude Haiku 4.5向けのClaude APIおよびAmazon Bedrockで一般提供されています。構造化出力はMicrosoft Foundryではパブリックベータのままです。
</Note>

<Note>
This feature qualifies for [Zero Data Retention (ZDR)](/docs/en/build-with-claude/api-and-data-retention) with limited technical retention. See the [Data retention](#data-retention) section for details on what is retained and why.
</Note>

<Tip>
**ベータ版から移行する場合**`output_format`パラメータは`output_config.format`に移動し、ベータヘッダーは不要になりました。古いベータヘッダー（`structured-outputs-2025-11-13`）と`output_format`パラメータは移行期間中も引き続き機能します。更新されたAPIの形式については、以下のコード例を参照してください。
</Tip>

## 構造化出力を使用する理由

構造化出力がない場合、Claudeはアプリケーションを壊す不正なJSON応答や無効なツール入力を生成する可能性があります。慎重なプロンプト設計を行っても、以下のような問題が発生する可能性があります：
- 無効なJSON構文によるパースエラー
- 必須フィールドの欠落
- 一貫性のないデータ型
- エラー処理と再試行が必要なスキーマ違反

構造化出力は、制約付きデコーディングによってスキーマに準拠した応答を保証します：
- **常に有効**：`JSON.parse()`エラーはもう発生しない
- **型安全**：フィールド型と必須フィールドが保証される
- **信頼性が高い**：スキーマ違反のための再試行が不要

## JSON出力

JSON出力はClaudeの応答形式を制御し、スキーマに一致する有効なJSONをClaudeが返すことを保証します。JSON出力は以下の場合に使用します：

- Claudeの応答形式を制御する
- 画像やテキストからデータを抽出する
- 構造化されたレポートを生成する
- APIレスポンスをフォーマットする

### クイックスタート

<CodeGroup>

```bash Shell
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "messages": [
      {
        "role": "user",
        "content": "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm."
      }
    ],
    "output_config": {
      "format": {
        "type": "json_schema",
        "schema": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "email": {"type": "string"},
            "plan_interest": {"type": "string"},
            "demo_requested": {"type": "boolean"}
          },
          "required": ["name", "email", "plan_interest", "demo_requested"],
          "additionalProperties": false
        }
      }
    }
  }'
```

```python Python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm.",
        }
    ],
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "plan_interest": {"type": "string"},
                    "demo_requested": {"type": "boolean"},
                },
                "required": ["name", "email", "plan_interest", "demo_requested"],
                "additionalProperties": False,
            },
        }
    },
)
print(response.content[0].text)
```

```typescript TypeScript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content:
        "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm."
    }
  ],
  output_config: {
    format: {
      type: "json_schema",
      schema: {
        type: "object",
        properties: {
          name: { type: "string" },
          email: { type: "string" },
          plan_interest: { type: "string" },
          demo_requested: { type: "boolean" }
        },
        required: ["name", "email", "plan_interest", "demo_requested"],
        additionalProperties: false
      }
    }
  }
});
console.log(response.content[0].text);
```

```java Java
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.messages.*;

AnthropicClient client = AnthropicOkHttpClient.fromEnv();

// Java SDK uses class-based structured outputs
// See the Java SDK page for annotation-based approach
MessageCreateParams params = MessageCreateParams.builder()
    .model(Model.CLAUDE_OPUS_4_6)
    .maxTokens(1024)
    .addUserMessage("Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan.")
    .build();

Message message = client.beta().messages().create(params);
System.out.println(message.content());
```

```go Go
package main

import (
	"context"
	"fmt"

	"github.com/anthropics/anthropic-sdk-go"
)

func main() {
	client := anthropic.NewClient()

	response, _ := client.Messages.New(context.Background(),
		anthropic.MessageNewParams{
			Model:     anthropic.ModelClaudeOpus4_6,
			MaxTokens: 1024,
			Messages: []anthropic.MessageParam{
				anthropic.NewUserMessage(
					anthropic.NewTextBlock("Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan."),
				),
			},
			OutputConfig: anthropic.OutputConfigParam{
				Format: anthropic.JSONOutputFormatParam{
					Schema: map[string]interface{}{
						"type": "object",
						"properties": map[string]interface{}{
							"name":           map[string]string{"type": "string"},
							"email":          map[string]string{"type": "string"},
							"plan_interest":  map[string]string{"type": "string"},
							"demo_requested": map[string]string{"type": "boolean"},
						},
						"required":             []string{"name", "email", "plan_interest", "demo_requested"},
						"additionalProperties": false,
					},
				},
			},
		})

	fmt.Println(response.Content[0].Text)
}
```

```ruby Ruby
require "anthropic"

client = Anthropic::Client.new

response = client.messages.create(
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content: "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan."
    }
  ],
  output_config: {
    format: {
      type: "json_schema",
      schema: {
        type: "object",
        properties: {
          name: { type: "string" },
          email: { type: "string" },
          plan_interest: { type: "string" },
          demo_requested: { type: "boolean" }
        },
        required: ["name", "email", "plan_interest", "demo_requested"],
        additionalProperties: false
      }
    }
  }
)

puts response.content[0].text
```

```csharp C#
using Anthropic;

var client = new AnthropicClient();

var response = await client.Messages.CreateAsync(
    new MessageCreateParams
    {
        Model = "claude-opus-4-6",
        MaxTokens = 1024,
        Messages = new[]
        {
            new MessageParam
            {
                Role = "user",
                Content = "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan."
            }
        },
        OutputConfig = new OutputConfig
        {
            Format = new JsonOutputFormat
            {
                Type = "json_schema",
                Schema = new
                {
                    type = "object",
                    properties = new
                    {
                        name = new { type = "string" },
                        email = new { type = "string" },
                        plan_interest = new { type = "string" },
                        demo_requested = new { type = "boolean" }
                    },
                    required = new[] { "name", "email", "plan_interest", "demo_requested" },
                    additionalProperties = false
                }
            }
        }
    });

Console.WriteLine(response.Content[0].Text);
```

```php PHP
<?php

use Anthropic\Client;

$client = new Client(
    apiKey: getenv("ANTHROPIC_API_KEY")
);

$response = $client->beta->messages->create([
    'model' => 'claude-opus-4-6',
    'max_tokens' => 1024,
    'betas' => ['structured-outputs-2025-11-13'],
    'messages' => [
        [
            'role' => 'user',
            'content' => 'Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan.'
        ]
    ],
    'output_format' => [
        'type' => 'json_schema',
        'schema' => [
            'type' => 'object',
            'properties' => [
                'name' => ['type' => 'string'],
                'email' => ['type' => 'string'],
                'plan_interest' => ['type' => 'string'],
                'demo_requested' => ['type' => 'boolean']
            ],
            'required' => ['name', 'email', 'plan_interest', 'demo_requested'],
            'additionalProperties' => false
        ]
    ]
]);

echo $response->content[0]->text;
```

</CodeGroup>

**レスポンス形式：** `response.content[0].text`内のスキーマに一致する有効なJSON

```json
{
  "name": "John Smith",
  "email": "john@example.com",
  "plan_interest": "Enterprise",
  "demo_requested": true
}
```

### 仕組み

<Steps>
  <Step title="JSONスキーマを定義する">
    Claudeに従わせたい構造を記述するJSONスキーマを作成します。スキーマは標準のJSON Schema形式を使用しますが、いくつかの制限があります（[JSONスキーマの制限](#json-schema-limitations)を参照）。
  </Step>
  <Step title="output_config.formatパラメータを追加する">
    `type: "json_schema"`とスキーマ定義を含む`output_config.format`パラメータをAPIリクエストに含めます。
  </Step>
  <Step title="レスポンスをパースする">
    Claudeの応答は、`response.content[0].text`に返されるスキーマに一致する有効なJSONになります。
  </Step>
</Steps>

### SDKでのJSON出力の操作

SDKは、スキーマ変換、自動検証、人気のスキーマライブラリとの統合など、JSON出力の操作を容易にするヘルパーを提供します。

<Note>
SDKヘルパーメソッド（`.parse()`やPydantic/Zod統合など）は、便宜上のパラメータとして`output_format`を引き続き受け付けます。SDKは内部で`output_config.format`への変換を処理します。以下の例はSDKヘルパーの構文を示しています。
</Note>

#### ネイティブスキーマ定義の使用

生のJSONスキーマを記述する代わりに、使い慣れたスキーマ定義ツールを使用できます：

- **Python**: `client.messages.parse()`と[Pydantic](https://docs.pydantic.dev/)モデル
- **TypeScript**: `zodOutputFormat()`と[Zod](https://zod.dev/)スキーマ
- **Java**: `outputFormat(Class<T>)`による自動スキーマ導出を使用したプレーンJavaクラス
- **Ruby**: `output_config: {format: Model}`を使用した`Anthropic::BaseModel`クラス
- **C#**、**Go**、**PHP**: `output_config`経由で渡す生のJSONスキーマ

<CodeGroup>

```python Python
from pydantic import BaseModel
from anthropic import Anthropic


class ContactInfo(BaseModel):
    name: str
    email: str
    plan_interest: str
    demo_requested: bool


client = Anthropic()

response = client.messages.parse(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm.",
        }
    ],
    output_format=ContactInfo,
)

print(response.parsed_output)
```

```typescript TypeScript
import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";

const ContactInfoSchema = z.object({
  name: z.string(),
  email: z.string(),
  plan_interest: z.string(),
  demo_requested: z.boolean()
});

const client = new Anthropic();

const response = await client.messages.parse({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content:
        "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm."
    }
  ],
  output_config: { format: zodOutputFormat(ContactInfoSchema) }
});

// 型安全性が保証される
console.log(response.parsed_output.email);
```

```java Java
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.StructuredMessageCreateParams;
import com.anthropic.models.messages.Model;

class ContactInfo {
    public String name;
    public String email;
    public String planInterest;
    public boolean demoRequested;
}

AnthropicClient client = AnthropicOkHttpClient.fromEnv();

StructuredMessageCreateParams<ContactInfo> createParams = MessageCreateParams.builder()
  .model(Model.CLAUDE_OPUS_4_6)
  .maxTokens(1024)
  .outputFormat(ContactInfo.class)
  .addUserMessage("Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm.")
  .build();

var response = client.messages().create(createParams);
ContactInfo contact = response.output(ContactInfo.class);
System.out.println(contact.name + " (" + contact.email + ")");
```

```go Go
package main

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/anthropics/anthropic-sdk-go"
	"github.com/invopop/jsonschema"
)

type ContactInfo struct {
	Name          string `json:"name" jsonschema:"description=Full name"`
	Email         string `json:"email" jsonschema:"description=Email address"`
	PlanInterest  string `json:"plan_interest" jsonschema:"description=Plan type"`
	DemoRequested bool   `json:"demo_requested" jsonschema:"description=Whether a demo was requested"`
}

func generateSchema(v any) map[string]any {
	r := jsonschema.Reflector{AllowAdditionalProperties: false, DoNotReference: true}
	s := r.Reflect(v)
	b, _ := json.Marshal(s)
	var m map[string]any
	json.Unmarshal(b, &m)
	return m
}

func main() {
	client := anthropic.NewClient()
	schema := generateSchema(&ContactInfo{})

	message, _ := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
		Model:     anthropic.ModelClaudeOpus4_6,
		MaxTokens: 1024,
		Messages: []anthropic.MessageParam{
			anthropic.NewUserMessage(anthropic.NewTextBlock(
				"Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm.",
			)),
		},
		OutputConfig: anthropic.OutputConfigParam{
			Format: anthropic.JSONOutputFormatParam{
				Schema: schema,
			},
		},
	})

	var contact ContactInfo
	json.Unmarshal([]byte(message.Content[0].AsResponseTextBlock().Text), &contact)
	fmt.Printf("%s (%s)\n", contact.Name, contact.Email)
}
```

```ruby Ruby
require "anthropic"

client = Anthropic::Client.new

class ContactInfo < Anthropic::BaseModel
  required :name, String
  required :email, String
  required :plan_interest, String
  required :demo_requested, Anthropic::Boolean
end

message = client.messages.create(
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [{
    role: "user",
    content: "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm."
  }],
  output_config: {format: ContactInfo}
)

contact = message.parsed_output
puts "#{contact.name} (#{contact.email})"
```

```csharp C#
using System.Text.Json;
using Anthropic;
using Anthropic.Models.Messages;

var client = new AnthropicClient();

var response = await client.Messages.Create(new MessageCreateParams
{
    Model = "claude-opus-4-6",
    MaxTokens = 1024,
    Messages = [new() {
        Role = Role.User,
        Content = "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm."
    }],
    OutputConfig = new OutputConfig
    {
        Format = new JsonOutputFormat
        {
            Schema = new Dictionary<string, JsonElement>
            {
                ["type"] = JsonSerializer.SerializeToElement("object"),
                ["properties"] = JsonSerializer.SerializeToElement(new
                {
                    name = new { type = "string" },
                    email = new { type = "string" },
                    plan_interest = new { type = "string" },
                    demo_requested = new { type = "boolean" },
                }),
                ["required"] = JsonSerializer.SerializeToElement(
                    new[] { "name", "email", "plan_interest", "demo_requested" }),
                ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
            },
        },
    },
});

var json = (response.Content.First().Value as TextBlock)!.Text;
// JSONはスキーマに一致することが保証される
var contact = JsonSerializer.Deserialize<Dictionary<string, object>>(json);
Console.WriteLine($"{contact["name"]} ({contact["email"]})");
```

```php PHP
<?php

use Anthropic\Client;
use Anthropic\Messages\OutputConfig;
use Anthropic\Messages\JSONOutputFormat;

$client = new Client();

$response = $client->messages->create(
    maxTokens: 1024,
    messages: [
        ['role' => 'user', 'content' => 'Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan and wants to schedule a demo for next Tuesday at 2pm.'],
    ],
    model: 'claude-opus-4-6',
    outputConfig: OutputConfig::with(format: JSONOutputFormat::with(schema: [
        'type' => 'object',
        'properties' => [
            'name' => ['type' => 'string'],
            'email' => ['type' => 'string'],
            'plan_interest' => ['type' => 'string'],
            'demo_requested' => ['type' => 'boolean'],
        ],
        'required' => ['name', 'email', 'plan_interest', 'demo_requested'],
        'additionalProperties' => false,
    ])),
);

$data = json_decode($response->content[0]->text, true);
echo $data['name'] . ' (' . $data['email'] . ')';
```

</CodeGroup>

#### SDK固有のメソッド

各SDKは、構造化出力の操作を容易にするヘルパーを提供します。詳細については、各SDKのページを参照してください。

<Tabs>
<Tab title="Python">

**`client.messages.parse()`（推奨）**

`parse()`メソッドは、Pydanticモデルを自動的に変換し、レスポンスを検証して、`parsed_output`属性を返します。

<section title="使用例">

```python
from pydantic import BaseModel
import anthropic


class ContactInfo(BaseModel):
    name: str
    email: str
    plan_interest: str


client = anthropic.Anthropic()

response = client.messages.parse(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "..."}],
    output_format=ContactInfo,
)

# 解析済み出力に直接アクセス
contact = response.parsed_output
print(contact.name, contact.email)
```

</section>

**`transform_schema()`ヘルパー**

送信前にスキーマを手動で変換する必要がある場合、またはPydanticが生成したスキーマを変更したい場合に使用します。スキーマを自動的に変換する`client.messages.parse()`とは異なり、変換されたスキーマを返すのでさらにカスタマイズできます。

<section title="使用例">

```python
from anthropic import transform_schema
from pydantic import TypeAdapter

# まずPydanticモデルをJSONスキーマに変換し、次に変換する
schema = TypeAdapter(ContactInfo).json_schema()
schema = transform_schema(schema)
# 必要に応じてスキーマを変更
schema["properties"]["custom_field"] = {"type": "string"}

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "..."}],
    output_config={
        "format": {"type": "json_schema", "schema": schema},
    },
)
```

</section>

</Tab>
<Tab title="TypeScript">

**`zodOutputFormat()`を使用した`client.messages.parse()`**

`parse()`メソッドはZodスキーマを受け付け、レスポンスを検証し、スキーマに一致する推論されたTypeScript型を持つ`parsed_output`属性を返します。

<section title="使用例">

```typescript
import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";

const ContactInfo = z.object({
  name: z.string(),
  email: z.string(),
  planInterest: z.string()
});

const client = new Anthropic();

const response = await client.messages.parse({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "..." }],
  output_config: { format: zodOutputFormat(ContactInfo) }
});

// 型安全性が保証される
console.log(response.parsed_output.email);
```

</section>

</Tab>
<Tab title="Java">

**`outputFormat(Class<T>)`メソッド**

Javaクラスを`outputFormat()`に渡すと、SDKが自動的にJSONスキーマを導出し、検証して、`StructuredMessageCreateParams<T>`を返します。解析された結果には`response.output(Class<T>)`でアクセスします。

<section title="使用例">

```java
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.StructuredMessageCreateParams;
import com.anthropic.models.messages.Model;

class ContactInfo {
    public String name;
    public String email;
    public String planInterest;
}

StructuredMessageCreateParams<ContactInfo> createParams = MessageCreateParams.builder()
  .model(Model.CLAUDE_OPUS_4_6)
  .maxTokens(1024)
  .outputFormat(ContactInfo.class)
  .addUserMessage("...")
  .build();

var response = client.messages().create(createParams);
ContactInfo contact = response.output(ContactInfo.class);
System.out.println(contact.name + " (" + contact.email + ")");
```

</section>

<section title="ジェネリック型の消去">

フィールドのジェネリック型情報はクラスのメタデータに保持されますが、他のスコープではジェネリック型の消去が適用されます。`List<Book>`型の`BookList.books`フィールドからはJSONスキーマを導出できますが、同じ型のローカル変数からは有効なJSONスキーマを導出できません。

JSONレスポンスをJavaクラスインスタンスに変換する際にエラーが発生した場合、エラーメッセージには診断を支援するためのJSONレスポンスが含まれます。JSONレスポンスに機密情報が含まれる可能性がある場合は、直接ログに記録しないか、エラーメッセージから機密情報を削除してください。

</section>

<section title="ローカルスキーマ検証">

構造化出力は[JSONスキーマ言語のサブセット](/docs/ja/build-with-claude/structured-outputs#json-schema-limitations)をサポートしています。スキーマはこのサブセットに合わせてクラスから自動的に生成されます。`outputFormat(Class<T>)`メソッドは、指定されたクラスから導出されたスキーマの検証チェックを実行します。

主なポイント：

- **ローカル検証**はリモートAIモデルへのリクエストを送信せずに行われます。
- **リモート検証**もJSONスキーマを受信したAIモデルによって実行されます。
- **バージョン互換性**: SDKバージョンが古い場合、ローカル検証が失敗してもリモート検証が成功することがあります。
- **ローカル検証の無効化**: 互換性の問題が発生した場合は`JsonSchemaLocalValidation.NO`を渡してください：

```java
import com.anthropic.core.JsonSchemaLocalValidation;
import com.anthropic.models.beta.messages.MessageCreateParams;
import com.anthropic.models.beta.messages.StructuredMessageCreateParams;
import com.anthropic.models.messages.Model;

StructuredMessageCreateParams<BookList> createParams = MessageCreateParams.builder()
  .model(Model.CLAUDE_OPUS_4_6)
  .maxTokens(2048)
  .outputFormat(BookList.class, JsonSchemaLocalValidation.NO)
  .addUserMessage("List some famous late twentieth century novels.")
  .build();
```

</section>

<section title="ストリーミング">

構造化出力はストリーミングでも使用できます。レスポンスがストリームイベントとして届く際は、JSONをデシリアライズする前にレスポンス全体を蓄積する必要があります。

`BetaMessageAccumulator`を使用してストリームからJSONの文字列を収集します。蓄積が完了したら、`BetaMessageAccumulator.message(Class<T>)`を呼び出して蓄積された`BetaMessage`を`StructuredMessage`に変換します。これにより、JSONが自動的にJavaクラスにデシリアライズされます。

</section>

<section title="JSONスキーマのプロパティ">

JavaクラスからJSONスキーマが導出される際、デフォルトでは`public`フィールドまたは`public`ゲッターメソッドで表されるすべてのプロパティが含まれます。非`public`フィールドとゲッターメソッドは除外されます。

アノテーションで可視性を制御できます：

- `@JsonIgnore`は`public`フィールドまたはゲッターメソッドを除外します
- `@JsonProperty`は非`public`フィールドまたはゲッターメソッドを含めます

`public`ゲッターメソッドを持つ`private`フィールドを定義した場合、プロパティ名はゲッターから導出されます（例：`public`メソッド`getMyValue()`を持つ`private`フィールド`myValue`は`"myValue"`プロパティを生成します）。非慣例的なゲッター名を使用するには、メソッドに`@JsonProperty`アノテーションを付けてください。

各クラスはJSONスキーマに少なくとも1つのプロパティを定義する必要があります。以下の場合など、フィールドまたはゲッターメソッドがスキーマプロパティを生成できない場合は検証エラーが発生します：

- クラスにフィールドまたはゲッターメソッドがない
- すべての`public`メンバーに`@JsonIgnore`アノテーションが付いている
- すべての非`public`メンバーに`@JsonProperty`アノテーションがない
- フィールドが`Map`型を使用しており、空の`"properties"`フィールドを生成する

</section>

<section title="アノテーション（JacksonとSwagger）">

JacksonのDatabindアノテーションを使用して、Javaクラスから導出されたJSONスキーマを充実させることができます：

```java
import com.fasterxml.jackson.annotation.JsonClassDescription;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;

class Person {

  @JsonPropertyDescription("The first name and surname of the person")
  public String name;

  public int birthYear;

  @JsonPropertyDescription("The year the person died, or 'present' if the person is living.")
  public String deathYear;
}

@JsonClassDescription("The details of one published book")
class Book {

  public String title;
  public Person author;

  @JsonPropertyDescription("The year in which the book was first published.")
  public int publicationYear;

  @JsonIgnore
  public String genre;
}

class BookList {

  public List<Book> books;
}
```

アノテーションの概要：

- `@JsonClassDescription` -- クラスに説明を追加する
- `@JsonPropertyDescription` -- フィールドまたはゲッターメソッドに説明を追加する
- `@JsonIgnore` -- `public`フィールドまたはゲッターをスキーマから除外する
- `@JsonProperty` -- 非`public`フィールドまたはゲッターをスキーマに含める

`@JsonProperty(required = false)`を使用した場合、`false`の値は無視されます。AnthropicのJSONスキーマはすべてのプロパティを必須としてマークする必要があります。

型固有の制約にはOpenAPI Swagger 2の`@Schema`および`@ArraySchema`アノテーションも使用できます：

```java
import io.swagger.v3.oas.annotations.media.ArraySchema;
import io.swagger.v3.oas.annotations.media.Schema;

class Article {

  @ArraySchema(minItems = 1)
  public List<String> authors;

  public String title;

  @Schema(format = "date")
  public String publicationDate;

  @Schema(minimum = "1")
  public int pageCount;
}
```

ローカル検証では、サポートされていない制約キーワードを使用していないかチェックしますが、制約の値はローカルでは検証されません。例えば、サポートされていない`"format"`値はローカル検証を通過してもリモートエラーを引き起こす可能性があります。

JacksonとSwaggerの両方のアノテーションを使用して同じスキーマフィールドを設定した場合、Jacksonのアノテーションが優先されます。

</section>

</Tab>
<Tab title="Go">

**`OutputConfigParam`経由の生のJSONスキーマ**

Go SDKは生のJSONスキーマで動作します。jsonタグを持つGoの構造体を定義し、JSONスキーマを生成し（例えば`invopop/jsonschema`を使用）、レスポンステキストを構造体にアンマーシャルします。

<section title="使用例">

```go
package main

import (
	"context"
	"encoding/json"
	"fmt"

	"github.com/anthropics/anthropic-sdk-go"
	"github.com/invopop/jsonschema"
)

type ContactInfo struct {
	Name         string `json:"name" jsonschema:"description=Full name"`
	Email        string `json:"email" jsonschema:"description=Email address"`
	PlanInterest string `json:"plan_interest" jsonschema:"description=Plan type"`
}

func generateSchema(v any) map[string]any {
	r := jsonschema.Reflector{AllowAdditionalProperties: false, DoNotReference: true}
	s := r.Reflect(v)
	b, _ := json.Marshal(s)
	var m map[string]any
	json.Unmarshal(b, &m)
	return m
}

func main() {
	client := anthropic.NewClient()
	schema := generateSchema(&ContactInfo{})

	message, _ := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
		Model:     anthropic.ModelClaudeOpus4_6,
		MaxTokens: 1024,
		Messages: []anthropic.MessageParam{
			anthropic.NewUserMessage(anthropic.NewTextBlock(
				"Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan.",
			)),
		},
		OutputConfig: anthropic.OutputConfigParam{
			Format: anthropic.JSONOutputFormatParam{
				Schema: schema,
			},
		},
	})

	var contact ContactInfo
	json.Unmarshal([]byte(message.Content[0].AsResponseTextBlock().Text), &contact)
	fmt.Printf("%s (%s)\n", contact.Name, contact.Email)
}
```

</section>

</Tab>
<Tab title="Ruby">

**`parsed_output`を使用した`output_config: {format: Model}`**

`Anthropic::BaseModel`を継承したモデルクラスを定義し、`messages.create()`のformatとして渡します。レスポンスには型付きRubyオブジェクトを持つ`parsed_output`属性が含まれます。

<section title="使用例">

```ruby
require "anthropic"

class ContactInfo < Anthropic::BaseModel
  required :name, String
  required :email, String
  required :plan_interest, String
end

client = Anthropic::Client.new

message = client.messages.create(
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [{role: "user", content: "..."}],
  output_config: {format: ContactInfo}
)

contact = message.parsed_output
puts "#{contact.name} (#{contact.email})"
```

</section>

<section title="高度なモデル機能">

Ruby SDKは、より豊富なスキーマのための追加モデル定義機能をサポートしています：

- **`doc:`キーワード** -- より情報量の多いスキーマ出力のためにフィールドに説明を追加する
- **`Anthropic::ArrayOf[T]`** -- `min_length`と`max_length`制約を持つ型付き配列
- **`Anthropic::EnumOf[:a, :b]`** -- 制約された値を持つEnumフィールド
- **`Anthropic::UnionOf[T1, T2]`** -- `anyOf`にマッピングされるユニオン型

```ruby
class FamousNumber < Anthropic::BaseModel
  required :value, Float
  optional :reason, String, doc: "why is this number mathematically significant?"
end

class Output < Anthropic::BaseModel
  required :numbers, Anthropic::ArrayOf[FamousNumber], min_length: 3, max_length: 5
end

message = anthropic.messages.create(
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [{role: "user", content: "give me some famous numbers"}],
  output_config: {format: Output}
)

message.parsed_output
# => #<Output numbers=[#<FamousNumber value=3.14159... reason="Pi is...">...]>
```

</section>

</Tab>
<Tab title="C#">

**`OutputConfig`経由の生のJSONスキーマ**

C# SDKは`JsonSerializer.SerializeToElement`でプログラム的に構築された生のJSONスキーマを使用します。レスポンスのJSONは`JsonSerializer.Deserialize`でデシリアライズします。

<section title="使用例">

```csharp
using System.Text.Json;
using Anthropic;
using Anthropic.Models.Messages;

var client = new AnthropicClient();

var response = await client.Messages.Create(new MessageCreateParams
{
    Model = "claude-opus-4-6",
    MaxTokens = 1024,
    Messages = [new() {
        Role = Role.User,
        Content = "Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan."
    }],
    OutputConfig = new OutputConfig
    {
        Format = new JsonOutputFormat
        {
            Schema = new Dictionary<string, JsonElement>
            {
                ["type"] = JsonSerializer.SerializeToElement("object"),
                ["properties"] = JsonSerializer.SerializeToElement(new
                {
                    name = new { type = "string" },
                    email = new { type = "string" },
                    plan_interest = new { type = "string" },
                }),
                ["required"] = JsonSerializer.SerializeToElement(
                    new[] { "name", "email", "plan_interest" }),
                ["additionalProperties"] = JsonSerializer.SerializeToElement(false),
            },
        },
    },
});

var json = (response.Content.First().Value as TextBlock)!.Text;
// JSONはスキーマに一致することが保証される
var contact = JsonSerializer.Deserialize<Dictionary<string, object>>(json);
Console.WriteLine($"{contact["name"]} ({contact["email"]})");
```

</section>

</Tab>
<Tab title="PHP">

**`OutputConfig::with()`経由の生のJSONスキーマ**

PHP SDKは`OutputConfig::with()`経由で連想配列として生のJSONスキーマを渡します。レスポンスは`json_decode()`でデコードします。

<section title="使用例">

```php
<?php

use Anthropic\Client;
use Anthropic\Messages\OutputConfig;
use Anthropic\Messages\JSONOutputFormat;

$client = new Client();

$response = $client->messages->create(
    maxTokens: 1024,
    messages: [
        ['role' => 'user', 'content' => 'Extract the key information from this email: John Smith (john@example.com) is interested in our Enterprise plan.'],
    ],
    model: 'claude-opus-4-6',
    outputConfig: OutputConfig::with(format: JSONOutputFormat::with(schema: [
        'type' => 'object',
        'properties' => [
            'name' => ['type' => 'string'],
            'email' => ['type' => 'string'],
            'plan_interest' => ['type' => 'string'],
        ],
        'required' => ['name', 'email', 'plan_interest'],
        'additionalProperties' => false,
    ])),
);

$data = json_decode($response->content[0]->text, true);
echo $data['name'] . ' (' . $data['email'] . ')';
```

</section>

</Tab>
</Tabs>

#### SDK変換の仕組み

PythonとTypeScriptのSDKは、サポートされていない機能を持つスキーマを自動的に変換します：

1. **サポートされていない制約を削除**（例：`minimum`、`maximum`、`minLength`、`maxLength`）
2. **制約情報で説明を更新**（例：「少なくとも100以上である必要があります」）、構造化出力で直接サポートされていない制約の場合
3. **すべてのオブジェクトに`additionalProperties: false`を追加**
4. **文字列フォーマットをサポートされているリストのみにフィルタリング**
5. **元のスキーマに対してレスポンスを検証**（すべての制約を含む）

これにより、Claudeは簡略化されたスキーマを受け取りますが、コードは検証を通じてすべての制約を引き続き適用します。

**例：** `minimum: 100`を持つPydanticフィールドは、送信されるスキーマではプレーンな整数になりますが、説明は「少なくとも100以上である必要があります」に更新され、SDKは元の制約に対してレスポンスを検証します。

### 一般的なユースケース

<section title="データ抽出">

非構造化テキストから構造化データを抽出する：

<CodeGroup>

```python Python
from pydantic import BaseModel
from typing import List


class Invoice(BaseModel):
    invoice_number: str
    date: str
    total_amount: float
    line_items: List[dict]
    customer_name: str


response = client.messages.parse(
    model="claude-opus-4-6",
    output_format=Invoice,
    messages=[
        {"role": "user", "content": f"Extract invoice data from: {invoice_text}"}
    ],
)
```

```typescript TypeScript
import { z } from "zod";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";

const InvoiceSchema = z.object({
  invoice_number: z.string(),
  date: z.string(),
  total_amount: z.number(),
  line_items: z.array(z.record(z.string(), z.any())),
  customer_name: z.string()
});

const response = await client.messages.create({
  model: "claude-opus-4-6",
  output_config: { format: zodOutputFormat(InvoiceSchema) },
  messages: [{ role: "user", content: `Extract invoice data from: ${invoiceText}` }]
});
```

</CodeGroup>

</section>

<section title="分類">

構造化されたカテゴリでコンテンツを分類する：

<CodeGroup>

```python Python
from pydantic import BaseModel
from typing import List


class Classification(BaseModel):
    category: str
    confidence: float
    tags: List[str]
    sentiment: str


response = client.messages.parse(
    model="claude-opus-4-6",
    output_format=Classification,
    messages=[{"role": "user", "content": f"Classify this feedback: {feedback_text}"}],
)
```

```typescript TypeScript
import { z } from "zod";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";

const ClassificationSchema = z.object({
  category: z.string(),
  confidence: z.number(),
  tags: z.array(z.string()),
  sentiment: z.string()
});

const response = await client.messages.create({
  model: "claude-opus-4-6",
  output_config: { format: zodOutputFormat(ClassificationSchema) },
  messages: [{ role: "user", content: `Classify this feedback: ${feedbackText}` }]
});
```

</CodeGroup>

</section>

<section title="APIレスポンスのフォーマット">

API対応のレスポンスを生成する：

<CodeGroup>

```python Python
from pydantic import BaseModel
from typing import List, Optional


class APIResponse(BaseModel):
    status: str
    data: dict
    errors: Optional[List[dict]]
    metadata: dict


response = client.messages.parse(
    model="claude-opus-4-6",
    output_format=APIResponse,
    messages=[{"role": "user", "content": "Process this request: ..."}],
)
```

```typescript TypeScript
import { z } from "zod";
import { zodOutputFormat } from "@anthropic-ai/sdk/helpers/zod";

const APIResponseSchema = z.object({
  status: z.string(),
  data: z.record(z.string(), z.any()),
  errors: z.array(z.record(z.string(), z.any())).optional(),
  metadata: z.record(z.string(), z.any())
});

const response = await client.messages.create({
  model: "claude-opus-4-6",
  output_config: { format: zodOutputFormat(APIResponseSchema) },
  messages: [{ role: "user", content: "Process this request: ..." }]
});
```

</CodeGroup>

</section>

## 厳格なツール使用

厳格なツール使用はツールパラメータを検証し、Claudeが正しく型付けされた引数で関数を呼び出すことを保証します。以下の場合に厳格なツール使用を使用してください：

- ツールパラメータを検証する
- エージェントワークフローを構築する
- 型安全な関数呼び出しを保証する
- ネストされたプロパティを持つ複雑なツールを処理する

### エージェントにとって厳格なツール使用が重要な理由

信頼性の高いエージェントシステムを構築するには、スキーマへの準拠が保証される必要があります。厳格モードがない場合、Claudeは互換性のない型（`2`の代わりに`"2"`）や必須フィールドの欠落を返す可能性があり、関数が壊れてランタイムエラーが発生します。

厳格なツール使用は型安全なパラメータを保証します：
- 関数は毎回正しく型付けされた引数を受け取る
- ツール呼び出しを検証して再試行する必要がない
- 大規模で一貫して動作する本番対応エージェント

例えば、予約システムが`passengers: int`を必要とするとします。厳格モードがない場合、Claudeは`passengers: "two"`や`passengers: "2"`を提供する可能性があります。`strict: true`を使用すると、レスポンスには常に`passengers: 2`が含まれます。

### クイックスタート

<CodeGroup>

```bash Shell
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "messages": [
      {"role": "user", "content": "What is the weather in San Francisco?"}
    ],
    "tools": [{
      "name": "get_weather",
      "description": "Get the current weather in a given location",
      "strict": true,
      "input_schema": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA"
          },
          "unit": {
            "type": "string",
            "enum": ["celsius", "fahrenheit"]
          }
        },
        "required": ["location"],
        "additionalProperties": false
      }
    }]
  }'
```

```python Python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "What's the weather like in San Francisco?"}],
    tools=[
        {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "strict": True,  # 厳格モードを有効化
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The unit of temperature, either 'celsius' or 'fahrenheit'",
                    },
                },
                "required": ["location"],
                "additionalProperties": False,
            },
        }
    ],
)
print(response.content)
```

```typescript TypeScript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY
});

const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content: "What's the weather like in San Francisco?"
    }
  ],
  tools: [
    {
      name: "get_weather",
      description: "Get the current weather in a given location",
      strict: true, // 厳格モードを有効化
      input_schema: {
        type: "object",
        properties: {
          location: {
            type: "string",
            description: "The city and state, e.g. San Francisco, CA"
          },
          unit: {
            type: "string",
            enum: ["celsius", "fahrenheit"]
          }
        },
        required: ["location"],
        additionalProperties: false
      }
    }
  ]
});
console.log(response.content);
```

</CodeGroup>

**レスポンス形式：** `response.content[x].input`に検証済み入力を持つツール使用ブロック

```json
{
  "type": "tool_use",
  "name": "get_weather",
  "input": {
    "location": "San Francisco, CA"
  }
}
```

**保証事項：**
- ツールの`input`は`input_schema`に厳密に従う
- ツールの`name`は常に有効（提供されたツールまたはサーバーツールから）

### 仕組み

<Steps>
  <Step title="ツールスキーマを定義する">
    ツールの`input_schema`のJSONスキーマを作成します。スキーマは標準のJSONスキーマ形式を使用しますが、いくつかの制限があります（[JSONスキーマの制限](#json-schema-limitations)を参照）。
  </Step>
  <Step title="strict: trueを追加する">
    ツール定義のトップレベルプロパティとして`"strict": true`を設定します。`name`、`description`、`input_schema`と並べて設定します。
  </Step>
  <Step title="ツール呼び出しを処理する">
    Claudeがツールを使用する際、tool_useブロックの`input`フィールドは`input_schema`に厳密に従い、`name`は常に有効になります。
  </Step>
</Steps>

### 一般的なユースケース

<section title="検証済みツール入力">

ツールパラメータがスキーマと完全に一致することを確認します：

<CodeGroup>

```python Python
response = client.messages.create(
    model="claude-opus-4-6",
    messages=[{"role": "user", "content": "Search for flights to Tokyo"}],
    tools=[
        {
            "name": "search_flights",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string"},
                    "departure_date": {"type": "string", "format": "date"},
                    "passengers": {
                        "type": "integer",
                        "enum": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    },
                },
                "required": ["destination", "departure_date"],
                "additionalProperties": False,
            },
        }
    ],
)
```

```typescript TypeScript
const response = await client.messages.create({
  model: "claude-opus-4-6",
  messages: [{ role: "user", content: "Search for flights to Tokyo" }],
  tools: [
    {
      name: "search_flights",
      strict: true,
      input_schema: {
        type: "object",
        properties: {
          destination: { type: "string" },
          departure_date: { type: "string", format: "date" },
          passengers: { type: "integer", enum: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] }
        },
        required: ["destination", "departure_date"],
        additionalProperties: false
      }
    }
  ]
});
```

</CodeGroup>

</section>

<section title="複数の検証済みツールを使用したエージェントワークフロー">

保証されたツールパラメータで信頼性の高いマルチステップエージェントを構築します：

<CodeGroup>

```python Python
response = client.messages.create(
    model="claude-opus-4-6",
    messages=[{"role": "user", "content": "Help me plan a trip to Paris for 2 people"}],
    tools=[
        {
            "name": "search_flights",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string"},
                    "destination": {"type": "string"},
                    "departure_date": {"type": "string", "format": "date"},
                    "travelers": {"type": "integer", "enum": [1, 2, 3, 4, 5, 6]},
                },
                "required": ["origin", "destination", "departure_date"],
                "additionalProperties": False,
            },
        },
        {
            "name": "search_hotels",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "check_in": {"type": "string", "format": "date"},
                    "guests": {"type": "integer", "enum": [1, 2, 3, 4]},
                },
                "required": ["city", "check_in"],
                "additionalProperties": False,
            },
        },
    ],
)
```

```typescript TypeScript
const response = await client.messages.create({
  model: "claude-opus-4-6",
  messages: [{ role: "user", content: "Help me plan a trip to Paris for 2 people" }],
  tools: [
    {
      name: "search_flights",
      strict: true,
      input_schema: {
        type: "object",
        properties: {
          origin: { type: "string" },
          destination: { type: "string" },
          departure_date: { type: "string", format: "date" },
          travelers: { type: "integer", enum: [1, 2, 3, 4, 5, 6] }
        },
        required: ["origin", "destination", "departure_date"],
        additionalProperties: false
      }
    },
    {
      name: "search_hotels",
      strict: true,
      input_schema: {
        type: "object",
        properties: {
          city: { type: "string" },
          check_in: { type: "string", format: "date" },
          guests: { type: "integer", enum: [1, 2, 3, 4] }
        },
        required: ["city", "check_in"],
        additionalProperties: false
      }
    }
  ]
});
```

</CodeGroup>

</section>

## 両機能を組み合わせて使用する

JSON出力とストリクトツールユースは異なる問題を解決するものであり、組み合わせて使用できます：

- **JSON出力**はClaudeのレスポンス形式を制御します（Claudeが何を言うか）
- **ストリクトツールユース**はツールパラメータを検証します（ClaudeがどのようにあなたのFunctionを呼び出すか）

組み合わせることで、Claudeは保証された有効なパラメータでツールを呼び出し、かつ構造化されたJSONレスポンスを返すことができます。これは、信頼性の高いツール呼び出しと構造化された最終出力の両方が必要なエージェントワークフローに役立ちます。

<CodeGroup>

```python Python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Help me plan a trip to Paris for next month"}
    ],
    # JSON出力：構造化されたレスポンス形式
    output_config={
        "format": {
            "type": "json_schema",
            "schema": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "next_steps": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["summary", "next_steps"],
                "additionalProperties": False,
            },
        }
    },
    # ストリクトツールユース：保証されたツールパラメータ
    tools=[
        {
            "name": "search_flights",
            "strict": True,
            "input_schema": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string"},
                    "date": {"type": "string", "format": "date"},
                },
                "required": ["destination", "date"],
                "additionalProperties": False,
            },
        }
    ],
)
```

```typescript TypeScript
const response = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Help me plan a trip to Paris for next month" }],
  // JSON出力：構造化されたレスポンス形式
  output_config: {
    format: {
      type: "json_schema",
      schema: {
        type: "object",
        properties: {
          summary: { type: "string" },
          next_steps: { type: "array", items: { type: "string" } }
        },
        required: ["summary", "next_steps"],
        additionalProperties: false
      }
    }
  },
  // ストリクトツールユース：保証されたツールパラメータ
  tools: [
    {
      name: "search_flights",
      strict: true,
      input_schema: {
        type: "object",
        properties: {
          destination: { type: "string" },
          date: { type: "string", format: "date" }
        },
        required: ["destination", "date"],
        additionalProperties: false
      }
    }
  ]
});
```

</CodeGroup>

## 重要な考慮事項

### 文法のコンパイルとキャッシュ

構造化出力は、コンパイルされた文法アーティファクトを使用した制約付きサンプリングを使用します。これにより、注意すべきいくつかのパフォーマンス特性が生じます：

- **初回リクエストのレイテンシ**：特定のスキーマを初めて使用する場合、文法がコンパイルされる間に追加のレイテンシが発生します
- **自動キャッシュ**：コンパイルされた文法は最終使用から24時間キャッシュされ、後続のリクエストが大幅に高速化されます
- **キャッシュの無効化**：以下を変更するとキャッシュが無効化されます：
  - JSONスキーマ構造
  - リクエスト内のツールセット（構造化出力とツールユースの両方を使用する場合）
  - `name`または`description`フィールドのみの変更ではキャッシュは無効化されません

### プロンプトの変更とトークンコスト

構造化出力を使用する場合、Claudeは期待される出力形式を説明する追加のシステムプロンプトを自動的に受け取ります。これは以下を意味します：

- 入力トークン数がわずかに増加します
- 注入されたプロンプトは他のシステムプロンプトと同様にトークンコストが発生します
- `output_config.format`パラメータを変更すると、その会話スレッドの[プロンプトキャッシュ](/docs/ja/build-with-claude/prompt-caching)が無効化されます

### JSONスキーマの制限

構造化出力は標準のJSONスキーマをサポートしていますが、いくつかの制限があります。JSON出力とストリクトツールユースの両方がこれらの制限を共有します。

<section title="サポートされている機能">

- すべての基本型：object、array、string、integer、number、boolean、null
- `enum`（文字列、数値、ブール値、またはnullのみ - 複合型は不可）
- `const`
- `anyOf`および`allOf`（制限あり - `$ref`を使用した`allOf`はサポートされていません）
- `$ref`、`$def`、および`definitions`（外部`$ref`はサポートされていません）
- すべてのサポートされている型の`default`プロパティ
- `required`および`additionalProperties`（オブジェクトには`false`に設定する必要があります）
- 文字列フォーマット：`date-time`、`time`、`date`、`duration`、`email`、`hostname`、`uri`、`ipv4`、`ipv6`、`uuid`
- 配列の`minItems`（値0と1のみサポート）

</section>

<section title="サポートされていない機能">

- 再帰的スキーマ
- enum内の複合型
- 外部`$ref`（例：`'$ref': 'http://...'`）
- 数値制約（`minimum`、`maximum`、`multipleOf`など）
- 文字列制約（`minLength`、`maxLength`）
- `minItems`が0または1を超える配列制約
- `false`以外に設定された`additionalProperties`

サポートされていない機能を使用すると、詳細を含む400エラーが返されます。

</section>

<section title="パターンサポート（正規表現）">

**サポートされている正規表現機能：**
- 完全マッチング（`^...$`）と部分マッチング
- 量指定子：`*`、`+`、`?`、単純な`{n,m}`ケース
- 文字クラス：`[]`、`.`、`\d`、`\w`、`\s`
- グループ：`(...)`

**サポートされていない機能：**
- グループへの後方参照（例：`\1`、`\2`）
- 先読み/後読みアサーション（例：`(?=...)`、`(?!...)`）
- 単語境界：`\b`、`\B`
- 大きな範囲を持つ複雑な`{n,m}`量指定子

単純な正規表現パターンは正常に機能します。複雑なパターンは400エラーになる場合があります。

</section>

<Tip>
PythonおよびTypeScript SDKは、サポートされていない機能を持つスキーマを、それらを削除してフィールドの説明に制約を追加することで自動的に変換できます。詳細については[SDK固有のメソッド](#sdk-specific-methods)を参照してください。
</Tip>

### プロパティの順序

構造化出力を使用する場合、オブジェクト内のプロパティはスキーマで定義された順序を維持しますが、重要な注意点があります：**必須プロパティが最初に表示され、その後にオプションのプロパティが続きます**。

例えば、このスキーマが与えられた場合：

```json
{
  "type": "object",
  "properties": {
    "notes": { "type": "string" },
    "name": { "type": "string" },
    "email": { "type": "string" },
    "age": { "type": "integer" }
  },
  "required": ["name", "email"],
  "additionalProperties": false
}
```

出力はプロパティを以下の順序で並べます：

1. `name`（必須、スキーマ順）
2. `email`（必須、スキーマ順）
3. `notes`（オプション、スキーマ順）
4. `age`（オプション、スキーマ順）

つまり、出力は次のようになります：

```json
{
  "name": "John Smith",
  "email": "john@example.com",
  "notes": "Interested in enterprise plan",
  "age": 35
}
```

出力のプロパティ順序がアプリケーションにとって重要な場合は、すべてのプロパティを必須としてマークするか、解析ロジックでこの並べ替えを考慮してください。

### 無効な出力

構造化出力はほとんどの場合にスキーマへの準拠を保証しますが、出力がスキーマと一致しない可能性があるシナリオがあります：

**拒否**（`stop_reason: "refusal"`）

Claudeは構造化出力を使用する場合でも、安全性と有用性のプロパティを維持します。Claudeが安全上の理由でリクエストを拒否した場合：

- レスポンスには`stop_reason: "refusal"`が含まれます
- 200ステータスコードが返されます
- 生成されたトークンに対して課金されます
- 拒否メッセージがスキーマ制約より優先されるため、出力がスキーマと一致しない場合があります

**トークン制限に達した場合**（`stop_reason: "max_tokens"`）

`max_tokens`制限に達してレスポンスが切り捨てられた場合：

- レスポンスには`stop_reason: "max_tokens"`が含まれます
- 出力が不完全でスキーマと一致しない場合があります
- 完全な構造化出力を得るために、より高い`max_tokens`値で再試行してください

### スキーマの複雑さの制限

構造化出力は、JSONスキーマをClaudeの出力を制約する文法にコンパイルすることで機能します。より複雑なスキーマはより大きな文法を生成し、コンパイルに時間がかかります。過度なコンパイル時間を防ぐため、APIはいくつかの複雑さの制限を適用します。

#### 明示的な制限

以下の制限は、`output_config.format`または`strict: true`を使用するすべてのリクエストに適用されます：

| 制限 | 値 | 説明 |
|-------|-------|-------------|
| リクエストごとのストリクトツール数 | 20 | `strict: true`を持つツールの最大数。非ストリクトツールはこの制限にカウントされません。 |
| オプションパラメータ | 24 | すべてのストリクトツールスキーマとJSON出力スキーマにわたるオプションパラメータの合計。`required`にリストされていない各パラメータがこの制限にカウントされます。 |
| ユニオン型を持つパラメータ | 16 | すべてのストリクトスキーマにわたって`anyOf`または型配列（例：`"type": ["string", "null"]`）を使用するパラメータの合計。これらは指数関数的なコンパイルコストを生み出すため、特にコストがかかります。 |

<Note>
これらの制限は、単一リクエスト内のすべてのストリクトスキーマにわたる合計に適用されます。例えば、それぞれ6つのオプションパラメータを持つ4つのストリクトツールがある場合、単一のツールが複雑に見えなくても、24パラメータの制限に達します。
</Note>

#### 追加の内部制限

上記の明示的な制限に加えて、コンパイルされた文法サイズに関する追加の内部制限があります。これらの制限が存在するのは、スキーマの複雑さが単一の次元に還元されないためです：オプションパラメータ、ユニオン型、ネストされたオブジェクト、ツールの数などの機能が互いに影響し合い、コンパイルされた文法が不均衡に大きくなる可能性があります。

これらの制限を超えると、「Schema is too complex for compilation.」というメッセージとともに400エラーが返されます。これらのエラーは、上記の個々の制限がすべて満たされていても、スキーマの組み合わせた複雑さが効率的にコンパイルできる範囲を超えていることを意味します。最終的な安全策として、APIは**180秒のコンパイルタイムアウト**も適用します。すべての明示的なチェックをパスしても非常に大きなコンパイル済み文法を生成するスキーマは、このタイムアウトに達する可能性があります。

#### スキーマの複雑さを減らすためのヒント

複雑さの制限に達している場合は、以下の戦略を順番に試してください：

1. **重要なツールのみをストリクトとしてマークする。** 多くのツールがある場合は、スキーマ違反が実際の問題を引き起こすツールに限定し、よりシンプルなツールにはClaudeの自然な準拠に頼ってください。

2. **オプションパラメータを減らす。** 可能な限りパラメータを`required`にしてください。各オプションパラメータは文法の状態空間の一部をほぼ2倍にします。パラメータに常に合理的なデフォルト値がある場合は、必須にしてClaudeがそのデフォルトを明示的に提供するようにすることを検討してください。

3. **ネストされた構造を簡素化する。** オプションフィールドを持つ深くネストされたオブジェクトは複雑さを複合させます。可能な限り構造をフラット化してください。

4. **複数のリクエストに分割する。** 多くのストリクトツールがある場合は、別々のリクエストまたはサブエージェントに分割することを検討してください。

有効なスキーマで継続的な問題が発生する場合は、スキーマ定義とともに[サポートに連絡](https://support.claude.com/en/articles/9015913-how-to-get-support)してください。

## データ保持

構造化出力を使用する場合、プロンプトとレスポンスはZDRで処理されます。ただし、JSONスキーマ自体は最適化のために最終使用から最大24時間一時的にキャッシュされます。プロンプトまたはレスポンスデータはAPIレスポンスを超えて保持されません。

すべての機能にわたるZDRの適格性については、[APIとデータ保持](/docs/ja/build-with-claude/api-and-data-retention)を参照してください。

## 機能の互換性

**動作する機能：**
- **[バッチ処理](/docs/ja/build-with-claude/batch-processing)**：50%割引でスケールで構造化出力を処理
- **[トークンカウント](/docs/ja/build-with-claude/token-counting)**：コンパイルなしでトークンをカウント
- **[ストリーミング](/docs/ja/build-with-claude/streaming)**：通常のレスポンスと同様に構造化出力をストリーム
- **組み合わせ使用**：同じリクエストでJSON出力（`output_config.format`）とストリクトツールユース（`strict: true`）を一緒に使用

**互換性のない機能：**
- **[引用](/docs/ja/build-with-claude/citations)**：引用はテキストに引用ブロックを挿入する必要があり、厳格なJSONスキーマ制約と競合します。`output_config.format`で引用が有効になっている場合は400エラーが返されます。
- **メッセージプリフィリング**：JSON出力と互換性がありません

<Tip>
**文法のスコープ**：文法はClaudeの直接出力にのみ適用され、ツールユース呼び出し、ツール結果、または思考タグ（[拡張思考](/docs/ja/build-with-claude/extended-thinking)を使用する場合）には適用されません。文法の状態はセクション間でリセットされ、Claudeが自由に思考しながら最終レスポンスで構造化出力を生成できます。
</Tip>