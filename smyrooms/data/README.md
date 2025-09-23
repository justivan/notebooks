# Data Directory Structure

This directory contains all data-related files for the Smyrooms project.

## Directory Structure

```
data/
├── input/         # Input data files and API responses
├── output/        # Generated files and exports
├── backups/       # Backup files and data snapshots
├── logs/          # Application and processing logs
└── temp/          # Temporary files (git-ignored)
```

## Usage Guidelines

1. **Input Data** (`input/`):
   - Original API responses
   - Raw data files
   - Source data for analysis
   - Document data sources and dates

2. **Output Data** (`output/`):
   - Analysis results
   - Generated reports
   - Data exports
   - Processed datasets

3. **Backups** (`backups/`):
   - Important data snapshots
   - Database dumps
   - Critical file backups
   - Use ISO date format: YYYY-MM-DD

4. **Logs** (`logs/`):
   - Application logs
   - Processing logs
   - Debug output
   - Error reports
   - Rotate/archive regularly

5. **Temporary** (`temp/`):
   - Working files
   - Intermediate results
   - Scratch space
   - Git-ignored, clean regularly

## Best Practices

1. Use clear, descriptive filenames with dates
2. Include metadata files where appropriate
3. Document data sources and processing steps
4. Maintain proper backup rotation
5. Clean temp files regularly
6. Use appropriate file formats (.parquet for large datasets)