import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .paths import ProjectPaths


class Backup:
    """Project-aware backup utility for saving data to JSON files."""

    def __init__(
        self, project_name: str | None = None, backup_dir: str | Path | None = None
    ):
        """Initialize backup utility with project-aware path management.

        Args:
            project_name: Name of the project (uses ProjectPaths if provided)
            backup_dir: Custom backup directory (overrides project paths)

        Note:
            If project_name is provided, uses standardized project backup directory.
            If backup_dir is provided, uses custom directory directly.
            One of project_name or backup_dir must be provided.
        """
        if project_name is None and backup_dir is None:
            raise ValueError("Either project_name or backup_dir must be provided")

        if project_name is not None:
            self.paths = ProjectPaths(project_name)
            self.paths.setup_data_dirs()
            self.backup_dir = self.paths.get_data_dir("backups")
        else:
            self.paths = None
            self.backup_dir = Path(backup_dir)
            self.backup_dir.mkdir(exist_ok=True, parents=True)

    @classmethod
    def for_project(cls, project_name: str) -> "Backup":
        """Create a backup instance for a specific project using standardized paths.

        Args:
            project_name: Name of the project

        Returns:
            Backup instance configured for the project
        """
        return cls(project_name=project_name)

    @classmethod
    def for_directory(cls, backup_dir: str | Path) -> "Backup":
        """Create a backup instance for a custom directory.

        Args:
            backup_dir: Custom backup directory path

        Returns:
            Backup instance configured for the directory
        """
        return cls(backup_dir=backup_dir)

    def save_to_json(
        self,
        data: Any,
        filename: str,
        add_timestamp: bool = True,
    ) -> Path:
        """Save data to a JSON file.

        Args:
            data: Data to backup (must be JSON serializable)
            filename: Base filename without extension
            add_timestamp: Whether to add timestamp to filename

        Returns:
            Path to the created backup file

        Raises:
            TypeError: If data is not JSON serializable
            OSError: If there's an error writing to the file
        """
        if not isinstance(filename, str):
            raise TypeError(f"Filename must be a string, got {type(filename)}")

        if add_timestamp:
            timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            filename = f"{timestamp}_{filename}"

        filepath = self.backup_dir / f"{filename}.json"

        try:
            # Test if data is JSON serializable first
            json.dumps(data)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            return filepath

        except TypeError as e:
            raise TypeError(f"Data is not JSON serializable: {e}") from e
        except OSError as e:
            raise OSError(f"Failed to write backup to {filepath}: {e}") from e

    def get_latest_backup(self, filename_pattern: str) -> Path | None:
        """Get the most recent backup file matching a pattern.

        Args:
            filename_pattern: Base filename to search for (without timestamp or
                extension)

        Returns:
            Path to the most recent backup file, or None if no backups found
        """
        pattern = f"*_{filename_pattern}.json"
        backup_files = list(self.backup_dir.glob(pattern))

        if not backup_files:
            return None

        # With timestamp-first naming, simple string sorting works
        return max(backup_files, key=lambda f: f.name)

    def load_latest_backup(self, filename_pattern: str) -> Any | None:
        """Load data from the most recent backup file.

        Args:
            filename_pattern: Base filename to search for

        Returns:
            Loaded data from the latest backup, or None if no backup found

        Raises:
            OSError: If there's an error reading the file
            json.JSONDecodeError: If the backup file contains invalid JSON
        """
        latest_file = self.get_latest_backup(filename_pattern)

        if latest_file is None:
            return None

        try:
            with open(latest_file, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            raise type(e)(f"Failed to load backup from {latest_file}: {e}") from e
