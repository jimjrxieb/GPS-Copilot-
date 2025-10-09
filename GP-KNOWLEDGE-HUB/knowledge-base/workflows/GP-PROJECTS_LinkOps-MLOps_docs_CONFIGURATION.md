# Local Development Configuration

This document explains how to configure your local development environment to match the CI/CD pipeline requirements.

## Python Configuration

### Tools Used
- **Black**: Code formatting
- **isort**: Import sorting
- **Ruff**: Linting and import sorting
- **Bandit**: Security scanning

### Configuration Files
- `pyproject.toml`: Contains all Python tool configurations

### Local Commands

```bash
# Install tools
pip install ruff bandit isort black

# Format code
ruff format mlops/ shadows/

# Sort imports
isort mlops/ shadows/

# Lint code
ruff check mlops/ shadows/

# Security scan
bandit -r mlops/ shadows/
```

### VS Code Extensions
- Python
- Black Formatter
- isort
- Ruff

## Frontend Configuration

### Tools Used
- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting

### Configuration Files
- `.prettierrc`: Prettier configuration
- `.eslintrc.json`: ESLint configuration
- `package.json`: Scripts and dependencies

### Local Commands

```bash
cd frontend

# Install dependencies
npm install

# Format code
npm run format

# Lint code
npm run lint
```

### VS Code Extensions
- ESLint
- Prettier - Code formatter

## YAML Configuration

### Tools Used
- **yamllint**: YAML linting
- **Prettier**: YAML formatting

### Configuration Files
- `.yamllint.yml`: YAML linting rules

### Local Commands

```bash
# Install yamllint
pip install yamllint

# Install Prettier globally
npm install --global prettier

# Lint YAML files
yamllint helm/ .github/

# Format YAML files
prettier --write "helm/**/*.yaml" ".github/**/*.yml"
```

## Pre-commit Setup (Optional)

Create a `.pre-commit-config.yaml` file:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        types: [yaml, json]
```

Install pre-commit:
```bash
pip install pre-commit
pre-commit install
```

## IDE Integration

### VS Code Settings
Add to `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[yaml]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[json]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

## Troubleshooting

### Common Issues

1. **Black and isort conflicts**: The configuration in `pyproject.toml` ensures compatibility
2. **ESLint and Prettier conflicts**: The `.eslintrc.json` includes `plugin:prettier/recommended`
3. **YAML formatting issues**: Use the `.yamllint.yml` configuration for consistent formatting

### Version Compatibility
- Python: 3.11+
- Node.js: 20+
- npm: 8+

## Pipeline Alignment

These configurations ensure that:
- Local formatting matches CI/CD pipeline expectations
- Linting rules are consistent across environments
- Security scanning can be performed locally
- Import sorting follows the same rules as the pipeline

The CI/CD pipeline uses the same tools and configurations, so code that passes local checks should pass the pipeline. 