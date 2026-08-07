# MathForge X

**Adaptive procedural mathematics engine and Gradio tutor with 18 skill areas, Elo-style mastery tracking, mistake diagnosis, deterministic challenge IDs, worked solutions, and multi-format worksheet export.**

MathForge X is a local-first mathematics generation and tutoring system built in Python with Gradio. It generates reproducible questions algorithmically, verifies answers against the same parameters used to construct each problem, adapts practice to topic-level performance, and produces both interactive tutoring sessions and printable worksheet bundles.

It requires **no LLM, external model, API key, or cloud inference service**.

## Highlights

- **18 mathematical skill areas + Mixed mode** across arithmetic, number and algebra.
- **Five difficulty bands** from Beginner through Expert.
- **Adaptive Tutor** with per-topic mastery ratings and Elo-style updates.
- **Weak-skill targeting** that increases practice on low-rated and under-sampled topics.
- **Challenge bias** for gentler review or stretch practice.
- **Deterministic generation** using seeds and stable challenge IDs.
- **Worked solutions and hints** generated from the problem construction parameters.
- **Mistake diagnostics** for common answer patterns such as sign errors, reciprocals, percentage ×100 errors, missing quadratic roots and reversed ordered pairs.
- **Multiple answer representations**, including scalars, ratios, sets, ordered pairs and scientific notation.
- **Balanced, random and mastery-aware worksheet strategies**.
- **Worksheet auditing** for uniqueness, topic distribution and answer representation.
- **ZIP exports** containing printable HTML, TXT, CSV and JSON.
- **Browser-persistent learning profile** using Gradio `BrowserState`.
- **Public Gradio API endpoints** for programmatic generation and adaptive practice.

## Topics

| Domain | Skills |
|---|---|
| Arithmetic | Addition, subtraction, multiplication, division, order of operations, averages |
| Number | Fractions, percentages, ratios & proportions, scientific notation, number theory, probability |
| Algebra | Powers & roots, sequences, absolute values, linear equations, simultaneous equations, quadratics |

## How the adaptive engine works

Each skill starts with a mastery rating of **1000**. MathForge X maps problem difficulty to approximate rating bands and updates the relevant topic after each scored response using an Elo-style expected-performance model.

When the tutor is in Mixed mode, topic selection is not uniformly random. The scheduler weights:

1. lower-rated skills,
2. under-practised skills,
3. the requested challenge bias, and
4. the learner's recent response history.

This produces a genuine feedback loop: the next problem is selected after the previous result is known rather than generating a supposedly “adaptive” worksheet in advance.

## Deterministic generation

A problem contains a reproducible challenge ID derived from its generated structure. Generation is seedable, making MathForge X useful for:

- repeatable classroom worksheets,
- automated regression tests,
- benchmark datasets,
- debugging individual questions,
- educational experiments, and
- offline/local deployments.

## Mistake diagnosis

Incorrect answers are analysed for recognizable mathematical error patterns. Depending on the problem representation, the engine can identify or flag patterns including:

- sign errors,
- reciprocal/inversion errors,
- percentage scale errors,
- missing quadratic roots,
- reversed `(x, y)` solutions,
- near-miss arithmetic,
- scientific-notation formatting issues.

These diagnostics are heuristic teaching signals rather than claims about a learner's reasoning process.

## Installation

### Requirements

- Python 3.10+ recommended
- Gradio 6.5+

```bash
git clone https://github.com/kai9987kai/Maths-PuzzelUltra.git
cd Maths-PuzzelUltra
git switch mathforge-x
pip install -r requirements.txt
```

## Run

```bash
python app.py
```

Gradio will print the local application URL in the terminal.

## Tests

Run the deterministic smoke/property suite:

```bash
python test_engine.py
```

The current test suite checks:

- every topic across every difficulty band,
- generated answer equivalence,
- problem metadata completeness,
- mixed-set uniqueness and skill coverage,
- adaptive mastery updates,
- mistake diagnosis,
- bundle export generation.

During development, the engine passed **1,800 generated-answer verification checks**, a **100-question mixed uniqueness/coverage test**, adaptive-state tests and export tests.

## Gradio API

Important named endpoints include:

- `generate_math_set_v2`
- `export_math_bundle_v2`
- `start_adaptive_session`
- `adaptive_check_answer`
- `next_adaptive_problem`
- `reset_mastery_profile`
- `generate_problem_objects`

These make the UI useful as both an interactive application and a programmatically callable mathematics engine.

## Project structure

```text
.
├── app.py                       # Gradio UI and public API wiring
├── mathforge_core.py            # Configuration, state and problem schema
├── mathforge_generators.py      # Procedural mathematical generators
├── mathforge_evaluation.py      # Answer parsing, equivalence and diagnostics
├── mathforge_worksheet.py       # Worksheet strategies, audits and exports
├── mathforge_adaptive.py        # Mastery model and adaptive tutoring loop
├── test_engine.py               # Deterministic smoke/property tests
├── requirements.txt             # Runtime dependency constraints
├── PROJECT_DESCRIPTION.md       # Concise repository description
├── HF_SPACE_README.md           # Hugging Face Space metadata/documentation
└── .gitignore
```

## Hugging Face Space deployment

`HF_SPACE_README.md` preserves the Gradio Space front matter. To deploy on Hugging Face, use it as the Space repository's `README.md` together with the Python modules and `requirements.txt`.

## Design principles

MathForge X is deliberately inspectable. Instead of asking a language model to invent a question and separately guess its answer, the generator constructs the mathematical object first and derives the displayed question, expected answer, hint and worked solution from the same source parameters.

That architecture improves reproducibility, testability and answer consistency while keeping the system lightweight enough to run locally.

## Status

**MathForge X v2.0** — active experimental educational software.

Contributions, issue reports and additional generator types are welcome.
