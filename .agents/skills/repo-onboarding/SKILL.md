---
name: repo-onboarding
description: "Map and explain the AquaMind repository before implementation, including architecture, entry points, commands, and task-relevant modules. Use for prompts such as 'onboard me', 'สำรวจ repo', 'explain the architecture', or 'where should this change go'; do not use to implement, fix, or review a concrete patch."
---

# Repository Onboarding

## Purpose

Build a task-focused map of the current AquaMind implementation before any code change.

## When to use

- Use when a user asks to explore, explain, or locate work in the repository.
- Use before a later implementation when the affected subsystem is not yet clear.

## When not to use

- Do not use as a substitute for implementing a feature, fixing a bug, writing tests, or reviewing a patch.
- Do not use to inventory every file without a concrete question.

## Required context

1. Locate and read every `AGENTS.md` that governs the files under discussion. For frontend work, this includes `frontend/AGENTS.md`.
2. Read `README.md` and the README for each relevant area: `backend/README.md`, `frontend/README.md`, or `Model/README.md`.
3. Read `AquaMind_Final_ReportV2.md` sections 5.4 and 7 only when architecture, component status, or recorded verification matters.
4. Read `backend/data/DATA_CONTRACT.md` for dataset, label, ground-truth, or lineage questions.
5. Inspect manifests and nearby implementation/tests; do not rely on documentation alone when code can confirm current behavior.

## Workflow

1. Confirm the Git root and report pre-existing worktree changes without modifying them.
2. Identify the requested task or decision; keep exploration proportional to that target.
3. Map the current runtime path: external weather/Sentinel inputs, backend adapters and model logic, FastAPI, then Next.js or Streamlit.
4. Identify entry points relevant to the task:
   - FastAPI: `backend/main.py`
   - Data pipeline CLI: `backend/pipeline.py`
   - Streamlit: `streamlit_app.py`
   - Next.js UI: `frontend/app/page.tsx` and `frontend/app/layout.tsx`
   - Synthetic experiment: `Model/generate_dataset.py`, `Model/train.py`, and `Model/predict.py`
5. Trace only the modules and tests connected to the task. Start from imports, route handlers, CLI subcommands, or UI fetch calls.
6. Record verified commands and their source:
   - Python install: `python -m pip install -r requirements.txt` or `python -m pip install -r backend/requirements.txt`
   - Backend dev: `python -m uvicorn backend.main:app --reload --port 8000`
   - Streamlit dev: `streamlit run streamlit_app.py`
   - Frontend install/dev: run `npm install`, then `npm run dev` from `frontend/`
   - Backend tests: `python -m pytest backend -q`
   - Frontend lint/build: run `npm run lint` and `npm run build` from `frontend/`
7. State that no repository formatting command, standalone type-check command, or frontend test command was found if that remains true.
8. Finish with the likely files for the requested work, dependencies between them, and unresolved questions. Do not edit code.

## Guardrails

- Distinguish the implemented architecture from the target architecture documented in the final report.
- Preserve the repository's distinction between the environmental-watch index, synthetic demonstrations, and a field-validated bloom probability.
- Do not infer database, authentication, notification, or migration infrastructure; the current architecture document marks them as unimplemented.
- Do not start long-running development servers or network-backed refresh jobs unless the user asks.
- Separate verified facts from assumptions and label stale or contradictory documentation.

## Verification

- Cross-check commands against `README.md`, area READMEs, and `frontend/package.json`.
- For an operational-readiness request, run only the relevant checks: `python -m backend.pipeline status`, `python -m pytest backend -q`, `npm run lint`, or `npm run build`.
- If a check is not run, report the exact command, reason, and remaining risk.

## Final response

Report the architecture and entry points, relevant subsystem, verified commands, likely change locations, facts versus assumptions, checks run, and unresolved risks. State explicitly that no production code was changed.
