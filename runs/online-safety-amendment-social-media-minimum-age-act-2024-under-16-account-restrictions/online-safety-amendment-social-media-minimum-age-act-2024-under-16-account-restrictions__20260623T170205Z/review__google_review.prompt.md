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
  "policy_id": "online-safety-amendment-social-media-minimum-age-act-2024-under-16-account-restrictions",
  "title": "Online Safety Amendment (Social Media Minimum Age) Act 2024 - under-16 account restrictions",
  "status": "active",
  "evaluation_mode": "current",
  "jurisdiction": "federal",
  "as_of_date": "2026-06-24",
  "original_decision_date": null,
  "policy_owner": null,
  "summary": "Australia's Online Safety Amendment (Social Media Minimum Age) Act 2024 amended the Online Safety Act 2021 to require providers of age-restricted social media platforms to take reasonable steps to prevent Australian users under 16 from having accounts. The bill was introduced in November 2024, passed both Houses on 29 November 2024, and received assent on 10 December 2024. The policy review should focus on the current statutory framework and implementation design for under-16 account restrictions, including provider obligations, platform scope, age assurance, privacy, child safety, enforcement, and proportionality.\n",
  "policy_text_file": "policy.md",
  "attachments": [],
  "sources": [
    {
      "url": "https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Search_Results/Result?bId=r7284",
      "note": "Queued agenda source"
    },
    {
      "url": "https://www.legislation.gov.au/C2024A00127/latest/text",
      "note": "Queued agenda source"
    },
    {
      "url": "https://www.aph.gov.au/Parliamentary_Business/Committees/Senate/Environment_and_Communications/SocialMediaMinimumAge",
      "note": "Queued agenda source"
    },
    {
      "url": "https://www.infrastructure.gov.au/department/media/publications/online-safety-amendment-social-media-minimum-age-bill-2024-fact-sheet",
      "note": "Queued agenda source"
    }
  ],
  "tags": [
    "online-safety",
    "social-media",
    "children",
    "privacy",
    "digital-regulation"
  ],
  "notes": [
    "Record the exact policy text and source links before submitting to models.",
    "Keep hindsight separate from contemporaneous analysis for historical reviews."
  ]
}
```

## Policy Text

```markdown
# Online Safety Amendment (Social Media Minimum Age) Act 2024 - under-16 account restrictions

## Policy text

Collect the exact policy text, bill extract, instrument, consultation paper, or official agenda material here before final review.

## Context

Australia's Online Safety Amendment (Social Media Minimum Age) Act 2024 amended the Online Safety Act 2021 to require providers of age-restricted social media platforms to take reasonable steps to prevent Australian users under 16 from having accounts. The bill was introduced in November 2024, passed both Houses on 29 November 2024, and received assent on 10 December 2024. The policy review should focus on the current statutory framework and implementation design for under-16 account restrictions, including provider obligations, platform scope, age assurance, privacy, child safety, enforcement, and proportionality.

## Source links

- https://www.aph.gov.au/Parliamentary_Business/Bills_Legislation/Bills_Search_Results/Result?bId=r7284
- https://www.legislation.gov.au/C2024A00127/latest/text
- https://www.aph.gov.au/Parliamentary_Business/Committees/Senate/Environment_and_Communications/SocialMediaMinimumAge
- https://www.infrastructure.gov.au/department/media/publications/online-safety-amendment-social-media-minimum-age-bill-2024-fact-sheet
```
