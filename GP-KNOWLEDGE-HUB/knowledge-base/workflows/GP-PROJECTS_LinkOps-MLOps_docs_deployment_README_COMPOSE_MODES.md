# LinkOps-MLOps: Daytime & Nighttime Docker Compose Modes

## ☀️ Daytime Mode: Input Ingestion & Sanitation

**File:** `docker-compose.daytime.yml`

- **Purpose:** Run only the pipeline up to data collection and sanitation.
- **Services:**
  - `db` (PostgreSQL)
  - `whis_data_input` (task input, GUI/API)
  - `whis_sanitize` (sanitization, redaction)
- **Volumes:**
  - `pgdata` (database)
  - `sanitized_data` (sanitized JSON output)

**How to run:**
```bash
docker-compose -f docker-compose.daytime.yml up -d
```

**What happens:**
- Accepts task inputs via `whis_data_input`
- Passes them to `whis_sanitize`
- Writes sanitized JSON into the shared volume or data lake
- Database is shared and preloaded

---

## 🌙 Nighttime Mode: Training, Smithing, Enhancement

**File:** `docker-compose.nighttime.yml`

- **Purpose:** Nightly training mode — Whis reads sanitized data, generates Orbs and Runes, and enhances agents.
- **Services:**
  - `db` (PostgreSQL)
  - `whis_smithing` (rune/orb generation, merging)
  - `whis_enhance` (agent enhancement, training)
- **Volumes:**
  - `pgdata` (database)
  - `sanitized_data` (input for smithing)
  - `orbs` (output)
  - `runes` (output)

**How to run:**
```bash
docker-compose -f docker-compose.nighttime.yml up -d
```

**What happens:**
- Reads sanitized files from shared volume (`/data/sanitized`)
- Generates Orbs and Runes, stores to `orbs/`, `runes/`
- `whis_enhance` reads those and updates agents (or queues deployments)

---

## 🔐 Security & Environment Variables

- All secrets (e.g., `POSTGRES_PASSWORD`) are referenced via environment variables, never hardcoded.
- Use `.env` or export variables in your shell before running Compose:

```bash
export POSTGRES_PASSWORD=yourpassword
export OPENAI_API_KEY=sk-...
docker-compose -f docker-compose.daytime.yml up -d
```

- `.env` is in `.gitignore` and should never be committed.
- See `ENVIRONMENT_SETUP.md` for more details on secure configuration.

---

## 🧠 Pro Tips
- You can run both modes in parallel (on different ports/volumes) for advanced workflows.
- Use `docker-compose down` to stop and clean up after each mode.
- For production, consider using Docker secrets or Kubernetes secrets for even stronger security.

---

**This split gives you a fast, focused pipeline for both real-time data ingestion and nightly AI training.**

**Switch modes as needed for performance, cost, and security!** 