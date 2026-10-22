---
name: implement-feature
description: "Implement a new AquaMind capability across Python, FastAPI, Next.js, Streamlit, or the data/ML pipeline. Use for prompts such as 'add', 'build', 'implement', or 'เพิ่มฟีเจอร์'; do not use for diagnosis-only, test-only, repository-tour, or review-only requests."
---

# Implement Feature

## Purpose

Deliver the smallest complete feature that follows existing AquaMind contracts and remains backward compatible.

## When to use

- Use when requested behavior requires production-code changes.
- Use for a vertical slice spanning backend, UI, Streamlit, or pipeline modules.

## When not to use

- Do not use for explanation, review, pure test additions, or a bug whose expected behavior already exists.
- Do not use merely to regenerate data or model artifacts; use `run-data-pipeline`.

## Required context

1. Read the governing `AGENTS.md` files. Before frontend edits, read `frontend/AGENTS.md` and the relevant local Next.js guide it points to.
2. Read the relevant README and inspect the current entry point, neighboring implementation, and tests.
3. For data, model, label, or forecast work, read `backend/data/DATA_CONTRACT.md`, `backend/README.md`, and the relevant pipeline/training module.
4. Inspect `backend/test_main.py` and `backend/test_real_pipeline.py` for current test patterns.

## Workflow

1. Restate the requirement as observable acceptance criteria. Mark ambiguities and assumptions.
2. Trace the current request/data flow and find the closest existing implementation pattern.
3. List the files expected to change and why before editing.
4. Check impact on:
   - FastAPI/Pydantic response fields and frontend TypeScript consumers
   - environmental-watch versus operational-probability semantics
   - dataset labels, decision times, data lineage, and model artifacts
   - environment variables and Next.js proxy configuration
   - persistence or migrations; note that this repository has no database migration workflow
5. Choose the smallest design that satisfies current acceptance criteria. Reuse existing modules and avoid speculative abstractions.
6. Preserve existing API fields and behavior unless the user explicitly approves a breaking change. Call out any unavoidable public-contract change before making it.
7. Implement the vertical slice and update or add behavior-focused tests in the existing backend test suite.
8. For frontend-only behavior with no existing automated test framework, do not invent or install one; use lint/build and disclose the missing behavioral coverage.
9. Review the diff for unrelated refactors, hand-edited generated artifacts, and inaccurate scientific or operational claims.

## Guardrails

- Do not describe an environmental-watch score or synthetic-model output as bloom probability, field accuracy, or validated risk.
- Do not bypass `verification_status=VERIFIED`, the t+3-to-t+5 label contract, temporal leakage controls, or the operational-model validation gate.
- Do not hand-edit generated model/data artifacts. Regenerate them through existing code only when artifact regeneration is explicitly in scope, then review the artifact diff.
- Do not introduce destructive data or schema changes without explicit approval; no migration/rollback workflow exists in this repository.
- Do not refactor unrelated modules or add dependencies unless the user expands the scope.
- Do not claim verification passed unless the command was run successfully in this worktree.

## Verification

Run targeted checks first, then broader checks for affected surfaces:

- Backend route/watch changes: `python -m pytest backend/test_main.py -q`
- Pipeline/data-contract changes: `python -m pytest backend/test_real_pipeline.py -q`
- All backend changes: `python -m pytest backend -q`
- Frontend changes, from `frontend/`: `npm run lint`, then `npm run build`

No standalone formatter, type-check script, or frontend test script is defined. If any relevant command is not run, report the exact command, reason, and remaining risk.

## Final response

Report acceptance criteria, chosen approach, API/data/config impact, files changed, tests added or updated, commands run with results, assumptions, and remaining risks.
