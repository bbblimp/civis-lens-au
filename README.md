# Civis Lens AU

Civis Lens AU is a greenfield scaffold for AI-assisted review of Australian government policy. The project is designed to make policy analysis more transparent, reproducible, and easier to challenge by running the same policy through multiple models under the same method.

## Mission

Test whether AI can improve policy analysis by making reasoning more consistent, auditable, date-aware, and open to critique.

## Why This Matters

This project has value if it is treated as open policy-review infrastructure rather than an oracle. The workflow forces fixed prompts, date-anchored reasoning, preserved raw outputs, and explicit disagreement across models. That does not make the result neutral or final, but it does make it more inspectable and easier to challenge than opaque policy commentary.

The strongest use case is not "AI should govern." The strongest use case is "policy analysis should be reproducible, challengeable, and harder to manipulate quietly."

## What This Repository Is

- A methodology-first repository for reviewing historical, current, and proposed policies.
- A prompt and schema set for running the same policy through three review models plus one synthesis model.
- A logging workflow that tracks the exact prompt, model, parameters, and timestamp used for every run.

## What This Repository Is Not

- A claim that any model is automatically neutral or incorruptible.
- A replacement for democratic legitimacy, human accountability, or public scrutiny.
- A hidden-policy generator. The method is meant to stay inspectable.
- A proof that AI should replace government, public servants, ministers, or parliamentary process.

## Core Principles

1. Process over rhetoric: neutrality is pursued through fixed prompts, explicit rubrics, and full logging.
2. Date accuracy matters: historical policies must be assessed using what could reasonably have been known on the relevant date, with hindsight separated out.
3. Evidence hierarchy matters: primary and official sources outrank commentary.
4. Disagreement is useful: the synthesis stage must preserve disputes and uncertainty, not flatten them away.
5. Human oversight stays in the loop: the project supports policy audit and drafting review, not automated government.

## Public Positioning

If this project is presented as "AI-driven meritocracy" or "uncorruptable machine government," it will be easy to dismiss. A more defensible public position is:

- open policy review infrastructure
- multi-model civic audit
- reproducible policy critique with a full evidence trail

That framing matches what the repository can actually demonstrate today.

## Repository Layout

```text
docs/        Constitution, methodology, and scoring rubric.
models/      Registry of review and synthesis models.
outputs/     Human-readable synthesis reports.
policies/    Policy inputs, split by historical/current/proposed.
prompts/     Versioned prompt templates.
runs/        Immutable run bundles and raw model outputs.
schemas/     JSON schemas for manifests and run artifacts.
scripts/     Small Python tools for ingesting policies and logging runs.
```

## Quick Start

1. Create a virtual environment and install dependencies.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

2. Create a policy workspace.

```bash
python3 scripts/ingest_policy.py \
  --title "Example Policy" \
  --evaluation-mode proposed \
  --jurisdiction federal \
  --as-of-date 2026-03-14
```

3. Fill in the generated `policy.md` and `policy_manifest.yaml`.

4. Prepare review bundles for the configured review models.

```bash
python3 scripts/run_review.py prepare \
  --policy-dir policies/proposed/example-policy
```

5. Submit each generated `review__*.prompt.md` file to your chosen models and save their raw responses.

6. Record the raw responses against their bundle files.

```bash
python3 scripts/run_review.py record \
  --bundle runs/example-policy/<run-group>/review__openai_review.json \
  --response-file /path/to/openai-response.txt
```

7. Prepare and record the synthesis stage.

```bash
python3 scripts/synthesize_review.py prepare \
  --run-dir runs/example-policy/<run-group>

python3 scripts/synthesize_review.py record \
  --bundle runs/example-policy/<run-group>/synthesis__synthesis_primary.json \
  --response-file /path/to/synthesis-response.txt
```

The synthesis recorder writes a Markdown report into `outputs/`.

## Live Provider Execution

The repository can now execute prepared bundles directly against OpenAI, Anthropic, and Google Gemini APIs.

Required environment variables:

```bash
export OPENAI_API_KEY=...
export ANTHROPIC_API_KEY=...
export GEMINI_API_KEY=...
```

You can also place those values in `.env` or `.env.local` at the repository root. Those files are ignored by git and loaded automatically during live execution.

Optional model overrides:

```bash
export OPENAI_MODEL=gpt-4.1-mini
export ANTHROPIC_MODEL=claude-sonnet-4-20250514
export GEMINI_MODEL=gemini-2.5-flash
```

Run all prepared review bundles in a run group:

```bash
python3 scripts/run_review.py execute \
  --run-dir runs/example-policy/<run-group>
```

Prepare and execute synthesis after the three review bundles have responses:

```bash
python3 scripts/synthesize_review.py prepare \
  --run-dir runs/example-policy/<run-group>

python3 scripts/synthesize_review.py execute \
  --run-dir runs/example-policy/<run-group>
```

Each live execution writes:

- extracted model text to `*.response.txt`
- provider request payload to `*.api_request.json`
- provider response payload to `*.api_response.json`
- updated bundle metadata with request IDs, usage, and resolved model names

For manual web-model runs:

- paste the generated `*.prompt.md` file unchanged
- require the model to begin with `## Section 1: JSON`
- require one raw JSON object only in section 1, with no code fences
- require rubric scores to be integers from `0` to `5` only

## Recommended Workflow

- Use one policy directory per policy.
- Keep the policy text itself separate from commentary.
- Track source URLs and source dates in the manifest.
- Treat the first version of a run bundle as the audit artifact for that prompt/model combination.
- Add a red-team or adversarial review step later if you want stronger bias checks.

## Traction Strategy

Public traction is plausible, but trust has to be earned through evidence. The current best path is to start with serious niche users who already care about auditability:

- journalists
- civic-tech groups
- policy students and researchers
- advocacy organizations
- parliamentary or ministerial staff willing to test the workflow privately

The current project roadmap for that work is in [TODO.md](TODO.md).

## Initial Status

This repository is intentionally a bootstrap. It sets the project method, structure, and logging discipline first. Provider-specific integrations can be added later without changing the core audit model.
