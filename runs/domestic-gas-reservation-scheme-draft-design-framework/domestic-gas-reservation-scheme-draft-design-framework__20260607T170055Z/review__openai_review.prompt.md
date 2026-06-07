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
  "policy_id": "domestic-gas-reservation-scheme-draft-design-framework",
  "title": "Domestic Gas Reservation Scheme draft Design Framework",
  "status": "proposed",
  "evaluation_mode": "proposed",
  "jurisdiction": "federal",
  "as_of_date": "2026-06-08",
  "original_decision_date": null,
  "policy_owner": null,
  "summary": "The Australian Government is consulting on a draft Design Framework for a Domestic Gas Reservation Scheme. The proposal would require LNG exporters to supply gas to the Australian domestic market equivalent to 20 per cent of their LNG exports each year, described as a domestic supply obligation, with obligations intended to commence from 1 July 2027. The framework also canvasses regulatory architecture, export approvals, compliance and enforcement arrangements, flexibility mechanisms, and related gas market transparency and conduct reforms. Submissions are invited until 11:30pm AEST on 30 June 2026.\n",
  "policy_text_file": "policy.md",
  "attachments": [],
  "sources": [
    {
      "url": "https://consult.dcceew.gov.au/domestic-gas-reservation-scheme-draft-design-framework",
      "note": "Queued agenda source"
    },
    {
      "url": "https://www.dcceew.gov.au/about/news/have-your-say-domestic-gas-reservation-scheme",
      "note": "Queued agenda source"
    },
    {
      "url": "https://storage.googleapis.com/files-au-climate/climate-au/p/prj3ce30473c51fb474d08e6/page/Domestic_Gas_Reservation_scheme_draft_Design_Framework_May2026.pdf",
      "note": "Queued agenda source"
    },
    {
      "url": "https://storage.googleapis.com/files-au-climate/climate-au/p/prj3ce30473c51fb474d08e6/page/Domestic_Gas_Reservation_draft_Design_Framework_Attachment_A_Export_Process_and_Flexibility_Mechanisms.pdf",
      "note": "Queued agenda source"
    },
    {
      "url": "https://storage.googleapis.com/files-au-climate/climate-au/p/prj3ce30473c51fb474d08e6/page/DGR_Draft_Design_Framework_Att_B_Increased_Transparency_Measures.pdf",
      "note": "Queued agenda source"
    }
  ],
  "tags": [
    "energy",
    "gas",
    "lng",
    "consultation",
    "market-regulation"
  ],
  "notes": [
    "Record the exact policy text and source links before submitting to models.",
    "Keep hindsight separate from contemporaneous analysis for historical reviews."
  ]
}
```

## Policy Text

```markdown
# Domestic Gas Reservation Scheme draft Design Framework

## Policy text

Collect the exact policy text, bill extract, instrument, consultation paper, or official agenda material here before final review.

## Context

The Australian Government is consulting on a draft Design Framework for a Domestic Gas Reservation Scheme. The proposal would require LNG exporters to supply gas to the Australian domestic market equivalent to 20 per cent of their LNG exports each year, described as a domestic supply obligation, with obligations intended to commence from 1 July 2027. The framework also canvasses regulatory architecture, export approvals, compliance and enforcement arrangements, flexibility mechanisms, and related gas market transparency and conduct reforms. Submissions are invited until 11:30pm AEST on 30 June 2026.

## Source links

- https://consult.dcceew.gov.au/domestic-gas-reservation-scheme-draft-design-framework
- https://www.dcceew.gov.au/about/news/have-your-say-domestic-gas-reservation-scheme
- https://storage.googleapis.com/files-au-climate/climate-au/p/prj3ce30473c51fb474d08e6/page/Domestic_Gas_Reservation_scheme_draft_Design_Framework_May2026.pdf
- https://storage.googleapis.com/files-au-climate/climate-au/p/prj3ce30473c51fb474d08e6/page/Domestic_Gas_Reservation_draft_Design_Framework_Attachment_A_Export_Process_and_Flexibility_Mechanisms.pdf
- https://storage.googleapis.com/files-au-climate/climate-au/p/prj3ce30473c51fb474d08e6/page/DGR_Draft_Design_Framework_Att_B_Increased_Transparency_Measures.pdf
```
