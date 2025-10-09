# AI Coding Agent Instructions

This is a Python workspace for data analysis notebooks with standardized project structure and shared utilities.

## Architecture Overview

This workspace contains multiple notebook projects (e.g., `<project>/`, future projects) that share common utilities in `shared/`. Projects follow a specific pattern: API clients in `client/`, analysis notebooks in `notebooks/`, and standardized data directories.

Key architectural components:
- **Shared utilities**: Configuration, database access, path management, backup utilities
- **Project-specific code**: API clients, notebooks, data processing  
- **Standardized data flow**: `input/` → processing → `output/` with `backups/` and `logs/`

## Critical Patterns

### 1. Configuration Management
Always extend `AppConfig` from `shared.config` for type-safe environment variable loading:

```python
class ProjectConfig(AppConfig):
    API_KEY: str          # Required field (no default)
    TIMEOUT: int = 30     # Optional field with default
```

- Fields must be ALL_CAPS with type annotations
- Use `load_dotenv()` before creating config instances
- Boolean parsing: "true"/"yes"/"1" → True

### 2. Path Management  
Use `ProjectPaths` from `shared.utils.paths` for workspace-aware file operations:

```python
from shared.utils.paths import ProjectPaths

paths = ProjectPaths("<project>")
paths.setup_data_dirs()  # Creates input/, output/, backups/, logs/, temp/
backup_file = paths.get_data_dir("backups") / "data.json"
```

- Automatically finds workspace root via `pyproject.toml`
- Creates standardized data directory structure
- Use `get_data_dir()` with: "input", "output", "backups", "logs", "temp"

### 3. Data Backup Pattern
Use project-aware backups with ISO timestamps:

```python
from shared.utils.backup import Backup

backup = Backup.for_project("<project>")
backup.save_json(data, "analysis_results")  # Auto-generates timestamped filename
# Creates: YYYY-MM-DDTHH-MM-SS_analysis_results.json
```

### 4. Database Access
Use `Database` from `shared.database` for multi-database setups:

```python
from shared.database import Database

db = Database(config.database_config)
# Access via: db.database_name.query_to_df(query)
```

- Each database gets a proxy with `.session()` context manager
- Use `.query_to_df()` for pandas integration
- Tables auto-loaded and accessible as attributes

## Notebook Workflows

### Standard Notebook Imports
```python
import json
from shared.utils.backup import Backup
from shared.utils.paths import ProjectPaths
from project_name.client.api_client import ClientClass
from project_name.config import Config
```

### Typical Analysis Flow
1. Initialize project utilities: `Backup.for_project("project_name")`
2. Load previous backups: `backup.paths.get_data_dir("backups") / "file.json"`
3. Fetch fresh data via API client
4. Compare/analyze data using pandas
5. Save results: `backup.save_json(results, "analysis_name")`

## Development Setup

- **Python**: 3.13 (enforced in pyproject.toml)
- **Code formatting**: Ruff with 88-char line length
- **Dependencies**: Managed via uv with uv.lock
- **Environment**: Use `.env` files for configuration

### Key Commands
```bash
# Run code formatting
ruff format .

# Run linting  
ruff check .

# Install dependencies
uv sync
```

## Project Structure Rules

- Projects in workspace root (e.g., `<project>/`)
- API clients in `project/client/` 
- Notebooks in `project/notebooks/analysis/` or `project/notebooks/operations/`
- Configuration in `project/config.py` extending `AppConfig`
- Data follows standard directory structure via `ProjectPaths`
- Shared utilities in `shared/` module

## Code Standards
 
These are lightweight, opinionated standards to keep the codebase consistent and low-maintenance.
 
- Formatting and style
    - Use `ruff` for formatting and linting. Target an 88-character line length.
    - Run `ruff format .` before committing. If you add `pre-commit`, enable `ruff` there.
    - Prefer clear, idiomatic Python: use f-strings, context managers, and comprehensions when simple.
 
- Typing and structure
    - Add type annotations on public functions and methods. Use `typing` types (e.g., `list[str]`, `dict[str, Any]`).
    - Prefer small, focused functions. Use `dataclasses.dataclass` for plain data holders.
    - For complex config/data validation use a light-weight validator (e.g., Pydantic) only when necessary.
 
- Tests
    - Use `pytest` for unit tests. Put tests beside modules in a `tests/` folder or name them `test_*.py`.
    - Aim for small, fast unit tests (no external network or DB by default). Use fixtures and mocks for integration.
 
- Notebooks
    - Keep notebooks reproducible: include imports and configuration cells at the top.
    - Clear large outputs before committing. Do not store credentials or long secrets in notebook cells.
    - When code becomes stable, prefer moving it into `.py` modules and import from notebooks.
 
- Secrets and credentials
    - Never commit secrets. Use `.env` and `shared.config.AppConfig` for loading environment values.
    - Use `ProjectPaths` and the `data/` directories for non-secret artifacts only.
 
- Commits and PRs
    - Make small, focused commits with descriptive messages. Include a short rationale in the PR description.
    - Run `ruff format .` and `ruff check .` before opening a PR.

## Integration Points

- **Database**: Multi-database support via SQLAlchemy proxies
- **APIs**: RESTful clients with requests.Session
- **Data persistence**: JSON backups with ISO timestamps
- **Environment**: python-dotenv for configuration
- **Analysis**: pandas, numpy for data processing

Focus on the standardized patterns rather than implementing ad-hoc solutions. The shared utilities handle most common operations like path management, configuration, and data persistence.