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
  "policy_id": "enhancing-australia-s-first-right-to-repair-laws-agricultural-machinery-and-mvis-improvements",
  "title": "Enhancing Australia's first right to repair laws - agricultural machinery and MVIS improvements",
  "status": "proposed",
  "evaluation_mode": "proposed",
  "jurisdiction": "federal",
  "as_of_date": "2026-06-16",
  "original_decision_date": null,
  "policy_owner": null,
  "summary": "Treasury is consulting on proposals to expand Australia's Motor Vehicle Service and Repair Information Sharing Scheme to certain agricultural machinery and to improve the existing motor-vehicle right to repair scheme. The discussion paper seeks feedback on machinery and equipment coverage, eligible access to repair information, use limits for scheme information, safety and security information, intermediaries, electronic logbooks, pricing, supply timeframes, governance, and enforcement. The consultation opened on 22 May 2026 and closes on 3 July 2026.\n",
  "policy_text_file": "policy.md",
  "attachments": [],
  "sources": [
    {
      "url": "https://consult.treasury.gov.au/c2026-760808",
      "note": "Queued agenda source"
    },
    {
      "url": "https://storage.googleapis.com/files-au-treasury/treasury/p/prj3c8735784e10eec0231f0/page/c2026_760808.pdf",
      "note": "Queued agenda source"
    },
    {
      "url": "https://treasury.gov.au/review/review-motor-vehicle-information-sharing-scheme",
      "note": "Queued agenda source"
    },
    {
      "url": "https://treasury.gov.au/publication/p2026-740225",
      "note": "Queued agenda source"
    },
    {
      "url": "https://ministers.treasury.gov.au/ministers/andrew-leigh-2025/media-releases/right-repair-delivering-motorists-small-business-and",
      "note": "Queued agenda source"
    },
    {
      "url": "https://ministers.treasury.gov.au/ministers/jim-chalmers-2022/media-releases/treasurers-agree-reforms-increase-competition-and-boost",
      "note": "Queued agenda source"
    }
  ],
  "tags": [
    "right-to-repair",
    "agriculture",
    "competition",
    "consumer-policy",
    "consultation"
  ],
  "notes": [
    "Record the exact policy text and source links before submitting to models.",
    "Keep hindsight separate from contemporaneous analysis for historical reviews."
  ]
}
```

## Policy Text

```markdown
# Enhancing Australia's first right to repair laws - agricultural machinery and MVIS improvements

## Policy text

Collect the exact policy text, bill extract, instrument, consultation paper, or official agenda material here before final review.

## Context

Treasury is consulting on proposals to expand Australia's Motor Vehicle Service and Repair Information Sharing Scheme to certain agricultural machinery and to improve the existing motor-vehicle right to repair scheme. The discussion paper seeks feedback on machinery and equipment coverage, eligible access to repair information, use limits for scheme information, safety and security information, intermediaries, electronic logbooks, pricing, supply timeframes, governance, and enforcement. The consultation opened on 22 May 2026 and closes on 3 July 2026.

## Source links

- https://consult.treasury.gov.au/c2026-760808
- https://storage.googleapis.com/files-au-treasury/treasury/p/prj3c8735784e10eec0231f0/page/c2026_760808.pdf
- https://treasury.gov.au/review/review-motor-vehicle-information-sharing-scheme
- https://treasury.gov.au/publication/p2026-740225
- https://ministers.treasury.gov.au/ministers/andrew-leigh-2025/media-releases/right-repair-delivering-motorists-small-business-and
- https://ministers.treasury.gov.au/ministers/jim-chalmers-2022/media-releases/treasurers-agree-reforms-increase-competition-and-boost
```
