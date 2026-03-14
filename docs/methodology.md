# Methodology

## Evaluation Modes

### Historical

Use the `as_of_date` to anchor what was reasonably knowable at the time the policy was proposed, enacted, or assessed. Any later evidence belongs in a distinct hindsight section.

### Current

Assess the policy against current implementation status, available evidence, and live regulatory, fiscal, and administrative constraints.

### Proposed

Treat the policy as a forecast problem. Expose assumptions, incentive effects, delivery risks, and unknowns without claiming certainty.

## Evidence Hierarchy

From strongest to weakest:

1. Policy text, legislation, regulations, explanatory memoranda
2. Budget papers, implementation plans, auditor reports, court decisions, official evaluations
3. Parliamentary committee material, academic work, independent technical analysis
4. Reputable reporting and think-tank commentary
5. Model inference without direct support

Model inference is allowed, but it must be labelled as inference.

## Output Labels

Each review should distinguish:

- `fact`: directly grounded in cited or supplied evidence
- `inference`: reasoned extension from evidence
- `forecast`: statement about likely future effects
- `value_judgment`: normative position or tradeoff
- `uncertainty`: an unresolved gap, conflict, or confidence limit

## Multi-Model Flow

1. Create a policy manifest with date, jurisdiction, source, and status metadata.
2. Run the same review prompt across three configured review models.
3. Record the exact prompt text, prompt hash, model configuration, and raw outputs.
4. Submit the completed review outputs to a synthesis model.
5. Produce a consolidated report that shows consensus, disputes, weak points, and required human checks.

## Date Discipline

Every policy directory should capture at least:

- `as_of_date`
- `evaluation_mode`
- `status`
- source dates
- original decision date if relevant

This is essential if historical and current reviews are going to be compared honestly.

## Known Limits

- Models may share hidden training biases or source contamination.
- A good synthesis can still inherit blind spots from the review stage.
- Policy quality cannot be reduced to scores alone.
- Democratic legitimacy, ethics, and coercive state power cannot be delegated to a model by technical convenience.

