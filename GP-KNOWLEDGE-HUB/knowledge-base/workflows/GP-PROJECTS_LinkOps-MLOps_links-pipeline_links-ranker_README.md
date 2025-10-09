# links-ranker

This service provides the autonomy ranker model for determining if tasks can be executed autonomously in the LinkOps pipeline.

## API

- **POST /autonomy-score**: Accepts `{ "task_text": str, "category": str }` and returns `{ "output": { "can_execute": bool, "autonomy_score": float } }`.

---

- Place your business logic in `logic/`
- Define Pydantic models in `schemas/`
- Add tests in `tests/` 