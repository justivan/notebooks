from contextlib import contextmanager

import pandas as pd
from sqlalchemy import MetaData, Table, create_engine, func, select
from sqlalchemy.orm import Session


class DatabaseConfig:
    """Configuration for database connections with timezone support"""

    def __init__(self, databases: dict, default_timezone: str = "UTC"):
        self.databases = databases
        self.default_timezone = default_timezone


class DatabaseProxy:
    """Proxy class for individual database connections"""

    def __init__(self, name, engine, metadata):
        self.name = name
        self.engine = engine
        self.metadata = metadata
        self.tables = {}

    def add_table(self, name, table):
        """Add a table to this database proxy"""
        self.tables[name] = table
        setattr(self, name, table)

    @contextmanager
    def session(self):
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

    def query_to_df(self, query):
        """Execute query and return pandas DataFrame for this database"""
        return pd.read_sql(query, self.engine)

    def describe_table(self, table_name):
        """Show table structure"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} not found in {self.name} database")
        table = self.tables[table_name]
        return [
            (col.name, str(col.type), col.nullable, str(col.default))
            for col in table.columns
        ]

    def quick_sample(self, table_name, limit=5):
        """Get sample data from table"""
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} not found in {self.name} database")
        table = self.tables[table_name]
        return self.query_to_df(select(table).limit(limit))

    def list_tables(self):
        """List all available tables in this database"""
        return list(self.tables.keys())

    def table_info(self):
        """Get info about all tables in this database"""
        info = {}
        for table_name, table in self.tables.items():
            info[table_name] = {
                "columns": len(table.columns),
                "column_names": [col.name for col in table.columns],
            }
        return info


class Database:
    """Main database manager class with timezone support"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.default_timezone = config.default_timezone
        self.engines = {}
        self.metadata = {}
        self.db_names = list(config.databases.keys())
        self.setup_databases(config.databases)

    def setup_databases(self, config):
        """Initialize all database connections and load tables"""
        print("Setting up database connections...")

        for db_name, db_config in config.items():
            print(f"Configuring {db_name} database...")

            try:
                # Create engine and metadata
                engine = create_engine(db_config["connection"])
                metadata = MetaData()

                # Test connection
                with engine.connect() as conn:
                    conn.execute(select(1))
                print(f"Connected to {db_name}")

                # Store engine and metadata
                self.engines[db_name] = engine
                self.metadata[db_name] = metadata

                # Create database proxy
                db_proxy = DatabaseProxy(db_name, engine, metadata)
                setattr(self, db_name, db_proxy)

                # Load tables
                loaded_tables = []
                failed_tables = []

                for table_name in db_config["tables"]:
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

            except Exception as e:
                print(f"Failed to connect to {db_name}: {e}")

        print("Database setup complete!")
        print(f"Available databases: {', '.join(self.list_databases())}")

    def list_databases(self):
        """List all available databases"""
        return self.db_names

    def get_database(self, db_name):
        """Get a specific database proxy"""
        if not hasattr(self, db_name):
            raise ValueError(f"Database {db_name} not found")
        return getattr(self, db_name)

    def overview(self):
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

    def apply_timezone_to_datetime_column(self, column, target_timezone=None):
        """Apply timezone conversion to a datetime column."""
        timezone = target_timezone or self.default_timezone
        if timezone == "UTC":
            return column
        return column.op("AT TIME ZONE")(timezone)

    def date_with_timezone(self, datetime_column, target_timezone=None):
        """Extract date from datetime column with timezone conversion."""
        timezone = target_timezone or self.default_timezone
        if timezone == "UTC":
            return func.date(datetime_column)
        return func.date(datetime_column.op("AT TIME ZONE")(timezone))
