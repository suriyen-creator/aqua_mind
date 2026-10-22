---
name: fix-bug
description: "Diagnose and repair an AquaMind defect or regression with the smallest safe patch. Use for prompts such as 'fix this bug', 'why is this failing', 'แก้บั๊ก', incorrect API/UI output, or broken pipeline behavior; do not use for new capabilities, review-only work, or broad refactoring."
---

# Fix Bug

## Purpose

Prove the failure, identify its root cause, and apply a minimal regression-backed fix.

## When to use

- Use for reproducible incorrect behavior, exceptions, regressions, or failing checks.
- Use when diagnosis and implementation of the repair are both requested.

## When not to use

- Do not use for feature requests, speculative cleanup, or diagnosis-only requests.
- Do not use to force a blocked operational model into service.

## Required context

1. Read the `AGENTS.md` files governing the affected path. For frontend defects, follow `frontend/AGENTS.md` before editing.
2. Read the relevant README and inspect the failing entry point, its direct dependencies, and nearby tests.
3. Read `backend/data/DATA_CONTRACT.md` for dataset, label, forecast, or lineage failures.
4. Capture the current worktree state and preserve unrelated user changes.

## Workflow

1. Write down expected behavior, actual behavior, inputs, environment, and failure evidence.
2. Reproduce the issue with the narrowest existing command or request. If reproduction is impossible, explain why and identify the evidence used instead.
3. Trace the failing path from entry point to output. Separate visible symptoms from the first incorrect state or decision.
4. Form a root-cause hypothesis and verify it against code, data contracts, or a focused experiment.
5. Add a regression test that fails for the demonstrated defect when practical. Use existing `TestClient`, `monkeypatch`, and `tmp_path` patterns as appropriate.
6. Apply the smallest patch that restores the documented contract. Avoid cleanup outside the causal path.
7. Re-run the reproducer/regression test, then the relevant broader suite.
8. Review public API fields, frontend consumers, pipeline outputs, and model/data semantics for collateral changes.

## Guardrails

- Do not weaken assertions, skip tests, fabricate data, or suppress errors merely to make checks pass.
- Do not replace missing Sentinel or field evidence with silent defaults that make the system appear healthy.
- Do not relabel missing field reports as negative examples or bypass the `VERIFIED` ground-truth gate.
- Do not hand-edit model artifacts, snapshots, generated CSVs, or validation reports as a bug fix.
- Do not refactor unrelated code or change a public API without reporting the compatibility impact.
- Do not state that the bug is fixed without successful verification evidence; distinguish verified results from remaining inference.

## Verification

Run the narrowest relevant check first:

- API/watch regression: `python -m pytest backend/test_main.py -q`
- Sentinel, forecast, or dataset regression: `python -m pytest backend/test_real_pipeline.py -q`
- Backend suite after a backend fix: `python -m pytest backend -q`
- Frontend fix, from `frontend/`: `npm run lint`, then `npm run build`

If live external data is needed, keep that check separate from deterministic tests. Report every command not run, why, and the risk that remains.

## Final response

Report expected versus actual behavior, reproduction evidence, root cause, minimal fix, regression coverage, files changed, commands and results, assumptions, and remaining risk.
