# Cron Agent Prompt

You are running the unattended Civis Lens AU daily preparation job.

Use the repository's existing workflow and guardrails:

1. Inspect `agendas/queue.yaml`.
2. Select exactly one `status: queued` civic agenda item, normally the first one.
3. If the selected item still has placeholder text, replace it with a real Australian civic agenda or policy item using official or primary sources where possible.
4. Keep the item narrow enough to fit one policy review workspace.
5. Fill source URLs, neutral summary, tags, and notes in the queue item.
6. Run `python3 scripts/daily_prepare.py`.
7. Verify that a policy workspace, review prompts, manual batch folder, and agenda queue update were created.

Rules:

- Prefer Australian official, parliamentary, regulator, department, legislation, budget, inquiry, auditor, ombudsman, or consultation sources.
- Keep source collection factual and restrained.
- Do not invent source URLs.
- Do not run live model API execution unless the repository has explicit API keys and the operator asked for it.
- Do not commit manually from inside the agent run; the wrapper handles narrow auto-publish after successful preparation.
- Do not push from inside the agent run.
- Do not expose secrets or local private data.
- If a complete agenda cannot be prepared, leave a clear note in `agendas/queue.yaml` and do not mark it as prepared.
