# Batch Processing

Batch processing allows you to submit multiple requests together for asynchronous processing, useful for large volumes of data, non-time-sensitive tasks, and cost optimization.

## How the Message Batches API Works

1. The system creates a new Message Batch with the provided Messages requests
2. The batch is processed asynchronously, with each request handled independently
3. You can poll for the status of the batch and retrieve results when processing has ended

Useful for: large-scale evaluations, content moderation, data analysis, and generating insights for large datasets.

## Key Features

- 50% discount on both input and output tokens compared to standard API pricing
- Most batches finish in less than 1 hour
- Each request in the batch is processed independently
- Results can be retrieved when all requests have completed

## Batch Processing Limits

- Maximum 100,000 requests per batch
- Batches expire after 24 hours if not completed
- Results are available for 29 days after batch completion

## Extended Output

On the Message Batches API, Opus 4.6 and Sonnet 4.6 support up to 300k output tokens by using the output-300k-2026-03-24 beta header.

## Pricing

| Model | Batch input | Batch output |
|-------|------------|-------------|
| Claude Opus 4.6 | $2.50 / MTok | $12.50 / MTok |
| Claude Sonnet 4.6 | $1.50 / MTok | $7.50 / MTok |
| Claude Haiku 4.5 | $0.50 / MTok | $2.50 / MTok |

This represents a 50% discount compared to standard API pricing.
