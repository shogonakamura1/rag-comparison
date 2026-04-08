# Tool use with Claude

Connect Claude to external tools and APIs. Learn where tools execute and how the agentic loop works.

Tool use lets Claude call functions you define or that Anthropic provides. Claude decides when to call a tool based on the user's request and the tool's description, then returns a structured call that your application executes (client tools) or that Anthropic executes (server tools).

## How tool use works

Tools differ primarily by where the code executes. Client tools (including user-defined tools and Anthropic-schema tools like bash and text_editor) run in your application: Claude responds with stop_reason: "tool_use" and one or more tool_use blocks, your code executes the operation, and you send back a tool_result. Server tools (web_search, code_execution, web_fetch, tool_search) run on Anthropic's infrastructure: you see the results directly without handling execution.

You can guarantee schema conformance with strict tool use by adding strict: true to your tool definitions to ensure Claude's tool calls always match your schema exactly.

Tool access is one of the highest-leverage primitives you can give an agent. On benchmarks like LAB-Bench FigQA (scientific figure interpretation) and SWE-bench (real-world software engineering), adding even basic tools produces outsized capability gains, often surpassing human expert baselines.

## Tool use for defining custom functions

Claude can be given custom tool definitions using JSON Schema to define input parameters. When Claude determines it needs to use a tool, it returns a structured tool_use block with the tool name and input parameters as JSON. Your application then executes the function and returns the result via a tool_result block.

This enables Claude to interact with external APIs, databases, search engines, calculators, and any other service you want to integrate. Claude handles the decision of when to call a tool and what parameters to provide.

## What happens when Claude needs more information

If the user's prompt doesn't include enough information to fill all the required parameters for a tool, Claude Opus is much more likely to recognize that a parameter is missing and ask for it. Claude Sonnet may ask, especially when prompted to think before outputting a tool request. But it may also do its best to infer a reasonable value.

## Pricing

Tool use requests are priced based on:
1. The total number of input tokens sent to the model (including in the tools parameter)
2. The number of output tokens generated
3. For server-side tools, additional usage-based pricing (e.g., web search charges per search performed)

Client-side tools are priced the same as any other Claude API request, while server-side tools may incur additional charges based on their specific usage.
