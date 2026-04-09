# Extended Thinking

Extended thinking gives Claude enhanced reasoning capabilities for complex tasks with transparency into its step-by-step thought process before delivering final answers.

## Key Features
- Claude creates thinking content blocks with internal reasoning
- API responses include thinking blocks followed by text blocks
- Compatible with all Claude models with model-specific behaviors

## Supported Models
- Claude Mythos Preview: Uses adaptive thinking by default
- Claude Opus 4.6 & Claude Sonnet 4.6: Adaptive thinking recommended; manual mode deprecated
- All other Claude models: Extended thinking supported

## How to Enable
Add a thinking object to your API request with type set to "enabled" and budget_tokens specifying maximum tokens for internal reasoning (must be less than max_tokens). For Opus 4.6/Sonnet 4.6, use type "adaptive" instead.

## Summarized Thinking
For Claude 4 models, thinking is summarized by default. You are charged for full thinking tokens generated, not the summary. The display field controls thinking visibility: "summarized" returns summarized thinking (default), "omitted" returns empty thinking field with encrypted signature for faster streaming.

## Extended Thinking with Tool Use
Extended thinking works alongside tool use with limitations: only supports tool_choice auto or none, and thinking blocks must be preserved when passing tool results back.

## Interleaved Thinking
With tool use, Claude can think between tool calls. Claude Opus 4.6 uses adaptive thinking for automatic interleaved thinking. With interleaved thinking, budget_tokens can exceed max_tokens.

## Key Limitations
1. Cannot toggle thinking mid-turn during tool use loops
2. Tool choice limited to "auto" or "none"
3. Thinking blocks must be preserved when continuing conversations with tools
4. budget_tokens deprecated on Opus 4.6/Sonnet 4.6 (use adaptive thinking instead)

## Costs
Charged for full thinking tokens (not summaries). Summarized output incurs overhead from summarization model. Omitted display reduces latency, not cost.
