# Pricing

## Model Pricing

| Model | Base Input Tokens | Output Tokens |
|-------|------------------|---------------|
| Claude Opus 4.6 | $5 / MTok | $25 / MTok |
| Claude Opus 4.5 | $5 / MTok | $25 / MTok |
| Claude Opus 4.1 | $15 / MTok | $75 / MTok |
| Claude Opus 4 | $15 / MTok | $75 / MTok |
| Claude Sonnet 4.6 | $3 / MTok | $15 / MTok |
| Claude Sonnet 4.5 | $3 / MTok | $15 / MTok |
| Claude Sonnet 4 | $3 / MTok | $15 / MTok |
| Claude Haiku 4.5 | $1 / MTok | $5 / MTok |
| Claude Haiku 3.5 | $0.80 / MTok | $4 / MTok |
| Claude Haiku 3 | $0.25 / MTok | $1.25 / MTok |

MTok = Million tokens.

## Prompt Caching Pricing

| Cache operation | Multiplier | Duration |
|----------------|-----------|----------|
| 5-minute cache write | 1.25x base input price | 5 minutes |
| 1-hour cache write | 2x base input price | 1 hour |
| Cache read (hit) | 0.1x base input price | Same as write duration |

Cache hit costs 10% of standard input price. Caching pays off after one read for 5-minute, two reads for 1-hour duration.

## Batch Processing Pricing

50% discount on both input and output tokens for asynchronous batch processing.

| Model | Batch input | Batch output |
|-------|------------|-------------|
| Claude Opus 4.6 | $2.50 / MTok | $12.50 / MTok |
| Claude Sonnet 4.6 | $1.50 / MTok | $7.50 / MTok |
| Claude Haiku 4.5 | $0.50 / MTok | $2.50 / MTok |

## Fast Mode Pricing

Fast mode for Claude Opus 4.6 provides faster output at 6x standard rates: $30/MTok input, $150/MTok output.

## Tool Pricing

- Web search: $10 per 1,000 searches plus standard token costs
- Web fetch: No additional charges beyond standard token costs
- Code execution: Free when used with web search/fetch. Otherwise $0.05/hour per container (1,550 free hours/month)
- Bash tool: Adds 245 input tokens per call
- Text editor tool: Adds 700 input tokens per call
- Computer use: 735 input tokens per tool definition

## Long Context Pricing

Opus 4.6 and Sonnet 4.6 include the full 1M token context window at standard pricing. No premium for longer inputs.

## Third-Party Platforms

Available on AWS Bedrock, Google Vertex AI, and Microsoft Foundry. Regional endpoints include a 10% premium over global endpoints (for Claude 4.5+ models).

## Rate Limits

Rate limits vary by usage tier (Tier 1-4 and Enterprise). Enterprise customers can negotiate custom limits.
