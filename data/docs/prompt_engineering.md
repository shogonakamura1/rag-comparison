# Prompting Best Practices

Comprehensive guide to prompt engineering techniques for Claude's latest models.

## General Principles

### Be clear and direct
Claude responds well to clear, explicit instructions. Think of Claude as a brilliant but new employee who lacks context on your norms and workflows. The more precisely you explain what you want, the better the result. Golden rule: Show your prompt to a colleague with minimal context and ask them to follow it. If they'd be confused, Claude will be too.

### Add context to improve performance
Providing context or motivation behind your instructions can help Claude better understand your goals. Claude is smart enough to generalize from the explanation.

### Use examples effectively
Examples (few-shot or multishot prompting) are one of the most reliable ways to steer Claude's output format, tone, and structure. Include 3-5 examples for best results. Make them relevant, diverse, and structured with example tags.

### Structure prompts with XML tags
XML tags help Claude parse complex prompts unambiguously. Use consistent, descriptive tag names. Nest tags when content has a natural hierarchy.

### Give Claude a role
Setting a role in the system prompt focuses Claude's behavior and tone for your use case.

### Long context prompting
When working with large documents (20k+ tokens): put longform data at the top of prompts, structure document content with XML tags, and ground responses in quotes from the documents. Queries at the end can improve response quality by up to 30%.

## Output and Formatting

### Communication style
Claude's latest models are more direct, conversational, and less verbose. May skip verbal summaries after tool calls.

### Control response format
- Tell Claude what to do instead of what not to do
- Use XML format indicators
- Match your prompt style to the desired output
- Claude Opus 4.6 defaults to LaTeX for math expressions

## Tool Use
Claude's latest models benefit from explicit direction to use specific tools. Be explicit about taking action vs suggesting. Claude Opus 4.6 excels at parallel tool execution.

## Thinking and Reasoning
Claude Opus 4.6 does significantly more upfront exploration than previous models. Use adaptive thinking for workloads requiring agentic behavior. Prefer general instructions over prescriptive steps for thinking.

## Agentic Systems

### Long-horizon reasoning
Claude excels at long-horizon tasks with exceptional state tracking. Claude 4.6 features context awareness, enabling the model to track its remaining context window.

### Balancing autonomy and safety
Claude Opus 4.6 may take difficult-to-reverse actions without guidance. Add explicit instructions about confirming before risky actions.

### Subagent orchestration
Claude can recognize when tasks benefit from delegating to specialized subagents and does so proactively. Watch for overuse of subagents.
