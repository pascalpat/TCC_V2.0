# Agent Guidelines for TCC_V2.0

This project is a modular Flask + JavaScript application for tracking construction costs. The goal is to capture daily site data and store it for reporting, analysis, and audit. Admin section will uses React framework.

## Design Notes
- Each data entry tab displays a form on the left and a table of pending entries on the right. A "Confirm Tab" action commits the entries.
- Session entries remain `pending` until confirmed. After confirmation they become `committed` or may be `rejected`.
- Allowed status values: `pending`, `committed`, `rejected`.

## Instructions for Agents
- Consult `docs/api_and_ui_reference.md` whenever modifying DOM IDs, API endpoints, or JSON payload fields. Follow the validation checklist provided there.
- Keep routes modular: one blueprint per file, and preserve the project's existing naming conventions.
- Provide code suggestions in small increments (no more than 2–3 steps). For large tasks, break them into stages and ask for user confirmation before proceeding.
- Run `pytest` before committing code. If `codex_test_loop.py` is available, it may be used instead.
- See `README.md` and the `docs/` directory for additional setup and architecture details.

This file centralizes agent guidelines for this repository.