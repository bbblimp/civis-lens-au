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

## Policy Metadata

```json
{
  "policy_id": "f2023l00298-christmas-island-section-11-exemption",
  "title": "2023 Section 11 exemption for voyages between Christmas Island and Australian states and territories",
  "status": "historical",
  "evaluation_mode": "historical",
  "jurisdiction": "federal",
  "as_of_date": "2023-03-21",
  "original_decision_date": "2023-03-06",
  "policy_owner": "Minister for Infrastructure, Transport, Regional Development and Local Government",
  "summary": "A legislative instrument made under section 11 of the Coastal Trading (Revitalising Australian Shipping) Act 2012 that exempts a class of voyages between Christmas Island and Australian states or territories from the Act's coastal trading requirements, while excluding broader mainland-to-mainland carriage.\n",
  "policy_text_file": "policy.md",
  "attachments": [],
  "sources": [
    {
      "id": "primary-instrument",
      "title": "2023 Section 11 exemption for voyages between Christmas Island and Australian states and territories",
      "type": "primary",
      "date": "2023-03-21",
      "url": "https://www.legislation.gov.au/F2023L00298/asmade/text"
    },
    {
      "id": "explanatory-statement",
      "title": "Explanatory statement for the 2023 Section 11 exemption for voyages between Christmas Island and Australian states and territories",
      "type": "official",
      "date": "2023-03-21",
      "url": "https://www.legislation.gov.au/F2023L00298/asmade/text/explanatory-statement"
    },
    {
      "id": "enabling-act",
      "title": "Coastal Trading (Revitalising Australian Shipping) Act 2012",
      "type": "primary",
      "date": "2012-06-29",
      "url": "https://www.legislation.gov.au/C2012A00055/latest/text"
    }
  ],
  "tags": [
    "shipping",
    "christmas-island",
    "coastal-trading",
    "exemption",
    "legislative-instrument"
  ],
  "notes": [
    "Anchor historical evaluation to the registration date of 2023-03-21.",
    "Treat the commencement and effective-period wording separately from later implementation outcomes.",
    "Keep any later evidence about service impacts or market effects in hindsight analysis only."
  ]
}
```

## Policy Text

```markdown
# 2023 Section 11 exemption for voyages between Christmas Island and Australian states and territories

## Policy metadata snapshot

- Register ID: `F2023L00298`
- Instrument type: Legislative instrument
- Made: `2023-03-06`
- Registered: `2023-03-21`
- Effective period stated in the instrument: `2023-04-08` to `2028-04-07`
- Enabling law: section 11 of the `Coastal Trading (Revitalising Australian Shipping) Act 2012`
- Administering portfolio at registration: Infrastructure, Transport, Regional Development, Communications, Sport and the Arts

## Primary instrument text

The instrument states that the Minister directs that the provisions of the `Coastal Trading (Revitalising Australian Shipping) Act 2012` do not apply to the class of vessels described in the schedule.

It states that the exemption has effect for the period commencing `8 April 2023` and ceasing on `7 April 2028`.

### Schedule

All vessels undertaking any voyage for the carriage of cargo or passengers between Christmas Island and any port in the Commonwealth or in the Territories are covered, except voyages where a vessel takes on cargo or passengers from another Commonwealth or Territory port for unloading or disembarking at another such port.

## Explanatory statement

The explanatory statement says the Act regulates coastal trading by providing for licences authorising vessels to engage in coastal trading, with civil penalties potentially applying if a vessel engages in coastal trading without a licence.

It explains that section 11 allows the Minister to direct that the Act does not apply to a vessel, class of vessels, person, or class of persons, and that the exemption can be confined to specific periods or voyages.

It says the instrument exempts vessels undertaking voyages carrying cargo or passengers between Christmas Island and any port in the Commonwealth or Territories, while excluding voyages involving additional loading from other Commonwealth or Territory ports for unloading at another such port.

It says the exemption continues a longstanding exemption previously provided under subsection 421(1) of the `Navigation Act 1912`, unchanged from that earlier arrangement, and that the exemption has been in place since `1998` to allow Christmas Island to access shipping services.

It also states that external consultation was considered unnecessary because the exemption was treated as minor or machinery in nature and did not alter existing arrangements.

## Human rights compatibility statement

The statement of compatibility says the instrument does not engage any applicable rights or freedoms listed in the `Human Rights (Parliamentary Scrutiny) Act 2011` and concludes that the instrument is compatible with human rights.

## Source URLs

- Primary instrument: `https://www.legislation.gov.au/F2023L00298/asmade/text`
- Explanatory statement: `https://www.legislation.gov.au/F2023L00298/asmade/text/explanatory-statement`
- Enabling Act: `https://www.legislation.gov.au/C2012A00055/latest/text`
```
