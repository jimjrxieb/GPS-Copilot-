# links-preprocess

This service provides the preprocess-sanitize model for the LinkOps pipeline.

## API

- **POST /sanitize**: Accepts `{ "task_text": str }` and returns `{ "output": { "cleaned": str, "category": str } }`.

---

- Place your business logic in `logic/`
- Define Pydantic models in `schemas/`
- Add tests in `tests/` 