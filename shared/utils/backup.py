import json
from datetime import datetime
from pathlib import Path
from typing import Any


class Backup:
    """Generic backup utility for saving data to JSON files."""

    def __init__(self, backup_dir: str | Path):
        """Initialize backup utility with a specific backup directory.

        Args:
            backup_dir: Path to the backup directory. Can be relative or absolute.
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True, parents=True)

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
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{filename}_{timestamp}"

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
