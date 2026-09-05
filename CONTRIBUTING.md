# Contributing

Contributions that improve data quality, reproducibility, documentation, tests, or analytical depth are welcome.

## Before opening a change

1. Fork the repository and create a focused branch.
2. Create a Python 3.11 or 3.12 virtual environment.
3. Install the pinned dependencies with pip install -r requirements.txt.
4. Keep raw data out of Git and document any new source, license, retrieval date, and transformation.
5. Run python -m pytest -q and python -m compileall -q src scripts dashboard.

## Pull-request checklist

- Explain the user or analytical problem the change addresses.
- Add or update tests for behavior changes.
- Keep generated outputs deterministic and reasonably small.
- Update the README when commands, inputs, outputs, or limitations change.
- Do not include credentials, API keys, personal data, or proprietary datasets.

Small, reviewable pull requests are easier to validate and merge. For substantial new analysis, open an issue first so the scope and evidence standard can be agreed.
