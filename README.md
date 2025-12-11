# UV Disk Manager

A comprehensive CLI tool for monitoring and cleaning up disk space used by uv Python packages.

## Features

- **Disk Usage Analysis**: Detailed breakdown of UV cache and virtual environment sizes
- **Interactive Menu**: Easy-to-use menu interface for all operations
- **Cache Cleanup**: Safely clean UV package cache
- **Virtual Environment Management**: Identify and remove unused virtual environments
- **Space Monitoring**: Track disk space changes when running `uv` commands
- **Cleanup Recommendations**: Get suggestions for freeing up space

## Installation

1. Navigate to the tool directory:
   ```bash
   cd ~/code/python/uv-disk-manager
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

3. Run the installation script:
   ```bash
   ./install.sh
   ```

4. If `~/.local/bin` is not in your PATH, add it to your `~/.bashrc` or `~/.zshrc`:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   source ~/.bashrc  # or source ~/.zshrc
   ```

5. Verify installation:
   ```bash
   uv-disk-clean --version
   ```

## Usage

### Interactive Mode (Recommended)

Simply run the tool from anywhere:

```bash
uv-disk-clean
```

This will launch an interactive menu with the following options:

1. **Show detailed analysis** - View comprehensive disk usage breakdown
2. **Clean UV cache** - Remove cached packages (safe, will re-download when needed)
3. **Remove unused virtual environments** - Automatically identify and remove unused venvs
4. **Remove specific virtual environment** - Manually select a venv to remove
5. **Show cleanup recommendations** - Get suggestions for freeing space
6. **Monitor space (run uv command)** - Track space usage for uv commands
7. **Exit** - Quit the tool

### Command Line Options

```bash
uv-disk-clean [OPTIONS]

Options:
  --base-path PATH    Base path to search for virtual environments
                      (default: ~/code/python)
  --version           Show version information
  --help              Show help message
```

Example:
```bash
uv-disk-clean --base-path ~/projects
```

## How It Works

### Disk Analysis

The tool analyzes:
- **UV Cache** (`~/.cache/uv`): Downloaded package archives and built wheels
- **Virtual Environments**: All `.venv` directories in the specified base path

### Cleanup Operations

1. **Cache Cleanup**: Runs `uv cache clean` to remove cached packages
   - Safe operation - packages re-download automatically when needed
   - Can free significant space (often 10-20GB+)

2. **Virtual Environment Removal**: 
   - Identifies unused venvs based on:
     - Days since last activity (>30 days)
     - No git repository and small size
     - Very few Python files
   - Requires confirmation before removal

### Space Monitoring

When monitoring `uv` commands, the tool:
- Measures disk usage before and after the command
- Shows what changed (cache, venv, packages)
- Logs all operations to `~/.uv_space_log.json`

## Log Files

The tool creates log files in your home directory:

- `~/.uv_space_log.json` - History of space monitoring operations
- `~/.uv_disk_cleanup_log.json` - History of cleanup operations

## Examples

### Clean up cache
```bash
uv-disk-clean
# Select option 2: Clean UV cache
```

### Monitor a package installation
```bash
uv-disk-clean
# Select option 6: Monitor space
# Enter: uv add pandas
```

### Remove unused virtual environments
```bash
uv-disk-clean
# Select option 3: Remove unused virtual environments
```

## Project Structure

```
uv-disk-manager/
├── main.py              # Main entry point
├── install.sh           # Installation script
├── core/                # Core functionality
│   ├── analyzer.py      # Disk usage analysis
│   ├── cleaner.py       # Cleanup operations
│   ├── monitor.py       # Space monitoring
│   └── utils.py         # Shared utilities
└── cli/                 # CLI interface
    └── menu.py          # Interactive menu system
```

## Requirements

- Python 3.8+
- `uv` command available in PATH
- `du` command (standard on Linux/WSL)
- Standard Linux utilities (`find`, `stat`, `git`)
- Dependencies are managed via `pyproject.toml` (run `uv sync` to install)

## Notes

- The tool is conservative in identifying unused virtual environments
- All cleanup operations require confirmation
- Cache cleanup is safe - packages will re-download when needed
- Virtual environment removal is permanent - use with caution

## Troubleshooting

**Import errors**: Make sure you're running the tool from the installed location or using the symlink created by `install.sh`.

**Permission errors**: Ensure you have write permissions to the directories you're trying to clean.

**Command not found**: Make sure `~/.local/bin` is in your PATH and you've run `install.sh`.

## License

This tool is provided as-is for personal use.

