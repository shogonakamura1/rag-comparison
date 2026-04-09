# Constitutional AI: Harmlessness from AI Feedback

## Overview

Anthropic's research explores methods for training AI systems to be helpful and harmless through self-improvement mechanisms, without requiring extensive human labeling of harmful outputs.

## Key Approach

The methodology relies on a constitution—a set of rules or principles—to guide AI behavior. The training process unfolds in two primary phases:

### Supervised Learning Phase
- Sample outputs from an initial model
- Generate self-critiques of problematic responses
- Create revised, improved versions
- Finetune the original model on these corrections

### Reinforcement Learning Phase
- Sample from the refined model
- Use AI evaluation to compare output pairs
- Build a preference dataset from AI judgments
- Train a preference model as reward signal
- Apply reinforcement learning based on AI feedback (RLAIF)

## Outcomes

The resulting system demonstrates the ability to engage with difficult queries by explaining its reasoning rather than simply refusing to engage. Both training phases leverage chain-of-thought reasoning to enhance performance transparency and human evaluation.

## Significance

This approach enables more precise behavioral control with substantially fewer human annotations, addressing a key challenge in AI alignment research.
