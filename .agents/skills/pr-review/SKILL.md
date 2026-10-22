---
name: pr-review
description: "Review an AquaMind pull request, commit, or diff for correctness, safety, compatibility, and test coverage. Use for prompts such as 'review this PR', 'review my diff', 'รีวิวโค้ด', or 'find risks'; do not use to implement fixes, perform a repository tour, or report formatter-managed style noise."
---

# PR Review

## Purpose

Find actionable defects and risks in a proposed change, prioritizing correctness over style.

## When to use

- Use for a PR, commit range, staged changes, working-tree diff, or patch supplied by the user.
- Use for a read-only pre-merge risk assessment.

## When not to use

- Do not use to modify the patch or implement suggested fixes unless the user separately requests changes.
- Do not use for general onboarding or unscoped architecture critique.

## Required context

1. Establish the exact review base and changed files. If the base is ambiguous and materially affects findings, state the assumption.
2. Read all `AGENTS.md` files governing changed paths. For frontend changes, read `frontend/AGENTS.md` and relevant local Next.js documentation.
3. Read the relevant README, implementation context around each hunk, and affected tests.
4. Read `backend/data/DATA_CONTRACT.md` for data, ground-truth, forecast, model, or lineage changes.

## Workflow

1. Inspect the diff, then trace each changed behavior through callers and consumers.
2. Review correctness first: contracts, branching, state, time windows, numerical semantics, and failure behavior.
3. Check edge cases and error handling, especially stale/missing external data, unknown stations, provider failures, and partial pipeline outputs.
4. Check security and configuration: secrets, environment-variable boundaries, proxy destinations, CORS exposure, untrusted inputs, and sensitive farm/location data.
5. Check compatibility across FastAPI/Pydantic responses, Next.js consumers, Streamlit, persisted CSV/JSON fields, and model metadata.
6. Check repository-specific scientific safeguards: watch index versus probability, `VERIFIED` ground truth, no automatic negative labels, decision-time leakage controls, quality-gated Sentinel evidence, and operational-model approval.
7. Assess tests for changed behavior, happy paths, boundaries, and failure paths. Flag a missing test only when it protects a concrete risk.
8. Ignore style issues already handled by ESLint or an existing build check unless they cause correctness or maintainability risk.
9. Classify each finding as `Blocker`, `Warning`, `Suggestion`, or `Question` and cite the precise file and line.
10. If no findings remain, state that explicitly and list untested or unreviewed risk areas.

## Guardrails

- Do not modify files during review.
- Do not present speculative concerns as defects; state the execution path and consequence.
- Do not rely only on the diff when a caller, response consumer, or generated artifact can invalidate the change.
- Do not approve claims of field accuracy or bloom probability without verified ground truth and a passing operational validation artifact.
- Do not report formatter/linter-owned style preferences as findings.
- Separate verified findings, questions, and assumptions.

## Verification

Run checks only when useful and permitted by the review scope:

- Backend: `python -m pytest backend -q`
- Frontend, from `frontend/`: `npm run lint` and `npm run build`
- Pipeline state: `python -m backend.pipeline status`

Prefer focused backend test files before the full suite. Report commands not run, reasons, and residual risk; a green suite does not replace code-path review.

## Final response

List findings first, ordered by severity, each with file/line, evidence, impact, and a concrete remedy. Then report questions, verification results, assumptions, and residual risks. If there are no findings, say so and identify what was not verified.
