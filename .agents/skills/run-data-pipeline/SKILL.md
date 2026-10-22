---
name: run-data-pipeline
description: "Operate and verify AquaMind's existing live-data and operational-model pipeline. Use for prompts such as 'refresh live data', 'backfill forecasts', 'build the dataset', 'train the operational model', 'pipeline status', or 'รัน pipeline'; do not use to change pipeline code, fabricate ground truth, hand-edit artifacts, or run mutating/network steps for an informational request."
---

# Run Data Pipeline

## Purpose

Run the repository's existing pipeline commands safely while preserving provenance, temporal validity, and the operational-model gate.

## When to use

- Use to inspect pipeline status or explicitly run refresh, backfill, dataset-build, or training operations.
- Use to explain outputs and blocked validation states after those operations.

## When not to use

- Do not use to implement or debug pipeline code.
- Do not use to create, guess, or approve field ground truth.
- Do not run write-producing or network-backed commands when the user asks only for status or explanation.

## Required context

1. Read `backend/README.md`, `backend/data/DATA_CONTRACT.md`, and relevant `AGENTS.md` files.
2. Inspect `backend/pipeline.py` for current CLI arguments, prerequisites, and output paths.
3. Inspect `git status` before execution so generated-data changes are distinguishable from pre-existing user work.
4. Confirm installed dependencies; do not install them unless the user separately requests installation.

## Workflow

1. Run `python -m backend.pipeline status` first and record snapshot, observation, forecast, verified-ground-truth, supervised-row, and operational-model state.
2. Select only the explicitly requested operation:
   - Refresh Sentinel-2 and current Weather/Ocean: `python -m backend.pipeline refresh-live --lookback-days 180 --max-scenes 6`
   - Backfill decision-time forecasts: `python -m backend.pipeline backfill-forecasts`
   - Build supervised data: `python -m backend.pipeline build-dataset`
   - Train and validate the operational model: `python -m backend.pipeline train`
   - Read status: `python -m backend.pipeline status`
3. Check prerequisites before execution. `backfill-forecasts` needs Sentinel observations; dataset build needs the source CSVs and ground-truth file; training needs a built supervised dataset.
4. Treat refresh and backfill as network-backed operations and all operations except `status` as write-producing. Do not broaden parameters beyond the documented command without explaining why.
5. Capture command output and errors. Never replace a failed provider response or missing row with fabricated values.
6. Run status again after a write-producing operation.
7. Review changes to snapshots, observations, forecasts, dataset/audit files, validation reports, and model artifacts. Preserve unrelated changes.
8. Verify relevant deterministic contracts with `python -m pytest backend/test_real_pipeline.py -q`; run `python -m pytest backend -q` when the operation is part of a broader readiness check.
9. Report whether the operational model remains blocked. Treat a validation report that creates no approved model artifact as a valid fail-closed result, not a pipeline success claim.

## Guardrails

- Accept only `verification_status=VERIFIED` field observations for training. Never infer a negative label from no report.
- Preserve Sentinel processing latency and decision-time forecast selection; do not use future observations or realized future marine conditions.
- Preserve item IDs, provider URLs, issue/decision times, event IDs, and audit output required for lineage.
- Do not hand-edit `ground_truth.csv`, generated snapshots/CSVs, validation reports, or model JSON to force a desired status.
- Do not bypass validation/calibration policy or present an environmental-watch score as operational bloom probability.
- Do not claim a refresh is current or complete without inspecting timestamps, rejected scenes/errors, and post-run status.

## Verification

- Before and after: `python -m backend.pipeline status`
- Pipeline contract tests: `python -m pytest backend/test_real_pipeline.py -q`
- Full backend readiness: `python -m pytest backend -q`

For any skipped command, report the exact command, reason, and resulting uncertainty. Network success and deterministic test success must be reported separately.

## Final response

Report the requested operation, before/after status, files or artifacts changed, row counts and timestamps, rejected scenes/errors, validation-gate result, commands and exit results, assumptions, and remaining data or network risks.
