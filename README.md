# notebooks

A Python workspace that groups several notebook projects, primarily focused on data analysis and API interactions. This workspace provides a standardized structure and shared utilities for building maintainable data analysis projects.

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
  - `utils/backup.py`: Project-aware backup utilities for JSON data
- `/<project>/`: Project-specific code for individual integrations
  - `client/`: API client implementations
  - `notebooks/`: Jupyter notebooks for analysis
  - `data/`: Project data following standard structure

## Key Components

### 1. Configuration Management

The project uses a typed configuration pattern via the `AppConfig` base class in `shared/config.py`:

```python
class ProjectConfig(AppConfig):
    API_KEY: str
    DATABASE_URL: str
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

API clients follow a consistent pattern (e.g., `<project>/client/<service>_client.py`):
- Base `APIClient` class handles authentication and requests
- Feature-specific classes (e.g., `DataAPI`, `SearchAPI`) for endpoint grouping
- Environment-based URL configuration

### 4. Path Management

The workspace uses a standardized path management system through the `ProjectPaths` class in `shared/utils/paths.py`:

```python
# Example usage in a project
from shared.utils.paths import ProjectPaths

# Initialize project-specific paths
paths = ProjectPaths("project_name")

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

### 5. Backup Management

The workspace provides a standardized backup system through the `Backup` class in `shared/utils/backup.py`:

```python
# Example usage in a project
from shared.utils.backup import Backup

# Create project-aware backup instance
backup = Backup.for_project("project_name")

# Save data with automatic timestamping
backup_file = backup.save_to_json(data, "api_response")

# Load the most recent backup
latest_data = backup.load_latest_backup("api_response")

# Or use custom directory
custom_backup = Backup.for_directory("/path/to/custom/backups")
```

Key Features:
- Project-aware: Integrates with `ProjectPaths` for standardized backup locations
- Timestamped files: Automatic timestamp prefixes for chronological ordering
- JSON serialization: Built-in JSON encoding/decoding with error handling
- Latest file retrieval: Easy access to most recent backups by pattern
- Flexible initialization: Support for both project-based and custom directory modes

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
   paths = ProjectPaths("project_name")
   paths.setup_data_dirs()  # Creates standard directories
   backup_dir = paths.get_data_dir("backups")
   ```

3. **Data Backup**:
   ```python
   from shared.utils.backup import Backup
   backup = Backup.for_project("project_name")
   backup.save_to_json(api_data, "provider_list")
   ```

4. **Configuration Access**:
   ```python
   from <project>.config import Config
   db_config = Config.database_config
   ```

## Key Files for Reference

- `pyproject.toml`: Project dependencies and tool configurations
- `shared/config.py`: Base configuration patterns
- `shared/database.py`: Database access patterns
- `<project>/client/<service>_client.py`: API client patterns
