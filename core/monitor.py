"""Space monitoring module for tracking uv command disk usage."""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
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
    
    def monitor_command(self, command_args, console=None):
        """Monitor a uv command and report space changes.
        
        Args:
            command_args: List of command arguments (e.g., ['uv', 'add', 'pandas'])
            console: Optional Rich Console instance for formatted output
        """
        if console is None:
            console = Console()
        
        info_table = Table.grid(padding=(0, 2))
        info_table.add_column(style="cyan")
        info_table.add_column(style="green")
        info_table.add_row("Working directory:", str(self.base_path))
        info_table.add_row("Command:", ' '.join(command_args))
        
        console.print()
        console.print(Panel(info_table, title="[bold cyan]UV Space Monitor[/bold cyan]", border_style="cyan"))
        console.print()
        
        # Get usage before
        console.print("[cyan]Measuring disk usage BEFORE command...[/cyan]")
        before = self.get_current_usage()
        packages_before = self.get_package_list(before['venv_path'])
        
        before_table = Table.grid(padding=(0, 2))
        before_table.add_column(style="cyan")
        before_table.add_column(style="green", justify="right")
        before_table.add_row("Cache size:", format_size(before['cache_size']))
        before_table.add_row(".venv size:", format_size(before['venv_size']))
        before_table.add_row("Total:", f"[bold]{format_size(before['total_size'])}[/bold]")
        before_table.add_row("Packages:", str(len(packages_before)))
        
        console.print(before_table)
        console.print()
        
        # Run the command
        console.print("[yellow]Running command...[/yellow]")
        console.print("-" * 80)
        try:
            result = subprocess.run(
                command_args,
                check=False,
                capture_output=False
            )
            console.print("-" * 80)
            console.print()
            
            if result.returncode != 0:
                console.print(f"[yellow]Warning: Command exited with code {result.returncode}[/yellow]")
                console.print()
        except KeyboardInterrupt:
            console.print("\n[yellow]Command interrupted by user[/yellow]")
            return
        except Exception as e:
            console.print(f"[bold red]Error running command:[/bold red] {e}")
            return
        
        # Get usage after
        console.print("[cyan]Measuring disk usage AFTER command...[/cyan]")
        after = self.get_current_usage()
        packages_after = self.get_package_list(after['venv_path'])
        
        after_table = Table.grid(padding=(0, 2))
        after_table.add_column(style="cyan")
        after_table.add_column(style="green", justify="right")
        after_table.add_row("Cache size:", format_size(after['cache_size']))
        after_table.add_row(".venv size:", format_size(after['venv_size']))
        after_table.add_row("Total:", f"[bold]{format_size(after['total_size'])}[/bold]")
        after_table.add_row("Packages:", str(len(packages_after)))
        
        console.print(after_table)
        console.print()
        
        # Calculate differences
        cache_diff = after['cache_size'] - before['cache_size']
        venv_diff = after['venv_size'] - before['venv_size']
        total_diff = after['total_size'] - before['total_size']
        packages_diff = len(packages_after) - len(packages_before)
        
        changes_table = Table(title="[bold yellow]Changes[/bold yellow]", box=box.ROUNDED)
        changes_table.add_column("Metric", style="cyan")
        changes_table.add_column("Change", justify="right", style="green")
        changes_table.add_column("Bytes", justify="right", style="dim")
        
        def format_diff(value):
            sign = "+" if value >= 0 else ""
            color = "green" if value >= 0 else "red"
            return f"[{color}]{sign}{format_size(value)}[/{color}]"
        
        changes_table.add_row("Cache change", format_diff(cache_diff), f"{cache_diff:+,}")
        changes_table.add_row(".venv change", format_diff(venv_diff), f"{venv_diff:+,}")
        changes_table.add_row("Total change", format_diff(total_diff), f"{total_diff:+,}")
        changes_table.add_row("Packages added", f"[green]{packages_diff:+d}[/green]", "")
        
        console.print(Panel(changes_table, border_style="yellow"))
        
        # Show new packages
        new_packages = set()
        if packages_diff > 0:
            new_packages = set(packages_after) - set(packages_before)
            if new_packages:
                console.print()
                pkg_list = "\n".join(f"  • {pkg}" for pkg in sorted(new_packages))
                console.print(Panel(
                    pkg_list,
                    title="[bold green]New packages installed[/bold green]",
                    border_style="green"
                ))
        
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
        
        console.print()
        console.print(Panel(
            f"[dim]Monitoring complete. Log saved to:[/dim] {self.log_file}",
            border_style="cyan"
        ))

