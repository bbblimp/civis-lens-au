# Operations

## Daily Preparation

Add civic agenda items to `agendas/queue.yaml` with `status: queued`.

Prepare the next queued item:

```bash
python3 scripts/daily_prepare.py
```

This creates:

- a policy workspace under `policies/<mode>/<policy-id>/`
- review prompts and bundles under `runs/<policy-id>/<run-group>/`
- manual response placeholders under the run directory
- a human batching guide under `manual_batches/<date>__<policy-id>/`

## Manual Model Batch

Open the batch README created under `manual_batches/`, paste each `review__*.prompt.md` into the matching web model, then save the raw answer into the matching `review__*.manual_response.txt` file.

Record whatever is ready:

```bash
python3 scripts/record_manual_batch.py --batch manual_batches/YYYY-MM-DD__policy-id
```

Once all review responses are recorded, the recorder prepares a synthesis prompt. Paste that prompt into the synthesis model and save the answer into `synthesis__synthesis_primary.manual_response.txt`, then run the same recorder command again. The recorder writes the final report under `outputs/` and refreshes the README covered-policy table.

## Cron

Use `scripts/cron_wrapper.sh` from cron:

```cron
0 4 * * * /home/blech/git/civis-lens-au/scripts/cron_wrapper.sh
```

The wrapper:

- creates a lockfile in `state/`
- runs the local Codex CLI with `prompts/cron-agent.md` when available
- falls back to `scripts/daily_prepare.py` when Codex is unavailable
- commits agenda, policy, run, manual-batch, output, and index changes
- pushes the generated commit to `origin/main` by default
- writes raw logs under `logs/raw/`

Disable commits for a run with:

```bash
CIVIS_AUTO_COMMIT=0 scripts/cron_wrapper.sh
```

Disable push while keeping the local commit with:

```bash
CIVIS_AUTO_PUSH=0 scripts/cron_wrapper.sh
```

Smoke-test the Codex wiring without editing files:

```bash
scripts/cron_wrapper.sh --smoke-agent
```
