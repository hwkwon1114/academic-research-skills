# Cross-Model Verification Protocol (v4.0)

## Overview

This protocol enables optional cross-model verification for high-stakes AI judgments within `deep-research`. When enabled, a second AI model independently reviews outputs from the primary model, reducing shared-bias blind spots.

**This is entirely optional.** `deep-research` works with Claude alone. Cross-model verification is an additional layer for users who want higher confidence in source verification and devil's advocate challenges.

## Why Cross-Model Verification

A stress test of 68 AI-generated citations found 31% had problems — and all passed three rounds of same-model integrity checks. The root cause: the verifying AI and the generating AI share the same training data distribution, so they share the same blind spots. A different model can catch errors that the primary model systematically misses.

**What it improves:** Error rate reduction (estimated 31% → ~5-10%). Different models catch different types of hallucination patterns.

**What it doesn't solve:** Frame-lock (all LLMs share most training data), sycophancy. These are degree improvements, not kind improvements.

## Supported Models

| Model | API ID | Provider | Best For |
|-------|--------|----------|----------|
| Claude Opus 4.6 | `claude-opus-4-6` | Anthropic | Primary model (default) |
| GPT-5.4 Pro | `gpt-5.4-pro` | OpenAI | Cross-verification — strongest reasoning |
| GPT-5.4 | `gpt-5.4` | OpenAI | Cross-verification — balanced cost/performance |
| Gemini 3.1 Pro | `gemini-3.1-pro-preview` | Google | Cross-verification — strong at factual verification |

## Setup

Add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
export OPENAI_API_KEY="sk-your-key-here"
export ARS_CROSS_MODEL="gpt-5.4-pro"  # or gemini-3.1-pro-preview
```

## How It Works in deep-research

### Source Verification (`source_verification_agent`)

**When `ARS_CROSS_MODEL` is set:**
- Primary model (Claude) runs full verification as normal.
- After primary verification completes, a random 30% sample of references is sent to the cross-model for independent verification.
- Cross-model receives only the reference text and context — not Claude's verification result (to prevent anchoring).
- Disagreements are flagged as `[CROSS-MODEL-DISAGREEMENT]` and highlighted in the report.

**When `ARS_CROSS_MODEL` is not set:**
- Standard single-model verification (unchanged).

### Devil's Advocate (`devils_advocate_agent`)

**When `ARS_CROSS_MODEL` is set:**
- After the DA completes its standard checkpoint, the cross-model receives the same material and generates an independent critique.
- Any CRITICAL or MAJOR issues found by the cross-model but not by the DA are added as `[CROSS-MODEL-FINDING]`.

**When `ARS_CROSS_MODEL` is not set:**
- Standard single-model DA (unchanged).

## API Call Patterns

### OpenAI

```bash
curl -s https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"$ARS_CROSS_MODEL"'",
    "messages": [
      {"role": "system", "content": "You are a verification assistant."},
      {"role": "user", "content": "'"$(echo "$PROMPT" | jq -Rs .)"'"}
    ],
    "temperature": 0.1,
    "max_tokens": 2000
  }' | jq -r '.choices[0].message.content'
```

### Google Gemini

```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models/${ARS_CROSS_MODEL}:generateContent?key=$GOOGLE_AI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contents": [{"parts": [{"text": "'"$(echo "$PROMPT" | jq -Rs .)"'"}]}],
    "generationConfig": {"temperature": 0.1, "maxOutputTokens": 2000}
  }' | jq -r '.candidates[0].content.parts[0].text'
```

## Graceful Degradation

If cross-model verification fails (API error, rate limit, key expired):
- Log: `[CROSS-MODEL-ERROR: reason]`
- Continue with single-model verification — never block on cross-model failure.
- Include a note in the report: "Cross-model verification was configured but unavailable for this run."
