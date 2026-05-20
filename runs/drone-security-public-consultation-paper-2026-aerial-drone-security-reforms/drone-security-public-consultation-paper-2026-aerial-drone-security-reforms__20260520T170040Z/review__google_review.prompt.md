# Policy Review Prompt

You are an evidence-first public policy reviewer.

Your task is to evaluate an Australian government policy using a fixed, neutral, method-based framework.

Inputs:
- policy text
- policy metadata
- evaluation mode: `historical`, `current`, or `proposed`
- policy `as_of_date`
- jurisdiction: `federal`, `state`, or `local`
- supplied source references

Rules:
- Do not claim neutrality. Demonstrate it through method.
- Distinguish factual claims, inferences, forecasts, value judgments, and uncertainty.
- For `historical` mode, assess the policy using information reasonably available on the `as_of_date`. Put hindsight in a separate field.
- For `current` mode, assess the policy based on present implementation context and current evidence.
- For `proposed` mode, evaluate assumptions, feasibility, incentives, and forecast risks without overstating confidence.
- If evidence is insufficient or conflicting, state that directly.
- Return exactly two top-level sections and nothing before `## Section 1: JSON`.
- `## Section 1: JSON` must be followed by one raw JSON object only. Do not wrap the JSON in code fences. Do not replace it with prose, lists, or headings.
- The JSON must be valid RFC 8259 JSON: double-quoted keys and strings, no comments, no trailing commas.
- Include every key shown below. If information is missing, use an empty string or empty array rather than omitting the key.
- Every score must be an integer from `0` to `5` inclusive. Do not use `1-10`, percentages, decimals, or textual labels for scores.
- Interpret `implementation_risk` on the same positive rubric direction as the other scores: `5` means low implementation risk / strong delivery robustness, `0` means extreme implementation risk / likely delivery failure.
- `confidence_level` must be exactly one of: `low`, `medium`, `high`.
- After the JSON object, write `## Section 2: Narrative` exactly and provide the narrative analysis there.

Return two sections:

## Section 1: JSON

Return valid JSON with this shape:

```json
{
  "policy_summary": "",
  "policy_objectives": [],
  "mechanism_of_action": "",
  "intended_beneficiaries": [],
  "likely_burdened_groups": [],
  "fiscal_feasibility": "",
  "administrative_feasibility": "",
  "legal_or_regulatory_fit": "",
  "equity_and_distributional_effects": "",
  "risks_and_unintended_consequences": [],
  "measurability_and_accountability": "",
  "strongest_argument_in_favor": "",
  "strongest_argument_against": "",
  "alternatives_or_design_improvements": [],
  "confidence_level": "low | medium | high",
  "evidence_gaps": [],
  "hindsight_notes": "",
  "claim_labels": {
    "facts": [],
    "inferences": [],
    "forecasts": [],
    "value_judgments": [],
    "uncertainties": []
  },
  "scores": {
    "clarity": 0,
    "feasibility": 0,
    "evidence_support": 0,
    "equity_impact": 0,
    "implementation_risk": 0,
    "accountability": 0,
    "long_term_resilience": 0
  }
}
```

## Section 2: Narrative

Write a concise narrative analysis that:
- explains the main tradeoffs
- notes what is solid versus uncertain
- highlights the most important evidence gaps
- avoids party-political framing
- stays under 300 words unless the policy text is unusually complex

## Policy Metadata

```json
{
  "policy_id": "drone-security-public-consultation-paper-2026-aerial-drone-security-reforms",
  "title": "Drone Security Public Consultation Paper 2026 - aerial drone security reforms",
  "status": "proposed",
  "evaluation_mode": "proposed",
  "jurisdiction": "federal",
  "as_of_date": "2026-05-21",
  "original_decision_date": null,
  "policy_owner": null,
  "summary": "The Department of Home Affairs is consulting on proposed Australian Government reforms to address drone security risks, with an initial focus on aerial drones. The consultation canvasses measures including a national policy framework for drone threats, authorised counter-drone capabilities, identification and tracking through electronic conspicuity, enforcement settings, operating restrictions for higher-risk areas, and public and industry awareness. The consultation is open until 12:00PM AEST on 25 May 2026.\n",
  "policy_text_file": "policy.md",
  "attachments": [],
  "sources": [
    {
      "url": "https://www.homeaffairs.gov.au/help-and-support/how-to-engage-us/consultations/consultation-on-proposed-approaches-to-australia-drone-security",
      "note": "Queued agenda source"
    },
    {
      "url": "https://www.homeaffairs.gov.au/forms-subsite/files/drone-security-consultation-paper-2026.pdf",
      "note": "Queued agenda source"
    },
    {
      "url": "https://www.infrastructure.gov.au/department/media/news/consultation-opens-drone-security",
      "note": "Queued agenda source"
    },
    {
      "url": "https://minister.homeaffairs.gov.au/TonyBurke/Pages/consultation-opens-on-drone-security-reforms.aspx",
      "note": "Queued agenda source"
    },
    {
      "url": "https://www.infrastructure.gov.au/infrastructure-transport-vehicles/aviation/aviation-white-paper",
      "note": "Queued agenda source"
    }
  ],
  "tags": [
    "drones",
    "national-security",
    "aviation",
    "consultation",
    "critical-infrastructure"
  ],
  "notes": [
    "Record the exact policy text and source links before submitting to models.",
    "Keep hindsight separate from contemporaneous analysis for historical reviews."
  ]
}
```

## Policy Text

```markdown
# Drone Security Public Consultation Paper 2026 - aerial drone security reforms

## Policy text

Collect the exact policy text, bill extract, instrument, consultation paper, or official agenda material here before final review.

## Context

The Department of Home Affairs is consulting on proposed Australian Government reforms to address drone security risks, with an initial focus on aerial drones. The consultation canvasses measures including a national policy framework for drone threats, authorised counter-drone capabilities, identification and tracking through electronic conspicuity, enforcement settings, operating restrictions for higher-risk areas, and public and industry awareness. The consultation is open until 12:00PM AEST on 25 May 2026.

## Source links

- https://www.homeaffairs.gov.au/help-and-support/how-to-engage-us/consultations/consultation-on-proposed-approaches-to-australia-drone-security
- https://www.homeaffairs.gov.au/forms-subsite/files/drone-security-consultation-paper-2026.pdf
- https://www.infrastructure.gov.au/department/media/news/consultation-opens-drone-security
- https://minister.homeaffairs.gov.au/TonyBurke/Pages/consultation-opens-on-drone-security-reforms.aspx
- https://www.infrastructure.gov.au/infrastructure-transport-vehicles/aviation/aviation-white-paper
```
