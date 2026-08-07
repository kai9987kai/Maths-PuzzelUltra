---
title: MathForge X Adaptive Mathematics Engine
emoji: ∑
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 6.5.1
app_file: app.py
pinned: false
---

# MathForge X — Adaptive Mathematics Engine

MathForge X is a deterministic procedural maths engine and adaptive tutor built with Gradio. It does not require an LLM, external API, model download, or API key.

## What changed in v2

- Expanded from 10 to 18 skill topics plus Mixed mode.
- Added a genuine adaptive tutor loop rather than calling a pre-generated worksheet “adaptive”.
- Browser-persistent per-topic mastery ratings using an Elo-style update model.
- Mastery-aware topic selection that increases sampling of weak and under-practised skills.
- Difficulty calibration from Beginner through Expert based on current mastery.
- Challenge bias control for gentler or stretch practice.
- Deterministic challenge IDs for reproducibility and debugging.
- Deterministic worked solutions and hints for every generated problem.
- Mistake diagnostics for sign errors, reciprocals, factor-of-100 errors, missing roots, reversed ordered pairs, near misses, and scientific-notation formatting mistakes.
- Multiple exact answer representations: scalar, ratio, set, ordered pair and scientific notation.
- Balanced, random, and mastery-aware mixed worksheet strategies.
- Generation audit with uniqueness, topic distribution and answer-representation checks.
- ZIP export containing printable HTML, TXT, CSV and JSON.
- Public Gradio API endpoints for generation, adaptive practice, reset, and export.
- Client-side BrowserState profile/history persistence.

## Topics

Arithmetic: addition, subtraction, multiplication, division, order of operations, averages.

Number: fractions, percentages, ratios and proportions, scientific notation, number theory, probability.

Algebra: powers and roots, sequences, absolute values, linear equations, simultaneous equations, quadratics.

## Adaptive model

Each skill begins at rating 1000. Problem bands are centred at ratings 800, 950, 1100, 1250 and 1400. After a scored answer, MathForge X updates that topic using an Elo-style expected-performance equation. Mixed adaptive practice weights lower-rated and under-sampled skills more heavily, while the difficulty selector targets the user’s current skill rating plus an optional challenge bias.

The profile is stored in Gradio `BrowserState`, so it is session/client-oriented rather than server-global.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```

## API

Important Gradio API names include:

- `generate_math_set_v2`
- `export_math_bundle_v2`
- `start_adaptive_session`
- `adaptive_check_answer`
- `next_adaptive_problem`
- `reset_mastery_profile`
- `generate_problem_objects`

## Design principle

MathForge X keeps generation algorithmic and inspectable. Every answer and solution is derived from the same parameters used to construct the question, which makes the system suitable for reproducible worksheets, automated testing, educational experiments, and local/offline-style deployments.
