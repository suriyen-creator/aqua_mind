---
name: write-tests
description: "Add or improve automated tests for existing AquaMind behavior using the repository's current pytest patterns. Use for prompts such as 'write tests', 'add coverage', 'เพิ่มเทสต์', or 'add a regression test'; do not use to implement production behavior, weaken failing tests, or introduce a new frontend test framework without explicit scope."
---

# Write Tests

## Purpose

Increase confidence in existing behavior with deterministic, contract-focused tests.

## When to use

- Use for test-only work or when the requested deliverable is coverage for existing behavior.
- Use to encode a known regression after the production fix is handled separately.

## When not to use

- Do not use when production behavior must change to satisfy a new requirement.
- Do not use to regenerate datasets/models or to create an unsupported frontend test stack.

## Required context

1. Read the governing `AGENTS.md` files and the README for the affected subsystem.
2. Read `backend/test_main.py` and `backend/test_real_pipeline.py` before writing Python tests.
3. Inspect the implementation contract, not only internal function structure.
4. Read `backend/data/DATA_CONTRACT.md` for data-pipeline and label tests.
5. Confirm that no frontend test script/framework exists before proposing frontend automation.

## Workflow

1. Define the behavior and failure mode each test must prove.
2. Match the existing pytest style: plain test functions, direct assertions, `TestClient`, `monkeypatch`, and `tmp_path` fixtures where appropriate.
3. Prefer public routes and observable outputs. Test private helpers only when they encode a critical data/window/QC contract that is difficult to reach otherwise.
4. Cover the relevant mix of:
   - happy path
   - boundary and stale/missing-data cases
   - provider or validation failures
   - compatibility-sensitive response fields
5. For data tests, use small local fixtures and assert decision-time windows, `VERIFIED` filtering, duplicate handling, audit output, and lineage behavior as relevant.
6. Avoid network calls; patch external adapters at their use site, following the existing `monkeypatch` pattern.
7. Keep tests deterministic: fixed timestamps, explicit inputs, isolated temporary paths, and no dependence on mutable repository snapshots.
8. Run the focused test file, then the full backend suite when appropriate.
9. Confirm the change contains no production-code edits unless the user explicitly requested them.

## Guardrails

- Do not test implementation details when a stable behavior or contract can be asserted.
- Do not over-mock the unit under test or mock away the behavior being verified.
- Do not lower assertions, delete coverage, skip tests, or change expected outputs only to make the suite green.
- Do not treat absent field reports as negative labels or synthetic metrics as field accuracy in fixtures or assertions.
- Do not install Jest, Vitest, Playwright, or another frontend test framework without explicit approval and scope; the current `package.json` has no test script.
- Do not claim coverage for paths that were not executed.

## Verification

- API/watch tests: `python -m pytest backend/test_main.py -q`
- Pipeline/data tests: `python -m pytest backend/test_real_pipeline.py -q`
- Full backend suite: `python -m pytest backend -q`
- For frontend files touched only to expose testable behavior, run `npm run lint` and `npm run build` from `frontend/`; these are not substitutes for behavioral tests.

If a command cannot run, report the exact command, reason, and untested behavior.

## Final response

Report behaviors covered, cases added, files changed, commands and results, any production-code changes, assumptions, coverage gaps, and remaining risk.
