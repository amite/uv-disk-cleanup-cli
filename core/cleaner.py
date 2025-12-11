"""Cleanup operations module."""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
from core.utils import get_dir_size, format_size, get_last_modified, has_git_repo, get_git_last_commit, count_python_files


class Cleaner:
    """Handles cleanup operations for uv cache and virtual environments."""
    
    def __init__(self, base_path=None):
        """Initialize cleaner.
        
        Args:
            base_path: Base path to search for virtual environments.
                      Defaults to ~/code/python
        """
        self.home = Path.home()
        self.cache_dir = self.home / '.cache' / 'uv'
        if base_path:
            self.base_path = Path(base_path)
        else:
            self.base_path = self.home / 'code' / 'python'
        self.log_file = self.home / '.uv_disk_cleanup_log.json'
    
    def clean_cache(self, dry_run=False):
        """Clean UV cache.
        
        Args:
            dry_run: If True, only show what would be cleaned without doing it.
            
        Returns:
            dict: Result with 'success', 'size_freed', 'files_removed' keys
        """
        if not self.cache_dir.exists():
            return {
                'success': False,
                'message': 'Cache directory does not exist',
                'size_freed': 0,
                'files_removed': 0
            }
        
        # Get size before
        size_before = get_dir_size(self.cache_dir)
        
        if dry_run:
            return {
                'success': True,
                'message': 'Dry run - would clean cache',
                'size_freed': size_before,
                'files_removed': 0,
                'dry_run': True
            }
        
        try:
            result = subprocess.run(
                ['uv', 'cache', 'clean'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse output to get files removed
            files_removed = 0
            if 'Removed' in result.stdout:
                # Try to extract number from output like "Removed 88974 files"
                import re
                match = re.search(r'Removed (\d+) files', result.stdout)
                if match:
                    files_removed = int(match.group(1))
            
            self._log_cleanup('cache', size_before, 0, files_removed)
            
            return {
                'success': True,
                'message': 'Cache cleaned successfully',
                'size_freed': size_before,
                'files_removed': files_removed
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'message': f'Error cleaning cache: {e}',
                'size_freed': 0,
                'files_removed': 0
            }
    
    def remove_venv(self, venv_path, dry_run=False):
        """Remove a specific virtual environment.
        
        Args:
            venv_path: Path to virtual environment to remove
            dry_run: If True, only show what would be removed without doing it.
            
        Returns:
            dict: Result with 'success', 'size_freed' keys
        """
        venv_path = Path(venv_path)
        
        if not venv_path.exists():
            return {
                'success': False,
                'message': f'Virtual environment does not exist: {venv_path}',
                'size_freed': 0
            }
        
        size_before = get_dir_size(venv_path)
        
        if dry_run:
            return {
                'success': True,
                'message': f'Dry run - would remove {venv_path}',
                'size_freed': size_before,
                'dry_run': True
            }
        
        try:
            import shutil
            shutil.rmtree(venv_path)
            self._log_cleanup('venv', size_before, 0, 0, str(venv_path))
            
            return {
                'success': True,
                'message': f'Virtual environment removed: {venv_path}',
                'size_freed': size_before
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error removing virtual environment: {e}',
                'size_freed': 0
            }
    
    def analyze_unused_venvs(self, min_days_inactive=30, max_size_mb=500):
        """Analyze virtual environments to identify potentially unused ones.
        
        Args:
            min_days_inactive: Minimum days of inactivity to consider for removal
            max_size_mb: Maximum size in MB for small projects without git
        
        Returns:
            list: List of dictionaries with venv info and removal reasons
        """
        candidates = []
        
        for venv_path in self.base_path.rglob('.venv'):
            if not venv_path.is_dir():
                continue
            
            project_path = venv_path.parent
            venv_size = get_dir_size(venv_path)
            
            # Skip if very small (likely empty or minimal)
            if venv_size < 1024 * 1024:  # Less than 1MB
                continue
            
            # Get project info
            last_modified = get_last_modified(project_path)
            has_git = has_git_repo(project_path)
            git_last_commit = get_git_last_commit(project_path) if has_git else 0
            python_files = count_python_files(project_path)
            
            # Determine last activity
            last_activity = max(last_modified, git_last_commit) if git_last_commit else last_modified
            days_since_activity = (datetime.now().timestamp() - last_activity) / 86400 if last_activity > 0 else 999
            
            reasons = []
            
            # Check if inactive for more than specified days
            if days_since_activity > min_days_inactive:
                reasons.append(f"Inactive for {days_since_activity:.0f} days")
            
            # Check if no git repo and small
            if not has_git and venv_size < max_size_mb * 1024 * 1024:
                reasons.append("No git repo and relatively small")
            
            # Check if very few Python files
            if python_files < 5 and venv_size < 200 * 1024 * 1024:
                reasons.append("Very few Python files")
            
            if reasons:
                rel_path = venv_path.relative_to(self.base_path.parent)
                candidates.append({
                    'venv_path': venv_path,
                    'project_path': project_path,
                    'rel_path': str(rel_path),
                    'size': venv_size,
                    'days_since_activity': days_since_activity,
                    'has_git': has_git,
                    'python_files': python_files,
                    'reasons': reasons
                })
        
        # Sort by size (smallest first - safer to remove)
        candidates.sort(key=lambda x: x['size'])
        
        return candidates
    
    def get_cleanup_candidates(self):
        """Get all cleanup candidates (cache and unused venvs).
        
        Returns:
            dict: Dictionary with 'cache' and 'venvs' keys
        """
        candidates = {
            'cache': None,
            'venvs': []
        }
        
        # Check cache
        if self.cache_dir.exists():
            cache_size = get_dir_size(self.cache_dir)
            if cache_size > 0:
                candidates['cache'] = {
                    'path': str(self.cache_dir),
                    'size': cache_size,
                    'type': 'cache'
                }
        
        # Check unused venvs
        candidates['venvs'] = self.analyze_unused_venvs()
        
        return candidates
    
    def _log_cleanup(self, cleanup_type, size_freed, size_after, files_removed=0, path=None):
        """Log cleanup operation to file.
        
        Args:
            cleanup_type: Type of cleanup ('cache' or 'venv')
            size_freed: Size freed in bytes
            size_after: Size after cleanup in bytes
            files_removed: Number of files removed (for cache)
            path: Path to cleaned item (for venv)
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': cleanup_type,
            'size_freed': size_freed,
            'size_after': size_after,
            'files_removed': files_removed,
            'path': path
        }
        
        log_data = []
        if self.log_file.exists():
            try:
                import json
                with open(self.log_file, 'r') as f:
                    log_data = json.load(f)
            except:
                pass
        
        log_data.append(log_entry)
        # Keep only last 100 entries
        log_data = log_data[-100:]
        
        try:
            import json
            with open(self.log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
        except:
            pass

