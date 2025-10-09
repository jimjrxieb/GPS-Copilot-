# LinkOps Tools

This folder includes CLI tools and test scripts for validating the LinkOps microservices — including Whis, FickNury, Igris, Katie, and James.

## CLI Tools

| File | Description |
|------|-------------|
| `cli/submit_youtube.py` | Submit a YouTube URL and topic to Whis via the API |
| `cli/submit_manual_task.py` | Submit a local task file manually |

## Test Scripts

| File | Description |
|------|-------------|
| `test_transcript_download.py` | Dry run YouTube transcript extraction only |
| `test_youtube_transcript_upload.py` | Submit a transcript using mocked JSON |
| `test_manual_task_upload.py` | Submit manual task using mocked JSON |

## Mocks

| File | Description |
|------|-------------|
| `sample_task.json` | Raw task for ingestion testing |
| `sample_transcript.json` | Sample video transcript request |

## Structure

```
tools/
├── cli/
│   ├── submit_youtube.py            # Calls data_input API
│   ├── submit_manual_task.py        # Uploads local sample_task.json
│   └── run_full_pipeline.py         # Calls input → sanitize → train
├── mocks/
│   ├── sample_transcript.json
│   ├── sample_task.json
│   └── sample_error_fix.json
├── test_current_vs_desired.py       # Compare agent logic before/after training
├── test_orb_generation.py           # Simulate smithing from one input
├── reset_whis_state.py              # Clear DB queues, memory, logs
├── nightly_training_runner.py       # Can be used for cronjob or CLI kickoff
├── audit_structure.py               # Project structure audit
├── health_check.py                  # Service health check
├── fix_flake8.py                    # Flake8 fixer
├── lint.sh                          # Linting shell script
├── git_push.sh                      # Git push helper
├── rebuild.sh                       # Rebuild helper
└── README.md                        # This file
```

## Usage
- **cli/**: Scripts for submitting tasks, running pipelines, and simulating API calls.
- **mocks/**: Example payloads and data for testing.
- **audit_structure.py**: Checks project structure and organization.
- **health_check.py**: Checks health endpoints of all services.
- **reset_whis_state.py**: (Recommended) Script to clear DB, queues, and logs for a fresh start.

## How to Run

```bash
# Example: Run a CLI tool
python tools/cli/submit_youtube.py --url <youtube_url> --topic <topic>

# Example: Run a health check
python tools/health_check.py
```

## Contributing
- Add new tools with clear names and docstrings.
- Place test data in `mocks/`.
- Document new scripts in this README.