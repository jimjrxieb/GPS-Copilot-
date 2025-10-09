# links-evaluator

This service provides the task evaluator model for evaluating generated tools in the LinkOps pipeline.

## API

- **POST /evaluate-tool**: Accepts `{ "tool_code": str, "tags": list }` and returns `{ "output": { "passed": bool, "score": float } }`.

---

- Place your business logic in `logic/`
- Define Pydantic models in `schemas/`
- Add tests in `tests/` 