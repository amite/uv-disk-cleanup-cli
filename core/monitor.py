"""Space monitoring module for tracking uv command disk usage."""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from core.utils import get_dir_size, format_size


class SpaceMonitor:
    """Monitors disk space usage when running uv commands."""
    
    def __init__(self, base_path=None):
        """Initialize monitor.
        
        Args:
            base_path: Base path for current project. Defaults to current working directory.
        """
        self.home = Path.home()
        self.cache_dir = self.home / '.cache' / 'uv'
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.log_file = self.home / '.uv_space_log.json'
    
    def get_current_usage(self):
        """Get current disk usage for uv-related directories.
        
        Returns:
            dict: Usage information with cache_size, venv_size, total_size, etc.
        """
        usage = {
            'timestamp': datetime.now().isoformat(),
            'cache_size': 0,
            'venv_size': 0,
            'venv_path': None,
            'total_size': 0
        }
        
        # Check cache
        if self.cache_dir.exists():
            usage['cache_size'] = get_dir_size(self.cache_dir)
        
        # Check current project's .venv
        venv_path = self.base_path / '.venv'
        if venv_path.exists():
            usage['venv_size'] = get_dir_size(venv_path)
            usage['venv_path'] = str(venv_path)
        
        usage['total_size'] = usage['cache_size'] + usage['venv_size']
        
        return usage
    
    def load_log(self):
        """Load previous measurements from log file.
        
        Returns:
            list: List of log entries
        """
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def save_log(self, log_data):
        """Save measurements to log file.
        
        Args:
            log_data: List of log entries to save
        """
        try:
            with open(self.log_file, 'w') as f:
                json.dump(log_data, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save log file: {e}", file=sys.stderr)
    
    def get_package_list(self, venv_path):
        """Get list of installed packages in venv.
        
        Args:
            venv_path: Path to virtual environment (string or Path)
            
        Returns:
            list: List of package names
        """
        if not venv_path or not Path(venv_path).exists():
            return []
        
        venv = Path(venv_path)
        site_packages_dirs = list(venv.glob('lib/python*/site-packages'))
        if not site_packages_dirs:
            return []
        
        site_packages = site_packages_dirs[0]
        packages = []
        
        for item in site_packages.iterdir():
            if item.is_dir() and not item.name.endswith('.dist-info'):
                packages.append(item.name)
        
        return sorted(packages)
    
    def monitor_command(self, command_args):
        """Monitor a uv command and report space changes.
        
        Args:
            command_args: List of command arguments (e.g., ['uv', 'add', 'pandas'])
        """
        print("=" * 80)
        print("UV Space Monitor")
        print("=" * 80)
        print(f"Working directory: {self.base_path}")
        print(f"Command: {' '.join(command_args)}")
        print()
        
        # Get usage before
        print("Measuring disk usage BEFORE command...")
        before = self.get_current_usage()
        packages_before = self.get_package_list(before['venv_path'])
        
        print(f"  Cache size:     {format_size(before['cache_size']):>15s}")
        print(f"  .venv size:     {format_size(before['venv_size']):>15s}")
        print(f"  Total:          {format_size(before['total_size']):>15s}")
        print(f"  Packages:       {len(packages_before):>15d}")
        print()
        
        # Run the command
        print("Running command...")
        print("-" * 80)
        try:
            result = subprocess.run(
                command_args,
                check=False,
                capture_output=False
            )
            print("-" * 80)
            print()
            
            if result.returncode != 0:
                print(f"Warning: Command exited with code {result.returncode}")
                print()
        except KeyboardInterrupt:
            print("\nCommand interrupted by user")
            return
        except Exception as e:
            print(f"Error running command: {e}")
            return
        
        # Get usage after
        print("Measuring disk usage AFTER command...")
        after = self.get_current_usage()
        packages_after = self.get_package_list(after['venv_path'])
        
        print(f"  Cache size:     {format_size(after['cache_size']):>15s}")
        print(f"  .venv size:     {format_size(after['venv_size']):>15s}")
        print(f"  Total:          {format_size(after['total_size']):>15s}")
        print(f"  Packages:       {len(packages_after):>15d}")
        print()
        
        # Calculate differences
        print("Changes")
        print("-" * 80)
        cache_diff = after['cache_size'] - before['cache_size']
        venv_diff = after['venv_size'] - before['venv_size']
        total_diff = after['total_size'] - before['total_size']
        packages_diff = len(packages_after) - len(packages_before)
        
        print(f"  Cache change:   {format_size(cache_diff):>15s} ({'+' if cache_diff >= 0 else ''}{cache_diff:,} bytes)")
        print(f"  .venv change:   {format_size(venv_diff):>15s} ({'+' if venv_diff >= 0 else ''}{venv_diff:,} bytes)")
        print(f"  Total change:   {format_size(total_diff):>15s} ({'+' if total_diff >= 0 else ''}{total_diff:,} bytes)")
        print(f"  Packages added: {packages_diff:>15d}")
        print()
        
        # Show new packages
        if packages_diff > 0:
            new_packages = set(packages_after) - set(packages_before)
            if new_packages:
                print("New packages installed:")
                for pkg in sorted(new_packages):
                    print(f"  • {pkg}")
                print()
        
        # Save to log
        log_entry = {
            'timestamp': before['timestamp'],
            'command': ' '.join(command_args),
            'working_dir': str(self.base_path),
            'before': before,
            'after': after,
            'changes': {
                'cache_diff': cache_diff,
                'venv_diff': venv_diff,
                'total_diff': total_diff,
                'packages_added': packages_diff,
                'new_packages': list(new_packages) if packages_diff > 0 else []
            }
        }
        
        log_data = self.load_log()
        log_data.append(log_entry)
        # Keep only last 100 entries
        log_data = log_data[-100:]
        self.save_log(log_data)
        
        print("=" * 80)
        print(f"Monitoring complete. Log saved to: {self.log_file}")
        print("=" * 80)

