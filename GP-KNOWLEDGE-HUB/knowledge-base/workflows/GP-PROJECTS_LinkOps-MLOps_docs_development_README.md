# Storage Directory

This directory contains persistent data for the ficknury_deploy service.

## Structure

- `logs/` - Task execution logs and verification data
  - `.gitkeep` - Ensures the directory is tracked in version control
  - Task logs are stored as JSON files with format: `{task_id}_{status}.json`

## Usage

The `verifier.py` module reads from this directory to verify task completion status.
The `executor.py` module writes execution logs to this directory.

## Permissions

The directory is owned by the non-root `app` user in the container for security. 