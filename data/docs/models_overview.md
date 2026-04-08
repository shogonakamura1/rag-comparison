# Models overview

Claude is a family of state-of-the-art large language models developed by Anthropic. This guide introduces the available models and compares their performance.

## Choosing a model

If you're unsure which model to use, consider starting with Claude Opus 4.6 for the most complex tasks. It is the most intelligent broadly available model with exceptional performance in coding and reasoning.

All current Claude models support text and image input, text output, multilingual capabilities, and vision. Models are available via the Claude API, AWS Bedrock, and Google Vertex AI.

### Latest models comparison

| Feature | Claude Opus 4.6 | Claude Sonnet 4.6 | Claude Haiku 4.5 |
|:--------|:----------------|:------------------|:-----------------|
| Description | The most intelligent broadly available model for agents and coding | The best combination of speed and intelligence | The fastest model with near-frontier intelligence |
| Claude API ID | claude-opus-4-6 | claude-sonnet-4-6 | claude-haiku-4-5-20251001 |
| Pricing | $5 / input MTok, $25 / output MTok | $3 / input MTok, $15 / output MTok | $1 / input MTok, $5 / output MTok |
| Extended thinking | Yes | Yes | Yes |
| Adaptive thinking | Yes | Yes | No |
| Comparative latency | Moderate | Fast | Fastest |
| Context window | 1M tokens (~750k words) | 1M tokens (~750k words) | 200k tokens (~150k words) |
| Max output | 128k tokens | 64k tokens | 64k tokens |
| Reliable knowledge cutoff | May 2025 | Aug 2025 | Feb 2025 |
| Training data cutoff | Aug 2025 | Jan 2026 | Jul 2025 |

## Legacy models

The following models are still available. Consider migrating to current models for improved performance:

| Feature | Claude Sonnet 4.5 | Claude Opus 4.5 | Claude Opus 4.1 | Claude Sonnet 4 | Claude Opus 4 |
|:--------|:------------------|:----------------|:----------------|:----------------|:--------------|
| Pricing | $3 / input MTok, $15 / output MTok | $5 / input MTok, $25 / output MTok | $15 / input MTok, $75 / output MTok | $3 / input MTok, $15 / output MTok | $15 / input MTok, $75 / output MTok |
| Extended thinking | Yes | Yes | Yes | Yes | Yes |
| Context window | 200k tokens | 200k tokens | 200k tokens | 200k tokens | 200k tokens |
| Max output | 64k tokens | 64k tokens | 32k tokens | 64k tokens | 32k tokens |

Claude 3.5 Sonnet was a previous generation model known for its excellent balance of intelligence and speed at an affordable price point. It excelled at coding, data analysis, and text generation tasks with strong cost performance.

Claude 3 Haiku was the fastest and most cost-effective model in the Claude 3 family, ideal for chatbots, real-time translation, and simple classification tasks requiring low latency.

## Prompt and output performance

Claude 4 models excel in:
- Performance: Top-tier results in reasoning, coding, multilingual tasks, long-context handling, honesty, and image processing.
- Engaging responses: Claude models are ideal for applications that require rich, human-like interactions.
- Output quality: When migrating from previous model generations to Claude 4, you may notice larger improvements in overall performance.
