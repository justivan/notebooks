# AI Assistant Instructions for notebooks-workspace

This is a Python workspace that groups several notebook projects, primarily focused on data analysis and API interactions. Below are the key patterns and conventions to understand.

## Project Structure

### Key Paths

All projects follow a standardized path structure managed by the `ProjectPaths` class:

- `data/`: Base data directory for each project
  - `input/`: Input data files and API responses
  - `output/`: Generated files and exports
  - `backups/`: Backup files and snapshots
  - `logs/`: Application and processing logs
  - `temp/`: Temporary files (git-ignored)

### Module Layout

- `/shared/`: Common utilities shared across projects
  - `config.py`: Base configuration handling with environment variables
  - `database.py`: Database connection and query management
  - `utils/paths.py`: Workspace-aware path management
- `/smyrooms/`: Project-specific code for Smyrooms integration
  - `client/`: API client implementations
  - `notebooks/`: Jupyter notebooks for analysis
  - `data/`: Project data following standard structure

## Key Components

### 1. Configuration Management

The project uses a typed configuration pattern via the `AppConfig` base class in `shared/config.py`:

```python
class SmyroomsConfig(AppConfig):
    DISTRIBUTOR_APIKEY: str
    DB_CCENTER: str
```

- Environment variables must match class field names
- Fields must be in ALL_CAPS and have type annotations
- Configuration is loaded from .env files via python-dotenv

### 2. Database Access

Database interactions use SQLAlchemy through the `DatabaseProxy` class in `shared/database.py`:

- Each database connection is wrapped in a proxy object
- Tables are automatically loaded and accessible as attributes
- Built-in pandas DataFrame conversion with `query_to_df()`
- Session management via context managers: `with db.session() as session:`

### 3. API Clients

API clients follow a consistent pattern (`smyrooms/client/distributor_client.py`):
- Base `APIClient` class handles authentication and requests
- Feature-specific classes (e.g., `LevelCloseAPI`, `ProviderFilterAPI`) for endpoint grouping
- Environment-based URL configuration

### 4. Path Management

The workspace uses a standardized path management system through the `ProjectPaths` class in `shared/utils/paths.py`:

```python
# Example usage in a project
from shared.utils.paths import ProjectPaths

# Initialize project-specific paths
paths = ProjectPaths("smyrooms")

# Create standard data directories
paths.setup_data_dirs()

# Access data directories safely
input_dir = paths.get_data_dir("input")
output_dir = paths.get_data_dir("output")

# Work with project files
data_file = paths.get_data_file("input", "api_response.json")
```

Key Features:
- Workspace-aware: Automatically detects project root via `pyproject.toml`
- Standard directories: input, output, backups, logs, temp
- Safe path construction: OS-agnostic path handling
- Directory validation: Automatic creation and existence checks
- Type safety: Directory types validated at runtime

## Development Workflows

1. **Environment Setup**:
   - Python 3.12 required (see `.python-version`)
   - Dependencies managed via `uv` (see `uv.lock`)

2. **Code Style**:
   - Ruff for formatting and linting (configured in `pyproject.toml`)
   - Black-compatible 88 character line length
   - Double quotes for strings
   - Imports sorted with `isort` configuration

3. **Notebook Development**:
   - Place analysis notebooks in project-specific `/notebooks` directories
   - Import client modules relatively from project root
   - Use environment-specific configurations (e.g., `environment="pro"` for production)

## Common Patterns

1. **Error Handling**:
   ```python
   with db.session() as session:
       try:
           # Database operations
           session.commit()
       except Exception:
           session.rollback()
           raise
   ```

2. **Path Management**:
   ```python
   from shared.utils.paths import ProjectPaths
   paths = ProjectPaths("smyrooms")
   paths.setup_data_dirs()  # Creates standard directories
   backup_dir = paths.get_data_dir("backups")
   ```

3. **Configuration Access**:
   ```python
   from smyrooms.config import Config
   db_config = Config.database_config
   ```

## Key Files for Reference

- `pyproject.toml`: Project dependencies and tool configurations
- `shared/config.py`: Base configuration patterns
- `shared/database.py`: Database access patterns
- `smyrooms/client/distributor_client.py`: API client patterns