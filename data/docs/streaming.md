# Streaming Messages

When creating a Message, you can set "stream": true to incrementally stream the response using server-sent events (SSE).

## Streaming with SDKs

The Python and TypeScript SDKs offer multiple ways of streaming. The PHP SDK provides streaming via createStream(). The Python SDK allows both sync and async streams.

## How streaming works

Streaming uses Server-Sent Events (SSE) to deliver response tokens incrementally as they are generated, rather than waiting for the complete response. This allows applications to display partial results in real-time, improving perceived responsiveness.

When streaming is enabled, the API sends a series of events:
1. message_start - Contains the initial Message object with metadata
2. content_block_start - Signals the beginning of a content block
3. content_block_delta - Contains incremental text updates (the actual generated tokens)
4. content_block_stop - Signals the end of a content block
5. message_delta - Contains final message-level data like stop_reason and usage
6. message_stop - Signals the end of the stream

## Event types

Each streaming event has a specific type and associated data:

- message_start: Includes the full Message object (without content) containing id, model, role, and initial usage information.
- content_block_start: Contains the index and initial content block (e.g., text block with empty text).
- content_block_delta: Contains the delta with incremental text additions. For text blocks, this includes a text_delta with the new text chunk.
- content_block_stop: Signals completion of a content block at a given index.
- message_delta: Contains the final delta with stop_reason (e.g., "end_turn") and final output token usage.
- message_stop: The final event signaling the complete end of the streaming response.

## Benefits of streaming

- Improved user experience: Users see responses appearing in real-time rather than waiting for the full response
- Lower perceived latency: The time-to-first-token is much shorter than time-to-complete-response
- Progressive rendering: Chat UIs can display text as it arrives, similar to human typing
- Early termination: Applications can choose to stop processing the stream early if needed

## Basic streaming request

To enable streaming, set stream to true in your Messages API request. The response will be delivered as a series of SSE events rather than a single JSON response.
