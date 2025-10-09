# links-forging

This service provides the forging model for generating resources in the LinkOps pipeline.

## API

- **POST /generate-resource**: Accepts `{ "task_text": str }` and returns `{ "output": { "resource_code": str, "tags": list } }`.

---

- Place your business logic in `logic/`
- Define Pydantic models in `schemas/`
- Add tests in `tests/` 