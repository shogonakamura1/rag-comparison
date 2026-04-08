# Constitutional AI: Harmlessness from AI Feedback

## Overview

Anthropic's research explores training harmless AI assistants through self-improvement mechanisms without requiring human labels for harmful outputs. The approach relies on a list of rules or principles to guide the process, termed Constitutional AI.

## What is Constitutional AI?

Constitutional AI (CAI) is a method developed by Anthropic for training AI systems to be helpful, harmless, and honest. Instead of relying solely on human feedback to identify harmful outputs, CAI uses a set of principles (a "constitution") that the AI uses to evaluate and improve its own responses.

The key innovation is that the AI itself generates feedback based on these principles, reducing the need for extensive human labeling of harmful content while achieving better safety outcomes.

## Methodology

The training process comprises two phases:

### Supervised Learning Phase
- Sample responses from an initial model
- Have the model generate self-critiques of its own responses based on constitutional principles
- Have the model generate revised responses that address the critiques
- Fine-tune the original model on the revised responses

### Reinforcement Learning Phase (RLAIF)
- Sample responses from the fine-tuned model
- Use another AI model to evaluate which responses are better according to the constitution
- Train a preference model from these AI-generated preferences
- Apply reinforcement learning using the preference model as a reward signal

This is called RLAIF (Reinforcement Learning from AI Feedback), as opposed to RLHF (Reinforcement Learning from Human Feedback).

## Key Results

The method produces a harmless but non-evasive AI assistant that engages with harmful queries by explaining its objections to them. Both training phases leverage chain-of-thought reasoning to enhance transparency and performance.

Unlike models trained purely with RLHF, Constitutional AI models can explain why they decline certain requests rather than simply refusing, leading to more helpful and educational interactions even when the model cannot comply with a request.

## Significance

This approach enables control of AI behavior more precisely and with far fewer human labels, representing a meaningful advance in AI alignment methodology. It demonstrates that AI systems can be trained to follow nuanced behavioral guidelines through self-supervision, potentially scaling safety training more effectively than human-feedback-only approaches.

## Content Policy and Safety

Claude's content policy is built on Constitutional AI principles. Claude is designed to:
- Refuse to generate violent, illegal, or discriminatory content
- Prevent inappropriate use of personal information
- Honestly communicate uncertainty about information
- Suppress the spread of misinformation
- Engage thoughtfully with sensitive topics rather than simply refusing all discussion

Related Publication: https://arxiv.org/abs/2212.08073
