"""Interactive menu system for the CLI tool."""

import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich import box
from core.analyzer import DiskAnalyzer
from core.cleaner import Cleaner
from core.monitor import SpaceMonitor
from core.utils import format_size


class Menu:
    """Interactive menu for disk space management."""
    
    def __init__(self, base_path=None):
        """Initialize menu.
        
        Args:
            base_path: Base path for analysis. Defaults to ~/code/python
        """
        self.console = Console()
        self.analyzer = DiskAnalyzer(base_path)
        self.cleaner = Cleaner(base_path)
        self.base_path = base_path
        self.running = True
    
    def display_header(self):
        """Display menu header with current usage."""
        summary = self.analyzer.get_summary()
        
        # Create a table for the stats
        stats_table = Table.grid(padding=(0, 2))
        stats_table.add_column(style="cyan", justify="right")
        stats_table.add_column(style="magenta")
        
        stats_table.add_row("Current Usage:", f"[bold green]{format_size(summary['total_size'])}[/bold green]")
        stats_table.add_row("Cache:", f"[yellow]{format_size(summary['cache_size'])}[/yellow]")
        stats_table.add_row("Virtual Envs:", f"[blue]{format_size(summary['venv_size'])}[/blue] ({summary['venv_count']} environments)")
        
        header_panel = Panel(
            stats_table,
            title="[bold cyan]UV Disk Space Manager[/bold cyan]",
            border_style="cyan",
            padding=(1, 2)
        )
        
        self.console.print("\n")
        self.console.print(header_panel)
    
    def display_menu(self):
        """Display main menu options."""
        menu_table = Table.grid(padding=(0, 2))
        menu_table.add_column(style="yellow", justify="right")
        menu_table.add_column()
        
        menu_table.add_row("1", "Show detailed analysis")
        menu_table.add_row("2", "Clean UV cache")
        menu_table.add_row("3", "Remove unused virtual environments")
        menu_table.add_row("4", "Remove specific virtual environment")
        menu_table.add_row("5", "Show cleanup recommendations")
        menu_table.add_row("6", "Monitor space (run uv command)")
        menu_table.add_row("7", "[red]Exit[/red]")
        
        menu_panel = Panel(
            menu_table,
            title="[bold]Options[/bold]",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print("\n")
        self.console.print(menu_panel)
        self.console.print()
    
    def show_detailed_analysis(self):
        """Show detailed disk usage analysis."""
        self.console.print()
        
        # Cache analysis
        cache_subdirs, cache_total = self.analyzer.analyze_cache()
        
        cache_table = Table(title="[bold cyan]UV Cache Analysis[/bold cyan]", box=box.ROUNDED)
        cache_table.add_column("Component", style="cyan")
        cache_table.add_column("Size", justify="right", style="green")
        
        if cache_total > 0:
            cache_table.add_row("Total Cache", format_size(cache_total))
            cache_table.add_row("Location", str(self.analyzer.cache_dir))
            
            if cache_subdirs:
                cache_table.add_section()
                for name, size in sorted(cache_subdirs.items(), key=lambda x: x[1], reverse=True):
                    cache_table.add_row(name, format_size(size))
        else:
            cache_table.add_row("[dim]No uv cache found[/dim]", "")
        
        self.console.print(Panel(cache_table, border_style="cyan"))
        
        # Virtual environment analysis
        venvs = self.analyzer.analyze_venvs()
        
        venv_table = Table(title="[bold blue]Virtual Environment Analysis[/bold blue]", box=box.ROUNDED)
        venv_table.add_column("Virtual Environment", style="cyan", overflow="fold")
        venv_table.add_column("Size", justify="right", style="green")
        
        if venvs:
            total_venv_size = sum(size for _, size in venvs)
            venv_table.add_row("[bold]Total[/bold]", f"[bold green]{format_size(total_venv_size)}[/bold green]")
            venv_table.add_row(f"[dim]Found {len(venvs)} virtual environment(s)[/dim]", "")
            venv_table.add_section()
            
            for venv_path, size in venvs:
                rel_path = venv_path.relative_to(self.analyzer.base_path.parent)
                venv_table.add_row(str(rel_path), format_size(size))
            
            # Show largest packages in largest venv
            if venvs:
                largest_venv_path, _ = venvs[0]
                packages = self.analyzer.analyze_packages(largest_venv_path)
                
                if packages:
                    self.console.print()
                    pkg_table = Table(
                        title=f"[bold yellow]Largest packages in: {largest_venv_path.relative_to(self.analyzer.base_path.parent)}[/bold yellow]",
                        box=box.ROUNDED
                    )
                    pkg_table.add_column("Package", style="cyan")
                    pkg_table.add_column("Size", justify="right", style="green")
                    
                    for name, size in list(packages.items())[:20]:
                        pkg_table.add_row(name, format_size(size))
                    
                    self.console.print(Panel(pkg_table, border_style="yellow"))
        else:
            venv_table.add_row("[dim]No .venv directories found[/dim]", "")
        
        self.console.print()
        self.console.print(Panel(venv_table, border_style="blue"))
        self.console.print()
        
        Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
    
    def clean_cache(self):
        """Clean UV cache with confirmation."""
        cache_subdirs, cache_total = self.analyzer.analyze_cache()
        
        if cache_total == 0:
            self.console.print("\n[yellow]No cache to clean.[/yellow]")
            Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
            return
        
        info_table = Table.grid(padding=(0, 2))
        info_table.add_column(style="cyan")
        info_table.add_column(style="green")
        info_table.add_row("Cache size:", f"[bold]{format_size(cache_total)}[/bold]")
        info_table.add_row("Location:", str(self.analyzer.cache_dir))
        
        self.console.print()
        self.console.print(Panel(info_table, title="[bold yellow]UV Cache Cleanup[/bold yellow]", border_style="yellow"))
        self.console.print()
        
        if not Confirm.ask("Do you want to clean the cache?", default=False):
            self.console.print("[yellow]Cache cleanup cancelled.[/yellow]")
            Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
            return
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Cleaning cache...", total=None)
            result = self.cleaner.clean_cache()
        
        self.console.print()
        if result['success']:
            self.console.print(f"[bold green]✓ Success![/bold green] Freed [bold]{format_size(result['size_freed'])}[/bold]")
            if result.get('files_removed', 0) > 0:
                self.console.print(f"[dim]Removed {result['files_removed']} files[/dim]")
        else:
            self.console.print(f"[bold red]✗ Error:[/bold red] {result['message']}")
        
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]", default="")
    
    def remove_unused_venvs(self):
        """Remove unused virtual environments with confirmation."""
        with self.console.status("[cyan]Analyzing unused virtual environments...[/cyan]"):
            candidates = self.cleaner.analyze_unused_venvs()
        
        if not candidates:
            self.console.print("\n[green]No unused virtual environments found.[/green]")
            self.console.print("[dim]All virtual environments appear to be in active use.[/dim]")
            Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
            return
        
        self.console.print(f"\n[bold yellow]Found {len(candidates)} potentially unused virtual environment(s):[/bold yellow]")
        
        venv_table = Table(box=box.ROUNDED)
        venv_table.add_column("#", style="cyan", justify="right")
        venv_table.add_column("Virtual Environment", style="cyan", overflow="fold")
        venv_table.add_column("Size", justify="right", style="green")
        venv_table.add_column("Days Inactive", justify="right", style="yellow")
        venv_table.add_column("Reasons", style="dim")
        
        for i, candidate in enumerate(candidates, 1):
            reasons = ", ".join(candidate['reasons'])
            venv_table.add_row(
                str(i),
                candidate['rel_path'],
                format_size(candidate['size']),
                f"{candidate['days_since_activity']:.0f}",
                reasons
            )
        
        self.console.print()
        self.console.print(Panel(venv_table, border_style="yellow"))
        self.console.print()
        
        if not Confirm.ask("Do you want to remove these virtual environments?", default=False):
            self.console.print("[yellow]Removal cancelled.[/yellow]")
            Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
            return
        
        total_freed = 0
        removed = 0
        failed = 0
        
        with Progress(console=self.console) as progress:
            task = progress.add_task("Removing virtual environments...", total=len(candidates))
            
            for candidate in candidates:
                progress.update(task, description=f"Removing {candidate['rel_path']}...")
                result = self.cleaner.remove_venv(candidate['venv_path'])
                
                if result['success']:
                    total_freed += result['size_freed']
                    removed += 1
                    progress.console.print(f"  [green]✓[/green] Freed {format_size(result['size_freed'])}")
                else:
                    failed += 1
                    progress.console.print(f"  [red]✗[/red] Error: {result['message']}")
                
                progress.advance(task)
        
        summary_table = Table.grid(padding=(0, 2))
        summary_table.add_column(style="cyan")
        summary_table.add_column(style="green")
        summary_table.add_row("Removed:", f"[bold green]{removed}[/bold green] virtual environment(s)")
        if failed > 0:
            summary_table.add_row("Failed:", f"[bold red]{failed}[/bold red] virtual environment(s)")
        summary_table.add_row("Total space freed:", f"[bold green]{format_size(total_freed)}[/bold green]")
        
        self.console.print()
        self.console.print(Panel(summary_table, title="[bold green]Cleanup Summary[/bold green]", border_style="green"))
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]", default="")
    
    def remove_specific_venv(self):
        """Remove a specific virtual environment."""
        venvs = self.analyzer.analyze_venvs()
        
        if not venvs:
            self.console.print("\n[yellow]No virtual environments found.[/yellow]")
            Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
            return
        
        venv_table = Table(title="[bold yellow]Select Virtual Environment to Remove[/bold yellow]", box=box.ROUNDED)
        venv_table.add_column("#", style="cyan", justify="right")
        venv_table.add_column("Virtual Environment", style="cyan", overflow="fold")
        venv_table.add_column("Size", justify="right", style="green")
        
        for i, (venv_path, size) in enumerate(venvs, 1):
            rel_path = venv_path.relative_to(self.analyzer.base_path.parent)
            venv_table.add_row(str(i), str(rel_path), format_size(size))
        
        venv_table.add_row("[dim]Cancel[/dim]", f"[dim]{len(venvs) + 1}[/dim]", "")
        
        self.console.print()
        self.console.print(Panel(venv_table, border_style="yellow"))
        self.console.print()
        
        try:
            choice = int(Prompt.ask("Enter number", default=str(len(venvs) + 1)))
            if choice < 1 or choice > len(venvs) + 1:
                self.console.print("[red]Invalid choice.[/red]")
                Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
                return
            
            if choice == len(venvs) + 1:
                self.console.print("[yellow]Cancelled.[/yellow]")
                Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
                return
            
            venv_path, size = venvs[choice - 1]
            rel_path = venv_path.relative_to(self.analyzer.base_path.parent)
            
            info_table = Table.grid(padding=(0, 2))
            info_table.add_column(style="cyan")
            info_table.add_column(style="green")
            info_table.add_row("Selected:", str(rel_path))
            info_table.add_row("Size:", format_size(size))
            
            self.console.print()
            self.console.print(Panel(info_table, border_style="yellow"))
            self.console.print()
            
            if not Confirm.ask("Are you sure you want to remove this virtual environment?", default=False):
                self.console.print("[yellow]Removal cancelled.[/yellow]")
                Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
                return
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Removing virtual environment...", total=None)
                result = self.cleaner.remove_venv(venv_path)
            
            self.console.print()
            if result['success']:
                self.console.print(f"[bold green]✓ Success![/bold green] Freed [bold]{format_size(result['size_freed'])}[/bold]")
            else:
                self.console.print(f"[bold red]✗ Error:[/bold red] {result['message']}")
            
            Prompt.ask("\n[dim]Press Enter to continue...[/dim]", default="")
        except ValueError:
            self.console.print("[red]Invalid input. Please enter a number.[/red]")
            Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
        except Exception as e:
            self.console.print(f"[bold red]Error:[/bold red] {e}")
            Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
    
    def show_recommendations(self):
        """Show cleanup recommendations."""
        self.console.print()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            # Step 1: Analyze cache
            task1 = progress.add_task("[cyan]Analyzing UV cache...", total=None)
            cache_subdirs, cache_total = self.analyzer.analyze_cache()
            progress.update(task1, description="[green]✓[/green] Cache analyzed")
            
            # Step 2: Scan for virtual environments
            task2 = progress.add_task("[cyan]Scanning for virtual environments...", total=None)
            venvs = self.analyzer.analyze_venvs()
            venv_total = sum(size for _, size in venvs)
            progress.update(task2, description=f"[green]✓[/green] Found {len(venvs)} virtual environment(s)")
            
            # Step 3: Analyze unused venvs
            task3 = progress.add_task("[cyan]Analyzing unused virtual environments...", total=None)
            candidates = self.cleaner.get_cleanup_candidates()
            progress.update(task3, description="[green]✓[/green] Analysis complete")
        
        # Build summary from collected data
        summary = {
            'cache_size': cache_total,
            'venv_size': venv_total,
            'total_size': cache_total + venv_total,
            'cache_subdirs': cache_subdirs or {},
            'venv_count': len(venvs),
            'venvs': venvs
        }
        
        self.console.print()
        recommendations = []
        
        # Cache recommendation
        if candidates['cache']:
            cache_size = candidates['cache']['size']
            if cache_size > 5 * 1024**3:  # > 5GB
                recommendations.append({
                    'type': 'cache',
                    'action': 'Clean UV cache',
                    'potential_savings': cache_size,
                    'description': f'UV cache is {format_size(cache_size)}. Safe to clean - packages will re-download when needed.'
                })
        
        # Venv recommendations
        if candidates['venvs']:
            total_venv_size = sum(v['size'] for v in candidates['venvs'])
            recommendations.append({
                'type': 'venvs',
                'action': f'Remove {len(candidates["venvs"])} unused virtual environment(s)',
                'potential_savings': total_venv_size,
                'description': f'Found {len(candidates["venvs"])} potentially unused virtual environments totaling {format_size(total_venv_size)}.'
            })
        
        # General recommendations
        if summary['venv_count'] > 10:
            recommendations.append({
                'type': 'general',
                'action': 'Review virtual environments',
                'potential_savings': 0,
                'description': f'You have {summary["venv_count"]} virtual environments. Consider removing unused ones.'
            })
        
        self.console.print()
        
        if not recommendations:
            self.console.print(Panel(
                "[green]No specific recommendations at this time.[/green]\n[dim]Your disk usage appears to be well-managed.[/dim]",
                title="[bold cyan]Cleanup Recommendations[/bold cyan]",
                border_style="cyan"
            ))
        else:
            total_potential = sum(r['potential_savings'] for r in recommendations)
            
            rec_table = Table(title="[bold cyan]Cleanup Recommendations[/bold cyan]", box=box.ROUNDED)
            rec_table.add_column("#", style="cyan", justify="right")
            rec_table.add_column("Action", style="yellow")
            rec_table.add_column("Potential Savings", justify="right", style="green")
            rec_table.add_column("Description", style="dim")
            
            for i, rec in enumerate(recommendations, 1):
                savings_str = format_size(rec['potential_savings']) if rec['potential_savings'] > 0 else "[dim]N/A[/dim]"
                rec_table.add_row(
                    str(i),
                    rec['action'],
                    savings_str,
                    rec['description']
                )
            
            summary_text = f"[bold]Potential space savings:[/bold] [bold green]{format_size(total_potential)}[/bold green]"
            
            self.console.print(Panel(rec_table, border_style="cyan"))
            self.console.print()
            self.console.print(Panel(summary_text, border_style="green"))
        
        self.console.print()
        Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
    
    def monitor_command(self):
        """Monitor a uv command."""
        info_panel = Panel(
            "[cyan]Enter the uv command to monitor[/cyan]\n[dim]Example: 'uv add pandas' or 'uv sync'[/dim]\n[dim]Or type 'cancel' to go back[/dim]",
            title="[bold yellow]UV Command Monitor[/bold yellow]",
            border_style="yellow"
        )
        self.console.print()
        self.console.print(info_panel)
        self.console.print()
        
        command = Prompt.ask("Command", default="").strip()
        if command.lower() == 'cancel':
            return
        
        if not command.startswith('uv '):
            command = 'uv ' + command
        
        command_args = command.split()
        
        monitor = SpaceMonitor(self.base_path if self.base_path else None)
        monitor.monitor_command(command_args, console=self.console)
        
        Prompt.ask("\n[dim]Press Enter to continue...[/dim]", default="")
    
    def run(self):
        """Run the interactive menu loop."""
        while self.running:
            try:
                self.display_header()
                self.display_menu()
                
                choice = Prompt.ask("Select option", default="7").strip()
                
                if choice == '1':
                    self.show_detailed_analysis()
                elif choice == '2':
                    self.clean_cache()
                elif choice == '3':
                    self.remove_unused_venvs()
                elif choice == '4':
                    self.remove_specific_venv()
                elif choice == '5':
                    self.show_recommendations()
                elif choice == '6':
                    self.monitor_command()
                elif choice == '7':
                    self.console.print("\n[dim]Exiting...[/dim]")
                    self.running = False
                else:
                    self.console.print("\n[red]Invalid option. Please select 1-7.[/red]")
                    Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")
            except KeyboardInterrupt:
                self.console.print("\n\n[dim]Exiting...[/dim]")
                self.running = False
            except Exception as e:
                self.console.print(f"\n[bold red]Error:[/bold red] {e}")
                Prompt.ask("[dim]Press Enter to continue...[/dim]", default="")

