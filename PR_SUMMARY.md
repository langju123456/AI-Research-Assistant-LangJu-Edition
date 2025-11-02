PR summary
==========

This PR prepares the repository for smoother local development and CI runs. Changes include:

- Fixes and developer ergonomics
  - Normalize `app/*.py` files to UTF-8 and add `scripts/ensure_utf8.py` and `scripts/check_utf8.py`.
  - Add `app/__init__.py` to make `app` a proper package.
  - `run_dev.ps1` PowerShell helper to create/activate venv, set PYTHONPATH and start Streamlit.

- Tests and CI
  - Add `.github/workflows/ci.yml` with three jobs:
    - `checks`: flake8 lint + UTF-8 check
    - `test`: lightweight unit tests with minimal pip deps (fast)
    - `integration`: runs on main or manual dispatch and uses conda/mamba to create an env with `faiss-cpu` and runs integration tests
  - Adjusted CI to cache pip/conda packages where possible to speed up runs.

- Code quality and runtime improvements
  - Lazy-load heavy dependencies (faiss, sentence-transformers, chromadb) in `app/memory/vector_store.py`.
  - Lazy-initialize `VectorStore` in `app/agent_core.py` to avoid heavy imports during module import (helps tests & CI).
  - Migrate Pydantic model config in `app/models/model_wrapper.py` to `ConfigDict` (Pydantic v2 style) to remove deprecation warnings.

- Docs
  - Update `README.md` with developer quick start and troubleshooting/FAQ (ModuleNotFoundError, ExecutionPolicy, encoding, CI tips).

Notes for reviewers
- The integration job installs full `requirements.txt` after creating the conda env; this can be adjusted if some deps are not needed for CI.
- Flake8 is run with a permissive `.flake8` config; lint failures do not currently fail the checks job (adjustable).

How to test locally
- Run unit tests quickly without activating venv:
  - `.\.venv\Scripts\python -m pytest -q`
- Normalize encodings:
  - `.\.venv\Scripts\python scripts/ensure_utf8.py`

If you'd like, I can split heavy integration tests into a separate matrix or add caching improvements for conda packages.
