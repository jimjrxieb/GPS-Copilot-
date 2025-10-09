# links-smithing

This service provides the smithing model for generating tools in the LinkOps pipeline.

## API

- **POST /generate-tool**: Accepts `{ "task_text": str }` and returns `{ "output": { "tool_code": str, "tags": list } }`.

---

- Place your business logic in `logic/`
- Define Pydantic models in `schemas/`
- Add tests in `tests/` 