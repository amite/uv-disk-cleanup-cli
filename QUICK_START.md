# Quick Start Guide

## Installation

```bash
cd ~/code/python/uv-disk-manager
./install.sh
```

## Basic Usage

Run from anywhere:
```bash
uv-disk-clean
```

## Common Tasks

### Check disk usage
1. Run `uv-disk-clean`
2. Select option `1` (Show detailed analysis)

### Clean cache (frees 10-20GB typically)
1. Run `uv-disk-clean`
2. Select option `2` (Clean UV cache)
3. Confirm with `yes`

### Remove unused virtual environments
1. Run `uv-disk-clean`
2. Select option `3` (Remove unused virtual environments)
3. Review the list and confirm with `yes`

### Monitor a package installation
1. Run `uv-disk-clean`
2. Select option `6` (Monitor space)
3. Enter command like: `uv add pandas`

## Tips

- The tool is conservative - it won't remove anything without confirmation
- Cache cleanup is safe - packages re-download automatically
- Virtual environment removal is permanent - review carefully
- All operations are logged to `~/.uv_disk_cleanup_log.json`

## Getting Help

```bash
uv-disk-clean --help
```

