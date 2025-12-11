"""Shared utility functions for disk space operations."""

import subprocess
from pathlib import Path
from datetime import datetime


def get_dir_size(path):
    """Get total size of a directory in bytes."""
    try:
        result = subprocess.run(
            ['du', '-sb', str(path)],
            capture_output=True,
            text=True,
            check=True
        )
        return int(result.stdout.split()[0])
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        return 0


def format_size(size_bytes):
    """Format bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_last_modified(path):
    """Get last modification time of directory."""
    try:
        result = subprocess.run(
            ['find', str(path), '-type', 'f', '-exec', 'stat', '-c', '%Y', '{}', ';'],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            timestamps = [int(t) for t in result.stdout.strip().split('\n') if t]
            if timestamps:
                return max(timestamps)
        return 0
    except:
        return 0


def has_git_repo(path):
    """Check if directory has a git repository."""
    return (path / '.git').exists()


def get_git_last_commit(path):
    """Get last git commit date."""
    try:
        result = subprocess.run(
            ['git', '-C', str(path), 'log', '-1', '--format=%ct'],
            capture_output=True,
            text=True,
            check=True
        )
        if result.stdout.strip():
            return int(result.stdout.strip())
    except:
        pass
    return 0


def count_python_files(path):
    """Count Python files in project."""
    try:
        result = subprocess.run(
            ['find', str(path), '-name', '*.py', '-type', 'f'],
            capture_output=True,
            text=True
        )
        return len([f for f in result.stdout.strip().split('\n') if f])
    except:
        return 0

