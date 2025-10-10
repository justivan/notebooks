from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import pandas as pd
from sqlalchemy import Column, Engine, MetaData, Table, create_engine, func, select
from sqlalchemy.orm import Session


class DatabaseConfig:
    """Configuration for database connections with timezone support"""

    def __init__(
        self, databases: dict[str, dict[str, Any]], default_timezone: str = "UTC"
    ) -> None:
        self.databases = databases
        self.default_timezone = default_timezone


class DatabaseProxy:
    """Proxy class for individual database connections"""

    def __init__(self, name: str, engine: Engine, metadata: MetaData) -> None:
        self.name = name
        self.engine = engine
        self.metadata = metadata
        self.tables: dict[str, Table] = {}

    def add_table(self, name: str, table: Table) -> None:
        """Add a table to this database proxy"""
        self.tables[name] = table
        setattr(self, name, table)

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Get a database session for this specific database"""
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def query_to_df(self, query: Any) -> pd.DataFrame:
        """Execute query and return pandas DataFrame for this database"""
        return pd.read_sql(query, self.engine)

    def describe_table(self, table_name: str) -> list[tuple[str, str, bool, str]]:
        """Show table structure"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} not found in {self.name} database")
        table = self.tables[table_name]
        return [
            (col.name, str(col.type), col.nullable, str(col.default))
            for col in table.columns
        ]

    def quick_sample(self, table_name: str, limit: int = 5) -> pd.DataFrame:
        """Get sample data from table"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} not found in {self.name} database")
        table = self.tables[table_name]
        return self.query_to_df(select(table).limit(limit))

    def list_tables(self) -> list[str]:
        """List all available tables in this database"""
        return list(self.tables.keys())

    def table_info(self) -> dict[str, dict[str, Any]]:
        """Get info about all tables in this database"""
        return {
            table_name: {
                "columns": len(table.columns),
                "column_names": [col.name for col in table.columns],
            }
            for table_name, table in self.tables.items()
        }


class Database:
    """Main database manager class with timezone support"""

    def __init__(self, config: DatabaseConfig) -> None:
        self.config = config
        self.default_timezone = config.default_timezone
        self.engines: dict[str, Engine] = {}
        self.metadata: dict[str, MetaData] = {}
        self.db_names = list(config.databases.keys())
        self.setup_databases(config.databases)

    def setup_databases(self, config: dict[str, dict[str, Any]]) -> None:
        """Initialize all database connections and load tables"""
        print("Setting up database connections...")

        for db_name, db_config in config.items():
            self._setup_single_database(db_name, db_config)

        print("Database setup complete!")
        print(f"Available databases: {', '.join(self.list_databases())}")

    def _setup_single_database(self, db_name: str, db_config: dict[str, Any]) -> None:
        """Setup a single database connection"""
        print(f"Configuring {db_name} database...")

        try:
            engine = create_engine(db_config["connection"])
            metadata = MetaData()

            # Test connection
            with engine.connect() as conn:
                conn.execute(select(1))
            print(f"Connected to {db_name}")

            self.engines[db_name] = engine
            self.metadata[db_name] = metadata

            db_proxy = DatabaseProxy(db_name, engine, metadata)
            setattr(self, db_name, db_proxy)

            self._load_tables(db_proxy, db_config["tables"], engine, metadata)

        except Exception as e:
            print(f"Failed to connect to {db_name}: {e}")

    def _load_tables(
        self,
        db_proxy: DatabaseProxy,
        table_names: list[str],
        engine: Engine,
        metadata: MetaData,
    ) -> None:
        """Load tables for a database proxy"""
        loaded_tables = []
        failed_tables = []

        for table_name in table_names:
            try:
                table = Table(table_name, metadata, autoload_with=engine)
                db_proxy.add_table(table_name, table)
                loaded_tables.append(table_name)
            except Exception as e:
                failed_tables.append((table_name, str(e)))

        print(f"Loaded {len(loaded_tables)} tables")
        if failed_tables:
            print(f"Failed to load {len(failed_tables)} tables")
            for table, error in failed_tables:
                print(f" - {table}: {error}")

    def list_databases(self) -> list[str]:
        """List all available databases"""
        return self.db_names

    def get_database(self, db_name: str) -> DatabaseProxy:
        """Get a specific database proxy"""
        if not hasattr(self, db_name):
            raise ValueError(f"Database {db_name} not found")
        return getattr(self, db_name)

    def overview(self) -> None:
        """Print overview of all databases and tables"""
        print("Database Overview:")
        print("=" * 50)

        for db_name in self.db_names:
            if hasattr(self, db_name):
                db_proxy = getattr(self, db_name)
                tables = db_proxy.list_tables()
                print(f"\n{db_name.upper()} ({len(tables)} tables):")
                for table in sorted(tables):
                    print(f"   • {table}")
            else:
                print(f"\n{db_name.upper()}: Not connected")

    def apply_timezone_to_datetime_column(
        self, column: Column, target_timezone: str | None = None
    ) -> Column:
        """Apply timezone conversion to a datetime column."""
        timezone = target_timezone or self.default_timezone
        if timezone == "UTC":
            return column
        return column.op("AT TIME ZONE")(timezone)

    def date_with_timezone(
        self, datetime_column: Column, target_timezone: str | None = None
    ) -> Any:
        """Extract date from datetime column with timezone conversion."""
        timezone = target_timezone or self.default_timezone
        if timezone == "UTC":
            return func.date(datetime_column)
        return func.date(datetime_column.op("AT TIME ZONE")(timezone))
