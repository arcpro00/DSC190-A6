# AGENTS.md

## General Instructions

- Do not hard-code outputs or special-case inputs simply to pass tests.
- Implement general solutions that work for unseen inputs as well.
- Prefer clear, maintainable, and readable code.
- Use descriptive variable and function names.
- Avoid unnecessary complexity.
- Ensure code passes `ruff check .`
- Ensure code passes `mypy .`
- Use proper type hints.
- Follow existing project formatting conventions.

## Project Setup

- This project is a Python project managed with `uv`.

## Testing

- Tests are run using `pytest`.
- Run tests with:

```bash
uv run pytest
