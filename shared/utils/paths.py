from pathlib import Path


class ProjectPaths:
    """Project path manager with caching and validation."""

    DATA_DIRS = ["input", "output", "backups", "logs", "temp"]

    def __init__(self, project_name: str):
        self.project_name = project_name
        self._root: Path | None = None
        self._workspace_root: Path | None = None

    @property
    def root(self) -> Path:
        """Cached project root path."""
        if self._root is None:
            self._root = self._get_project_root()
        return self._root

    def _get_project_root(self) -> Path:
        """Find project root by looking for pyproject.toml."""
        current = Path.cwd()
        while current != current.parent:
            if (current / "pyproject.toml").exists():
                project_dir = current / self.project_name
                if not project_dir.is_dir():
                    raise ValueError(
                        f"Project '{self.project_name}' not found in workspace"
                    )
                return project_dir
            current = current.parent
        raise ValueError("Could not find workspace root (no pyproject.toml found)")

    @property
    def data(self) -> Path:
        """Base data directory for the project."""
        return self.root / "data"

    def get_data_dir(self, data_type: str) -> Path:
        """Get a specific data directory.

        Args:
            data_type: Directory type ('input', 'output', 'backups', 'logs', 'temp')

        Returns:
            Path to the requested data directory
        """
        if data_type not in self.DATA_DIRS:
            raise ValueError(
                f"Invalid data directory type '{data_type}'. "
                f"Must be one of: {', '.join(self.DATA_DIRS)}"
            )
        return self.data / data_type

    def ensure_dirs(self, *dirs: str | Path) -> None:
        """Ensure directories exist, creating if necessary.

        Args:
            *dirs: Directory paths or data directory types to ensure exist
        """
        for dir in dirs:
            if isinstance(dir, str) and dir in self.DATA_DIRS:
                path = self.get_data_dir(dir)
            else:
                path = Path(dir)
            path.mkdir(parents=True, exist_ok=True)

    def setup_data_dirs(self) -> None:
        """Create all standard data directories."""
        self.ensure_dirs(*self.DATA_DIRS)
