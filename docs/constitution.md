# Civis Lens AU Constitution

## Purpose

Civis Lens AU exists to test whether policy analysis can be made more transparent, more consistent, and less vulnerable to opaque institutional failure by using multiple AI models under a fixed public method.

## Foundational Position

The project does not assume that any model is neutral, objective, or incorruptible. It assumes only that a well-logged multi-model process can be easier to inspect and challenge than closed decision-making.

## Commitments

1. Every run must be reproducible from the repository artifacts.
2. Historical analysis must separate contemporaneous knowledge from hindsight.
3. Current-policy analysis must identify live implementation constraints and evidence gaps.
4. Proposed-policy analysis must state assumptions, incentives, and forecast uncertainty clearly.
5. Final reports must preserve disagreement, not just average it away.
6. Human reviewers must be able to audit the exact prompts, models, and outputs.

## Non-Goals

- Replacing democratic institutions with automated decision-making
- Claiming political neutrality as a branding exercise
- Allowing hidden prompt edits or undocumented run changes
- Presenting speculative claims as settled fact

## Governance Rules

- Prompts are part of the method and must be versioned.
- Rubric changes should be deliberate and documented.
- Model aliases should stay stable after use so historical comparisons remain readable.
- Raw responses should remain preserved in `runs/` once recorded.
- Public-facing summaries belong in `outputs/`, not in place of the raw record.

## Bias Handling

Bias is handled as an operational risk, not a problem solved by assertion.

Controls:
- fixed prompt structure
- multiple review models
- explicit source tracking
- synthesis model with disagreement detection
- human follow-up requirements
- clear uncertainty labels

## Legitimacy Boundary

This project can support policy review, drafting, consultation, and audit. It does not create democratic legitimacy on its own. Public authority remains a human and institutional question.

